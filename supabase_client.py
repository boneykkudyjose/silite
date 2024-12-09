from supabase import create_client
import streamlit as st
import pandas as pd
# Initialize Supabase client
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
def fetch_top_holdings(period_of_report):
    try:
        response = supabase.rpc("get_top_holdings", {"report_date": period_of_report}).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        else:
            print("No data returned from Supabase.")
            return pd.DataFrame()  # Return an empty DataFrame if no data
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error

# Call the function with the desired period_of_report
print (fetch_top_holdings("2024-06-30"))