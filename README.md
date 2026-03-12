# CommerceIQ — Unified Commerce Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly.js-2.32-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)

> A full-stack e-commerce analytics platform that generates realistic Indian market data and visualises it through an interactive dark-themed dashboard. Built to demonstrate end-to-end data engineering, from synthetic data pipelines to production-quality BI visualisation.

CommerceIQ combines a Python data generation engine with a self-contained HTML dashboard featuring 15+ interactive Plotly charts, real-time filtering, and AI-powered insight summaries — all running offline without any backend dependencies.

---

## ✨ Features

| Area | Highlights |
|------|-----------|
| 📊 **Sales Analytics** | Revenue trends, top products, category breakdowns, channel analysis, state-wise revenue tables |
| 🛒 **E-Commerce Intelligence** | Conversion funnels, marketing channel ROAS, customer segmentation, traffic trends, new vs returning users |
| 📦 **Operations & Supply Chain** | Warehouse performance, delivery SLA tracking, return rate analysis, stock cover forecasting, inventory health |
| 🎛️ **Global Filters** | Date period (quarterly/custom), sales channel, customer segment — updates all KPIs and charts simultaneously |
| 🤖 **AI Insights** | Auto-generated narrative summaries for each dashboard tab based on filtered data |
| 🇮🇳 **Indian Market Focus** | Faker `en_IN` locale, INR formatting, 12 major Indian cities, festive season (Oct–Dec) demand modelling |
| 🔒 **Fully Offline** | Zero external API calls — all data embedded in JavaScript, works without internet |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data Generation** | Python 3.10+, Faker, Pandas, NumPy | Synthetic dataset creation with realistic distributions |
| **Visualisation** | Plotly.js 2.32 | Interactive charts with hover tooltips, zoom, pan |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Single-file dashboard, no build step required |
| **Typography** | Inter (Google Fonts) | Clean, professional UI text rendering |
| **Design System** | Custom dark theme (#0f172a / #1e293b / #06b6d4) | Production-grade visual identity |

---

## 📋 Dataset Schema

### `customers.csv` — 500 rows

| Column | Type | Description |
|--------|------|-------------|
| `CustomerID` | string | Unique ID (CUST-0001 to CUST-0500) |
| `Name` | string | Indian locale names via Faker |
| `City` | string | One of 12 major Indian cities |
| `State` | string | Mapped from city |
| `Email` | string | Generated email address |
| `Segment` | string | B2C (60%) / B2B (30%) / Enterprise (10%) |
| `JoinDate` | date | Random date between 2020–2024 |

### `products.csv` — 50 rows

| Column | Type | Description |
|--------|------|-------------|
| `ProductID` | string | PROD-001 to PROD-050 |
| `Name` | string | Product name |
| `Category` | string | Electronics / Apparel / Home / Sports / Beauty |
| `Price` | float | Electronics: ₹2,000–8,000; Others: ₹300–2,500 |
| `Cost` | float | Price × 0.6 |
| `Stock` | int | Random 0–500 units |
| `ReorderLevel` | int | Fixed at 50 units |

### `orders.csv` — 5,000 rows

| Column | Type | Description |
|--------|------|-------------|
| `OrderID` | string | ORD-00001 to ORD-05000 |
| `CustomerID` | string | FK → customers |
| `OrderDate` | date | Jan–Dec 2024, Oct–Dec weighted +40% |
| `Channel` | string | Online (50%) / Marketplace (35%) / InStore (15%) |
| `Status` | string | Delivered (80%) / Returned (12%) / Pending (8%) |

### `order_items.csv` — ~12,500 rows

| Column | Type | Description |
|--------|------|-------------|
| `OrderID` | string | FK → orders |
| `ProductID` | string | FK → products |
| `Quantity` | int | 1–5 units |
| `UnitPrice` | float | Product price at time of order |
| `Discount` | float | 0–20% random discount |

### `operations.csv` — 5,000 rows

| Column | Type | Description |
|--------|------|-------------|
| `OrderID` | string | FK → orders (1:1) |
| `WarehouseID` | string | WH-North / South / East / West |
| `ShipDate` | date | OrderDate + 1–3 days |
| `DeliveryDate` | date | ShipDate + 1–7 days |
| `DeliveryDays` | int | Total days from order to delivery |
| `OnTimeFlag` | int | 1 if DeliveryDays ≤ 5, else 0 |
| `ReturnFlag` | int | Category-based: Electronics 15%, Apparel 10%, Others 5% |
| `ReturnReason` | string | Defective / Wrong Size / Changed Mind / Damaged / Not as Expected |

> **Data Quality:** ~2% random nulls injected in non-key columns to simulate real-world data quality issues.

---

## 🚀 How to Run

### Prerequisites

```bash
pip install faker pandas numpy
```

### Step 1: Generate Data

```bash
python generate_data.py
```

This creates 5 CSV files in the `./data/` directory with reproducible outputs (seed=42).

### Step 2: Open Dashboard

```bash
# Simply open in any browser — no server needed
open dashboard/index.html

# Or serve locally for development
python -m http.server 8000 --directory dashboard
```

Navigate to `http://localhost:8000` and explore all three dashboard tabs.

---

## 📊 Dashboard Modules

### Tab 1 — Sales Analytics
Six KPI cards showing total revenue, orders, gross profit, margin, AOV, and YTD achievement. Includes a dual-axis revenue/orders trend chart, top 10 product bar chart, category donut, channel comparison, and state-wise revenue table.

### Tab 2 — E-Commerce Intelligence
Conversion funnel visualisation (Sessions → Cart → Checkout → Purchase), marketing channel performance table with ROAS metrics, customer segment distribution, monthly traffic trends, and new vs returning customer analysis.

### Tab 3 — Operations & Supply Chain
Inventory distribution by warehouse and category, monthly return rate trend, stock cover days forecast, top returned products with reasons, and warehouse performance comparison table with SLA compliance.

---

## 📸 Screenshots

> Screenshots will be added after deployment. The dashboard features a dark theme with teal accents, responsive grid layout, and fully interactive Plotly charts.

---

## 🔮 Future Enhancements

1. **Real-time Data Pipeline** — Connect to PostgreSQL/MongoDB for live data ingestion with Apache Kafka streaming
2. **ML Forecasting Module** — Time-series demand forecasting using Prophet or LSTM models for inventory optimisation
3. **Cohort Analysis Engine** — Customer lifetime value (CLV) calculation with retention heatmaps and churn prediction
4. **Automated Email Reports** — Scheduled PDF report generation with anomaly detection alerts via SendGrid
5. **Multi-tenant Architecture** — Role-based access control with JWT authentication for enterprise deployment

---

## 📁 Project Structure

```
CommerceIQ/
├── generate_data.py          # Python data generation script
├── data/
│   ├── customers.csv         # 500 customer profiles
│   ├── products.csv          # 50 product SKUs
│   ├── orders.csv            # 5,000 orders
│   ├── order_items.csv       # ~12,500 line items
│   └── operations.csv        # 5,000 fulfilment records
├── dashboard/
│   └── index.html            # Self-contained interactive dashboard
└── README.md                 # This file
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

**Built with data engineering best practices for the Indian e-commerce market.**
