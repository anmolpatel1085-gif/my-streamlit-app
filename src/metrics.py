import pandas as pd
import numpy as np


def compute_product_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute product-level KPIs and return aggregated DataFrame keyed by Product ID/Name.

    Returns columns: Product ID, Product Name, Revenue, Profit, Units, Avg_Margin_pct,
    Revenue Contribution, Profit Contribution, Profit per Unit.
    """
    df = df.copy()
    # Derived fields with safe handling
    df['Gross Margin %'] = 0
    if 'Gross Profit' in df.columns and 'Sales' in df.columns:
        df['Gross Margin %'] = (df['Gross Profit'] / df['Sales']) * 100
        df['Gross Margin %'] = df['Gross Margin %'].replace([np.inf, -np.inf], np.nan).fillna(0)

    df['Profit per Unit'] = None
    if 'Units' in df.columns and 'Gross Profit' in df.columns:
        df['Profit per Unit'] = df['Gross Profit'] / df['Units']
        df['Profit per Unit'] = df['Profit per Unit'].replace([np.inf, -np.inf], np.nan).fillna(0)

    agg = df.groupby(['Product ID', 'Product Name'], dropna=False).agg(
        Revenue=('Sales', 'sum'),
        Profit=('Gross Profit', 'sum'),
        Units=('Units', 'sum'),
        Avg_Margin_pct=('Gross Margin %', 'mean'),
        Profit_per_Unit=('Profit per Unit', 'mean')
    ).reset_index()

    total_revenue = agg['Revenue'].sum()
    total_profit = agg['Profit'].sum()
    denom_rev = total_revenue if total_revenue != 0 else 1
    denom_prof = total_profit if total_profit != 0 else 1
    agg['Revenue Contribution'] = agg['Revenue'] / denom_rev
    agg['Profit Contribution'] = agg['Profit'] / denom_prof

    return agg


def compute_division_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate key KPIs by Division."""
    df = df.copy()
    grp = df.groupby('Division', dropna=False).agg(
        Revenue=('Sales', 'sum'),
        Profit=('Gross Profit', 'sum'),
        Units=('Units', 'sum')
    ).reset_index()
    grp['Avg_Margin_pct'] = 0
    grp['Avg_Margin_pct'] = (grp['Profit'] / grp['Revenue']) * 100
    grp['Avg_Margin_pct'] = grp['Avg_Margin_pct'].replace([np.inf, -np.inf], np.nan).fillna(0)

    total_revenue = grp['Revenue'].sum()
    grp['Revenue Share'] = grp['Revenue'] / total_revenue.replace(0, 1)
    return grp


def segment_products(prod_df: pd.DataFrame, high_margin_thresh: float = 0.2, high_sales_percentile: float = 0.8) -> pd.DataFrame:
    """Tag products into segments using profit, margin and sales thresholds.

    - high_margin_thresh: e.g., 0.2 means 20% margin
    - high_sales_percentile: percentile to consider high-sales (0-1)
    """
    df = prod_df.copy()
    # compute margin as Profit / Revenue
    df['Margin'] = 0
    with pd.option_context('mode.use_inf_as_na', True):
        df['Margin'] = df['Profit'] / df['Revenue']
        df['Margin'] = df['Margin'].fillna(0)

    sales_threshold = df['Revenue'].quantile(high_sales_percentile)

    def tag(row):
        if row['Profit'] > 0 and row['Margin'] >= high_margin_thresh:
            return 'High-profit/High-margin'
        if row['Revenue'] >= sales_threshold and row['Margin'] < high_margin_thresh:
            return 'High-sales/Low-margin'
        if row['Revenue'] < sales_threshold and row['Profit'] <= 0:
            return 'Low-sales/Low-profit'
        return 'Other'

    df['Segment'] = df.apply(tag, axis=1)
    return df


def compute_pareto_products(df: pd.DataFrame, revenue_col: str = 'Revenue', profit_col: str = 'Profit') -> pd.DataFrame:
    """Compute cumulative revenue and profit share by product and return a dataframe sorted by revenue.

    Returns columns: Product ID, Product Name, Revenue, Profit, CumRevenuePct, CumProfitPct
    """
    if df is None or df.empty:
        return pd.DataFrame()

    cols = ['Product ID', 'Product Name', revenue_col, profit_col]
    for c in cols:
        if c not in df.columns:
            raise ValueError(f'Missing column: {c}')

    dfp = df[[ 'Product ID', 'Product Name', revenue_col, profit_col ]].copy()
    dfp = dfp.groupby(['Product ID', 'Product Name'], dropna=False).sum().reset_index()
    dfp = dfp.sort_values(by=revenue_col, ascending=False).reset_index(drop=True)

    total_rev = dfp[revenue_col].sum()
    total_profit = dfp[profit_col].sum()
    dfp['CumRevenue'] = dfp[revenue_col].cumsum()
    dfp['CumProfit'] = dfp[profit_col].cumsum()
    denom_rev = total_rev if total_rev != 0 else 1
    denom_prof = total_profit if total_profit != 0 else 1
    dfp['CumRevenuePct'] = dfp['CumRevenue'] / denom_rev
    dfp['CumProfitPct'] = dfp['CumProfit'] / denom_prof

    return dfp


