# Contributing to Trivya Portfolio Tracker

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to Trivya Portfolio Tracker. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, CSV samples)
- **Describe the behavior you observed** vs **expected behavior**
- **Include screenshots** if relevant
- **Mention your environment:**
  - OS (Windows/macOS/Linux)
  - Python version
  - Package versions (`pip list`)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List some examples** of how it would work

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Add tests** if you've added code that should be tested
3. **Update documentation** (README, docstrings)
4. **Follow the Python style guide** (PEP 8)
5. **Ensure all tests pass**
6. **Issue the pull request!**

## Development Setup

```bash
# Fork and clone your fork
git clone https://github.com/YOUR-USERNAME/Trivya-portfolio-tracker.git
cd Trivya-portfolio-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy
```

## Code Style

### Python

- Follow **PEP 8**
- Use **type hints** where appropriate
- Write **docstrings** for functions/classes
- Keep functions **focused** and **small**
- Use **meaningful variable names**

**Format code with Black:**
```bash
black *.py
```

**Check with flake8:**
```bash
flake8 *.py --max-line-length=100
```

### Example

```python
def calculate_sharpe_ratio(
    returns: pd.Series, 
    risk_free_rate: float = 0.068
) -> float:
    """
    Calculate Sharpe Ratio for a return series.
    
    Args:
        returns: Pandas Series of daily returns
        risk_free_rate: Annual risk-free rate (default: 6.8% for India)
    
    Returns:
        Sharpe ratio as float
    
    Example:
        >>> returns = pd.Series([0.01, -0.02, 0.015, ...])
        >>> sharpe = calculate_sharpe_ratio(returns)
        >>> print(f"Sharpe: {sharpe:.3f}")
    """
    excess_returns = returns.mean() * 252 - risk_free_rate
    volatility = returns.std() * np.sqrt(252)
    
    return excess_returns / volatility if volatility > 0 else 0
```

## Project Structure

```
Trivya-portfolio-tracker/
├── portfolio_tracker.py       # Main equity tracking
├── backtest_strategy.py       # Options backtesting
├── dashboard.py               # Streamlit dashboard
├── requirements.txt           # Dependencies
├── README.md                  # Main documentation
├── USAGE_GUIDE.md            # User guide
├── DEPLOYMENT_GUIDE.md       # Streamlit Cloud guide
├── CONTRIBUTING.md           # This file
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore rules
├── sample_holdings.csv      # Sample equity data
├── sample_trade_history.csv # Sample options data
├── sample_options_positions.csv
└── tests/                   # Unit tests (to be added)
    ├── test_portfolio.py
    └── test_backtest.py
```

## Feature Ideas (Help Wanted!)

We'd love help with these features:

### High Priority
- [ ] Unit tests with pytest
- [ ] Excel export functionality
- [ ] Email/SMS alerts for drawdowns
- [ ] Portfolio optimization (Markowitz)
- [ ] Support for BSE stocks
- [ ] Dividend tracking

### Medium Priority
- [ ] Crypto portfolio tracking
- [ ] Multi-currency support
- [ ] Historical trade journal
- [ ] Tax calculator (India)
- [ ] Broker integration APIs

### Low Priority
- [ ] Dark mode for dashboard
- [ ] Custom themes
- [ ] Mobile app version
- [ ] Voice commands (Alexa/Google)

## Testing

Add tests for new features:

```python
# tests/test_portfolio.py
import pytest
from portfolio_tracker import PortfolioTracker

def test_calculate_pnl():
    tracker = PortfolioTracker('sample_holdings.csv')
    tracker.fetch_current_prices()
    
    assert tracker.holdings['pnl'].sum() != 0
    assert 'current_price' in tracker.holdings.columns
```

Run tests:
```bash
pytest tests/
```

## Documentation

- Update README.md for major features
- Update USAGE_GUIDE.md for user-facing changes
- Add docstrings to all functions
- Include code examples

## Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests

**Examples:**
```
Add Monte Carlo variance analysis
Fix bug in Greeks calculation for ITM options
Update README with deployment instructions
```

## Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `docs/what-you-changed` - Documentation
- `refactor/what-you-refactored` - Code refactoring

## Code Review Process

1. Maintainer reviews PR within 48 hours
2. Address feedback/requested changes
3. Once approved, PR is merged to `main`
4. Your contribution is live! 🎉

## Recognition

All contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in README (for major features)

## Questions?

Feel free to:
- Open an issue with tag `question`
- Email: pratyushsingh.live@gmail.com
- Start a discussion on GitHub

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Examples of behavior that contributes to a positive environment:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting pratyushsingh.live@gmail.com. All complaints will be reviewed and investigated.

---

**Thank you for contributing to Trivya Portfolio Tracker! 🚀**
