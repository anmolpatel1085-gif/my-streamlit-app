import streamlit as st
import altair as alt
import pandas as pd
from src.metrics import compute_cost_diagnostics, flag_high_cost_products


def render(df):
    st.header('Cost vs Margin Diagnostics')
    if df.empty:
        st.info('No data to analyze')
        return

    # Compute cost diagnostics (accept order-level or product-level)
    cost_df = compute_cost_diagnostics(df)

    st.subheader('Cost vs Revenue Scatter')
    # Use Altair scatter: x=Cost, y=Revenue, color=Margin
    chart = alt.Chart(cost_df).mark_circle(size=60).encode(
        x=alt.X('Cost:Q', title='Total Cost'),
        y=alt.Y('Revenue:Q', title='Total Revenue'),
        color=alt.Color('Margin:Q', title='Margin (Profit/Revenue)'),
        tooltip=['Product Name', 'Revenue', 'Cost', 'Profit', 'Cost_per_Unit', 'Margin']
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

    st.subheader('High-cost / Low-margin Products')
    flagged = flag_high_cost_products(cost_df, cost_to_revenue_thresh=0.5, low_margin_thresh=0.1)
    if flagged.empty:
        st.write('No products flagged for high cost or low margin with current thresholds.')
    else:
        st.dataframe(flagged[['Product ID', 'Product Name', 'Revenue', 'Profit', 'Cost', 'Cost_to_Revenue', 'Margin', 'Cost_per_Unit', 'Flag']])
        csv = flagged.to_csv(index=False)
        st.download_button('Download flagged products', csv, file_name='flagged_cost_products.csv')

    st.markdown('Adjust thresholds in `src/metrics.py` or add UI controls to tune detection.')
