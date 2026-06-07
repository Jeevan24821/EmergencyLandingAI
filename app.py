from typing import Optional, Tuple, Dict, List
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import logging
import time
import json
import os

# Try to import supporting modules from the repo. If any are missing, we add safe fallbacks.
try:
    import charts
except Exception:
    charts = None

try:
    import risk_model
except Exception:
    risk_model = None

try:
    import map_builder
except Exception:
    map_builder = None

try:
    import simulator_component
except Exception:
    simulator_component = None

try:
    import data_simulator
except Exception:
    data_simulator = None

try:
    import advanced_features
except Exception:
    advanced_features = None

try:
    import styles_final
except Exception:
    styles_final = None

try:
    import app_advanced_update
    # This module contains render_analysis_tab and helpers from your earlier snippet.
except Exception:
    app_advanced_update = None

logger = logging.getLogger("ELZF")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# -----------------------------
# Minimal fallbacks
# -----------------------------
def safe_bar_chart_html(zones):
    if charts and hasattr(charts, "bar_chart_html"):
        return charts.bar_chart_html(zones)
    # fallback simple HTML
    labels = [z["name"] for z in zones]
    scores = [z["score"] for z in zones]
    bars = "".join(f"<div style='display:flex;align-items:center;margin:6px 0;'><div style='width:160px;color:#a8c9ff'>{labels[i]}</div><div style='height:12px;background:#2b7cff;border-radius:6px;width:{scores[i]}px;margin-left:8px'></div><div style='width:40px;text-align:right;color:#cbd6ea;margin-left:8px'>{scores[i]}</div></div>" for i in range(len(labels)))
    return f"<div style='padding:12px;color:#cbd6ea;font-family:Space Mono,monospace'>{bars}</div>"

def safe_radar_html(zone, factor_scores):
    if charts and hasattr(charts, "radar_chart_html"):
        return charts.radar_chart_html(zone, factor_scores)
    return f"<div style='padding:12px;color:#cbd6ea;'>Radar unavailable</div>"

def safe_gauge_html(score):
    if charts and hasattr(charts, "gauge_html"):
        return charts.gauge_html(score)
    return f"<div style='padding:12px;color:#cbd6ea;'>Gauge unavailable</div>"

def safe_get_factor_scores(zone):
    if risk_model and hasattr(risk_model, "get_factor_scores"):
        return risk_model.get_factor_scores(zone)
    # approximate fallback
    return {
        "Surface": 70, "Clearance": 60, "Area": 55, "Wind": 70, "Visibility": 80, "Landing Sfc": 65
    }

# -----------------------------
# Aircraft sound system (keeps original API minimal)
# -----------------------------
try:
    import numpy as _np
    import io as _io
    import wave as _wave
except Exception:
    _np = None

class AircraftSoundSystem:
    """Lightweight sound helper — generates brief alert waveforms for in-app playback"""

    SAMPLE_RATE = 22050

    @staticmethod
    def generate_sine_wave(frequency: float, duration: float, amplitude: float = 0.3):
        if _np is None:
            return None
        t = _np.linspace(0, duration, int(AircraftSoundSystem.SAMPLE_RATE * duration), False)
        tone = _np.sin(frequency * 2 * _np.pi * t) * amplitude
        # Normalize to 16-bit PCM
        audio = (tone * (2**15 - 1)).astype(_np.int16)
        # Write to bytes using wave
        buf = _io.BytesIO()
        with _wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(AircraftSoundSystem.SAMPLE_RATE)
            wf.writeframes(audio.tobytes())
        return buf.getvalue()

    @staticmethod
    def play_sound_streamlit(pattern_name: str):
        """Play a short tone in Streamlit (non-blocking)."""
        if _np is None:
            return
        freq_map = {
            "alert": 1046.50,
            "critical": 1174.66,
            "danger": 1318.51,
            "confirm": 523.25,
            "chime": 659.25,
            "landing": 440.0,
        }
        freq = freq_map.get(pattern_name, 1046.50)
        wav = AircraftSoundSystem.generate_sine_wave(freq, 0.35, amplitude=0.25)
        if wav:
            st.audio(wav, format="audio/wav")

