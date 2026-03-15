# app.py
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import streamlit_authenticator as stauth
from ui_components import inject_css, render_radar_chart
from data_logic import fetch_data, fetch_central_bank_data, fetch_commodity_data, fetch_news, compute_hist_scores_commodity, compute_hist_scores_sgx, compute_hist_scores_cb
from pdf_report import generate_pdf
import json
import os

APP_TITLE = "FRS-1000 — Scoring Platform"

def render_pricing_section():
    """全タブ共通の料金プラン比較表"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center; padding:50px 20px; background:#FFFFFF; border-radius:24px; border:1px solid #e2e8f0; box-shadow:0 10px 25px rgba(0,0,0,0.05); margin-top:40px; font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">

<div style="margin-bottom:10px;">
<span style="font-size:3em; font-weight:900; color:#2E7BE6; letter-spacing:-2px;">FRS-1000</span>
</div>
<p style="font-size:1.05em; color:#64748b; margin-bottom:40px;">Choose the plan that fits your needs.</p>

<div style="display:flex; justify-content:center; gap:20px; flex-wrap:wrap; margin-bottom:40px; align-items:stretch;">

<!-- Starter -->
<div style="background:#f8fafc; border:2px solid #e2e8f0; border-radius:16px; padding:30px 25px; width:260px; text-align:center; display:flex; flex-direction:column;">
<div style="font-size:0.75em; font-weight:700; color:#94a3b8; letter-spacing:1px; text-transform:uppercase;">Starter</div>
<div style="font-size:2em; font-weight:900; color:#1e3a8a; margin:10px 0;">S$500<span style="font-size:0.4em; color:#64748b;"> /mo</span></div>
<div style="font-size:0.8em; color:#64748b; line-height:2; text-align:left; padding:15px 10px; border-top:1px solid #e2e8f0; flex:1;">
<span style="color:#10b981;">&#10003;</span> 1 User Account<br>
<span style="color:#10b981;">&#10003;</span> SGX Top 30 Stocks<br>
<span style="color:#10b981;">&#10003;</span> 5 Central Banks<br>
<span style="color:#10b981;">&#10003;</span> 3 Commodities<br>
<span style="color:#10b981;">&#10003;</span> PDF & CSV Export<br>
<span style="color:#10b981;">&#10003;</span> Score History & Rankings<br>
<span style="color:#10b981;">&#10003;</span> Daily Score Alerts<br>
<span style="color:#ef4444;">&#10007;</span> White-label PDF<br>
<span style="color:#ef4444;">&#10007;</span> API Access<br>
<span style="color:#ef4444;">&#10007;</span> Custom Scoring Model
</div>
</div>

<!-- Professional -->
<div style="background:#fff; border:3px solid #2E7BE6; border-radius:16px; padding:30px 25px; width:260px; text-align:center; position:relative; display:flex; flex-direction:column;">
<div style="position:absolute; top:-12px; left:50%; transform:translateX(-50%); background:#2E7BE6; color:#fff; font-size:0.7em; font-weight:700; padding:3px 16px; border-radius:20px; letter-spacing:1px;">POPULAR</div>
<div style="font-size:0.75em; font-weight:700; color:#2E7BE6; letter-spacing:1px; text-transform:uppercase;">Professional</div>
<div style="font-size:2em; font-weight:900; color:#1e3a8a; margin:10px 0;">S$1,500<span style="font-size:0.4em; color:#64748b;"> /mo</span></div>
<div style="font-size:0.8em; color:#64748b; line-height:2; text-align:left; padding:15px 10px; border-top:1px solid #e2e8f0; flex:1;">
<span style="color:#10b981;">&#10003;</span> Up to 5 Users<br>
<span style="color:#10b981;">&#10003;</span> All SGX-Listed Stocks<br>
<span style="color:#10b981;">&#10003;</span> 20+ Central Banks<br>
<span style="color:#10b981;">&#10003;</span> 10+ Commodities<br>
<span style="color:#10b981;">&#10003;</span> PDF & CSV Export<br>
<span style="color:#10b981;">&#10003;</span> Score History & Rankings<br>
<span style="color:#10b981;">&#10003;</span> Daily Score Alerts<br>
<span style="color:#10b981;">&#10003;</span> White-label PDF<br>
<span style="color:#ef4444;">&#10007;</span> API Access<br>
<span style="color:#ef4444;">&#10007;</span> Custom Scoring Model
</div>
</div>

<!-- Enterprise -->
<div style="background:#f8fafc; border:2px solid #e2e8f0; border-radius:16px; padding:30px 25px; width:260px; text-align:center; display:flex; flex-direction:column;">
<div style="font-size:0.75em; font-weight:700; color:#94a3b8; letter-spacing:1px; text-transform:uppercase;">Enterprise</div>
<div style="font-size:2em; font-weight:900; color:#1e3a8a; margin:10px 0;">S$5,000<span style="font-size:0.4em; color:#64748b;"> /mo</span></div>
<div style="font-size:0.8em; color:#64748b; line-height:2; text-align:left; padding:15px 10px; border-top:1px solid #e2e8f0; flex:1;">
<span style="color:#10b981;">&#10003;</span> Unlimited Users<br>
<span style="color:#10b981;">&#10003;</span> All SGX-Listed Stocks<br>
<span style="color:#10b981;">&#10003;</span> 20+ Central Banks<br>
<span style="color:#10b981;">&#10003;</span> 20+ Commodities<br>
<span style="color:#10b981;">&#10003;</span> PDF & CSV Export<br>
<span style="color:#10b981;">&#10003;</span> Score History & Rankings<br>
<span style="color:#10b981;">&#10003;</span> Daily Score Alerts<br>
<span style="color:#10b981;">&#10003;</span> White-label PDF<br>
<span style="color:#10b981;">&#10003;</span> API Access<br>
<span style="color:#10b981;">&#10003;</span> Custom Scoring Model
</div>
</div>

</div>

<div style="margin-bottom:30px;">
<div style="font-size:0.8em; color:#94a3b8; font-weight:700; letter-spacing:1px; text-transform:uppercase;">Founding Member Slots</div>
<div style="font-size:1.3em; font-weight:800; color:#10b981;">5 Remaining</div>
</div>

<div style="background:#1e3a8a; color:#FFFFFF; padding:16px 50px; font-size:1.2em; font-weight:900; border-radius:50px; display:inline-block; cursor:pointer; box-shadow:0 10px 20px rgba(30,58,138,0.2); text-transform:uppercase; letter-spacing:1px;">
Get Started
</div>

<div style="margin-top:20px; padding:16px; background:#f8fafc; border-radius:10px; font-size:0.7em; color:#64748b; line-height:1.6; text-align:left; border-left:4px solid #2E7BE6; max-width:600px; margin-left:auto; margin-right:auto;">
<strong>DISCLAIMER:</strong> This service is for informational purposes only and does not constitute investment advice, recommendation, or solicitation. All investment decisions should be made at the user's own discretion and risk.
</div>

</div>
""", unsafe_allow_html=True)

