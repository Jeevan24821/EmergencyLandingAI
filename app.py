"""
app.py - Full integrated EmergencyLandingAI application
- Preserves existing functionality (charts, risk model, map builder, advanced features)
- Integrates a client-side helicopter mission simulator (simulator_component.py)
- Designed for Streamlit Cloud compatibility and contest-grade visuals

How to run:
    streamlit run app.py
"""

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
    import advanced_patent_features
except Exception:
    advanced_patent_features = None

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
    return f"<div style='padding:12px;color:#cbd6ea;'>Bar chart unavailable. Zones: {labels}</div>"

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
    else:
        # Minimal styling fallback
        st.markdown(
            """
            <style>
            body { background: #07101a; color:#cbd6ea; font-family: 'Space Mono', monospace; }
            .stButton > button { border-radius: 8px; }
            </style>
            """,
            unsafe_allow_html=True,
        )

def render_topbar():
    if styles_final and hasattr(styles_final, "TOPBAR_HTML"):
        st.markdown(styles_final.TOPBAR_HTML, unsafe_allow_html=True)
    else:
        st.markdown("<div style='padding:8px 0;color:#00d4ff;font-weight:700'>ELZF-AI — Emergency Landing Zone Finder</div>", unsafe_allow_html=True)

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

# -----------------------------
# Data helpers (use data_simulator if available)
# -----------------------------
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
        }
    # fallback static
    return {"latitude": 37.6190, "longitude": -122.375, "altitude": 800, "speed_mps": 35, "speed": 35,
            "heading": 0, "fuel": "MODERATE", "emergency": "Engine Failure", "passengers": 120}

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
    st.markdown(SECTION_HEADER("🏠", "Home", "OVERVIEW"))
    st.write("Welcome to ELZF-AI — Emergency Landing Zone Finder. Use the sidebar to navigate to Analysis, Simulator, Map and Advanced features.")
    st.markdown("---")
    st.write("Quick controls:")
    st.metric("Aircraft Type", st.session_state.aircraft.get("type", "H145"))
    st.metric("Last Mission Count", len(st.session_state.mission_log))

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
    st.markdown(SECTION_HEADER("🧠", "Advanced Patent Features", "PATENT-LEVEL AI MODULES"), unsafe_allow_html=True)
    if advanced_patent_features:
        # Render summaries of the module's functionality (non-invasive)
        st.write("This section exposes advanced features implemented in advanced_patent_features.py.")
        # Predictive trajectory demo
        try:
            tp = advanced_patent_features.TrajectoryPredictor
            pred = tp.predict_trajectory(st.session_state.aircraft, st.session_state.zones, prediction_minutes=5)
            st.subheader("Predicted Position (5 min)")
            st.json(pred)
        except Exception as e:
            st.write("Predictive trajectory unavailable:", e)
        # Health assessment
        try:
            pfa = advanced_patent_features.PredictiveFailureAnalysis
            health = pfa.assess_aircraft_health(st.session_state.aircraft)
            st.subheader("Aircraft Health")
            st.json(health)
        except Exception as e:
            st.write("Health analysis unavailable:", e)
        # Risk matrix demo
        try:
            drm = advanced_patent_features.DynamicRiskMatrix
            rm = drm.calculate_risk_matrix(st.session_state.zones.iloc[0].to_dict(), st.session_state.aircraft)
            st.subheader("Risk Matrix (sample zone)")
            st.json(rm)
        except Exception as e:
            st.write("Risk matrix unavailable:", e)
    else:
        st.warning("advanced_patent_features.py not found. This page shows a placeholder.")
        st.info("Place advanced_patent_features.py in the repo to unlock advanced AI features.")

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
        t = f"Mission {len(st.session_state.mission_log) - i}: dist={int(m.get('distance',0))}m ETA={int(m.get('travel_time',0))}s"
        st.sidebar.write(t)

if __name__ == "__main__":
    main()