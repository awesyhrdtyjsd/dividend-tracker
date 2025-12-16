import streamlit as st
import yfinance as yf
import pandas as pd
import requests

st.set_page_config(page_title="High Dividend Stock Tracker", layout="wide")
st.title("💰 Indian High Dividend Stock Tracker")
st.write("Live data fetched from Yahoo Finance for NSE stocks.")

tickers = [
    "IOC.NS", "COALINDIA.NS", "VEDL.NS", "REC.NS", "PFC.NS", 
    "NMDC.NS", "GAIL.NS", "HINDZINC.NS", "PETRONET.NS", 
    "ONGC.NS", "POWERGRID.NS", "NHPC.NS"
]

@st.cache_data(ttl=600)
def get_data():
    data_list = []
    
    # FIX: Create a session with a User-Agent to avoid being blocked
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    with st.spinner('Fetching latest stock prices...'):
        for ticker_symbol in tickers:
            try:
                # Use the session to fetch data
                stock = yf.Ticker(ticker_symbol, session=session)
                info = stock.info
                
                # Try getting the price from different possible keys
                price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                name = info.get('shortName', ticker_symbol)
                div_yield = info.get('dividendYield', 0)
                
                if div_yield is None: div_yield = 0
                div_yield_perc = round(div_yield * 100, 2)
                
                if price:
                    data_list.append({
                        "Stock Name": name,
                        "Ticker": ticker_symbol,
                        "Price (₹)": price,
                        "Dividend Yield (%)": div_yield_perc,
                        "Est. Yearly Div (₹)": round(price * (div_yield_perc/100), 2)
                    })
            except Exception as e:
                continue
                
    return pd.DataFrame(data_list)

df = get_data()

if not df.empty:
    df_sorted = df.sort_values(by="Dividend Yield (%)", ascending=False)
    st.dataframe(
        df_sorted.style.format({
            "Price (₹)": "₹{:.2f}",
            "Dividend Yield (%)": "{:.2f}%",
            "Est. Yearly Div (₹)": "₹{:.2f}"
        }).background_gradient(subset=["Dividend Yield (%)"], cmap="Greens"),
        use_container_width=True,
        hide_index=True
    )
    st.success("Data updated successfully!")
else:
    st.error("Yahoo Finance is currently blocking the connection. Please wait 1 minute and click Refresh.")

if st.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()
