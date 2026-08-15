import os
from src.etl import load_orders
import pandas as pd


def test_load_orders_creates_df(tmp_path):
    # create a small csv
    p = tmp_path / "orders.csv"
    df = pd.DataFrame({
        'Order ID': [1,2],
        'Order Date': ['2021-01-01','2021-01-02'],
        'Product ID': ['P1','P2'],
        'Product Name': ['A','B'],
        'Sales': [100,200],
        'Cost': [60,120]
    })
    df.to_csv(p, index=False)
    out = load_orders(str(p))
    assert not out.empty
    assert 'Gross Profit' in out.columns
    assert out['Gross Profit'].iloc[0] == 40
