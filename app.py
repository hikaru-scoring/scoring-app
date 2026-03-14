# app.py
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from ui_components import inject_css, render_radar_chart
from data_logic import fetch_data, fetch_central_bank_data, fetch_commodity_data, fetch_news

APP_TITLE = "FRS-1000 — SGX Dashboard"

# 冒頭 9行目付近
AXES = [
    "Future Focus",
    "Market Position",
    "Financial Strength",
    "Cashflow Quality",
    "People"
]

st.set_page_config(page_title=APP_TITLE, layout="wide")

def main():
    #inject_css()
    st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem !important; }
    header[data-testid="stHeader"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    if "saved_data" not in st.session_state:
        st.session_state.saved_data = None
    if "saved_cb_data" not in st.session_state:
        st.session_state.saved_cb_data = None
    if "saved_comm_data" not in st.session_state:
        st.session_state.saved_comm_data = None

    # --- タブ ---
    tab1, tab2, tab3 = st.tabs(["SGX", "Central Banks", "Commodities"])

    # --- SGX TAB ---
    with tab1:

        top_5 = [
            {"name": "DBS Group", "symbol": "D05"},
            {"name": "Singtel", "symbol": "Z74"},
            {"name": "OCBC Bank", "symbol": "O39"},
            {"name": "Keppel Ltd", "symbol": "BN4"},
            {"name": "CapitaLand Investment", "symbol": "9CI"}
        ]

        options = [f"{s['name']} ({s['symbol']})" for s in top_5]

        target = st.selectbox(
            "Select Asset",
            options
        )

        # 名前抽出
        name = target.rsplit(" (", 1)[0]

        # シンボル取得
        symbol = next(
            s["symbol"] for s in top_5 if s["name"] == name
        )

        st.markdown(
            f'<div style="font-size:1.1em; font-weight:700; color:#333; margin:4px 0 2px;">{name}</div>',
            unsafe_allow_html=True
        )

        # データ取得
        data = fetch_data(symbol, name)

        options = [f"{s['name']} ({s['symbol']})" for s in top_5]

        if data is None:
            DUMMY_AXES = {"Future Focus": 100, "Market Position": 100, "Financial Strength": 100, "Cashflow Quality": 100, "People": 100}
            data = {"axes": DUMMY_AXES, "total": 500, "name": name, "price_hist": None, "current_price": 0, "pe": "N/A", "market_cap": 0}
            data["_loading"] = True

        if data:

            if data.get("_loading"):
                st.warning("Stock data is currently unavailable (Yahoo Finance rate limit). Scores will load automatically — please check back later.")

            col_btn1, col_btn2, col_btn_rest = st.columns([1, 1, 8])

            with col_btn1:
                save_it = st.button("Save")

            with col_btn2:
                clear_it = st.button("Clear")

            # 3. ボタンごとの動作設定
            if save_it:
                st.session_state.saved_data = data
                st.rerun()

            if clear_it:
                st.session_state.saved_data = None
                st.rerun()

            # 1. 総合点数（中央上部）
            source = st.session_state.saved_data if st.session_state.saved_data else data
            display_total = int(data.get("total", 0))

            st.markdown(f"""
            <div style="text-align:center; margin-top:4px; margin-bottom:10px;">
                <div style="font-size:14px; letter-spacing:2px; color:#666;">TOTAL SCORE</div>
                <div style="font-size:90px; font-weight:800; color:#2E7BE6; line-height:1;">
                    {display_total}
                    <span style="font-size:35px; color:#BBB;">/ 1000</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 2. 中段：レーダーチャート（左）と DNA点数（右）
            col_left, col_right = st.columns([1.8, 1])

            with col_left:
                # タイトルの上下余白を極限まで詰める
                st.markdown("<div style='font-size: 1.1em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 5px;'>I. Intelligence Radar</div>", unsafe_allow_html=True)

                fig_r = render_radar_chart(
                    data,
                    st.session_state.saved_data,
                    AXES
                )

                st.plotly_chart(
                    fig_r,
                    use_container_width=True
                )
            with col_right:

                # 右側のタイトルも左に合わせて上に寄せる
                st.markdown(
                    "<div style='font-size: 0.9em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 15px; border-left: 3px solid #2E7BE6; padding-left: 8px;'>II. ANALYSIS SCORE METRICS</div>",
                    unsafe_allow_html=True
                )

                # 表示ソースの確定
                source = st.session_state.saved_data if st.session_state.saved_data else data
                is_oil = source.get('name') == "WTI CRUDE OIL"

                # 🚀 会社用のロジック解説（Peopleに復刻）
                logic_descriptions = {
                    "Future Focus": "Momentum (Price vs Avg) × Valuation (PER)",
                    "Market Position": "Market Volatility × Market Capitalization",
                    "Financial Strength": "Price Resilience × Debt-to-Equity Ratio",
                    "Cashflow Quality": "Return on Equity (ROE): Capital Efficiency",
                    "People": "Long-term Growth × Dividend Yield"
                }

                oil_labels = [
                    "Demand Forecast",
                    "Geopolitical Risk",
                    "Price Level Stress",
                    "Supply Stability",
                    "Market Heat Index"
                ]

                oil_descriptions = {
                    "Demand Forecast": "Price vs 1Y Average",
                    "Geopolitical Risk": "Market Volatility × Risk",
                    "Price Level Stress": "Distance from 1Y High",
                    "Supply Stability": "20-Day Volatility",
                    "Market Heat Index": "Annual Growth Rate"
                }

                # 指標カードの生成（25% Enlarged Version）
                for i, k in enumerate(AXES):

                    v1 = data["axes"].get(k, 0)  # 現在の資産（青）
                    v2 = st.session_state.saved_data["axes"].get(k, 0) if st.session_state.saved_data else None  # 保存済み（オレンジ）

                    display_label = oil_labels[i] if is_oil else k
                    desc_text = oil_descriptions.get(display_label, "") if is_oil else logic_descriptions.get(k, "")

                    # 比較中は現在選択をオレンジ、保存済みを青。単独表示は青。
                    c1 = '#F4A261' if v2 is not None else '#2E7BE6'
                    score_html = f'<span style="color: {c1};">{int(v1)}</span>'

                    if v2 is not None:
                        score_html += f' <span style="color: #ccc; font-size: 0.9em; font-weight:bold; margin: 0 6px;">vs</span> <span style="color: #2E7BE6;">{int(v2)}</span>'

                    st.markdown(
                        f"""
                        <div style="
                            background-color: #FFFFFF; 
                            padding: 20px; 
                            border-radius: 12px; 
                            margin-bottom: 12px; 
                            border: 1px solid #E0E0E0; 
                            border-left: 8px solid #2E7BE6; 
                            box-shadow: 2px 2px 5px rgba(0,0,0,0.07);
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-size: 1.2em; font-weight: 800; color: #333333;">{display_label}</span>
                                <span style="font-size: 1.7em; font-weight: 900; line-height: 1;">{score_html}</span>
                            </div>
                            <p style="font-size: 0.95em; color: #777777; margin: 0; line-height: 1.3; font-weight: 500;">{desc_text}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # 3. 下段：株価チャート
            st.markdown("<div class='section-title'>V. Price Performance (5Y)</div>", unsafe_allow_html=True)

            if data.get('price_hist') is None:
                st.info("Price chart unavailable — data is loading. Please refresh in 1-2 minutes.")
            else:
                fig_p = go.Figure()

                if st.session_state.saved_data and st.session_state.saved_data.get('price_hist') is not None:
                    s_data = st.session_state.saved_data
                    y1 = (data['price_hist'] / data['price_hist'].iloc[0] - 1) * 100
                    y2 = (s_data['price_hist'] / s_data['price_hist'].iloc[0] - 1) * 100
                    fig_p.add_trace(go.Scatter(x=y1.index, y=y1.values, mode='lines', name=name, line=dict(color='#F4A261', width=3)))
                    fig_p.add_trace(go.Scatter(x=y2.index, y=y2.values, mode='lines', name=s_data['name'], line=dict(color='#2E7BE6', width=3)))
                    fig_p.update_layout(yaxis_title="Return (%)")
                else:
                    fig_p.add_trace(go.Scatter(x=data['price_hist'].index, y=data['price_hist'].values, mode='lines', name=name, line=dict(color='#2E7BE6', width=3)))
                    fig_p.update_layout(yaxis_title="Price")

                fig_p.update_layout(
                    plot_bgcolor='white',
                    height=400,
                    margin=dict(l=0, r=0, t=20, b=0),
                    hovermode="x unified",
                    clickmode='none',
                    dragmode=False
                )
                st.plotly_chart(fig_p, use_container_width=True)

            # 4. Snapshot（比較対応版）
            st.markdown("<div class='section-title'>VI. Snapshot Comparison</div>", unsafe_allow_html=True)

            s1, s2, s3 = st.columns(3)

            saved = st.session_state.saved_data  # 比較対象データ

            # --- PRICE ---
            p1 = data.get("current_price", 0)
            p2 = saved.get("current_price") if saved else None

            p1_color = '#F4A261' if p2 is not None else '#2E7BE6'
            p_html = f'<span style="color:{p1_color};">{p1:.2f}</span>'

            if p2 is not None:
                p_html += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#2E7BE6;">{p2:.2f}</span>'

            s1.markdown(
                f'<div class="card"><div style="font-size:11px; color:#999;">PRICE</div><div style="font-size:22px; font-weight:900;">{p_html}</div></div>',
                unsafe_allow_html=True
            )        
            # --- P/E RATIO ---
            pe1 = data.get("pe", "N/A")
            pe1_txt = f"{pe1:.1f}" if isinstance(pe1, (int, float)) and pe1 != 0 else "N/A"
            pe2 = saved.get("pe") if saved else None
            pe2_txt = f"{pe2:.1f}" if isinstance(pe2, (int, float)) and pe2 != 0 else "N/A"

            pe1_color = '#F4A261' if saved else '#2E7BE6'
            pe_html = f'<span style="color:{pe1_color};">{pe1_txt}</span>'
            if saved:
                pe_html += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#2E7BE6;">{pe2_txt}</span>'

            s2.markdown(
                f'<div class="card"><div style="font-size:11px; color:#999;">P/E RATIO</div><div style="font-size:22px; font-weight:900;">{pe_html}</div></div>',
                unsafe_allow_html=True
            )

            # --- MARKET CAP ---
            cap1 = data.get("market_cap", 0)
            cap2 = saved.get("market_cap", 0) if saved else None

            cap1_color = '#F4A261' if cap2 is not None else '#2E7BE6'
            cap_html = f'<span style="color:{cap1_color};">{cap1/1e9:.1f}B</span>'
            if cap2 is not None:
                cap2_txt = f"{cap2/1e9:.1f}B" if cap2 > 0 else "N/A"
                cap_html += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#2E7BE6;">{cap2_txt}</span>'

            s3.markdown(
                f'<div class="card"><div style="font-size:11px; color:#999;">MARKET CAP</div><div style="font-size:22px; font-weight:900;">{cap_html}</div></div>',
                unsafe_allow_html=True
            )

            # --- VII. NEWS ---
            st.markdown("<div class='section-title'>VII. Latest News</div>", unsafe_allow_html=True)
            news_items = fetch_news(f"{symbol}.SI")
            if news_items:
                for item in news_items:
                    st.markdown(
                        f'<div style="padding:10px 0; border-bottom:1px solid #F0F0F0;">'
                        f'<a href="{item["link"]}" target="_blank" style="font-size:0.95em; font-weight:600; color:#1e3a8a; text-decoration:none;">{item["title"]}</a>'
                        f'<div style="font-size:0.8em; color:#999; margin-top:3px;">{item["publisher"]} · {item["date"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.caption("No recent news available.")

            # --- VIII. METHODOLOGY ---
            with st.expander("How does the scoring work?"):
                st.markdown("### FRS-1000 Scoring Framework")
                st.markdown("Each asset is scored across **5 axes**, each worth up to **200 points** (max total: **1,000 points**).")

                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown("""
**How to read the score**
- **800–1000** — Strong across most dimensions
- **600–799** — Solid, with some areas to watch
- **400–599** — Mixed signals, warrants deeper analysis
- **Below 400** — Significant weaknesses in multiple areas

**How to use the comparison**
Press **Save** on any asset, then switch to another.
The radar chart and score cards will show both side-by-side,
making it easy to identify where one asset outperforms the other.
""")
                with col_m2:
                    st.markdown("""
**Data sources & update frequency**
- Stock data: Yahoo Finance (refreshed every 24 hours)
- Central bank data: FRED, ECB API, World Bank (refreshed every 24 hours)
- Commodity data: Yahoo Finance (refreshed every 24 hours)

**Premium Plan**
The current version covers selected SGX stocks for demonstration.
Subscribers get access to **all SGX-listed stocks** with real-time,
institutional-grade data and full historical scoring.
""")

                st.caption("This tool is for informational and screening purposes only. It does not constitute investment advice. All investment decisions are made at the user's own risk.")

            # --- VIII. PRE-ORDER SECTION (Branded White Edition) ---
            st.markdown("<br><br>", unsafe_allow_html=True)

            st.markdown(
"""
<div style="text-align: center; padding: 60px 40px; background: #FFFFFF; border-radius: 24px; color: #1e293b; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-top: 40px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
<div style="margin-bottom: 20px;">
<span style="font-size: 3.5em; font-weight: 900; color: #2E7BE6; letter-spacing: -2px;">SCORING</span>
</div>
<p style="font-size: 1.1em; color: #64748b; margin-bottom: 35px;">Exclusive Early Access for the First Visionaries.</p>
<div style="display: flex; justify-content: center; gap: 40px; margin-bottom: 40px;">
<div style="text-align: center;">
<div style="font-size: 0.8em; color: #94a3b8; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">Registration Status</div>
<div style="font-size: 1.3em; font-weight: 800; color: #10b981;">OPEN</div>
</div>
</div>

<div style="background: #f8fafc; padding: 35px; border-radius: 16px; margin-bottom: 40px; border: 1px solid #f1f5f9;">
<div style="font-size: 4.2em; font-weight: 900; color: #1e3a8a; line-height: 1;">S$500 <span style="font-size: 0.35em; font-weight: 600; color: #64748b; vertical-align: middle;">/ MONTH</span></div>
</div>

<div style="background: #1e3a8a; color: #FFFFFF; padding: 18px 60px; font-size: 1.4em; font-weight: 900; border-radius: 50px; display: inline-block; cursor: pointer; box-shadow: 0 10px 20px rgba(30, 58, 138, 0.2); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 30px;">
Secure Your Slot Now
</div>

<div style="margin-top: 10px; padding: 20px; background: #f8fafc; border-radius: 12px; font-size: 0.75em; color: #64748b; line-height: 1.6; text-align: left; border-left: 5px solid #2E7BE6; max-width: 600px; margin-left: auto; margin-right: auto;">
<strong>DISCLAIMER:</strong> This service is for informational purposes only and does not constitute investment advice, recommendation, or solicitation. While we strive for accuracy, we do not guarantee the completeness or reliability of the data provided. All investment decisions should be made at the user's own discretion and risk. We shall not be held liable for any loss or damage arising from the use of this service.
</div>

<div style="margin-top: 30px; font-size: 0.85em; color: #94a3b8; font-weight: 500;">
Official Launch: March 1, 2026 | Full Institutional Engine Unlocked
</div>
</div>
""",
                unsafe_allow_html=True
            )

    # --- Central Banks TAB ---
    CB_AXES = [
        "Price Stability",
        "Employment",
        "Monetary Policy",
        "Liquidity",
        "Market Stability",
    ]

    cb_logic_descriptions = {
        "Price Stability": "CPI YoY deviation from 2% target",
        "Employment":      "Labor market health (inverse unemployment)",
        "Monetary Policy": "Yield curve spread (10Y − 2Y)",
        "Liquidity":       "M2 money supply YoY growth",
        "Market Stability":"10Y yield volatility (20-day)",
    }

    with tab2:

        st.markdown(
            "<div class='company-header'>Central Banks</div>",
            unsafe_allow_html=True
        )

        banks = [
            "Federal Reserve",
            "European Central Bank",
            "Bank of Japan",
            "Bank of England",
            "MAS"
        ]

        bank = st.selectbox("Select Central Bank", banks)

        # FREDデータ取得
        bank_data = fetch_central_bank_data(bank)

        if bank_data:

            cb_btn1, cb_btn2 = st.columns(2)
            with cb_btn1:
                cb_save = st.button("Save", key="cb_save")
            with cb_btn2:
                cb_clear = st.button("Clear", key="cb_clear")

            if cb_save:
                st.session_state.saved_cb_data = bank_data
                st.rerun()
            if cb_clear:
                st.session_state.saved_cb_data = None
                st.rerun()

            # --- 1. Total Score ---
            display_total_cb = int(bank_data.get("total", 0))

            st.markdown(f"""
            <div style="text-align:center; margin-top:40px; margin-bottom:30px;">
                <div style="font-size:14px; letter-spacing:2px; color:#666;">TOTAL SCORE</div>
                <div style="font-size:90px; font-weight:800; color:#2E7BE6;">
                    {display_total_cb}
                    <span style="font-size:35px; color:#BBB;">/ 1000</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- 2. レーダーチャート（左）＋ スコアカード（右） ---
            cb_col_left, cb_col_right = st.columns([1.8, 1])

            with cb_col_left:
                st.markdown(
                    "<div style='font-size: 1.1em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 5px;'>I. Intelligence Radar</div>",
                    unsafe_allow_html=True
                )
                fig_cb = render_radar_chart(
                    bank_data,
                    st.session_state.saved_cb_data,
                    CB_AXES
                )
                st.plotly_chart(fig_cb, use_container_width=True)

            with cb_col_right:
                st.markdown(
                    "<div style='font-size: 0.9em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 15px; border-left: 3px solid #2E7BE6; padding-left: 8px;'>II. ANALYSIS SCORE METRICS</div>",
                    unsafe_allow_html=True
                )

                for k in CB_AXES:
                    v1 = bank_data["axes"].get(k, 0)
                    v2 = st.session_state.saved_cb_data["axes"].get(k, 0) if st.session_state.saved_cb_data else None
                    desc_text = cb_logic_descriptions.get(k, "")

                    score_html = f'<span style="color: #2E7BE6;">{int(v1)}</span>'
                    if v2 is not None:
                        score_html += f' <span style="color: #ccc; font-size: 0.9em; font-weight:bold; margin: 0 6px;">vs</span> <span style="color: #F4A261;">{int(v2)}</span>'

                    st.markdown(
                        f"""
                        <div style="
                            background-color: #FFFFFF;
                            padding: 20px;
                            border-radius: 12px;
                            margin-bottom: 12px;
                            border: 1px solid #E0E0E0;
                            border-left: 8px solid #2E7BE6;
                            box-shadow: 2px 2px 5px rgba(0,0,0,0.07);
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-size: 1.2em; font-weight: 800; color: #333333;">{k}</span>
                                <span style="font-size: 1.7em; font-weight: 900; line-height: 1;">{score_html}</span>
                            </div>
                            <p style="font-size: 0.95em; color: #777777; margin: 0; line-height: 1.3; font-weight: 500;">{desc_text}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # --- 3. Snapshot（Raw Macro Data） ---
            st.markdown("<div class='section-title'>III. Macro Snapshot</div>", unsafe_allow_html=True)

            saved_cb = st.session_state.saved_cb_data
            snap1, snap2, snap3 = st.columns(3)

            def snap_html(label, val1, val2, fmt="{:.2f}%"):
                v1_str = fmt.format(val1) if val1 is not None else "N/A"
                h = f'<span style="color:#2E7BE6;">{v1_str}</span>'
                if val2 is not None:
                    h += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#F4A261;">{fmt.format(val2)}</span>'
                return f'<div class="card"><div style="font-size:11px; color:#999;">{label}</div><div style="font-size:22px; font-weight:900;">{h}</div></div>'

            snap1.markdown(snap_html("10Y YIELD",     bank_data["y10"],         saved_cb["y10"]         if saved_cb else None), unsafe_allow_html=True)
            snap2.markdown(snap_html("CPI YoY",       bank_data["cpi_yoy"],     saved_cb["cpi_yoy"]     if saved_cb else None), unsafe_allow_html=True)
            snap3.markdown(snap_html("UNEMPLOYMENT",  bank_data["unemployment"], saved_cb["unemployment"] if saved_cb else None), unsafe_allow_html=True)

            snap4, snap5, snap6 = st.columns(3)
            snap4.markdown(snap_html("M2 YoY",        bank_data["m2_yoy"],      saved_cb["m2_yoy"]      if saved_cb else None), unsafe_allow_html=True)
            snap5.markdown(snap_html("YIELD CURVE",   bank_data["curve"],       saved_cb["curve"]       if saved_cb else None), unsafe_allow_html=True)
            snap6.markdown(snap_html("2Y YIELD",      bank_data["y2"],          saved_cb["y2"]          if saved_cb else None), unsafe_allow_html=True)

            # --- 4. 10年債利回りチャート ---
            st.markdown("<div class='section-title'>IV. 10Y Yield History (5Y)</div>", unsafe_allow_html=True)

            if bank_data.get("y10_hist") is not None:
                fig_y = go.Figure()
                hist = bank_data["y10_hist"]
                hist_5y = hist[hist.index >= (hist.index[-1] - pd.DateOffset(years=5))]

                if saved_cb and saved_cb.get("y10_hist") is not None:
                    s_hist = saved_cb["y10_hist"]
                    s_hist_5y = s_hist[s_hist.index >= (s_hist.index[-1] - pd.DateOffset(years=5))]
                    fig_y.add_trace(go.Scatter(x=hist_5y.index, y=hist_5y.values, mode='lines', name=bank_data["name"], line=dict(color='#2E7BE6', width=3)))
                    fig_y.add_trace(go.Scatter(x=s_hist_5y.index, y=s_hist_5y.values, mode='lines', name=saved_cb["name"], line=dict(color='#F4A261', width=3)))
                else:
                    fig_y.add_trace(go.Scatter(x=hist_5y.index, y=hist_5y.values, mode='lines', name=bank_data["name"], line=dict(color='#2E7BE6', width=3)))

                fig_y.update_layout(
                    plot_bgcolor='white',
                    height=400,
                    margin=dict(l=0, r=0, t=20, b=0),
                    hovermode="x unified",
                    yaxis_title="Yield (%)"
                )
                st.plotly_chart(fig_y, use_container_width=True)
            else:
                st.info("10Y Yield data is not available for MAS via FRED.")

            # --- 5. News ---
            st.markdown("<div class='section-title'>V. Latest News</div>", unsafe_allow_html=True)
            cb_ticker_map = {
                "Federal Reserve":        "^TNX",
                "European Central Bank":  "EURUSD=X",
                "Bank of Japan":          "JPY=X",
                "Bank of England":        "GBPUSD=X",
                "MAS":                    "SGD=X",
            }
            cb_ticker = cb_ticker_map.get(bank, "^TNX")
            cb_news = fetch_news(cb_ticker)
            if cb_news:
                for item in cb_news:
                    st.markdown(
                        f'<div style="padding:10px 0; border-bottom:1px solid #F0F0F0;">'
                        f'<a href="{item["link"]}" target="_blank" style="font-size:0.95em; font-weight:600; color:#1e3a8a; text-decoration:none;">{item["title"]}</a>'
                        f'<div style="font-size:0.8em; color:#999; margin-top:3px;">{item["publisher"]} · {item["date"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.caption("No recent news available.")

        else:
            st.warning("Central bank data could not be loaded.")

    COMM_AXES = ["Price Momentum", "Supply Stability", "Demand Signal", "Price Level", "Market Trend"]

    comm_logic_descriptions = {
        "Price Momentum":   "3-month price change trend",
        "Supply Stability": "Inverse of 20-day price volatility",
        "Demand Signal":    "Current price vs 1-year average",
        "Price Level":      "Current price vs 52-week high",
        "Market Trend":     "1-year price performance",
    }

    with tab3:

        st.markdown(
            "<div class='company-header'>Commodities</div>",
            unsafe_allow_html=True
        )

        assets = ["WTI Crude Oil", "Gold", "Copper"]
        asset = st.selectbox("Select Commodity", assets)

        comm_data = fetch_commodity_data(asset)

        if comm_data:

            cm_btn1, cm_btn2 = st.columns(2)
            with cm_btn1:
                if st.button("Save", key="comm_save"):
                    st.session_state.saved_comm_data = comm_data
                    st.rerun()
            with cm_btn2:
                if st.button("Clear", key="comm_clear"):
                    st.session_state.saved_comm_data = None
                    st.rerun()

            # --- 1. Total Score ---
            st.markdown(f"""
            <div style="text-align:center; margin-top:40px; margin-bottom:30px;">
                <div style="font-size:14px; letter-spacing:2px; color:#666;">TOTAL SCORE</div>
                <div style="font-size:90px; font-weight:800; color:#2E7BE6;">
                    {comm_data['total']}
                    <span style="font-size:35px; color:#BBB;">/ 1000</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- 2. Radar + Score Cards ---
            cm_col_left, cm_col_right = st.columns([1.8, 1])

            with cm_col_left:
                st.markdown(
                    "<div style='font-size: 1.1em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 5px;'>I. Intelligence Radar</div>",
                    unsafe_allow_html=True
                )
                fig_cm = render_radar_chart(comm_data, st.session_state.saved_comm_data, COMM_AXES)
                st.plotly_chart(fig_cm, use_container_width=True)

            with cm_col_right:
                st.markdown(
                    "<div style='font-size: 0.9em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 15px; border-left: 3px solid #2E7BE6; padding-left: 8px;'>II. ANALYSIS SCORE METRICS</div>",
                    unsafe_allow_html=True
                )
                saved_cm = st.session_state.saved_comm_data
                for k in COMM_AXES:
                    v1 = comm_data["axes"].get(k, 0)
                    v2 = saved_cm["axes"].get(k, 0) if saved_cm else None
                    score_html = f'<span style="color: #2E7BE6;">{int(v1)}</span>'
                    if v2 is not None:
                        score_html += f' <span style="color: #ccc; font-size: 0.9em; font-weight:bold; margin: 0 6px;">vs</span> <span style="color: #F4A261;">{int(v2)}</span>'
                    st.markdown(f"""
                        <div style="background-color:#FFFFFF;padding:20px;border-radius:12px;margin-bottom:12px;border:1px solid #E0E0E0;border-left:8px solid #2E7BE6;box-shadow:2px 2px 5px rgba(0,0,0,0.07);">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                                <span style="font-size:1.2em;font-weight:800;color:#333;">{k}</span>
                                <span style="font-size:1.7em;font-weight:900;line-height:1;">{score_html}</span>
                            </div>
                            <p style="font-size:0.95em;color:#777;margin:0;line-height:1.3;font-weight:500;">{comm_logic_descriptions.get(k, '')}</p>
                        </div>
                    """, unsafe_allow_html=True)

            # --- 3. Snapshot ---
            st.markdown("<div class='section-title'>III. Market Snapshot</div>", unsafe_allow_html=True)

            def comm_snap(label, val, val2, fmt):
                v1_str = fmt.format(val) if val is not None else "N/A"
                h = f'<span style="color:#2E7BE6;">{v1_str}</span>'
                if val2 is not None:
                    h += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#F4A261;">{fmt.format(val2)}</span>'
                return f'<div class="card"><div style="font-size:11px; color:#999;">{label}</div><div style="font-size:22px; font-weight:900;">{h}</div></div>'

            cs1, cs2, cs3, cs4 = st.columns(4)
            cs1.markdown(comm_snap("PRICE",      comm_data["current_price"], saved_cm["current_price"] if saved_cm else None, "${:.2f}"),    unsafe_allow_html=True)
            cs2.markdown(comm_snap("52W HIGH",   comm_data["high_52w"],      saved_cm["high_52w"]      if saved_cm else None, "${:.2f}"),    unsafe_allow_html=True)
            cs3.markdown(comm_snap("YoY CHANGE", comm_data["yoy_change"],    saved_cm["yoy_change"]    if saved_cm else None, "{:.2f}%"),    unsafe_allow_html=True)
            cs4.markdown(comm_snap("20D VOL",    comm_data["vol_20d"],       saved_cm["vol_20d"]       if saved_cm else None, "{:.2f}%"),    unsafe_allow_html=True)

            # --- 4. Price History ---
            st.markdown("<div class='section-title'>IV. Price History (5Y)</div>", unsafe_allow_html=True)

            fig_cp = go.Figure()
            ph = comm_data["price_hist"]
            fig_cp.add_trace(go.Scatter(x=ph.index, y=ph.values, mode='lines', name=asset, line=dict(color='#2E7BE6', width=3)))
            if saved_cm and saved_cm.get("price_hist") is not None:
                sph = saved_cm["price_hist"]
                fig_cp.add_trace(go.Scatter(x=sph.index, y=sph.values, mode='lines', name=saved_cm["name"], line=dict(color='#F4A261', width=3)))
            fig_cp.update_layout(
                plot_bgcolor='white',
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                hovermode="x unified",
                yaxis_title="Price (USD)"
            )
            st.plotly_chart(fig_cp, use_container_width=True)

            # --- 5. News ---
            st.markdown("<div class='section-title'>V. Latest News</div>", unsafe_allow_html=True)
            comm_ticker_map = {"WTI Crude Oil": "CL=F", "Gold": "GC=F", "Copper": "HG=F"}
            comm_ticker = comm_ticker_map.get(asset, "CL=F")
            comm_news = fetch_news(comm_ticker)
            if comm_news:
                for item in comm_news:
                    st.markdown(
                        f'<div style="padding:10px 0; border-bottom:1px solid #F0F0F0;">'
                        f'<a href="{item["link"]}" target="_blank" style="font-size:0.95em; font-weight:600; color:#1e3a8a; text-decoration:none;">{item["title"]}</a>'
                        f'<div style="font-size:0.8em; color:#999; margin-top:3px;">{item["publisher"]} · {item["date"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.caption("No recent news available.")

        else:
            st.warning("Commodity data could not be loaded.")


# 💡 ここからは if data: ブロックの外側。一番左に配置
if __name__ == "__main__":
    main()