import sys
from pathlib import Path

# Ensure project root is on sys.path so `from src...` works when Streamlit runs
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from src.etl import load_orders
from src.cleaning import clean_orders
from src.metrics import compute_product_metrics
from app.pages import product_overview, division_performance, cost_diagnostics, pareto_analysis


st.set_page_config(page_title="Nassau Candy — Product Profitability", layout='wide')


DATA_PATH = 'data/raw/orders.csv'


@st.cache_data
def load_data(path):
    # If the data file is missing, `load_orders` will fall back to a small sample.
    from pathlib import Path as _P
    exists = _P(path).exists()
    df = load_orders(path)
    df = clean_orders(df)
    # Notify user in the app when sample data is being used
    if not exists:
        st.warning("No `data/raw/orders.csv` found — using built-in sample data. Add your real export to `data/raw/orders.csv` and redeploy for real results.")
    return df


def apply_shared_filters(df: pd.DataFrame):
    st.sidebar.header('Filters')
    # Date range
    if 'Order Date' in df.columns and not df['Order Date'].isna().all():
        min_date = pd.to_datetime(df['Order Date'].min()).date()
        max_date = pd.to_datetime(df['Order Date'].max()).date()
        date_range = st.sidebar.date_input('Order date range', [min_date, max_date])
    else:
        date_range = None

    # Division filter
    divisions = []
    if 'Division' in df.columns:
        divisions = sorted(df['Division'].dropna().unique().tolist())
    selected_divs = st.sidebar.multiselect('Division', options=divisions, default=divisions)

    # Product search
    product_search = st.sidebar.text_input('Product search')

    # Apply filters
    mask = pd.Series(True, index=df.index)
    if selected_divs:
        if 'Division' in df.columns:
            mask &= df['Division'].isin(selected_divs)
    if date_range and len(date_range) == 2 and 'Order Date' in df.columns:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        mask &= (df['Order Date'] >= start) & (df['Order Date'] <= end)
    if product_search and 'Product Name' in df.columns:
        mask &= df['Product Name'].str.contains(product_search, case=False, na=False)

    return df[mask]


def main():
    st.title("Nassau Candy — Product Profitability & Margin Analysis")
    df = load_data(DATA_PATH)

    if df.empty:
        st.info("No data found in data/raw/orders.csv. Please add an order export and refresh.")
        return

    # Page selector
    PAGES = {
        'Home': 'Home',
        'Product Overview': product_overview,
        'Division Performance': division_performance,
        'Cost Diagnostics': cost_diagnostics,
        'Profit Concentration': pareto_analysis,
    }

    page = st.sidebar.selectbox('Page', options=list(PAGES.keys()))

    # Apply filters and pass filtered df to pages
    df_filtered = apply_shared_filters(df)

    if page == 'Home':
        st.header('Product Profitability Overview')
        prod_metrics = compute_product_metrics(df_filtered)
        st.dataframe(prod_metrics.sort_values('Profit', ascending=False).head(20))

        st.header('Quick Charts')
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Revenue by Product (top 10)')
            top_rev = prod_metrics.sort_values('Revenue', ascending=False).head(10)
            if 'Product Name' in top_rev.columns:
                st.bar_chart(top_rev.set_index('Product Name')['Revenue'])
            else:
                st.bar_chart(top_rev['Revenue'])
        with col2:
            st.subheader('Profit by Product (top 10)')
            top_profit = prod_metrics.sort_values('Profit', ascending=False).head(10)
            if 'Product Name' in top_profit.columns:
                st.bar_chart(top_profit.set_index('Product Name')['Profit'])
            else:
                st.bar_chart(top_profit['Profit'])

    else:
        page_module = PAGES.get(page)
        # Each page module exposes a `render(df)` function
        try:
            page_module.render(df_filtered)
        except Exception as e:
            st.error(f'Error rendering page {page}: {e}')


if __name__ == '__main__':
    main()
