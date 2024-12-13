from datetime import datetime
from supabase import create_client
import streamlit as st
import pandas as pd
import numpy as np

import seaborn as sns
import math
import matplotlib
import yfinance as yf
import matplotlib.pyplot as plt

# Initialize Supabase client
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_top_holdings(period_of_report):
    try:
        response = supabase.rpc("get_top_holdings", {
                                "report_date": period_of_report}).execute()
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
    response = supabase.rpc("get_reporting_period_list", {
                            "cik_input": cik}).execute()
    # print(response.data)
    if response:
        rows = response.data
        reporting_periods = pd.DataFrame(rows, columns=['period_of_report'])
        latest_two_periods = reporting_periods.sort_values(
            by='period_of_report', ascending=False).head(2)
        latest_two_periods['period_of_report'] = pd.to_datetime(
            latest_two_periods['period_of_report'], errors='coerce')
        str_date = latest_two_periods['period_of_report'].dt.strftime(
            '%Y-%m-%d')
        return str_date.tolist()
    else:
        print(f"Error: {response.error_message}")
        return []


print(get_reporting_period_list())

period1, period2 = get_reporting_period_list()


def get_filtered_holdings(period1, period2):
    response = supabase.rpc("get_filtered_holdings", {
                            "period1": period1, "period2": period2}).execute()
    if response.data:
        rows = response.data
        df = pd.DataFrame(rows, columns=[
            'total_shares', 'cusip', 'ticker', 'security_name', 'period_of_report', 'value','last_close'
        ])
        return df
    else:
        print(f"Error: {response.error_message}")
        return None


def calculate_holding_changes(df, str_date):
    print(df)
    latest_date_str = str_date[0]
    oldest_date_str = str_date[1]
    # latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d').date()
    # oldest_date = datetime.strptime(oldest_date_str, '%Y-%m-%d').date()

    holdings_changes = "NaN"
    holding_changes = []
    subset = df[df['PeriodOfReport'] == latest_date_str]

    # mask_1 = select holdings for 2021-03-31 period
    mask_1 = df['PeriodOfReport'] == oldest_date_str

    for index, holding_2021_06_30 in subset.iterrows():
        # mask_2 = select holdings with same NameOfIssuer
        mask_2 = df['CUSIP'] == holding_2021_06_30['CUSIP']
        # merge both masks
        holdings_2021_03_31 = df[(mask_1 & mask_2)]

        if len(holdings_2021_03_31) != 0:
            holding_2021_03_31 = holdings_2021_03_31.iloc[0]

            share_delta_absolute = holding_2021_06_30['Shares'] - \
                holding_2021_03_31['Shares']
            share_delta_relative = (
                share_delta_absolute / holding_2021_03_31['Shares']) * 100
            shares_2021_06_30 = holding_2021_06_30['Shares']
            value_2021_06_30 = holding_2021_06_30['value']

            shares_2021_03_31 = holding_2021_03_31['Shares']
            value_2021_03_31 = holding_2021_03_31['value']

        else:
            # holding didn't exist in 2021-03-31 filing
            share_delta_absolute = holding_2021_06_30['Shares']
            share_delta_relative = 100
            shares_2021_06_30 = holding_2021_06_30['Shares']
            value_2021_06_30 = holding_2021_06_30['value']

            shares_2021_03_31 = 0

        holding_changes.append((holding_2021_06_30['CUSIP'],
                                holding_2021_06_30['Ticker'],
                                holding_2021_06_30['SecurityName'],
                                shares_2021_03_31,
                                shares_2021_06_30,
                                share_delta_absolute,
                                share_delta_relative,
                                value_2021_03_31))

    holding_changes = pd.DataFrame(holding_changes, columns=['CUSIP',
                                                             'Ticker',
                                                             'SecurityName',
                                                             'Shares2021_03_31',
                                                             'Shares2021_06_30',
                                                             'DeltaAbsolute',
                                                             'DeltaRelative', 'value'])
    return holding_changes

def calculate_shape(n_elements):
    """
    Dynamically calculates the rows and columns for reshaping an array.
    Ensures that rows * cols >= n_elements, with rows and cols being as close as possible.
    """
    # Start with the square root
    sqrt = int(np.sqrt(n_elements))

    # Search for the closest factors of n_elements
    best_rows, best_cols = sqrt, sqrt
    min_diff = abs(best_rows * best_cols - n_elements)

    # Try different combinations of rows and cols
    for r in range(sqrt, n_elements + 1):
        c = (n_elements + r - 1) // r  # Calculate the required columns for this number of rows
        diff = abs(r * c - n_elements)
        
        if diff < min_diff:
            best_rows, best_cols = r, c
            min_diff = diff

    return best_rows, best_cols





