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
            calendar_year SMALLINT NOT NULL,
            calendar_quarter SMALLINT NOT NULL,
            earnings_date DATE,
            fiscal_year SMALLINT,
            fiscal_quarter SMALLINT,
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
            fiscal_date DATE,
            session VARCHAR(10),
            eps NUMERIC(10,4),
            eps_estimated NUMERIC(10,4),
            revenue NUMERIC(20,2),
            revenue_estimated NUMERIC(20,2),
            price_before NUMERIC(12,4),
            price_after NUMERIC(12,4),
            source                 VARCHAR(255),                  -- e.g., 'fmp', 'yahoo', etc.
            raw_json               JSONB        NOT NULL,                 -- verbatim payload (optional but useful)
            raw_json_sha256        CHAR(64)     NOT NULL,
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
        CREATE TABLE IF NOT EXISTS core.income_statements (
            -- Identity & period alignment
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,
            earnings_date                     DATE         NOT NULL,    -- period end date (company fiscal)
            fiscal_year                       SMALLINT    NOT NULL,                 -- e.g., 2025
            fiscal_quarter                    SMALLINT    NOT NULL,                 -- 1–4 for quarters, 0 = full fiscal year (FY)
            fiscal_date                       DATE       NOT NULL,
            period                            VARCHAR(10)  NOT NULL,    -- "Q1".."Q4", "FY" (as reported)

            -- Filing / meta
            filing_date                           DATE,
            accepted_date                         TIMESTAMP,                -- raw feed is naive (no TZ)
            cik                                   VARCHAR(20),
            reported_currency                     VARCHAR(10),

            -- Key financials 
            revenue                               BIGINT,
            cost_of_revenue                       BIGINT,
            gross_profit                          BIGINT,
            research_and_development_expenses     BIGINT,
            general_and_administrative_expenses   BIGINT,
            selling_and_marketing_expenses        BIGINT,
            selling_general_and_administrative_expenses BIGINT,
            other_expenses                        BIGINT,
            operating_expenses                    BIGINT,
            cost_and_expenses                     BIGINT,

            -- Operating & non-operating
            ebitda                                BIGINT,
            ebit                                  BIGINT,
            non_operating_income_excluding_interest BIGINT,
            operating_income                      BIGINT,
            total_other_income_expenses_net       BIGINT,
            income_before_tax                     BIGINT,
            income_tax_expense                    BIGINT,

            -- Net income breakdowns
            net_income_from_continuing_operations BIGINT,
            net_income_from_discontinued_operations BIGINT,
            other_adjustments_to_net_income       BIGINT,
            net_income                            BIGINT,
            net_income_deductions                 BIGINT,
            bottom_line_net_income                BIGINT,

            -- Interest details
            net_interest_income                   BIGINT,
            interest_income                       BIGINT,
            interest_expense                      BIGINT,
            depreciation_and_amortization         BIGINT,

            -- EPS & shares
            eps                                   NUMERIC(10,2),
            eps_diluted                           NUMERIC(10,2),
            weighted_average_shs_out              BIGINT,
            weighted_average_shs_out_dil          BIGINT,

            -- Raw payload for traceability
            raw_json                              JSONB        NOT NULL,
            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'income_statements' created or already exists with unique constraint.")


       # Create a table for balance sheets if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.balance_sheets (
            -- Identity & period alignment
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,
            earnings_date                     DATE         NOT NULL,    -- period end date (company fiscal)
            fiscal_year                       SMALLINT    NOT NULL,                 -- e.g., 2025
            fiscal_quarter                    SMALLINT    NOT NULL,                 -- 1–4 for quarters, 0 = full fiscal year (FY)
            fiscal_date                       DATE       NOT NULL,
            period                            VARCHAR(10)  NOT NULL,    -- "Q1".."Q4", "FY" (as reported)

            -- Filing / meta
            filing_date                           DATE,
            accepted_date                         TIMESTAMP,                -- raw feed is naive (no TZ)
            cik                                   VARCHAR(20),
            reported_currency                     VARCHAR(10), 

            -- Assets
            cash_and_cash_equivalents           BIGINT,
            short_term_investments              BIGINT,
            cash_and_short_term_investments     BIGINT,
            net_receivables                     BIGINT,
            accounts_receivables                BIGINT,
            other_receivables                   BIGINT,
            inventory                           BIGINT,
            prepaids                            BIGINT,
            other_current_assets                BIGINT,
            total_current_assets                BIGINT,

            property_plant_equipment_net        BIGINT,
            goodwill                            BIGINT,
            intangible_assets                   BIGINT,
            goodwill_and_intangible_assets      BIGINT,
            long_term_investments               BIGINT,
            tax_assets                          BIGINT,
            other_non_current_assets            BIGINT,
            total_non_current_assets            BIGINT,
            other_assets                        BIGINT,
            total_assets                        BIGINT,

            -- Liabilities
            total_payables                      BIGINT,
            account_payables                    BIGINT,
            other_payables                      BIGINT,
            accrued_expenses                    BIGINT,
            short_term_debt                     BIGINT,
            capital_lease_obligations_current   BIGINT,
            tax_payables                        BIGINT,
            deferred_revenue                    BIGINT,
            other_current_liabilities           BIGINT,
            total_current_liabilities           BIGINT,

            long_term_debt                      BIGINT,
            capital_lease_obligations_non_current   BIGINT,
            deferred_revenue_non_current        BIGINT,
            deferred_tax_liabilities_non_current BIGINT,
            other_non_current_liabilities       BIGINT,
            total_non_current_liabilities       BIGINT,

            other_liabilities                   BIGINT,
            capital_lease_obligations           BIGINT,
            total_liabilities                   BIGINT,

            -- Equity
            treasury_stock                      BIGINT,
            preferred_stock                     BIGINT,
            common_stock                        BIGINT,
            retained_earnings                   BIGINT,
            additional_paid_in_capital          BIGINT,
            accumulated_other_comprehensive_income_loss BIGINT,
            other_total_stockholders_equity     BIGINT,
            total_stockholders_equity           BIGINT,
            total_equity                        BIGINT,
            minority_interest                   BIGINT,
            total_liabilities_and_total_equity  BIGINT,

            -- Derived Totals
            total_investments                   BIGINT,
            total_debt                          BIGINT,
            net_debt                            BIGINT,

            -- Raw payload for traceability
            raw_json                              JSONB        NOT NULL,
            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'balance_sheets' created or already exists with unique constraint.")


       # Create a table for cash flow statements if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.cash_flow_statements (
            -- Identity & period alignment
            event_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,
            earnings_date                     DATE         NOT NULL,    -- period end date (company fiscal)
            fiscal_year                       SMALLINT    NOT NULL,                 -- e.g., 2025
            fiscal_quarter                    SMALLINT    NOT NULL,                 -- 1–4 for quarters, 0 = full fiscal year (FY)
            fiscal_date                       DATE       NOT NULL,
            period                            VARCHAR(10)  NOT NULL,    -- "Q1".."Q4", "FY" (as reported)

            -- Filing / meta
            filing_date                           DATE,
            accepted_date                         TIMESTAMP,                -- raw feed is naive (no TZ)
            cik                                   VARCHAR(20),
            reported_currency                     VARCHAR(10),

            -- Operating Activities
            net_income                              BIGINT,
            depreciation_and_amortization           BIGINT,
            deferred_income_tax                     BIGINT,
            stock_based_compensation                BIGINT,
            change_in_working_capital               BIGINT,
            accounts_receivables                    BIGINT,
            inventory                               BIGINT,
            accounts_payables                       BIGINT,
            other_working_capital                   BIGINT,
            other_non_cash_items                    BIGINT,
            net_cash_provided_by_operating_activities BIGINT,

            -- Investing Activities
            investments_in_property_plant_and_equipment  BIGINT,
            acquisitions_net                         BIGINT,
            purchases_of_investments                 BIGINT,
            sales_maturities_of_investments          BIGINT,
            other_investing_activities               BIGINT,
            net_cash_provided_by_investing_activities BIGINT,

            -- Financing Activities
            net_debt_issuance                        BIGINT,
            long_term_net_debt_issuance              BIGINT,
            short_term_net_debt_issuance             BIGINT,
            net_stock_issuance                       BIGINT,
            net_common_stock_issuance                BIGINT,
            common_stock_issuance                    BIGINT,
            common_stock_repurchased                 BIGINT,
            net_preferred_stock_issuance             BIGINT,
            net_dividends_paid                       BIGINT,
            common_dividends_paid                    BIGINT,
            preferred_dividends_paid                 BIGINT,
            other_financing_activities               BIGINT,
            net_cash_provided_by_financing_activities BIGINT,

            -- Cash & Reconciliation
            effect_of_forex_changes_on_cash          BIGINT,
            net_change_in_cash                       BIGINT,
            cash_at_end_of_period                    BIGINT,
            cash_at_beginning_of_period              BIGINT,

            -- Derived / Analytical Metrics
            operating_cash_flow                      BIGINT,
            capital_expenditure                      BIGINT,
            free_cash_flow                           BIGINT,
            income_taxes_paid                        BIGINT,
            interest_paid                            BIGINT,

            -- Raw payload for traceability
            raw_json                              JSONB        NOT NULL,
            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, fiscal_year, fiscal_quarter)
        );
        """)
        print("Table 'cash_flow_statements' created or already exists with unique constraint.")



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