# -----------------------------
# UI helpers
# -----------------------------
def inject_style():
    if styles_final and hasattr(styles_final, "DARK_CSS"):
        st.markdown(styles_final.DARK_CSS, unsafe_allow_html=True)
        return
    # Minimal styling fallback including base fonts / colors
    st.markdown(
        """
        <style>
        :root {
            --bg:#07101a;
            --muted:#8892b0;
            --accent:#00d4ff;
            --card:#071826;
            --glass: rgba(255,255,255,0.03);
        }
        body { background: var(--bg); color:#cbd6ea; font-family: 'Space Mono', monospace; }
        .stButton > button { border-radius: 8px; }
        .elzf-topbar { padding:8px 10px; color:var(--accent); font-weight:700; font-family: 'Space Mono', monospace; }
        .elzf-card { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:12px; border-radius:10px; box-shadow: 0 6px 18px rgba(0,0,0,0.6); }
        .feature-card { background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(0,212,255,0.02)); border-left: 3px solid #00d4ff; padding: 14px; border-radius: 8px; margin-bottom: 12px; }
        .status-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .status-active { background: rgba(34,197,94,0.15); color: #22c55e; }
        .status-inactive { background: rgba(107,114,128,0.15); color: #9ca3af; }
        .metric-box { background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; border: 1px solid rgba(0,212,255,0.1); margin: 8px 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_topbar():
    if styles_final and hasattr(styles_final, "TOPBAR_HTML"):
        st.markdown(styles_final.TOPBAR_HTML, unsafe_allow_html=True)
    else:
        st.markdown("<div class='elzf-topbar'>ELZF-AI — Emergency Landing Zone Finder</div>", unsafe_allow_html=True)

def SECTION_HEADER(icon: str, title: str, subtitle: str) -> str:
    if styles_final and hasattr(styles_final, "SECTION_HEADER"):
        return styles_final.SECTION_HEADER(icon, title, subtitle)
    return f"""
    <div style="display:flex;gap:12px;align-items:center;margin-bottom:10px;">
      <div style="font-size:22px;">{icon}</div>
      <div>
        <div style="font-size:14px;font-weight:800;color:#00d4ff;font-family:Space Mono,monospace;">{title}</div>
        <div style="font-size:10px;color:#8892b0;font-family:Space Mono,monospace;">{subtitle}</div>
      </div>
    </div>
    """

# Enhanced card renderer for features
def render_feature_card(title: str, description: str, status: str = "active", icon: str = "📌") -> str:
    status_class = "status-active" if status == "active" else "status-inactive"
    return f"""
    <div class="feature-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">{icon}</span>
                <span style="font-weight: 600; color: #00d4ff;">{title}</span>
            </div>
            <span class="status-badge {status_class}">{'ACTIVE' if status == 'active' else 'INACTIVE'}</span>
        </div>
        <div style="color: #cbd6ea; font-size: 13px; line-height: 1.5;">{description}</div>
    </div>
    """

# Enhanced metric box renderer
def render_metric_box(label: str, value: str, unit: str = "", detail: str = "") -> str:
    return f"""
    <div class="metric-box">
        <div style="color: #8892b0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">{label}</div>
        <div style="color: #00d4ff; font-size: 20px; font-weight: 700;">{value}<span style="font-size: 14px; color: #cbd6ea;"> {unit}</span></div>
        {f'<div style="color: #6b7280; font-size: 11px; margin-top: 4px;">{detail}</div>' if detail else ''}
    </div>
    """

# Data helpers (use data_simulator if available)
def get_demo_aircraft():
    if data_simulator and hasattr(data_simulator, "get_aircraft_data"):
        d = data_simulator.get_aircraft_data()
        # convert keys to expected ones
        return {
            "latitude": d.get("latitude", 37.6190),
            "longitude": d.get("longitude", -122.375),
            "altitude": d.get("altitude", 800),
            "speed_mps": d.get("speed", 35),
            "speed": d.get("speed", 35),
            "heading": d.get("heading", 0),
            "fuel": d.get("fuel", "MODERATE"),
            "emergency": d.get("emergency", ""),
            "passengers": d.get("passengers", 120),
            "type": d.get("type", "H145"),
        }
    # fallback static
    return {"latitude": 37.6190, "longitude": -122.375, "altitude": 800, "speed_mps": 35, "speed": 35,
            "heading": 0, "fuel": "MODERATE", "emergency": "Engine Failure", "passengers": 120, "type": "H145"}

def get_demo_zones(lat: float = 37.6190, lon: float = -122.375):
    if data_simulator and hasattr(data_simulator, "generate_zones"):
        zones = data_simulator.generate_zones(lat, lon)
        # Ensure score exists
        df = pd.DataFrame(zones)
        if "score" not in df.columns:
            df["score"] = df.apply(lambda r: max(0, min(100, int(70 - (r.get("wind", 0) * 4)))), axis=1)
        return df
    # fallback static sample
    return pd.DataFrame([
        {"name":"Field Alpha","lat":lat+0.001,"lon":lon+0.001,"score":82,"type":"field","area":10000,"wind":3,"obstacles":"Low","visibility":"Clear","surface":"Grass"},
        {"name":"Highway Bravo","lat":lat-0.005,"lon":lon-0.01,"score":68,"type":"highway","area":8000,"wind":6,"obstacles":"Medium","visibility":"Hazy","surface":"Asphalt"},
        {"name":"Lake Charlie","lat":lat+0.01,"lon":lon-0.02,"score":45,"type":"water","area":6000,"wind":4,"obstacles":"Low","visibility":"Foggy","surface":"Water"},
        {"name":"Hill Delta","lat":lat+0.02,"lon":lon+0.015,"score":28,"type":"terrain","area":3000,"wind":8,"obstacles":"High","visibility":"Hazy","surface":"Gravel"},
    ])

# -----------------------------
# Application pages (preserve original features, add simulator)
# -----------------------------
def page_home():
    # Use HTML header with unsafe allow
    st.markdown(SECTION_HEADER("🏠", "Home", "OVERVIEW"), unsafe_allow_html=True)

    # Top layout: left column = visual + controls, right column = quick stats + zones
    left, right = st.columns([1,1.2])

    # Antigravity controls that adjust the client animation
    with right:
        st.subheader("Quick controls")
        st.metric("Aircraft Type", st.session_state.aircraft.get("type", "H145"))
        st.metric("Last Mission Count", len(st.session_state.mission_log))
        st.write("Use the controls below to trigger sounds or jump to the simulator.")
        if st.button("Open Simulator"):
            # set sidebar page selection (not always possible), provide hint
            st.sidebar.radio("Navigate", ["Home", "Analysis", "Simulator", "Map", "Advanced", "Settings"], index=2)
            st.info("Simulator selected in sidebar. If not visible, open the sidebar and click Simulator.")

        if st.button("Play Alert Tone"):
            AircraftSoundSystem.play_sound_streamlit("alert")

        st.markdown("---")
        st.subheader("Top Landing Zones")
        df = st.session_state.zones
        top = df.sort_values("score", ascending=False).head(4).reset_index(drop=True)
        st.dataframe(top[["name","type","score","area"]], height=220)
        # compact bar chart (client)
        try:
            chart_html = safe_bar_chart_html(top.to_dict("records"))
            components.html(chart_html, height=180, scrolling=False)
        except Exception:
            st.write("Chart preview unavailable.")

    with left:
        st.subheader("Antigravity HUD")
        # Antigravity toggle and intensity control
        antigravity = st.checkbox("Enable Antigravity visual", value=True)
        intensity = st.slider("Lift intensity", min_value=0, max_value=60, value=18)

        # Build a small HTML/CSS/JS snippet that animates a helicopter icon with rotor spin and float amplitude controlled by intensity
        html = f"""
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        :root {{
            --bg: #07101a;
            --card: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
            --accent: #00d4ff;
            --amp: {intensity}px;
            --speed: 2.6s;
        }}
        body{{ margin:0; background:var(--bg); color:#cbd6ea; font-family: 'Space Mono', monospace; }}
        .scene{{ display:flex; align-items:center; justify-content:center; height:380px; }}
        .card{{ width:360px; height:320px; border-radius:14px; background:var(--card); display:flex; align-items:center; justify-content:center; box-shadow: 0 8px 30px rgba(0,0,0,0.6); position:relative; overflow:hidden; }}
        .heli {{
            width:160px; height:160px; border-radius:12px; display:flex; align-items:center; justify-content:center; flex-direction:column;
            color:#071826; font-weight:900; font-size:56px;
            background: radial-gradient(circle at 30% 20%, rgba(0,212,255,0.12), transparent 30%), linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
            transform-origin: center;
            transition: transform 0.25s linear;
            margin-top: 0px;
        }}
        /* float animation */
        @keyframes floatX {{
            0% {{ transform: translateY(calc(var(--amp) * -1)) translateX(-6px) rotate(-1deg); }}
            50% {{ transform: translateY(calc(var(--amp) * 1)) translateX(6px) rotate(1deg); }}
            100% {{ transform: translateY(calc(var(--amp) * -1)) translateX(-6px) rotate(-1deg); }}
        }}
        .heli.animate {{ animation: floatX var(--speed) ease-in-out infinite; }}

        /* rotor */
        .rotor {{
            width:120px; height:12px; border-radius:6px; background: linear-gradient(90deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
            position:relative; margin-bottom:8px;
            box-shadow: 0 3px 16px rgba(0,0,0,0.6);
        }}
        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        .rotor.spin {{ animation: spin 0.6s linear infinite; transform-origin:center; }}

        .hud {{
            position:absolute; left:12px; bottom:12px; color:#9fbde8; font-size:12px;
            background: rgba(0,0,0,0.18); padding:8px 10px; border-radius:8px;
        }}

        .pulse {{
            position:absolute; border-radius:50%; width:300px; height:300px; background: radial-gradient(circle, rgba(0,212,255,0.06), transparent 40%); opacity:0.6; pointer-events:none;
            filter: blur(8px);
            animation: pulse 3.2s ease-out infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(0.85); opacity:0.6; }}
            70% {{ transform: scale(1.15); opacity:0.12; }}
            100% {{ transform: scale(0.85); opacity:0.6; }}
        }}

        /* small responsive */
        @media (max-width:600px) {{
            .card{{ width:100%; height:280px; }}
        }}
        </style>
        </head>
        <body>
        <div class="scene">
            <div class="card" role="region" aria-label="Antigravity HUD">
                <div style="position:absolute; right:12px; top:12px; color:var(--accent); font-size:12px;">ELZF-AI HUD</div>
                <div style="position:absolute; left:12px; top:12px; color:#9fbde8; font-size:12px;">Helicopter: {st.session_state.aircraft.get('type','H145')}</div>
                <div style="position:relative; z-index:2; display:flex; align-items:center; justify-content:center; width:100%; height:100%;">
                    <div id="heli" class="heli {'animate' if antigravity else ''}">
                        <div id="rotor" class="rotor {'spin' if antigravity else ''}"></div>
                        <div style="font-size:34px; color:#c6f0ff;">🚁</div>
                        <div style="font-size:12px; color:#9fbde8; margin-top:6px;">Altitude: {int(st.session_state.aircraft.get('altitude',0))} m</div>
                    </div>
                    <div class="pulse" style="z-index:1; opacity:0.22;"></div>
                </div>
                <div class="hud">
                    <div><strong>Lat:</strong> {st.session_state.aircraft.get('latitude',0):.5f}</div>
                    <div><strong>Lon:</strong> {st.session_state.aircraft.get('longitude',0):.5f}</div>
                    <div><strong>Speed:</strong> {st.session_state.aircraft.get('speed_mps',0)} m/s</div>
                </div>
            </div>
        </div>
        <script>
            // Allow subtle interactivity: clicking the heli pulses rotor when antigravity is on
            const heli = document.getElementById('heli');
            const rotor = document.getElementById('rotor');
            heli.addEventListener('click', () => {{
                if (!heli.classList.contains('animate')) {{
                    // quick bounce
                    heli.style.transform = 'translateY(-12px) scale(1.02)';
                    setTimeout(() => heli.style.transform = '', 260);
                }} else {{
                    // rotor boost visual
                    rotor.style.animationDuration = '0.18s';
                    setTimeout(() => rotor.style.animationDuration = '', 300);
                }}
            }});
        </script>
        </body>
        </html>
        """
        # Render the animated widget in an iframe
        components.html(html, height=420, scrolling=False)

    st.markdown("---")
    st.write("Tip: keep the Simulator tab open to run missions. Antigravity animation is a visual HUD; it does not affect mission physics.")

def page_analysis():
    # Use your existing analysis tab renderer if available
    st.markdown(SECTION_HEADER("📊", "Analysis", "AI-Powered Landing Zone Analysis"), unsafe_allow_html=True)
    df = st.session_state.zones
    sel_index = st.session_state.sel_index
    sel_zone = df.loc[sel_index].to_dict()
    best = df.loc[df['score'].idxmax()].to_dict()

    # If we have the app_advanced_update render function, use it
    if app_advanced_update and hasattr(app_advanced_update, "render_analysis_tab"):
        try:
            app_advanced_update.render_analysis_tab(df, sel_zone, best)
            return
        except Exception as e:
            logger.exception("render_analysis_tab failed - falling back: %s", e)

    # Fallback rendering
    st.write("Top zones")
    st.dataframe(df.sort_values("score", ascending=False).reset_index(drop=True))
    with st.expander("Selected zone details"):
        st.json(sel_zone)
    # simple charts
    if charts and hasattr(charts, "bar_chart_html"):
        components.html(charts.bar_chart_html(df.to_dict("records")), height=300, scrolling=False)
    else:
        st.write("Bar chart module not available.")

def page_simulator():
    st.markdown(SECTION_HEADER("🚁", "Mission Simulator", "REAL-TIME HELICOPTER EMERGENCY MISSION"), unsafe_allow_html=True)
    st.write("This simulator animates a helicopter approaching the selected landing zone with HUD, ETA, altitude reduction, warnings, and rotor effects.")
    df = st.session_state.zones
    sel_idx = st.session_state.sel_index
    sel_zone = df.loc[sel_idx].to_dict()
    # Mission controls
    col1, col2 = st.columns([1,1])
    with col1:
        start_lat = st.number_input("Start lat", value=st.session_state.aircraft.get("latitude", 37.6190), format="%.6f")
        start_lon = st.number_input("Start lon", value=st.session_state.aircraft.get("longitude", -122.375), format="%.6f")
        start_alt = st.number_input("Start altitude (m)", value=st.session_state.aircraft.get("altitude", 800), min_value=0)
    with col2:
        groundspeed = st.number_input("Groundspeed (m/s)", value=st.session_state.aircraft.get("speed_mps",35.0))
        dt = st.slider("Telemetry interval (s)", 0.2, 2.0, 1.0, step=0.1)

    # Update session aircraft coords
    st.session_state.aircraft.update({"latitude": start_lat, "longitude": start_lon, "altitude": start_alt, "speed_mps": groundspeed})

    if simulator_component and hasattr(simulator_component, "build_mission_payload") and hasattr(simulator_component, "render_simulator"):
        if st.button("Prepare Mission"):
            aircraft = st.session_state.get("aircraft", {})
            # update aircraft coords from inputs
            aircraft.update({"latitude": start_lat, "longitude": start_lon, "altitude": start_alt, "speed_mps": groundspeed})
            mission_payload = simulator_component.build_mission_payload(aircraft=aircraft, zone=sel_zone, dt=dt, groundspeed=groundspeed, autostart=False, zoom=13)
            st.session_state.last_mission = mission_payload
            st.success("Mission prepared. Use the HUD below to Start/Abort/Replay.")

        # Ensure we always have a payload for display (non-blocking)
        if st.session_state.last_mission is None:
            aircraft = st.session_state.get("aircraft")
            mission_payload = simulator_component.build_mission_payload(aircraft=aircraft, zone=sel_zone, dt=dt, groundspeed=groundspeed, autostart=False, zoom=13)
            st.session_state.last_mission = mission_payload

        # Render the simulator component (client-side animation)
        simulator_component.render_simulator(st.session_state.last_mission, height=640)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        # Server-trigger start button
        if st.button("Start Mission (Server-trigger)"):
            st.session_state.last_mission["autostart"] = True
            simulator_component.render_simulator(st.session_state.last_mission, height=640)
            st.session_state.last_mission["autostart"] = False

        # Save mission to session log
        if st.button("Save Mission Log"):
            st.session_state.mission_log.append(st.session_state.last_mission)
            st.success("Mission saved to session log.")

        # Show brief mission stats
        mp = st.session_state.last_mission or {}
        st.markdown("### Mission Summary")
        try:
            st.metric("ETA (s)", f"{int(mp.get('travel_time',0))} s")
            st.metric("Distance (m)", f"{int(mp.get('distance',0))} m")
            st.metric("Start Alt (m)", f"{int(mp.get('telemetry',[{'alt':0}])[0]['alt'])}")
        except Exception:
            pass

        st.markdown("### Saved Missions")
        for i, m in enumerate(st.session_state.mission_log):
            st.markdown(f"- Mission {i+1}: start={m['start']} dest={m['dest']} distance={int(m['distance'])} m")
    else:
        st.warning("Simulator component not found. Ensure simulator_component.py exists in the repo.")
        st.write("Fallback: show static map and telemetry preview.")
        # show static map via map_builder if available
        try:
            import folium
            from streamlit_folium import st_folium
            if map_builder and hasattr(map_builder, "build_map"):
                m = map_builder.build_map(st.session_state.aircraft, st.session_state.zones)
                st_folium(m, width=700, height=480)
            else:
                st.map(st.session_state.zones[["lat", "lon"]])
        except Exception as e:
            st.write("Map fallback:", e)

def page_map():
    st.markdown(SECTION_HEADER("🗺️", "Map View", "INTERACTIVE MAP & ZONE DETAILS"), unsafe_allow_html=True)
    try:
        import folium
        from streamlit_folium import st_folium
        if map_builder and hasattr(map_builder, "build_map"):
            m = map_builder.build_map(st.session_state.aircraft, st.session_state.zones)
            st_folium(m, width=900, height=600)
        else:
            st.map(st.session_state.zones[["lat", "lon"]])
    except Exception as e:
        st.write("Map display error:", e)

def page_advanced():
    """Enhanced Advanced section with proper UI and organized layout."""
    st.markdown(SECTION_HEADER("🧠", "Advanced Features", "AI-POWERED INTELLIGENCE MODULES"), unsafe_allow_html=True)
    
    if not advanced_features:
        st.warning("🔌 Advanced features module not loaded")
        st.info("Place `advanced_features.py` in your repository to unlock AI-powered intelligence.")
        st.markdown("---")
        return

    # Top-level feature overview with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Predictive Analysis", "Risk Assessment", "Fleet Intelligence"])

    # ========== TAB 1: OVERVIEW ==========
    with tab1:
        st.markdown(SECTION_HEADER("📋", "Integrated AI Modules", "System-wide Intelligence"), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(render_feature_card(
                "Trajectory Prediction",
                "AI-powered helicopter trajectory forecasting with multi-variable analysis",
                "active",
                "🛤️"
            ), unsafe_allow_html=True)
            
        with col2:
            st.markdown(render_feature_card(
                "Health Diagnostics",
                "Predictive failure analysis for aircraft systems",
                "active",
                "⚕️"
            ), unsafe_allow_html=True)
            
        with col3:
            st.markdown(render_feature_card(
                "Dynamic Risk Matrix",
                "Real-time risk assessment across multiple parameters",
                "active",
                "⚠️"
            ), unsafe_allow_html=True)

        st.markdown("---")
        
        # System statistics
        st.subheader("System Status")
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.markdown(render_metric_box(
                "AI Version",
                "2.1",
                "beta",
                "Multi-module integration"
            ), unsafe_allow_html=True)
            
        with stat_col2:
            st.markdown(render_metric_box(
                "Modules Active",
                "3",
                "of 3",
                "All systems operational"
            ), unsafe_allow_html=True)
            
        with stat_col3:
            st.markdown(render_metric_box(
                "Prediction Window",
                "5",
                "min",
                "Real-time forecasting"
            ), unsafe_allow_html=True)
            
        with stat_col4:
            st.markdown(render_metric_box(
                "Update Frequency",
                "500",
                "ms",
                "High-frequency analysis"
            ), unsafe_allow_html=True)

    # ========== TAB 2: PREDICTIVE ANALYSIS ==========
    with tab2:
        st.markdown(SECTION_HEADER("🛤️", "Trajectory Prediction", "5-Minute Forecast"), unsafe_allow_html=True)
        
        col_pred1, col_pred2 = st.columns([1, 1])
        
        with col_pred1:
            prediction_window = st.slider("Prediction window (minutes)", 1, 10, 5, help="How far ahead to predict the helicopter trajectory")
        
        with col_pred2:
            confidence_threshold = st.slider("Confidence threshold (%)", 50, 100, 85, help="Minimum confidence for predictions")
        
        try:
            if hasattr(advanced_features, "TrajectoryPredictor"):
                tp = advanced_features.TrajectoryPredictor
                pred = tp.predict_trajectory(
                    st.session_state.aircraft, 
                    st.session_state.zones, 
                    prediction_minutes=prediction_window
                )
                
                # Display prediction results
                pred_col1, pred_col2, pred_col3 = st.columns(3)
                
                with pred_col1:
                    st.markdown(render_metric_box(
                        "Predicted Latitude",
                        f"{pred.get('latitude', 0):.5f}",
                        "°",
                        f"Confidence: {pred.get('confidence', 0):.0f}%"
                    ), unsafe_allow_html=True)
                    
                with pred_col2:
                    st.markdown(render_metric_box(
                        "Predicted Longitude",
                        f"{pred.get('longitude', 0):.5f}",
                        "°",
                        f"Accuracy: ±{pred.get('uncertainty', 0):.3f}°"
                    ), unsafe_allow_html=True)
                    
                with pred_col3:
                    st.markdown(render_metric_box(
                        "Predicted Altitude",
                        f"{pred.get('altitude', 0):.0f}",
                        "m",
                        "AGL elevation"
                    ), unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Detailed trajectory data
                with st.expander("📊 Detailed Trajectory Waypoints", expanded=False):
                    st.json(pred)
                    
        except Exception as e:
            st.error(f"❌ Trajectory prediction unavailable: {str(e)}")
            logger.exception("TrajectoryPredictor failed")

    # ========== TAB 3: RISK ASSESSMENT ==========
    with tab3:
        st.markdown(SECTION_HEADER("⚠️", "Risk Assessment", "Multi-Variable Analysis"), unsafe_allow_html=True)
        
        # Zone selection for risk analysis
        zones_df = st.session_state.zones
        selected_zone_idx = st.selectbox(
            "Select zone for analysis",
            options=zones_df.index,
            format_func=lambda i: f"{zones_df.loc[i, 'name']} (Score: {zones_df.loc[i, 'score']:.0f})",
            help="Choose a landing zone to analyze its risk profile"
        )
        selected_zone = zones_df.loc[selected_zone_idx].to_dict()
        
        st.markdown("---")
        
        try:
            if hasattr(advanced_features, "DynamicRiskMatrix"):
                drm = advanced_features.DynamicRiskMatrix
                risk_matrix = drm.calculate_risk_matrix(selected_zone, st.session_state.aircraft)
                
                # Risk summary cards
                risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
                
                with risk_col1:
                    overall_risk = risk_matrix.get("overall_risk_score", 0)
                    risk_level = "🔴 HIGH" if overall_risk > 70 else "🟡 MEDIUM" if overall_risk > 40 else "🟢 LOW"
                    st.markdown(render_metric_box(
                        "Overall Risk Score",
                        f"{overall_risk:.0f}",
                        "/ 100",
                        risk_level
                    ), unsafe_allow_html=True)
                    
                with risk_col2:
                    terrain_risk = risk_matrix.get("terrain_risk", 0)
                    st.markdown(render_metric_box(
                        "Terrain Risk",
                        f"{terrain_risk:.0f}",
                        "%",
                        f"Safety: {'Good' if terrain_risk < 40 else 'Fair' if terrain_risk < 70 else 'Poor'}"
                    ), unsafe_allow_html=True)
                    
                with risk_col3:
                    weather_risk = risk_matrix.get("weather_risk", 0)
                    st.markdown(render_metric_box(
                        "Weather Risk",
                        f"{weather_risk:.0f}",
                        "%",
                        f"Conditions: {'Optimal' if weather_risk < 30 else 'Challenging' if weather_risk < 60 else 'Hazardous'}"
                    ), unsafe_allow_html=True)
                    
                with risk_col4:
                    operational_risk = risk_matrix.get("operational_risk", 0)
                    st.markdown(render_metric_box(
                        "Operational Risk",
                        f"{operational_risk:.0f}",
                        "%",
                        f"Readiness: {'Excellent' if operational_risk < 35 else 'Good' if operational_risk < 65 else 'Compromised'}"
                    ), unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Risk factors breakdown
                st.subheader("Risk Factor Breakdown")
                
                risk_factors_col1, risk_factors_col2 = st.columns(2)
                
                with risk_factors_col1:
                    st.markdown("**Environmental Factors**")
                    env_factors = {
                        "Wind Speed": risk_matrix.get("wind_factor", 0),
                        "Visibility": risk_matrix.get("visibility_factor", 0),
                        "Surface Condition": risk_matrix.get("surface_factor", 0),
                        "Obstacles": risk_matrix.get("obstacles_factor", 0),
                    }
                    for factor, value in env_factors.items():
                        st.write(f"• {factor}: `{value:.1f}%`")
                        
                with risk_factors_col2:
                    st.markdown("**Aircraft Factors**")
                    aircraft_factors = {
                        "Fuel Level": risk_matrix.get("fuel_factor", 0),
                        "Structural Integrity": risk_matrix.get("structure_factor", 0),
                        "Engine Health": risk_matrix.get("engine_factor", 0),
                        "Crew Fatigue": risk_matrix.get("crew_factor", 0),
                    }
                    for factor, value in aircraft_factors.items():
                        st.write(f"• {factor}: `{value:.1f}%`")
                
                st.markdown("---")
                
                # Detailed risk matrix
                with st.expander("📈 Full Risk Matrix Data", expanded=False):
                    st.json(risk_matrix)
                    
        except Exception as e:
            st.error(f"❌ Risk assessment unavailable: {str(e)}")
            logger.exception("DynamicRiskMatrix failed")

    # ========== TAB 4: FLEET INTELLIGENCE ==========
    with tab4:
        st.markdown(SECTION_HEADER("⚕️", "Aircraft Health Diagnostics", "Predictive Maintenance"), unsafe_allow_html=True)
        
        health_refresh = st.button("🔄 Refresh Health Analysis", help="Re-run comprehensive system diagnostics")
        
        try:
            if hasattr(advanced_features, "PredictiveFailureAnalysis"):
                pfa = advanced_features.PredictiveFailureAnalysis
                health = pfa.assess_aircraft_health(st.session_state.aircraft)
                
                # Overall health gauge
                overall_health = health.get("overall_health_score", 0)
                health_status = "✅ EXCELLENT" if overall_health > 85 else "⚠️ GOOD" if overall_health > 70 else "🔴 CAUTION"
                
                st.markdown(f"""
                <div class="metric-box">
                    <div style="color: #8892b0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Aircraft Overall Health</div>
                    <div style="color: #00d4ff; font-size: 28px; font-weight: 700;">{overall_health:.1f}<span style="font-size: 18px; color: #cbd6ea;">%</span></div>
                    <div style="color: #6b7280; font-size: 11px; margin-top: 8px;">{health_status}</div>
                    <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; margin-top: 8px; overflow: hidden;">
                        <div style="width: {overall_health}%; height: 100%; background: linear-gradient(90deg, #22c55e, #00d4ff); border-radius: 3px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # System health breakdown
                st.subheader("System Component Health")
                
                systems = [
                    ("Engine", health.get("engine_health", 0)),
                    ("Transmission", health.get("transmission_health", 0)),
                    ("Hydraulics", health.get("hydraulics_health", 0)),
                    ("Avionics", health.get("avionics_health", 0)),
                    ("Structural", health.get("structural_health", 0)),
                    ("Fuel System", health.get("fuel_system_health", 0)),
                ]
                
                for system_name, health_value in systems:
                    status_icon = "🟢" if health_value > 80 else "🟡" if health_value > 60 else "🔴"
                    st.write(f"{status_icon} **{system_name}**: {health_value:.0f}%")
                    st.progress(health_value / 100)
                
                st.markdown("---")
                
                # Maintenance predictions
                st.subheader("Maintenance Predictions")
                
                if health.get("next_service_hours"):
                    col_maintenance1, col_maintenance2 = st.columns(2)
                    with col_maintenance1:
                        st.info(f"⏱️ **Next Service Due**: {health.get('next_service_hours', 'N/A')} hours")
                    with col_maintenance2:
                        st.warning(f"🔧 **Priority Inspections**: {health.get('priority_inspections', 'None identified')}")
                
                st.markdown("---")
                
                # Health trends
                with st.expander("📊 Detailed Health Report", expanded=False):
                    st.json(health)
                    
        except Exception as e:
            st.error(f"❌ Health assessment unavailable: {str(e)}")
            logger.exception("PredictiveFailureAnalysis failed")

def page_settings():
    st.markdown(SECTION_HEADER("⚙️", "Settings", "APPLICATION CONFIGURATION"), unsafe_allow_html=True)
    st.text_input("Owner / Project name", value="Your Name / Project")
    if st.button("Reset Session"):
        st.session_state.clear()
        st.experimental_rerun()

# -----------------------------
# Main entry
# -----------------------------
def init_session_state():
    if "aircraft" not in st.session_state:
        st.session_state.aircraft = get_demo_aircraft()
    if "zones" not in st.session_state:
        st.session_state.zones = get_demo_zones(st.session_state.aircraft["latitude"], st.session_state.aircraft["longitude"])
    if "sel_index" not in st.session_state:
        st.session_state.sel_index = 0
    if "mission_log" not in st.session_state:
        st.session_state.mission_log = []
    if "last_mission" not in st.session_state:
        st.session_state.last_mission = None

def main():
    st.set_page_config(page_title="ELZF-AI — Emergency Landing Simulator", layout="wide", initial_sidebar_state="expanded")
    inject_style()
    render_topbar()

    init_session_state()

    # Sidebar navigation
    st.sidebar.title("ELZF-AI")
    page = st.sidebar.radio("Navigate", ["Home", "Analysis", "Simulator", "Map", "Advanced", "Settings"])

    # Zone selection widget in sidebar
    zones = st.session_state.zones
    if not zones.empty:
        sel = st.sidebar.selectbox("Select landing zone", zones.index, format_func=lambda i: f"{zones.loc[i,'name']} ({zones.loc[i,'score']:.0f})", index=st.session_state.sel_index)
        st.session_state.sel_index = sel

    # Aircraft quick controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("Aircraft")
    st.sidebar.write(f"Type: {st.session_state.aircraft.get('type', 'H145')}")
    if st.sidebar.button("Play Alert Tone"):
        AircraftSoundSystem.play_sound_streamlit("alert")

    st.sidebar.markdown("---")
    st.sidebar.caption("ELZF-AI — keep simulator page open to run missions")

    # Render selected page
    if page == "Home":
        page_home()
    elif page == "Analysis":
        page_analysis()
    elif page == "Simulator":
        page_simulator()
    elif page == "Map":
        page_map()
    elif page == "Advanced":
        page_advanced()
    elif page == "Settings":
        page_settings()
    else:
        page_home()

    # Footer: mission log quick peek
    st.sidebar.markdown("---")
    st.sidebar.subheader("Mission Log")
    for i, m in enumerate(st.session_state.mission_log[-6:][::-1]):
        t = f"Mission {i+1}: start={m['start']} dest={m['dest']} distance={int(m['distance'])} m"
        st.sidebar.write(t)

if __name__ == "__main__":
    main()
