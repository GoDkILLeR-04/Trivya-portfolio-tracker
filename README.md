# 📊 Trivya Portfolio Tracker

<div align="center">

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Status](https://img.shields.io/badge/status-unactive-success.svg)

**Real-time equity portfolio tracker with risk analytics, Monte Carlo projections, and performance visualizations for Indian markets (NSE/BSE)**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Roadmap](#-roadmap)

</div>

---

## 🎯 Overview

For Indian equity traders and investors, Trivya is a feature-rich portfolio analytics platform built on Python. It offers institutional-grade risk metrics, Monte Carlo simulations, and expert visualizations and was built with yfinance for real-time data.

**Ideal for:**  Quantitative analysts, portfolio managers, equity traders, and finance students

### Why This Project?

- 📈 Use a weighted average cost basis to track several stock positions
- 🎲 Using Monte Carlo simulations for portfolio projections (more than 10,000 scenarios).
- 📊 Calculate the Sharpe Ratio, Beta, VaR, and Maximum Drawdown
- 🖼️ Create reports and charts that are ready for publication
- 💾 Basic data management using CSV

---

## ✨ Features

### Current Features (v1.0)

✅ **Multi-Transaction Support**
- Automatically aggregates multiple purchases of the same stock
- Calculates weighted average buy price
- Displays transaction history breakdown

✅ **Real-Time Portfolio Tracking**
- Live NSE/BSE stock prices via yfinance API
- Current portfolio value and P&L calculations
- Position-level and portfolio-level analytics

✅ **Risk Metrics Analysis**
- **Sharpe Ratio** - Risk-adjusted returns measurement
- **Beta** - Portfolio volatility vs Nifty 50
- **Value at Risk (VaR)** - 95% confidence downside risk
- **Maximum Drawdown** - Largest peak-to-trough decline
- **Annual Volatility** - Standard deviation of returns

✅ **Individual Stock Metrics**
- Annualized returns per stock
- Volatility analysis
- Stock-level Sharpe ratios

✅ **Monte Carlo Portfolio Projection**
- 10,000+ simulation scenarios
- Confidence intervals (5th, 25th, 50th, 75th, 95th percentiles)
- Probability of profit calculations
- Visual projection paths

✅ **Professional Visualizations**
- Portfolio allocation pie chart
- P&L bar charts by position
- Historical performance comparison (normalized)
- Returns distribution histogram
- Monte Carlo projection paths
- Final value probability distribution

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup
- Clone the repository
  git clone https://github.com/YOUR_USERNAME/trivya-portfolio-tracker.git
  cd trivya-portfolio-tracker
- Create virtual environment
  python -m venv venv
- Activate virtual environment
  On Windows:
  venv\Scripts\activate
- On macOS/Linux:
  source venv/bin/activate
- Install dependencies
  pip install -r requirements.txt

### Dependencies
- yfinance>=0.2.30
- pandas>=2.0.0
- numpy>=1.24.0
- matplotlib>=3.7.0
- scipy>=1.11.0

---

## 🖼️ Screenshots

### Portfolio Analytics Dashboard
![Portfolio Dashboard](outputs/portfolio_analysis.png)

*4-panel dashboard showing allocation, P&L, historical performance, and returns distribution*

### Monte Carlo Projection
![Monte Carlo](outputs/monte_carlo_projection.png)

*10,000 simulated portfolio paths with confidence intervals*

---

## 📂 Project Structure

Trivya-portfolio-tracker/
├──  portfolio_tracker.py
├──  holdings.csv
├──  requirements.txt
├──  README.md 
├──  outputs
├──  portfolio_analysis.png
├──  monte_carlo_projection.png

## 🗺️ Roadmap

| Phase | Feature | Status |
|-------|---------|--------|
| **Week 1** | Equity tracker with risk metrics | ✅ Complete |
| **Week 2** | Options Greeks calculator | 🔨 In Progress |
| **Week 3** | Streamlit interactive dashboard | 📋 Planned |
| **Week 4** | Backtesting engine | 📋 Planned |
| **Week 5** | Portfolio optimization | 📋 Planned |
| **Week 6** | Alert system & notifications | 📋 Planned |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 Use Cases

### For Traders
- Track real-time P&L across multiple positions
- Understand portfolio risk exposure (Beta, VaR)
- Project future portfolio values with Monte Carlo

### For Students
- Learn portfolio management concepts hands-on
- Understand risk metrics practically
- Build finance + Python skills simultaneously

### For Analysts
- Generate professional reports for presentations
- Export data for further analysis
- Visualize complex portfolio data easily

---

## ⚠️ Disclaimer

This tool is for **educational and analytical purposes only**. It is not financial advice. Always consult with a qualified financial advisor before making investment decisions. Past performance does not guarantee future results.

Market data is sourced from yfinance (Yahoo Finance) and may have delays or inaccuracies.

---

## 📬 Contact

**Built by:** Pratyush
**LinkedIn:** 
**Email:** pratyushsingh.live@gmail.com

**Project Link:** 
---

## 🙏 Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) for market data API
- [pandas](https://pandas.pydata.org/) for data manipulation
- [matplotlib](https://matplotlib.org/) for visualizations
- NSE India for providing market data access

---

<div align="center">

**⭐ Star this repo if you find it useful!**

</div>


