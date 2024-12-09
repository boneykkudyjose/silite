from supabase import create_client
import streamlit as st

# Initialize Supabase client
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL Query
query = """
    SELECT COUNT(tmp_table.cusip) as counter, tmp_table.cusip, tmp_table.ticker, tmp_table.security_name
    FROM (
        SELECT DISTINCT holdings.cusip, ticker, security_name, holdings.filing_id
        FROM "holdings"
        INNER JOIN "filings"
        ON filings.filing_id = holdings.filing_id
        INNER JOIN holding_infos
        ON holdings.cusip = holding_infos.cusip
        WHERE period_of_report = '2024-06-30' AND NOT holdings.cusip LIKE '000%'
    ) tmp_table
    GROUP BY tmp_table.cusip, tmp_table.ticker, tmp_table.security_name
    ORDER BY counter DESC
    LIMIT 100
"""

# Execute the query
def execute_query(query):
    try:
        response = supabase.execute(query)
        if response.error:
            print(f"Error occurred: {response.error}")
        else:
            print("Query executed successfully!")
            for row in response.data:
                print(row)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Execute
execute_query(query)
