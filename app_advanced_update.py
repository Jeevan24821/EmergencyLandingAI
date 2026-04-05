# Add to app_advanced.py - INSERT after render_alert_box function

def render_ai_tips_and_warnings(zones: pd.DataFrame, best_zone: dict, aircraft: dict):
    """Render AI-powered tips and danger zone warnings"""
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # AI Tips
        if best_zone.get("score", 0) < 50:
            tip_icon = "🚫"
            tip_text = f"DANGER ZONE — Score {best_zone['score']:.0f}/100. Consider diverting to safer zones."
            tip_color = "#ff3d71"
        elif best_zone.get("score", 0) < 75:
            tip_icon = "⚠️"
            tip_text = f"CAUTION — Acceptable landing zone. Approach with elevated attention."
            tip_color = "#ffb800"
        else:
            tip_icon = "✓"
            tip_text = f"OPTIMAL — Excellent conditions. Score {best_zone['score']:.0f}/100"
            tip_color = "#00ff9d"
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba{(int(tip_color[1:3], 16), int(tip_color[3:5], 16), int(tip_color[5:7], 16), 0.15)});
            border: 2px solid {tip_color};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 12px;
        ">
            <div style="display: flex; gap: 10px; align-items: flex-start;">
                <div style="font-size: 24px;">{tip_icon}</div>
                <div>
                    <div style="font-size: 12px; color: {tip_color}; font-weight: 700; font-family: 'Space Mono', monospace;">
                        AI RECOMMENDATION
                    </div>
                    <div style="font-size: 11px; color: #8892b0; margin-top: 4px; font-family: 'Space Mono', monospace;">
                        {tip_text}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Danger Zones Summary
        danger_zones = zones[zones["score"] < 30]
        if len(danger_zones) > 0:
            st.markdown(f"""
            <div style="
                background: rgba(255, 61, 113, 0.15);
                border: 2px solid #ff3d71;
                border-radius: 10px;
                padding: 12px;
            ">
                <div style="font-size: 12px; color: #ff3d71; font-weight: 700; font-family: 'Space Mono', monospace; margin-bottom: 8px;">
                    🚫 {len(danger_zones)} DANGER ZONE(S) DETECTED
                </div>
                <div style="font-size: 10px; color: #ffb8cc; font-family: 'Space Mono', monospace; line-height: 1.6;">
                    {"<br>".join([f"• {z['name']} (Score: {z['score']:.0f})" for z in danger_zones.head(3).itertuples()])}
                </div>
            </div>
            """, unsafe_allow_html=True)

# REPLACE the render_analysis_tab function with this:
def render_analysis_tab(df: pd.DataFrame, sel_zone: Dict, best: Dict):
    """Render analysis tab with charts and zone images"""
    
    # AI Tips Section
    st.markdown(SECTION_HEADER("🤖", "AI-Powered Analysis", "REAL-TIME RECOMMENDATIONS"),
                unsafe_allow_html=True)
    render_ai_tips_and_warnings(df, best, st.session_state.aircraft)
    
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    
    # Charts Section
    st.markdown(SECTION_HEADER("📊", "Risk Analysis", "ZONE METRICS & COMPARISONS"),
                unsafe_allow_html=True)
    
    ch1, ch2, ch3 = st.columns([1, 1, 0.6])

    with ch1:
        st.markdown("<div style='font-size:11px;color:#8892b0;font-family:Space Mono,monospace;margin-bottom:8px;'>📊 Zone Score Comparison</div>",
                    unsafe_allow_html=True)
        try:
            bar_html = bar_chart_html(df.to_dict("records"))
            components.html(bar_html, height=250, scrolling=False)
        except Exception as e:
            logger.error(f"Bar chart error: {e}")
            st.warning(f"⚠️ Chart unavailable")

    with ch2:
        st.markdown(f"<div style='font-size:11px;color:#8892b0;font-family:Space Mono,monospace;margin-bottom:8px;'>🕸️ Risk Radar — {sel_zone.get('name', 'Unknown')}</div>",
                    unsafe_allow_html=True)
        try:
            factor_scores = get_factor_scores(sel_zone)
            radar_html = radar_chart_html(sel_zone, factor_scores)
            components.html(radar_html, height=270, scrolling=False)
        except Exception as e:
            logger.error(f"Radar chart error: {e}")
            st.warning(f"⚠️ Radar unavailable")

    with ch3:
        st.markdown("<div style='font-size:11px;color:#8892b0;font-family:Space Mono,monospace;margin-bottom:8px;'>🎯 Safety Score</div>",
                    unsafe_allow_html=True)
        try:
            g_html = gauge_html(int(best["score"]))
            components.html(g_html, height=200, scrolling=False)
        except Exception as e:
            logger.error(f"Gauge chart error: {e}")
            st.warning(f"⚠️ Gauge unavailable")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        factor_best = get_factor_scores(best)
        render_factor_bars(factor_best)

    # Zone Comparison Cards
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown(SECTION_HEADER("🗂️", "Zone Comparison", "TOP 4 LANDING OPTIONS"),
                unsafe_allow_html=True)
    
    zone_cols = st.columns(4)
    for idx, (col, (_, zone)) in enumerate(zip(zone_cols, df.head(4).iterrows())):
        with col:
            zone_dict = zone.to_dict()
            score = zone_dict.get("score", 0)
            risk_color = "#00ff9d" if score >= 75 else "#00d4ff" if score >= 50 else "#ffb800" if score >= 30 else "#ff3d71"
            
            st.markdown(f"""
            <div style="
                background: rgba(15, 21, 39, 0.7);
                border: 1px solid {risk_color};
                border-radius: 10px;
                padding: 12px;
                text-align: center;
            ">
                <div style="font-size: 28px; margin-bottom: 8px;">
                    {["🌾", "🛣️", "✈️", "💧", "⛰️", "🏙️", "🏖️", "🏜️"][idx % 8]}
                </div>
                <div style="
                    font-size: 11px;
                    font-weight: 700;
                    color: #00d4ff;
                    font-family: 'Space Mono', monospace;
                    margin-bottom: 4px;
                ">ZONE {chr(65+idx)}</div>
                <div style="
                    font-size: 10px;
                    color: #8892b0;
                    font-family: 'Space Mono', monospace;
                    margin-bottom: 6px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                ">{zone_dict.get('name', 'Unknown')}</div>
                <div style="
                    font-size: 20px;
                    font-weight: 700;
                    color: {risk_color};
                    margin-bottom: 6px;
                ">{score:.0f}</div>
                <div style="
                    background: rgba(0, 212, 255, 0.2);
                    border: 1px solid #00d4ff;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 9px;
                    color: #00d4ff;
                    font-family: 'Space Mono', monospace;
                    font-weight: 700;
                ">{zone_dict.get('type', 'Unknown').upper()}</div>
            </div>
            """, unsafe_allow_html=True)