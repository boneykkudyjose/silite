# cusip-mapper.py
import pandas as pd
from supabase import create_client
import streamlit as st

# Initialize Supabase client
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load your CSV file that contains CUSIP and Ticker columns
df = pd.read_csv('CUSIP.csv',sep="|")
# Example function to lookup CUSIP
def get_ticker(cusip):
    result = df[df['CUSIP'] == cusip]
    if not result.empty:
        return result['Ticker'].values[0] 
    else:
        return None
# connect to database

def fetch_distinct_cusip():
    try:
        # Call the RPC function
        response = supabase.rpc("get_distinct_cusip").execute()
        return [row["cusip"] for row in response.data]


    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []


def insert_into_holding_infos(cusip, ticker, security_name, security_type):
    try:
        # Define the data to insert
        data = {
            "cusip": cusip,
            "ticker": ticker,
            "security_name": security_name,
            "security_type": security_type,
        }
        
        # Perform the insert operation
        response = supabase.table("holding_infos").insert(data).execute()
        
        if response:
            print(f"inserted : {response}")
            return False
        else:
            print("Insert successful!")
            return True
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    
def cusips_to_tickers(cusips):
    for cusip in cusips:
        result = df[df['CUSIP'] == cusip]
        if not result.empty:
            insert_into_holding_infos(cusip, result['SYMBOL'].values[0], result['DESCRIPTION'].values[0], "notype")
        else:
            print (f"no ticker to insert for {cusip}")

cusips=fetch_distinct_cusip() 
cusips_to_tickers(cusips)