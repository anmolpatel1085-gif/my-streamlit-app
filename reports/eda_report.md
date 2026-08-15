# EDA Research Report — Product Line Profitability & Margin Performance

## Executive summary

This analysis identifies which products and divisions are driving profitability for Nassau Candy Distributor, highlights margin-risk products, and surfaces candidates for pricing or sourcing changes.

## Data overview
- Source: order-level exports (orders.csv)
- Key fields: Sales, Cost, Gross Profit, Units, Product ID/Name, Division, Order Date

## Methods
- Product-level KPIs: Revenue, Profit, Units, Margin, Profit per Unit
- Pareto concentration: cumulative revenue and profit per product
- Cost diagnostics: cost per unit, cost-to-revenue, margin
- Margin-risk: composite score from margin volatility, margin level, profit contribution, and concentration

## Selected findings
- Pareto concentration: a limited set of products account for ~80% of revenue/profit — focus assortment and promotions there.
- Cost flags: high cost-to-revenue products were identified (see `reports/images` for charts if generated).
- Risk scoring: products with high volatility and low profit contribution received High risk flags and should be reviewed for repricing or discontinuation.

## Recommended next steps
1. Validate supplier pricing for flagged products and negotiate costs for high-cost items.\n2. Review promotional effectiveness on high-sales/low-margin SKUs.\n3. Rationalize long-tail low-profit SKUs to reduce SKU complexity.\n4. Schedule a quarterly run of this pipeline and incorporate into reporting.

## Artifacts
- Dashboard: `app/dashboard.py` (interactive Streamlit app)
- Notebook: `notebooks/eda.ipynb` (this notebook)
- Downloads: product-level tables and Pareto CSV available from the dashboard

