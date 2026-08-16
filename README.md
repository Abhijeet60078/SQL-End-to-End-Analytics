# SQL Business Analysis Project — E-Commerce Sales

A complete, end-to-end SQL analytics project built on a simulated e-commerce
dataset (250 customers, 51 products, 1,500 orders, 4,500+ line items across
2 years). The project answers 12 realistic business questions using SQL,
covering revenue trends, customer behavior, product performance, and
operational health.

## Why this project
This mirrors what a BI/Data Analyst does day to day: take a business
question from a stakeholder, translate it into a SQL query against a
relational schema, and turn the result into an insight or recommendation.

## Tech stack
- **SQLite** (zero-setup relational database — swap in MySQL/PostgreSQL easily)
- **SQL**: joins, aggregations, window functions (`LAG`), CTEs, date functions
- **Python** (`sqlite3`, `csv`): data generation and query automation

## Project structure
```
sql_business_analysis/
├── schema.sql                       # Database schema (5 tables)
├── generate_data.py                 # Builds ecommerce.db with sample data
├── run_analysis.py                  # Runs all queries, exports CSVs
├── queries/
│   └── business_questions.sql       # 12 business questions in SQL
├── outputs/                         # CSV result of each query (for Excel/Power BI)
└── ecommerce.db                     # The generated SQLite database
```

## Data model (ERD)
```
customers 1---* orders 1---* order_items *---1 products *---1 categories
```
- **customers**: customer_id, name, email, city, state, signup_date, segment
- **orders**: order_id, customer_id, order_date, order_status, ship_state
- **order_items**: order_item_id, order_id, product_id, quantity, unit_price
- **products**: product_id, product_name, category_id, unit_price, unit_cost
- **categories**: category_id, category_name

## How to run

```bash
# 1. Generate the database (creates ecommerce.db)
python generate_data.py

# 2. Run all 12 business questions and export results to /outputs
python run_analysis.py

# 3. (Optional) Explore interactively
sqlite3 ecommerce.db
sqlite> .read queries/business_questions.sql
```

No installation needed beyond Python 3 (sqlite3 is built in).

## Business questions answered
| # | Question | Business use |
|---|----------|--------------|
| Q1 | What's the monthly revenue trend? | Track growth, spot seasonality |
| Q2 | Who are the top 10 customers by revenue? | Target for loyalty/VIP programs |
| Q3 | What are the best-selling products? | Inventory & marketing focus |
| Q4 | Which categories are most profitable? | Focus on margin, not just revenue |
| Q5 | What % of customers are repeat buyers? | Core retention metric |
| Q6 | How is average order value trending? | Pricing / upsell strategy |
| Q7 | How fast is the customer base growing? | Acquisition tracking |
| Q8 | Which customers are at risk of churning? | Win-back campaign targeting |
| Q9 | Which regions generate the most revenue? | Regional marketing/logistics |
| Q10 | What's the order cancellation/return rate? | Operational health check |
| Q11 | RFM (Recency, Frequency, Monetary) per customer | Customer segmentation base table |
| Q12 | What's the year-over-year revenue growth? | Headline metric for leadership |

## Sample insights (from the generated dataset)
- **Repeat purchase rate is 84.8%** — most customers who buy, buy again, suggesting good product-market fit.
- **Home & Kitchen** is the top revenue *and* profit category (~47% margin), while **Electronics** has the lowest margin (~42%) despite high revenue — worth reviewing pricing/cost there.
- The **top 10 customers contribute a disproportionate share of revenue**, supporting a case for a formal VIP/loyalty tier.
- **~14% of orders** are cancelled or returned combined — worth investigating root causes (e.g., specific product categories or regions).
- **50 customers (of 191 active)** haven't ordered in 90+ days — a concrete, actionable churn/win-back list.

*(Note: since data is randomly generated, exact numbers will vary slightly if you regenerate — the query logic and insight structure is what to showcase.)*

## How to extend this for your resume/portfolio
- **Add a dashboard**: Load `outputs/*.csv` into Power BI/Tableau/Excel and build 3-4 visuals (revenue trend, top customers, category profit, churn list).
- **Swap in real data**: Replace `generate_data.py` with a real public dataset (e.g., Kaggle's "Online Retail" or "Superstore" dataset) to add authenticity.
- **Move to a real RDBMS**: Import `schema.sql` into MySQL/PostgreSQL to demonstrate you're not limited to SQLite.
- **Add a write-up**: A one-page PDF/slide summarizing the 3 biggest insights and your recommendation — this is what turns "I ran some queries" into "I did an analysis."

## Suggested resume bullet
> Designed and queried a 5-table relational e-commerce database (SQLite/SQL) to answer 12 business questions across revenue, customer retention, and profitability; identified an 85% repeat-purchase rate and a 50-customer churn risk segment, and exported results for BI dashboarding.
