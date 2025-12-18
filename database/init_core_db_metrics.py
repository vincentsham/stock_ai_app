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
        CREATE TABLE IF NOT EXISTS core.earnings_metrics (
            -- Entity & period
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_id           UUID NOT NULL,
            tic               VARCHAR(10) NOT NULL,
            calendar_year       INT         NOT NULL,
            calendar_quarter    SMALLINT    NOT NULL,

            -- Raw values / estimates
            eps               FLOAT,
            eps_estimated     FLOAT,
            revenue           FLOAT,
            revenue_estimated FLOAT,
                       

            -- EPS regime
            eps_regime         VARCHAR(50),

            -- EPS surprise / beats
            eps_surprise               FLOAT,
            eps_beat_flag                  SMALLINT,
            eps_beat_count_4q              SMALLINT,
            eps_beat_streak_length         SMALLINT,

            -- EPS surprise classification
            eps_surprise_class    VARCHAR(50),
            eps_surprise_regime            VARCHAR(50),

            -- Revenue surprise / beats
            revenue_surprise               FLOAT,
            revenue_beat_flag                  SMALLINT,
            revenue_beat_count_4q              SMALLINT,
            revenue_beat_streak_length         SMALLINT,

            -- Revenue surprise classification
            revenue_surprise_class    VARCHAR(50),
            revenue_surprise_regime            VARCHAR(50), 
                       

            -- Bookkeeping
            raw_json_sha256   CHAR(64)    NOT NULL,
            updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            UNIQUE (tic, calendar_year, calendar_quarter),
            UNIQUE (event_id),
            FOREIGN KEY (event_id)
                REFERENCES core.earnings (event_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'earnings_metrics' created or already exists.")


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.analyst_rating_monthly_summary (
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic               VARCHAR(10)   NOT NULL,
            start_date        DATE          NOT NULL,
            end_date          DATE          NOT NULL,

            -- ---- Price Target (pt_) statistics ----
            pt_count          INTEGER       DEFAULT 0,
            pt_high           FLOAT,
            pt_low            FLOAT,
            pt_p25            FLOAT,
            pt_median         FLOAT,
            pt_p75            FLOAT,
            pt_mean           FLOAT,
            pt_stddev         FLOAT,
            pt_dispersion     FLOAT,

            pt_upgrade_n      INTEGER       DEFAULT 0,
            pt_downgrade_n    INTEGER       DEFAULT 0,
            pt_reiterate_n    INTEGER       DEFAULT 0,
            pt_init_n         INTEGER       DEFAULT 0,

            -- ---- Grade statistics ----
            grade_count       INTEGER       DEFAULT 0,
            grade_buy_n       INTEGER       DEFAULT 0,
            grade_hold_n      INTEGER       DEFAULT 0,
            grade_sell_n      INTEGER       DEFAULT 0,
            grade_buy_ratio   FLOAT,
            grade_hold_ratio  FLOAT,
            grade_sell_ratio  FLOAT,
            grade_balance     FLOAT,

            grade_upgrade_n   INTEGER       DEFAULT 0,
            grade_downgrade_n INTEGER       DEFAULT 0,
            grade_reiterate_n INTEGER       DEFAULT 0,
            grade_init_n      INTEGER       DEFAULT 0,

            -- ---- Implied return statistics ----
            ret_mean          FLOAT,
            ret_median        FLOAT,
            ret_p25           FLOAT,
            ret_p75           FLOAT,
            ret_stddev        FLOAT,
            ret_dispersion    FLOAT,
            ret_high          FLOAT,
            ret_low           FLOAT,

            -- ---- Price statistics ----
            price_start       FLOAT,
            price_end         FLOAT,
            price_high        FLOAT,
            price_low         FLOAT,
            price_p25         FLOAT,
            price_median      FLOAT,
            price_p75         FLOAT,
            price_mean        FLOAT,
            price_stddev      FLOAT,

            updated_at        TIMESTAMPTZ DEFAULT NOW(),

            UNIQUE (tic, end_date)
        );
        """)
        print("Table 'analyst_rating_monthly_summary' created or already exists.")


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.analyst_rating_quarterly_summary (
            inferences_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic               VARCHAR(10)   NOT NULL,
            start_date        DATE          NOT NULL,
            end_date          DATE          NOT NULL,

            -- ---- Price Target (pt_) statistics ----
            pt_count          INTEGER       DEFAULT 0,
            pt_high           FLOAT,
            pt_low            FLOAT,
            pt_p25            FLOAT,
            pt_median         FLOAT,
            pt_p75            FLOAT,
            pt_mean           FLOAT,
            pt_stddev         FLOAT,
            pt_dispersion     FLOAT,

            pt_upgrade_n      INTEGER       DEFAULT 0,
            pt_downgrade_n    INTEGER       DEFAULT 0,
            pt_reiterate_n    INTEGER       DEFAULT 0,
            pt_init_n         INTEGER       DEFAULT 0,

            -- ---- Grade statistics ----
            grade_count       INTEGER       DEFAULT 0,
            grade_buy_n       INTEGER       DEFAULT 0,
            grade_hold_n      INTEGER       DEFAULT 0,
            grade_sell_n      INTEGER       DEFAULT 0,
            grade_buy_ratio   FLOAT,
            grade_hold_ratio  FLOAT,
            grade_sell_ratio  FLOAT,
            grade_balance     FLOAT,

            grade_upgrade_n   INTEGER       DEFAULT 0,
            grade_downgrade_n INTEGER       DEFAULT 0,
            grade_reiterate_n INTEGER       DEFAULT 0,
            grade_init_n      INTEGER       DEFAULT 0,

            -- ---- Implied return statistics ----
            ret_mean          FLOAT,
            ret_median        FLOAT,
            ret_p25           FLOAT,
            ret_p75           FLOAT,
            ret_stddev        FLOAT,
            ret_dispersion    FLOAT,
            ret_high          FLOAT,
            ret_low           FLOAT,

            -- ---- Price statistics ----
            price_start       FLOAT,
            price_end         FLOAT,
            price_high        FLOAT,
            price_low         FLOAT,
            price_p25         FLOAT,
            price_median      FLOAT,
            price_p75         FLOAT,
            price_mean        FLOAT,
            price_stddev      FLOAT,

            updated_at        TIMESTAMPTZ DEFAULT NOW(),

            UNIQUE (tic, end_date)
        );
        """)
        print("Table 'analyst_rating_quarterly_summary' created or already exists.")



        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.analyst_rating_yearly_summary (
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic               VARCHAR(10)   NOT NULL,
            start_date        DATE          NOT NULL,
            end_date          DATE          NOT NULL,

            -- ---- Price Target (pt_) statistics ----
            pt_count          INTEGER       DEFAULT 0,
            pt_high           FLOAT,
            pt_low            FLOAT,
            pt_p25            FLOAT,
            pt_median         FLOAT,
            pt_p75            FLOAT,
            pt_mean           FLOAT,
            pt_stddev         FLOAT,
            pt_dispersion     FLOAT,

            pt_upgrade_n      INTEGER       DEFAULT 0,
            pt_downgrade_n    INTEGER       DEFAULT 0,
            pt_reiterate_n    INTEGER       DEFAULT 0,
            pt_init_n         INTEGER       DEFAULT 0,

            -- ---- Grade statistics ----
            grade_count       INTEGER       DEFAULT 0,
            grade_buy_n       INTEGER       DEFAULT 0,
            grade_hold_n      INTEGER       DEFAULT 0,
            grade_sell_n      INTEGER       DEFAULT 0,
            grade_buy_ratio   FLOAT,
            grade_hold_ratio  FLOAT,
            grade_sell_ratio  FLOAT,
            grade_balance     FLOAT,

            grade_upgrade_n   INTEGER       DEFAULT 0,
            grade_downgrade_n INTEGER       DEFAULT 0,
            grade_reiterate_n INTEGER       DEFAULT 0,
            grade_init_n      INTEGER       DEFAULT 0,

            -- ---- Implied return statistics ----
            ret_mean          FLOAT,
            ret_median        FLOAT,
            ret_p25           FLOAT,
            ret_p75           FLOAT,
            ret_stddev        FLOAT,
            ret_dispersion    FLOAT,
            ret_high          FLOAT,
            ret_low           FLOAT,

            -- ---- Price statistics ----
            price_start       FLOAT,
            price_end         FLOAT,
            price_high        FLOAT,
            price_low         FLOAT,
            price_p25         FLOAT,
            price_median      FLOAT,
            price_p75         FLOAT,
            price_mean        FLOAT,
            price_stddev      FLOAT,

            updated_at        TIMESTAMPTZ DEFAULT NOW(),

            UNIQUE (tic, end_date)
        );
        """)
        print("Table 'analyst_rating_yearly_summary' created or already exists.")




       # Create a table for revenue metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.revenue_metrics (
            -- Identity & period alignment
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_id           UUID NOT NULL,
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- Revenue Metrics
            revenue                        BIGINT,
            revenue_ttm                        BIGINT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            revenue_qoq_growth             FLOAT,
            revenue_qoq_positive_flag        SMALLINT,
            revenue_qoq_count_4q                SMALLINT,
            revenue_qoq_streak_length           SMALLINT,
            revenue_qoq_growth_class        VARCHAR(50),
            revenue_qoq_growth_regime          VARCHAR(50), 
                       
            revenue_qoq_volatility_4q        FLOAT,
            revenue_qoq_volatility_flag           SMALLINT,
            revenue_qoq_growth_drift             FLOAT,
            revenue_qoq_outlier_flag               SMALLINT,
            revenue_qoq_stability_regime        VARCHAR(50),
                       
            revenue_qoq_accel                  FLOAT,
            revenue_qoq_accel_count_4q             SMALLINT,  
            revenue_qoq_accel_positive_flag        SMALLINT,
            revenue_qoq_accel_streak_length           SMALLINT,
            revenue_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            revenue_yoy_growth             FLOAT,
            revenue_yoy_positive_flag        SMALLINT,
            revenue_yoy_count_4q                SMALLINT,
            revenue_yoy_streak_length           SMALLINT,
            revenue_yoy_growth_class        VARCHAR(50),
            revenue_yoy_growth_regime          VARCHAR(50),
            
            revenue_yoy_volatility_4q        FLOAT,
            revenue_yoy_volatility_flag           SMALLINT,
            revenue_yoy_growth_drift             FLOAT,
            revenue_yoy_outlier_flag               SMALLINT,
            revenue_yoy_stability_regime        VARCHAR(50),

            revenue_yoy_accel                  FLOAT,
            revenue_yoy_accel_count_4q             SMALLINT,  
            revenue_yoy_accel_positive_flag        SMALLINT,
            revenue_yoy_accel_streak_length           SMALLINT,
            revenue_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            revenue_ttm_growth             FLOAT,
            revenue_ttm_positive_flag        SMALLINT,
            revenue_ttm_count_4q                SMALLINT,
            revenue_ttm_streak_length           SMALLINT,
            revenue_ttm_growth_class        VARCHAR(50),
            revenue_ttm_growth_regime          VARCHAR(50),

            revenue_ttm_volatility_4q        FLOAT,
            revenue_ttm_volatility_flag           SMALLINT,
            revenue_ttm_growth_drift             FLOAT,
            revenue_ttm_outlier_flag               SMALLINT,
            revenue_ttm_stability_regime        VARCHAR(50),

            revenue_ttm_accel                  FLOAT,
            revenue_ttm_accel_count_4q             SMALLINT,
            revenue_ttm_accel_positive_flag        SMALLINT,
            revenue_ttm_accel_streak_length           SMALLINT,
            revenue_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

            UNIQUE (tic, calendar_year, calendar_quarter),
            UNIQUE (event_id),
            FOREIGN KEY (event_id)
                REFERENCES core.earnings (event_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'revenue_metrics' created or already exists with composite primary key.")



       # Create a table for earnings per share diluted (EPS diluted) metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.eps_diluted_metrics (
            -- Identity & period alignment
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_id           UUID NOT NULL,
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            eps_diluted                           NUMERIC(10,2),
            eps_diluted_ttm                       NUMERIC(10,2),
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            eps_diluted_qoq_growth             FLOAT,
            eps_diluted_qoq_positive_flag        SMALLINT,
            eps_diluted_qoq_count_4q                SMALLINT,
            eps_diluted_qoq_streak_length           SMALLINT,
            eps_diluted_qoq_growth_class        VARCHAR(50),
            eps_diluted_qoq_growth_regime          VARCHAR(50), 
                       
            eps_diluted_qoq_volatility_4q        FLOAT,
            eps_diluted_qoq_volatility_flag           SMALLINT,
            eps_diluted_qoq_growth_drift             FLOAT,
            eps_diluted_qoq_outlier_flag               SMALLINT,
            eps_diluted_qoq_stability_regime        VARCHAR(50),
                       
            eps_diluted_qoq_accel                  FLOAT,
            eps_diluted_qoq_accel_count_4q             SMALLINT,  
            eps_diluted_qoq_accel_positive_flag        SMALLINT,
            eps_diluted_qoq_accel_streak_length           SMALLINT,
            eps_diluted_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            eps_diluted_yoy_growth             FLOAT,
            eps_diluted_yoy_positive_flag        SMALLINT,
            eps_diluted_yoy_count_4q                SMALLINT,
            eps_diluted_yoy_streak_length           SMALLINT,
            eps_diluted_yoy_growth_class        VARCHAR(50),
            eps_diluted_yoy_growth_regime          VARCHAR(50),
            
            eps_diluted_yoy_volatility_4q        FLOAT,
            eps_diluted_yoy_volatility_flag           SMALLINT,
            eps_diluted_yoy_growth_drift             FLOAT,
            eps_diluted_yoy_outlier_flag               SMALLINT,
            eps_diluted_yoy_stability_regime        VARCHAR(50),

            eps_diluted_yoy_accel                  FLOAT,
            eps_diluted_yoy_accel_count_4q             SMALLINT,  
            eps_diluted_yoy_accel_positive_flag        SMALLINT,
            eps_diluted_yoy_accel_streak_length           SMALLINT,
            eps_diluted_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            eps_diluted_ttm_growth             FLOAT,
            eps_diluted_ttm_positive_flag        SMALLINT,
            eps_diluted_ttm_count_4q                SMALLINT,
            eps_diluted_ttm_streak_length           SMALLINT,
            eps_diluted_ttm_growth_class        VARCHAR(50),
            eps_diluted_ttm_growth_regime          VARCHAR(50),

            eps_diluted_ttm_volatility_4q        FLOAT,
            eps_diluted_ttm_volatility_flag           SMALLINT,
            eps_diluted_ttm_growth_drift             FLOAT,
            eps_diluted_ttm_outlier_flag               SMALLINT,
            eps_diluted_ttm_stability_regime        VARCHAR(50),

            eps_diluted_ttm_accel                  FLOAT,
            eps_diluted_ttm_accel_count_4q             SMALLINT,
            eps_diluted_ttm_accel_positive_flag        SMALLINT,
            eps_diluted_ttm_accel_streak_length           SMALLINT,
            eps_diluted_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
                       
            UNIQUE (tic, calendar_year, calendar_quarter),
            UNIQUE (event_id),
            FOREIGN KEY (event_id)
                REFERENCES core.earnings (event_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'eps_diluted_metrics' created or already exists with composite primary key.")


       # Create a table for valuation metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.valuation_metrics (
            -- Identity & period alignment
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,
                       
            market_cap          NUMERIC(20, 2),   -- price * diluted shares
            pe_ttm              NUMERIC(20, 6),   -- Price / EPS (TTM)
            pe_forward          NUMERIC(20, 6),   -- Price / Forward EPS

            ev_to_ebitda_ttm    NUMERIC(20, 6),   -- EV / EBITDA (TTM)
            fcf_yield_ttm       NUMERIC(20, 8),   -- FCF / Market Cap (TTM)
            ps_ttm              NUMERIC(20, 6),   -- Price / Sales (TTM)
            
            

            /* =========================
                ➕ Contextual
                ========================= */

            ev_to_revenue_ttm   NUMERIC(20, 6),   -- EV / Revenue (TTM)
            p_to_fcf_ttm        NUMERIC(20, 6),   -- Price / Free Cash Flow (TTM)
            peg_ratio           NUMERIC(20, 6),   -- PE / EPS growth (explicit growth basis)
            peg_ratio_forward           NUMERIC(20, 6),   -- PE / EPS growth (explicit growth basis)
            price_to_book       NUMERIC(20, 6),   -- Market Cap / Equity

            /* =========================
                🧠 Advanced (Optional)
                ========================= */

            ev_to_fcf_ttm       NUMERIC(20, 6),   -- EV / FCF (TTM)
            earnings_yield_ttm  NUMERIC(20, 8),   -- EPS / Price  (or NI / Market Cap)
            revenue_yield_ttm   NUMERIC(20, 8),   -- Revenue / Market Cap

            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, date)
        );
        """)
        print("Table 'valuation_metrics' created or already exists with composite primary key.")


       # Create a table for profitability metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.profitability_metrics (
            -- Identity & period alignment
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,

            gross_margin         NUMERIC(20, 8),  -- (Revenue - COGS) / Revenue
            operating_margin     NUMERIC(20, 8),  -- EBIT / Revenue
            ebitda_margin        NUMERIC(20, 8),  -- EBITDA / Revenue
            net_margin           NUMERIC(20, 8),  -- Net Income / Revenue

            /* =========================
                Expand for More
                ========================= */

            roe                  NUMERIC(20, 8),  -- Net Income / Avg Equity
            roa                  NUMERIC(20, 8),  -- Net Income / Avg Assets
            ocf_margin           NUMERIC(20, 8),  -- Operating Cash Flow / Revenue
            fcf_margin           NUMERIC(20, 8),  -- Free Cash Flow / Revenue
                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, date)
        );
        """)
        print("Table 'profitability_metrics' created or already exists with composite primary key.")


       # Create a table for growth metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.growth_metrics (
            -- Identity & period alignment
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,

            /* =========================
                Default View (UX)
                ========================= */

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

            /* =========================
                Expand for More
                ========================= */
                          
            operating_income_growth_yoy NUMERIC(20, 8), -- optional (EBIT / OpInc)

            forward_revenue_growth   NUMERIC(20, 8),  -- optional, expected
            forward_eps_growth       NUMERIC(20, 8),  -- optional, expected

                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, date)
        );
        """)
        print("Table 'growth_metrics' created or already exists with composite primary key.")



       # Create a table for efficiency metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.efficiency_metrics (
            -- Identity & period alignment
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,
                
            /* =========================
                Default View (UX)
                ========================= */

            asset_turnover           NUMERIC(20, 8),  -- Revenue / Avg Total Assets
            cash_conversion_cycle    NUMERIC(20, 6),  -- DSO + DIO - DPO (days)
            dso                      NUMERIC(20, 6),  -- Avg AR / Revenue * 365 (days)
            dio                      NUMERIC(20, 6),  -- Avg Inventory / COGS * 365 (days)
            dpo                      NUMERIC(20, 6),  -- Avg AP / COGS * 365 (days)

            /* =========================
                Expand for More
                ========================= */

            fixed_asset_turnover     NUMERIC(20, 8),  -- Revenue / Avg Net PPE
            revenue_per_employee     NUMERIC(20, 2),  -- Revenue / Employees
            opex_ratio               NUMERIC(20, 8),  -- (SG&A + R&D) / Revenue

                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, date)
        );
        """)
        print("Table 'efficiency_metrics' created or already exists with composite primary key.")



       # Create a table for financial health metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.financial_health_metrics (
            -- Identity & period alignment
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,

            /* =========================
                Default View (UX)
                ========================= */

            net_debt_to_ebitda_ttm  NUMERIC(20, 6),   -- Net Debt / EBITDA (TTM)
            interest_coverage_ttm   NUMERIC(20, 6),   -- EBIT / Interest Expense (TTM)
            current_ratio           NUMERIC(20, 6),   -- Current Assets / Current Liabilities

            /* =========================
                Expand for More
                ========================= */

            quick_ratio             NUMERIC(20, 6),   -- (Current Assets - Inventory) / Current Liabilities
            cash_ratio              NUMERIC(20, 6),   -- Cash & Equivalents / Current Liabilities

            debt_to_equity          NUMERIC(20, 6),   -- Total Debt / Shareholders' Equity (NULL if equity <= 0)
            debt_to_assets          NUMERIC(20, 6),   -- Total Debt / Total Assets
                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, date)
        );
        """)
        print("Table 'financial_health_metrics' created or already exists with composite primary key.")


       # Create a table for capital allocation metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.capital_allocation_metrics (
            -- Identity & period alignment
            inference_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,

            -- Default View (UX)
            roic                   NUMERIC(20,8),  -- NOPAT_TTM / Avg Invested Capital
            total_shareholder_yield NUMERIC(20,8), -- dividend_yield + buyback_yield
            share_count_change_yoy     NUMERIC(20,8),  -- dilution / accretion

            -- Expand (Advanced)
            reinvestment_rate         NUMERIC(20,8),  -- (CapEx + ΔWC) / NOPAT_TTM
            fcf_per_share_growth_yoy   NUMERIC(20,8),  -- YoY growth of (FCF_TTM / diluted shares)

                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, date)
        );
        """)
        print("Table 'capital_allocation_metrics' created or already exists with composite primary key.")


       # Create a table for valuation percentiles if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.valuation_percentiles (
            -- Identity & period alignment
            inference_id                      UUID         NOT NULL,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,
                       
            market_cap_percentile          NUMERIC(6, 3),   -- price * diluted shares
            pe_ttm_percentile             NUMERIC(6, 3),   -- Price / EPS (TTM)
            pe_forward_percentile        NUMERIC(6, 3),   -- Price / Forward EPS

            ev_to_ebitda_ttm_percentile    NUMERIC(6, 3),   -- EV / EBITDA (TTM)
            fcf_yield_ttm_percentile       NUMERIC(6, 3),   -- FCF / Market Cap (TTM)
            ps_ttm_percentile              NUMERIC(6, 3),   -- Price / Sales (TTM)
            
            /* =========================
                ➕ Contextual
                ========================= */

            ev_to_revenue_ttm_percentile   NUMERIC(6, 3),   -- EV / Revenue (TTM)
            p_to_fcf_ttm_percentile        NUMERIC(6, 3),   -- Price / Free Cash Flow (TTM)
            peg_ratio_percentile           NUMERIC(6, 3),   -- PE / EPS growth (explicit growth basis)
            peg_ratio_forward_percentile           NUMERIC(6, 3),   -- PE / EPS growth (explicit growth basis)
            price_to_book_percentile       NUMERIC(6, 3),   -- Market Cap / Equity

            /* =========================
                🧠 Advanced (Optional)
                ========================= */

            ev_to_fcf_ttm_percentile       NUMERIC(6, 3),   -- EV / FCF (TTM)
            earnings_yield_ttm_percentile  NUMERIC(6, 3),   -- EPS / Price  (or NI / Market Cap)
            revenue_yield_ttm_percentile   NUMERIC(6, 3),   -- Revenue / Market Cap

            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            
            UNIQUE (tic, date),
            UNIQUE (inference_id),
            FOREIGN KEY (inference_id)
                REFERENCES core.valuation_metrics (inference_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'valuation_percentiles' created or already exists with composite primary key.")



       # Create a table for profitability percentiles if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.profitability_percentiles (
            -- Identity & period alignment
            inference_id       UUID NOT NULL,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,

            gross_margin_percentile         NUMERIC(6, 3),  -- (Revenue - COGS) / Revenue
            operating_margin_percentile     NUMERIC(6, 3),  -- EBIT / Revenue
            ebitda_margin_percentile        NUMERIC(6, 3),  -- EBITDA / Revenue
            net_margin_percentile           NUMERIC(6, 3),  -- Net Income / Revenue

            /* =========================
                Expand for More
                ========================= */

            roe_percentile                  NUMERIC(6, 3),  -- Net Income / Avg Equity
            roa_percentile                  NUMERIC(6, 3),  -- Net Income / Avg Assets
            ocf_margin_percentile           NUMERIC(6, 3),  -- Operating Cash Flow / Revenue
            fcf_margin_percentile           NUMERIC(6, 3),  -- Free Cash Flow / Revenue
                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

            UNIQUE (tic, date),
            UNIQUE (inference_id),
            FOREIGN KEY (inference_id)
                REFERENCES core.profitability_metrics (inference_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'profitability_percentiles' created or already exists with composite primary key.")


       # Create a table for growth percentiles if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.growth_percentiles (
            -- Identity & period alignment
            inference_id       UUID NOT NULL,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,

            /* =========================
                Default View (UX)
                ========================= */

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
                       
            /* =========================
                Expand for More
                ========================= */


                     
            operating_income_growth_yoy_percentile NUMERIC(6, 3), -- optional (EBIT / OpInc)

            forward_revenue_growth_percentile   NUMERIC(6, 3),  -- optional, expected
            forward_eps_growth_percentile       NUMERIC(6, 3),  -- optional, expected
                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

            UNIQUE (tic, date),
            UNIQUE (inference_id),
            FOREIGN KEY (inference_id)
                REFERENCES core.growth_metrics (inference_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'growth_percentiles' created or already exists with composite primary key.")



       # Create a table for efficiency percentiles if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.efficiency_percentiles (
            -- Identity & period alignment
            inference_id       UUID NOT NULL,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,
                
            /* =========================
                Default View (UX)
                ========================= */

            asset_turnover_percentile           NUMERIC(6, 3),  -- Revenue / Avg Total Assets
            cash_conversion_cycle_percentile    NUMERIC(6, 3),  -- DSO + DIO - DPO (days)
            dso_percentile                      NUMERIC(6, 3),  -- Avg AR / Revenue * 365 (days)
            dio_percentile                      NUMERIC(6, 3),  -- Avg Inventory / COGS * 365 (days)
            dpo_percentile                      NUMERIC(6, 3),  -- Avg AP / COGS * 365 (days)
            /* =========================
                Expand for More
                ========================= */

            fixed_asset_turnover_percentile     NUMERIC(6, 3),  -- Revenue / Avg Net PPE
            revenue_per_employee_percentile     NUMERIC(6, 3),  -- Revenue / Employees
            opex_ratio_percentile               NUMERIC(6, 3),  -- (SG&A + R&D) / Revenue

                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

            UNIQUE (tic, date),
            UNIQUE (inference_id),
            FOREIGN KEY (inference_id)
                REFERENCES core.efficiency_metrics (inference_id)
                ON DELETE CASCADE
                       
        );
        """)
        print("Table 'efficiency_percentiles' created or already exists with composite primary key.")



       # Create a table for financial health percentiles if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.financial_health_percentiles (
            -- Identity & period alignment
            inference_id       UUID NOT NULL,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,

            /* =========================
                Default View (UX)
                ========================= */

            net_debt_to_ebitda_ttm_percentile  NUMERIC(6, 3),   -- Net Debt / EBITDA (TTM)
            interest_coverage_ttm_percentile   NUMERIC(6, 3),   -- EBIT / Interest Expense (TTM)
            current_ratio_percentile           NUMERIC(6, 3),   -- Current Assets / Current Liabilities

            /* =========================
                Expand for More
                ========================= */

            quick_ratio_percentile             NUMERIC(6, 3),   -- (Current Assets - Inventory) / Current Liabilities
            cash_ratio_percentile              NUMERIC(6, 3),   -- Cash & Equivalents / Current Liabilities

            debt_to_equity_percentile          NUMERIC(6, 3),   -- Total Debt / Shareholders' Equity (NULL if equity <= 0)
            debt_to_assets_percentile          NUMERIC(6, 3),   -- Total Debt / Total Assets

                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, date),
            UNIQUE (inference_id),
            FOREIGN KEY (inference_id)
                REFERENCES core.financial_health_metrics (inference_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'financial_health_percentiles' created or already exists with composite primary key.")


       # Create a table for capital allocation percentiles if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.capital_allocation_percentiles (
            -- Identity & period alignment
            inference_id       UUID NOT NULL,
            tic                               VARCHAR(10)  NOT NULL,
            date                              DATE         NOT NULL,

            -- Default View (UX)
            roic_percentile                   NUMERIC(6,3),  -- NOPAT_TTM / Avg Invested Capital
            total_shareholder_yield_percentile NUMERIC(6,3), -- dividend_yield + buyback_yield
            share_count_change_yoy_percentile     NUMERIC(6,3),  -- dilution / accretion

            -- Expand (Advanced)
            reinvestment_rate_percentile         NUMERIC(6,3),  -- (CapEx + ΔWC) / NOPAT_TTM
            fcf_per_share_growth_yoy_percentile   NUMERIC(6,3),  -- YoY growth of (FCF_TTM / diluted shares)
                   
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (tic, date),
            UNIQUE (inference_id),
            FOREIGN KEY (inference_id)
                REFERENCES core.capital_allocation_metrics (inference_id)
                ON DELETE CASCADE
        );
        """)
        print("Table 'capital_allocation_percentiles' created or already exists with composite primary key.")




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