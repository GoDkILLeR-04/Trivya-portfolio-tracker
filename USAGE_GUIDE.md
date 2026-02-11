# 📘 Trivya Portfolio Tracker - Usage Guide

Complete step-by-step guide to get started with portfolio tracking.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/GoDkiLLeR-04/Trivya-portfolio-tracker.git
cd Trivya-portfolio-tracker

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Prepare Your Data

**Option A: Use Sample Data (Testing)**
```bash
# Rename sample files
cp sample_holdings.csv holdings.csv
cp sample_trade_history.csv trade_history.csv
cp sample_options_positions.csv options_positions.csv
```

**Option B: Use Your Own Data**

Create `holdings.csv` with this format:
```csv
symbol,quantity,buy_price,date
RELIANCE.NS,50,2450.00,2024-01-15
TCS.NS,30,3650.00,2024-02-10
```

**Important:** Use NSE symbols with `.NS` suffix (e.g., `RELIANCE.NS`, `TCS.NS`)

### Step 3: Run the Portfolio Tracker

```bash
python portfolio_tracker.py
```

**Output:**
- Console report with metrics
- `portfolio_analysis.png` - 4-panel dashboard

### Step 4: Run Backtesting (Optional)

```bash
python backtest_strategy.py
```

**Output:**
- Backtest statistics
- `backtest_analysis.png` - 6-panel report

### Step 5: Run Interactive Dashboard (Optional)

```bash
streamlit run dashboard.py
```

**Opens in browser:** Live interactive analytics at `http://localhost:8501`

---

## 📊 Understanding Your CSV Files

### `holdings.csv` - Your Stock Positions

| Column | Description | Example |
|--------|-------------|---------|
| symbol | NSE stock ticker with .NS | RELIANCE.NS |
| quantity | Number of shares | 50 |
| buy_price | Purchase price per share | 2450.00 |
| date | Purchase date | 2024-01-15 |

**Multiple Purchases:**
You can have multiple rows for the same stock (different purchase dates). The system automatically calculates weighted average cost.

```csv
symbol,quantity,buy_price,date
RELIANCE.NS,50,2450.00,2024-01-15
RELIANCE.NS,25,2520.00,2024-06-12
```

### `trade_history.csv` - Options Trades (For Backtesting)

| Column | Description | Example |
|--------|-------------|---------|
| entry_date | When trade opened | 2024-01-10 |
| exit_date | When trade closed | 2024-01-15 |
| strategy | Strategy type | Bull Call Spread |
| position_type | long or short | long |
| quantity | Lot size | 50 |
| entry_price | Premium at entry | 120 |
| exit_price | Premium at exit | 145 |

### `options_positions.csv` - Current Options (For Dashboard)

| Column | Description | Example |
|--------|-------------|---------|
| date | Position date | 2026-02-01 |
| option_type | CE or PE | CE |
| strike | Strike price | 25000 |
| expiry | Expiry date | 2026-02-27 |
| quantity | Lot size (+/- for long/short) | 50 |
| premium_paid | Entry premium | 125.50 |
| strategy | Strategy name | Bull Call Spread |

---

## 🎯 What Each Script Does

### 1. `portfolio_tracker.py` - Equity Portfolio Analytics

**What it does:**
- Fetches live NSE/BSE prices
- Calculates P&L for all positions
- Computes risk metrics (Sharpe, Beta, VaR, Max Drawdown)
- Generates 4-panel visualization

**When to use:** Daily portfolio monitoring, risk assessment

**Output:**
```
============================================================
PORTFOLIO SUMMARY
============================================================

Total Invested:    ₹5,45,000.00
Current Value:     ₹6,23,450.00
Total P&L:         ₹78,450.00 (+14.39%)

🏆 Best Performer:  INFY.NS (+22.45%)
📉 Worst Performer: HDFCBANK.NS (-5.32%)
```

### 2. `backtest_strategy.py` - Options Strategy Backtesting

**What it does:**
- Analyzes historical options trades
- Calculates win rate, profit factor, expectancy
- Runs Monte Carlo simulations (10,000+ scenarios)
- Projects future portfolio outcomes

**When to use:** Validating trading strategies, planning capital allocation

