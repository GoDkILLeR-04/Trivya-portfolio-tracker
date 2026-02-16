"""
Trivya Portfolio Tracker - Unified Dashboard
Showcases: Portfolio Analytics + Options Greeks + Strategy Backtesting
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Try to import backtesting module
try:
    from backtest_strategies import StrategyBacktester
    BACKTEST_AVAILABLE = True
except:
    BACKTEST_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="Trivya Portfolio Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {font-size:20px !important; font-weight: bold;}
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📊 Trivya Portfolio Tracker")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**All-in-One Portfolio Analytics**

Three powerful tools combined:
- 📈 Equity Portfolio Tracker
- 📉 Options Greeks Calculator  
- 🎲 Strategy Backtesting
""")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Tool:",
    ["🏠 Home", "📈 Portfolio Tracker", "📉 Options Tracker", "🎲 Strategy Backtesting"]
)

# Data loading functions
@st.cache_data(ttl=300)
def load_equity_holdings():
    try:
        df = pd.read_csv('holdings.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_options_positions():
    try:
        df = pd.read_csv('options_positions.csv')
        df['date'] = pd.to_datetime(df['date'])
        df['expiry'] = pd.to_datetime(df['expiry'])
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_current_prices(symbols):
    prices = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            prices[symbol] = info.get('currentPrice', info.get('regularMarketPrice', 0))
        except:
            prices[symbol] = 0
    return prices

@st.cache_data(ttl=300)
def fetch_nifty_spot():
    try:
        nifty = yf.Ticker("^NSEI")
        return nifty.info.get('regularMarketPrice', nifty.history(period='1d')['Close'].iloc[-1])
    except:
        return 25000

def calculate_equity_metrics(holdings_df, prices):
    for i, row in holdings_df.iterrows():
        current_price = prices.get(row['symbol'], 0)
        holdings_df.at[i, 'current_price'] = current_price
        holdings_df.at[i, 'invested_value'] = row['quantity'] * row['buy_price']
        holdings_df.at[i, 'current_value'] = row['quantity'] * current_price
        holdings_df.at[i, 'pnl'] = (current_price - row['buy_price']) * row['quantity']
        holdings_df.at[i, 'pnl_pct'] = ((current_price - row['buy_price']) / row['buy_price']) * 100
    return holdings_df

def black_scholes_greeks(S, K, T, r, sigma, option_type):
    if T <= 0:
        price = max(S - K, 0) if option_type == 'CE' else max(K - S, 0)
        return {'price': price, 'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'CE':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = -norm.cdf(-d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
    
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    
    return {'price': price, 'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega}

# ==================== HOME PAGE ====================
if page == "🏠 Home":
    st.title("📊 Trivya Portfolio Tracker")
    st.markdown("### Professional Portfolio Analytics for Indian Markets")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📈 Portfolio Tracker")
        st.markdown("""
        **Features:**
        - Real-time NSE/BSE prices
        - Multi-position tracking
        - Risk metrics (Sharpe, VaR, Drawdown)
        - Portfolio allocation charts
        - Performance analytics
        
        **Output:**
        - Current portfolio value & P&L
        - Best/worst performers
        - Risk-adjusted returns
        - Historical performance graphs
        """)
    
    with col2:
        st.markdown("### 📉 Options Tracker")
        st.markdown("""
        **Features:**
        - Real-time Greeks calculation
        - Black-Scholes pricing
        - Portfolio Greeks aggregation
        - Strategy P&L tracking
        - Time decay monitoring
        
        **Output:**
        - Portfolio Delta, Gamma, Theta, Vega
        - Current options prices
        - P&L by strategy
        - Days to expiry tracking
        """)
    
    with col3:
        st.markdown("### 🎲 Strategy Backtesting")
        st.markdown("""
        **Features:**
        - Historical trade analysis
        - Win rate & profit factor
        - Monte Carlo simulations (10k+)
        - Strategy comparison
        - Risk projections
        
        **Output:**
        - Backtest metrics
        - Probability of profit
        - Expected returns
        - 6-panel visualization dashboard
        """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 The Edge")
    st.info("""
    **What makes this special:**
    
    ✅ **All-in-One**: Equity + Options + Backtesting in one place
    
    ✅ **Real-time Data**: Live NSE/BSE prices via yfinance
    
    ✅ **Institutional Metrics**: Sharpe Ratio, Beta, VaR, Greeks
    
    ✅ **Predictive Analytics**: Monte Carlo simulations with 10,000+ scenarios
    
    ✅ **Indian Markets**: Specifically built for NSE/BSE with INR formatting
    
    ✅ **Professional Output**: Publication-ready charts and reports
    """)
    
    st.markdown("---")
    
    st.markdown("### 🚀 Tech Stack")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Data & Analytics:**
        - `yfinance` - Real-time market data
        - `pandas` - Data manipulation
        - `numpy` - Numerical computing
        - `scipy` - Statistical functions
        """)
    
    with col2:
        st.markdown("""
        **Visualization:**
        - `matplotlib` - Static charts
        - `plotly` - Interactive graphs
        - `streamlit` - Web dashboard
        """)
    
    st.markdown("---")
    
    st.success("👈 **Select a tool from the sidebar to see it in action!**")

# ==================== PORTFOLIO TRACKER ====================
elif page == "📈 Portfolio Tracker":
    st.title("📈 Equity Portfolio Tracker")
    st.markdown("*Real-time tracking with risk analytics and performance metrics*")
    
    equity_holdings = load_equity_holdings()
    
    if equity_holdings.empty:
        st.error("No equity data found. Please add holdings.csv")
        st.stop()
    
    with st.spinner("Fetching live NSE/BSE prices..."):
        symbols = equity_holdings['symbol'].unique().tolist()
        prices = fetch_current_prices(symbols)
        equity_holdings = calculate_equity_metrics(equity_holdings, prices)
    
    # Key metrics
    st.markdown("### 📊 Portfolio Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    total_invested = equity_holdings['invested_value'].sum()
    total_current = equity_holdings['current_value'].sum()
    total_pnl = equity_holdings['pnl'].sum()
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    col1.metric("Portfolio Value", f"₹{total_current:,.0f}", f"{total_pnl_pct:+.2f}%")
    col2.metric("Total P&L", f"₹{total_pnl:,.0f}")
    col3.metric("Invested", f"₹{total_invested:,.0f}")
    
    agg_holdings = equity_holdings.groupby('symbol').agg({'pnl': 'sum'}).reset_index()
    num_stocks = len(agg_holdings)
    num_profitable = len(agg_holdings[agg_holdings['pnl'] > 0])
    col4.metric("Positions", f"{num_stocks} stocks", f"{num_profitable} winning")
    
    st.markdown("---")
    
    # Best/Worst performers
    col1, col2 = st.columns(2)
    with col1:
        best = equity_holdings.loc[equity_holdings['pnl_pct'].idxmax()]
        st.success("🏆 **Best Performer**")
        st.markdown(f"**{best['symbol']}**")
        st.markdown(f"P&L: ₹{best['pnl']:,.0f} ({best['pnl_pct']:+.2f}%)")
    
    with col2:
        worst = equity_holdings.loc[equity_holdings['pnl_pct'].idxmin()]
        st.error("📉 **Worst Performer**")
        st.markdown(f"**{worst['symbol']}**")
        st.markdown(f"P&L: ₹{worst['pnl']:,.0f} ({worst['pnl_pct']:+.2f}%)")
    
    st.markdown("---")
    
    # Holdings table
    st.markdown("### 📋 Holdings")
    agg_holdings = equity_holdings.groupby('symbol').agg({
        'quantity': 'sum',
        'invested_value': 'sum',
        'current_value': 'sum',
        'pnl': 'sum'
    }).reset_index()
    agg_holdings['pnl_pct'] = (agg_holdings['pnl'] / agg_holdings['invested_value'] * 100)
    
    display_df = agg_holdings.copy()
    display_df['invested_value'] = display_df['invested_value'].apply(lambda x: f"₹{x:,.0f}")
    display_df['current_value'] = display_df['current_value'].apply(lambda x: f"₹{x:,.0f}")
    display_df['pnl'] = display_df['pnl'].apply(lambda x: f"₹{x:,.0f}")
    display_df['pnl_pct'] = display_df['pnl_pct'].apply(lambda x: f"{x:+.2f}%")
    display_df.columns = ['Symbol', 'Quantity', 'Invested', 'Current Value', 'P&L', 'P&L %']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Charts
    st.markdown("### 📊 Visualizations")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(agg_holdings, values='current_value', names='symbol', 
                     title='Portfolio Allocation', hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        colors = ['green' if x > 0 else 'red' for x in agg_holdings['pnl']]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=agg_holdings['symbol'], y=agg_holdings['pnl'], 
                            marker_color=colors))
        fig.update_layout(title='P&L by Stock', xaxis_title='Stock', yaxis_title='P&L (₹)')
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk metrics
    st.markdown("### ⚠️ Risk Metrics")
    
    with st.spinner("Calculating risk metrics..."):
        symbols_str = ' '.join(symbols)
        hist_data = yf.download(symbols_str, period="1y", progress=False)['Close']
        if isinstance(hist_data, pd.Series):
            hist_data = hist_data.to_frame()
            hist_data.columns = [symbols[0]]
        
        returns = hist_data.pct_change().dropna()
        symbol_allocation = equity_holdings.groupby('symbol')['current_value'].sum()
        weights = symbol_allocation / symbol_allocation.sum()
        weights = weights.reindex(returns.columns, fill_value=0)
        portfolio_returns = (returns * weights.values).sum(axis=1)
        
        sharpe = (portfolio_returns.mean() * 252 - 0.068) / (portfolio_returns.std() * np.sqrt(252))
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        var_95 = np.percentile(portfolio_returns, 5)
        volatility = portfolio_returns.std() * np.sqrt(252)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sharpe Ratio", f"{sharpe:.3f}")
    col2.metric("Max Drawdown", f"{max_dd*100:.2f}%")
    col3.metric("VaR (95%)", f"{var_95*100:.2f}%")
    col4.metric("Volatility", f"{volatility*100:.2f}%")
    
    if sharpe > 1:
        st.success("✓ Excellent risk-adjusted returns (Sharpe > 1)")
    elif sharpe > 0:
        st.warning("⚠ Positive returns but moderate efficiency (Sharpe > 0)")
    else:
        st.error("✗ Returns below risk-free rate (Sharpe < 0)")

# ==================== OPTIONS TRACKER ====================
elif page == "📉 Options Tracker":
    st.title("📉 Options Portfolio Tracker")
    st.markdown("*Real-time Greeks calculation and options P&L tracking*")
    
    options_df = load_options_positions()
    
    if options_df.empty:
        st.warning("No options positions found. Add options_positions.csv")
        st.stop()
    
    spot_price = fetch_nifty_spot()
    st.metric("Nifty Spot Price", f"₹{spot_price:,.2f}")
    
    st.markdown("---")
    
    # Calculate Greeks
    with st.spinner("Calculating Greeks..."):
        for i, pos in options_df.iterrows():
            T = max((pos['expiry'] - datetime.now()).days / 365.0, 0.001)
            sigma = 0.20
            
            greeks = black_scholes_greeks(spot_price, pos['strike'], T, 0.068, sigma, pos['option_type'])
            
            options_df.at[i, 'current_price'] = greeks['price']
            options_df.at[i, 'delta'] = greeks['delta'] * pos['quantity']
            options_df.at[i, 'gamma'] = greeks['gamma'] * pos['quantity']
            options_df.at[i, 'theta'] = greeks['theta'] * pos['quantity']
            options_df.at[i, 'vega'] = greeks['vega'] * pos['quantity']
            
            if pos['quantity'] > 0:
                pnl = (greeks['price'] - pos['premium_paid']) * pos['quantity']
            else:
                pnl = (pos['premium_paid'] - greeks['price']) * pos['quantity']
            options_df.at[i, 'pnl'] = pnl
    
    # Portfolio Greeks
    st.markdown("### 🎯 Portfolio Greeks")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Delta", f"{options_df['delta'].sum():.2f}")
    col2.metric("Theta (Daily)", f"₹{options_df['theta'].sum():.2f}")
    col3.metric("Vega", f"₹{options_df['vega'].sum():.2f}")
    col4.metric("Total P&L", f"₹{options_df['pnl'].sum():,.0f}")
    
    st.markdown("---")
    
    # Positions table
    st.markdown("### 📋 Options Positions")
    display_options = options_df.copy()
    display_options['days_to_expiry'] = (display_options['expiry'] - datetime.now()).dt.days
    display_options = display_options[['option_type', 'strike', 'days_to_expiry', 'quantity', 
                                       'premium_paid', 'current_price', 'pnl', 'delta', 'theta']]
    st.dataframe(display_options, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Strategy P&L
    if 'strategy' in options_df.columns:
        st.markdown("### 📊 Strategy-wise P&L")
        strategy_pnl = options_df.groupby('strategy')['pnl'].sum().reset_index()
        fig = px.bar(strategy_pnl, x='strategy', y='pnl', title='P&L by Strategy',
                    color='pnl', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    # Greeks explanation
    with st.expander("📚 Understanding Greeks"):
        st.markdown("""
        **Delta**: Rate of change of option price relative to underlying price
        - Call Delta: 0 to 1 | Put Delta: -1 to 0
        
        **Gamma**: Rate of change of Delta
        - Higher Gamma = More risk near expiry
        
        **Theta**: Time decay per day
        - Negative for long positions (you lose daily)
        - Positive for short positions (you gain daily)
        
        **Vega**: Sensitivity to volatility changes
        - Long options benefit from rising volatility
        """)

# ==================== STRATEGY BACKTESTING ====================
elif page == "🎲 Strategy Backtesting":
    st.title("🎲 Strategy Backtesting & Monte Carlo")
    st.markdown("*Historical performance analysis with future projections*")
    
    if not BACKTEST_AVAILABLE:
        st.error("❌ Backtesting module not available")
        st.info("Please ensure backtest_strategies.py is in your repository")
        st.stop()
    
    # Check for trade history
    try:
        trade_data = pd.read_csv('trade_history.csv')
        st.success(f"✅ Loaded {len(trade_data)} historical trades")
    except:
        st.error("❌ trade_history.csv not found")
        st.stop()
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Simulation Parameters")
    col1, col2, col3 = st.columns(3)
    with col1:
        initial_capital = st.number_input("Initial Capital (₹)", value=100000, step=10000)
    with col2:
        num_trades = st.number_input("Trades to Simulate", value=50, min_value=10, max_value=200)
    with col3:
        num_simulations = st.number_input("Simulations", value=10000, min_value=1000, step=1000)
    
    if st.button("🚀 Run Backtest & Monte Carlo", type="primary"):
        try:
            with st.spinner("Running analysis... This may take a minute"):
                backtester = StrategyBacktester('trade_history.csv')
                
                # Backtest
                stats = backtester.backtest_options_trades()
                if not stats:
                    st.error("Backtest failed")
                    st.stop()
                
                # Monte Carlo
                mc_results = backtester.monte_carlo_simulation(
                    initial_capital=int(initial_capital),
                    num_simulations=int(num_simulations),
                    num_trades=int(num_trades)
                )
                
                # Visualizations
                fig = backtester.create_visualizations(mc_results)
            
            st.success("✅ Analysis Complete!")
            
            # Results
            st.markdown("### 📊 Backtest Results")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Trades", stats['total_trades'])
            col2.metric("Win Rate", f"{stats['win_rate']:.1f}%")
            col3.metric("Profit Factor", f"{stats['profit_factor']:.2f}")
            col4.metric("Expectancy", f"₹{stats['expectancy']:.2f}")
            
            st.markdown("---")
            
            # Interpretation
            st.markdown("### 🎯 Performance Evaluation")
            
            if stats['win_rate'] >= 60:
                st.success(f"✅ **Excellent**: Win rate of {stats['win_rate']:.1f}% indicates strong strategy")
            elif stats['win_rate'] >= 50:
                st.warning(f"⚠️ **Good**: Win rate of {stats['win_rate']:.1f}% - room for improvement")
            else:
                st.error(f"❌ **Poor**: Win rate of {stats['win_rate']:.1f}% - strategy needs refinement")
            
            if stats['profit_factor'] > 2:
                st.success(f"✅ **Strong**: Profit factor of {stats['profit_factor']:.2f} shows excellent risk/reward")
            elif stats['profit_factor'] > 1:
                st.warning(f"⚠️ **Moderate**: Profit factor of {stats['profit_factor']:.2f} - profitable but can improve")
            else:
                st.error(f"❌ **Losing**: Profit factor {stats['profit_factor']:.2f} < 1 means net loss")
            
            st.markdown("---")
            
            # Monte Carlo results
            st.markdown("### 🎲 Monte Carlo Projections")
            col1, col2, col3 = st.columns(3)
            col1.metric("Probability of Profit", f"{mc_results['prob_profit']:.1f}%")
            col2.metric("Risk of Ruin", f"{mc_results['prob_ruin']:.1f}%")
            col3.metric("Median Final Capital", f"₹{mc_results['median_final']:,.0f}")
            
            if mc_results['prob_profit'] > 70:
                st.success("✅ Strong probability of profit")
            elif mc_results['prob_profit'] > 50:
                st.warning("⚠️ Moderate probability of profit")
            else:
                st.error("❌ Low probability of profit")
            
            st.markdown("---")
            
            # Visualizations
            st.markdown("### 📈 Analysis Dashboard")
            if fig:
                st.pyplot(fig)
            
            st.markdown("---")
            
            # Trade history
            st.markdown("### 📋 Trade-by-Trade Breakdown")
            if backtester.results is not None and not backtester.results.empty:
                st.dataframe(backtester.results, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"📅 Last updated: {datetime.now().strftime('%H:%M:%S')}")
if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Trivya Portfolio Tracker v2.0**

Built by Pratyush Singh

[GitHub](https://github.com/GoDkiLLeR-04/Trivya-portfolio-tracker) | [LinkedIn](https://linkedin.com)
""")










