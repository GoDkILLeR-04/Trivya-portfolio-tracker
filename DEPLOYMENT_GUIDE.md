# 🚀 Deploy Your Dashboard to Streamlit Cloud (FREE)

Turn your portfolio tracker into a live web app accessible from anywhere!

---

## Why Deploy?

- ✅ Access your dashboard from any device (phone, tablet, laptop)
- ✅ Share with friends/colleagues via URL
- ✅ No need to run Python locally
- ✅ **100% FREE** hosting from Streamlit
- ✅ Auto-updates when you push to GitHub

---

## Prerequisites

- GitHub account (you already have this!)
- Your code pushed to GitHub (done!)
- Streamlit Cloud account (free, takes 2 minutes)

---

## Step-by-Step Deployment

### Step 1: Sign Up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign up with GitHub"
3. Authorize Streamlit to access your repositories

### Step 2: Deploy Your App

1. Click "New app" button
2. Select:
   - **Repository:** `GoDkiLLeR-04/Trivya-portfolio-tracker`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
   
3. Click "Deploy!"

### Step 3: Wait for Deployment

- Takes 2-3 minutes for first deployment
- Streamlit Cloud will:
  - Read your `requirements.txt`
  - Install all dependencies
  - Launch your app

### Step 4: Get Your Live URL

Your app will be live at:
```
https://YOUR-APP-NAME.streamlit.app
```

Example: `https://trivya-portfolio-tracker.streamlit.app`

---

## ⚠️ Important: Handling Your Private Data

**NEVER upload your real `holdings.csv` or `trade_history.csv` to GitHub!**

### Option 1: Use Sample Data (Recommended for Public Demo)

```bash
# In your repo, keep only sample files
git add sample_holdings.csv sample_trade_history.csv
git commit -m "Add sample data for demo"
git push
```

In `dashboard.py`, modify to use sample files:
```python
def load_equity_holdings():
    try:
        df = pd.read_csv('sample_holdings.csv')  # Use sample data
        # ...
```

### Option 2: Use Streamlit Secrets (For Private Data)

1. In Streamlit Cloud dashboard, go to your app settings
2. Click "Secrets" 
3. Add your holdings as TOML format:
```toml
[holdings]
RELIANCE_NS = {quantity = 50, buy_price = 2450.00, date = "2024-01-15"}
TCS_NS = {quantity = 30, buy_price = 3650.00, date = "2024-02-10"}
```

4. In your code:
```python
import streamlit as st

# Load from secrets
holdings_data = st.secrets["holdings"]
```

### Option 3: File Upload in Dashboard

Modify `dashboard.py` to let users upload their own CSV:

```python
st.sidebar.title("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload holdings.csv", type="csv")

if uploaded_file:
    holdings_df = pd.read_csv(uploaded_file)
else:
    # Use sample data
    holdings_df = pd.read_csv('sample_holdings.csv')
```

This way:
- Public demo uses sample data
- Users can upload their real data (stays in their browser only!)

---

## 🎨 Customization Before Deployment

### Update App Config

In `dashboard.py`, customize the page config:

```python
st.set_page_config(
    page_title="Your Name - Portfolio Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/GoDkiLLeR-04/Trivya-portfolio-tracker',
        'Report a bug': "https://github.com/GoDkiLLeR-04/Trivya-portfolio-tracker/issues",
        'About': "# Trivya Portfolio Tracker\nBuilt with Streamlit & Python"
    }
)
```

### Add Authentication (Optional)

For private use only:

```python
import streamlit as st

def check_password():
    """Returns `True` if user entered correct password."""
    
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    # Main app code here
    st.title("Portfolio Dashboard")
    # ...
```

Then add to Streamlit Secrets:
```toml
password = "your-secret-password"
```

---

## 📊 Managing Your Deployed App

### Update Your App

Any time you push to GitHub:
```bash
git add .
git commit -m "Update dashboard features"
git push
```

Streamlit Cloud auto-detects and redeploys in ~2 minutes!

### View Logs

- In Streamlit Cloud dashboard
- Click "Manage app" → "Logs"
- Debug errors here

### Reboot App

If app crashes:
1. Streamlit Cloud dashboard
2. Click three dots (⋮)
3. Click "Reboot app"

### Delete App

1. Streamlit Cloud dashboard
2. App settings → "Delete app"

---

## 🌐 Share Your Live Dashboard

### Get Shareable Link

Your app URL: `https://YOUR-APP.streamlit.app`

### Add to Your README

Update `README.md`:

```markdown
## 🌐 Live Demo

Try the live dashboard: **[Launch App](https://trivya-portfolio-tracker.streamlit.app)** 🚀

*Uses sample data. Upload your own CSV to see your portfolio.*
```

### Add to LinkedIn Profile

1. LinkedIn Profile → "Featured" section
2. Add link to your live dashboard
3. Recruiters can see it working!

---

## 🎯 Best Practices

### 1. Use Sample Data for Public Demo
```python
# Default to sample data
DEFAULT_CSV = 'sample_holdings.csv'

try:
    df = pd.read_csv(DEFAULT_CSV)
except:
    st.error("Sample data not found!")
```

### 2. Add Disclaimers
```python
st.sidebar.warning("""
⚠️ **Demo Mode**  
This dashboard uses sample data for demonstration.  
Not financial advice.
""")
```

### 3. Handle Errors Gracefully
```python
try:
    prices = fetch_current_prices(symbols)
except Exception as e:
    st.error(f"Error fetching prices: {str(e)}")
    st.info("Using cached data from last update.")
```

### 4. Add Loading States
```python
with st.spinner("Fetching live prices..."):
    prices = fetch_current_prices(symbols)

st.success("✅ Data updated!")
```

---

## 🐛 Common Deployment Issues

### Issue: "ModuleNotFoundError"
**Solution:** Update `requirements.txt` with missing package

### Issue: "File not found"
**Solution:** Ensure all referenced files are in GitHub repo

### Issue: App crashes on startup
**Solution:** 
1. Check logs in Streamlit Cloud
2. Test locally first: `streamlit run dashboard.py`
3. Add try-except blocks around file loading

### Issue: Slow loading
**Solution:**
```python
# Add caching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    return pd.read_csv('data.csv')
```

---

## 📈 Analytics & Usage

Streamlit Cloud provides:
- **Number of visitors**
- **Active users**
- **Resource usage**

View in: App settings → Analytics

---

## 🎓 Next-Level Features

Once deployed, consider adding:

1. **Email Alerts**
```python
if portfolio_drawdown > 10%:
    send_email_alert()  # Using Streamlit Secrets for SMTP
```

2. **Export to PDF**
```python
if st.button("Download Report"):
    generate_pdf_report()
```

3. **Multi-User Support**
```python
# Different portfolios per user
user_id = st.text_input("Enter User ID")
df = load_user_portfolio(user_id)
```

---

## ✅ Deployment Checklist

Before deploying:

- [ ] Push all code to GitHub
- [ ] Include `requirements.txt`
- [ ] Use sample data (or implement file upload)
- [ ] Test locally: `streamlit run dashboard.py`
- [ ] Add disclaimers
- [ ] Update README with live link
- [ ] Test on mobile browser
- [ ] Share on LinkedIn!

---

## 🆘 Need Help?

- [Streamlit Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Community Forum](https://discuss.streamlit.io/)
- Email: pratyushsingh.live@gmail.com

---

**Your portfolio dashboard is now live! 🎉**

Share it with the world and showcase your Python + Finance skills!
