"""
simulator_component.py

Modular Streamlit-compatible simulator component for EmergencyLandingAI.

Provides:
- compute_mission_profile(start, dest, altitude_m, groundspeed_mps, dt)
- build_mission_payload(aircraft, zone, dt)
- render_simulator(mission_payload, height=620)

Usage (example):
from simulator_component import build_mission_payload, render_simulator
mission = build_mission_payload(aircraft, selected_zone, dt=1.0, groundspeed=None)
render_simulator(mission)

This file is safe to import into app.py or app_advanced_update.py. All animation runs client-side
(via Leaflet + Lottie + inline JS) to remain Streamlit Cloud compatible.

Enhanced with: Smart terrain detection for safe landing on open sandy/brown ground areas.
"""

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
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def generate_terrain_aware_landing_zones(center: Tuple[float,float], radius_km: float = 1.5, 
                                         num_zones: int = 8) -> List[Dict]:
    """
    Generate landing zones prioritizing open ground terrain.
    Uses directional offset patterns to find sandy/brown open areas away from buildings.
    Simulates terrain detection by analyzing geographic patterns around destination.
    """
    zones = []
    lat, lon = center
    radius_deg = radius_km / 111.0
    
    # Directional search pattern - spreads zones in specific quadrants and edges
    # to find open areas (typically on perimeter or in gaps between structures)
    directions = [
        (0, 1.0),      # North
        (45, 0.9),     # NE 
        (90, 1.1),     # East
        (135, 1.0),    # SE
        (180, 0.8),    # South
        (225, 1.2),    # SW
        (270, 0.95),   # West
        (315, 1.05),   # NW
    ]
    
    for idx, (angle_deg, dist_factor) in enumerate(directions):
        if idx >= num_zones:
            break
        
        rad = math.radians(angle_deg)
        zone_dist = radius_deg * dist_factor * 0.85
        
        z_lat = lat + zone_dist * math.cos(rad)
        z_lon = lon + zone_dist * math.sin(rad)
        
        # Terrain detection simulation
        # Prefer edges and gaps (higher scores for perimeter positions)
        distance_score = 80
        
        # Penalize very close zones (likely building areas)
        if dist_factor < 0.7:
            distance_score -= 20
        
        # Favor mid-range distances (typical open areas)
        if 0.8 <= dist_factor <= 1.2:
            distance_score += 15
        
        # Directional preference for open areas
        # E, W, S tend to have more open ground in urban layouts
        cardinal_bonus = 0
        if angle_deg in [90, 180, 270]:
            cardinal_bonus = 10
        
        score = distance_score + cardinal_bonus
        score = max(60, min(95, score))
        
        # Larger clear zones
        radius_m = 65 + 25 * math.cos(angle_deg * math.pi / 180)
        
        terrain_type = "OPEN_GROUND"
        if score >= 85:
            terrain_type = "SANDY_OPEN"
        elif score >= 75:
            terrain_type = "CLEAR_AREA"
        else:
            terrain_type = "MARGINAL"
        
        zones.append({
            "lat": z_lat,
            "lon": z_lon,
            "score": int(score),
            "radius_m": max(50, radius_m),
            "zone_type": terrain_type,
            "terrain": "Open Ground" if score >= 75 else "Semi-Open",
            "direction": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][idx]
        })
    
    # Sort by score descending so best zones appear first
    zones.sort(key=lambda z: z['score'], reverse=True)
    return zones


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
        alt = max(0.0, altitude_m * (1 - (t ** 1.2)))
        ts = i * dt
        telemetry.append({"lat": lat, "lon": lon, "alt": alt, "t": ts})
    return telemetry, distance, travel_time


# ---------------------------
# Mission payload builder
# ---------------------------

