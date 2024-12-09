import seaborn as sns
import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt

from supabase_client import fetch_top_holdings


# Streamlit App
st.title("Top Holdings Heatmap")

# Input for report_date
report_date = st.text_input("Enter the report date (YYYY-MM-DD):", "2024-06-30")

if st.button("Fetch and Plot"):
    # Fetch data
    df = fetch_top_holdings(report_date)

    if df.empty:
        st.warning("No data found for the specified report date.")
    else:
        st.write("Top Holdings Data:")
        st.dataframe(df)

      # Convert 'counter' values to integers for the heatmap
        pivot_data = df.pivot_table(index="security_name", columns="ticker", values="counter", fill_value=0).astype(int)

        # Plot heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot_data, annot=True, fmt="d", cmap="coolwarm", ax=ax)
        ax.set_title("Top Holdings Heatmap")
        st.pyplot(fig)