import streamlit as st
import pandas as pd
import altair as alt
from src.metrics import compute_pareto_products, find_pareto_cutoff


def render(df):
    st.header('Profit & Revenue Concentration (Pareto)')
    if df.empty:
        st.info('No data available')
        return

    # Compute product-level aggregates first
    from src.metrics import compute_product_metrics
    prod = compute_product_metrics(df)
    pareto = compute_pareto_products(prod, revenue_col='Revenue', profit_col='Profit')

    if pareto.empty:
        st.info('Not enough product data for Pareto analysis')
        return

    # Show cumulative lines
    base = alt.Chart(pareto.reset_index()).encode(x=alt.X('index:Q', title='Product Rank (by Revenue)'))
    rev_line = base.mark_line(color='steelblue').encode(y=alt.Y('CumRevenuePct:Q', axis=alt.Axis(format='%')))
    prof_line = base.mark_line(color='orange').encode(y=alt.Y('CumProfitPct:Q', axis=alt.Axis(format='%')))

    chart = alt.layer(rev_line, prof_line).resolve_scale(y='independent')
    st.altair_chart(chart.properties(height=300), use_container_width=True)

    # Determine cutoffs
    rev_cut = find_pareto_cutoff(pareto, pct=0.8, col='CumRevenuePct')
    prof_cut = find_pareto_cutoff(pareto, pct=0.8, col='CumProfitPct')

    st.markdown(f"- Products covering 80% of revenue: **{rev_cut}**")
    st.markdown(f"- Products covering 80% of profit: **{prof_cut}**")

    # Top contributors table
    st.subheader('Top products by revenue')
    st.dataframe(pareto[['Product Name', 'Revenue', 'Profit']].head(20))

    # Download option
    csv = pareto.to_csv(index=False)
    st.download_button('Download Pareto CSV', csv, file_name='pareto_products.csv')