**Output:**
```
============================================================
BACKTESTING HISTORICAL OPTIONS TRADES
============================================================

Total Trades:        15
Winning Trades:      9 (60.0%)
Total P&L:           ₹45,250.00
Profit Factor:       2.15
Expectancy:          ₹3,016.67 per trade
```

### 3. `dashboard.py` - Interactive Streamlit Dashboard

**What it does:**
- Live web interface for portfolio monitoring
- Real-time Greeks calculation for options
- Interactive charts with Plotly
- Multiple pages: Overview, Equity, Options, Settings

**When to use:** Interactive analysis, presentations, daily monitoring

**Access:** Browser at `http://localhost:8501`

---

## 🔧 Common Issues & Solutions

### Issue: "Module not found"
**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall
pip install -r requirements.txt
```

### Issue: "No data found for symbol XYZ"
**Solution:**
- Ensure you're using NSE symbols with `.NS` suffix
- Examples: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`
- Not: `RELIANCE`, `TCS`, `INFY`

### Issue: "FileNotFoundError: holdings.csv"
**Solution:**
```bash
# Use sample data first
cp sample_holdings.csv holdings.csv
```

### Issue: Streamlit dashboard not loading
**Solution:**
```bash
# Check if streamlit is installed
pip install streamlit

# Run with explicit path
streamlit run dashboard.py --server.port 8501
```

---

## 📈 Best Practices

### 1. Data Management
- Keep your real `holdings.csv` private (it's in `.gitignore`)
- Regularly backup your CSV files
- Use sample files for testing

### 2. Daily Workflow
```bash
# Morning routine
python portfolio_tracker.py  # Check overnight changes

# Weekly review
python backtest_strategy.py  # Validate strategy performance

# Interactive analysis
streamlit run dashboard.py  # Deep dive into positions
```

### 3. Risk Management
- Monitor Sharpe Ratio (aim for > 1.0)
- Keep Max Drawdown < 20%
- Use Monte Carlo to understand worst-case scenarios

---

## 🎓 Learning Resources

### Understanding Metrics

**Sharpe Ratio:**
- Measures risk-adjusted returns
- > 1.0 = Good
- > 2.0 = Excellent

**Beta:**
- Portfolio sensitivity to Nifty 50
- 1.0 = Moves with market
- > 1.0 = More volatile than market

**VaR (Value at Risk):**
- Expected loss in worst 5% of days
- Example: VaR = -1.5% means you could lose 1.5%+ in bad days

**Maximum Drawdown:**
- Largest peak-to-trough decline
- Shows how much you could lose from portfolio highs

---

## 💡 Example Workflows

### Scenario 1: New User Testing
```bash
1. Clone repo
2. Install dependencies
3. cp sample_holdings.csv holdings.csv
4. python portfolio_tracker.py
5. Review portfolio_analysis.png
```

### Scenario 2: Daily Monitoring
```bash
1. Update holdings.csv with new purchases
2. python portfolio_tracker.py
3. Check P&L and risk metrics
4. Review charts for concerning patterns
```

### Scenario 3: Strategy Validation
```bash
1. Export your broker trades to trade_history.csv
2. python backtest_strategy.py
3. Analyze win rate and profit factor
4. Run Monte Carlo for future projections
5. Adjust strategy if needed
```

### Scenario 4: Client Presentation
```bash
1. streamlit run dashboard.py
2. Open browser to localhost:8501
3. Use interactive charts for discussion
4. Export screenshots for reports
```

---

## 🆘 Need Help?

1. Check [Issues](https://github.com/GoDkiLLeR-04/Trivya-portfolio-tracker/issues) on GitHub
2. Email: pratyushsingh.live@gmail.com
3. Review this guide again
4. Create a GitHub issue with:
   - Error message
   - What you tried
   - Your OS and Python version

---

## 🎯 Next Steps

Once comfortable with basics:

1. ✅ Try backtesting with your own trade history
2. ✅ Deploy Streamlit dashboard to Streamlit Cloud (free hosting)
3. ✅ Customize charts and metrics to your needs
4. ✅ Add alerts for portfolio drawdowns
5. ✅ Export data to Excel for deeper analysis

---

**Happy Trading! 📊💹**
