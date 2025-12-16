import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="High Dividend Stock Tracker", layout="wide")
st.title("💰 Indian High Dividend Stock Tracker")
st.write("Live data fetched from Yahoo Finance for NSE stocks.")

# 2. List of Stocks to Track (Add more tickers ending with .NS for NSE)
tickers = [
    "IOC.NS", "COALINDIA.NS", "VEDL.NS", "REC.NS", "PFC.NS", 
    "NMDC.NS", "GAIL.NS", "HINDZINC.NS", "PETRONET.NS", 
    "ONGC.NS", "POWERGRID.NS", "NHPC.NS", "BALMERLAWRIE.NS"
]

# 3. Function to fetch data
@st.cache_data(ttl=300) # Updates data every 5 minutes
def get_data():
    data_list = []
    
    # Show a loading spinner while fetching
    with st.spinner('Fetching latest stock prices...'):
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get key details
                name = info.get('shortName', ticker)
                price = info.get('currentPrice', 0)
                div_yield = info.get('dividendYield', 0)
                
                # Convert yield to percentage (e.g., 0.05 -> 5.0%)
                if div_yield is not None:
                    div_yield_perc = round(div_yield * 100, 2)
                else:
                    div_yield_perc = 0
                
                # Filter: Only showing stocks under ₹500 (Optional)
                # You can remove this 'if' statement to see expensive stocks too
                if price > 0: 
                    data_list.append({
                        "Stock Name": name,
                        "Ticker": ticker,
                        "Price (₹)": price,
                        "Dividend Yield (%)": div_yield_perc,
                        "Est. Annual Dividend (₹)": round(price * (div_yield_perc/100), 2)
                    })
            except Exception as e:
                pass # Skip if data error
                
    return pd.DataFrame(data_list)

# 4. Process and Display Data
df = get_data()

# Sort by Dividend Yield (Highest first)
if not df.empty:
    df_sorted = df.sort_values(by="Dividend Yield (%)", ascending=False)
    
    # Highlight high yields
    st.dataframe(
        df_sorted.style.format({
            "Price (₹)": "₹{:.2f}",
            "Dividend Yield (%)": "{:.2f}%",
            "Est. Annual Dividend (₹)": "₹{:.2f}"
        }).background_gradient(subset=["Dividend Yield (%)"], cmap="Greens"),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("Could not fetch data. Please try again later.")

# 5. Refresh Button
if st.button('Refresh Data'):
    st.cache_data.clear()
