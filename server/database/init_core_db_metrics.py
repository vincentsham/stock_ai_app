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


       # Create a table for revenue metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.revenue_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- Revenue Metrics
            revenue                        BIGINT,
            revenue_ttm                        BIGINT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            revenue_qoq_growth_pct             FLOAT,
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
            revenue_yoy_growth_pct             FLOAT,
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
            revenue_ttm_growth_pct             FLOAT,
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
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'revenue_metrics' created or already exists with composite primary key.")



       # Create a table for earnings per share diluted (EPS diluted) metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.eps_diluted_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            eps_diluted                           NUMERIC(10,2),
            eps_diluted_ttm                       NUMERIC(10,2),
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            eps_diluted_qoq_growth_pct             FLOAT,
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
            eps_diluted_yoy_growth_pct             FLOAT,
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
            eps_diluted_ttm_growth_pct             FLOAT,
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
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'eps_diluted_metrics' created or already exists with composite primary key.")




       # Create a table for gross profit metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.gross_profit_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            gross_profit                           BIGINT,
            gross_profit_ttm                       BIGINT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            gross_profit_qoq_growth_pct             FLOAT,
            gross_profit_qoq_positive_flag        SMALLINT,
            gross_profit_qoq_count_4q                SMALLINT,
            gross_profit_qoq_streak_length           SMALLINT,
            gross_profit_qoq_growth_class        VARCHAR(50),
            gross_profit_qoq_growth_regime          VARCHAR(50), 
                       
            gross_profit_qoq_volatility_4q        FLOAT,
            gross_profit_qoq_volatility_flag           SMALLINT,
            gross_profit_qoq_growth_drift             FLOAT,
            gross_profit_qoq_outlier_flag               SMALLINT,
            gross_profit_qoq_stability_regime        VARCHAR(50),
                       
            gross_profit_qoq_accel                  FLOAT,
            gross_profit_qoq_accel_count_4q             SMALLINT,  
            gross_profit_qoq_accel_positive_flag        SMALLINT,
            gross_profit_qoq_accel_streak_length           SMALLINT,
            gross_profit_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            gross_profit_yoy_growth_pct             FLOAT,
            gross_profit_yoy_positive_flag        SMALLINT,
            gross_profit_yoy_count_4q                SMALLINT,
            gross_profit_yoy_streak_length           SMALLINT,
            gross_profit_yoy_growth_class        VARCHAR(50),
            gross_profit_yoy_growth_regime          VARCHAR(50),
            
            gross_profit_yoy_volatility_4q        FLOAT,
            gross_profit_yoy_volatility_flag           SMALLINT,
            gross_profit_yoy_growth_drift             FLOAT,
            gross_profit_yoy_outlier_flag               SMALLINT,
            gross_profit_yoy_stability_regime        VARCHAR(50),

            gross_profit_yoy_accel                  FLOAT,
            gross_profit_yoy_accel_count_4q             SMALLINT,  
            gross_profit_yoy_accel_positive_flag        SMALLINT,
            gross_profit_yoy_accel_streak_length           SMALLINT,
            gross_profit_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            gross_profit_ttm_growth_pct             FLOAT,
            gross_profit_ttm_positive_flag        SMALLINT,
            gross_profit_ttm_count_4q                SMALLINT,
            gross_profit_ttm_streak_length           SMALLINT,
            gross_profit_ttm_growth_class        VARCHAR(50),
            gross_profit_ttm_growth_regime          VARCHAR(50),

            gross_profit_ttm_volatility_4q        FLOAT,
            gross_profit_ttm_volatility_flag           SMALLINT,
            gross_profit_ttm_growth_drift             FLOAT,
            gross_profit_ttm_outlier_flag               SMALLINT,
            gross_profit_ttm_stability_regime        VARCHAR(50),

            gross_profit_ttm_accel                  FLOAT,
            gross_profit_ttm_accel_count_4q             SMALLINT,
            gross_profit_ttm_accel_positive_flag        SMALLINT,
            gross_profit_ttm_accel_streak_length           SMALLINT,
            gross_profit_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'gross_profit_metrics' created or already exists with composite primary key.")



       # Create a table for ebit metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.ebit_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            ebit                           BIGINT,
            ebit_ttm                       BIGINT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            ebit_qoq_growth_pct             FLOAT,
            ebit_qoq_positive_flag        SMALLINT,
            ebit_qoq_count_4q                SMALLINT,
            ebit_qoq_streak_length           SMALLINT,
            ebit_qoq_growth_class        VARCHAR(50),
            ebit_qoq_growth_regime          VARCHAR(50), 
                       
            ebit_qoq_volatility_4q        FLOAT,
            ebit_qoq_volatility_flag           SMALLINT,
            ebit_qoq_growth_drift             FLOAT,
            ebit_qoq_outlier_flag               SMALLINT,
            ebit_qoq_stability_regime        VARCHAR(50),
                       
            ebit_qoq_accel                  FLOAT,
            ebit_qoq_accel_count_4q             SMALLINT,  
            ebit_qoq_accel_positive_flag        SMALLINT,
            ebit_qoq_accel_streak_length           SMALLINT,
            ebit_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            ebit_yoy_growth_pct             FLOAT,
            ebit_yoy_positive_flag        SMALLINT,
            ebit_yoy_count_4q                SMALLINT,
            ebit_yoy_streak_length           SMALLINT,
            ebit_yoy_growth_class        VARCHAR(50),
            ebit_yoy_growth_regime          VARCHAR(50),
            
            ebit_yoy_volatility_4q        FLOAT,
            ebit_yoy_volatility_flag           SMALLINT,
            ebit_yoy_growth_drift             FLOAT,
            ebit_yoy_outlier_flag               SMALLINT,
            ebit_yoy_stability_regime        VARCHAR(50),

            ebit_yoy_accel                  FLOAT,
            ebit_yoy_accel_count_4q             SMALLINT,  
            ebit_yoy_accel_positive_flag        SMALLINT,
            ebit_yoy_accel_streak_length           SMALLINT,
            ebit_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            ebit_ttm_growth_pct             FLOAT,
            ebit_ttm_positive_flag        SMALLINT,
            ebit_ttm_count_4q                SMALLINT,
            ebit_ttm_streak_length           SMALLINT,
            ebit_ttm_growth_class        VARCHAR(50),
            ebit_ttm_growth_regime          VARCHAR(50),

            ebit_ttm_volatility_4q        FLOAT,
            ebit_ttm_volatility_flag           SMALLINT,
            ebit_ttm_growth_drift             FLOAT,
            ebit_ttm_outlier_flag               SMALLINT,
            ebit_ttm_stability_regime        VARCHAR(50),

            ebit_ttm_accel                  FLOAT,
            ebit_ttm_accel_count_4q             SMALLINT,
            ebit_ttm_accel_positive_flag        SMALLINT,
            ebit_ttm_accel_streak_length           SMALLINT,
            ebit_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'ebit_metrics' created or already exists with composite primary key.")



       # Create a table for profit margin metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.profit_margin_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            profit_margin                           FLOAT,
            profit_margin_ttm                       FLOAT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            profit_margin_qoq_growth_pct             FLOAT,
            profit_margin_qoq_positive_flag        SMALLINT,
            profit_margin_qoq_count_4q                SMALLINT,
            profit_margin_qoq_streak_length           SMALLINT,
            profit_margin_qoq_growth_class        VARCHAR(50),
            profit_margin_qoq_growth_regime          VARCHAR(50), 
                       
            profit_margin_qoq_volatility_4q        FLOAT,
            profit_margin_qoq_volatility_flag           SMALLINT,
            profit_margin_qoq_growth_drift             FLOAT,
            profit_margin_qoq_outlier_flag               SMALLINT,
            profit_margin_qoq_stability_regime        VARCHAR(50),
                       
            profit_margin_qoq_accel                  FLOAT,
            profit_margin_qoq_accel_count_4q             SMALLINT,  
            profit_margin_qoq_accel_positive_flag        SMALLINT,
            profit_margin_qoq_accel_streak_length           SMALLINT,
            profit_margin_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            profit_margin_yoy_growth_pct             FLOAT,
            profit_margin_yoy_positive_flag        SMALLINT,
            profit_margin_yoy_count_4q                SMALLINT,
            profit_margin_yoy_streak_length           SMALLINT,
            profit_margin_yoy_growth_class        VARCHAR(50),
            profit_margin_yoy_growth_regime          VARCHAR(50),
            
            profit_margin_yoy_volatility_4q        FLOAT,
            profit_margin_yoy_volatility_flag           SMALLINT,
            profit_margin_yoy_growth_drift             FLOAT,
            profit_margin_yoy_outlier_flag               SMALLINT,
            profit_margin_yoy_stability_regime        VARCHAR(50),

            profit_margin_yoy_accel                  FLOAT,
            profit_margin_yoy_accel_count_4q             SMALLINT,  
            profit_margin_yoy_accel_positive_flag        SMALLINT,
            profit_margin_yoy_accel_streak_length           SMALLINT,
            profit_margin_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            profit_margin_ttm_growth_pct             FLOAT,
            profit_margin_ttm_positive_flag        SMALLINT,
            profit_margin_ttm_count_4q                SMALLINT,
            profit_margin_ttm_streak_length           SMALLINT,
            profit_margin_ttm_growth_class        VARCHAR(50),
            profit_margin_ttm_growth_regime          VARCHAR(50),

            profit_margin_ttm_volatility_4q        FLOAT,
            profit_margin_ttm_volatility_flag           SMALLINT,
            profit_margin_ttm_growth_drift             FLOAT,
            profit_margin_ttm_outlier_flag               SMALLINT,
            profit_margin_ttm_stability_regime        VARCHAR(50),

            profit_margin_ttm_accel                  FLOAT,
            profit_margin_ttm_accel_count_4q             SMALLINT,
            profit_margin_ttm_accel_positive_flag        SMALLINT,
            profit_margin_ttm_accel_streak_length           SMALLINT,
            profit_margin_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'profit_margin_metrics' created or already exists with composite primary key.")


       # Create a table for Operating Cash Flow (OCF) metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.ocf_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            ocf                           BIGINT,
            ocf_ttm                       BIGINT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            ocf_qoq_growth_pct             FLOAT,
            ocf_qoq_positive_flag        SMALLINT,
            ocf_qoq_count_4q                SMALLINT,
            ocf_qoq_streak_length           SMALLINT,
            ocf_qoq_growth_class        VARCHAR(50),
            ocf_qoq_growth_regime          VARCHAR(50), 
                       
            ocf_qoq_volatility_4q        FLOAT,
            ocf_qoq_volatility_flag           SMALLINT,
            ocf_qoq_growth_drift             FLOAT,
            ocf_qoq_outlier_flag               SMALLINT,
            ocf_qoq_stability_regime        VARCHAR(50),
                       
            ocf_qoq_accel                  FLOAT,
            ocf_qoq_accel_count_4q             SMALLINT,  
            ocf_qoq_accel_positive_flag        SMALLINT,
            ocf_qoq_accel_streak_length           SMALLINT,
            ocf_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            ocf_yoy_growth_pct             FLOAT,
            ocf_yoy_positive_flag        SMALLINT,
            ocf_yoy_count_4q                SMALLINT,
            ocf_yoy_streak_length           SMALLINT,
            ocf_yoy_growth_class        VARCHAR(50),
            ocf_yoy_growth_regime          VARCHAR(50),
            
            ocf_yoy_volatility_4q        FLOAT,
            ocf_yoy_volatility_flag           SMALLINT,
            ocf_yoy_growth_drift             FLOAT,
            ocf_yoy_outlier_flag               SMALLINT,
            ocf_yoy_stability_regime        VARCHAR(50),

            ocf_yoy_accel                  FLOAT,
            ocf_yoy_accel_count_4q             SMALLINT,  
            ocf_yoy_accel_positive_flag        SMALLINT,
            ocf_yoy_accel_streak_length           SMALLINT,
            ocf_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            ocf_ttm_growth_pct             FLOAT,
            ocf_ttm_positive_flag        SMALLINT,
            ocf_ttm_count_4q                SMALLINT,
            ocf_ttm_streak_length           SMALLINT,
            ocf_ttm_growth_class        VARCHAR(50),
            ocf_ttm_growth_regime          VARCHAR(50),

            ocf_ttm_volatility_4q        FLOAT,
            ocf_ttm_volatility_flag           SMALLINT,
            ocf_ttm_growth_drift             FLOAT,
            ocf_ttm_outlier_flag               SMALLINT,
            ocf_ttm_stability_regime        VARCHAR(50),

            ocf_ttm_accel                  FLOAT,
            ocf_ttm_accel_count_4q             SMALLINT,
            ocf_ttm_accel_positive_flag        SMALLINT,
            ocf_ttm_accel_streak_length           SMALLINT,
            ocf_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'ocf_metrics' created or already exists with composite primary key.")



       # Create a table for Free Cash Flow (FCF) metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.fcf_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            fcf                           BIGINT,
            fcf_ttm                       BIGINT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            fcf_qoq_growth_pct             FLOAT,
            fcf_qoq_positive_flag        SMALLINT,
            fcf_qoq_count_4q                SMALLINT,
            fcf_qoq_streak_length           SMALLINT,
            fcf_qoq_growth_class        VARCHAR(50),
            fcf_qoq_growth_regime          VARCHAR(50), 
                       
            fcf_qoq_volatility_4q        FLOAT,
            fcf_qoq_volatility_flag           SMALLINT,
            fcf_qoq_growth_drift             FLOAT,
            fcf_qoq_outlier_flag               SMALLINT,
            fcf_qoq_stability_regime        VARCHAR(50),
                       
            fcf_qoq_accel                  FLOAT,
            fcf_qoq_accel_count_4q             SMALLINT,  
            fcf_qoq_accel_positive_flag        SMALLINT,
            fcf_qoq_accel_streak_length           SMALLINT,
            fcf_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            fcf_yoy_growth_pct             FLOAT,
            fcf_yoy_positive_flag        SMALLINT,
            fcf_yoy_count_4q                SMALLINT,
            fcf_yoy_streak_length           SMALLINT,
            fcf_yoy_growth_class        VARCHAR(50),
            fcf_yoy_growth_regime          VARCHAR(50),
            
            fcf_yoy_volatility_4q        FLOAT,
            fcf_yoy_volatility_flag           SMALLINT,
            fcf_yoy_growth_drift             FLOAT,
            fcf_yoy_outlier_flag               SMALLINT,
            fcf_yoy_stability_regime        VARCHAR(50),

            fcf_yoy_accel                  FLOAT,
            fcf_yoy_accel_count_4q             SMALLINT,  
            fcf_yoy_accel_positive_flag        SMALLINT,
            fcf_yoy_accel_streak_length           SMALLINT,
            fcf_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            fcf_ttm_growth_pct             FLOAT,
            fcf_ttm_positive_flag        SMALLINT,
            fcf_ttm_count_4q                SMALLINT,
            fcf_ttm_streak_length           SMALLINT,
            fcf_ttm_growth_class        VARCHAR(50),
            fcf_ttm_growth_regime          VARCHAR(50),

            fcf_ttm_volatility_4q        FLOAT,
            fcf_ttm_volatility_flag           SMALLINT,
            fcf_ttm_growth_drift             FLOAT,
            fcf_ttm_outlier_flag               SMALLINT,
            fcf_ttm_stability_regime        VARCHAR(50),

            fcf_ttm_accel                  FLOAT,
            fcf_ttm_accel_count_4q             SMALLINT,
            fcf_ttm_accel_positive_flag        SMALLINT,
            fcf_ttm_accel_streak_length           SMALLINT,
            fcf_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'fcf_metrics' created or already exists with composite primary key.")




       # Create a table for Free Cash Flow Margin (FCF Margin) metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.fcf_margin_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            fcf_margin                           FLOAT,
            fcf_margin_ttm                       FLOAT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            fcf_margin_qoq_growth_pct          FLOAT,
            fcf_margin_qoq_positive_flag        SMALLINT,
            fcf_margin_qoq_count_4q                SMALLINT,
            fcf_margin_qoq_streak_length           SMALLINT,
            fcf_margin_qoq_growth_class        VARCHAR(50),
            fcf_margin_qoq_growth_regime          VARCHAR(50), 
                       
            fcf_margin_qoq_volatility_4q        FLOAT,
            fcf_margin_qoq_volatility_flag           SMALLINT,
            fcf_margin_qoq_growth_drift             FLOAT,
            fcf_margin_qoq_outlier_flag               SMALLINT,
            fcf_margin_qoq_stability_regime        VARCHAR(50),
                       
            fcf_margin_qoq_accel                  FLOAT,
            fcf_margin_qoq_accel_count_4q             SMALLINT,  
            fcf_margin_qoq_accel_positive_flag        SMALLINT,
            fcf_margin_qoq_accel_streak_length           SMALLINT,
            fcf_margin_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            fcf_margin_yoy_growth_pct             FLOAT,
            fcf_margin_yoy_positive_flag        SMALLINT,
            fcf_margin_yoy_count_4q                SMALLINT,
            fcf_margin_yoy_streak_length           SMALLINT,
            fcf_margin_yoy_growth_class        VARCHAR(50),
            fcf_margin_yoy_growth_regime          VARCHAR(50),
            
            fcf_margin_yoy_volatility_4q        FLOAT,
            fcf_margin_yoy_volatility_flag           SMALLINT,
            fcf_margin_yoy_growth_drift             FLOAT,
            fcf_margin_yoy_outlier_flag               SMALLINT,
            fcf_margin_yoy_stability_regime        VARCHAR(50),

            fcf_margin_yoy_accel                  FLOAT,
            fcf_margin_yoy_accel_count_4q             SMALLINT,  
            fcf_margin_yoy_accel_positive_flag        SMALLINT,
            fcf_margin_yoy_accel_streak_length           SMALLINT,
            fcf_margin_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            fcf_margin_ttm_growth_pct             FLOAT,
            fcf_margin_ttm_positive_flag        SMALLINT,
            fcf_margin_ttm_count_4q                SMALLINT,
            fcf_margin_ttm_streak_length           SMALLINT,
            fcf_margin_ttm_growth_class        VARCHAR(50),
            fcf_margin_ttm_growth_regime          VARCHAR(50),

            fcf_margin_ttm_volatility_4q        FLOAT,
            fcf_margin_ttm_volatility_flag           SMALLINT,
            fcf_margin_ttm_growth_drift             FLOAT,
            fcf_margin_ttm_outlier_flag               SMALLINT,
            fcf_margin_ttm_stability_regime        VARCHAR(50),

            fcf_margin_ttm_accel                  FLOAT,
            fcf_margin_ttm_accel_count_4q             SMALLINT,
            fcf_margin_ttm_accel_positive_flag        SMALLINT,
            fcf_margin_ttm_accel_streak_length           SMALLINT,
            fcf_margin_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'fcf_margin_metrics' created or already exists with composite primary key.")




       # Create a table for Free CapEx metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.capex_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            capex                           BIGINT,
            capex_ttm                       BIGINT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            capex_qoq_growth_pct          FLOAT,
            capex_qoq_positive_flag        SMALLINT,
            capex_qoq_count_4q                SMALLINT,
            capex_qoq_streak_length           SMALLINT,
            capex_qoq_growth_class        VARCHAR(50),
            capex_qoq_growth_regime          VARCHAR(50), 
                       
            capex_qoq_volatility_4q        FLOAT,
            capex_qoq_volatility_flag           SMALLINT,
            capex_qoq_growth_drift             FLOAT,
            capex_qoq_outlier_flag               SMALLINT,
            capex_qoq_stability_regime        VARCHAR(50),
                       
            capex_qoq_accel                  FLOAT,
            capex_qoq_accel_count_4q             SMALLINT,  
            capex_qoq_accel_positive_flag        SMALLINT,
            capex_qoq_accel_streak_length           SMALLINT,
            capex_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            capex_yoy_growth_pct             FLOAT,
            capex_yoy_positive_flag        SMALLINT,
            capex_yoy_count_4q                SMALLINT,
            capex_yoy_streak_length           SMALLINT,
            capex_yoy_growth_class        VARCHAR(50),
            capex_yoy_growth_regime          VARCHAR(50),
            
            capex_yoy_volatility_4q        FLOAT,
            capex_yoy_volatility_flag           SMALLINT,
            capex_yoy_growth_drift             FLOAT,
            capex_yoy_outlier_flag               SMALLINT,
            capex_yoy_stability_regime        VARCHAR(50),

            capex_yoy_accel                  FLOAT,
            capex_yoy_accel_count_4q             SMALLINT,  
            capex_yoy_accel_positive_flag        SMALLINT,
            capex_yoy_accel_streak_length           SMALLINT,
            capex_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            capex_ttm_growth_pct             FLOAT,
            capex_ttm_positive_flag        SMALLINT,
            capex_ttm_count_4q                SMALLINT,
            capex_ttm_streak_length           SMALLINT,
            capex_ttm_growth_class        VARCHAR(50),
            capex_ttm_growth_regime          VARCHAR(50),

            capex_ttm_volatility_4q        FLOAT,
            capex_ttm_volatility_flag           SMALLINT,
            capex_ttm_growth_drift             FLOAT,
            capex_ttm_outlier_flag               SMALLINT,
            capex_ttm_stability_regime        VARCHAR(50),

            capex_ttm_accel                  FLOAT,
            capex_ttm_accel_count_4q             SMALLINT,
            capex_ttm_accel_positive_flag        SMALLINT,
            capex_ttm_accel_streak_length           SMALLINT,
            capex_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'capex_metrics' created or already exists with composite primary key.")


       # Create a table for Cash Conversion Ratio (CCR) metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.ccr_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            ccr                           FLOAT,
            ccr_ttm                       FLOAT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            ccr_qoq_growth_pct          FLOAT,
            ccr_qoq_positive_flag        SMALLINT,
            ccr_qoq_count_4q                SMALLINT,
            ccr_qoq_streak_length           SMALLINT,
            ccr_qoq_growth_class        VARCHAR(50),
            ccr_qoq_growth_regime          VARCHAR(50), 
                       
            ccr_qoq_volatility_4q        FLOAT,
            ccr_qoq_volatility_flag           SMALLINT,
            ccr_qoq_growth_drift             FLOAT,
            ccr_qoq_outlier_flag               SMALLINT,
            ccr_qoq_stability_regime        VARCHAR(50),
                       
            ccr_qoq_accel                  FLOAT,
            ccr_qoq_accel_count_4q             SMALLINT,  
            ccr_qoq_accel_positive_flag        SMALLINT,
            ccr_qoq_accel_streak_length           SMALLINT,
            ccr_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            ccr_yoy_growth_pct             FLOAT,
            ccr_yoy_positive_flag        SMALLINT,
            ccr_yoy_count_4q                SMALLINT,
            ccr_yoy_streak_length           SMALLINT,
            ccr_yoy_growth_class        VARCHAR(50),
            ccr_yoy_growth_regime          VARCHAR(50),
            
            ccr_yoy_volatility_4q        FLOAT,
            ccr_yoy_volatility_flag           SMALLINT,
            ccr_yoy_growth_drift             FLOAT,
            ccr_yoy_outlier_flag               SMALLINT,
            ccr_yoy_stability_regime        VARCHAR(50),

            ccr_yoy_accel                  FLOAT,
            ccr_yoy_accel_count_4q             SMALLINT,  
            ccr_yoy_accel_positive_flag        SMALLINT,
            ccr_yoy_accel_streak_length           SMALLINT,
            ccr_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            ccr_ttm_growth_pct             FLOAT,
            ccr_ttm_positive_flag        SMALLINT,
            ccr_ttm_count_4q                SMALLINT,
            ccr_ttm_streak_length           SMALLINT,
            ccr_ttm_growth_class        VARCHAR(50),
            ccr_ttm_growth_regime          VARCHAR(50),

            ccr_ttm_volatility_4q        FLOAT,
            ccr_ttm_volatility_flag           SMALLINT,
            ccr_ttm_growth_drift             FLOAT,
            ccr_ttm_outlier_flag               SMALLINT,
            ccr_ttm_stability_regime        VARCHAR(50),

            ccr_ttm_accel                  FLOAT,
            ccr_ttm_accel_count_4q             SMALLINT,
            ccr_ttm_accel_positive_flag        SMALLINT,
            ccr_ttm_accel_streak_length           SMALLINT,
            ccr_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'ccr_metrics' created or already exists with composite primary key.")

       # Create a table for Return on Assets (ROA) metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.roa_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            roa                           FLOAT,
            roa_ttm                       FLOAT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            roa_qoq_growth_pct          FLOAT,
            roa_qoq_positive_flag        SMALLINT,
            roa_qoq_count_4q                SMALLINT,
            roa_qoq_streak_length           SMALLINT,
            roa_qoq_growth_class        VARCHAR(50),
            roa_qoq_growth_regime          VARCHAR(50), 
                       
            roa_qoq_volatility_4q        FLOAT,
            roa_qoq_volatility_flag           SMALLINT,
            roa_qoq_growth_drift             FLOAT,
            roa_qoq_outlier_flag               SMALLINT,
            roa_qoq_stability_regime        VARCHAR(50),
                       
            roa_qoq_accel                  FLOAT,
            roa_qoq_accel_count_4q             SMALLINT,  
            roa_qoq_accel_positive_flag        SMALLINT,
            roa_qoq_accel_streak_length           SMALLINT,
            roa_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            roa_yoy_growth_pct             FLOAT,
            roa_yoy_positive_flag        SMALLINT,
            roa_yoy_count_4q                SMALLINT,
            roa_yoy_streak_length           SMALLINT,
            roa_yoy_growth_class        VARCHAR(50),
            roa_yoy_growth_regime          VARCHAR(50),
            
            roa_yoy_volatility_4q        FLOAT,
            roa_yoy_volatility_flag           SMALLINT,
            roa_yoy_growth_drift             FLOAT,
            roa_yoy_outlier_flag               SMALLINT,
            roa_yoy_stability_regime        VARCHAR(50),

            roa_yoy_accel                  FLOAT,
            roa_yoy_accel_count_4q             SMALLINT,  
            roa_yoy_accel_positive_flag        SMALLINT,
            roa_yoy_accel_streak_length           SMALLINT,
            roa_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            roa_ttm_growth_pct             FLOAT,
            roa_ttm_positive_flag        SMALLINT,
            roa_ttm_count_4q                SMALLINT,
            roa_ttm_streak_length           SMALLINT,
            roa_ttm_growth_class        VARCHAR(50),
            roa_ttm_growth_regime          VARCHAR(50),

            roa_ttm_volatility_4q        FLOAT,
            roa_ttm_volatility_flag           SMALLINT,
            roa_ttm_growth_drift             FLOAT,
            roa_ttm_outlier_flag               SMALLINT,
            roa_ttm_stability_regime        VARCHAR(50),

            roa_ttm_accel                  FLOAT,
            roa_ttm_accel_count_4q             SMALLINT,
            roa_ttm_accel_positive_flag        SMALLINT,
            roa_ttm_accel_streak_length           SMALLINT,
            roa_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'roa_metrics' created or already exists with composite primary key.")

       # Create a table for Return on Equity (ROE) metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.roe_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            roe                           FLOAT,
            roe_ttm                       FLOAT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            roe_qoq_growth_pct          FLOAT,
            roe_qoq_positive_flag        SMALLINT,
            roe_qoq_count_4q                SMALLINT,
            roe_qoq_streak_length           SMALLINT,
            roe_qoq_growth_class        VARCHAR(50),
            roe_qoq_growth_regime          VARCHAR(50), 
                       
            roe_qoq_volatility_4q        FLOAT,
            roe_qoq_volatility_flag           SMALLINT,
            roe_qoq_growth_drift             FLOAT,
            roe_qoq_outlier_flag               SMALLINT,
            roe_qoq_stability_regime        VARCHAR(50),
                       
            roe_qoq_accel                  FLOAT,
            roe_qoq_accel_count_4q             SMALLINT,  
            roe_qoq_accel_positive_flag        SMALLINT,
            roe_qoq_accel_streak_length           SMALLINT,
            roe_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            roe_yoy_growth_pct             FLOAT,
            roe_yoy_positive_flag        SMALLINT,
            roe_yoy_count_4q                SMALLINT,
            roe_yoy_streak_length           SMALLINT,
            roe_yoy_growth_class        VARCHAR(50),
            roe_yoy_growth_regime          VARCHAR(50),
            
            roe_yoy_volatility_4q        FLOAT,
            roe_yoy_volatility_flag           SMALLINT,
            roe_yoy_growth_drift             FLOAT,
            roe_yoy_outlier_flag               SMALLINT,
            roe_yoy_stability_regime        VARCHAR(50),

            roe_yoy_accel                  FLOAT,
            roe_yoy_accel_count_4q             SMALLINT,  
            roe_yoy_accel_positive_flag        SMALLINT,
            roe_yoy_accel_streak_length           SMALLINT,
            roe_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            roe_ttm_growth_pct             FLOAT,
            roe_ttm_positive_flag        SMALLINT,
            roe_ttm_count_4q                SMALLINT,
            roe_ttm_streak_length           SMALLINT,
            roe_ttm_growth_class        VARCHAR(50),
            roe_ttm_growth_regime          VARCHAR(50),

            roe_ttm_volatility_4q        FLOAT,
            roe_ttm_volatility_flag           SMALLINT,
            roe_ttm_growth_drift             FLOAT,
            roe_ttm_outlier_flag               SMALLINT,
            roe_ttm_stability_regime        VARCHAR(50),

            roe_ttm_accel                  FLOAT,
            roe_ttm_accel_count_4q             SMALLINT,
            roe_ttm_accel_positive_flag        SMALLINT,
            roe_ttm_accel_streak_length           SMALLINT,
            roe_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'roe_metrics' created or already exists with composite primary key.")


       # Create a table for Return on Invested Capital (ROIC) metrics if it does not exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS core.roic_metrics (
            -- Identity & period alignment
            tic                               VARCHAR(10)  NOT NULL,
            calendar_year                     SMALLINT     NOT NULL,
            calendar_quarter                  SMALLINT     NOT NULL,

            -- EPS Metrics
            roic                           FLOAT,
            roic_ttm                       FLOAT,
                       
            -- Quarter-over-Quarter (QoQ) Growth Metrics           
            roic_qoq_growth_pct          FLOAT,
            roic_qoq_positive_flag        SMALLINT,
            roic_qoq_count_4q                SMALLINT,
            roic_qoq_streak_length           SMALLINT,
            roic_qoq_growth_class        VARCHAR(50),
            roic_qoq_growth_regime          VARCHAR(50), 
                       
            roic_qoq_volatility_4q        FLOAT,
            roic_qoq_volatility_flag           SMALLINT,
            roic_qoq_growth_drift             FLOAT,
            roic_qoq_outlier_flag               SMALLINT,
            roic_qoq_stability_regime        VARCHAR(50),
                       
            roic_qoq_accel                  FLOAT,
            roic_qoq_accel_count_4q             SMALLINT,  
            roic_qoq_accel_positive_flag        SMALLINT,
            roic_qoq_accel_streak_length           SMALLINT,
            roic_qoq_accel_regime              VARCHAR(50),

            -- Year-over-Year (YoY) Growth Metrics           
            roic_yoy_growth_pct             FLOAT,
            roic_yoy_positive_flag        SMALLINT,
            roic_yoy_count_4q                SMALLINT,
            roic_yoy_streak_length           SMALLINT,
            roic_yoy_growth_class        VARCHAR(50),
            roic_yoy_growth_regime          VARCHAR(50),
            
            roic_yoy_volatility_4q        FLOAT,
            roic_yoy_volatility_flag           SMALLINT,
            roic_yoy_growth_drift             FLOAT,
            roic_yoy_outlier_flag               SMALLINT,
            roic_yoy_stability_regime        VARCHAR(50),

            roic_yoy_accel                  FLOAT,
            roic_yoy_accel_count_4q             SMALLINT,  
            roic_yoy_accel_positive_flag        SMALLINT,
            roic_yoy_accel_streak_length           SMALLINT,
            roic_yoy_accel_regime              VARCHAR(50),
            
            -- TTM Growth Metrics
            roic_ttm_growth_pct             FLOAT,
            roic_ttm_positive_flag        SMALLINT,
            roic_ttm_count_4q                SMALLINT,
            roic_ttm_streak_length           SMALLINT,
            roic_ttm_growth_class        VARCHAR(50),
            roic_ttm_growth_regime          VARCHAR(50),

            roic_ttm_volatility_4q        FLOAT,
            roic_ttm_volatility_flag           SMALLINT,
            roic_ttm_growth_drift             FLOAT,
            roic_ttm_outlier_flag               SMALLINT,
            roic_ttm_stability_regime        VARCHAR(50),

            roic_ttm_accel                  FLOAT,
            roic_ttm_accel_count_4q             SMALLINT,
            roic_ttm_accel_positive_flag        SMALLINT,
            roic_ttm_accel_streak_length           SMALLINT,
            roic_ttm_accel_regime              VARCHAR(50),

            raw_json_sha256                       CHAR(64)     NOT NULL,
            updated_at                            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (tic, calendar_year, calendar_quarter)
        );
        """)
        print("Table 'roic_metrics' created or already exists with composite primary key.")



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