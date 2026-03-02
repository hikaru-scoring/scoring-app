import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from ui_components import inject_css, render_radar_chart
from data_logic import fetch_data

APP_TITLE = "FRS-1000 — SGX Dashboard"
# 冒頭 9行目付近
AXES = ["Future Focus", "Market Position", "Financial Strength", "Cashflow Quality", "People"]

def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    inject_css()

    if "saved_data" not in st.session_state:
        st.session_state.saved_data = None

    # --- 🚀 厳選5資産固定ロジック（Global Macro版） ---
    top_5 = [
        {"name": "US 10Y Yield", "symbol": "^TNX"},
        {"name": "Copper (Industrial)", "symbol": "HG=F"},
        {"name": "WTI Crude Oil", "symbol": "CL=F"},
    ]
    
    options = [f"{s['name']} ({s['symbol']})" for s in top_5]
    target = st.selectbox("Select Asset", options)
    
    # 選択した銘柄の名前とシンボルを抽出
    name = target.rsplit(" (", 1)[0]
    symbol = next(s['symbol'] for s in top_5 if s['name'] == name)

    st.markdown(f'<div class="company-header">{name}</div>', unsafe_allow_html=True)

    # 比較ボタン
    c1, c2, c3, _ = st.columns([1.2, 1.2, 1.5, 3])
    save_it = c1.button("💾 SAVE COMPANY")
    clear_it = c2.button("🗑️ CLEAR")
    compare_oil = c3.button("🛢️ COMPARE WITH OIL")
    
    # 2. メインデータの取得（デバッグ版に差し替え）
    try:
        if symbol == "MAS":
            from data_logic import fetch_mas_logic
            data = fetch_mas_logic()
            
            # 🔴 もし表示されない（Noneが返る）場合、原因を画面に出す
            if data is None:
                st.warning("⚠️ MAS data logic failed. Diagnostic mode activated.")
                import requests
                # MAS_RESOURCESはdata_logicから直接インポート
                from data_logic import MAS_RESOURCES
                
                # 生データを1件だけ取って構造を確認する
                test_url = f"https://eservices.mas.gov.sg/api/action/datastore/search.json?resource_id={MAS_RESOURCES['SGS_YIELD']}&limit=1"
                raw_res = requests.get(test_url).json()
                
                st.write("--- [API DEBUG INFO] ---")
                st.write("Target URL:", test_url)
                st.json(raw_res) # 👈 これでJSONの中身が画面に表示されます
        else:
            data = fetch_data(symbol, name)
            
    except Exception as e:
        st.error(f"Logic Error: {e}")
        st.stop()

    if data:
        # 3. ボタンごとの動作設定
        if save_it: 
            st.session_state.saved_data = data
            st.rerun()
        if clear_it: 
            st.session_state.saved_data = None
            st.rerun()
        if compare_oil:
            # data_logic.pyから原油データを呼んでくる
            from data_logic import fetch_oil_data 
            st.session_state.saved_data = fetch_oil_data()
            st.rerun()

        # --- 🚀 1. 看板（ラベル）を銘柄ごとに自動決定 ---
        if any(x in name for x in ["Copper", "Oil", "WTI"]):
            current_axes = ["Industrial Demand", "Supply Chain", "Global Inventory", "Price Volatility", "Macro Hedge"]
            descriptions = {"Industrial Demand": "PMI Index", "Supply Chain": "Mining Output", "Global Inventory": "LME Stock", "Price Volatility": "Spot Stdev", "Macro Hedge": "USD Corr"}
        elif "Bitcoin" in name:
            current_axes = ["Network Hashrate", "Adoption Rate", "Scarcity Value", "Market Liquidity", "Sovereign Risk"]
            descriptions = {"Network Hashrate": "Security Budget", "Adoption Rate": "Active Wallets", "Scarcity Value": "S2F Ratio", "Market Liquidity": "Order Book", "Sovereign Risk": "Fiat Risk"}
        else:
            # 米国債（FRB）用
            current_axes = ["Future Focus", "Market Position", "Financial Strength", "Cashflow Quality", "People"]
            descriptions = {"Future Focus": "Inflation Control", "Market Position": "Yield Stability", "Financial Strength": "Real Rate Ammo", "Cashflow Quality": "M2 Balance", "People": "Employment Balance"}

        # --- 🚀 2. 総合点数の表示（格付けなしのシンプル版） ---
        st.markdown(f"""
            <div class="total-score-container" style="margin-bottom: 20px; padding: 20px; background: white; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center;">
                <div class="total-score-label" style="color: #94a3b8; font-size: 14px; font-weight: 800;">TOTAL SCORE</div>
                <div class="total-score-val" style="font-size: 50px; font-weight: 900; color: #1e293b;">
                    {display_total} <span style="font-size: 24px; color: #cbd5e1;">/ 1000</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- 🚀 3. レーダーチャート（左）と詳細カード（右） ---
        col_left, col_right = st.columns([1.8, 1])

        with col_left:
            st.markdown("<div style='font-size: 1.1em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 5px;'>I. Intelligence Radar</div>", unsafe_allow_html=True)
            # 自動決定した current_axes を使用
            fig_r = render_radar_chart(data, st.session_state.saved_data, current_axes)
            st.plotly_chart(fig_r, use_container_width=True)

        with col_right:
            st.markdown("<div style='font-size: 0.9em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 15px; border-left: 3px solid #2E7BE6; padding-left: 8px;'>II. ANALYSIS SCORE METRICS</div>", unsafe_allow_html=True)
            for k in current_axes:
                v1 = data["axes"].get(k, 0)
                v2 = st.session_state.saved_data["axes"].get(k, 0) if st.session_state.saved_data else None
                score_html = f'<span style="color: #2E7BE6;">{int(v1)}</span>'
                if v2 is not None: score_html += f' <span style="color: #ccc; font-size: 0.9em; font-weight:bold; margin: 0 6px;">vs</span> <span style="color: #F4A261;">{int(v2)}</span>'

                st.markdown(f"""
                    <div style="background-color: #FFFFFF; padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #E0E0E0; border-left: 8px solid #2E7BE6;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                            <span style="font-size: 1.1em; font-weight: 800; color: #333333;">{k}</span>
                            <span style="font-size: 1.5em; font-weight: 900; line-height: 1;">{score_html}</span>
                        </div>
                        <p style="font-size: 0.85em; color: #777777; margin: 0; line-height: 1.2;">{descriptions.get(k, "")}</p>
                    </div>
                """, unsafe_allow_html=True)

        # 3. 下段：株価チャート
        st.markdown("<div class='section-title'>V. 10-Year Treasury Yield (5Y) Trend</div>", unsafe_allow_html=True)
        fig_p = go.Figure()
        if st.session_state.saved_data:
            s_data = st.session_state.saved_data
            # 市場が違う（SGX vs 米国先物）のでmergeせず、それぞれ%変化率で描画
            y1 = (data['price_hist'] / data['price_hist'].iloc[0] - 1) * 100
            y2 = (s_data['price_hist'] / s_data['price_hist'].iloc[0] - 1) * 100
            
            fig_p.add_trace(go.Scatter(x=y1.index, y=y1.values, mode='lines', name=name, line=dict(color='#2E7BE6', width=3)))
            fig_p.add_trace(go.Scatter(x=y2.index, y=y2.values, mode='lines', name=s_data['name'], line=dict(color='#F4A261', width=3)))
            fig_p.update_layout(yaxis_title="Return (%)")
        else:
            fig_p.add_trace(go.Scatter(x=data['price_hist'].index, y=data['price_hist'].values, mode='lines', name=name, line=dict(color='#2E7BE6', width=3)))
            fig_p.update_layout(yaxis_title="Price")

        fig_p.update_layout(plot_bgcolor='white', height=400, margin=dict(l=0, r=0, t=20, b=0), hovermode="x unified")
        st.plotly_chart(fig_p, use_container_width=True)

        # 4. Snapshot（比較対応版）
        st.markdown("<div class='section-title'>VI. Snapshot Comparison</div>", unsafe_allow_html=True)
        s1, s2, s3 = st.columns(3)
        
        saved = st.session_state.saved_data # 比較対象データ
        
        # --- PRICE ---
        p1 = data.get("current_price", 0)
        p2 = saved.get("current_price") if saved else None
        p_html = f'<span style="color:#2E7BE6;">{p1:.2f}</span>'
        if p2 is not None:
            p_html += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#F4A261;">{p2:.2f}</span>'
        s1.markdown(f'<div class="card"><div style="font-size:11px; color:#999;">PRICE</div><div style="font-size:22px; font-weight:900;">{p_html}</div></div>', unsafe_allow_html=True)
        
        # --- P/E RATIO ---
        pe1 = data.get("pe", "N/A")
        pe1_txt = f"{pe1:.1f}" if isinstance(pe1, (int, float)) and pe1 != 0 else "N/A"
        pe2 = saved.get("pe") if saved else None
        pe2_txt = f"{pe2:.1f}" if isinstance(pe2, (int, float)) and pe2 != 0 else "N/A"
        
        pe_html = f'<span style="color:#2E7BE6;">{pe1_txt}</span>'
        if saved:
            pe_html += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#F4A261;">{pe2_txt}</span>'
        s2.markdown(f'<div class="card"><div style="font-size:11px; color:#999;">P/E RATIO</div><div style="font-size:22px; font-weight:900;">{pe_html}</div></div>', unsafe_allow_html=True)
        
        # --- MARKET CAP ---
        cap1 = data.get("market_cap", 0)
        cap2 = saved.get("market_cap", 0) if saved else None
        
        cap_html = f'<span style="color:#2E7BE6;">{cap1/1e9:.1f}B</span>'
        if cap2 is not None:
            cap2_txt = f"{cap2/1e9:.1f}B" if cap2 > 0 else "N/A"
            cap_html += f' <span style="font-size:0.5em; color:#666;">vs</span> <span style="color:#F4A261;">{cap2_txt}</span>'
        s3.markdown(f'<div class="card"><div style="font-size:11px; color:#999;">MARKET CAP</div><div style="font-size:22px; font-weight:900;">{cap_html}</div></div>', unsafe_allow_html=True)
        
        # --- VII. PRE-ORDER SECTION (Branded White Edition) ---
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
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
    <div style="font-size: 1.4em; color: #7f8c8d; text-decoration: line-through; text-decoration-thickness: 2px; margin-bottom: 5px; font-weight: 700;">Standard: S$99 / MONTH</div>
    <div style="font-size: 4.2em; font-weight: 900; color: #1e3a8a; line-height: 1;">S$50 <span style="font-size: 0.35em; font-weight: 600; color: #64748b; vertical-align: middle;">/ MONTH</span></div>
    <div style="display: inline-block; background-color: #EBF5FF; padding: 6px 16px; border-radius: 20px; margin-top: 10px; border: 1px solid #D0E7FF;">
    <p style="font-size: 0.9em; color: #2E7BE6; margin: 0; font-weight: 800; letter-spacing: 0.5px;">
        EXCLUSIVE: S$50 Rate for the First 30 Members — Valid for 3 Months
    </p>
</div>
</div>
""", unsafe_allow_html=True)

        # 🚀 本物のリンクボタン（ここだけPythonのコードとして書く）
        st.link_button(
            "SECURE YOUR SLOT NOW", 
            "https://square.link/u/s2z4dwRO",
            use_container_width=True,
            type="primary"
        )

        st.markdown("""
<div style="margin-top: 10px; padding: 20px; background: #f8fafc; border-radius: 12px; font-size: 0.75em; color: #64748b; line-height: 1.6; text-align: left; border-left: 5px solid #2E7BE6; max-width: 600px; margin-left: auto; margin-right: auto;">
    <strong>DISCLAIMER:</strong> This service is for informational purposes only and does not constitute investment advice, recommendation, or solicitation. While we strive for accuracy, we do not guarantee the completeness or reliability of the data provided. All investment decisions should be made at the user's own discretion and risk. We shall not be held liable for any loss or damage arising from the use of this service.
</div>

<div style="margin-top: 30px; font-size: 0.85em; color: #94a3b8; font-weight: 500;">
Official Launch: March 1, 2026 | Full Institutional Engine Unlocked
</div>
</div>
""", unsafe_allow_html=True)

# 💡 ここからは if data: ブロックの外側。一番左に配置
if __name__ == "__main__":

    main()
