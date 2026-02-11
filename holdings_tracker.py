"""
Portfolio Analytics System - Week 1 Complete (FIXED)
Tracks portfolio performance, calculates risk metrics, and generates visualizations
Handles duplicate stock entries correctly
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from scipy import stats

class PortfolioTracker:
    def __init__(self, csv_file):
        """Initialize portfolio tracker with holdings CSV file"""
        # Load original data (keep for transaction history)
        self.transactions = pd.read_csv(csv_file)
        self.transactions['date'] = pd.to_datetime(self.transactions['date'])
    
    # Create aggregated holdings for calculations
        self.holdings = self._aggregate_positions()
    
        self.portfolio_data = None
        self.historical_data = None
    
        print(f"✓ Loaded {len(self.holdings)} unique positions from {len(self.transactions)} transactions")

    def _aggregate_positions(self):
        """
        Aggregate multiple purchases into single position per stock
        Uses weighted average for buy price
        """
        df = self.transactions if hasattr(self, 'transactions') else self.holdings.copy()
    
    # Check if aggregation is needed
        if df['symbol'].duplicated().any():
            aggregated = df.groupby('symbol').apply(
            lambda x: pd.Series({
                'quantity': x['quantity'].sum(),
                'buy_price': np.average(x['buy_price'], weights=x['quantity']),
                'date': x['date'].min(),
                'num_transactions': len(x)
            })
            ).reset_index()
            return aggregated
        else:
        # No duplicates, return as-is
            return df

    def show_transaction_history(self):
        """Display individual transactions for duplicate positions"""
    
    # Check if we have the original transaction data
        if not hasattr(self, 'transactions'):
         self.transactions = self.holdings.copy()
    
    # Find symbols with multiple purchases
        duplicates = self.transactions['symbol'].value_counts()
        duplicates = duplicates[duplicates > 1]
    
        if len(duplicates) == 0:
         return  # No duplicates, skip this section
    
        print(f"\n📊 Multiple purchases detected: {', '.join(duplicates.index.tolist())}")
        print("\n" + "="*60)
        print("TRANSACTION HISTORY")
        print("="*60)
    
        for symbol in duplicates.index:
         trades = self.transactions[self.transactions['symbol'] == symbol]
        
         print(f"\n{symbol} - {len(trades)} transactions:")
         for _, trade in trades.iterrows():
            print(f"  ├─ {trade['date'].strftime('%Y-%m-%d')} | "
                  f"{int(trade['quantity'])} shares @ ₹{trade['buy_price']:,.2f}")
        
        # Calculate and show aggregated result
            total_qty = trades['quantity'].sum()
            weighted_avg = np.average(trades['buy_price'], weights=trades['quantity'])
            print(f"  └─ TOTAL: {int(total_qty)} shares @ ₹{weighted_avg:,.2f} avg")
     
    def fetch_current_prices(self):
        """Fetch current prices and calculate P&L"""
        print("\n" + "="*60)
        print("FETCHING CURRENT PRICES...")
        print("="*60)
        
        for i, row in self.holdings.iterrows():
            try:
                ticker = yf.Ticker(row['symbol'])
                info = ticker.info
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                
                self.holdings.at[i, 'current_price'] = current_price
                self.holdings.at[i, 'invested_value'] = row['quantity'] * row['buy_price']
                self.holdings.at[i, 'current_value'] = row['quantity'] * current_price
                self.holdings.at[i, 'pnl'] = (current_price - row['buy_price']) * row['quantity']
                self.holdings.at[i, 'pnl_pct'] = ((current_price - row['buy_price']) / row['buy_price']) * 100
                
                print(f"✓ {row['symbol']}: ₹{current_price:,.2f}")
            except Exception as e:
                print(f"✗ Error fetching {row['symbol']}: {str(e)}")
                self.holdings.at[i, 'current_price'] = 0
        
        return self.holdings
    
    def display_portfolio_summary(self):
        """Display portfolio overview"""
        print("\n" + "="*60)
        print("PORTFOLIO SUMMARY")
        print("="*60)
        
        total_invested = self.holdings['invested_value'].sum()
        total_current = self.holdings['current_value'].sum()
        total_pnl = self.holdings['pnl'].sum()
        total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
        
        print(f"\nTotal Invested:    ₹{total_invested:,.2f}")
        print(f"Current Value:     ₹{total_current:,.2f}")
        print(f"Total P&L:         ₹{total_pnl:,.2f} ({total_pnl_pct:+.2f}%)")
        
        print("\n" + "-"*60)
        print(f"{'Symbol':<15} {'Qty':<8} {'Buy':<10} {'Current':<10} {'P&L':<12} {'P&L%':<10}")
        print("-"*60)
        
        for _, row in self.holdings.iterrows():
            print(f"{row['symbol']:<15} {int(row['quantity']):<8} "
                  f"₹{row['buy_price']:<9,.0f} ₹{row['current_price']:<9,.0f} "
                  f"₹{row['pnl']:<11,.0f} {row['pnl_pct']:+.2f}%")
        
        print("-"*60)
        
        # Best and worst performers
        best = self.holdings.loc[self.holdings['pnl_pct'].idxmax()]
        worst = self.holdings.loc[self.holdings['pnl_pct'].idxmin()]
        
        print(f"\n🏆 Best Performer:  {best['symbol']} ({best['pnl_pct']:+.2f}%)")
        print(f"📉 Worst Performer: {worst['symbol']} ({worst['pnl_pct']:+.2f}%)")
    
    def fetch_historical_data(self, period="1y"):
        """Fetch historical data for all UNIQUE stocks"""
        print("\n" + "="*60)
        print("FETCHING HISTORICAL DATA...")
        print("="*60)
        
        # Get unique symbols only
        unique_symbols = self.holdings['symbol'].unique().tolist()
        symbols = ' '.join(unique_symbols)
        
        self.historical_data = yf.download(symbols, period=period, progress=False)['Close']
        
        # Handle single stock case
        if isinstance(self.historical_data, pd.Series):
            self.historical_data = self.historical_data.to_frame()
            self.historical_data.columns = [unique_symbols[0]]
        
        print(f"✓ Downloaded {len(self.historical_data)} days of data for {len(unique_symbols)} unique stocks")
        return self.historical_data
    
    def calculate_risk_metrics(self):
        """Calculate comprehensive risk metrics"""
        print("\n" + "="*60)
        print("RISK METRICS ANALYSIS")
        print("="*60)
        
        if self.historical_data is None:
            self.fetch_historical_data()
        
        # Calculate daily returns
        returns = self.historical_data.pct_change().dropna()
        
        # Portfolio weights based on current allocation
        # Group by symbol to handle duplicates
        symbol_allocation = self.holdings.groupby('symbol')['current_value'].sum()
        total_value = symbol_allocation.sum()
        weights = symbol_allocation / total_value
        
        # Ensure weights align with returns columns
        weights = weights.reindex(returns.columns, fill_value=0)
        
        # Portfolio returns
        portfolio_returns = (returns * weights.values).sum(axis=1)
        
        # Risk-free rate (India 10Y G-Sec ≈ 6.8%)
        risk_free_rate = 0.068
        
        # 1. Sharpe Ratio
        excess_returns = portfolio_returns.mean() * 252 - risk_free_rate
        portfolio_vol = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = excess_returns / portfolio_vol if portfolio_vol > 0 else 0
        
        # 2. Maximum Drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 3. Value at Risk (95% confidence)
        var_95 = np.percentile(portfolio_returns, 5)
        
        # 4. Beta (vs Nifty 50)
        try:
            nifty = yf.download("^NSEI", period="1y", progress=False)['Close']
            nifty_returns = nifty.pct_change().dropna()
            
            # Align dates
            common_dates = portfolio_returns.index.intersection(nifty_returns.index)
            portfolio_aligned = portfolio_returns.loc[common_dates]
            nifty_aligned = nifty_returns.loc[common_dates]
            
            covariance = np.cov(portfolio_aligned, nifty_aligned)[0][1]
            nifty_variance = np.var(nifty_aligned)
            beta = covariance / nifty_variance if nifty_variance > 0 else 0
        except:
            beta = 0
            print("⚠ Could not calculate Beta (Nifty data unavailable)")
        
        # 5. Volatility
        annual_volatility = portfolio_vol
        
        # Display metrics
        print(f"\nSharpe Ratio:        {sharpe_ratio:.3f}")
        print(f"Maximum Drawdown:    {max_drawdown*100:.2f}%")
        print(f"Value at Risk (95%): {var_95*100:.2f}% (daily)")
        print(f"Annual Volatility:   {annual_volatility*100:.2f}%")
        if beta != 0:
            print(f"Beta (vs Nifty):     {beta:.3f}")
        
        # Interpretation
        print("\n" + "-"*60)
        print("INTERPRETATION:")
        print("-"*60)
        
        if sharpe_ratio > 1:
            print("✓ Sharpe Ratio > 1: Good risk-adjusted returns")
        elif sharpe_ratio > 0:
            print("⚠ Sharpe Ratio > 0: Positive returns but moderate efficiency")
        else:
            print("✗ Sharpe Ratio < 0: Returns below risk-free rate")
        
        if abs(max_drawdown) < 0.10:
            print("✓ Max Drawdown < 10%: Low historical losses")
        elif abs(max_drawdown) < 0.20:
            print("⚠ Max Drawdown < 20%: Moderate risk exposure")
        else:
            print("✗ Max Drawdown > 20%: High risk exposure")
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'volatility': annual_volatility,
            'beta': beta
        }
    
    def calculate_stock_metrics(self):
        """Calculate individual stock metrics"""
        print("\n" + "="*60)
        print("INDIVIDUAL STOCK METRICS")
        print("="*60)
        
        if self.historical_data is None:
            self.fetch_historical_data()
        
        returns = self.historical_data.pct_change().dropna()
        
        print(f"\n{'Symbol':<15} {'Ann. Return':<12} {'Volatility':<12} {'Sharpe':<10}")
        print("-"*60)
        
        for col in returns.columns:
            ann_return = returns[col].mean() * 252
            volatility = returns[col].std() * np.sqrt(252)
            sharpe = (ann_return - 0.068) / volatility if volatility > 0 else 0
            
            print(f"{col:<15} {ann_return*100:>10.2f}% {volatility*100:>10.2f}% {sharpe:>10.3f}")
    
    def create_visualizations(self):
        """Generate portfolio visualizations"""
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS...")
        print("="*60)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Portfolio Analytics Dashboard', fontsize=16, fontweight='bold')
        
        # Aggregate holdings by symbol for visualization
        agg_holdings = self.holdings.groupby('symbol').agg({
            'current_value': 'sum',
            'pnl': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        # 1. Portfolio Allocation Pie Chart
        ax1 = axes[0, 0]
        colors = plt.cm.Set3(range(len(agg_holdings)))
        ax1.pie(agg_holdings['current_value'], 
                labels=agg_holdings['symbol'],
                autopct='%1.1f%%',
                colors=colors,
                startangle=90)
        ax1.set_title('Portfolio Allocation by Value')
        
        # 2. P&L Bar Chart
        ax2 = axes[0, 1]
        colors_pnl = ['green' if x > 0 else 'red' for x in agg_holdings['pnl']]
        ax2.bar(range(len(agg_holdings)), agg_holdings['pnl'], color=colors_pnl)
        ax2.set_xticks(range(len(agg_holdings)))
        ax2.set_xticklabels(agg_holdings['symbol'], rotation=45, ha='right')
        ax2.set_title('Profit/Loss by Stock')
        ax2.set_ylabel('P&L (₹)')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Historical Performance
        if self.historical_data is not None:
            ax3 = axes[1, 0]
            
            # Normalize prices to 100 for comparison
            normalized = (self.historical_data / self.historical_data.iloc[0]) * 100
            
            for col in normalized.columns:
                ax3.plot(normalized.index, normalized[col], label=col, linewidth=2)
            
            ax3.set_title('Historical Performance (Normalized to 100)')
            ax3.set_xlabel('Date')
            ax3.set_ylabel('Normalized Price')
            ax3.legend(loc='best', fontsize=8)
            ax3.grid(alpha=0.3)
        
        # 4. Returns Distribution
        ax4 = axes[1, 1]
        if self.historical_data is not None:
            returns = self.historical_data.pct_change().dropna()
            
            # Calculate portfolio returns with correct weights
            symbol_allocation = self.holdings.groupby('symbol')['current_value'].sum()
            weights = symbol_allocation / symbol_allocation.sum()
            weights = weights.reindex(returns.columns, fill_value=0)
            
            portfolio_returns = (returns * weights.values).sum(axis=1)
            
            ax4.hist(portfolio_returns * 100, bins=50, edgecolor='black', alpha=0.7)
            ax4.axvline(portfolio_returns.mean() * 100, color='red', 
                       linestyle='--', linewidth=2, label='Mean')
            ax4.set_title('Portfolio Daily Returns Distribution')
            ax4.set_xlabel('Daily Return (%)')
            ax4.set_ylabel('Frequency')
            ax4.legend()
            ax4.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('portfolio_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: portfolio_analysis.png")
        
        return fig

    def monte_carlo_portfolio_projection(self, months=12, num_simulations=10000):
        """
        Monte Carlo simulation for EQUITY PORTFOLIO future value projection
        Different from options trading MC - this simulates holding your current stocks
        """
        print("\n" + "="*70)
        print("MONTE CARLO PORTFOLIO PROJECTION")
        print("="*70)
        
        if self.historical_data is None:
            self.fetch_historical_data()
        
        # Calculate returns and volatility for each stock
        returns = self.historical_data.pct_change().dropna()
        
        # Current portfolio state
        current_values = self.holdings.groupby('symbol')['current_value'].sum()
        total_value = current_values.sum()
        weights = current_values / total_value
        
        # Align weights with returns columns
        weights = weights.reindex(returns.columns, fill_value=0)
        
        # Historical statistics
        mean_returns = returns.mean() * 252  # Annualized
        cov_matrix = returns.cov() * 252     # Annualized
        
        print(f"\nSimulation Parameters:")
        print(f"Current Portfolio Value:  ₹{total_value:,.0f}")
        print(f"Time Horizon:             {months} months")
        print(f"Number of Simulations:    {num_simulations:,}")
        print(f"Number of Stocks:         {len(current_values)}")
        
        # Run simulations
        days = int(months * 21)  # Trading days per month approx 21
        
        portfolio_values = np.zeros((days, num_simulations))
        portfolio_values[0, :] = total_value
        
        for sim in range(num_simulations):
            for day in range(1, days):
                # Generate correlated random returns
                random_returns = np.random.multivariate_normal(
                    mean_returns / 252,  # Daily returns
                    cov_matrix / 252,    # Daily covariance
                    1
                )[0]
                
                # Calculate portfolio return
                portfolio_return = np.dot(weights.values, random_returns)
                
                # Update portfolio value
                portfolio_values[day, sim] = portfolio_values[day-1, sim] * (1 + portfolio_return)
        
        # Final values after specified months
        final_values = portfolio_values[-1, :]
        
        # Calculate statistics
        median_final = np.median(final_values)
        mean_final = np.mean(final_values)
        
        percentile_5 = np.percentile(final_values, 5)
        percentile_25 = np.percentile(final_values, 25)
        percentile_75 = np.percentile(final_values, 75)
        percentile_95 = np.percentile(final_values, 95)
        
        prob_profit = (final_values > total_value).sum() / num_simulations * 100
        prob_loss_20 = (final_values < total_value * 0.8).sum() / num_simulations * 100
        
        expected_return = (median_final - total_value) / total_value * 100
        
        # Display results
        print("\n" + "-"*70)
        print("PROJECTION RESULTS:")
        print("-"*70)
        
        print(f"\nFinal Portfolio Value (after {months} months):")
        print(f"Current Value:       ₹{total_value:,.0f}")
        print(f"Median (50%):        ₹{median_final:,.0f} ({(median_final/total_value-1)*100:+.2f}%)")
        print(f"Mean:                ₹{mean_final:,.0f} ({(mean_final/total_value-1)*100:+.2f}%)")
        
        print(f"\nConfidence Intervals:")
        print(f"5th Percentile:      ₹{percentile_5:,.0f} ({(percentile_5/total_value-1)*100:+.2f}%)")
        print(f"25th Percentile:     ₹{percentile_25:,.0f} ({(percentile_25/total_value-1)*100:+.2f}%)")
        print(f"75th Percentile:     ₹{percentile_75:,.0f} ({(percentile_75/total_value-1)*100:+.2f}%)")
        print(f"95th Percentile:     ₹{percentile_95:,.0f} ({(percentile_95/total_value-1)*100:+.2f}%)")
        
        print(f"\nProbabilities:")
        print(f"Chance of Profit:    {prob_profit:.1f}%")
        print(f"Chance of >20% Loss: {prob_loss_20:.1f}%")
        
        # Interpretation
        print("\n" + "-"*70)
        print("INTERPRETATION:")
        print("-"*70)
        
        print(f"After {months} months, there's a:")
        print(f"  • {prob_profit:.0f}% chance your portfolio will be profitable")
        print(f"  • 50% chance it will be worth at least ₹{median_final:,.0f}")
        print(f"  • 90% chance it will be between ₹{percentile_5:,.0f} and ₹{percentile_95:,.0f}")
        
        if expected_return > 10:
            print(f"\n✓ Expected return of {expected_return:.1f}% - Strong growth potential")
        elif expected_return > 0:
            print(f"\n⚠ Expected return of {expected_return:.1f}% - Moderate growth")
        else:
            print(f"\n✗ Expected return of {expected_return:.1f}% - Consider rebalancing")
        
        # Create visualization
        self._plot_mc_projection(portfolio_values, total_value, months)
        
        return {
            'final_values': final_values,
            'median_final': median_final,
            'prob_profit': prob_profit,
            'portfolio_values': portfolio_values
        }
    
    def _plot_mc_projection(self, portfolio_values, initial_value, months):
        """Plot Monte Carlo projection results"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # 1. Simulation paths
        ax1 = axes[0]
        days = portfolio_values.shape[0]
        time_axis = np.linspace(0, months, days)
        
        # Plot sample paths (first 100)
        for i in range(min(100, portfolio_values.shape[1])):
            ax1.plot(time_axis, portfolio_values[:, i], alpha=0.1, color='blue')
        
        # Plot percentiles
        percentile_5 = np.percentile(portfolio_values, 5, axis=1)
        percentile_50 = np.percentile(portfolio_values, 50, axis=1)
        percentile_95 = np.percentile(portfolio_values, 95, axis=1)
        
        ax1.plot(time_axis, percentile_50, 'r-', linewidth=2, label='Median (50%)')
        ax1.plot(time_axis, percentile_5, 'g--', linewidth=2, label='5th Percentile')
        ax1.plot(time_axis, percentile_95, 'g--', linewidth=2, label='95th Percentile')
        ax1.axhline(y=initial_value, color='orange', linestyle='--', 
                    linewidth=2, label='Current Value')
        
        ax1.set_title(f'Portfolio Value Projection ({months} months)')
        ax1.set_xlabel('Months')
        ax1.set_ylabel('Portfolio Value (₹)')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # 2. Final value distribution
        ax2 = axes[1]
        final_values = portfolio_values[-1, :]
        ax2.hist(final_values, bins=50, edgecolor='black', alpha=0.7)
        ax2.axvline(x=np.median(final_values), color='red', linestyle='--',
                    linewidth=2, label=f'Median: ₹{np.median(final_values):,.0f}')
        ax2.axvline(x=initial_value, color='orange', linestyle='--',
                    linewidth=2, label='Current Value')
        ax2.set_title('Final Portfolio Value Distribution')
        ax2.set_xlabel('Portfolio Value (₹)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('monte_carlo_projection.png', dpi=300, bbox_inches='tight')
        print("\n✓ Saved: monte_carlo_projection.png")
        
        return fig


    def generate_report(self):
        """Generate complete portfolio report"""
        print("\n" + "="*80)
        print(" "*20 + "PORTFOLIO ANALYSIS REPORT")
        print(" "*25 + f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80)
    
        # Fetch data
        self.fetch_current_prices()
        self.display_portfolio_summary()
        self.fetch_historical_data()
        self.calculate_risk_metrics()
        self.calculate_stock_metrics()
        
        # Monte Carlo Projection
        self.monte_carlo_portfolio_projection(months=12, num_simulations=10000)
        
        self.create_visualizations()
        
        print("\n" + "="*80)
        print("✓ ANALYSIS COMPLETE")
        print("="*80)
        print("\nGenerated Files:")
        print("  - portfolio_analysis.png (4 charts dashboard)")
        print("  - monte_carlo_projection.png (2 charts projection)")  # NEW
        print("\nNext Steps:")
        print("  1. Review the risk metrics and adjust portfolio if needed")
        print("  2. Check portfolio_analysis.png for visual insights")
        print("  3. Review monte_carlo_projection.png for future projections")  # NEW
        print("  4. Use this data for your LinkedIn post/GitHub README")
        print("="*80 + "\n")



# Main execution
if __name__ == "__main__":
    print("\n" + "="*80)
    print(" "*25 + "PORTFOLIO TRACKER v1.0")
    print(" "*20 + "yfinance + Python Analytics System")
    print("="*80)
    
    # Initialize tracker
    tracker = PortfolioTracker('holdings.csv')
    
    # Generate complete report
    tracker.generate_report()
    
    # Optional: Show plots
    plt.show()
