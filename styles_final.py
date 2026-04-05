"""
ELZF-AI Styling Module - Clean, Professional, No Code Display
"""

DARK_CSS = """
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: linear-gradient(135deg, #0f1527 0%, #1a1f3a 100%);
    color: #e0e6ed;
    font-family: 'Inter', 'Space Mono', sans-serif;
    overflow-x: hidden;
}
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: rgba(0, 212, 255, 0.05); }
::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.3); border-radius: 4px; }
.stApp { background: linear-gradient(135deg, #0f1527 0%, #1a1f3a 100%); }
[data-testid="stAppViewContainer"] { background: transparent; }
.stButton > button {
    background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
    color: #0f1527 !important;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
}
.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5);
    transform: translateY(-2px);
}
</style>
"""

TOPBAR_HTML = """
<div style="background: linear-gradient(90deg, rgba(0,212,255,0.1) 0%, rgba(0,255,157,0.05) 100%);border-bottom: 2px solid rgba(0,212,255,0.2);padding: 12px 20px;border-radius: 0 0 12px 12px;margin-bottom: 10px;">
    <div style="display: flex;align-items: center;gap: 10px;font-family: 'Space Mono', monospace;font-size: 12px;color: #00ff9d;font-weight: 700;letter-spacing: 0.05em;text-transform: uppercase;">
        <span style="color: #ff3d71;">●</span>
        <span>ELZF-AI v2.5 — EMERGENCY LANDING ZONE FINDER — LIVE</span>
        <span style="color: #00d4ff;">◆</span>
        <span style="color: #00d4ff;">PATENT-LEVEL AI ANALYSIS ACTIVE</span>
    </div>
</div>
"""

def TICKER_HTML(content: str) -> str:
    return f"""
    <div style="background: linear-gradient(90deg, rgba(255,61,113,0.1) 0%, rgba(0,212,255,0.1) 100%);border: 1px solid rgba(0,212,255,0.15);border-radius: 8px;padding: 8px 15px;margin-bottom: 12px;overflow: hidden;">
        <style>
            @keyframes scroll {{
                0% {{ transform: translateX(0); }}
                100% {{ transform: translateX(-100%); }}
            }}
            .ticker {{
                animation: scroll 25s linear infinite;
                white-space: nowrap;
                font-family: 'Space Mono', monospace;
                font-size: 11px;
                color: #00d4ff;
                font-weight: 600;
                letter-spacing: 0.04em;
            }}
        </style>
        <div class="ticker">{content}</div>
    </div>
    """

def SECTION_HEADER(icon: str, title: str, subtitle: str) -> str:
    return f"""
    <div style="margin-bottom: 12px;padding-bottom: 8px;border-bottom: 1px solid rgba(0,212,255,0.15);">
        <div style="display: flex;align-items: center;gap: 8px;margin-bottom: 4px;">
            <span style="font-size: 18px;">{icon}</span>
            <span style="font-size: 14px;font-weight: 700;color: #00ff9d;font-family: 'Space Mono', monospace;letter-spacing: 0.03em;">{title}</span>
        </div>
        <div style="font-size: 10px;color: #8892b0;font-family: 'Space Mono', monospace;letter-spacing: 0.05em;text-transform: uppercase;">{subtitle}</div>
    </div>
    """

def stat_card(label: str, value: str, unit: str, color: str, badge_text: str, badge_type: str) -> str:
    badge_bg = {"ok": "rgba(0, 255, 157, 0.1)", "info": "rgba(0, 212, 255, 0.1)", "warn": "rgba(255, 184, 0, 0.1)", "danger": "rgba(255, 61, 113, 0.1)"}
    badge_color = {"ok": "#00ff9d", "info": "#00d4ff", "warn": "#ffb800", "danger": "#ff3d71"}
    return f"""
    <div style="background: rgba(15, 21, 39, 0.6);border: 1px solid rgba(0, 212, 255, 0.15);border-radius: 10px;padding: 12px;min-height: 100px;display: flex;flex-direction: column;justify-content: space-between;transition: all 0.3s ease;box-shadow: 0 4px 15px rgba(0, 212, 255, 0.05);">
        <div>
            <div style="font-size: 11px;color: #8892b0;font-family: 'Space Mono', monospace;font-weight: 600;text-transform: uppercase;letter-spacing: 0.05em;margin-bottom: 6px;">{label}</div>
            <div style="font-size: 24px;font-weight: 700;color: {color};display: flex;align-items: baseline;gap: 4px;">
                <span>{value}</span>
                <span style="font-size: 14px; opacity: 0.7;">{unit}</span>
            </div>
        </div>
        <div style="background: {badge_bg[badge_type]};border: 1px solid {badge_color[badge_type]};border-radius: 6px;padding: 6px 8px;font-size: 10px;color: {badge_color[badge_type]};font-family: 'Space Mono', monospace;font-weight: 700;text-transform: uppercase;text-align: center;letter-spacing: 0.03em;">{badge_text}</div>
    </div>
    """

