<h1 align=center> riskfolio_beta </h1>

* [📘 Overview: Risk Attribution for Modern Banking Portfolios](#1)
* [⚖️ From Mean-Variance Allocation to Basel-Aligned Attribution](#2)
* [🚀 Features](#3)
* [🧰 Core Functions & Usage Guide](#4)
* [📦 Installation](#5)

---

**riskfolio_beta** is a Python library for capital attribution, RWA (Risk-Weighted Assets) analysis, and profitability evaluation in financial risk management. It provides a modular and object-oriented framework to calculate, attribute, and visualize key risk metrics such as TCE (Tangible Common Equity) allocation, capital charge, return on capital, and RWA share.  

The library is designed for quant developers, risk managers, and financial analysts who want a flexible and extensible way to model portfolio risk and performance attribution at various aggregation levels (e.g., desk, product, portfolio).

This library is still in beta version. Please read instructions carefully before using and check the details of each function when necessary.

---

<h2 id='1'> 📘 Overview: Risk Attribution for Modern Banking Portfolios </h2>

In the post-Basel III era, capital allocation is no longer a matter of simple portfolio optimization — it is a regulatory imperative. Banks are required to calculate and manage a series of risk-sensitive metrics such as Risk-Weighted Assets (RWA), Total Common Equity (TCE) allocation, and G-SIB (Global Systemically Important Bank) scores. These measures directly influence a bank’s minimum capital requirements, cost of equity, and even its systemic surcharge, shaping everything from product pricing to strategic asset mix.

This project provides a modular, Python-based library that demonstrates how these regulatory metrics can be computed, attributed, and stress-tested at a granular level (e.g., by desk, product, or counterparty). Built around synthetic fixed-income trading data, it illustrates the computational backbone behind modern regulatory reporting and internal capital allocation — serving as both a teaching tool and a foundation for production-scale systems.

---

<h2 id = '2'> ⚖️ From Mean-Variance Allocation to Basel-Aligned Attribution </h2>


Traditional portfolio asset allocation techniques focus on optimizing risk-adjusted returns by balancing expected return, volatility, and correlation — often ignoring regulatory constraints. However, for banks subject to Basel III, capital is the scarce resource, and decisions must be evaluated through the lens of their regulatory cost. For example, a high-yield bond desk might offer attractive returns, but its elevated RWA and G-SIB contribution could erode net profitability once capital charges are considered.

This library bridges that gap. Instead of optimizing portfolios purely for Sharpe ratios or tracking error, it enables users to attribute capital consumption and regulatory costs across organizational dimensions. The result is a clear picture of which activities truly create economic value after accounting for regulatory drag, and how alternative risk-weight or business-mix scenarios would impact capital efficiency.

---

<h2 id = '3'> 🚀 Features </h2>

- **Capital Charge Computation** – Calculate capital charge and net income from allocated TCE and PnL.  
- **Attribution Table Generation** – Aggregate key metrics by desk, product, or other dimensions with automatically calculated performance ratios.  
- **Scenario Analysis** – Apply weight changes to products and instantly recompute RWA and profitability metrics.  
- **Extensible Design** – Built with modular components (`core`, `reporting`, `validators`, `exceptions`, etc.) to support future extensions.  
- **Object-Oriented API** – Easily integrate with larger analytics pipelines or use as a standalone analysis tool.  

---


<h2 id = '4'> 🧰 Core Functions & Usage Guide </h2>

This section provides a comprehensive overview of the core functions included in the library. Each function is designed to support portfolio risk attribution, Basel III capital calculations, and scenario analysis workflows. Below you’ll find the purpose, key parameters, return values, and sample usage examples for each major function.

To give a try on your own with these functions, you can download the [**mock data**](https://github.com/kerwinliao/riskfolio/blob/main/content/fif_trades_test.csv) and [**code example**](https://github.com/kerwinliao/riskfolio/blob/main/content/test_demo.py).

---

### 1. `compute_gsib_toy(df: pd.DataFrame) -> dict`

**Purpose:**  
Computes a simplified Global Systemically Important Bank (G-SIB) score based on portfolio data. The score is calculated from four dimensions defined by the Basel Committee: size, interconnectedness, complexity, and cross-jurisdictional activity.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `df` | `pd.DataFrame` | Portfolio-level DataFrame containing columns such as `EAD`, `desk`, `cp_rating`, `notional`, `product`, `maturity_days`, and `country`. |

**Returns:**  
`dict` – A dictionary of scores for each G-SIB component and the total score.

**Example:**

```python
from riskfolio_beta.core import AttributionEngine

scores = AttributionEngine.compute_gsib_toy(df)
print(scores)
```

**Output Example:**

```python
{
  "size_score": 68.52,
  "interconnectedness_score": 41.20,
  "complexity_score": 32.15,
  "cross_jurisdiction_score": 12.00,
  "G_SIB_total": 45.67
}
```

---

### 2. `attribution_table(df: pd.DataFrame, dims=("desk",), metrics=None) -> pd.DataFrame`

**Purpose:**  
Generates a risk and return attribution table aggregated by one or more portfolio dimensions (e.g., desk, product, region). The table summarizes key financial metrics and performance indicators such as return on TCE and RWA-based returns.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `df` | `pd.DataFrame` | Input portfolio data containing financial metrics. |
| `dims` | `tuple` | Columns to group by (default: `("desk",)`). |
| `metrics` | `dict` | Optional mapping of metric names to aggregation methods. If `None`, defaults include `notional`, `EAD`, `RWA`, `PnL`, `TCE_alloc`, and `Net_Income`. |

**Returns:**  
`pd.DataFrame` – A summary attribution table with calculated metrics.

**Example:**

```python
from riskfolio_beta.core import AttributionEngine

summary = AttributionEngine.attribution_table(df, dims=("desk", "product"))
print(summary.head())
```

**Output Example:**

| desk       | product          | notional | EAD     | RWA     | PnL     | TCE_alloc | Net_Income | Return_on_TCE | RWA_Return | RWA_Share |
|------------|------------------|----------|---------|---------|---------|------------|-------------|----------------|------------|------------|
| Credit     | HY_Bond          | 21000000 | 1900000 | 890000  | 112000  | 450000     | 88000       | 0.1956         | 0.0988     | 0.42       |
| Credit     | NonAgency_MBS    | 34000000 | 2700000 | 1100000 | 145000  | 550000     | 105000      | 0.1909         | 0.0954     | 0.52       |
---

✅ **Best Practice Tips:**

- Use `apply_weight_scenario()` **before** generating an attribution table if you want to evaluate the impact of portfolio adjustments.
- Combine `compute_gsib_toy()` with `attribution_table()` to understand both **systemic risk contribution** and **return efficiency** under Basel III metrics.
- Automate scenario sweeps by looping over different `weight_changes` dictionaries for sensitivity analysis.


---

<h2 id = '5'> 📦 Installation </h2>

Use **pip** function in Python to install (easy and convenient):

```bash
pip install riskfolio-beta
