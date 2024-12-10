import seaborn as sns
import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt

from supabase_client import fetch_top_holdings, get_reporting_period_list


# Streamlit App
st.title("Top Holdings Heatmap")
reporting_date=get_reporting_period_list()
# Input for report_date
report_date = st.text_input("Enter the report date (YYYY-MM-DD):", reporting_date[0])

if st.button("Fetch and Plot"):
    # Fetch data
    df = fetch_top_holdings(report_date)

    if df.empty:
        st.warning("No data found for the specified report date.")
    else:
        st.write("Top Holdings Data:")
        st.dataframe(df)

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

    title = f"Top 100 Holdings Distribution Across 13F Filings, {reporting_date}"
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
