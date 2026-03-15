import streamlit as st

st.set_page_config(page_title="Methodology — FRS-1000", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 2rem !important; max-width: 900px; }
header[data-testid="stHeader"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-bottom: 48px;">
  <div style="font-size:3em; font-weight:900; color:#2E7BE6; letter-spacing:-2px;">FRS-1000</div>
  <div style="font-size:1.2em; color:#64748b; margin-top:8px;">Scoring Methodology</div>
</div>
""", unsafe_allow_html=True)

# --- What is FRS-1000 ---
st.markdown("## What is FRS-1000?")
st.markdown("""
FRS-1000 is a multi-dimensional scoring framework designed to give financial advisors and investors a structured,
at-a-glance view of asset quality. Each asset is scored across **5 axes**, each worth up to **200 points**,
for a maximum total of **1,000 points**.

The score is not a buy or sell recommendation. It is a screening tool — a way to surface candidates
for deeper analysis and facilitate structured conversations with clients.
""")

st.divider()

# --- SGX Equities ---
st.markdown("## SGX Equities")
st.markdown("Scores Singapore-listed companies across 5 fundamental and market-based dimensions.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
**Entry Edge** *(max 200)*
Momentum score combining price-to-moving-average ratio with P/E valuation.
*Higher score = strong momentum + reasonable valuation*

**Stability Profile** *(max 200)*
Derived from market capitalisation and price volatility.
*Higher score = large, stable market presence*

**Durability** *(max 200)*
Price resilience relative to 52-week high, adjusted by debt-to-equity ratio.
*Higher score = strong balance sheet, price near highs*
""")

with col2:
    st.markdown("""
**Cashflow Quality** *(max 200)*
Return on Equity (ROE) — a proxy for capital efficiency.
*Higher score = effective use of shareholder equity*

**Shareholder Return** *(max 200)*
Long-term price growth combined with dividend yield.
*Higher score = sustained growth + shareholder returns*
""")

st.divider()

# --- Central Banks ---
st.markdown("## Central Banks")
st.markdown("Scores the macroeconomic health of five major central banks using publicly available data.")

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
**Price Stability** *(max 200)*
CPI year-on-year deviation from the 2% inflation target.
*Higher score = inflation close to target*

**Employment** *(max 200)*
Inverse of the unemployment rate.
*Higher score = low unemployment*

**Monetary Policy** *(max 200)*
Yield curve spread (10Y minus 2Y/short-term rate).
*Higher score = healthy positive curve*
""")

with col4:
    st.markdown("""
**Liquidity** *(max 200)*
M2 money supply year-on-year growth deviation from 5% benchmark.
*Higher score = stable, moderate money supply growth*

**Market Stability** *(max 200)*
Inverse of 20-day 10Y yield volatility.
*Higher score = stable bond market*
""")

st.markdown("""
**Data Sources:** Federal Reserve (FRED), European Central Bank (ECB SDMX API), World Bank API
""")

st.divider()

# --- Commodities ---
st.markdown("## Commodities")
st.markdown("Scores commodity assets based on price dynamics and market structure.")

col5, col6 = st.columns(2)

with col5:
    st.markdown("""
**Price Momentum** *(max 200)*
3-month price change trend.
*Higher score = strong recent upward momentum*

**Supply Stability** *(max 200)*
Inverse of 20-day price volatility.
*Higher score = stable supply dynamics*

**Demand Signal** *(max 200)*
Current price relative to 1-year average.
*Higher score = price above historical average = demand strength*
""")

with col6:
    st.markdown("""
**Price Level** *(max 200)*
Current price relative to 52-week high.
*Higher score = price near recent highs*

**Market Trend** *(max 200)*
1-year price performance (annualised return).
*Higher score = sustained upward trend*
""")

st.divider()

# --- Disclaimer ---
st.markdown("""
<div style="background:#f8fafc; border-left:4px solid #2E7BE6; padding:20px; border-radius:8px; font-size:0.85em; color:#64748b;">
<strong>DISCLAIMER:</strong> FRS-1000 scores are for informational and screening purposes only.
They do not constitute investment advice, recommendations, or solicitation to buy or sell any security.
All investment decisions should be made at the user's own discretion and risk.
We do not guarantee the accuracy, completeness, or timeliness of any data used in the scoring model.
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