def find_pareto_cutoff(dfp: pd.DataFrame, pct: float = 0.8, col: str = 'CumRevenuePct') -> int:
    """Return the number of products required to reach `pct` cumulative share based on `col`.

    If dfp is empty, returns 0.
    """
    if dfp is None or dfp.empty:
        return 0
    mask = dfp[col] >= pct
    if not mask.any():
        return len(dfp)
    return int(mask.idxmax()) + 1


def compute_cost_diagnostics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute cost-related diagnostics at product level.

    Returns a DataFrame with columns: Product ID, Product Name, Revenue, Profit, Cost,
    Cost_per_Unit, Cost_to_Revenue (Cost / Revenue), Margin (Profit/Revenue).
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Ensure necessary product identifier columns
    for c in ['Product ID', 'Product Name']:
        if c not in df.columns:
            raise ValueError(f'Missing column for cost diagnostics: {c}')

    # If raw df (order-level) provided, aggregate first
    if 'Cost' in df.columns and 'Sales' in df.columns and 'Units' in df.columns:
        # assume order-level
        agg = df.groupby(['Product ID', 'Product Name'], dropna=False).agg(
            Revenue=('Sales', 'sum'),
            Profit=('Gross Profit', 'sum'),
            Cost=('Cost', 'sum'),
            Units=('Units', 'sum')
        ).reset_index()
    else:
        # expect product-level with Revenue/Profit
        agg = df.copy()
        if 'Cost' not in agg.columns:
            agg['Cost'] = 0
        if 'Units' not in agg.columns:
            agg['Units'] = 0

    agg['Cost_per_Unit'] = agg['Cost'] / agg['Units'].replace(0, 1)
    agg['Cost_to_Revenue'] = (agg['Cost'] / agg['Revenue']).replace([np.inf, -np.inf], np.nan).fillna(0)
    agg['Margin'] = (agg['Profit'] / agg['Revenue']).replace([np.inf, -np.inf], np.nan).fillna(0)

    return agg


def flag_high_cost_products(cost_df: pd.DataFrame, cost_to_revenue_thresh: float = 0.5, low_margin_thresh: float = 0.1) -> pd.DataFrame:
    """Flag products with cost issues.

    - cost_to_revenue_thresh: flag when Cost/Revenue >= thresh
    - low_margin_thresh: flag when Margin <= thresh
    Returns subset with Flag column detailing reasons.
    """
    if cost_df is None or cost_df.empty:
        return pd.DataFrame()

    df = cost_df.copy()
    reasons = []
    for _, row in df.iterrows():
        r = []
        if row.get('Cost_to_Revenue', 0) >= cost_to_revenue_thresh:
            r.append('High cost share')
        if row.get('Margin', 0) <= low_margin_thresh:
            r.append('Low margin')
        if row.get('Cost_per_Unit', 0) > 0 and row.get('Profit', 0) <= 0:
            r.append('Unprofitable')
        reasons.append('; '.join(r) if r else '')

    df['Flag'] = reasons
    flagged = df[df['Flag'] != ''].copy()
    return flagged.sort_values(['Cost_to_Revenue', 'Margin'], ascending=[False, True])


def compute_margin_volatility(order_df: pd.DataFrame, period: str = 'M') -> pd.DataFrame:
    """Compute margin volatility per product using period aggregation (default monthly).

    Returns DataFrame with Product ID, Product Name, MarginVolatility (stddev of period margin).
    """
    if order_df is None or order_df.empty:
        return pd.DataFrame()

    df = order_df.copy()
    if 'Order Date' not in df.columns:
        return pd.DataFrame()

    df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    # compute margin per order
    df['Margin'] = (df['Gross Profit'] / df['Sales']).replace([np.inf, -np.inf], np.nan).fillna(0)

    # group by product and period
    df['Period'] = df['Order Date'].dt.to_period(period).dt.to_timestamp()
    grouped = df.groupby(['Product ID', 'Product Name', 'Period']).agg(
        Revenue=('Sales', 'sum'), Profit=('Gross Profit', 'sum')
    ).reset_index()
    grouped['PeriodMargin'] = (grouped['Profit'] / grouped['Revenue']).replace([np.inf, -np.inf], np.nan).fillna(0)

    vol = grouped.groupby(['Product ID', 'Product Name']).agg(MarginVolatility=('PeriodMargin', 'std')).reset_index()
    vol['MarginVolatility'] = vol['MarginVolatility'].fillna(0)
    return vol


