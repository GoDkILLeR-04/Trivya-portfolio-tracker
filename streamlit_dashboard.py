import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from scipy.stats import norm
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Try to import StrategyBacktester - with proper error handling
try:
   try:
    from backtest_strategies import StrategyBacktester
    BACKTEST_AVAILABLE = True
except ImportError:
    BACKTEST_AVAILABLE = False
    BACKTEST_AVAILABLE = True
except ImportError:
    BACKTEST_AVAILABLE = False
    # Will show warning in sidebar later


# Page configuration
st.set_page_config(
    page_title="Portfolio Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📊 Portfolio Dashboard")
st.sidebar.markdown("---")

# Show warning if backtesting not available
if not BACKTEST_AVAILABLE:
    st.sidebar.warning("⚠️ **Backtesting Unavailable**\n\nMake sure `backtest_strategies.py` is in the same folder!")

page = st.sidebar.radio(
    pages = ["🏠 Overview", "📈 Equity Analysis", "📉 Options Analysis", "⚙️ Settings"]
if BACKTEST_AVAILABLE:
    pages.insert(3, "📊 Strategy Backtesting")

page = st.sidebar.radio("Navigate to:", pages)

# Load data functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_equity_holdings():
    """Load equity holdings from CSV"""
    try:
        df = pd.read_csv('holdings.csv')  # Use sample data for demo
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("holdings.csv not found!")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_options_positions():
    """Load options positions from CSV"""
    try:
        df = pd.read_csv('options_positions.csv')  # Use sample data
        df['date'] = pd.to_datetime(df['date'])
        df['expiry'] = pd.to_datetime(df['expiry'])
        return df
    except FileNotFoundError:
        st.warning("options_positions.csv not found. Options analysis unavailable.")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def fetch_current_prices(symbols):
    """Fetch current prices for symbols"""
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
    """Fetch Nifty spot price"""
    try:
        nifty = yf.Ticker("^NSEI")
        return nifty.info.get('regularMarketPrice', 
                             nifty.history(period='1d')['Close'].iloc[-1])
    except:
        return 25000

def calculate_equity_metrics(holdings_df, prices):
    """Calculate equity portfolio metrics"""
    for i, row in holdings_df.iterrows():
        current_price = prices.get(row['symbol'], 0)
        holdings_df.at[i, 'current_price'] = current_price
        holdings_df.at[i, 'invested_value'] = row['quantity'] * row['buy_price']
        holdings_df.at[i, 'current_value'] = row['quantity'] * current_price
        holdings_df.at[i, 'pnl'] = (current_price - row['buy_price']) * row['quantity']
        holdings_df.at[i, 'pnl_pct'] = ((current_price - row['buy_price']) / row['buy_price']) * 100
    
    return holdings_df

def black_scholes_greeks(S, K, T, r, sigma, option_type):
    """Calculate Black-Scholes Greeks"""
    if T <= 0:
        price = max(S - K, 0) if option_type == 'CE' else max(K - S, 0)
        return {'price': price, 'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'CE':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                 - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = -norm.cdf(-d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                 + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
    
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    
    return {'price': price, 'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega}

# ==================== OVERVIEW PAGE ====================
if page == "🏠 Overview":
    st.title("📊 Portfolio Analytics Dashboard")
    st.markdown("### Real-time Portfolio Monitoring & Analysis")
    
    # Load data
    equity_holdings = load_equity_holdings()
    options_positions = load_options_positions()
    
    if equity_holdings.empty:
        st.error("No equity data available. Please add sample_holdings.csv")
        st.stop()
    
    # Fetch current prices
    with st.spinner("Fetching live prices..."):
        symbols = equity_holdings['symbol'].unique().tolist()
        prices = fetch_current_prices(symbols)
        equity_holdings = calculate_equity_metrics(equity_holdings, prices)
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_invested = equity_holdings['invested_value'].sum()
    total_current = equity_holdings['current_value'].sum()
    total_pnl = equity_holdings['pnl'].sum()
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    with col1:
        st.metric(
            "Total Portfolio Value",
            f"₹{total_current:,.0f}",
            f"{total_pnl_pct:+.2f}%"
        )
    
    with col2:
        st.metric(
            "Total P&L",
            f"₹{total_pnl:,.0f}",
            delta_color="normal" if total_pnl >= 0 else "inverse"
        )
    
    with col3:
        st.metric(
            "Total Invested",
            f"₹{total_invested:,.0f}"
        )
    
    with col4:
        num_stocks = len(equity_holdings['symbol'].unique())
        num_profitable = len(equity_holdings[equity_holdings['pnl'] > 0]['symbol'].unique())
        st.metric(
            "Positions",
            f"{num_stocks} stocks",
            f"{num_profitable} profitable"
        )
    
    st.markdown("---")
    
    # Best and Worst Performers
    col1, col2 = st.columns(2)
    
    with col1:
        best = equity_holdings.loc[equity_holdings['pnl_pct'].idxmax()]
        st.success("🏆 **Best Performer**")
        st.markdown(f"### {best['symbol']}")
        st.markdown(f"**P&L:** ₹{best['pnl']:,.0f} ({best['pnl_pct']:+.2f}%)")
    
    with col2:
        worst = equity_holdings.loc[equity_holdings['pnl_pct'].idxmin()]
        st.error("📉 **Worst Performer**")
        st.markdown(f"### {worst['symbol']}")
        st.markdown(f"**P&L:** ₹{worst['pnl']:,.0f} ({worst['pnl_pct']:+.2f}%)")
    
    st.markdown("---")
    
    # Holdings Table
    st.subheader("📋 Current Holdings")
    
    # Aggregate by symbol
    agg_holdings = equity_holdings.groupby('symbol').agg({
        'quantity': 'sum',
        'invested_value': 'sum',
        'current_value': 'sum',
        'pnl': 'sum'
    }).reset_index()
    
    agg_holdings['pnl_pct'] = (agg_holdings['pnl'] / agg_holdings['invested_value'] * 100)
    
    # Format display dataframe
    display_df = agg_holdings.copy()
    display_df['invested_value'] = display_df['invested_value'].apply(lambda x: f"₹{x:,.0f}")
    display_df['current_value'] = display_df['current_value'].apply(lambda x: f"₹{x:,.0f}")
    display_df['pnl'] = display_df['pnl'].apply(lambda x: f"₹{x:,.0f}")
    display_df['pnl_pct'] = display_df['pnl_pct'].apply(lambda x: f"{x:+.2f}%")
    
    display_df.columns = ['Symbol', 'Quantity', 'Invested', 'Current Value', 'P&L', 'P&L %']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Portfolio allocation pie
        fig = px.pie(
            agg_holdings,
            values='current_value',
            names='symbol',
            title='Portfolio Allocation',
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # P&L bar chart
        fig = go.Figure()
        colors = ['green' if x > 0 else 'red' for x in agg_holdings['pnl']]
        fig.add_trace(go.Bar(
            x=agg_holdings['symbol'],
            y=agg_holdings['pnl'],
            marker_color=colors,
            text=agg_holdings['pnl'].apply(lambda x: f"₹{x:,.0f}"),
            textposition='outside'
        ))
        fig.update_layout(
            title='Profit/Loss by Stock',
            xaxis_title='Stock',
            yaxis_title='P&L (₹)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Last updated
    st.sidebar.markdown("---")
    st.sidebar.info(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ==================== EQUITY ANALYSIS PAGE ====================
elif page == "📈 Equity Analysis":
    st.title("📈 Detailed Equity Analysis")
    
    equity_holdings = load_equity_holdings()
    
    if equity_holdings.empty:
        st.error("No equity data available.")
        st.stop()
    
    # Fetch prices
    with st.spinner("Analyzing portfolio..."):
        symbols = equity_holdings['symbol'].unique().tolist()
        prices = fetch_current_prices(symbols)
        equity_holdings = calculate_equity_metrics(equity_holdings, prices)
        
        # Fetch historical data
        symbols_str = ' '.join(symbols)
        hist_data = yf.download(symbols_str, period="1y", progress=False)['Close']
        
        if isinstance(hist_data, pd.Series):
            hist_data = hist_data.to_frame()
            hist_data.columns = [symbols[0]]
    
    # Risk metrics
    st.subheader("⚠️ Risk Metrics")
    
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
    
    # Interpretation
    if sharpe > 1:
        st.success("✓ Sharpe Ratio > 1: Good risk-adjusted returns")
    elif sharpe > 0:
        st.warning("⚠ Sharpe Ratio > 0: Positive but moderate efficiency")
    else:
        st.error("✗ Sharpe Ratio < 0: Returns below risk-free rate")
    
    st.markdown("---")
    
    # Historical performance
    st.subheader("📊 Historical Performance")
    
    normalized = (hist_data / hist_data.iloc[0]) * 100
    
    fig = go.Figure()
    for col in normalized.columns:
        fig.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized[col],
            name=col,
            mode='lines'
        ))
    
    fig.update_layout(
        title='Normalized Price Performance (Base 100)',
        xaxis_title='Date',
        yaxis_title='Normalized Price',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Individual stock metrics
    st.subheader("📋 Individual Stock Metrics")
    
    stock_metrics = []
    for col in returns.columns:
        ann_return = returns[col].mean() * 252
        vol = returns[col].std() * np.sqrt(252)
        stock_sharpe = (ann_return - 0.068) / vol if vol > 0 else 0
        
        stock_metrics.append({
            'Symbol': col,
            'Annual Return': f"{ann_return*100:.2f}%",
            'Volatility': f"{vol*100:.2f}%",
            'Sharpe Ratio': f"{stock_sharpe:.3f}"
        })
    
    st.dataframe(pd.DataFrame(stock_metrics), use_container_width=True, hide_index=True)

# ==================== OPTIONS ANALYSIS PAGE ====================
elif page == "📉 Options Analysis":
    st.title("📉 Options Portfolio Analysis")
    
    options_df = load_options_positions()
    
    if options_df.empty:
        st.warning("No options positions found. Add sample_options_positions.csv to enable this feature.")
        st.stop()
    
    # Fetch Nifty spot
    spot_price = fetch_nifty_spot()
    
    st.metric("Nifty Spot Price", f"₹{spot_price:,.2f}")
    
    # Calculate Greeks
    with st.spinner("Calculating Greeks..."):
        for i, pos in options_df.iterrows():
            T = max((pos['expiry'] - datetime.now()).days / 365.0, 0.001)
            sigma = 0.20  # Simplified: use 20% IV
            
            greeks = black_scholes_greeks(
                spot_price, pos['strike'], T, 0.068, sigma, pos['option_type']
            )
            
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
    st.subheader("🎯 Portfolio Greeks")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Portfolio Delta", f"{options_df['delta'].sum():.2f}")
    col2.metric("Daily Theta", f"₹{options_df['theta'].sum():.2f}")
    col3.metric("Total Vega", f"₹{options_df['vega'].sum():.2f}")
    col4.metric("Total P&L", f"₹{options_df['pnl'].sum():,.0f}")
    
    # Positions table
    st.subheader("📋 Options Positions")
    
    display_options = options_df.copy()
    display_options['days_to_expiry'] = (display_options['expiry'] - datetime.now()).dt.days
    display_options = display_options[[
        'option_type', 'strike', 'days_to_expiry', 'quantity', 
        'premium_paid', 'current_price', 'pnl', 'delta', 'theta'
    ]]
    
    st.dataframe(display_options, use_container_width=True, hide_index=True)
    
    # Strategy analysis
    if 'strategy' in options_df.columns:
        st.subheader("📊 Strategy-wise P&L")
        
        strategy_pnl = options_df.groupby('strategy')['pnl'].sum().reset_index()
        
        fig = px.bar(
            strategy_pnl,
            x='strategy',
            y='pnl',
            title='P&L by Strategy',
            color='pnl',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== Strategy Backtesting ====================
elif page == "📊 Strategy Backtesting":
    st.title("📊 Strategy Backtesting & Monte Carlo")
    
    # Check if backtesting is available
    if not BACKTEST_AVAILABLE:
        st.error("❌ **Backtesting Module Not Available**")
        st.info("""
        To enable backtesting:
        1. Make sure `backtest_strategies.py` is in the same folder as this dashboard
        2. Restart the Streamlit app
        
        Or upload a trade history CSV and we'll run basic analysis.
        """)
        st.stop()
    
    st.markdown("Upload your historical trades to analyze strategy performance and run Monte Carlo simulations.")

    uploaded_file = st.file_uploader("Upload trade_history.csv", type="csv")

    # User inputs for simulation
    col1, col2, col3 = st.columns(3)
    with col1:
        initial_capital = st.number_input("Initial Capital (₹)", value=100000, step=10000)
    with col2:
        num_trades = st.number_input("Trades to Simulate", value=50, min_value=1, max_value=200)
    with col3:
        num_simulations = st.number_input("Number of Simulations", value=5000, min_value=100, step=500)

    if st.button("🚀 Run Backtest & Monte Carlo", type="primary"):
        if not uploaded_file:
            st.warning("⚠️ Please upload a trade_history.csv file to run the backtest.")
            st.stop()

        try:
            with st.spinner("Running backtest and Monte Carlo simulations..."):
                # Instantiate the backtester
                backtester = StrategyBacktester(uploaded_file)

                # Run backtest
                stats = backtester.backtest_options_trades()
                if stats is None:
                    st.error("❌ Backtest returned no results — check uploaded CSV format and columns.")
                    st.stop()

                # Run Monte Carlo
                mc_results = backtester.monte_carlo_simulation(
                    initial_capital=int(initial_capital),
                    num_simulations=int(num_simulations),
                    num_trades=int(num_trades)
                )

                # Create visualizations
                fig = backtester.create_visualizations(mc_results)

            # Display summary metrics
            st.success("✅ Analysis Complete!")
            st.markdown("### 📊 Backtest Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Trades", stats['total_trades'])
            col2.metric("Win Rate", f"{stats['win_rate']:.1f}%")
            col3.metric("Profit Factor", f"{stats['profit_factor']:.2f}")
            col4.metric("Expectancy", f"₹{stats['expectancy']:.2f}")
            
            # Interpretation
            st.markdown("### 🎯 Strategy Performance")
            if stats['win_rate'] >= 60:
                st.success(f"✅ Excellent win rate of {stats['win_rate']:.1f}%")
            elif stats['win_rate'] >= 50:
                st.warning(f"⚠️ Acceptable win rate of {stats['win_rate']:.1f}% - room for improvement")
            else:
                st.error(f"❌ Low win rate of {stats['win_rate']:.1f}% - strategy needs refinement")
            
            if stats['profit_factor'] > 2:
                st.success(f"✅ Strong profit factor of {stats['profit_factor']:.2f}")
            elif stats['profit_factor'] > 1:
                st.warning(f"⚠️ Moderate profit factor of {stats['profit_factor']:.2f}")
            else:
                st.error(f"❌ Losing strategy - profit factor {stats['profit_factor']:.2f} < 1")

            # Show per-trade results
            st.markdown("### 📋 Individual Trade Results")
            if backtester.results is not None and not backtester.results.empty:
                st.dataframe(backtester.results.reset_index(drop=True), use_container_width=True)
            else:
                st.info("No per-trade results to display.")

            # Monte Carlo results
            st.markdown("### 🎲 Monte Carlo Simulation Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("Probability of Profit", f"{mc_results['prob_profit']:.1f}%")
            col2.metric("Risk of Ruin", f"{mc_results['prob_ruin']:.1f}%")
            col3.metric("Median Final Capital", f"₹{mc_results['median_final']:,.0f}")

            # Render matplotlib figure
            st.markdown("### 📈 Visualization Dashboard")
            st.pyplot(fig)

            # Download button
            try:
                with open("backtest_analysis.png", "rb") as f:
                    st.download_button(
                        "📥 Download Analysis Report (PNG)", 
                        f, 
                        file_name="backtest_analysis.png",
                        mime="image/png"
                    )
            except FileNotFoundError:
                pass

        except Exception as e:
            st.error("❌ An error occurred while running the backtest.")
            st.exception(e)
            st.info("Please check that your CSV has the required columns: entry_date, exit_date, strategy, position_type, quantity, entry_price, exit_price")

# ==================== SETTINGS PAGE ====================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings & Configuration")
    
    st.subheader("📁 Data Files")
    st.info("**For Demo Mode:** This app uses sample data files")
    st.code("holdings.csv - Sample equity positions")
    st.code("options_positions.csv - Sample options positions")
    st.code("trade_history.csv - Sample trade history")
    
    st.markdown("---")
    st.subheader("📤 Upload Your Own Data")
    st.markdown("To use your real portfolio data:")
    st.markdown("1. Prepare CSV files with the same column structure as samples")
    st.markdown("2. Replace 'sample_' prefix in code with your actual filenames")
    st.markdown("3. Restart the app")
    
    st.markdown("---")
    st.subheader("🔄 Cache Settings")
    if st.button("Clear All Cache"):
        st.cache_data.clear()
        st.success("✅ Cache cleared! Data will refresh on next page load.")
    
    st.markdown("---")
    st.subheader("📊 About")
    st.markdown("""
    **Portfolio Analytics Dashboard v2.0**
    
    Built with:
    - Python 3.9+
    - Streamlit 1.28+
    - yfinance (real-time market data)
    - Plotly (interactive charts)
    - SciPy (options pricing & Monte Carlo)
    
    Features:
    - ✅ Real-time equity tracking with live NSE/BSE prices
    - ✅ Options Greeks calculation (Black-Scholes model)
    - ✅ Risk metrics analysis (Sharpe, VaR, Max Drawdown)
    - ✅ Strategy backtesting with historical trades
    - ✅ Monte Carlo simulations (10,000+ scenarios)
    - ✅ Interactive visualizations with Plotly
    
    ---
    
    **Created by:** Pratyush Singh  
    **GitHub:** [github.com/GoDkiLLeR-04/Trivya-portfolio-tracker](https://github.com/GoDkiLLeR-04/Trivya-portfolio-tracker)  
    **License:** MIT  
    """)
    
    if BACKTEST_AVAILABLE:
        st.success("✅ Backtesting module loaded successfully")
    else:
        st.warning("⚠️ Backtesting module not available")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Built with ❤️ using Streamlit**")
st.sidebar.markdown("v2.0 | [GitHub](https://github.com/GoDkiLLeR-04/Trivya-portfolio-tracker)")
