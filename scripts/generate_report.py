import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

import sys

ROOT = Path(__file__).resolve().parents[1]
# ensure project root is importable so `src` package can be found
sys.path.insert(0, str(ROOT))

from src.metrics import compute_product_metrics, compute_pareto_products, compute_cost_diagnostics, compute_margin_risk
DATA_PATH = ROOT / 'data' / 'raw' / 'orders.csv'
OUT_DIR = ROOT / 'reports'
IM_DIR = OUT_DIR / 'images'
OUT_PDF = OUT_DIR / 'executive_summary.pdf'

os.makedirs(IM_DIR, exist_ok=True)

# Load data
print(f'Loading data from {DATA_PATH}')
if not DATA_PATH.exists():
    print('Data file not found — creating fallback sample dataset')
    sample = [
        (1,1001,'2024-01-05','2024-01-07','Standard','C001','USA','Miami','FL','33101','Chocolate','East','P001','Wonka Bar - Nutty Crunch Surprise',120.00,12,48.00,72.00),
        (2,1002,'2024-01-06','2024-01-08','Express','C002','USA','Orlando','FL','32801','Chocolate','East','P002','Wonka Bar - Fudge Mallows',200.00,20,80.00,120.00),
        (3,1003,'2024-01-07','2024-01-09','Standard','C003','USA','Tampa','FL','33601','Chocolate','East','P003','Wonka Bar - Scrumdiddlyumptious',85.00,10,17.00,68.00),
    ]
    cols = ['Row ID','Order ID','Order Date','Ship Date','Ship Mode','Customer ID','Country/Region','City','State/Province','Postal Code','Division','Region','Product ID','Product Name','Sales','Units','Gross Profit','Cost']
    sdf = pd.DataFrame(sample, columns=cols)
    # ensure parent directory exists
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    sdf.to_csv(DATA_PATH, index=False)
    df = sdf.copy()
else:
    df = pd.read_csv(DATA_PATH, parse_dates=['Order Date','Ship Date'])

# Compute metrics
prod = compute_product_metrics(df)
pareto = compute_pareto_products(prod)
cost_diag = compute_cost_diagnostics(df)
risk = compute_margin_risk(df)

# Pareto chart
plt.figure(figsize=(8,4))
plt.plot(pareto['CumRevenuePct'].values, label='Cumulative Revenue')
plt.plot(pareto['CumProfitPct'].values, label='Cumulative Profit', color='orange')
plt.xlabel('Product Rank (by Revenue)')
plt.ylabel('Cumulative Share')
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1.0))
plt.legend()
plt.tight_layout()
pareto_img = IM_DIR / 'pareto.png'
plt.savefig(pareto_img, dpi=150)
plt.close()

# Cost vs Revenue scatter (top products)
top = cost_diag.sort_values('Revenue', ascending=False).head(50)
plt.figure(figsize=(8,4))
sc = plt.scatter(top['Cost'], top['Revenue'], c=top['Margin'], cmap='RdYlGn', s=80)
plt.xlabel('Total Cost')
plt.ylabel('Total Revenue')
plt.colorbar(sc, label='Margin')
plt.tight_layout()
cost_img = IM_DIR / 'cost_scatter.png'
plt.savefig(cost_img, dpi=150)
plt.close()

# Risk distribution histogram
plt.figure(figsize=(8,4))
plt.hist(risk['RiskScore'].fillna(0), bins=20, color='salmon')
plt.xlabel('Risk Score')
plt.ylabel('Number of Products')
plt.tight_layout()
risk_img = IM_DIR / 'risk_hist.png'
plt.savefig(risk_img, dpi=150)
plt.close()

# Compose PDF
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(str(OUT_PDF), pagesize=A4)
story = []

story.append(Paragraph('Executive Summary — Product Line Profitability & Margin Performance', styles['Title']))
story.append(Spacer(1, 12))

story.append(Paragraph('Overview', styles['Heading2']))
story.append(Paragraph('This report summarizes product- and division-level profitability, cost diagnostics, Pareto concentration, and margin-risk scoring for Nassau Candy Distributor. The analysis uses order-level data to compute KPIs and flag products that require attention.', styles['BodyText']))
story.append(Spacer(1, 12))

story.append(Paragraph('Profitability Findings', styles['Heading2']))
# top products by profit
top_profit = prod.sort_values('Profit', ascending=False).head(5)
text = '<br/>'.join([f"{i+1}. {row['Product Name']} — Revenue: ${row['Revenue']:.2f}, Profit: ${row['Profit']:.2f}, Margin: {row['Avg_Margin_pct']:.1f}%" for i,row in top_profit.iterrows()])
story.append(Paragraph(text, styles['BodyText']))
story.append(Spacer(1, 12))

story.append(Paragraph('Cost Findings', styles['Heading2']))
story.append(Paragraph('Cost diagnostics reveal products with high cost-to-revenue ratios and low margins; these are candidates for repricing, renegotiation, or discontinuation.', styles['BodyText']))
story.append(Image(str(cost_img), width=6*inch, height=3*inch))
story.append(Spacer(1, 12))

story.append(Paragraph('Margin-Risk Findings', styles['Heading2']))
story.append(Paragraph('Margin-risk scoring combines margin volatility, margin level, profit contribution, and concentration to prioritize products for review. Products with High risk scores should be reviewed first.', styles['BodyText']))
story.append(Image(str(risk_img), width=6*inch, height=3*inch))
story.append(Spacer(1, 12))

story.append(Paragraph('Pareto Insights', styles['Heading2']))
story.append(Paragraph('A minority of products account for the majority of revenue and profit. Focus assortment, promotions, and service levels on top products identified in the Pareto analysis.', styles['BodyText']))
story.append(Image(str(pareto_img), width=6*inch, height=3*inch))
story.append(Spacer(1, 12))

story.append(Paragraph('Recommendations', styles['Heading2']))
rec_text = '\n'.join([
    '1. Rename and prioritize top profit and high-risk SKUs for pricing and supplier review.',
    '2. Negotiate supplier costs or consider alternative factories for high cost-to-revenue products.',
    '3. Reduce promotions on high-sales/low-margin SKUs unless they have strategic value.',
    '4. Implement quarterly automated runs of this pipeline and incorporate into executive reporting.'
])
story.append(Paragraph(rec_text, styles['BodyText']))
story.append(Spacer(1, 12))

story.append(Paragraph('Artifacts', styles['Heading2']))
story.append(Paragraph('See dashboard at `app/dashboard.py`. The product-level tables and Pareto CSVs are available for download from the dashboard.', styles['BodyText']))

print(f'Writing PDF to {OUT_PDF}')
doc.build(story)
print('Done')
