import seaborn as sns
import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt

from supabase_client import calculate_holding_changes, calculate_purchase_price, fetch_top_holdings, get_filtered_holdings, get_reporting_period_list, get_ticker_stock_price_from_name, percentage_difference, plot_holdings, plot_holdings2, plot_price_holdings


# Streamlit App
st.title("Super Investor Holdings")
reporting_date=get_reporting_period_list()
# Input for report_date
#report_date = st.text_input("Enter the report date (YYYY-MM-DD):", reporting_date[0])


# Fetch data
df = fetch_top_holdings(reporting_date[0])

if df.empty:
    st.warning("No data found for the specified report date.")


  # Convert 'counter' values to integers for the heatmap
import math
import numpy as np
# heatmap shape: 10 rows, 10 columns
shape = (10, 10) 
total_number_of_funds = 3005
df['CounterRelative'] = [round(counter/(total_number_of_funds )*100,1) for counter in df['counter']]

tickers = np.asarray(df['ticker']).reshape(shape)
counters = np.asarray(df['CounterRelative']).reshape(shape)

df['Position'] = range(1,len(df) + 1)
df['y_rows'] = [(math.floor(x/shape[1]) + 1 if x%shape[1] != 0 else math.floor(x/shape[1])) for x in df['Position']]
df['x_cols'] = [(x%shape[1] if x%shape[1] != 0 else shape[1]) for x in df['Position']]

pivot_table = df.pivot(index='y_rows', columns='x_cols', values='CounterRelative')
fig, ax = plt.subplots(figsize=(18, 7))

title = f"Top superinvestors holdings for the period , {reporting_date[1]} -  {reporting_date[0]} "
heatmap_labels = np.asarray(["{0} \n {1}%".format(ticker, counter) 
                          for ticker, counter in zip(tickers.flatten(), counters.flatten())]).reshape(shape)


plt.title(title, fontsize=18)
ttl = ax.title
ttl.set_position([0.5, 1.05])

ax.set_xticks([])
ax.set_yticks([])

ax.axis('off')

sns.heatmap(pivot_table, annot=heatmap_labels, fmt="", cmap="BuGn", linewidths=0.30, ax=ax)

st.pyplot(fig)
all_holding_df= get_filtered_holdings(reporting_date[0],reporting_date[1])
print(all_holding_df.columns)
all_holding_df = all_holding_df.rename(columns={'total_shares':'Shares', 'cusip':'CUSIP', 'ticker': 'Ticker','security_name': 'SecurityName','period_of_report':'PeriodOfReport','last_close':'Current Price'})
print(all_holding_df)
#all_holdings = pd.DataFrame(all_holding_df, columns =['Shares', 'CUSIP', 'Ticker', 'SecurityName', 'PeriodOfReport','value'])
all_holding_changes= calculate_holding_changes(all_holding_df,reporting_date)
mask_1 = all_holding_changes['DeltaRelative'] > 0
mask_2 = all_holding_changes['DeltaRelative'] != np.inf
bought_all = all_holding_changes[(mask_1 & mask_2)].sort_values(by=['DeltaRelative'], ascending=False)
top_100_bought = bought_all[bought_all['Shares2021_03_31'] > 500000][:100].reset_index()
plot_holdings2(top_100_bought,'buy',reporting_date[::-1])

mask_1 = all_holding_changes['DeltaRelative'] < 0
mask_2 = all_holding_changes['DeltaRelative'] != np.inf
bought_all = all_holding_changes[(mask_1 & mask_2)].sort_values(by=['DeltaRelative'], ascending=True)
top_100_sold = bought_all[bought_all['Shares2021_03_31'] < 500000][:100].reset_index()
plot_holdings2(top_100_sold,'sell',reporting_date[::-1])

#all_holding_df['Current Price'] = all_holding_df.apply(get_ticker_stock_price_from_name,axis=1)
all_holding_df['purchase_price_per_share'] = all_holding_df.apply(calculate_purchase_price, axis=1)

all_holding_df['Percentage Difference'] = all_holding_df.apply(percentage_difference, axis=1)
all_holding_df = all_holding_df[all_holding_df['Current Price'] != 0]

# Filter rows where Current Price is less than Purchase Price
filtered_df = all_holding_df[all_holding_df['Current Price'] < all_holding_df['purchase_price_per_share']]

# Sort by Percentage Difference in ascending order to get "top" (largest negative difference)
sorted_df = filtered_df.sort_values(by='Percentage Difference')
# Display top tickers
top_tickers = sorted_df[['Ticker', 'Current Price', 'purchase_price_per_share', 'Percentage Difference']]
#st.dataframe(top_tickers.head(100))
top_100_tickers = top_tickers.drop_duplicates(subset='Ticker').head(100)

plot_price_holdings(top_100_tickers,'price diff',reporting_date[::-1])
