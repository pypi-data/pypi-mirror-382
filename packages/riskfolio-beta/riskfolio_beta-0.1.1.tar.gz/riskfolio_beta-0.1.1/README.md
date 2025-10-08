# finattrib

**finattrib** is a Python library for capital attribution, RWA (Risk-Weighted Assets) analysis, and profitability evaluation in financial risk management. It provides a modular and object-oriented framework to calculate, attribute, and visualize key risk metrics such as TCE (Tangible Common Equity) allocation, capital charge, return on capital, and RWA share.  

The library is designed for quant developers, risk managers, and financial analysts who want a flexible and extensible way to model portfolio risk and performance attribution at various aggregation levels (e.g., desk, product, portfolio).

---

## 🚀 Features

- **Capital Charge Computation** – Calculate capital charge and net income from allocated TCE and PnL.  
- **Attribution Table Generation** – Aggregate key metrics by desk, product, or other dimensions with automatically calculated performance ratios.  
- **Scenario Analysis** – Apply weight changes to products and instantly recompute RWA and profitability metrics.  
- **Extensible Design** – Built with modular components (`core`, `reporting`, `validators`, `exceptions`, etc.) to support future extensions.  
- **Object-Oriented API** – Easily integrate with larger analytics pipelines or use as a standalone analysis tool.  

---

## 📦 Installation

Clone the repository and install the package in **editable mode** (recommended during development):

```bash
git clone https://github.com/yourusername/finattrib.git
cd finattrib
pip install -e .
