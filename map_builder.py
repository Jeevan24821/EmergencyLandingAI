import folium
import math
from folium import plugins


def score_color(score):
    if score > 80:  return "#00ff9d"
    if score > 55:  return "#00d4ff"
    if score > 30:  return "#ffb800"
    return "#ff3d71"


def dist_km(lat1, lon1, lat2, lon2):
    dLat = (lat2 - lat1) * math.pi / 180
    dLon = (lon2 - lon1) * math.pi / 180
    a = (math.sin(dLat/2)**2 +
         math.cos(lat1 * math.pi/180) *
         math.cos(lat2 * math.pi/180) *
         math.sin(dLon/2)**2)
    return round(6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 2)


def aircraft_icon_html(color="#ff6b35", is_editable=False):
    cursor_style = "cursor: pointer;" if is_editable else ""
    return f"""
    <div style="
        width:32px;height:32px;border-radius:50%;
        background:rgba(255,107,53,0.2);
        border:2px solid {color};
        display:flex;align-items:center;justify-content:center;
        box-shadow:0 0 12px {color}88;
        {cursor_style}
    ">
        <div style="font-size:18px">✈️</div>
    </div>
    """


def zone_icon_html(name, score, rank):
    col = score_color(score)
    bg  = col + "22"
    icon = "★" if rank == 0 else str(rank + 1)
    return f"""
    <div style="
        min-width:48px;padding:4px 8px;border-radius:8px;
        background:{bg};border:2px solid {col};
        text-align:center;
        box-shadow:0 0 10px {col}66;
        font-family:'Space Mono',monospace;
    ">
        <div style="font-size:14px;font-weight:700;color:{col}">{icon}</div>
        <div style="font-size:9px;color:{col};letter-spacing:0.05em">{name}</div>
        <div style="font-size:11px;font-weight:700;color:#fff">{score}</div>
    </div>
    """