SCORES_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "scores_history.json")

def _load_scores_history():
    """scores_history.json を読み込んで返す"""
    if os.path.exists(SCORES_HISTORY_FILE):
        with open(SCORES_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def render_score_delta(asset_name: str, current_total: int):
    """前日比のスコア変動を表示する"""
    history = _load_scores_history()
    if not history:
        return
    dates = sorted(history.keys(), reverse=True)
    prev_score = None
    for d in dates:
        s = history[d].get(asset_name)
        if s is not None:
            prev_score = s
            break
    if prev_score is None:
        return
    delta = current_total - prev_score
    if delta > 0:
        color, arrow = "#10b981", "&#9650;"  # green up
    elif delta < 0:
        color, arrow = "#ef4444", "&#9660;"  # red down
    else:
        color, arrow = "#94a3b8", "&#9644;"  # gray flat
    st.markdown(
        f'<div style="text-align:center; font-size:1.1em; font-weight:700; color:{color}; margin-top:-8px; margin-bottom:10px;">'
        f'{arrow} {delta:+d} from last record ({prev_score})'
        f'</div>',
        unsafe_allow_html=True
    )

def generate_excel(data: dict, axes_labels: list, tab_name: str,
                   logic_descriptions: dict = None, snapshot: dict = None) -> bytes:
    """スコアデータをCSVバイトとして返す（依存ゼロ）"""
    rows = []
    for k in axes_labels:
        desc = logic_descriptions.get(k, "") if logic_descriptions else ""
        rows.append({"Axis": k, "Score": int(data["axes"].get(k, 0)), "Description": desc})
    rows.append({"Axis": "TOTAL", "Score": int(data.get("total", 0)), "Description": ""})
    if snapshot:
        rows.append({"Axis": "", "Score": "", "Description": ""})
        for label, value in snapshot.items():
            rows.append({"Axis": label, "Score": value, "Description": ""})
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode("utf-8")

def render_daily_score_tracker(asset_name: str):
    """scores_history.json からデイリースコア推移チャートを表示する"""
    history = _load_scores_history()
    if not history:
        st.caption("No daily score records yet.")
        return

    dates = sorted(history.keys())
    values = []
    valid_dates = []
    for d in dates:
        score = history[d].get(asset_name)
        if score is not None:
            valid_dates.append(d)
            values.append(score)

    if len(valid_dates) < 2:
        st.caption(f"Not enough daily records for {asset_name} yet (need at least 2 days).")
        return

    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(
        x=valid_dates, y=values, mode='lines+markers',
        name=asset_name,
        line=dict(color='#2E7BE6', width=2),
        marker=dict(size=5),
        fill='tozeroy', fillcolor='rgba(46,123,230,0.05)'
    ))
    fig_daily.update_layout(
        yaxis=dict(range=[0, 1000], title="Score"),
        height=250,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor='white',
        hovermode="x unified",
        clickmode='none',
        dragmode=False,
    )
    st.plotly_chart(fig_daily, use_container_width=True, config={"displayModeBar": False})

