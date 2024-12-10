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
# print (fetch_top_holdings("2024-06-30"))


def get_reporting_period_list(cik=None):
    # Call Supabase function
    response = supabase.rpc("get_reporting_period_list", {"cik_input": cik}).execute()
    #print(response.data)
    if response:
        rows = response.data
        reporting_periods = pd.DataFrame(rows, columns=['period_of_report'])
        latest_two_periods = reporting_periods.sort_values(by='period_of_report', ascending=False).head(2)
        latest_two_periods['period_of_report'] = pd.to_datetime(latest_two_periods['period_of_report'], errors='coerce')
        str_date = latest_two_periods['period_of_report'].dt.strftime('%Y-%m-%d')
        return str_date.tolist()
    else:
        print(f"Error: {response.error_message}")
        return []

print(get_reporting_period_list())