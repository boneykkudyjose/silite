from supabase import create_client
import streamlit as st

# Initialize Supabase client
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
def fetch_top_holdings(period_of_report):
    try:
        response = supabase.rpc("get_top_holdings", {"report_date": period_of_report}).execute()
        if response:
            print("Query executed successfully!")
            for row in response.data:
                print(row)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Call the function with the desired period_of_report
fetch_top_holdings("2024-06-30")