def compute_margin_risk(order_df: pd.DataFrame,
                        rev_weight: float = 0.25,
                        profit_weight: float = 0.25,
                        vol_weight: float = 0.4,
                        conc_weight: float = 0.1,
                        top_pct: float = 0.8) -> pd.DataFrame:
    """Compute a composite margin-risk score per product.

    Components:
    - volatility (higher increases risk)
    - low margin (lower margin increases risk)
    - low profit contribution (lower contribution increases risk)
    - concentration dependency (if product is within top `top_pct` of revenue or profit, treated as critical -> increases risk)

    Returns product-level DataFrame with RiskScore (0-1) and RiskFlag (High/Medium/Low).
    """
    if order_df is None or order_df.empty:
        return pd.DataFrame()

    # product aggregates
    prod = compute_product_metrics(order_df)

    # volatility
    vol = compute_margin_volatility(order_df)
    prod = prod.merge(vol[['Product ID', 'MarginVolatility']], on='Product ID', how='left')
    prod['MarginVolatility'] = prod['MarginVolatility'].fillna(0)

    # profit contribution already between 0-1
    if 'Profit Contribution' not in prod.columns:
        prod['Profit Contribution'] = 0

    # margin: use Avg_Margin_pct (percent) -> convert to 0-1
    prod['Margin_frac'] = prod['Avg_Margin_pct'] / 100.0
    prod['Margin_frac'] = prod['Margin_frac'].fillna(0)

    # concentration: find pareto ranks
    pareto = compute_pareto_products(prod, revenue_col='Revenue', profit_col='Profit')
    # rank is index+1
    pareto = pareto.reset_index().rename(columns={'index': 'Rank'})
    # determine cutoff positions
    rev_cut = find_pareto_cutoff(pareto, pct=top_pct, col='CumRevenuePct')
    prof_cut = find_pareto_cutoff(pareto, pct=top_pct, col='CumProfitPct')
    pareto['InTopRevenue'] = pareto.index < rev_cut
    pareto['InTopProfit'] = pareto.index < prof_cut

    pareto_flag = pareto[['Product ID', 'InTopRevenue', 'InTopProfit']]
    prod = prod.merge(pareto_flag, on='Product ID', how='left')
    prod['InTopRevenue'] = prod['InTopRevenue'].fillna(False)
    prod['InTopProfit'] = prod['InTopProfit'].fillna(False)

    # normalize components
    # volatility normalized by max
    max_vol = prod['MarginVolatility'].max() if prod['MarginVolatility'].max() > 0 else 1
    prod['vol_norm'] = prod['MarginVolatility'] / max_vol

    # margin normalized: higher margin lowers risk -> use (1 - margin_norm)
    min_m, max_m = prod['Margin_frac'].min(), prod['Margin_frac'].max()
    denom_m = max_m - min_m if max_m - min_m > 0 else 1
    prod['margin_norm'] = (prod['Margin_frac'] - min_m) / denom_m

    # profit contribution is already 0-1 but may be relative; normalize
    min_pc, max_pc = prod['Profit Contribution'].min(), prod['Profit Contribution'].max()
    denom_pc = max_pc - min_pc if max_pc - min_pc > 0 else 1
    prod['pc_norm'] = (prod['Profit Contribution'] - min_pc) / denom_pc

    # concentration flag: 1 if in top revenue or top profit
    prod['conc_flag'] = ((prod['InTopRevenue']) | (prod['InTopProfit'])).astype(float)

    # risk components: higher vol_norm -> higher risk, lower margin_norm -> higher risk (so 1 - margin_norm),
    # lower pc_norm -> higher risk (so 1 - pc_norm), concentration adds fixed risk multiplier
    prod['risk_raw'] = (vol_weight * prod['vol_norm'] +
                        rev_weight * (1 - prod['margin_norm']) +
                        profit_weight * (1 - prod['pc_norm']) +
                        conc_weight * prod['conc_flag'])

    # normalize risk to 0-1
    min_r, max_r = prod['risk_raw'].min(), prod['risk_raw'].max()
    denom_r = max_r - min_r if max_r - min_r > 0 else 1
    prod['RiskScore'] = (prod['risk_raw'] - min_r) / denom_r

    # categorize
    prod['RiskFlag'] = pd.qcut(prod['RiskScore'].fillna(0), q=3, labels=['Low', 'Medium', 'High'])

    return prod[['Product ID', 'Product Name', 'Revenue', 'Profit', 'Margin_frac', 'MarginVolatility', 'Profit Contribution', 'RiskScore', 'RiskFlag', 'conc_flag']]
