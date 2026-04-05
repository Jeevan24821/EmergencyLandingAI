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


def aircraft_icon_html(color="#ff6b35"):
    return f"""
    <div style="
        width:32px;height:32px;border-radius:50%;
        background:rgba(255,107,53,0.2);
        border:2px solid {color};
        display:flex;align-items:center;justify-content:center;
        box-shadow:0 0 12px {color}88;
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


def build_map(aircraft, zones_df):
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
                ALT: {aircraft['altitude']} ft<br>
                SPD: {aircraft['speed']} kts<br>
                ⚠ {aircraft['emergency']}<br>
                FUEL: <span style='color:#ff3d71'>{aircraft['fuel']}</span>
            </div>""",
            sticky=True
        ),
        icon=folium.DivIcon(
            html=aircraft_icon_html(),
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
                    Type: {row['type']}<br>
                    Distance: {km} km<br>
                    Wind: {row['wind']} kts<br>
                    Obstacles: {row['obstacles']}<br>
                    Visibility: {row.get('visibility','—')}<br>
                    Surface: {row.get('surface','—')}<br>
                    Area: {row['area']:,} m²
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
            radius=max(200, row["area"] / 10),
            color=col,
            fill=True,
            fill_color=col,
            fill_opacity=0.06,
            weight=1,
        ).add_to(m)

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
    </style>
    """
    m.get_root().html.add_child(folium.Element(map_css))

    return m
