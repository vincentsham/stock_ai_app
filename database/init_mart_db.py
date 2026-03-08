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


        # Create schema 'mart' if it does not exist
        cursor.execute("""CREATE SCHEMA IF NOT EXISTS mart;""")
        print("Schema 'mart' created or already exists.")


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.stock_profiles (
            tic             VARCHAR(10),      -- one canonical record per ticker
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
            updated_at      TIMESTAMPTZ,     -- auto-managed timestamp
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate
        
            UNIQUE (tic, as_of_date)
        );
        """)
        print("Table 'stock_profiles' created or already exists.")


        # Create a table for earnings if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.earnings (
            tic                     VARCHAR(10) NOT NULL,
            calendar_year           SMALLINT     NOT NULL,
            calendar_quarter        SMALLINT    NOT NULL,
            earnings_date          DATE        NOT NULL,

            eps NUMERIC(10,4),
            eps_estimated NUMERIC(10,4),
            eps_yoy_growth NUMERIC(10,4),
            eps_yoy_acceleration NUMERIC(10,4),
            revenue NUMERIC(20,2),
            revenue_estimated NUMERIC(20,2),
            revenue_yoy_growth NUMERIC(10,4),
            revenue_yoy_acceleration NUMERIC(10,4),        
            updated_at      TIMESTAMPTZ,
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate

            UNIQUE (tic, calendar_year, calendar_quarter, as_of_date)
        );
        """)
        print("Table 'earnings' created or already exists with unique constraint.")



        # Create a table for earnings regime if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.earnings_regime (
            tic                     VARCHAR(10) NOT NULL,
            calendar_year           SMALLINT     NOT NULL,
            calendar_quarter        SMALLINT    NOT NULL,
            earnings_date          DATE        NOT NULL,

            eps_surprise_regime             VARCHAR(50),
            revenue_surprise_regime         VARCHAR(50),
            eps_yoy_growth_regime          VARCHAR(50),
            revenue_yoy_growth_regime      VARCHAR(50),
            eps_yoy_accel_regime          VARCHAR(50),
            revenue_yoy_accel_regime      VARCHAR(50),


            updated_at      TIMESTAMPTZ DEFAULT now(),
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate

            UNIQUE (tic, calendar_year, calendar_quarter, as_of_date)
        );
        """)
        print("Table 'earnings_regime' created or already exists with unique constraint.")



        # Create a table for earnings transcript analysis if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.earnings_transcript_analysis (
            inference_id       UUID,
            event_id           UUID NOT NULL,
            tic                     VARCHAR(10) NOT NULL,
            calendar_year           SMALLINT     NOT NULL,
            calendar_quarter        SMALLINT    NOT NULL,
            earnings_date          DATE        NOT NULL,

            -- === Past analysis ===
            sentiment               SMALLINT,       -- -1, 0, 1
            durability              SMALLINT,       -- 0, 1, 2
            performance_factors     TEXT[] NOT NULL,
            past_summary            TEXT,

            -- === Future analysis ===
            guidance_direction      SMALLINT,       -- -1, 0, 1
            revenue_outlook         SMALLINT,       -- -1, 0, 1
            margin_outlook          SMALLINT,       -- -1, 0, 1
            earnings_outlook        SMALLINT,       -- -1, 0, 1
            cashflow_outlook        SMALLINT,       -- -1, 0, 1
            growth_acceleration     SMALLINT,       -- -1, 0, 1
            future_outlook_sentiment SMALLINT,      -- -1, 0, 1
            growth_drivers               TEXT[] NOT NULL,
            future_summary          TEXT,

            -- === Risk analysis ===
            risk_mentioned          SMALLINT,       -- 0 or 1
            risk_impact             SMALLINT,       -- -1, 0, 1
            risk_time_horizon       SMALLINT,       -- 0, 1, 2
            risk_factors            TEXT[] NOT NULL,
            risk_summary            TEXT,

            -- === Mitigation / risk response ===
            mitigation_mentioned     SMALLINT,      -- 0 or 1
            mitigation_effectiveness SMALLINT,      -- -1, 0, 1
            mitigation_time_horizon  SMALLINT,      -- 0, 1, 2
            mitigation_actions       TEXT[] NOT NULL,
            mitigation_summary       TEXT,

            -- Optional for tracking & versioning
            transcript_sha256     CHAR(64) NOT NULL,
            updated_at      TIMESTAMPTZ,
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate

            UNIQUE (tic, calendar_year, calendar_quarter, as_of_date),
            UNIQUE (event_id, as_of_date)
        );
        """)
        print("Table 'earnings_transcript_analysis' created or already exists with unique constraint.")



       # Create a table for analyst rating yearly summary if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.analyst_rating_yearly_summary (
            tic                     VARCHAR(10) NOT NULL,
            date                   DATE        NOT NULL,
            close                  NUMERIC(12,4),
            pt_count                 INTEGER,
            pt_high                  NUMERIC(12,4),
            pt_low                   NUMERIC(12,4),
            pt_p25                   NUMERIC(12,4),
            pt_median                NUMERIC(12,4),
            pt_p75                   NUMERIC(12,4),
            pt_upgrade_n             INTEGER,
            pt_downgrade_n           INTEGER,
            pt_reiterate_n           INTEGER,
            pt_init_n                INTEGER,
            grade_count              INTEGER,
            grade_buy_n              INTEGER,
            grade_hold_n             INTEGER,
            grade_sell_n             INTEGER,
            grade_upgrade_n          INTEGER,
            grade_downgrade_n        INTEGER,
            grade_reiterate_n        INTEGER,
            grade_init_n             INTEGER,


            updated_at      TIMESTAMPTZ,
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate

            UNIQUE (tic, date, as_of_date)
        );
        """)
        print("Table 'analyst_rating_yearly_summary' created or already exists with unique constraint.")

        # Create a table for catalyst master if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.catalyst_master (
            catalyst_id      UUID,
            tic              VARCHAR(10),
            date             DATE,
            catalyst_type    VARCHAR(64),
            title            TEXT,
            summary          TEXT,
            state            VARCHAR(20),
            sentiment        SMALLINT,
            time_horizon     SMALLINT,
            magnitude        SMALLINT,
            impact_area      VARCHAR(32),

            mention_count    INTEGER,
            chunk_ids        TEXT[],
            source_types     TEXT[],
            citations        TEXT[],
            urls             TEXT[],
            created_at       TIMESTAMPTZ,
            updated_at       TIMESTAMPTZ ,
            as_of_date      DATE NOT NULL,        -- date when the data was last confirmed accurate
            
            UNIQUE (catalyst_id, as_of_date)
        );
        """)
        print("Table 'catalyst_master' created or already exists with unique constraint.")



       # Create a table for valuation metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.valuation_metrics (
            -- Identity & period alignment
            inference_id       UUID,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,
            score          NUMERIC(6, 3),  -- 0-100
                       
            pe_ttm              NUMERIC(20, 6),   -- Price / EPS (TTM)
            pe_forward          NUMERIC(20, 6),   -- Price / Forward EPS
            ev_to_ebitda_ttm    NUMERIC(20, 6),   -- EV / EBITDA (TTM)
            fcf_yield_ttm       NUMERIC(20, 8),   -- FCF / Market Cap (TTM)
            ps_ttm              NUMERIC(20, 6),   -- Price / Sales (TTM)        
            ev_to_revenue_ttm   NUMERIC(20, 6),   -- EV / Revenue (TTM)
            p_to_fcf_ttm        NUMERIC(20, 6),   -- Price / Free Cash Flow (TTM)
            peg_ratio           NUMERIC(20, 6),   -- PE / EPS growth (explicit growth basis)
            peg_ratio_forward   NUMERIC(20, 6),   -- PE / EPS growth (explicit growth basis)
            price_to_book       NUMERIC(20, 6),   -- Market Cap / Equity
            ev_to_fcf_ttm       NUMERIC(20, 6),   -- EV / FCF (TTM)
            earnings_yield_ttm  NUMERIC(20, 8),   -- EPS / Price  (or NI / Market Cap)
            revenue_yield_ttm   NUMERIC(20, 8),   -- Revenue / Market Cap
            total_shareholder_yield_ttm NUMERIC(20, 8), -- (Dividends + Buybacks) / Market Cap (TTM)

            pe_ttm_percentile              NUMERIC(6, 3),   -- Price / EPS (TTM)
            pe_forward_percentile          NUMERIC(6, 3),   -- Price / Forward EPS
            ev_to_ebitda_ttm_percentile    NUMERIC(6, 3),   -- EV / EBITDA (TTM)
            fcf_yield_ttm_percentile       NUMERIC(6, 3),   -- FCF / Market Cap (TTM)
            ps_ttm_percentile              NUMERIC(6, 3),   -- Price / Sales (TTM)
            ev_to_revenue_ttm_percentile   NUMERIC(6, 3),   -- EV / Revenue (TTM)
            p_to_fcf_ttm_percentile        NUMERIC(6, 3),   -- Price / Free Cash Flow (TTM)
            peg_ratio_percentile           NUMERIC(6, 3),   -- PE / EPS growth (explicit growth basis)
            peg_ratio_forward_percentile   NUMERIC(6, 3),   -- PE / EPS growth (explicit growth basis)
            price_to_book_percentile       NUMERIC(6, 3),   -- Market Cap / Equity
            ev_to_fcf_ttm_percentile       NUMERIC(6, 3),   -- EV / FCF (TTM)
            earnings_yield_ttm_percentile  NUMERIC(6, 3),   -- EPS / Price  (or NI / Market Cap)
            revenue_yield_ttm_percentile   NUMERIC(6, 3),   -- Revenue / Market Cap
            total_shareholder_yield_ttm_percentile NUMERIC(6, 3), -- (Dividends + Buybacks) / Market Cap (TTM)


            updated_at                            TIMESTAMPTZ  NOT NULL,
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate
            UNIQUE (tic, date, as_of_date)
        );
        """)
        print("Table 'valuation_metrics' created or already exists with composite primary key.")



       # Create a table for profitability metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.profitability_metrics (
            -- Identity & period alignment
            inference_id       UUID,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,
            score          NUMERIC(6, 3),  -- 0-100

            gross_margin         NUMERIC(20, 8),  -- (Revenue - COGS) / Revenue
            operating_margin     NUMERIC(20, 8),  -- EBIT / Revenue
            ebitda_margin        NUMERIC(20, 8),  -- EBITDA / Revenue
            net_margin           NUMERIC(20, 8),  -- Net Income / Revenue
            roe                  NUMERIC(20, 8),  -- Net Income / Avg Equity
            roa                  NUMERIC(20, 8),  -- Net Income / Avg Assets
            roic                 NUMERIC(20, 8),  -- NOPAT / (Debt + Equity - Cash)
            ocf_margin           NUMERIC(20, 8),  -- Operating Cash Flow / Revenue
            fcf_margin           NUMERIC(20, 8),  -- Free Cash Flow / Revenue
                       
            gross_margin_percentile         NUMERIC(6, 3),  -- (Revenue - COGS) / Revenue
            operating_margin_percentile     NUMERIC(6, 3),  -- EBIT / Revenue
            ebitda_margin_percentile        NUMERIC(6, 3),  -- EBITDA / Revenue
            net_margin_percentile           NUMERIC(6, 3),  -- Net Income / Revenue
            roe_percentile                  NUMERIC(6, 3),  -- Net Income / Avg Equity
            roa_percentile                  NUMERIC(6, 3),  -- Net Income / Avg Assets
            roic_percentile                 NUMERIC(6, 3),  -- NOPAT / (Debt + Equity - Cash)
            ocf_margin_percentile           NUMERIC(6, 3),  -- Operating Cash Flow / Revenue
            fcf_margin_percentile           NUMERIC(6, 3),  -- Free Cash Flow / Revenue
                   
                   
            updated_at                            TIMESTAMPTZ  NOT NULL,
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate
            UNIQUE (tic, date, as_of_date)
        );
        """)
        print("Table 'profitability_metrics' created or already exists with composite primary key.")


       # Create a table for growth metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.growth_metrics (
            -- Identity & period alignment
            inference_id       UUID,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,
            score          NUMERIC(6, 3),  -- 0-100

            revenue_growth_yoy       NUMERIC(20, 8),  -- (Rev_t - Rev_t-1) / abs(Rev_t-1)
            revenue_cagr_3y          NUMERIC(20, 8),  -- (Rev_t / Rev_t-3)^(1/3) - 1
            revenue_cagr_5y          NUMERIC(20, 8),  -- (Rev_t / Rev_t-5)^(1/5) - 1
            eps_growth_yoy           NUMERIC(20, 8),  -- (EPS_t - EPS_t-1) / abs(EPS_t-1)
            eps_cagr_3y              NUMERIC(20, 8),  -- (EPS_t / EPS_t-3)^(1/3) - 1
            eps_cagr_5y              NUMERIC(20, 8),  -- (EPS_t / EPS_t-5)^(1/5) - 1
            fcf_growth_yoy           NUMERIC(20, 8),  -- (FCF_t - FCF_t-1) / abs(FCF_t-1)
            fcf_cagr_3y              NUMERIC(20, 8),  -- (FCF_t / FCF_t-3)^(1/3) - 1
            fcf_cagr_5y              NUMERIC(20, 8),  -- (FCF_t / FCF_t-5)^(1/5) - 1
            ebitda_growth_yoy        NUMERIC(20, 8),  -- optional   
            ebitda_cagr_3y           NUMERIC(20, 8),  -- optional
            ebitda_cagr_5y           NUMERIC(20, 8),  -- optional         
            operating_income_growth_yoy NUMERIC(20, 8), -- optional (EBIT / OpInc)
            forward_revenue_growth   NUMERIC(20, 8),  -- optional, expected
            forward_eps_growth       NUMERIC(20, 8),  -- optional, expected

            revenue_growth_yoy_percentile       NUMERIC(6, 3),  -- (Rev_t - Rev_t-1) / abs(Rev_t-1)
            revenue_cagr_3y_percentile          NUMERIC(6, 3),  -- (Rev_t / Rev_t-3)^(1/3) - 1
            revenue_cagr_5y_percentile          NUMERIC(6, 3),  -- (Rev_t / Rev_t-5)^(1/5) - 1
            eps_growth_yoy_percentile           NUMERIC(6, 3),  -- (EPS_t - EPS_t-1) / abs(EPS_t-1)
            eps_cagr_3y_percentile              NUMERIC(6, 3),  -- (EPS_t / EPS_t-3)^(1/3) - 1
            eps_cagr_5y_percentile              NUMERIC(6, 3),  -- (EPS_t / EPS_t-5)^(1/5) - 1
            fcf_growth_yoy_percentile           NUMERIC(6, 3),  -- (FCF_t - FCF_t-1) / abs(FCF_t-1)
            fcf_cagr_3y_percentile              NUMERIC(6, 3),  -- (FCF_t / FCF_t-3)^(1/3) - 1
            fcf_cagr_5y_percentile              NUMERIC(6, 3),  -- (FCF_t / FCF_t-5)^(1/5) - 1
            ebitda_growth_yoy_percentile        NUMERIC(6, 3),  -- optional   
            ebitda_cagr_3y_percentile           NUMERIC(6, 3),  -- optional
            ebitda_cagr_5y_percentile           NUMERIC(6, 3),  -- optional                     
            operating_income_growth_yoy_percentile NUMERIC(6, 3), -- optional (EBIT / OpInc)
            forward_revenue_growth_percentile   NUMERIC(6, 3),  -- optional, expected
            forward_eps_growth_percentile       NUMERIC(6, 3),  -- optional, expected          
                       
            updated_at                            TIMESTAMPTZ  NOT NULL,
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate
            UNIQUE (tic, date, as_of_date)
        );
        """)
        print("Table 'growth_metrics' created or already exists with composite primary key.")



       # Create a table for efficiency metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.efficiency_metrics (
            -- Identity & period alignment
            inference_id       UUID,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,
            score          NUMERIC(6, 3),  -- 0-100
                
            asset_turnover           NUMERIC(20, 8),  -- Revenue / Avg Total Assets
            cash_conversion_cycle    NUMERIC(20, 6),  -- DSO + DIO - DPO (days)
            dso                      NUMERIC(20, 6),  -- Avg AR / Revenue * 365 (days)
            dio                      NUMERIC(20, 6),  -- Avg Inventory / COGS * 365 (days)
            dpo                      NUMERIC(20, 6),  -- Avg AP / COGS * 365 (days)
            fixed_asset_turnover     NUMERIC(20, 8),  -- Revenue / Avg Net PPE
            revenue_per_employee     NUMERIC(20, 2),  -- Revenue / Employees
            opex_ratio               NUMERIC(20, 8),  -- (SG&A + R&D) / Revenue


            asset_turnover_percentile           NUMERIC(6, 3),  -- Revenue / Avg Total Assets
            cash_conversion_cycle_percentile    NUMERIC(6, 3),  -- DSO + DIO - DPO (days)
            dso_percentile                      NUMERIC(6, 3),  -- Avg AR / Revenue * 365 (days)
            dio_percentile                      NUMERIC(6, 3),  -- Avg Inventory / COGS * 365 (days)
            dpo_percentile                      NUMERIC(6, 3),  -- Avg AP / COGS * 365 (days)
            fixed_asset_turnover_percentile     NUMERIC(6, 3),  -- Revenue / Avg Net PPE
            revenue_per_employee_percentile     NUMERIC(6, 3),  -- Revenue / Employees
            opex_ratio_percentile               NUMERIC(6, 3),  -- (SG&A + R&D) / Revenue
                       
            updated_at                            TIMESTAMPTZ  NOT NULL,
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate
            UNIQUE (tic, date, as_of_date)
        );
        """)
        print("Table 'efficiency_metrics' created or already exists with composite primary key.")


       # Create a table for financial health metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.financial_health_metrics (
            -- Identity & period alignment
            inference_id       UUID,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,
            score          NUMERIC(6, 3),  -- 0-100

            net_debt_to_ebitda_ttm  NUMERIC(20, 6),   -- Net Debt / EBITDA (TTM)
            interest_coverage_ttm   NUMERIC(20, 6),   -- EBIT / Interest Expense (TTM)
            current_ratio           NUMERIC(20, 6),   -- Current Assets / Current Liabilities
            quick_ratio             NUMERIC(20, 6),   -- (Current Assets - Inventory) / Current Liabilities
            cash_ratio              NUMERIC(20, 6),   -- Cash & Equivalents / Current Liabilities
            debt_to_equity          NUMERIC(20, 6),   -- Total Debt / Shareholders' Equity (NULL if equity <= 0)
            debt_to_assets          NUMERIC(20, 6),   -- Total Debt / Total Assets
            altman_z_score          NUMERIC(20, 6),   -- Altman Z-Score
                   
            net_debt_to_ebitda_ttm_percentile  NUMERIC(6, 3),   -- Net Debt / EBITDA (TTM)
            interest_coverage_ttm_percentile   NUMERIC(6, 3),   -- EBIT / Interest Expense (TTM)
            current_ratio_percentile           NUMERIC(6, 3),   -- Current Assets / Current Liabilities
            quick_ratio_percentile             NUMERIC(6, 3),   -- (Current Assets - Inventory) / Current Liabilities
            cash_ratio_percentile              NUMERIC(6, 3),   -- Cash & Equivalents / Current Liabilities
            debt_to_equity_percentile          NUMERIC(6, 3),   -- Total Debt / Shareholders' Equity (NULL if equity <= 0)
            debt_to_assets_percentile          NUMERIC(6, 3),   -- Total Debt / Total Assets
            altman_z_score_percentile          NUMERIC(6, 3),   -- Altman Z-Score
                   
            updated_at                            TIMESTAMPTZ  NOT NULL,
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate
            UNIQUE (tic, date, as_of_date)
        );
        """)
        print("Table 'financial_health_metrics' created or already exists with composite primary key.")

       # Create a table for stock scores if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mart.stock_scores (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,

            valuation_score          NUMERIC(6, 3),  -- 0-100
            profitability_score      NUMERIC(6, 3),  -- 0-100
            growth_score             NUMERIC(6, 3),  -- 0-100
            efficiency_score         NUMERIC(6, 3),  -- 0-100
            financial_health_score   NUMERIC(6, 3),  -- 0-100
            total_score              NUMERIC(6, 3),  -- 0-100
            updated_at                            TIMESTAMPTZ  NOT NULL,
            as_of_date      DATE NOT NULL,       -- date when the data was last confirmed accurate
            UNIQUE (tic, date, as_of_date)
        );
        """)
        print("Table 'stock_scores' created or already exists with composite primary key.")





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