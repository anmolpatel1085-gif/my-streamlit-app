import pandas as pd
from typing import Optional

REQUIRED_COLUMNS = [
    'Row ID', 'Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'Customer ID',
    'Country/Region', 'City', 'State/Province', 'Postal Code', 'Division', 'Region',
    'Product ID', 'Product Name', 'Sales', 'Units', 'Gross Profit', 'Cost'
]


def load_orders(path: str) -> pd.DataFrame:
    """Load orders CSV/Excel and perform basic parsing.

    - Parses dates for `Order Date` and `Ship Date`.
    - Ensures numeric columns are numeric.
    - Derives `Gross Profit` if missing (Sales - Cost).
    """
    try:
        if path.endswith('.xlsx') or path.endswith('.xls'):
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)
    except FileNotFoundError:
        # Fallback: return a small sample DataFrame so the app can still render
        # (useful for Streamlit Cloud when data is not bundled). We print a
        # message to stderr so logs contain the reason.
        import sys
        print(f"Warning: data file not found at {path}. Using built-in sample data.", file=sys.stderr)
        sample = {
            'Row ID': [1, 2, 3],
            'Order ID': ['O-001', 'O-002', 'O-003'],
            'Order Date': [pd.Timestamp('2024-01-10'), pd.Timestamp('2024-02-05'), pd.Timestamp('2024-03-12')],
            'Ship Date': [pd.Timestamp('2024-01-12'), pd.Timestamp('2024-02-07'), pd.Timestamp('2024-03-14')],
            'Ship Mode': ['Ground', 'Air', 'Ground'],
            'Customer ID': ['C-001', 'C-002', 'C-003'],
            'Country/Region': ['USA', 'USA', 'USA'],
            'City': ['CityA', 'CityB', 'CityC'],
            'State/Province': ['StateA', 'StateB', 'StateC'],
            'Postal Code': ['10001', '10002', '10003'],
            'Division': ['Confections', 'Confections', 'Snacks'],
            'Region': ['East', 'West', 'South'],
            'Product ID': ['P-001', 'P-002', 'P-003'],
            'Product Name': ['Chocolate Bar', 'Gummy Bears', 'Salted Chips'],
            'Sales': [100.0, 150.0, 80.0],
            'Units': [10, 15, 8],
            'Gross Profit': [30.0, 50.0, 10.0],
            'Cost': [70.0, 100.0, 70.0]
        }
        df = pd.DataFrame(sample)

    # Parse dates
    for dcol in ['Order Date', 'Ship Date']:
        if dcol in df.columns:
            df[dcol] = pd.to_datetime(df[dcol], errors='coerce')

    # Ensure numeric
    for col in ['Sales', 'Units', 'Gross Profit', 'Cost']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = pd.NA

    # Derive Gross Profit when possible
    if df['Gross Profit'].isna().all() and 'Sales' in df.columns and 'Cost' in df.columns:
        df['Gross Profit'] = df['Sales'] - df['Cost']

    return df