# 冒頭 9行目付近
AXES = [
    "Entry Edge",
    "Stability Profile",
    "Durability",
    "Cashflow Quality",
    "Shareholder Return"
]

st.set_page_config(page_title=APP_TITLE, layout="wide")

def main():
    #inject_css()
    st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    .viewerBadge_container__r5tak { display: none !important; }
    [data-testid="stActionButtonIcon"] { display: none !important; }
    a[href*="github.com"] img { display: none !important; }
    .styles_viewerBadge__CvC9N { display: none !important; }
    #MainMenu { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    if "saved_data" not in st.session_state:
        st.session_state.saved_data = None
    if "saved_cb_data" not in st.session_state:
        st.session_state.saved_cb_data = None
    if "saved_comm_data" not in st.session_state:
        st.session_state.saved_comm_data = None

    # White-label: PDF に社名を入れる
    with st.sidebar:
        st.markdown("**PDF White Label**")
        company_name = st.text_input("Company name for PDF", value="", placeholder="e.g. ABC Capital Pte Ltd", key="wl_company")

    # --- タブ ---
    tab1, tab2, tab3, tab4 = st.tabs(["SGX", "Central Banks", "Commodities", "Rankings"])

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
            DUMMY_AXES = {"Entry Edge": 100, "Stability Profile": 100, "Durability": 100, "Cashflow Quality": 100, "Shareholder Return": 100}
            data = {"axes": DUMMY_AXES, "total": 500, "name": name, "price_hist": None, "current_price": 0, "pe": "N/A", "market_cap": 0}
            data["_loading"] = True

        if data:

            if data.get("_loading"):
                st.warning("Stock data is currently unavailable (Yahoo Finance rate limit). Scores will load automatically — please check back later.")

            # ロジック解説（PDF生成とスコアカード両方で使用）
            logic_descriptions = {
                "Entry Edge": "Momentum (Price vs Avg) x Valuation (PER)",
                "Stability Profile": "Market Volatility x Market Capitalization",
                "Durability": "Price Resilience x Debt-to-Equity Ratio",
                "Cashflow Quality": "Capital Efficiency (ROE)",
                "Shareholder Return": "Long-term Growth x Dividend Yield"
            }

            sgx_snapshot = {
                "Price": f"{data.get('current_price', 0):.2f}",
                "P/E Ratio": f"{data.get('pe', 'N/A')}",
                "Market Cap": f"{data.get('market_cap', 0)/1e9:.1f}B" if data.get('market_cap') else "N/A",
            }

            col_btn1, col_btn2, col_btn3, col_btn4, col_btn_rest = st.columns([1, 1, 1.5, 1.5, 5.5])

            with col_btn1:
                save_it = st.button("Save")

            with col_btn2:
                clear_it = st.button("Clear")

            with col_btn3:
                sgx_pdf = generate_pdf(data, AXES, "SGX", logic_descriptions, sgx_snapshot, company_name)
                st.download_button("PDF", sgx_pdf, file_name=f"FRS1000_{name.replace(' ', '_')}.pdf", mime="application/pdf")

            with col_btn4:
                sgx_xlsx = generate_excel(data, AXES, "SGX", logic_descriptions, sgx_snapshot)
                st.download_button("Excel", sgx_xlsx, file_name=f"FRS1000_{name.replace(' ', '_')}.csv", mime="text/csv")

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

            render_score_delta(name, display_total)

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

                    v1 = data["axes"].get(k, 0)
                    v2 = st.session_state.saved_data["axes"].get(k, 0) if st.session_state.saved_data else None

                    display_label = oil_labels[i] if is_oil else k
                    desc_text = oil_descriptions.get(display_label, "") if is_oil else logic_descriptions.get(k, "")

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
                    fig_p.add_trace(go.Scatter(x=y1.index, y=y1.values, mode='lines', name=name, line=dict(color='#2E7BE6', width=3)))
                    fig_p.add_trace(go.Scatter(x=y2.index, y=y2.values, mode='lines', name=s_data['name'], line=dict(color='#F4A261', width=3)))
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

            # Score History
            st.markdown("<div class='section-title'>V-B. Score History</div>", unsafe_allow_html=True)
            hist_s = compute_hist_scores_sgx(data.get('price_hist'))
            if hist_s is not None and len(hist_s) > 0:
                fig_hs = go.Figure()
                fig_hs.add_trace(go.Scatter(x=hist_s.index, y=hist_s.values, mode='lines', name=name, line=dict(color='#2E7BE6', width=2), fill='tozeroy', fillcolor='rgba(46,123,230,0.05)'))
                if st.session_state.saved_data and st.session_state.saved_data.get('price_hist') is not None:
                    saved_hs = compute_hist_scores_sgx(st.session_state.saved_data['price_hist'])
                    if saved_hs is not None:
                        fig_hs.add_trace(go.Scatter(x=saved_hs.index, y=saved_hs.values, mode='lines', name=st.session_state.saved_data['name'], line=dict(color='#F4A261', width=2)))
                fig_hs.update_layout(yaxis=dict(range=[0,1000], title="Score"), height=280, margin=dict(l=0,r=0,t=10,b=0), plot_bgcolor='white', hovermode="x unified", clickmode='none', dragmode=False)
                st.plotly_chart(fig_hs, use_container_width=True, config={"displayModeBar": False})
            else:
                st.caption("Score history unavailable — insufficient price data.")

            # V-C. Daily Score Tracker
            st.markdown("<div class='section-title'>V-C. Daily Score Tracker</div>", unsafe_allow_html=True)
            render_daily_score_tracker(name)

            # 4. Snapshot（比較対応版）
            st.markdown("<div class='section-title'>VI. Snapshot Comparison</div>", unsafe_allow_html=True)

            s1, s2, s3 = st.columns(3)

            saved = st.session_state.saved_data  # 比較対象データ

            # --- PRICE ---
            p1 = data.get("current_price", 0)
            p2 = saved.get("current_price") if saved else None

            p_html = f'<span style="color:#2E7BE6;">{p1:.2f}</span>'
            if p2 is not None:
                p_html += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#F4A261;">{p2:.2f}</span>'

            s1.markdown(
                f'<div class="card"><div style="font-size:11px; color:#999;">PRICE</div><div style="font-size:22px; font-weight:900;">{p_html}</div></div>',
                unsafe_allow_html=True
            )        
            # --- P/E RATIO ---
            pe1 = data.get("pe", "N/A")
            pe1_txt = f"{pe1:.1f}" if isinstance(pe1, (int, float)) and pe1 != 0 else "N/A"
            pe2 = saved.get("pe") if saved else None
            pe2_txt = f"{pe2:.1f}" if isinstance(pe2, (int, float)) and pe2 != 0 else "N/A"

            pe_html = f'<span style="color:#2E7BE6;">{pe1_txt}</span>'
            if saved:
                pe_html += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#F4A261;">{pe2_txt}</span>'

            s2.markdown(
                f'<div class="card"><div style="font-size:11px; color:#999;">P/E RATIO</div><div style="font-size:22px; font-weight:900;">{pe_html}</div></div>',
                unsafe_allow_html=True
            )

            # --- MARKET CAP ---
            cap1 = data.get("market_cap", 0)
            cap2 = saved.get("market_cap", 0) if saved else None

            cap_html = f'<span style="color:#2E7BE6;">{cap1/1e9:.1f}B</span>'
            if cap2 is not None:
                cap2_txt = f"{cap2/1e9:.1f}B" if cap2 > 0 else "N/A"
                cap_html += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#F4A261;">{cap2_txt}</span>'

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

            render_pricing_section()

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
            "MAS",
            "Federal Reserve",
            "European Central Bank",
            "Bank of Japan",
            "Bank of England",
        ]

        bank = st.selectbox("Select Central Bank", banks)

        # FREDデータ取得
        bank_data = fetch_central_bank_data(bank)

        if bank_data:

            cb_snapshot = {
                "10Y Yield": f"{bank_data['y10']:.2f}%" if bank_data.get('y10') is not None else "N/A",
                "CPI YoY": f"{bank_data['cpi_yoy']:.2f}%",
                "Unemployment": f"{bank_data['unemployment']:.2f}%",
                "M2 YoY": f"{bank_data['m2_yoy']:.2f}%" if bank_data.get('m2_yoy') is not None else "N/A",
                "Yield Curve": f"{bank_data['curve']:.2f}%" if bank_data.get('curve') is not None else "N/A",
            }

            cb_btn1, cb_btn2, cb_btn3, cb_btn4, _ = st.columns([1, 1, 1.5, 1.5, 5.5])
            with cb_btn1:
                cb_save = st.button("Save", key="cb_save")
            with cb_btn2:
                cb_clear = st.button("Clear", key="cb_clear")
            with cb_btn3:
                cb_pdf = generate_pdf(bank_data, CB_AXES, "Central Banks", cb_logic_descriptions, cb_snapshot, company_name)
                st.download_button("PDF", cb_pdf, file_name=f"FRS1000_{bank.replace(' ', '_')}.pdf", mime="application/pdf", key="cb_pdf")
            with cb_btn4:
                cb_xlsx = generate_excel(bank_data, CB_AXES, "Central Banks", cb_logic_descriptions, cb_snapshot)
                st.download_button("Excel", cb_xlsx, file_name=f"FRS1000_{bank.replace(' ', '_')}.csv", mime="text/csv", key="cb_xlsx")

            if cb_save:
                st.session_state.saved_cb_data = bank_data
                st.rerun()
            if cb_clear:
                st.session_state.saved_cb_data = None
                st.rerun()

            # --- 1. Total Score ---
            display_total_cb = int(bank_data.get("total", 0))

            st.markdown(f"""
            <div style="text-align:center; margin-top:4px; margin-bottom:10px;">
                <div style="font-size:14px; letter-spacing:2px; color:#666;">TOTAL SCORE</div>
                <div style="font-size:90px; font-weight:800; color:#2E7BE6; line-height:1;">
                    {display_total_cb}
                    <span style="font-size:35px; color:#BBB;">/ 1000</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            render_score_delta(bank, display_total_cb)

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
                    yaxis_title="Yield (%)",
                    clickmode='none',
                    dragmode=False
                )
                st.plotly_chart(fig_y, use_container_width=True)
            else:
                st.info("10Y Yield data is not available for MAS via FRED.")

            # --- 4-B. Score History ---
            st.markdown("<div class='section-title'>IV-B. Score History</div>", unsafe_allow_html=True)
            hist_cb = compute_hist_scores_cb(bank_data.get('y10_hist'))
            if hist_cb is not None and len(hist_cb) > 0:
                fig_hcb = go.Figure()
                fig_hcb.add_trace(go.Scatter(x=hist_cb.index, y=hist_cb.values, mode='lines', name=bank, line=dict(color='#2E7BE6', width=2), fill='tozeroy', fillcolor='rgba(46,123,230,0.05)'))
                if saved_cb and saved_cb.get('y10_hist') is not None:
                    saved_hcb = compute_hist_scores_cb(saved_cb['y10_hist'])
                    if saved_hcb is not None:
                        fig_hcb.add_trace(go.Scatter(x=saved_hcb.index, y=saved_hcb.values, mode='lines', name=saved_cb['name'], line=dict(color='#F4A261', width=2)))
                fig_hcb.update_layout(yaxis=dict(range=[0,1000], title="Score"), height=280, margin=dict(l=0,r=0,t=10,b=0), plot_bgcolor='white', hovermode="x unified", clickmode='none', dragmode=False)
                st.plotly_chart(fig_hcb, use_container_width=True, config={"displayModeBar": False})
            else:
                st.caption("Score history unavailable — insufficient yield data.")

            # --- 4-C. Daily Score Tracker ---
            st.markdown("<div class='section-title'>IV-C. Daily Score Tracker</div>", unsafe_allow_html=True)
            render_daily_score_tracker(bank)

            # --- 5. News ---
            st.markdown("<div class='section-title'>V. Latest News</div>", unsafe_allow_html=True)
            cb_ticker_map = {
                "Federal Reserve":        "TLT",
                "European Central Bank":  "EZU",
                "Bank of Japan":          "EWJ",
                "Bank of England":        "EWU",
                "MAS":                    "EWS",
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

            with st.expander("How does the scoring work?"):
                st.markdown("### FRS-1000 Scoring Framework")
                st.markdown("Each central bank is scored across **5 axes**, each worth up to **200 points** (max total: **1,000 points**).")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown("""
**How to read the score**
- **800–1000** — Strong macro fundamentals
- **600–799** — Stable, with some areas to watch
- **400–599** — Mixed signals, warrants deeper analysis
- **Below 400** — Significant macro weaknesses

**How to use the comparison**
Press **Save** on any central bank, then switch to another.
The radar chart and score cards will show both side-by-side,
making it easy to compare macro environments across economies.
""")
                with col_m2:
                    st.markdown("""
**Data sources & update frequency**
- Federal Reserve & Bank of England: FRED (refreshed every 24 hours)
- European Central Bank: ECB SDMX API (refreshed every 24 hours)
- Bank of Japan: FRED + World Bank (refreshed every 24 hours)
- MAS: World Bank + FRED (refreshed every 24 hours)

**Premium Plan**
The current version covers 5 major central banks for demonstration.
Subscribers get access to **20+ central banks** with real-time,
institutional-grade data and full historical scoring.
""")
                st.caption("This tool is for informational and screening purposes only. It does not constitute investment advice.")

            render_pricing_section()

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

            comm_snapshot = {
                "Price": f"${comm_data['current_price']:.2f}",
                "52W High": f"${comm_data['high_52w']:.2f}",
                "YoY Change": f"{comm_data['yoy_change']:.2f}%",
                "20D Volatility": f"{comm_data['vol_20d']:.2f}%",
            }

            cm_btn1, cm_btn2, cm_btn3, cm_btn4, _ = st.columns([1, 1, 1.5, 1.5, 5.5])
            with cm_btn1:
                if st.button("Save", key="comm_save"):
                    st.session_state.saved_comm_data = comm_data
                    st.rerun()
            with cm_btn2:
                if st.button("Clear", key="comm_clear"):
                    st.session_state.saved_comm_data = None
                    st.rerun()
            with cm_btn3:
                comm_pdf = generate_pdf(comm_data, COMM_AXES, "Commodities", comm_logic_descriptions, comm_snapshot, company_name)
                st.download_button("PDF", comm_pdf, file_name=f"FRS1000_{asset.replace(' ', '_')}.pdf", mime="application/pdf", key="comm_pdf")
            with cm_btn4:
                comm_xlsx = generate_excel(comm_data, COMM_AXES, "Commodities", comm_logic_descriptions, comm_snapshot)
                st.download_button("Excel", comm_xlsx, file_name=f"FRS1000_{asset.replace(' ', '_')}.csv", mime="text/csv", key="comm_xlsx")

            # --- 1. Total Score ---
            st.markdown(f"""
            <div style="text-align:center; margin-top:4px; margin-bottom:10px;">
                <div style="font-size:14px; letter-spacing:2px; color:#666;">TOTAL SCORE</div>
                <div style="font-size:90px; font-weight:800; color:#2E7BE6; line-height:1;">
                    {comm_data['total']}
                    <span style="font-size:35px; color:#BBB;">/ 1000</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            render_score_delta(asset, int(comm_data['total']))

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
                yaxis_title="Price (USD)",
                clickmode='none',
                dragmode=False
            )
            st.plotly_chart(fig_cp, use_container_width=True)

            # Score History
            st.markdown("<div class='section-title'>IV-B. Score History</div>", unsafe_allow_html=True)
            hist_c = compute_hist_scores_commodity(comm_data.get('price_hist'))
            if hist_c is not None and len(hist_c) > 0:
                fig_hc = go.Figure()
                fig_hc.add_trace(go.Scatter(x=hist_c.index, y=hist_c.values, mode='lines', name=asset, line=dict(color='#2E7BE6', width=2), fill='tozeroy', fillcolor='rgba(46,123,230,0.05)'))
                if saved_cm and saved_cm.get('price_hist') is not None:
                    saved_hc = compute_hist_scores_commodity(saved_cm['price_hist'])
                    if saved_hc is not None:
                        fig_hc.add_trace(go.Scatter(x=saved_hc.index, y=saved_hc.values, mode='lines', name=saved_cm['name'], line=dict(color='#F4A261', width=2)))
                fig_hc.update_layout(yaxis=dict(range=[0,1000], title="Score"), height=280, margin=dict(l=0,r=0,t=10,b=0), plot_bgcolor='white', hovermode="x unified", clickmode='none', dragmode=False)
                st.plotly_chart(fig_hc, use_container_width=True, config={"displayModeBar": False})
            else:
                st.caption("Score history unavailable — insufficient price data.")

            # IV-C. Daily Score Tracker
            st.markdown("<div class='section-title'>IV-C. Daily Score Tracker</div>", unsafe_allow_html=True)
            render_daily_score_tracker(asset)

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

            with st.expander("How does the scoring work?"):
                st.markdown("### FRS-1000 Scoring Framework")
                st.markdown("Each commodity is scored across **5 axes**, each worth up to **200 points** (max total: **1,000 points**).")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown("""
**How to read the score**
- **800–1000** — Strong momentum and stable supply
- **600–799** — Solid, with some areas to watch
- **400–599** — Mixed signals, warrants deeper analysis
- **Below 400** — Significant weakness or high volatility

**How to use the comparison**
Press **Save** on any commodity, then switch to another.
The radar chart and score cards will show both side-by-side,
making it easy to compare commodities across multiple dimensions.
""")
                with col_m2:
                    st.markdown("""
**Data sources & update frequency**
- Commodity futures data: Yahoo Finance (refreshed every hour)

**Premium Plan**
The current version covers 3 commodities for demonstration.
Subscribers get access to **20+ commodities** including silver,
natural gas, agricultural products, and more with real-time data.
""")
                st.caption("This tool is for informational and screening purposes only. It does not constitute investment advice.")

            render_pricing_section()

        else:
            st.warning("Commodity data could not be loaded.")

    # --- Rankings TAB ---
    with tab4:
        st.markdown(
            "<div style='font-size:1.5em; font-weight:900; color:#1e3a8a; margin-bottom:20px;'>All Assets Ranking</div>",
            unsafe_allow_html=True
        )

        # Collect all scores
        ranking_rows = []

        # SGX
        sgx_stocks = [
            {"name": "DBS Group", "symbol": "D05"},
            {"name": "Singtel", "symbol": "Z74"},
            {"name": "OCBC Bank", "symbol": "O39"},
            {"name": "Keppel Ltd", "symbol": "BN4"},
            {"name": "CapitaLand Investment", "symbol": "9CI"},
        ]
        for s in sgx_stocks:
            d = fetch_data(s["symbol"], s["name"])
            if d and not d.get("_loading"):
                ranking_rows.append({"Asset": s["name"], "Category": "SGX", "Score": int(d["total"])})

        # Central Banks
        for b in ["MAS", "Federal Reserve", "European Central Bank", "Bank of Japan", "Bank of England"]:
            d = fetch_central_bank_data(b)
            if d:
                ranking_rows.append({"Asset": b, "Category": "Central Bank", "Score": int(d["total"])})

        # Commodities
        for c in ["WTI Crude Oil", "Gold", "Copper"]:
            d = fetch_commodity_data(c)
            if d:
                ranking_rows.append({"Asset": c, "Category": "Commodity", "Score": int(d["total"])})

        if ranking_rows:
            df_rank = pd.DataFrame(ranking_rows).sort_values("Score", ascending=False).reset_index(drop=True)
            df_rank.index = df_rank.index + 1
            df_rank.index.name = "Rank"

            # Delta from daily history
            history = _load_scores_history()
            dates = sorted(history.keys(), reverse=True) if history else []
            deltas = []
            for _, row in df_rank.iterrows():
                prev = None
                for dt in dates:
                    prev = history[dt].get(row["Asset"])
                    if prev is not None:
                        break
                if prev is not None:
                    d_val = row["Score"] - prev
                    deltas.append(f"{d_val:+d}")
                else:
                    deltas.append("-")
            df_rank["Change"] = deltas

            # Render as styled cards
            for idx, row in df_rank.iterrows():
                score = row["Score"]
                if score >= 800:
                    bar_color = "#10b981"
                elif score >= 600:
                    bar_color = "#2E7BE6"
                elif score >= 400:
                    bar_color = "#f59e0b"
                else:
                    bar_color = "#ef4444"

                change_str = row["Change"]
                if change_str != "-":
                    val = int(change_str)
                    if val > 0:
                        change_html = f'<span style="color:#10b981; font-weight:700;">&#9650; {change_str}</span>'
                    elif val < 0:
                        change_html = f'<span style="color:#ef4444; font-weight:700;">&#9660; {change_str}</span>'
                    else:
                        change_html = f'<span style="color:#94a3b8; font-weight:700;">&#9644; 0</span>'
                else:
                    change_html = '<span style="color:#94a3b8;">-</span>'

                cat_colors = {"SGX": "#2E7BE6", "Central Bank": "#8b5cf6", "Commodity": "#f59e0b"}
                cat_color = cat_colors.get(row["Category"], "#666")

                st.markdown(f"""
                <div style="display:flex; align-items:center; padding:14px 20px; background:#fff; border-radius:12px; margin-bottom:8px; border:1px solid #e2e8f0; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
                    <div style="font-size:1.4em; font-weight:900; color:#94a3b8; width:40px;">#{idx}</div>
                    <div style="flex:1;">
                        <div style="font-size:1.05em; font-weight:700; color:#1e293b;">{row['Asset']}</div>
                        <span style="font-size:0.75em; background:{cat_color}; color:#fff; padding:2px 8px; border-radius:20px;">{row['Category']}</span>
                    </div>
                    <div style="text-align:right; margin-right:20px;">
                        {change_html}
                    </div>
                    <div style="text-align:right; min-width:80px;">
                        <div style="font-size:1.5em; font-weight:900; color:{bar_color};">{score}</div>
                        <div style="background:#f1f5f9; border-radius:4px; height:6px; width:80px; margin-top:4px;">
                            <div style="background:{bar_color}; height:6px; border-radius:4px; width:{score/10}%;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Loading scores... please wait a moment and refresh.")


# --- Authentication ---
def _build_credentials():
    """Streamlit secrets からユーザー情報を構築する"""
    users = st.secrets.get("auth_users", {})
    creds = {"usernames": {}}
    for username, info in users.items():
        creds["usernames"][username] = {
            "email": info.get("email", ""),
            "first_name": info.get("first_name", ""),
            "last_name": info.get("last_name", ""),
            "password": info.get("password", ""),
            "logged_in": False,
            "failed_login_attempts": 0,
            "roles": ["viewer"],
        }
    return creds

if __name__ == "__main__":
    credentials = _build_credentials()

    if not credentials["usernames"]:
        # auth_users が未設定ならログインなしで動かす（開発用）
        main()
    else:
        authenticator = stauth.Authenticate(
            credentials,
            st.secrets["auth_cookie"]["name"],
            st.secrets["auth_cookie"]["key"],
            st.secrets["auth_cookie"]["expiry_days"],
        )

        try:
            authenticator.login()
        except Exception as e:
            st.error(e)

        if st.session_state.get("authentication_status"):
            with st.sidebar:
                st.markdown(f"**{st.session_state.get('name', '')}**")
                authenticator.logout("Logout")
            main()
        elif st.session_state.get("authentication_status") is False:
            st.error("Username or password is incorrect.")
        else:
            st.markdown("""
            <div style="text-align:center; margin-top:80px;">
                <div style="font-size:3em; font-weight:900; color:#2E7BE6; letter-spacing:-2px;">FRS-1000</div>
                <p style="color:#64748b; margin-top:10px;">Please log in to access the scoring dashboard.</p>
            </div>
            """, unsafe_allow_html=True)