import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from ui_components import inject_css, render_radar_chart
from data_logic import fetch_data

APP_TITLE = "Scoring Dashboard"
# 冒頭 9行目付近
# --- 指標定義（FRB用とコモディティ用） ---
FRB_AXES = ["Future Focus", "Market Position", "Financial Strength", "Cashflow Quality", "People"]

def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    inject_css()

    if "saved_data" not in st.session_state:
        st.session_state.saved_data = None

        # --- 🚀 世界の中央銀行 セレクション ---
    top_ = [
        {"name": "Federal Reserve (USA)", "symbol": "^TNX"},
        {"name": "Monetary Authority of Singapore (SGP)", "symbol": "SGP"},
    ]
    
    options = [f"{s['name']} ({s['symbol']})" for s in top_]
    target = st.selectbox("Select Asset", options)
    
    # 選択した銘柄の名前とシンボルを抽出
    name = target.rsplit(" (", 1)[0]
    symbol = next(s['symbol'] for s in top_ if s['name'] == name)

    # ✅ ここから挿入！
    display_axes = FRB_AXES
    descriptions = {
        "Future Focus": "Inflation Forecasting & Control",
        "Market Position": "Yield Stability & Curve Credibility",
        "Financial Strength": "Real Rate Cushion (Policy Ammo)",
        "Cashflow Quality": "M2 Money Supply Optimization",
        "People": "Natural Rate of Unemployment Target"
    }
    # ✅ ここまで挿入！
    st.markdown(f'<div class="company-header">{name}</div>', unsafe_allow_html=True)

    # 2. メイン銘柄のデータ取得
    data = fetch_data(symbol, name)

    if data:
        # 1. 総合点数（中央上部）
        source = st.session_state.saved_data if st.session_state.saved_data else data
        display_total = int(data.get("total", 0))

        # 1. 総合点数（中央上部）
        st.markdown(f"""
            <div class="total-score-container" style="margin-bottom: 10px; padding-top: 10px;">
                <div class="total-score-label" style="margin-bottom: 0px;">TOTAL SCORE</div>
                <div class="total-score-val">{display_total} <span style="font-size:30px; color:#DDD;">/ 1000</span></div>
            </div>
        """, unsafe_allow_html=True)

        # 2. 中段：レーダーチャート（左）と DNA点数（右）
        col_left, col_right = st.columns([1.8, 1])

        with col_left:
            # タイトルの上下余白を極限まで詰める
            st.markdown("<div style='font-size: 1.1em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 5px;'>I. Intelligence Radar</div>", unsafe_allow_html=True)
            fig_r = render_radar_chart(data, st.session_state.saved_data, display_axes)
            st.plotly_chart(fig_r, use_container_width=True)

        with col_right:
            # 右側のタイトルも左に合わせて上に寄せる
            st.markdown("<div style='font-size: 0.9em; font-weight: bold; color: #333; margin-top: -10px; margin-bottom: 15px; border-left: 3px solid #2E7BE6; padding-left: 8px;'>II. ANALYSIS SCORE METRICS</div>", unsafe_allow_html=True)
            
            # 表示ソースの確定
            source = st.session_state.saved_data if st.session_state.saved_data else data
            is_oil = source.get('name') == "WTI CRUDE OIL"
            
            
# 🚀 会社用のロジック解説（Peopleに復刻）
            logic_descriptions = {
                "Future Focus": "Inflation Forecasting & Control",
                "Market Position": "Yield Stability & Curve Credibility",
                "Financial Strength": "Real Rate Cushion (Policy Ammo)",
                "Cashflow Quality": "M2 Money Supply Optimization",
                "People": "Natural Rate of Unemployment Target"
            }
            # 🚀 原油用のロジック解説 (data_logic.py の計算式に準拠)
            oil_labels = ["Demand Forecast", "Geopolitical Risk", "Price Level Stress", "Supply Stability", "Market Heat Index"]
            oil_descriptions = {
                "Demand Forecast": "Price vs 1Y Average (Demand Strength Logic)",
                "Geopolitical Risk": "Market Volatility × Risk Coefficient (15x)",
                "Price Level Stress": "Distance from 1Y High (Overhead Resistance)",
                "Supply Stability": "20-Day Rolling Volatility Stability Index",
                "Market Heat Index": "Annual Growth Rate (Speculative Momentum)"
            }
            
            # 指標カードの生成（25% Enlarged Version）
            for i, k in enumerate(display_axes):
                v1 = data["axes"].get(k, 0)  # 現在の資産（青）
                v2 = st.session_state.saved_data["axes"].get(k, 0) if st.session_state.saved_data else None # 保存済み（オレンジ）
                
                display_label = oil_labels[i] if is_oil else k
                desc_text = oil_descriptions.get(display_label, "") if is_oil else logic_descriptions.get(k, "")
                
                # スコア表示のHTML（フォントサイズを25%アップ: 1.3em -> 1.7em / 0.7em -> 0.9em）
                score_html = f'<span style="color: #2E7BE6;">{int(v1)}</span>'
                if v2 is not None:
                    score_html += f' <span style="color: #ccc; font-size: 0.9em; font-weight:bold; margin: 0 6px;">vs</span> <span style="color: #F4A261;">{int(v2)}</span>'

                st.markdown(f"""
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
                """, unsafe_allow_html=True)

        # 3. 下段：チャート（比較機能を維持 ＋ クリック・ズーム禁止）
        st.markdown(f"<div class='section-title'>V. {name} Trend</div>", unsafe_allow_html=True)
        fig_p = go.Figure()

        # 🎯 ここで「保存されたデータ」があるかチェックして比較線を引く
        if st.session_state.saved_data:
            s_data = st.session_state.saved_data
            y1 = (data['price_hist'] / data['price_hist'].iloc[0] - 1) * 100
            y2 = (s_data['price_hist'] / s_data['price_hist'].iloc[0] - 1) * 100
            
            fig_p.add_trace(go.Scatter(x=y1.index, y=y1.values, mode='lines', name=name, line=dict(color='#2E7BE6', width=3)))
            fig_p.add_trace(go.Scatter(x=y2.index, y=y2.values, mode='lines', name=s_data['name'], line=dict(color='#F4A261', width=3)))
            fig_p.update_layout(yaxis_title="Return (%)")
        else:
            fig_p.add_trace(go.Scatter(x=data['price_hist'].index, y=data['price_hist'].values, mode='lines', name=name, line=dict(color='#2E7BE6', width=3)))
            fig_p.update_layout(yaxis_title="Yield (%)")

        # 🎯 ここに「禁止設定」を入れました
        fig_p.update_layout(
            plot_bgcolor='white', height=400, margin=dict(l=0, r=0, t=20, b=0), 
            hovermode="x unified",
            clickmode='none',  # 👈 クリック反応を消す
            dragmode=False     # 👈 ズーム（変な感じ）を消す
        )

        # 🎯 右上のメニューバーも消してスッキリ
        st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})

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
""", unsafe_allow_html=True)

# 💡 ここからは if data: ブロックの外側。一番左に配置
if __name__ == "__main__":
    main()