def zone_card_clean(zone: dict, rank: int, selected: bool = False) -> str:
    score = zone.get("score", 0)
    risk_color = "#00ff9d" if score >= 75 else "#00d4ff" if score >= 50 else "#ffb800" if score >= 30 else "#ff3d71"
    risk_level = "✓ SAFE" if score >= 75 else "⚠ MEDIUM" if score >= 50 else "⚠ HIGH" if score >= 30 else "🚫 DANGER"
    risk_bg = "rgba(0, 255, 157, 0.1)" if score >= 75 else "rgba(0, 212, 255, 0.1)" if score >= 50 else "rgba(255, 184, 0, 0.1)" if score >= 30 else "rgba(255, 61, 113, 0.15)"
    
    zone_emoji = {"field": "🌾", "highway": "🛣️", "airport": "✈️", "water": "💧", "mountain": "⛰️", "urban": "🏙️", "beach": "🏖️", "desert": "🏜️"}
    emoji = zone_emoji.get(zone.get("type", "field").lower(), "📍")
    
    border_style = "2px solid #00d4ff" if selected else "1px solid rgba(0, 212, 255, 0.15)"
    bg_opacity = "0.8" if selected else "0.6"
    
    return f"""
    <div style="background: rgba(15, 21, 39, {bg_opacity});border: {border_style};border-radius: 10px;padding: 10px;margin-bottom: 10px;transition: all 0.3s ease;cursor: pointer;overflow: hidden;">
        <div style="display: flex;justify-content: space-between;align-items: center;margin-bottom: 8px;">
            <div style="font-size: 12px;font-weight: 700;color: #00ff9d;font-family: 'Space Mono', monospace;">{emoji} ZONE {chr(65+rank)}</div>
            <div style="background: rgba(0, 212, 255, 0.2);border: 1px solid #00d4ff;border-radius: 6px;padding: 3px 8px;font-size: 9px;color: #00d4ff;font-weight: 700;">#{rank+1}</div>
        </div>
        <div style="font-size: 11px;color: #8892b0;margin-bottom: 6px;font-family: 'Space Mono', monospace;overflow: hidden;text-overflow: ellipsis;white-space: nowrap;">{zone.get('name', 'Unknown')}</div>
        <div style="background: rgba(255,255,255,0.06);border-radius: 4px;height: 4px;margin-bottom: 8px;overflow: hidden;"><div style="width: {score}%;height: 100%;background: {risk_color};border-radius: 4px;"></div></div>
        <div style="display: flex;justify-content: space-between;align-items: center;margin-bottom: 8px;">
            <div style="font-size: 14px;font-weight: 700;color: {risk_color};">{score:.0f}</div>
            <div style="background: {risk_bg};border: 1px solid {risk_color};border-radius: 4px;padding: 3px 6px;font-size: 8px;color: {risk_color};font-family: 'Space Mono', monospace;font-weight: 700;text-transform: uppercase;">{risk_level}</div>
        </div>
    </div>
    """

def ai_tips_html(score: float) -> str:
    if score < 30:
        tip = "🚫 DANGER ZONE — Consider alternative landing sites immediately"
        tip_color = "#ff3d71"
        tip_bg = "rgba(255, 61, 113, 0.15)"
    elif score < 50:
        tip = "⚠️ HIGH RISK — Multiple hazards detected. Approach with caution"
        tip_color = "#ffb800"
        tip_bg = "rgba(255, 184, 0, 0.15)"
    elif score < 75:
        tip = "⚡ ACCEPTABLE — This zone is suitable for emergency landing"
        tip_color = "#00d4ff"
        tip_bg = "rgba(0, 212, 255, 0.15)"
    else:
        tip = "✓ OPTIMAL — Excellent landing conditions detected"
        tip_color = "#00ff9d"
        tip_bg = "rgba(0, 255, 157, 0.15)"
    
    return f"""
    <div style="background: {tip_bg};border: 1px solid {tip_color};border-radius: 10px;padding: 12px 15px;">
        <div style="font-size: 12px;color: {tip_color};font-family: 'Space Mono', monospace;font-weight: 700;">{tip}</div>
    </div>
    """

def danger_alert_html(danger_zones) -> str:
    if len(danger_zones) == 0:
        return ""
    
    danger_names = [row['name'] for _, row in danger_zones.head(3).iterrows()]
    danger_list = ", ".join(danger_names)
    
    return f"""
    <div style="background: rgba(255, 61, 113, 0.15);border: 2px solid #ff3d71;border-radius: 10px;padding: 12px 15px;">
        <div style="display: flex;gap: 10px;">
            <div style="font-size: 20px;">🚫</div>
            <div>
                <div style="font-size: 12px;color: #ff3d71;font-family: 'Space Mono', monospace;font-weight: 700;margin-bottom: 4px;">DANGER ZONES DETECTED</div>
                <div style="font-size: 10px;color: #ffb8cc;font-family: 'Space Mono', monospace;">Avoid: {danger_list}</div>
            </div>
        </div>
    </div>
    """