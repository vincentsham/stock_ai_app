from psycopg import connect
from utils import connect_to_db

# Connect to PostgreSQL
def table_creation(conn):
    try:
        cursor = conn.cursor()


        # Test the connection by executing a simple query
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        if result and result[0] == 1:
            print("Connection test successful!")
        else:
            print("Connection test failed!")


        # Create schema 'core' if it does not exist
        cursor.execute("""CREATE SCHEMA IF NOT EXISTS core;""")
        print("Schema 'core' created or already exists.")

        # Ensure the pgcrypto extension is available
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        print("Extension 'pgcrypto' created or already exists.")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.stock_profiles (
            tic             VARCHAR(10) PRIMARY KEY,      -- one canonical record per ticker
            name            VARCHAR(255),
            sector          VARCHAR(255),
            industry        VARCHAR(255),
            country         VARCHAR(255),
            market_cap      BIGINT,                
            employees       INTEGER,
            description     TEXT,
            website         TEXT,
            exchange        TEXT,
            currency        VARCHAR(10),
            summary         TEXT,                         -- ~200–300 words (for LLMs)
            short_summary   TEXT,                         -- ~80–150 words (UI-friendly)
            raw_json_sha256 CHAR(64),               -- hash of the raw JSON payload for integrity/lineage
            updated_at      TIMESTAMPTZ DEFAULT now()     -- auto-managed timestamp
        );
        """)
        print("Table 'stock_profiles' created or already exists.")



        # Create a table for news data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.news (
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic             VARCHAR(10) NOT NULL,              -- stock ticker
            published_at  TIMESTAMP   NOT NULL,              -- from API publishedDate
            publisher       TEXT,
            title           TEXT NOT NULL,
            site            TEXT,
            content         TEXT,
            url             TEXT NOT NULL,
            source          VARCHAR(255),
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            UNIQUE (tic, url)             -- unique news per ticker+url
        );
        """)
        print("Table 'news' created or already exists with unique constraint.")



        # Create a table for earnings calendar data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings_calendar (
            tic VARCHAR(10) NOT NULL,
            calendar_year INT NOT NULL,
            calendar_quarter INT NOT NULL,
            earnings_date DATE,
            fiscal_year INT,
            fiscal_quarter INT,
            fiscal_date DATE,
            session VARCHAR(10),
            updated_at            TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'earnings_calendar' created or already exists with composite primary key.")

        # Create a table for historical earnings data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings (
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic VARCHAR(10) NOT NULL,
            calendar_year SMALLINT NOT NULL,
            calendar_quarter SMALLINT NOT NULL,
            earnings_date DATE NOT NULL,
            fiscal_year SMALLINT,
            fiscal_quarter SMALLINT,
            fiscal_date DATE,
            session VARCHAR(10),
            eps NUMERIC(10,4),
            eps_estimated NUMERIC(10,4),
            revenue NUMERIC(20,2),
            revenue_estimated NUMERIC(20,2),
            source                 VARCHAR(255),                  -- e.g., 'fmp', 'yahoo', etc.
            raw_json               JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at            TIMESTAMPTZ DEFAULT now(),
            UNIQUE (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'earnings' created or already exists with unique constraint.")


        # Create a table for historical earnings transcripts data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings_transcripts (
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic             VARCHAR(10)  NOT NULL,
            calendar_year   SMALLINT     NOT NULL,
            calendar_quarter SMALLINT    NOT NULL,
            earnings_date   DATE         NOT NULL,
            transcript      TEXT         NOT NULL,
            transcript_sha256 CHAR(64)     NOT NULL,
            source          VARCHAR(255),
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),
            UNIQUE (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'earnings_transcripts' created or already exists with unique constraint.")



        # Create a table for analyst price targets data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.analyst_price_targets (
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic               varchar(10) NOT NULL,
            published_at      timestamp NOT NULL,
            title        text,
            site    text,
                       
            analyst_name      text,
            company   text,
            price_target      numeric(12,2),
            adj_price_target  numeric(12,2),
            price_when_posted numeric(12,4),

            url              text NOT NULL,
            source          VARCHAR(255),
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            UNIQUE (tic, url)
        );
        """)
        print("Table 'analyst_price_targets' created or already exists with unique constraint.")

        # Create a table for analyst grades data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.analyst_grades (
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic               varchar(10) NOT NULL,
            published_at      timestamp NOT NULL,
            title        text,
            site    text,
                       
            company           text,
            new_grade         SMALLINT,
            previous_grade    SMALLINT,
            action            text,
            price_when_posted numeric(12,4),

            url               text NOT NULL,
            source          VARCHAR(255),
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),

            UNIQUE (tic, url)
        );
        """)
        print("Table 'analyst_grades' created or already exists with unique constraint.")




       # Create a table for income statements if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.income_statements_quarterly (
            -- Identity & period alignment
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,
            earnings_date                     DATE         NOT NULL,    -- period end date (company fiscal)
            fiscal_year                       SMALLINT    NOT NULL,                 -- e.g., 2025
            fiscal_quarter                    SMALLINT    NOT NULL,                 -- 1–4 for quarters, 0 = full fiscal year (FY)
            fiscal_date                       DATE       NOT NULL,
    
            -- Key financials 
            revenue NUMERIC(20, 2),
            cost_of_revenue NUMERIC(20, 2),
            gross_profit NUMERIC(20, 2),

            -- 3. Operating Expenses (The cost of running the business)
            research_and_development NUMERIC(20, 2),
            selling_general_admin NUMERIC(20, 2),
            depreciation_amortization NUMERIC(20, 2),  -- Often hidden in other lines, but distinct
            operating_expenses NUMERIC(20, 2),         -- The total of the above

            -- 4. Operating Profitability
            operating_income NUMERIC(20, 2),
            ebitda NUMERIC(20, 2),
            ebit NUMERIC(20, 2),

            -- 5. Non-Operating Items (Interest & Investments)
            interest_income NUMERIC(20, 2),
            interest_expense NUMERIC(20, 2),
            other_non_operating_income NUMERIC(20, 2),

            -- 6. Pre-Tax & Tax
            income_before_tax NUMERIC(20, 2),
            income_tax_expense NUMERIC(20, 2),
            effective_tax_rate NUMERIC(10, 6),

            -- 7. Bottom Line (Profit)
            net_income NUMERIC(20, 2),

            -- 8. Share Information (For per-share calculations)
            weighted_average_shares_basic NUMERIC(20, 2),
            weighted_average_shares_diluted NUMERIC(20, 2),
            eps NUMERIC(10, 4),
            eps_diluted NUMERIC(10, 4),

            -- Raw payload for traceability
            raw_json                              JSONB        NOT NULL,
            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'income_statements_quarterly' created or already exists with unique constraint.")


       # Create a table for balance sheets if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.balance_sheets_quarterly (
            -- Identity & period alignment
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,
            earnings_date                     DATE         NOT NULL,    -- period end date (company fiscal)
            fiscal_year                       SMALLINT    NOT NULL,                 -- e.g., 2025
            fiscal_quarter                    SMALLINT    NOT NULL,                 -- 1–4 for quarters, 0 = full fiscal year (FY)
            fiscal_date                       DATE       NOT NULL,

            -- 1. ASSETS: Liquidity & Working Capital
            total_assets NUMERIC(20, 2),
            total_current_assets NUMERIC(20, 2),
            
            -- Cash & Investments (Critical for 'Net Debt' calculation)
            cash_and_short_term_investments NUMERIC(20, 2),
            cash_and_cash_equivalents NUMERIC(20, 2),
            
            -- Receivables (Critical for 'Days Sales Outstanding')
            accounts_receivable NUMERIC(20, 2),
            
            -- Inventory Breakdown (Critical for Manufacturing Efficiency analysis)
            inventory NUMERIC(20, 2),

            -- Long-Term Assets
            net_ppe NUMERIC(20, 2),              -- Property, Plant, Equipment
            goodwill_and_intangibles NUMERIC(20, 2),
            
            -- 2. LIABILITIES: Obligations
            total_liabilities NUMERIC(20, 2),
            total_current_liabilities NUMERIC(20, 2),
            
            -- Operational Liabilities
            accounts_payable NUMERIC(20, 2),
            deferred_revenue_current NUMERIC(20, 2),      -- Future revenue indicator
            deferred_revenue_non_current NUMERIC(20, 2), 

            -- Debt (Critical for Solvency & Enterprise Value)
            total_debt NUMERIC(20, 2),           -- Aggregated Debt
            long_term_debt NUMERIC(20, 2),
            current_debt_and_capital_lease NUMERIC(20, 2),

            -- 3. EQUITY: Shareholder Value
            total_equity NUMERIC(20, 2),
            retained_earnings NUMERIC(20, 2),    -- Measure of accumulated profit
            common_stock NUMERIC(20, 2),
            
            -- 4. KEY ANALYTICAL METRICS (Pre-calculated in source)
            working_capital NUMERIC(20, 2),
            invested_capital NUMERIC(20, 2),
            net_tangible_assets NUMERIC(20, 2),
            ordinary_shares_number NUMERIC(20, 2), -- Validating share counts

            -- Raw payload for traceability
            raw_json                              JSONB        NOT NULL,
            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'balance_sheets_quarterly' created or already exists with unique constraint.")


       # Create a table for cash flow statements if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.cash_flow_statements_quarterly (
            -- Identity & period alignment
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,
            earnings_date                     DATE         NOT NULL,    -- period end date (company fiscal)
            fiscal_year                       SMALLINT    NOT NULL,                 -- e.g., 2025
            fiscal_quarter                    SMALLINT    NOT NULL,                 -- 1–4 for quarters, 0 = full fiscal year (FY)
            fiscal_date                       DATE       NOT NULL,

            -- 1. OPERATING ACTIVITIES (The Core Business)
            net_income NUMERIC(20, 2),
            depreciation_amortization NUMERIC(20, 2),
            stock_based_compensation NUMERIC(20, 2), -- Key for Tech companies
            deferred_income_tax NUMERIC(20, 2),
            
            -- Working Capital Changes (Efficiency indicators)
            change_in_working_capital NUMERIC(20, 2),
            change_in_receivables NUMERIC(20, 2),
            change_in_inventory NUMERIC(20, 2),
            change_in_accounts_payable NUMERIC(20, 2),
            
            operating_cash_flow NUMERIC(20, 2), -- The "Quality of Earnings" check

            -- 2. INVESTING ACTIVITIES (Growth & Capex)
            capital_expenditure NUMERIC(20, 2),   -- "CapEx"
            acquisitions_net NUMERIC(20, 2),      -- Cash spent buying other companies
            investments_purchases NUMERIC(20, 2),
            investments_sales NUMERIC(20, 2),
            
            investing_cash_flow NUMERIC(20, 2),

            -- 3. FINANCING ACTIVITIES (Debt & Equity)
            net_debt_issuance NUMERIC(20, 2),
            common_stock_repurchased NUMERIC(20, 2), -- "Buybacks"
            dividends_paid NUMERIC(20, 2),
            
            financing_cash_flow NUMERIC(20, 2),

            -- 4. SUMMARY & SUPPLEMENTAL
            free_cash_flow NUMERIC(20, 2),        -- The "Holy Grail" metric
            net_change_in_cash NUMERIC(20, 2),
            end_cash_position NUMERIC(20, 2),
            income_tax_paid NUMERIC(20, 2),       -- Cash tax vs. Book tax
            interest_paid NUMERIC(20, 2),               -- Interest paid

            -- Raw payload for traceability
            raw_json                              JSONB        NOT NULL,
            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'cash_flow_statements_quarterly' created or already exists with unique constraint.")



        # Create a table for historical earnings transcripts data if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.earnings_transcripts (
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic             VARCHAR(10)  NOT NULL,
            calendar_year   SMALLINT     NOT NULL,
            calendar_quarter SMALLINT    NOT NULL,
            earnings_date   DATE         NOT NULL,
            transcript      TEXT         NOT NULL,
            transcript_sha256 CHAR(64)     NOT NULL,
            source          VARCHAR(255),
            raw_json        JSONB        NOT NULL,
            raw_json_sha256 CHAR(64)     NOT NULL,
            updated_at      TIMESTAMPTZ DEFAULT now(),
            UNIQUE (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'earnings_transcripts' created or already exists with unique constraint.")



        conn.commit()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            print("Tables created successfully!")
            conn.close()


if __name__ == "__main__":
    conn = connect_to_db()
    table_creation(conn)