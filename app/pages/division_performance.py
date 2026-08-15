import streamlit as st
import pandas as pd


def render(df):
    st.header('Division Performance')
    grp = df.groupby('Division').agg(Revenue=('Sales','sum'), Profit=('Gross Profit','sum'))
    grp['Avg Margin %'] = (grp['Profit'] / grp['Revenue']).fillna(0) * 100
    st.dataframe(grp.sort_values('Revenue', ascending=False))
