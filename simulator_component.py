import streamlit as st
import streamlit.components.v1 as components
import json
import math
from typing import Tuple, List, Dict

# ---------------------------
# Mission telemetry helpers
# ---------------------------

def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in meters."""
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)*2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)*2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def compute_mission_profile(start: Tuple[float,float], dest: Tuple[float,float], altitude_m: float = 800.0,
                            groundspeed_mps: float = 35.0, dt: float = 1.0) -> Tuple[List[Dict], float, float]:
    """
    Precompute mission telemetry from start to dest.
    Returns (telemetry_list, distance_m, travel_time_s).
    telemetry entries: {lat, lon, alt, t}
    """
    lat1, lon1 = start
    lat2, lon2 = dest
    distance = haversine_meters(lat1, lon1, lat2, lon2)
    if groundspeed_mps <= 0:
        groundspeed_mps = 1.0
    travel_time = max(1.0, distance / groundspeed_mps)
    steps = max(2, int(math.ceil(travel_time / dt)))
    telemetry = []
    for i in range(steps + 1):
        t = i / steps
        lat = lat1 + (lat2 - lat1) * t
        lon = lon1 + (lon2 - lon1) * t
        # altitude reduces smoothly to zero (touchdown) with easing
        alt = max(0.0, altitude_m * (1 - (t ** 1.2)))
        ts = i * dt
        telemetry.append({"lat": lat, "lon": lon, "alt": alt, "t": ts})
    return telemetry, distance, travel_time


# ---------------------------
# Mission payload builder
# ---------------------------

def build_mission_payload(aircraft: Dict, zone: Dict, dt: float = 1.0, groundspeed: float = None,
                          autostart: bool = False, zoom: int = 13) -> Dict:
    """Create mission payload JSON for the simulator component."""
    start = (aircraft.get("latitude"), aircraft.get("longitude"))
    dest = (zone.get("lat"), zone.get("lon"))
    if groundspeed is None:
        groundspeed = aircraft.get("speed_mps") or aircraft.get("speed") or 35.0
    telemetry, distance, travel_time = compute_mission_profile(start, dest, altitude_m=aircraft.get("altitude",800),
                                                               groundspeed_mps=groundspeed, dt=dt)
    payload = {
        "start": [start[0], start[1]],
        "dest": [dest[0], dest[1]],
        "telemetry": telemetry,
        "speed": groundspeed,
        "distance": distance,
        "travel_time": travel_time,
        "copilot_tip": f"Approach {zone.get('name','Target')} — Score {zone.get('score',0):.0f}/100",
        "best_score": zone.get('score', 0),
        "dt": dt,
        "autostart": autostart,
        "zoom": zoom
    }
    return payload


# ---------------------------
# HTML/JS Template (Leaflet + Lottie)
# ---------------------------

_SIMULATOR_HTML = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
  html,body,#map { height:100%; margin:0; padding:0; background:#07101a; color:#cbd6ea; font-family: 'Space Mono', monospace; }
  #container { height:100%; display:flex; gap:12px; }
  #map { flex:1; border-radius:10px; overflow:hidden; box-shadow: 0 6px 20px rgba(0,0,0,0.6); }
  #hud { width:360px; background:linear-gradient(180deg, rgba(8,11,20,0.9), rgba(10,14,24,0.85)); padding:12px; border-radius:10px; }
  .panel-title { font-weight:800; color:#00d4ff; font-size:12px; }
  .telemetry { font-size:12px; color:#cbd6ea; margin-top:6px; }
  .warning { color:#ff3d71; font-weight:800; }
  .mode-btn { background:rgba(255,255,255,0.03); color:#cbd6ea; padding:6px 8px; border-radius:6px; margin-right:6px; cursor:pointer; border:1px solid rgba(255,255,255,0.03) }
  .mode-btn.active { background:#00d4ff; color:#06121a; border:1px solid #00d4ff; }
  .rotor { position:absolute; width:160px; height:160px; left:50%; transform:translateX(-50%); top:8px; pointer-events:none; opacity:0.95; mix-blend-mode:screen; }
</style>
</head>
<body>
<div id="container">
  <div id="map"></div>
  <div id="hud">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div>
        <div class="panel-title">AI CO-PILOT</div>
        <div style="font-size:11px;color:#8892b0;margin-top:4px;" id="copilot-tip"></div>
      </div>
      <div>
        <div style="font-size:11px;color:#8892b0;">VIEW</div>
        <div style="margin-top:6px;">
          <button class="mode-btn active" id="mode-sat">Satellite</button>
          <button class="mode-btn" id="mode-tac">Tactical</button>
          <button class="mode-btn" id="mode-cockpit">Cockpit</button>
        </div>
      </div>
    </div>

    <div style="height:10px"></div>

    <div class="panel-title">MISSION CONTROL</div>
    <div class="telemetry" id="telemetry">
      ETA: --:--:-- <br>
      ALT: -- m <br>
      SPD: -- m/s <br>
      DIST: -- m <br>
      STATUS: <span id="status">Idle</span>
    </div>

    <div style="height:12px"></div>

    <div class="panel-title">WARNINGS</div>
    <div class="telemetry" id="warnings" style="min-height:42px;">
      <span style="color:#8892b0">No active warnings.</span>
    </div>

    <div style="height:12px"></div>

    <div style="display:flex;gap:8px;flex-wrap:wrap;">
      <button id="startBtn" class="mode-btn">Start Mission</button>
      <button id="abortBtn" class="mode-btn">Abort</button>
      <button id="replayBtn" class="mode-btn">Replay</button>
      <button id="downloadBtn" class="mode-btn">Download Log</button>
    </div>

    <div style="height:10px"></div>
    <div class="panel-title">MISSION LOG</div>
    <textarea id="missionLog" style="width:100%;height:140px;background:#07101a;color:#cbd6ea;border-radius:6px;padding:8px;font-family:inherit;font-size:11px;" readonly></textarea>
  </div>
</div>

<!-- Lottie player for rotor and touchdown -->
<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
const mission = _MISSION_JSON_;
const center = mission.start || [0,0];
const telemetry = mission.telemetry || [];
let speed_mps = mission.speed || 25;
let playing = false;
let playbackIndex = 0;
let replayMode = false;
let logLines = [];

const map = L.map('map', {
  center: center,
  zoom: mission.zoom || 13,
  zoomControl: false,
  attributionControl: false
});

// Tile layers
const sat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {attribution:''});
const tac = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution:''});
sat.addTo(map);

// route polyline
let coords = telemetry.map(p => [p.lat, p.lon]);
const route = L.polyline(coords, {color:'#00d4ff', weight:3, opacity:0.8}).addTo(map);

// helicopter icon and marker
const heliIcon = L.divIcon({
  html: `<div style="transform:translate(-50%,-50%);">
           <svg width="46" height="46" viewBox="0 0 512 512">
             <path fill="#00d4ff" d="M464 96c0-35.3-28.7-64-64-64H112C76.7 32 48 60.7 48 96v80l96 32v32H96v64h160v-64h-48v-32l120-40c7.2-2.4 14.9 1.1 17.3 8.3 2.4 7.1-0.8 14.8-7.5 18.7L240 288v112h64v32h64v-32h64V352l-64-24V96z"/>
           </svg>
         </div>`,
  className: '',
  iconSize: [46,46],
  iconAnchor: [23,23]
});

let heliMarker = L.marker(center, {icon: heliIcon}).addTo(map);

// HUD elements
const telemetryEl = document.getElementById('telemetry');
const warningsEl = document.getElementById('warnings');
const statusEl = document.getElementById('status');
const missionLogEl = document.getElementById('missionLog');
const copilotEl = document.getElementById('copilot-tip');
const downloadBtn = document.getElementById('downloadBtn');

copilotEl.innerText = mission.copilot_tip || "Standby. Monitoring environment...";

// Modes
const modeSat = document.getElementById('mode-sat');
const modeTac = document.getElementById('mode-tac');
const modeCock = document.getElementById('mode-cockpit');
modeSat.onclick = ()=>{ setMode('sat'); };
modeTac.onclick = ()=>{ setMode('tac'); };
modeCock.onclick = ()=>{ setMode('cockpit'); };
function setMode(m) {
  modeSat.classList.remove('active'); modeTac.classList.remove('active'); modeCock.classList.remove('active');
  if (m==='sat') { sat.addTo(map); tac.remove(); modeSat.classList.add('active'); }
  else if (m==='tac') { tac.addTo(map); sat.remove(); modeTac.classList.add('active'); }
  else if (m==='cockpit') { sat.addTo(map); tac.remove(); modeCock.classList.add('active'); map.setView(center, mission.zoom || 14); }
}

// mission control buttons
document.getElementById('startBtn').onclick = startMission;
document.getElementById('abortBtn').onclick = abortMission;
document.getElementById('replayBtn').onclick = replayMission;
downloadBtn.onclick = downloadLog;

function startMission() {
  if (telemetry.length === 0) return;
  playing = true;
  replayMode = false;
  playbackIndex = 0;
  statusEl.innerText = "In Flight";
  missionLogEl.value = "";
  logLines = [];
  loopPlay();
}

function abortMission() {
  playing = false;
  statusEl.innerText = "ABORTED";
  warningsEl.innerHTML = '<span class="warning">EMERGENCY ABORT — Climb and divert.</span>';
  logEvent('ABORTED');
}

function replayMission() {
  if (telemetry.length === 0) return;
  playing = true;
  replayMode = true;
  playbackIndex = 0;
  statusEl.innerText = "REPLAY";
  missionLogEl.value = "";
  logLines = [];
  loopPlay();
}

function downloadLog() {
  const blob = new Blob([missionLogEl.value], {type: 'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'mission_log.txt';
  a.click();
  URL.revokeObjectURL(url);
}

function logEvent(s) {
  const line = ${new Date().toISOString()} ${s};
  logLines.push(line);
  missionLogEl.value = logLines.join('\n');
}

function loopPlay() {
  if (!playing) return;
  if (playbackIndex >= telemetry.length) {
    // landing complete
    playing = false;
    statusEl.innerText = "LANDED";
    warningsEl.innerHTML = '<span style="color:#00ff9d">Touchdown confirmed. Systems nominal.</span>';
    logEvent('TOUCHDOWN');
    return;
  }
  const p = telemetry[playbackIndex];
  heliMarker.setLatLng([p.lat, p.lon]);
  route.setLatLngs(telemetry.slice(playbackIndex).map(x=>[x.lat,x.lon]));
  const rem = (telemetry[telemetry.length-1].t || 1) - p.t;
  telemetryEl.innerHTML = ETA: ${formatSeconds(rem)} <br>ALT: ${p.alt.toFixed(0)} m <br>SPD: ${mission.speed.toFixed(1)} m/s <br>DIST: ${Math.round(mission.distance * (1 - p.t / (telemetry[telemetry.length-1].t || 1)))} m <br>STATUS: <span>${statusEl.innerText}</span>;

  if (p.alt < 100 && !replayMode) {
    warningsEl.innerHTML = '<span class="warning">LOW ALTITUDE — Prepare for touchdown</span>';
  } else if (mission.best_score && mission.best_score < 40) {
    warningsEl.innerHTML = '<span class="warning">ZONE RISK HIGH — Consider abort/divert</span>';
  } else {
    warningsEl.innerHTML = '<span style="color:#8892b0">No active warnings.</span>';
  }

  const logline = t=${p.t}s lat=${p.lat.toFixed(5)} lon=${p.lon.toFixed(5)} alt=${p.alt.toFixed(0)};
  logEvent(logline);
  playbackIndex += 1;
  setTimeout(loopPlay, Math.max(100, Math.round(mission.dt * 1000)));
}

function formatSeconds(s) {
  s = Math.max(0, Math.round(s));
  const h = Math.floor(s/3600); const m = Math.floor((s%3600)/60); const sec = s%60;
  return ${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')};
}

if (coords.length>0) {
  const b = L.latLngBounds(coords);
  map.fitBounds(b.pad(0.3));
}

// add simple rotor visual using lottie
const rotorContainer = document.createElement('div');
rotorContainer.className = 'rotor';
rotorContainer.innerHTML = <lottie-player src="https://assets10.lottiefiles.com/packages/lf20_8y3zvv.json"  background="transparent"  speed="2"  style="width:160px; height:160px;"  loop  autoplay></lottie-player>;
document.body.appendChild(rotorContainer);

if (mission.autostart) startMission();

</script>
</body>
</html>
"""


# ---------------------------
# Renderer
# ---------------------------

def render_simulator(mission_payload: Dict, height: int = 640):
    """Render simulator in Streamlit using components.html.

    mission_payload: dictionary returned by build_mission_payload
    """
    mission_json = json.dumps(mission_payload)
    html = SIMULATOR_HTML.replace('MISSION_JSON_', mission_json)
    components.html(html, height=height, scrolling=False)


# ---------------------------
# Minimal CLI test for local dev
# ---------------------------
if _name_ == '_main_':
    # quick demo when run directly (not via Streamlit)
    print('Simulator module loaded. Use from within your Streamlit app:')
    print('from simulator_component import build_mission_payload, render_simulator')