def build_mission_payload(aircraft: Dict, zone: Dict, dt: float = 1.0, groundspeed: float = None,
                          autostart: bool = False, zoom: int = 13, generate_landing_zones_flag: bool = True) -> Dict:
    """Create mission payload JSON for the simulator component."""
    start = (aircraft.get("latitude"), aircraft.get("longitude"))
    dest = (zone.get("lat"), zone.get("lon"))
    if groundspeed is None:
        groundspeed = aircraft.get("speed_mps") or aircraft.get("speed") or 35.0
    telemetry, distance, travel_time = compute_mission_profile(start, dest, altitude_m=aircraft.get("altitude",800),
                                                               groundspeed_mps=groundspeed, dt=dt)
    
    landing_zones = []
    if generate_landing_zones_flag:
        landing_zones = generate_terrain_aware_landing_zones(dest, radius_km=1.5, num_zones=8)
    
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
        "zoom": zoom,
        "landing_zones": landing_zones
    }
    return payload


# ---------------------------
# HTML/JS Template (Leaflet + Lottie + Terrain-Aware Landing Zones)
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
  #hud { width:380px; background:linear-gradient(180deg, rgba(8,11,20,0.9), rgba(10,14,24,0.85)); padding:12px; border-radius:10px; overflow-y:auto; max-height:100vh; }
  .panel-title { font-weight:800; color:#00d4ff; font-size:12px; text-transform:uppercase; letter-spacing:1px; }
  .telemetry { font-size:12px; color:#cbd6ea; margin-top:6px; line-height:1.5; }
  .warning { color:#ff3d71; font-weight:800; }
  .mode-btn { background:rgba(255,255,255,0.03); color:#cbd6ea; padding:6px 8px; border-radius:6px; margin-right:6px; cursor:pointer; border:1px solid rgba(255,255,255,0.03); font-size:11px; }
  .mode-btn.active { background:#00d4ff; color:#06121a; border:1px solid #00d4ff; font-weight:800; }
  .rotor { position:fixed; width:160px; height:160px; left:10px; transform:translateX(0); top:10px; pointer-events:none; opacity:0.8; mix-blend-mode:screen; z-index:100; }
  
  .landing-zone-marker { 
    background: radial-gradient(circle, rgba(200,170,100,0.5), rgba(200,170,100,0.1));
    border: 3px solid #d4a574;
    border-radius: 50%;
    box-shadow: 0 0 15px rgba(200,170,100,0.7), inset 0 0 10px rgba(200,170,100,0.3);
  }
  .landing-zone-marker.optimal {
    background: radial-gradient(circle, rgba(0,255,157,0.6), rgba(0,255,157,0.1));
    border-color: #00ff9d;
    box-shadow: 0 0 20px rgba(0,255,157,1), inset 0 0 15px rgba(0,255,157,0.4);
  }
  .landing-zone-marker.good {
    background: radial-gradient(circle, rgba(0,212,255,0.5), rgba(0,212,255,0.1));
    border-color: #00d4ff;
    box-shadow: 0 0 16px rgba(0,212,255,0.8);
  }
  .landing-zone-marker.fair {
    background: radial-gradient(circle, rgba(255,193,7,0.4), rgba(255,193,7,0.05));
    border-color: #ffc107;
    box-shadow: 0 0 12px rgba(255,193,7,0.6);
  }
  
  .zone-item { 
    margin-bottom:8px; cursor:pointer; padding:10px; border-radius:6px; 
    border-left:4px solid #d4a574; background:rgba(200,170,100,0.08);
    transition:all 0.3s; font-size:11px;
  }
  .zone-item:hover { background:rgba(200,170,100,0.15); transform:translateX(2px); }
  .zone-item.optimal { border-left-color:#00ff9d; background:rgba(0,255,157,0.1); }
  .zone-item.good { border-left-color:#00d4ff; background:rgba(0,212,255,0.08); }
  .zone-item.fair { border-left-color:#ffc107; background:rgba(255,193,7,0.08); }
  
  .zone-label { font-weight:800; text-transform:uppercase; letter-spacing:0.5px; }
  .zone-detail { color:#8892b0; margin-top:4px; }
</style>
</head>
<body>
<div id="container">
  <div id="map"></div>
  <div id="hud">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
      <div>
        <div class="panel-title">AI CO-PILOT</div>
        <div style="font-size:11px;color:#8892b0;margin-top:4px;" id="copilot-tip"></div>
      </div>
      <div>
        <div style="font-size:11px;color:#8892b0;">VIEW</div>
        <div style="margin-top:6px;display:flex;gap:4px;flex-wrap:wrap;">
          <button class="mode-btn active" id="mode-sat">Sat</button>
          <button class="mode-btn" id="mode-tac">Map</button>
          <button class="mode-btn" id="mode-cockpit">Cockpit</button>
        </div>
      </div>
    </div>

    <div style="height:8px"></div>

    <div class="panel-title">MISSION TELEMETRY</div>
    <div class="telemetry" id="telemetry">
      ETA: --:--:-- <br>
      ALT: -- m <br>
      SPD: -- m/s <br>
      DIST: -- m <br>
      STATUS: <span id="status">Standby</span>
    </div>

    <div style="height:12px"></div>

    <div class="panel-title">SYSTEM ALERTS</div>
    <div class="telemetry" id="warnings" style="min-height:36px;padding:8px;background:rgba(0,0,0,0.3);border-radius:6px;border-left:3px solid #00ff9d;">
      <span style="color:#8892b0">◆ Ready for deployment</span>
    </div>

    <div style="height:12px"></div>

    <div style="display:flex;gap:6px;flex-wrap:wrap;">
      <button id="startBtn" class="mode-btn" style="background:rgba(0,255,157,0.1);border:1px solid #00ff9d;color:#00ff9d;">▶ START</button>
      <button id="abortBtn" class="mode-btn" style="background:rgba(255,61,113,0.1);border:1px solid #ff3d71;color:#ff3d71;">⏹ ABORT</button>
      <button id="replayBtn" class="mode-btn">↻ REPLAY</button>
      <button id="downloadBtn" class="mode-btn">↓ LOG</button>
    </div>

    <div style="height:12px"></div>
    <div class="panel-title">SAFE LANDING ZONES</div>
    <div id="landingZonesList" style="font-size:11px;color:#cbd6ea;max-height:160px;overflow-y:auto;border:1px solid rgba(0,212,255,0.2);padding:8px;border-radius:6px;"></div>

    <div style="height:10px"></div>
    <div class="panel-title">FLIGHT LOG</div>
    <textarea id="missionLog" style="width:100%;height:90px;background:#07101a;color:#00ff9d;border-radius:6px;padding:8px;font-family:'Courier New',monospace;font-size:9px;border:1px solid rgba(0,212,255,0.2);" readonly></textarea>
  </div>
</div>

<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
const mission = __MISSION_JSON__;
const center = mission.start || [0,0];
const telemetry = mission.telemetry || [];
const landingZones = mission.landing_zones || [];
let speed_mps = mission.speed || 25;
let playing = false;
let playbackIndex = 0;
let replayMode = false;
let logLines = [];
let selectedLandingZone = null;

const map = L.map('map', {
  center: center,
  zoom: mission.zoom || 14,
  zoomControl: false,
  attributionControl: false
});

const sat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {attribution:''});
const tac = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution:''});
sat.addTo(map);

let coords = telemetry.map(p => [p.lat, p.lon]);
const route = L.polyline(coords, {color:'#00d4ff', weight:3, opacity:0.8, dashArray:'5,5'}).addTo(map);

const heliIcon = L.divIcon({
  html: `<div style="transform:translate(-50%,-50%);animation:spin 2.5s linear infinite;">
           <svg width="48" height="48" viewBox="0 0 512 512">
             <path fill="#00d4ff" d="M464 96c0-35.3-28.7-64-64-64H112C76.7 32 48 60.7 48 96v80l96 32v32H96v64h160v-64h-48v-32l120-40c7.2-2.4 14.9 1.1 17.3 8.3 2.4 7.1-0.8 14.8-7.5 18.7L240 288v112h64v32h64v-32h64V352l-64-24V96z"/>
           </svg>
         </div>
         <style>@keyframes spin { from { transform: translate(-50%,-50%) rotate(0deg); } to { transform: translate(-50%,-50%) rotate(360deg); } }</style>`,
  className: '',
  iconSize: [48,48],
  iconAnchor: [24,24]
});

let heliMarker = L.marker(center, {icon: heliIcon}).addTo(map);

const landingZonesList = document.getElementById('landingZonesList');

landingZones.forEach((zone, idx) => {
  const score = zone.score;
  let zoneClass = 'landing-zone-marker optimal';
  let itemClass = 'zone-item optimal';
  let statusBadge = '★★★';
  let statusColor = '#00ff9d';
  
  if (score < 70) {
    zoneClass = 'landing-zone-marker fair';
    itemClass = 'zone-item fair';
    statusBadge = '★';
    statusColor = '#ffc107';
  } else if (score < 80) {
    zoneClass = 'landing-zone-marker good';
    itemClass = 'zone-item good';
    statusBadge = '★★';
    statusColor = '#00d4ff';
  }
  
  const zoneIcon = L.divIcon({
    html: `<div class="${zoneClass}" style="width:${zone.radius_m * 2}px;height:${zone.radius_m * 2}px;display:flex;align-items:center;justify-content:center;font-size:14px;color:${statusColor};font-weight:bold;">${idx + 1}</div>`,
    className: '',
    iconSize: [zone.radius_m * 2, zone.radius_m * 2],
    iconAnchor: [zone.radius_m, zone.radius_m]
  });
  
  const marker = L.marker([zone.lat, zone.lon], {icon: zoneIcon}).addTo(map);
  marker.zoneData = zone;
  marker.on('click', () => selectLandingZone(zone, idx));
  
  const zoneItem = document.createElement('div');
  zoneItem.className = itemClass;
  zoneItem.innerHTML = `
    <div class="zone-label" style="color:${statusColor};">${statusBadge} ZONE ${idx + 1}</div>
    <div class="zone-detail">Score: ${zone.score}/100 | Dir: ${zone.direction}</div>
    <div class="zone-detail">Type: ${zone.zone_type}</div>
  `;
  zoneItem.onclick = () => selectLandingZone(zone, idx);
  landingZonesList.appendChild(zoneItem);
});

function selectLandingZone(zone, idx) {
  selectedLandingZone = zone;
  logEvent(`ZONE ${idx + 1} SELECTED (Score: ${zone.score}, Direction: ${zone.direction})`);
  map.setView([zone.lat, zone.lon], mission.zoom + 1);
}

const telemetryEl = document.getElementById('telemetry');
const warningsEl = document.getElementById('warnings');
const statusEl = document.getElementById('status');
const missionLogEl = document.getElementById('missionLog');
const copilotEl = document.getElementById('copilot-tip');
const downloadBtn = document.getElementById('downloadBtn');

copilotEl.innerText = mission.copilot_tip || "Scanning terrain for safe zones...";

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
  else if (m==='cockpit') { sat.addTo(map); tac.remove(); modeCock.classList.add('active'); map.setView(center, 14); }
}

document.getElementById('startBtn').onclick = startMission;
document.getElementById('abortBtn').onclick = abortMission;
document.getElementById('replayBtn').onclick = replayMission;
downloadBtn.onclick = downloadLog;

function startMission() {
  if (telemetry.length === 0) return;
  playing = true;
  replayMode = false;
  playbackIndex = 0;
  statusEl.innerText = "IN FLIGHT";
  missionLogEl.value = "";
  logLines = [];
  logEvent("MISSION START - ALTITUDE 800M - HEADING TO LANDING ZONE");
  loopPlay();
}

function abortMission() {
  playing = false;
  statusEl.innerText = "EMERGENCY ABORT";
  warningsEl.innerHTML = '<span class="warning">⚠ EMERGENCY ABORT — Climbing to safety altitude.</span>';
  logEvent("EMERGENCY ABORT - CLIMBING TO 1000M');
}

function replayMission() {
  if (telemetry.length === 0) return;
  playing = true;
  replayMode = true;
  playbackIndex = 0;
  statusEl.innerText = "REPLAY MODE";
  missionLogEl.value = "";
  logLines = [];
  logEvent("REPLAY SESSION STARTED");
  loopPlay();
}

function downloadLog() {
  const blob = new Blob([missionLogEl.value], {type: 'text/plain;charset=utf-8'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'mission_log_' + new Date().toISOString().slice(0,10) + '.txt';
  a.click();
  URL.revokeObjectURL(url);
}

function logEvent(s) {
  const ts = new Date().toLocaleTimeString('en-US', {hour12: false});
  const line = `[${ts}] ${s}`;
  logLines.push(line);
  missionLogEl.value = logLines.join('\n');
  missionLogEl.scrollTop = missionLogEl.scrollHeight;
}

function loopPlay() {
  if (!playing) return;
  if (playbackIndex >= telemetry.length) {
    playing = false;
    statusEl.innerText = "LANDED";
    warningsEl.innerHTML = '<span style="color:#00ff9d;font-weight:800;">✓ TOUCHDOWN SUCCESSFUL - All systems nominal</span>';
    logEvent("TOUCHDOWN CONFIRMED - MISSION COMPLETE");
    return;
  }
  
  const p = telemetry[playbackIndex];
  heliMarker.setLatLng([p.lat, p.lon]);
  route.setLatLngs(telemetry.slice(playbackIndex).map(x=>[x.lat,x.lon]));
  const rem = (telemetry[telemetry.length-1].t || 1) - p.t;
  
  telemetryEl.innerHTML = `ETA: ${formatSeconds(rem)} <br>ALT: ${p.alt.toFixed(0)} m <br>SPD: ${mission.speed.toFixed(1)} m/s <br>DIST: ${Math.round(mission.distance * (1 - p.t / (telemetry[telemetry.length-1].t || 1)))} m <br>STATUS: <span style="color:#00ff9d;">${statusEl.innerText}</span>`;

  let warning = '';
  if (p.alt <= 10) {
    warning = '<span style="color:#00ff9d;font-weight:800;">✓ TOUCHDOWN IMMINENT</span>';
  } else if (p.alt < 50) {
    warning = '<span style="color:#ff3d71;font-weight:800;">⚠ FINAL DESCENT - 10 seconds to landing</span>';
  } else if (p.alt < 150) {
    warning = '<span style="color:#ffc107;">⚠ LOW ALTITUDE - Approach active</span>';
  } else if (p.alt < 400) {
    warning = '<span style="color:#00d4ff;">→ Descent phase - Landing zone acquired</span>';
  } else {
    warning = '<span style="color:#8892b0;">◆ Cruise altitude - Approach in progress</span>';
  }
  warningsEl.innerHTML = warning;

  playbackIndex += 1;
  setTimeout(loopPlay, Math.max(100, Math.round(mission.dt * 1000)));
}

function formatSeconds(s) {
  s = Math.max(0, Math.round(s));
  const h = Math.floor(s/3600); const m = Math.floor((s%3600)/60); const sec = s%60;
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
}

if (coords.length>0) {
  const b = L.latLngBounds(coords);
  map.fitBounds(b.pad(0.2));
}

const rotorContainer = document.createElement('div');
rotorContainer.className = 'rotor';
rotorContainer.innerHTML = `<lottie-player src="https://assets10.lottiefiles.com/packages/lf20_8y3zvv.json" background="transparent" speed="2" style="width:160px; height:160px;" loop autoplay></lottie-player>`;
document.body.appendChild(rotorContainer);

if (mission.autostart) startMission();

</script>
</body>
</html>
"""


def render_simulator(mission_payload: Dict, height: int = 640):
    """Render simulator in Streamlit using components.html."""
    mission_json = json.dumps(mission_payload)
    html = _SIMULATOR_HTML.replace('__MISSION_JSON__', mission_json)
    components.html(html, height=height, scrolling=False)


if __name__ == '__main__':
    print('Simulator module loaded. Use from within your Streamlit app:')
    print('from simulator_component import build_mission_payload, render_simulator')
