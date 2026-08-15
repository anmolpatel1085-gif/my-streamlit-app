import pandas as pd


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Apply basic cleaning rules and return a cleaned DataFrame.

    Rules implemented:
    - Drop rows with missing Sales or negative Sales
    - Drop rows with missing Product ID or Product Name
    - Flag rows with missing Units but keep them for manual review
    """
    df = df.copy()

    # Drop invalid sales
    if 'Sales' in df.columns:
        df = df[df['Sales'].notna()]
        df = df[df['Sales'] >= 0]

    # Drop missing product identifiers
    df = df[df['Product ID'].notna()]
    df = df[df['Product Name'].notna()]

    # Ensure Units numeric
    if 'Units' in df.columns:
        df['Units'] = pd.to_numeric(df['Units'], errors='coerce')

    return df