def plot_holdings(top_holdings, activity,reporting_date):
    # Convert the 'Ticker' column to a NumPy array
    tickers = np.asarray(top_holdings['Ticker'])
    # Calculate the optimal shape
    n_elements = len(tickers) 
    print(f'n_elements {n_elements}')
    data = np.arange(1, n_elements+1)  # Array with 63 elements
    # Calculate dynamic shape
    rows, cols = calculate_shape(len(data))
    shape=(rows,cols)
    print(rows,cols)
    #shape = (7, 9)

    #shape = reshape_to_closest(np.asarray(top_holdings['Ticker']))
    total_number_of_funds =3005
    # top_holdings['CounterRelative'] = [round(counter/(total_number_of_funds )*100,1) for counter in top_holdings['counter ']]
    top_holdings['DeltaRelative'] = round(top_holdings['DeltaRelative']/(total_number_of_funds )*100, 1)
    tickers = np.asarray(top_holdings['Ticker']).reshape(shape)
    counters = np.asarray(top_holdings['DeltaRelative']).reshape(shape)

    top_holdings['Position'] = range(1, len(top_holdings) + 1)
    top_holdings['y_rows'] = [(math.floor(x/shape[1]) + 1 if x % shape[1]
                               != 0 else math.floor(x/shape[1])) for x in top_holdings['Position']]
    top_holdings['x_cols'] = [
        (x % shape[1] if x % shape[1] != 0 else shape[1]) for x in top_holdings['Position']]

    pivot_table = top_holdings.pivot(
        index='y_rows', columns='x_cols', values='DeltaRelative')
    heatmap_labels = np.asarray(["{0} \n {1}%".format(ticker, counter)
                                 for ticker, counter in zip(tickers.flatten(), counters.flatten())]).reshape(shape)
    fig, ax = plt.subplots(figsize=(18, 7))

    title = f"Top superinvestors {activity} for the period , {reporting_date[0]} -  {reporting_date[1]} "

    plt.title(title, fontsize=18)
    ttl = ax.title
    ttl.set_position([0.5, 1.05])

    ax.set_xticks([])
    ax.set_yticks([])

    ax.axis('off')

    sns.heatmap(pivot_table, annot=heatmap_labels, fmt="",
                cmap="BuGn", linewidths=0.30, ax=ax)

    st.pyplot(fig)



def plot_price_holdings(top_holdings, activity,reporting_date):
    # Convert the 'Ticker' column to a NumPy array
    tickers = np.asarray(top_holdings['Ticker'])
    # Calculate the optimal shape
    n_elements = len(tickers) 
    print(f'n_elements {n_elements}')
    data = np.arange(1, n_elements+1) 
    # Calculate dynamic shape
    rows, cols = calculate_shape(len(data))
    shape=(rows,cols)
    print(rows,cols)
    #shape = (7, 9)

    #shape = reshape_to_closest(np.asarray(top_holdings['Ticker']))
    total_number_of_funds =3005
    # top_holdings['CounterRelative'] = [round(counter/(total_number_of_funds )*100,1) for counter in top_holdings['counter ']]
    top_holdings['pdifference'] = round(top_holdings['Percentage Difference'], 1)
    tickers = np.asarray(top_holdings['Ticker']).reshape(shape)
    counters = np.asarray(top_holdings['pdifference']).reshape(shape)

    top_holdings['Position'] = range(1, len(top_holdings) + 1)
    top_holdings['y_rows'] = [(math.floor(x/shape[1]) + 1 if x % shape[1]
                               != 0 else math.floor(x/shape[1])) for x in top_holdings['Position']]
    top_holdings['x_cols'] = [
        (x % shape[1] if x % shape[1] != 0 else shape[1]) for x in top_holdings['Position']]

    pivot_table = top_holdings.pivot(
        index='y_rows', columns='x_cols', values='pdifference')
    heatmap_labels = np.asarray(["{0} \n {1}%".format(ticker, counter)
                                 for ticker, counter in zip(tickers.flatten(), counters.flatten())]).reshape(shape)
    fig, ax = plt.subplots(figsize=(18, 7))

   
    title = f"Top superinvestors percentage change from time it was bought , {reporting_date[0]} -  {reporting_date[1]} "

    plt.title(title, fontsize=18)
    ttl = ax.title
    ttl.set_position([0.5, 1.05])

    ax.set_xticks([])
    ax.set_yticks([])

    ax.axis('off')

    sns.heatmap(pivot_table, annot=heatmap_labels, fmt="",
                cmap="BuGn_r", linewidths=0.30, ax=ax)

    st.pyplot(fig)



def calculate_purchase_price(row):
    try:
        total_value = row['value']   # Convert value to actual dollars
        purchase_price_per_share = total_value / row['Shares']
        return round(purchase_price_per_share, 2)
    except ZeroDivisionError:
        # Handle the division by zero case
        return np.nan  # You could also return None or 0, depending on your needs


def current_price(row):

    try:
        total_value = row['value']   # Convert value to actual dollars
        purchase_price_per_share = total_value / row['Shares']
        return round(purchase_price_per_share, 2)
    except ZeroDivisionError:
        # Handle the division by zero case
        return np.nan  # You could also return None or 0, depending on your needs


def percentage_difference(row):
    value1 = row['Current Price']
    value2 = row['purchase_price_per_share']
    return (value1 - value2) / ((value1 + value2) / 2) * 100



def get_ticker_stock_price_from_name(row):
    stock = yf.Ticker(row['Ticker'])
    try:
        stock_price = stock.history(period='1d')['Close'].iloc[-1]
        return stock_price
    except:
        return 0
