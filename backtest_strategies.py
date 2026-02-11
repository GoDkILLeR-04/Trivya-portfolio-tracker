"""
Strategy Backtesting & Monte Carlo Simulation System
Validates trading strategies and projects portfolio outcomes
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

class StrategyBacktester:
    def __init__(self, trades_csv=None):
        """
        Initialize backtester
        trades_csv: CSV file with historical trades (optional)
        """
        if trades_csv:
            self.trades = pd.read_csv(trades_csv)
            self.trades['entry_date'] = pd.to_datetime(self.trades['entry_date'])
            self.trades['exit_date'] = pd.to_datetime(self.trades['exit_date'])
        else:
            self.trades = None
        
        self.results = None
        
    def backtest_options_trades(self):
        """Backtest historical options trades"""
        if self.trades is None or len(self.trades) == 0:
            print("⚠ No trade data available for backtesting")
            return None
        
        print("\n" + "="*70)
        print("BACKTESTING HISTORICAL OPTIONS TRADES")
        print("="*70)
        
        results = []
        
        for i, trade in self.trades.iterrows():
            # Calculate holding period
            holding_days = (trade['exit_date'] - trade['entry_date']).days
            
            # Calculate P&L
            if trade['position_type'] == 'long':
                pnl = (trade['exit_price'] - trade['entry_price']) * trade['quantity']
            else:  # short
                pnl = (trade['entry_price'] - trade['exit_price']) * trade['quantity']
            
            # Calculate return percentage
            capital_deployed = trade['entry_price'] * abs(trade['quantity'])
            return_pct = (pnl / capital_deployed) * 100 if capital_deployed > 0 else 0
            
            results.append({
                'trade_id': i + 1,
                'entry_date': trade['entry_date'],
                'exit_date': trade['exit_date'],
                'strategy': trade['strategy'],
                'holding_days': holding_days,
                'pnl': pnl,
                'return_pct': return_pct,
                'win': 1 if pnl > 0 else 0
            })
        
        self.results = pd.DataFrame(results)
        
        # Calculate statistics
        total_trades = len(self.results)
        winning_trades = self.results['win'].sum()
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) * 100
        
        avg_win = self.results[self.results['win'] == 1]['pnl'].mean()
        avg_loss = self.results[self.results['win'] == 0]['pnl'].mean()
        
        total_pnl = self.results['pnl'].sum()
        avg_return = self.results['return_pct'].mean()
        
        # Profit factor
        gross_profit = self.results[self.results['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(self.results[self.results['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Expectancy
        expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)
        
        # Display results
        print(f"\nTotal Trades:        {total_trades}")
        print(f"Winning Trades:      {winning_trades} ({win_rate:.1f}%)")
        print(f"Losing Trades:       {losing_trades} ({100-win_rate:.1f}%)")
        print(f"\nAverage Win:         ₹{avg_win:,.2f}")
        print(f"Average Loss:        ₹{avg_loss:,.2f}")
        print(f"Win/Loss Ratio:      {abs(avg_win/avg_loss):.2f}x" if avg_loss != 0 else "N/A")
        print(f"\nTotal P&L:           ₹{total_pnl:,.2f}")
        print(f"Average Return:      {avg_return:.2f}%")
        print(f"Profit Factor:       {profit_factor:.2f}")
        print(f"Expectancy:          ₹{expectancy:.2f} per trade")
        
        # Interpretation
        print("\n" + "-"*70)
        print("INTERPRETATION:")
        print("-"*70)
        
        if win_rate >= 60:
            print("✓ Win Rate > 60%: Excellent strategy performance")
        elif win_rate >= 50:
            print("⚠ Win Rate > 50%: Acceptable, but room for improvement")
        else:
            print("✗ Win Rate < 50%: Strategy needs refinement")
        
        if profit_factor > 2:
            print("✓ Profit Factor > 2: Strong risk/reward profile")
        elif profit_factor > 1:
            print("⚠ Profit Factor > 1: Profitable but moderate efficiency")
        else:
            print("✗ Profit Factor < 1: Strategy losing money")
        
        if expectancy > 0:
            print(f"✓ Positive Expectancy: Expected to earn ₹{expectancy:.2f} per trade")
        else:
            print(f"✗ Negative Expectancy: Expected to lose ₹{abs(expectancy):.2f} per trade")
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'total_pnl': total_pnl
        }
    
    def strategy_breakdown(self):
        """Break down performance by strategy type"""
        if self.results is None:
            return
        
        print("\n" + "="*70)
        print("STRATEGY-WISE BREAKDOWN")
        print("="*70)
        
        strategy_stats = self.results.groupby('strategy').agg({
            'pnl': ['sum', 'mean', 'count'],
            'win': 'sum',
            'return_pct': 'mean'
        }).round(2)
        
        print(f"\n{'Strategy':<20} {'Trades':<8} {'Win%':<10} {'Total P&L':<15} {'Avg Return':<12}")
        print("-"*70)
        
        for strategy in strategy_stats.index:
            trades = strategy_stats.loc[strategy, ('pnl', 'count')]
            wins = strategy_stats.loc[strategy, ('win', 'sum')]
            win_pct = (wins / trades) * 100
            total_pnl = strategy_stats.loc[strategy, ('pnl', 'sum')]
            avg_return = strategy_stats.loc[strategy, ('return_pct', 'mean')]
            
            print(f"{strategy:<20} {int(trades):<8} {win_pct:<9.1f}% ₹{total_pnl:<13,.0f} {avg_return:>10.2f}%")
    
    def monte_carlo_simulation(self, initial_capital=100000, num_simulations=10000, num_trades=50):
        """
        Monte Carlo simulation for portfolio outcomes
        Based on historical trade statistics
        """
        print("\n" + "="*70)
        print("MONTE CARLO PORTFOLIO SIMULATION")
        print("="*70)
        
        if self.results is None or len(self.results) == 0:
            print("⚠ No backtest results. Creating sample simulation...")
            # Use sample statistics if no real data
            win_rate = 0.55
            avg_win = 5000
            avg_loss = -3000
            std_win = 2000
            std_loss = 1500
        else:
            # Use actual backtest statistics
            win_rate = self.results['win'].mean()
            avg_win = self.results[self.results['pnl'] > 0]['pnl'].mean()
            avg_loss = self.results[self.results['pnl'] < 0]['pnl'].mean()
            std_win = self.results[self.results['pnl'] > 0]['pnl'].std()
            std_loss = self.results[self.results['pnl'] < 0]['pnl'].std()
        
        print(f"\nSimulation Parameters:")
        print(f"Initial Capital:     ₹{initial_capital:,.0f}")
        print(f"Number of Trades:    {num_trades}")
        print(f"Simulations:         {num_simulations:,}")
        print(f"Win Rate:            {win_rate*100:.1f}%")
        print(f"Avg Win:             ₹{avg_win:,.0f}")
        print(f"Avg Loss:            ₹{avg_loss:,.0f}")
        
        # Run simulations
        final_capitals = []
        max_drawdowns = []
        
        for _ in range(num_simulations):
            capital = initial_capital
            peak_capital = initial_capital
            max_dd = 0
            
            for trade_num in range(num_trades):
                # Determine if trade wins or loses
                if np.random.random() < win_rate:
                    # Winning trade
                    pnl = np.random.normal(avg_win, std_win)
                else:
                    # Losing trade
                    pnl = np.random.normal(avg_loss, std_loss)
                
                capital += pnl
                
                # Track drawdown
                if capital > peak_capital:
                    peak_capital = capital
                
                current_dd = (peak_capital - capital) / peak_capital
                max_dd = max(max_dd, current_dd)
                
                # Risk of ruin - stop if capital drops too low
                if capital < initial_capital * 0.2:  # 80% drawdown = ruin
                    break
            
            final_capitals.append(capital)
            max_drawdowns.append(max_dd)
        
        final_capitals = np.array(final_capitals)
        max_drawdowns = np.array(max_drawdowns)
        
        # Calculate statistics
        median_final = np.median(final_capitals)
        mean_final = np.mean(final_capitals)
        
        percentile_5 = np.percentile(final_capitals, 5)
        percentile_25 = np.percentile(final_capitals, 25)
        percentile_75 = np.percentile(final_capitals, 75)
        percentile_95 = np.percentile(final_capitals, 95)
        
        prob_profit = (final_capitals > initial_capital).sum() / num_simulations * 100
        prob_double = (final_capitals > initial_capital * 2).sum() / num_simulations * 100
        prob_ruin = (final_capitals < initial_capital * 0.2).sum() / num_simulations * 100
        
        avg_max_dd = np.mean(max_drawdowns) * 100
        
        # Display results
        print("\n" + "-"*70)
        print("SIMULATION RESULTS:")
        print("-"*70)
        
        print(f"\nFinal Capital Statistics:")
        print(f"Median:              ₹{median_final:,.0f}")
        print(f"Mean:                ₹{mean_final:,.0f}")
        print(f"5th Percentile:      ₹{percentile_5:,.0f}")
        print(f"95th Percentile:     ₹{percentile_95:,.0f}")
        
        print(f"\nProbabilities:")
        print(f"Profit (>0%):        {prob_profit:.1f}%")
        print(f"Double (>100%):      {prob_double:.1f}%")
        print(f"Ruin (<-80%):        {prob_ruin:.1f}%")
        
        print(f"\nRisk Metrics:")
        print(f"Avg Max Drawdown:    {avg_max_dd:.2f}%")
        
        # Interpretation
        print("\n" + "-"*70)
        print("INTERPRETATION:")
        print("-"*70)
        
        if prob_profit > 70:
            print("✓ >70% chance of profit: Strong strategy edge")
        elif prob_profit > 50:
            print("⚠ 50-70% chance of profit: Moderate edge")
        else:
            print("✗ <50% chance of profit: Weak strategy")
        
        if prob_ruin < 5:
            print("✓ <5% risk of ruin: Good capital preservation")
        elif prob_ruin < 10:
            print("⚠ 5-10% risk of ruin: Moderate risk")
        else:
            print("✗ >10% risk of ruin: High risk - consider reducing position sizes")
        
        return {
            'final_capitals': final_capitals,
            'max_drawdowns': max_drawdowns,
            'prob_profit': prob_profit,
            'prob_ruin': prob_ruin,
            'median_final': median_final
        }
    
class StrategyBacktester:

    def __init__(self, trades_csv=None):
        self.results = None

        if trades_csv is not None:
            self.load_trades(trades_csv)

    # ---------------------------------
    # LOAD TRADES
    # ---------------------------------
    def load_trades(self, trades_csv):

        df = pd.read_csv(trades_csv)

        df.columns = df.columns.str.strip().str.lower()

        # Auto detect pnl column
        if "pnl" not in df.columns:
            if "profit" in df.columns:
                df["pnl"] = df["profit"]
            elif "p&l" in df.columns:
                df["pnl"] = df["p&l"]
            elif "net_pnl" in df.columns:
                df["pnl"] = df["net_pnl"]
            else:
                raise ValueError(
                    f"No PnL column found. Columns available: {df.columns.tolist()}"
                )

        if "strategy" not in df.columns:
            df["strategy"] = "Strategy_1"

        df["win"] = df["pnl"] > 0

        self.results = df

    # ---------------------------------
    # BACKTEST
    # ---------------------------------
    def run_backtest(self):
        return self.results

    # ---------------------------------
    # MONTE CARLO
    # ---------------------------------
    def run_monte_carlo(self, simulations=1000, initial_capital=100000):

        if self.results is None:
            return None

        returns = self.results["pnl"].values
        final_capitals = []
        max_drawdowns = []

        for _ in range(simulations):
            sampled = np.random.choice(returns, size=len(returns), replace=True)

            equity = initial_capital + np.cumsum(sampled)
            final_capitals.append(equity[-1])

            peak = np.maximum.accumulate(equity)
            dd = (equity - peak) / peak
            max_drawdowns.append(dd.min())

        return {
            "final_capitals": final_capitals,
            "median_final": np.median(final_capitals),
            "max_drawdowns": max_drawdowns,
        }

    # ---------------------------------
    # VISUALIZATION
    # ---------------------------------
    def create_visualizations(self, mc_results=None):

        if self.results is None:
            return None

        fig = plt.figure(figsize=(18, 12))

        ax1 = plt.subplot(2, 3, 1)
        ax2 = plt.subplot(2, 3, 2)
        ax3 = plt.subplot(2, 3, 3)
        ax4 = plt.subplot(2, 3, 4)
        ax5 = plt.subplot(2, 3, 5)
        ax6 = plt.subplot(2, 3, 6)

        cumulative = self.results["pnl"].cumsum()
        ax1.plot(cumulative)
        ax1.set_title("Cumulative PnL")

        wins = self.results[self.results["pnl"] > 0]["pnl"]
        losses = self.results[self.results["pnl"] < 0]["pnl"]
        ax2.hist([wins, losses], bins=20)
        ax2.set_title("Win / Loss Distribution")

        strat = self.results.groupby("strategy")["pnl"].sum()
        ax3.bar(strat.index, strat.values)
        ax3.set_title("PnL by Strategy")
        ax3.tick_params(axis="x", rotation=45)

        rolling = self.results["win"].rolling(10, min_periods=1).mean() * 100
        ax4.plot(rolling)
        ax4.set_title("Rolling Win Rate")

        if mc_results is not None:
            ax5.hist(mc_results["final_capitals"], bins=40)
            ax5.axvline(mc_results["median_final"], linestyle="--")
            ax5.set_title("Monte Carlo Final Capital")

            ax6.hist(np.array(mc_results["max_drawdowns"]) * 100, bins=40)
            ax6.set_title("Max Drawdown %")
        else:
            ax5.text(0.5, 0.5, "Run Monte Carlo", ha="center", va="center")
            ax6.text(0.5, 0.5, "Run Monte Carlo", ha="center", va="center")

        plt.tight_layout()
        return fig
    
    def generate_report(self, initial_capital=100000):
        """Generate complete backtesting report"""
        print("\n" + "="*80)
        print(" "*25 + "STRATEGY BACKTESTING REPORT")
        print(" "*30 + f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80)
        
        # Run backtest
        stats = self.backtest_options_trades()
        
        if stats:
            # Strategy breakdown
            self.strategy_breakdown()
            
            # Monte Carlo simulation
            mc_results = self.monte_carlo_simulation(
                initial_capital=initial_capital,
                num_simulations=10000,
                num_trades=50
            )
            
            # Generate visualizations
            self.create_visualizations(mc_results)
        
        print("\n" + "="*80)
        print("✓ BACKTESTING COMPLETE")
        print("="*80)
        print("\nGenerated Files:")
        print("  - backtest_analysis.png (6-panel report)")
        print("\nKey Takeaways:")
        if stats:
            print(f"  - Win Rate: {stats['win_rate']:.1f}%")
            print(f"  - Profit Factor: {stats['profit_factor']:.2f}")
            print(f"  - Total P&L: ₹{stats['total_pnl']:,.0f}")
        print("="*80 + "\n")


# Main execution
if __name__ == "__main__":
    print(" "*20 + "STRATEGY BACKTESTING & MONTE CARLO SYSTEM")
    print(" "*30 + "Options Trading Analysis")
    print("="*80)
    
    # Initialize backtester
    # If you have historical trades CSV, pass it here
    # Otherwise, it will use sample data for Monte Carlo
    backtester = StrategyBacktester('trade_history.csv')
    
    # Generate complete report
    backtester.generate_report(initial_capital=100000)
    
    # Show plots
    plt.show()
