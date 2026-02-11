"""
Options Tracker & Greeks Calculator
Tracks Nifty/Bank Nifty options positions, calculates Greeks, and analyzes strategies
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.stats import norm

class OptionsTracker:
    def __init__(self, csv_file):
        """Initialize options tracker with positions CSV"""
        self.positions = pd.read_csv(csv_file)
        self.positions['date'] = pd.to_datetime(self.positions['date'])
        self.positions['expiry'] = pd.to_datetime(self.positions['expiry'])
        self.spot_price = None
        self.risk_free_rate = 0.068  # India 10Y G-Sec rate
        
    def fetch_spot_price(self):
        """Fetch current Nifty spot price"""
        print("\n" + "="*60)
        print("FETCHING NIFTY SPOT PRICE...")
        print("="*60)
        
        try:
            nifty = yf.Ticker("^NSEI")
            self.spot_price = nifty.info.get('regularMarketPrice', 
                                            nifty.history(period='1d')['Close'].iloc[-1])
            print(f"✓ Nifty Spot: ₹{self.spot_price:,.2f}")
        except:
            print("⚠ Could not fetch live price, using default")
            self.spot_price = 25000
        
        return self.spot_price
    
    def calculate_time_to_expiry(self, expiry_date):
        """Calculate time to expiry in years"""
        today = datetime.now()
        days_to_expiry = (expiry_date - today).days
        return max(days_to_expiry / 365.0, 0.001)  # Min 0.001 to avoid division by zero
    
    def black_scholes_greeks(self, S, K, T, r, sigma, option_type):
        """
        Calculate Black-Scholes price and Greeks
        S: Spot price
        K: Strike price
        T: Time to expiry (years)
        r: Risk-free rate
        sigma: Implied volatility
        option_type: 'CE' or 'PE'
        """
        # Handle expired options
        if T <= 0:
            if option_type == 'CE':
                price = max(S - K, 0)
            else:
                price = max(K - S, 0)
            return {
                'price': price,
                'delta': 0,
                'gamma': 0,
                'theta': 0,
                'vega': 0
            }
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'CE':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            delta = norm.cdf(d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                     - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        else:  # PE
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            delta = -norm.cdf(-d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                     + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # Divide by 100 for 1% change
        
        return {
            'price': price,
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega
        }
    
    def estimate_iv(self, market_price, S, K, T, r, option_type):
        """Estimate implied volatility using simple iteration"""
        if T <= 0 or market_price <= 0:
            return 0.20  # Default 20% IV
        
        # Simple IV estimation (not Newton-Raphson, just approximation)
        for sigma in np.arange(0.05, 2.0, 0.01):
            greeks = self.black_scholes_greeks(S, K, T, r, sigma, option_type)
            if abs(greeks['price'] - market_price) < 1:
                return sigma
        
        return 0.20  # Default if no convergence
    
    def calculate_current_greeks(self):
        """Calculate Greeks for all current positions"""
        print("\n" + "="*60)
        print("CALCULATING GREEKS FOR ALL POSITIONS...")
        print("="*60)
        
        if self.spot_price is None:
            self.fetch_spot_price()
        
        for i, pos in self.positions.iterrows():
            T = self.calculate_time_to_expiry(pos['expiry'])
            
            # Estimate IV from premium paid (simplified)
            # In reality, you'd fetch this from market data
            sigma = self.estimate_iv(
                pos['premium_paid'], 
                self.spot_price, 
                pos['strike'], 
                T, 
                self.risk_free_rate, 
                pos['option_type']
            )
            
            greeks = self.black_scholes_greeks(
                self.spot_price,
                pos['strike'],
                T,
                self.risk_free_rate,
                sigma,
                pos['option_type']
            )
            
            # Store Greeks in dataframe
            self.positions.at[i, 'current_price'] = greeks['price']
            self.positions.at[i, 'delta'] = greeks['delta'] * pos['quantity']
            self.positions.at[i, 'gamma'] = greeks['gamma'] * pos['quantity']
            self.positions.at[i, 'theta'] = greeks['theta'] * pos['quantity']
            self.positions.at[i, 'vega'] = greeks['vega'] * pos['quantity']
            self.positions.at[i, 'iv'] = sigma
            
            # P&L calculation
            if pos['quantity'] > 0:  # Long position
                pnl = (greeks['price'] - pos['premium_paid']) * pos['quantity']
            else:  # Short position
                pnl = (pos['premium_paid'] - greeks['price']) * pos['quantity']
            
            self.positions.at[i, 'pnl'] = pnl
            
            print(f"✓ {pos['option_type']} {pos['strike']} - "
                  f"Delta: {greeks['delta']:.3f}, Theta: {greeks['theta']:.2f}")
        
        return self.positions
    
    def display_positions_summary(self):
        """Display options positions with Greeks"""
        print("\n" + "="*60)
        print("OPTIONS POSITIONS SUMMARY")
        print("="*60)
        
        total_pnl = self.positions['pnl'].sum()
        portfolio_delta = self.positions['delta'].sum()
        portfolio_theta = self.positions['theta'].sum()
        portfolio_vega = self.positions['vega'].sum()
        
        print(f"\nSpot Price:        ₹{self.spot_price:,.2f}")
        print(f"Total P&L:         ₹{total_pnl:,.2f}")
        print(f"Portfolio Delta:   {portfolio_delta:,.2f}")
        print(f"Portfolio Theta:   ₹{portfolio_theta:,.2f}/day")
        print(f"Portfolio Vega:    ₹{portfolio_vega:,.2f}/1% IV change")
        
        print("\n" + "-"*100)
        print(f"{'Type':<6} {'Strike':<8} {'Expiry':<12} {'Qty':<6} {'Premium':<10} "
              f"{'Current':<10} {'P&L':<10} {'Delta':<8} {'Theta':<8}")
        print("-"*100)
        
        for _, pos in self.positions.iterrows():
            days_left = (pos['expiry'] - datetime.now()).days
            print(f"{pos['option_type']:<6} {pos['strike']:<8.0f} "
                  f"{days_left:>3}d left   {pos['quantity']:<6.0f} "
                  f"₹{pos['premium_paid']:<9.2f} ₹{pos['current_price']:<9.2f} "
                  f"₹{pos['pnl']:<9,.0f} {pos['delta']:<8.2f} {pos['theta']:<8.2f}")
        
        print("-"*100)
    
    def analyze_strategies(self):
        """Analyze strategy-wise P&L"""
        print("\n" + "="*60)
        print("STRATEGY-WISE ANALYSIS")
        print("="*60)
        
        strategy_pnl = self.positions.groupby('strategy').agg({
            'pnl': 'sum',
            'delta': 'sum',
            'theta': 'sum'
        })
        
        print(f"\n{'Strategy':<20} {'Total P&L':<15} {'Net Delta':<12} {'Net Theta':<12}")
        print("-"*60)
        
        for strategy, row in strategy_pnl.iterrows():
            print(f"{strategy:<20} ₹{row['pnl']:<14,.2f} {row['delta']:<12.2f} {row['theta']:<12.2f}")
    
    def bear_put_spread_analysis(self):
        """Detailed analysis for bear put spreads"""
        print("\n" + "="*60)
        print("BEAR PUT SPREAD DETAILED ANALYSIS")
        print("="*60)
        
        spreads = self.positions[self.positions['strategy'] == 'bear_put_spread']
        
        if len(spreads) == 0:
            print("No bear put spreads found in portfolio")
            return
        
        # Group by expiry to find matching legs
        for expiry in spreads['expiry'].unique():
            spread_legs = spreads[spreads['expiry'] == expiry]
            
            if len(spread_legs) == 2:
                long_put = spread_legs[spread_legs['quantity'] > 0].iloc[0]
                short_put = spread_legs[spread_legs['quantity'] < 0].iloc[0]
                
                max_profit = (long_put['strike'] - short_put['strike'] - 
                             (long_put['premium_paid'] - short_put['premium_paid']))
                max_loss = long_put['premium_paid'] - short_put['premium_paid']
                
                current_pnl = spread_legs['pnl'].sum()
                
                print(f"\nExpiry: {expiry.strftime('%Y-%m-%d')}")
                print(f"Long Put:  {long_put['strike']} PE @ ₹{long_put['premium_paid']}")
                print(f"Short Put: {short_put['strike']} PE @ ₹{short_put['premium_paid']}")
                print(f"\nMax Profit:    ₹{max_profit * abs(long_put['quantity']):,.2f}")
                print(f"Max Loss:      ₹{max_loss * abs(long_put['quantity']):,.2f}")
                print(f"Current P&L:   ₹{current_pnl:,.2f}")
                print(f"Risk/Reward:   1:{max_profit/max_loss:.2f}")
                
                # Breakeven
                breakeven = long_put['strike'] - max_loss
                print(f"Breakeven:     ₹{breakeven:,.2f}")
                
                if self.spot_price < breakeven:
                    print(f"Status: ✓ In profit zone (Spot below breakeven)")
                else:
                    print(f"Status: ⚠ Above breakeven (Spot: ₹{self.spot_price:,.2f})")
    
    def create_visualizations(self):
        """Generate options analytics charts"""
        print("\n" + "="*60)
        print("GENERATING OPTIONS VISUALIZATIONS...")
        print("="*60)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Options Portfolio Analytics', fontsize=16, fontweight='bold')
        
        # 1. P&L by Position
        ax1 = axes[0, 0]
        position_labels = [f"{row['option_type']}{row['strike']}" 
                          for _, row in self.positions.iterrows()]
        colors_pnl = ['green' if x > 0 else 'red' for x in self.positions['pnl']]
        ax1.bar(range(len(self.positions)), self.positions['pnl'], color=colors_pnl)
        ax1.set_xticks(range(len(self.positions)))
        ax1.set_xticklabels(position_labels, rotation=45, ha='right')
        ax1.set_title('P&L by Option Position')
        ax1.set_ylabel('P&L (₹)')
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Greeks Distribution
        ax2 = axes[0, 1]
        greeks_df = pd.DataFrame({
            'Delta': self.positions['delta'].abs().sum(),
            'Gamma': self.positions['gamma'].abs().sum() * 100,  # Scale for visibility
            'Theta': abs(self.positions['theta'].sum()),
            'Vega': abs(self.positions['vega'].sum())
        }, index=[0])
        
        greeks_df.T.plot(kind='bar', ax=ax2, legend=False, color='steelblue')
        ax2.set_title('Portfolio Greeks (Absolute Values)')
        ax2.set_ylabel('Value')
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Payoff Diagram for Bear Put Spread
        ax3 = axes[1, 0]
        spreads = self.positions[self.positions['strategy'] == 'bear_put_spread']
        
        if len(spreads) >= 2:
            long_put = spreads[spreads['quantity'] > 0].iloc[0]
            short_put = spreads[spreads['quantity'] < 0].iloc[0]
            
            # Generate spot price range
            spot_range = np.linspace(
                short_put['strike'] - 500, 
                long_put['strike'] + 500, 
                100
            )
            
            net_premium = long_put['premium_paid'] - short_put['premium_paid']
            
            payoffs = []
            for spot in spot_range:
                long_payoff = max(long_put['strike'] - spot, 0) - long_put['premium_paid']
                short_payoff = short_put['premium_paid'] - max(short_put['strike'] - spot, 0)
                payoffs.append((long_payoff + short_payoff) * abs(long_put['quantity']))
            
            ax3.plot(spot_range, payoffs, linewidth=2, color='darkblue')
            ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax3.axvline(x=self.spot_price, color='red', linestyle='--', 
                       linewidth=2, label=f'Current Spot: ₹{self.spot_price:,.0f}')
            ax3.fill_between(spot_range, 0, payoffs, 
                            where=np.array(payoffs) > 0, 
                            alpha=0.3, color='green', label='Profit Zone')
            ax3.fill_between(spot_range, 0, payoffs, 
                            where=np.array(payoffs) < 0, 
                            alpha=0.3, color='red', label='Loss Zone')
            ax3.set_title('Bear Put Spread Payoff Diagram')
            ax3.set_xlabel('Nifty Spot Price')
            ax3.set_ylabel('P&L at Expiry (₹)')
            ax3.legend()
            ax3.grid(alpha=0.3)
        
        # 4. Time Decay (Theta) Analysis
        ax4 = axes[1, 1]
        days_to_expiry = [(row['expiry'] - datetime.now()).days 
                         for _, row in self.positions.iterrows()]
        ax4.scatter(days_to_expiry, self.positions['theta'], 
                   s=100, alpha=0.6, c=self.positions['theta'], cmap='RdYlGn_r')
        ax4.set_title('Theta vs Days to Expiry')
        ax4.set_xlabel('Days to Expiry')
        ax4.set_ylabel('Theta (₹/day)')
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.grid(alpha=0.3)
        
        # Add labels
        for i, (days, theta) in enumerate(zip(days_to_expiry, self.positions['theta'])):
            ax4.annotate(f"{self.positions.iloc[i]['option_type']}{self.positions.iloc[i]['strike']:.0f}", 
                        (days, theta), fontsize=8)
        
        plt.tight_layout()
        plt.savefig('options_analysis.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: options_analysis.png")
        
        return fig
    
    def generate_report(self):
        """Generate complete options report"""
        print("\n" + "="*80)
        print(" "*20 + "OPTIONS PORTFOLIO REPORT")
        print(" "*25 + f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80)
        
        self.fetch_spot_price()
        self.calculate_current_greeks()
        self.display_positions_summary()
        self.analyze_strategies()
        self.bear_put_spread_analysis()
        self.create_visualizations()
        
        print("\n" + "="*80)
        print("✓ OPTIONS ANALYSIS COMPLETE")
        print("="*80)
        print("\nGenerated Files:")
        print("  - options_analysis.png (4 charts dashboard)")
        print("\nKey Insights:")
        print(f"  - Portfolio Delta: {self.positions['delta'].sum():.2f} "
              f"({'Bullish' if self.positions['delta'].sum() > 0 else 'Bearish'})")
        print(f"  - Daily Theta Decay: ₹{self.positions['theta'].sum():.2f}")
        print(f"  - Total Options P&L: ₹{self.positions['pnl'].sum():,.2f}")
        print("="*80 + "\n")


# Main execution
if __name__ == "__main__":
    print("\n" + "="*80)
    print(" "*22 + "OPTIONS TRACKER & GREEKS ANALYZER")
    print(" "*25 + "Nifty Options Portfolio System")
    print("="*80)
    
    # Initialize tracker
    tracker = OptionsTracker('options_positions.csv')
    
    # Generate complete report
    tracker.generate_report()
    
    # Show plots
    plt.show()
