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
    if path.endswith('.xlsx') or path.endswith('.xls'):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

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
