import streamlit as st
from src.metrics import compute_product_metrics, compute_margin_risk
import pandas as pd


def render(df):
    st.header('Product Overview')
    metrics = compute_product_metrics(df)

    # compute margin risk using order-level df
    risk = compute_margin_risk(df)
    merged = metrics.merge(risk[['Product ID', 'RiskScore', 'RiskFlag']], on='Product ID', how='left')
    merged['RiskScore'] = merged['RiskScore'].fillna(0)
    merged['RiskFlag'] = merged['RiskFlag'].fillna('Low')

    st.subheader('Top products by Profit (with Risk)')
    st.dataframe(merged.sort_values(['RiskScore','Profit'], ascending=[False, False]).head(50))

    # download option
    csv = merged.to_csv(index=False)
    st.download_button('Download product metrics with risk', csv, file_name='product_metrics_with_risk.csv')