def build_map(aircraft, zones_df, enable_placement=False, callback_key=None):
    """
    Build interactive map with aircraft and landing zones.
    
    Args:
        aircraft: Dict with aircraft data (latitude, longitude, altitude, speed, emergency, fuel)
        zones_df: DataFrame with landing zones
        enable_placement: Bool - Enable manual helicopter placement via click
        callback_key: Str - Key for storing clicked coordinates in streamlit session state
    
    Returns:
        folium.Map object
    """
    lat = aircraft["latitude"]
    lon = aircraft["longitude"]

    m = folium.Map(
        location=[lat, lon],
        zoom_start=13,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    # ── Aircraft marker ───────────────────────────────────
    folium.Marker(
        [lat, lon],
        tooltip=folium.Tooltip(
            f"""<div style='font-family:monospace;font-size:12px;background:#1a2240;color:#e8eaf6;
                            padding:8px 12px;border:1px solid rgba(0,212,255,0.3);border-radius:8px'>
                <b style='color:#ff6b35'>✈ AIRCRAFT</b><br>
                LAT: {lat:.5f}<br>LON: {lon:.5f}<br>
                ALT: {aircraft.get('altitude', 0)} ft<br>
                SPD: {aircraft.get('speed', 0)} kts<br>
                ⚠ {aircraft.get('emergency', 'None')}<br>
                FUEL: <span style='color:#ff3d71'>{aircraft.get('fuel', 'Unknown')}</span>
                {'<br><br><i style="color:#00ff9d">Click on map to place helicopter</i>' if enable_placement else ''}
            </div>""",
            sticky=True
        ),
        icon=folium.DivIcon(
            html=aircraft_icon_html(is_editable=enable_placement),
            icon_size=(36, 36),
            icon_anchor=(18, 18),
        )
    ).add_to(m)

    # ── Range circle ──────────────────────────────────────
    folium.Circle(
        location=[lat, lon],
        radius=5000,
        color="rgba(255,107,53,0.3)",
        fill=True,
        fill_color="rgba(255,107,53,0.03)",
        weight=1,
        dash_array="6 4",
        tooltip="5km emergency radius"
    ).add_to(m)

    # ── Zone markers + lines ──────────────────────────────
    for rank, (_, row) in enumerate(zones_df.iterrows()):
        col = score_color(row["score"])

        # Line from aircraft to zone
        folium.PolyLine(
            [[lat, lon], [row["lat"], row["lon"]]],
            color=col,
            weight=1.5,
            opacity=0.35,
            dash_array="4 6",
        ).add_to(m)

        km = dist_km(lat, lon, row["lat"], row["lon"])
        risk, _ = ("SAFE" if row["score"] > 80 else
                   "MODERATE" if row["score"] > 55 else
                   "CAUTION" if row["score"] > 30 else
                   "DANGER"), col

        folium.Marker(
            [row["lat"], row["lon"]],
            tooltip=folium.Tooltip(
                f"""<div style='font-family:monospace;font-size:12px;background:#1a2240;color:#e8eaf6;
                                padding:8px 12px;border:1px solid {col}55;border-radius:8px;min-width:170px'>
                    <b style='color:{col}'>{row['name']}  —  {risk}</b><br>
                    Score: <b style='color:{col}'>{row['score']}</b><br>
                    Type: {row.get('type', 'Unknown')}<br>
                    Distance: {km} km<br>
                    Wind: {row.get('wind', '—')} kts<br>
                    Obstacles: {row.get('obstacles', '—')}<br>
                    Visibility: {row.get('visibility','—')}<br>
                    Surface: {row.get('surface','—')}<br>
                    Area: {row.get('area', 0):,} m²
                </div>""",
                sticky=True
            ),
            icon=folium.DivIcon(
                html=zone_icon_html(row["name"], row["score"], rank),
                icon_size=(52, 56),
                icon_anchor=(26, 56),
            )
        ).add_to(m)

        # Radius circle per zone
        folium.Circle(
            location=[row["lat"], row["lon"]],
            radius=max(200, row.get('area', 0) / 10),
            color=col,
            fill=True,
            fill_color=col,
            fill_opacity=0.06,
            weight=1,
        ).add_to(m)

    # ── Click functionality for placement ──────────────────
    if enable_placement:
        click_html = """
        <div id="map-click-handler" style="display:none;"></div>
        <script>
        map.on('click', function(e) {
            var lat = e.latlng.lat;
            var lng = e.latlng.lng;
            console.log('Clicked at: ' + lat + ', ' + lng);
            // Store in a data attribute that can be read later
            document.getElementById('map-click-handler').setAttribute('data-lat', lat);
            document.getElementById('map-click-handler').setAttribute('data-lng', lng);
            document.getElementById('map-click-handler').setAttribute('data-clicked', 'true');
        });
        </script>
        """
        m.get_root().html.add_child(folium.Element(click_html))

    # ── Fullscreen plugin ─────────────────────────────────
    plugins.Fullscreen(
        position="topright",
        title="Fullscreen",
        title_cancel="Exit fullscreen",
    ).add_to(m)

    # ── Custom map style injection ─────────────────────────
    map_css = """
    <style>
    .leaflet-container {
        background: #080d18 !important;
        font-family: 'Space Mono', monospace !important;
    }
    .leaflet-tooltip {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    .leaflet-control-zoom a {
        background: #1a2240 !important;
        color: #00d4ff !important;
        border: 1px solid rgba(0,212,255,0.3) !important;
    }
    .leaflet-control-zoom a:hover {
        background: #253060 !important;
    }
    .leaflet-container {
        cursor: crosshair !important;
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(map_css))

    return m


def build_interactive_placement_map(aircraft, simulator_component):
    """
    Build a map with interactive helicopter placement capability.
    Returns zones predicted for the clicked location.
    
    Args:
        aircraft: Dict with initial aircraft data
        simulator_component: Module with generate_terrain_aware_landing_zones function
    
    Returns:
        tuple: (map_object, predicted_zones_list or None)
    """
    lat = aircraft["latitude"]
    lon = aircraft["longitude"]

    m = folium.Map(
        location=[lat, lon],
        zoom_start=13,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    # ── Current aircraft marker (draggable concept via click) ───────
    folium.Marker(
        [lat, lon],
        tooltip=folium.Tooltip(
            f"""<div style='font-family:monospace;font-size:12px;background:#1a2240;color:#e8eaf6;
                            padding:8px 12px;border:1px solid rgba(0,212,255,0.3);border-radius:8px;min-width:180px'>
                <b style='color:#ff6b35'>✈ AIRCRAFT (Click map to relocate)</b><br>
                Current LAT: {lat:.5f}<br>
                Current LON: {lon:.5f}<br>
                ALT: {aircraft.get('altitude', 0)} ft<br>
                SPD: {aircraft.get('speed', 0)} kts<br>
                ⚠ {aircraft.get('emergency', 'None')}<br>
                FUEL: <span style='color:#ff3d71'>{aircraft.get('fuel', 'Unknown')}</span>
            </div>""",
            sticky=True
        ),
        icon=folium.DivIcon(
            html=aircraft_icon_html(is_editable=True),
            icon_size=(36, 36),
            icon_anchor=(18, 18),
        ),
        popup=folium.Popup(
            f"Helicopter at ({lat:.5f}, {lon:.5f})<br>Click map to place new position",
            max_width=250
        )
    ).add_to(m)

    # ── Range circle ──────────────────────────────────────
    folium.Circle(
        location=[lat, lon],
        radius=5000,
        color="rgba(255,107,53,0.3)",
        fill=True,
        fill_color="rgba(255,107,53,0.03)",
        weight=1,
        dash_array="6 4",
        tooltip="5km search radius for landing zones"
    ).add_to(m)

    # ── Click to place functionality ───────────────────────
    click_handler = """
    <script>
    var placedMarker = null;
    var lastClickedLat = null;
    var lastClickedLng = null;
    
    map.on('click', function(e) {
        var lat = e.latlng.lat;
        var lng = e.latlng.lng;
        
        // Remove previous placed marker
        if (placedMarker) {
            map.removeLayer(placedMarker);
        }
        
        // Add new marker at clicked location
        placedMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                html: '<div style="width:28px;height:28px;border-radius:50%;background:rgba(0,255,157,0.2);border:2px solid #00ff9d;display:flex;align-items:center;justify-content:center;box-shadow:0 0 12px #00ff9d88;"><div style="font-size:16px">📍</div></div>',
                iconSize: [28, 28],
                iconAnchor: [14, 14]
            }),
            title: 'New Helicopter Position'
        }).bindPopup(`New Position: ${lat.toFixed(5)}, ${lng.toFixed(5)}<br><i>Close and predict zones</i>`).addTo(map);
        
        // Store clicked coordinates
        lastClickedLat = lat;
        lastClickedLng = lng;
        
        console.log('New position marked: ' + lat + ', ' + lng);
    });
    </script>
    """
    m.get_root().html.add_child(folium.Element(click_handler))

    # ── Fullscreen plugin ─────────────────────────────────
    plugins.Fullscreen(
        position="topright",
        title="Fullscreen",
        title_cancel="Exit fullscreen",
    ).add_to(m)

    # ── Custom map style injection ─────────────────────────
    map_css = """
    <style>
    .leaflet-container {
        background: #080d18 !important;
        font-family: 'Space Mono', monospace !important;
        cursor: crosshair !important;
    }
    .leaflet-tooltip {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    .leaflet-popup-content-wrapper {
        background: #1a2240 !important;
        border: 1px solid rgba(0,212,255,0.3) !important;
        border-radius: 8px !important;
    }
    .leaflet-popup-content {
        color: #e8eaf6 !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 12px !important;
    }
    .leaflet-control-zoom a {
        background: #1a2240 !important;
        color: #00d4ff !important;
        border: 1px solid rgba(0,212,255,0.3) !important;
    }
    .leaflet-control-zoom a:hover {
        background: #253060 !important;
    }
    .leaflet-control-attribution {
        background: rgba(26, 34, 64, 0.8) !important;
        color: #cbd6ea !important;
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(map_css))

    return m
