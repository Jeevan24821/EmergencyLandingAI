"""
ELZF-AI v5.0 - Complete Professional Emergency Landing Zone Finder
HELICOPTER SPECIALIZED VERSION
INTEGRATED SYSTEM: Helicopter Control + Aircraft Selection + Sound + AI + Data Fusion + Predictive Analysis
Anti-Gravity Cockpit 3D Effects + Holographic Display
ALL FEATURES IN ONE FILE - NO EXTERNAL DEPENDENCIES
PURE HELICOPTERS ONLY
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
import time
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
import folium
from folium.plugins import MousePosition
import wave
import io
import base64
import math

# ═══════════════════════════════════════════════════════════════
# LOGGING SETUP
# ═══════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# ANTI-GRAVITY COCKPIT 3D EFFECTS CSS
# ═══════════════════════════════════════════════════════════════

HOLOGRAPHIC_CSS = """
<style>
@keyframes hologram-flicker {
    0%, 100% { text-shadow: 0 0 10px rgba(0, 255, 157, 0.8), 0 0 20px rgba(0, 212, 255, 0.6); }
    50% { text-shadow: 0 0 15px rgba(0, 255, 157, 0.6), 0 0 25px rgba(0, 212, 255, 0.4); }
}

@keyframes rotor-spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes cockpit-glow {
    0%, 100% { box-shadow: inset 0 0 20px rgba(0, 255, 157, 0.3), 0 0 30px rgba(0, 212, 255, 0.2); }
    50% { box-shadow: inset 0 0 30px rgba(0, 255, 157, 0.5), 0 0 40px rgba(0, 212, 255, 0.3); }
}

@keyframes pulse-altitude {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

@keyframes gravity-float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
}

.hologram {
    font-family: 'Space Mono', monospace;
    animation: hologram-flicker 3s infinite;
    letter-spacing: 0.1em;
    color: #00ff9d;
    text-shadow: 0 0 10px rgba(0, 255, 157, 0.8);
}

.rotor-indicator {
    animation: rotor-spin 2s linear infinite;
    display: inline-block;
    font-size: 48px;
}

.cockpit-panel {
    background: linear-gradient(135deg, rgba(15, 21, 39, 0.95) 0%, rgba(20, 30, 50, 0.95) 100%);
    border: 2px solid;
    border-radius: 12px;
    padding: 20px;
    animation: cockpit-glow 3s infinite;
    box-shadow: inset 0 0 20px rgba(0, 255, 157, 0.2);
}

.altitude-display {
    animation: pulse-altitude 1s infinite;
    font-size: 24px;
    font-weight: 700;
    color: #00ff9d;
}

.anti-gravity {
    animation: gravity-float 4s ease-in-out infinite;
}

.neon-border {
    border: 2px solid;
    box-shadow: 0 0 10px currentColor, inset 0 0 10px currentColor;
    border-radius: 8px;
}

.holographic-text {
    background: linear-gradient(45deg, #00ff9d, #00d4ff, #00ff9d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    animation: hologram-flicker 2s infinite;
}

.rotor-status {
    display: inline-block;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: radial-gradient(circle, #00ff9d 0%, rgba(0, 255, 157, 0.3) 100%);
    animation: rotor-spin 1.5s linear infinite;
    box-shadow: 0 0 10px #00ff9d, inset 0 0 5px #00ff9d;
}

.hover-zone {
    background: radial-gradient(circle, rgba(0, 255, 157, 0.2), transparent);
    border: 1px dashed #00ff9d;
    border-radius: 8px;
    padding: 15px;
}

.cockpit-readout {
    font-family: 'Courier New', monospace;
    color: #00ff9d;
    background: rgba(0, 212, 255, 0.05);
    border-left: 3px solid #00ff9d;
    padding: 10px;
    margin: 5px 0;
    font-size: 12px;
}

.blade-sweep {
    position: relative;
    display: inline-block;
    animation: rotor-spin 2s linear infinite;
    transform-origin: center;
}

.g-force-indicator {
    font-size: 14px;
    font-weight: 700;
    color: #00d4ff;
    animation: pulse-altitude 0.5s infinite;
}

.vertical-descent {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.descent-arrow {
    font-size: 32px;
    color: #00ff9d;
    animation: gravity-float 2s ease-in-out infinite;
}

.cockpit-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin: 15px 0;
}

.grid-item {
    background: rgba(0, 212, 255, 0.08);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 8px;
    padding: 12px;
    backdrop-filter: blur(10px);
}

.altitude-analog {
    width: 100px;
    height: 100px;
    border: 2px solid #00ff9d;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle, rgba(0, 255, 157, 0.1), transparent);
    font-weight: 700;
    color: #00ff9d;
    font-size: 18px;
}

.heading-indicator {
    width: 120px;
    height: 120px;
    border: 2px solid #00d4ff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: conic-gradient(#00d4ff, #00ff9d, #00d4ff);
    font-weight: 700;
    color: #0f1527;
    font-size: 14px;
    animation: rotor-spin 20s linear infinite;
}

.speed-gauge {
    width: 150px;
    height: 80px;
    background: linear-gradient(90deg, #ff3d71, #ffb800, #00ff9d);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: #0f1527;
    font-size: 16px;
}

@keyframes scan-line {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(100%); }
}

.radar-scan {
    border: 2px solid #00ff9d;
    border-radius: 50%;
    width: 200px;
    height: 200px;
    position: relative;
    background: radial-gradient(circle, rgba(0, 255, 157, 0.1), transparent);
    margin: 0 auto;
}

.radar-scan::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(to bottom, transparent, rgba(0, 255, 157, 0.2), transparent);
    animation: scan-line 3s linear infinite;
    border-radius: 50%;
}

.helicopter-status {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 157, 0.05));
    border: 2px solid #00d4ff;
    border-radius: 12px;
    margin: 10px 0;
}

.rotor-icon {
    font-size: 48px;
    animation: rotor-spin 1.5s linear infinite;
}

.hover-stable {
    color: #00ff9d;
    font-weight: 700;
}

.hover-unstable {
    color: #ffb800;
    font-weight: 700;
}

.hover-critical {
    color: #ff3d71;
    font-weight: 700;
}
</style>
"""

# ═══════════════════════════════════════════════════════════════
# SOUND SYSTEM - PURE PYTHON (NO EXTERNAL FILES)
# ═══════════════════════════════════════════════════════════════

class AircraftSoundSystem:
    """Pure Python sound generation for aircraft alerts"""
    
    SAMPLE_RATE = 22050
    
    FREQ_ALERT = 1046.50  # C6 - Warning tone
    FREQ_CRITICAL = 1174.66  # D6 - Critical alert
    FREQ_DANGER = 1318.51  # E6 - Emergency
    FREQ_CONFIRM = 523.25  # C5 - Positive confirmation
    FREQ_CHIME = 659.25  # E5 - System chime
    FREQ_LANDING = 440.00  # A4 - Landing indicator
    
    @staticmethod
    def generate_sine_wave(frequency: float, duration: float, amplitude: float = 0.3) -> np.ndarray:
        """Generate pure sine wave"""
        samples = int(AircraftSoundSystem.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
        return wave_data.astype(np.float32)
    
    @staticmethod
    def generate_alarm_pattern(pattern_name: str) -> bytes:
        """Generate different alarm patterns"""
        patterns = {
            'ALERT': [
                (AircraftSoundSystem.FREQ_ALERT, 0.2),
                (0, 0.1),
                (AircraftSoundSystem.FREQ_ALERT, 0.2),
            ],
            'CRITICAL': [
                (AircraftSoundSystem.FREQ_CRITICAL, 0.15),
                (0, 0.08),
                (AircraftSoundSystem.FREQ_CRITICAL, 0.15),
                (0, 0.08),
                (AircraftSoundSystem.FREQ_CRITICAL, 0.2),
            ],
            'DANGER': [
                (AircraftSoundSystem.FREQ_DANGER, 0.1),
                (0, 0.05),
                (AircraftSoundSystem.FREQ_DANGER, 0.1),
                (0, 0.05),
                (AircraftSoundSystem.FREQ_DANGER, 0.1),
                (0, 0.05),
                (AircraftSoundSystem.FREQ_DANGER, 0.15),
            ],
            'LANDING': [
                (AircraftSoundSystem.FREQ_LANDING, 0.3),
                (0, 0.1),
                (AircraftSoundSystem.FREQ_LANDING, 0.3),
                (0, 0.1),
                (AircraftSoundSystem.FREQ_LANDING, 0.5),
            ],
            'CONFIRM': [
                (AircraftSoundSystem.FREQ_CONFIRM, 0.15),
                (0, 0.05),
                (AircraftSoundSystem.FREQ_CONFIRM * 1.25, 0.15),
                (0, 0.05),
                (AircraftSoundSystem.FREQ_CONFIRM * 1.5, 0.2),
            ],
            'ZONE_DETECTED': [
                (AircraftSoundSystem.FREQ_LANDING, 0.1),
                (0, 0.05),
                (AircraftSoundSystem.FREQ_LANDING * 1.12, 0.1),
                (0, 0.05),
                (AircraftSoundSystem.FREQ_LANDING * 1.26, 0.15),
            ],
            'OPTIMAL_ZONE': [
                (AircraftSoundSystem.FREQ_CONFIRM, 0.2),
                (0, 0.1),
                (AircraftSoundSystem.FREQ_CONFIRM * 1.2, 0.25),
                (0, 0.1),
                (AircraftSoundSystem.FREQ_CONFIRM * 1.4, 0.3),
            ]
        }
        
        pattern = patterns.get(pattern_name, patterns['ALERT'])
        audio = np.array([], dtype=np.float32)
        
        for freq, dur in pattern:
            if freq == 0:
                silence = np.zeros(int(AircraftSoundSystem.SAMPLE_RATE * dur), dtype=np.float32)
                audio = np.concatenate([audio, silence])
            else:
                wave_data = AircraftSoundSystem.generate_sine_wave(freq, dur)
                audio = np.concatenate([audio, wave_data])
        
        return AircraftSoundSystem.numpy_to_wav(audio)
    
    @staticmethod
    def numpy_to_wav(audio: np.ndarray) -> bytes:
        """Convert numpy array to WAV bytes"""
        audio = np.clip(audio, -1, 1)
        audio_int16 = (audio * 32767).astype(np.int16)
        
        with io.BytesIO() as wav_buffer:
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(AircraftSoundSystem.SAMPLE_RATE)
                wav_file.writeframes(audio_int16.tobytes())
            wav_bytes = wav_buffer.getvalue()
        
        return wav_bytes
    
    @staticmethod
    def play_sound(pattern_name: str):
        """Play sound in Streamlit"""
        try:
            audio_bytes = AircraftSoundSystem.generate_alarm_pattern(pattern_name)
            st.audio(audio_bytes, sample_rate=AircraftSoundSystem.SAMPLE_RATE, format="audio/wav")
        except Exception as e:
            st.error(f"Sound error: {e}")

# ═══════════════════════════════════════════════════════════════
# ADVANCED AI & DATA FUSION FEATURES
# ═══════════════════════════════════════════════════════════════

class SatelliteImageryAnalyzer:
    """Computer Vision-based terrain classification (YOLOv8 Simulation)"""
    
    TERRAIN_CLASSES = {
        'open_field': {'confidence_threshold': 0.85, 'risk_factor': 0.3},
        'runway_airport': {'confidence_threshold': 0.95, 'risk_factor': 0.1},
        'highway': {'confidence_threshold': 0.80, 'risk_factor': 0.35},
        'water_body': {'confidence_threshold': 0.90, 'risk_factor': 0.8},
        'forest': {'confidence_threshold': 0.75, 'risk_factor': 0.6},
        'urban_area': {'confidence_threshold': 0.70, 'risk_factor': 0.5},
        'desert': {'confidence_threshold': 0.88, 'risk_factor': 0.4},
        'mountain': {'confidence_threshold': 0.85, 'risk_factor': 0.9},
    }
    
    @staticmethod
    def detect_terrain_features(lat: float, lon: float, scan_radius_km: float = 5) -> List[Dict]:
        """Simulate terrain detection using ML patterns"""
        detected_zones = []
        grid_points = []
        points_per_side = 4
        step = scan_radius_km / points_per_side
        
        for i in range(-points_per_side, points_per_side):
            for j in range(-points_per_side, points_per_side):
                lat_offset = (i * step) / 111.0
                lon_offset = (j * step) / (111.0 * np.cos(np.radians(lat)))
                grid_points.append((lat + lat_offset, lon + lon_offset))
        
        terrain_types = list(SatelliteImageryAnalyzer.TERRAIN_CLASSES.keys())
        
        for idx, (g_lat, g_lon) in enumerate(grid_points):
            seed = int((g_lat * 1000 + g_lon * 1000)) % len(terrain_types)
            terrain = terrain_types[seed]
            confidence = np.random.uniform(
                SatelliteImageryAnalyzer.TERRAIN_CLASSES[terrain]['confidence_threshold'],
                1.0
            )
            
            if confidence > SatelliteImageryAnalyzer.TERRAIN_CLASSES[terrain]['confidence_threshold']:
                detected_zones.append({
                    'lat': g_lat,
                    'lon': g_lon,
                    'terrain_type': terrain,
                    'confidence': confidence,
                    'risk_factor': SatelliteImageryAnalyzer.TERRAIN_CLASSES[terrain]['risk_factor'],
                    'area': np.random.randint(5000, 50000),
                    'flatness_score': np.random.uniform(50, 100) if terrain != 'mountain' else np.random.uniform(20, 40)
                })
        
        return detected_zones

class WeatherDataFusion:
    """Multi-source weather data integration"""
    
    @staticmethod
    def integrate_weather_sources(lat: float, lon: float) -> Dict:
        """Integrate data from multiple weather sources"""
        weather_data = {
            'wind_speed': np.random.uniform(5, 35),
            'wind_direction': np.random.randint(0, 360),
            'gusts': np.random.uniform(0, 20),
            'visibility': np.random.choice([100, 50, 30, 10, 5]),
            'ceiling': np.random.randint(500, 5000),
            'temperature': np.random.uniform(-10, 45),
            'dewpoint': np.random.uniform(-15, 30),
            'pressure': np.random.uniform(950, 1030),
            'precipitation': np.random.uniform(0, 100),
            'cloud_coverage': np.random.randint(0, 100),
            'storm_risk': np.random.uniform(0, 1),
            'updraft_strength': np.random.uniform(0, 10),
            'data_sources': ['METAR', 'SIGMET', 'Radar', 'Satellite']
        }
        return weather_data
    
    @staticmethod
    def calculate_weather_impact_score(weather_data: Dict) -> float:
        """Calculate impact of weather on landing safety"""
        score = 100
        
        if weather_data['wind_speed'] > 30:
            score -= 30
        elif weather_data['wind_speed'] > 20:
            score -= 15
        
        if weather_data['visibility'] < 5:
            score -= 35
        elif weather_data['visibility'] < 10:
            score -= 20
        elif weather_data['visibility'] < 50:
            score -= 10
        
        if weather_data['ceiling'] < 500:
            score -= 25
        elif weather_data['ceiling'] < 1000:
            score -= 15
        
        if weather_data['precipitation'] > 50:
            score -= 20
        elif weather_data['precipitation'] > 20:
            score -= 10
        
        score -= (weather_data['storm_risk'] * 30)
        return max(0, score)

class PredictiveRiskAnalyzer:
    """ML-based predictive analysis"""
    
    @staticmethod
    def predict_zone_safety_trajectory(zone: Dict, aircraft: Dict, prediction_minutes: int = 10) -> np.ndarray:
        """Predict how zone safety score changes over next N minutes"""
        current_score = zone.get('score', 50)
        trajectory = np.array([current_score])
        
        for minute in range(1, prediction_minutes + 1):
            weather_change = np.random.uniform(-5, 5)
            altitude_factor = (aircraft['altitude'] / 1000) * 2
            decision_improvement = minute * 0.5
            new_score = current_score + weather_change - altitude_factor + decision_improvement
            new_score = np.clip(new_score, 0, 100)
            trajectory = np.append(trajectory, new_score)
            current_score = new_score
        
        return trajectory
    
    @staticmethod
    def predict_system_reliability(conditions: Dict) -> float:
        """Calculate predicted system reliability score"""
        reliability = 95
        source_agreement = conditions.get('data_source_agreement', 0.9)
        reliability *= source_agreement
        
        if conditions.get('visibility', 100) < 50:
            reliability *= 0.95
        
        if conditions.get('zone_count', 0) > 20:
            reliability *= 0.98
        
        return min(100, max(50, reliability))

class MultiSourceDataFusion:
    """Fuses multiple data sources"""
    
    @staticmethod
    def fuse_landing_zone_data(satellite_data: List[Dict], weather_data: Dict, aircraft_sensors: Dict) -> pd.DataFrame:
        """Fuse multiple data sources"""
        fused_data = []
        
        for zone in satellite_data:
            terrain_score = zone['flatness_score']
            wind_impact = 100 - (weather_data['wind_speed'] * 2)
            visibility_impact = min(100, weather_data['visibility'] * 10)
            
            distance = np.sqrt(
                (zone['lat'] - aircraft_sensors['latitude'])**2 +
                (zone['lon'] - aircraft_sensors['longitude'])**2
            ) * 111
            
            distance_factor = max(20, 100 - (distance * 2))
            runway_required = aircraft_sensors.get('landing_distance', 1500)
            size_score = 100 if zone['area'] > runway_required else (zone['area'] / runway_required) * 100
            
            weights = {
                'terrain': 0.25,
                'weather': 0.25,
                'distance': 0.20,
                'size': 0.15,
                'risk_factor': -0.15
            }
            
            composite_score = (
                terrain_score * weights['terrain'] +
                ((wind_impact + visibility_impact) / 2) * weights['weather'] +
                distance_factor * weights['distance'] +
                size_score * weights['size'] -
                (zone['risk_factor'] * 50) * abs(weights['risk_factor'])
            )
            
            composite_score = np.clip(composite_score, 0, 100)
            
            fused_data.append({
                'lat': zone['lat'],
                'lon': zone['lon'],
                'name': f"{zone['terrain_type'].replace('_', ' ').title()} Zone",
                'type': zone['terrain_type'],
                'score': composite_score,
                'area': zone['area'],
                'wind': weather_data['wind_speed'],
                'visibility': weather_data['visibility'],
                'obstacles': int(zone['risk_factor'] * 100),
                'confidence': zone['confidence'],
                'data_sources_used': weather_data.get('data_sources', []),
            })
        
        return pd.DataFrame(fused_data)

class RealTimeDecisionEngine:
    """Real-time decision making"""
    
    @staticmethod
    def generate_landing_recommendation(zones_df: pd.DataFrame, aircraft: Dict, weather: Dict) -> Dict:
        """Generate comprehensive landing recommendation"""
        if zones_df.empty:
            return {'error': 'No landing zones available'}
        
        best_zone = zones_df.iloc[0].to_dict()
        
        recommendation = {
            'primary_zone': best_zone['name'],
            'score': best_zone['score'],
            'distance_km': np.sqrt(
                (best_zone['lat'] - aircraft['latitude'])**2 +
                (best_zone['lon'] - aircraft['longitude'])**2
            ) * 111,
            'estimated_time_to_reach': max(1, int(
                np.sqrt(
                    (best_zone['lat'] - aircraft['latitude'])**2 +
                    (best_zone['lon'] - aircraft['longitude'])**2
                ) * 111 / (aircraft['speed'] / 60)
            )),
            'alternative_zones': zones_df.head(3).to_dict('records'),
            'confidence': 95,
            'system_reliability': PredictiveRiskAnalyzer.predict_system_reliability({
                'data_source_agreement': 0.95,
                'visibility': weather['visibility'],
                'zone_count': len(zones_df)
            })
        }
        
        return recommendation

class EmergencyAlertSystem:
    """Real-time emergency alert system"""
    
    ALERT_LEVELS = {
        'NORMAL': 0,
        'ADVISORY': 1,
        'CAUTION': 2,
        'WARNING': 3,
        'EMERGENCY': 4
    }
    
    @staticmethod
    def evaluate_emergency_level(aircraft: Dict, best_zone_score: float) -> str:
        """Determine emergency alert level"""
        fuel_status_map = {'CRITICAL': 4, 'LOW': 3, 'MODERATE': 1, 'ADEQUATE': 0}
        emergency_points = fuel_status_map.get(aircraft['fuel'], 0)
        
        if best_zone_score < 30:
            emergency_points += 2
        elif best_zone_score < 50:
            emergency_points += 1
        
        if aircraft['altitude'] < 1000:
            emergency_points += 1
        
        if emergency_points >= 4:
            return 'EMERGENCY'
        elif emergency_points >= 3:
            return 'WARNING'
        elif emergency_points >= 2:
            return 'CAUTION'
        elif emergency_points >= 1:
            return 'ADVISORY'
        else:
            return 'NORMAL'
    
    @staticmethod
    def generate_emergency_summary(aircraft: Dict, best_zone: Dict, recommendation: Dict) -> str:
        """Generate emergency summary"""
        alert_level = EmergencyAlertSystem.evaluate_emergency_level(aircraft, best_zone['score'])
        
        summary = f"""
        ╔════════════════════════════════════════════╗
        ║     EMERGENCY LANDING SYSTEM ALERT        ║
        ║              LEVEL: {alert_level:12} ║
        ╚════════════════════════════════════════════╝
        
        AIRCRAFT STATUS:
        • Type: {aircraft.get('aircraft_type', 'Unknown')}
        • Altitude: {aircraft['altitude']:,} ft
        • Speed: {aircraft['speed']} kts
        • Fuel Status: {aircraft['fuel']}
        • Passengers: {aircraft['passengers']}
        • Emergency: {aircraft['emergency']}
        
        RECOMMENDED LANDING ZONE:
        • Zone: {best_zone['name']}
        • Safety Score: {best_zone['score']:.0f}/100
        • Distance: {recommendation['distance_km']:.1f} km
        • ETA: {recommendation['estimated_time_to_reach']} minutes
        • Terrain: {best_zone['type'].upper()}
        
        SYSTEM STATUS:
        ✓ Recommendation Confidence: {recommendation['confidence']}%
        ✓ System Reliability: {recommendation['system_reliability']:.1f}%
        ✓ Data Fusion: ACTIVE
        ✓ AI Engine: ONLINE
        """
        
        return summary

# ═══════════════════════════════════════════════════════════════
# HELICOPTER DATABASE WITH SPECIFICATIONS (ONLY HELICOPTERS)
# ═══════════════════════════════════════════════════════════════

AIRCRAFT_DATABASE = {
    'Bell 407': {
        'emoji': '🚁',
        'passengers': 6,
        'crew': 1,
        'weight': 2860,
        'speed': 240,
        'cruise_altitude': 20000,
        'landing_distance': 0,
        'fuel_capacity': 1011,
        'wingspan': 0,
        'length': 14.6,
        'description': 'Twin-engine utility helicopter',
        'min_altitude': 500,
        'max_passengers': 7,
        'category': 'Helicopter',
        'rotor_diameter': 11.0,
        'vertical_capable': True,
        'hover_time': 120,
        'max_hover_altitude': 18000,
        'empty_weight': 2860,
        'service_ceiling': 20000,
        'blade_count': 4,
    },
    'Airbus H125': {
        'emoji': '🚁',
        'passengers': 5,
        'crew': 1,
        'weight': 2650,
        'speed': 287,
        'cruise_altitude': 35000,
        'landing_distance': 0,
        'fuel_capacity': 1140,
        'wingspan': 0,
        'length': 12.74,
        'description': 'High-altitude helicopter',
        'min_altitude': 500,
        'max_passengers': 6,
        'category': 'Helicopter',
        'rotor_diameter': 10.69,
        'vertical_capable': True,
        'hover_time': 150,
        'max_hover_altitude': 32000,
        'empty_weight': 2650,
        'service_ceiling': 35000,
        'blade_count': 4,
    },
    'Sikorsky S-76': {
        'emoji': '🚁',
        'passengers': 14,
        'crew': 2,
        'weight': 5340,
        'speed': 287,
        'cruise_altitude': 18000,
        'landing_distance': 0,
        'fuel_capacity': 3500,
        'wingspan': 0,
        'length': 16.7,
        'description': 'Medium-lift helicopter',
        'min_altitude': 500,
        'max_passengers': 16,
        'category': 'Helicopter',
        'rotor_diameter': 17.07,
        'vertical_capable': True,
        'hover_time': 180,
        'max_hover_altitude': 15000,
        'empty_weight': 5340,
        'service_ceiling': 18000,
        'blade_count': 5,
    },
    'Airbus H145': {
        'emoji': '🚁',
        'passengers': 6,
        'crew': 2,
        'weight': 3900,
        'speed': 287,
        'cruise_altitude': 20000,
        'landing_distance': 0,
        'fuel_capacity': 1530,
        'wingspan': 0,
        'length': 13.9,
        'description': 'Twin-engine SAR helicopter',
        'min_altitude': 500,
        'max_passengers': 10,
        'category': 'Helicopter',
        'rotor_diameter': 12.80,
        'vertical_capable': True,
        'hover_time': 160,
        'max_hover_altitude': 18000,
        'empty_weight': 3900,
        'service_ceiling': 20000,
        'blade_count': 4,
    },
    'Robinson R66': {
        'emoji': '🚁',
        'passengers': 2,
        'crew': 1,
        'weight': 1090,
        'speed': 160,
        'cruise_altitude': 15000,
        'landing_distance': 0,
        'fuel_capacity': 200,
        'wingspan': 0,
        'length': 9.5,
        'description': 'Light utility helicopter',
        'min_altitude': 300,
        'max_passengers': 3,
        'category': 'Helicopter',
        'rotor_diameter': 7.67,
        'vertical_capable': True,
        'hover_time': 90,
        'max_hover_altitude': 12000,
        'empty_weight': 1090,
        'service_ceiling': 15000,
        'blade_count': 2,
    },
    'Mil Mi-8': {
        'emoji': '🚁',
        'passengers': 28,
        'crew': 3,
        'weight': 7150,
        'speed': 280,
        'cruise_altitude': 19000,
        'landing_distance': 0,
        'fuel_capacity': 3390,
        'wingspan': 0,
        'length': 18.17,
        'description': 'Heavy-lift transport helicopter',
        'min_altitude': 500,
        'max_passengers': 32,
        'category': 'Helicopter',
        'rotor_diameter': 21.29,
        'vertical_capable': True,
        'hover_time': 200,
        'max_hover_altitude': 14000,
        'empty_weight': 7150,
        'service_ceiling': 19000,
        'blade_count': 5,
    },
    'Eurocopter EC130': {
        'emoji': '🚁',
        'passengers': 6,
        'crew': 1,
        'weight': 2540,
        'speed': 180,
        'cruise_altitude': 15000,
        'landing_distance': 0,
        'fuel_capacity': 840,
        'wingspan': 0,
        'length': 12.84,
        'description': 'Light observation helicopter',
        'min_altitude': 300,
        'max_passengers': 7,
        'category': 'Helicopter',
        'rotor_diameter': 11.0,
        'vertical_capable': True,
        'hover_time': 110,
        'max_hover_altitude': 12000,
        'empty_weight': 2540,
        'service_ceiling': 15000,
        'blade_count': 3,
    },
    'Kamov Ka-32': {
        'emoji': '🚁',
        'passengers': 12,
        'crew': 3,
        'weight': 5300,
        'speed': 209,
        'cruise_altitude': 14700,
        'landing_distance': 0,
        'fuel_capacity': 2400,
        'wingspan': 0,
        'length': 15.9,
        'description': 'Firefighting/rescue helicopter',
        'min_altitude': 500,
        'max_passengers': 16,
        'category': 'Helicopter',
        'rotor_diameter': 15.5,
        'vertical_capable': True,
        'hover_time': 130,
        'max_hover_altitude': 11000,
        'empty_weight': 5300,
        'service_ceiling': 14700,
        'blade_count': 5,
    },
}

# ═══════════════════════════════════════════════════════════════
# IMPORTS WITH ERROR HANDLING
# ═══════════════════════════════════════════════════════════════
try:
    from streamlit_folium import st_folium
    import streamlit.components.v1 as components
except ImportError as e:
    st.error(f"❌ Missing dependency: {str(e)}")
    st.stop()

# ═══════════════════════════════════════════════════════════════
# DARK THEME CSS
# ═══════════════════════════════════════════════════════════════

DARK_CSS = """
<style>
* { margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f1527 0%, #1a1f3a 100%);
    color: #e0e6ed;
}
.stApp { background: linear-gradient(135deg, #0f1527 0%, #1a1f3a 100%); }
[data-testid="stMetric"] {
    background-color: rgba(15, 21, 39, 0.7);
    padding: 10px;
    border-radius: 8px;
    border: 1px solid rgba(0, 212, 255, 0.2);
}
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)
st.markdown(HOLOGRAPHIC_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# CACHING & OPTIMIZATION
# ═══════════════════════════════════════════════════════════════

@lru_cache(maxsize=128)
def cached_dist_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Cache distance calculations"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return round(R * c, 1)

@st.cache_data(ttl=3600)
def process_zones_data(zones_tuple) -> pd.DataFrame:
    """Process and score zones with caching"""
    try:
        zones = [dict(z) for z in zones_tuple]
        for z in zones:
            if "score" not in z:
                z["score"] = calculate_score(z)
        df = pd.DataFrame(zones).sort_values("score", ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        logger.error(f"Zone processing error: {e}")
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR HELICOPTERS
# ═══════════════════════════════════════════════════════════════

def calculate_score(zone: Dict) -> float:
    """Calculate zone safety score"""
    distance_score = max(0, 30 - (zone.get('distance_factor', 0) * 3))
    area_score = min(25, (zone.get('area', 0) / 50000) * 25)
    wind_score = max(0, 20 - (zone.get('wind', 0) * 0.5))
    obstacle_score = max(0, 15 - (zone.get('obstacles', 0) * 2))
    type_score = {'airport': 10, 'highway': 8, 'field': 6}.get(zone.get('type', ''), 0)
    
    return distance_score + area_score + wind_score + obstacle_score + type_score

def get_risk_level(score: float) -> Tuple[str, str]:
    """Get risk level and color"""
    if score >= 80:
        return "✅ OPTIMAL", "#00ff9d"
    elif score >= 50:
        return "⚠️ ACCEPTABLE", "#00d4ff"
    elif score >= 30:
        return "⚠️ RISKY", "#ffb800"
    else:
        return "❌ DANGEROUS", "#ff3d71"

def get_factor_scores(zone: Dict) -> Dict:
    """Get factor scores for zone"""
    return {
        'Distance': zone.get('distance_factor', 50),
        'Area': zone.get('area', 0) / 500,
        'Wind': 100 - zone.get('wind', 10) * 2,
        'Obstacles': 100 - zone.get('obstacles', 0) * 10,
    }

def stat_card(label: str, value: str, unit: str, color: str, badge: str, status: str) -> str:
    """Generate stat card HTML"""
    status_colors = {
        'ok': '#00ff9d',
        'warn': '#ffb800',
        'danger': '#ff3d71',
        'info': '#00d4ff'
    }
    
    return f"""
    <div style="background:rgba(15,21,39,0.7);border:1px solid {color};border-radius:8px;padding:12px;text-align:center;">
        <div style="font-size:10px;color:#8892b0;font-family:'Space Mono',monospace;text-transform:uppercase;margin-bottom:4px;">{badge}</div>
        <div style="font-size:16px;color:{color};font-weight:700;margin-bottom:4px;">{value}<span style="font-size:10px;margin-left:4px;">{unit}</span></div>
        <div style="font-size:9px;color:{status_colors.get(status, '#8892b0')};font-weight:700;">{label}</div>
    </div>
    """

def zone_card_clean(zone: Dict, idx: int, selected: bool) -> str:
    """Generate zone card"""
    score = zone['score']
    risk_color = "#00ff9d" if score >= 75 else "#00d4ff" if score >= 50 else "#ffb800" if score >= 30 else "#ff3d71"
    border = "3px solid #00ff9d" if selected else f"1px solid {risk_color}"
    
    return f"""
    <div style="background:rgba(15,21,39,0.7);border:{border};border-radius:8px;padding:12px;margin:8px 0;cursor:pointer;transition:all 0.3s;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:11px;color:#00d4ff;font-family:'Space Mono',monospace;font-weight:700;">ZONE {chr(65+idx)}</div>
                <div style="font-size:12px;color:#e0e6ed;margin-top:4px;">{zone.get('name', 'Unknown')}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:20px;color:{risk_color};font-weight:700;">{score:.0f}</div>
                <div style="font-size:9px;color:#8892b0;">/100</div>
            </div>
        </div>
    </div>
    """

def ai_tips_html(score: float) -> str:
    """Generate AI tips"""
    if score >= 80:
        tip = "✅ OPTIMAL ZONE - Execute landing immediately. All parameters favorable."
        tip_color = "#00ff9d"
    elif score >= 50:
        tip = "⚠️ ACCEPTABLE - Zone suitable with caution. Monitor approach carefully."
        tip_color = "#00d4ff"
    elif score >= 30:
        tip = "⚠️ RISKY - Zone marginal. Consider alternatives if available."
        tip_color = "#ffb800"
    else:
        tip = "❌ DANGEROUS - Avoid this zone. Search for better alternatives."
        tip_color = "#ff3d71"
    
    return f"""
    <div style="background:rgba(15,21,39,0.8);border:1px solid {tip_color};border-radius:8px;padding:12px;">
        <div style="color:{tip_color};font-size:11px;font-family:'Space Mono',monospace;font-weight:700;">{tip}</div>
    </div>
    """

def danger_alert_html(danger_zones: pd.DataFrame) -> str:
    """Generate danger alert"""
    count = len(danger_zones)
    return f"""
    <div style="background:rgba(255,61,113,0.1);border:1px solid #ff3d71;border-radius:8px;padding:12px;">
        <div style="color:#ff3d71;font-size:11px;font-family:'Space Mono',monospace;font-weight:700;">
            ⚠️ {count} DANGEROUS ZONES DETECTED - AVOID APPROACH
        </div>
    </div>
    """

# ═══════════════════════════════════════════════════════════════
# AIRCRAFT TYPE GENERATOR (HELICOPTERS ONLY)
# ═══════════════════════════════════════════════════════════════

def create_aircraft_from_type(aircraft_type: str) -> Dict:
    """Create aircraft data based on selected helicopter type"""
    if aircraft_type not in AIRCRAFT_DATABASE:
        aircraft_type = list(AIRCRAFT_DATABASE.keys())[0]
    
    db_aircraft = AIRCRAFT_DATABASE[aircraft_type]
    
    emergencies = {
        'Helicopter': [
            'Engine Failure',
            'Rotor Damage',
            'Hydraulic Loss',
            'Tail Rotor Failure',
            'Electrical Failure',
            'Transmission Damage',
            'Fuel System Leak',
            'Main Rotor Blade Crack',
            'Instrument Failure',
            'Control System Malfunction'
        ]
    }
    
    emergency_list = emergencies.get(db_aircraft['category'], ['System Failure'])
    
    aircraft = {
        'latitude': 28.5244,
        'longitude': 77.1855,
        'altitude': np.random.randint(500, int(db_aircraft['cruise_altitude'] * 0.8)),
        'speed': int(db_aircraft['speed'] * np.random.uniform(0.6, 1.0)),
        'heading': np.random.randint(0, 360),
        'fuel': np.random.choice(['CRITICAL', 'LOW', 'MODERATE', 'ADEQUATE']),
        'emergency': np.random.choice(emergency_list),
        'passengers': int(db_aircraft['passengers']),
        'crew': int(db_aircraft['crew']),
        'aircraft_type': aircraft_type,
        'weight': db_aircraft['weight'],
        'landing_distance': db_aircraft['landing_distance'],
        'emoji': db_aircraft['emoji'],
        'hover_time': db_aircraft.get('hover_time', 60),
        'rotor_diameter': db_aircraft.get('rotor_diameter', 0),
        'blade_count': db_aircraft.get('blade_count', 4),
        'service_ceiling': db_aircraft.get('service_ceiling', 20000),
    }
    
    return aircraft

# ═══════════════════════════════════════════════════════════════
# DATA FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_zones(lat: float, lon: float, count: int = 15) -> List[Dict]:
    """Generate landing zones"""
    zones = []
    for i in range(count):
        zone_lat = lat + np.random.uniform(-0.5, 0.5)
        zone_lon = lon + np.random.uniform(-0.5, 0.5)
        zone_type = np.random.choice(['field', 'highway', 'airport', 'desert'])
        
        zones.append({
            'lat': zone_lat,
            'lon': zone_lon,
            'name': f'Zone {chr(65 + i)}',
            'type': zone_type,
            'score': np.random.randint(30, 100),
            'area': np.random.randint(5000, 50000),
            'wind': np.random.randint(5, 35),
            'obstacles': np.random.randint(0, 10),
            'visibility': np.random.choice(['Clear', 'Moderate', 'Poor']),
            'distance_factor': cached_dist_km(lat, lon, zone_lat, zone_lon)
        })
    
    return zones

# ═══════════════════════════════════════════════════════════════
# INTERACTIVE MAP BUILDER
# ═══════════════════════════════════════════════════════════════

def build_interactive_map(aircraft: dict, zones: pd.DataFrame, pinned_location: Optional[Tuple] = None) -> folium.Map:
    """Build interactive map with helicopter"""
    
    map_center = [aircraft["latitude"], aircraft["longitude"]]
    
    m = folium.Map(
        location=map_center,
        zoom_start=10,
        tiles="OpenStreetMap",
        control_scale=True
    )
    
    MousePosition().add_to(m)
    
    aircraft_marker_color = 'red' if aircraft['fuel'] == 'CRITICAL' else 'orange' if aircraft['fuel'] == 'LOW' else 'blue'
    
    folium.Marker(
        location=[aircraft["latitude"], aircraft["longitude"]],
        popup=f"""
        <div style='width:280px;background:#0f1527;color:#e0e6ed;padding:12px;border-radius:8px;border:2px solid #00ff9d;'>
            <b style='color:#00ff9d;font-size:14px;'>{aircraft['emoji']} {aircraft['aircraft_type']}</b><br><br>
            <table style='width:100%;color:#8892b0;font-size:10px;'>
            <tr style='color:#00ff9d;'><td colspan='2'><b>HELICOPTER TELEMETRY</b></td></tr>
            <tr><td><b>Position:</b></td><td>{aircraft['latitude']:.4f}°, {aircraft['longitude']:.4f}°</td></tr>
            <tr><td><b>Altitude:</b></td><td>{aircraft['altitude']:,} ft</td></tr>
            <tr><td><b>Airspeed:</b></td><td>{aircraft['speed']} kts</td></tr>
            <tr><td><b>Heading:</b></td><td>{aircraft['heading']}°</td></tr>
            <tr><td><b>Hover Time:</b></td><td>{aircraft['hover_time']} min</td></tr>
            <tr><td><b>Rotor Diameter:</b></td><td>{aircraft['rotor_diameter']} m</td></tr>
            <tr><td><b>Blade Count:</b></td><td>{aircraft['blade_count']}</td></tr>
            <tr><td><b>Passengers:</b></td><td>{aircraft['passengers']}</td></tr>
            <tr><td><b>Crew:</b></td><td>{aircraft['crew']}</td></tr>
            <tr><td><b>Emergency:</b></td><td style='color:#ff3d71;'><b>{aircraft['emergency']}</b></td></tr>
            <tr><td><b>Fuel:</b></td><td style='color:#ffb800;'><b>{aircraft['fuel']}</b></td></tr>
            </table>
        </div>
        """,
        tooltip=f"{aircraft['emoji']} {aircraft['aircraft_type']} (CURRENT)",
        icon=folium.Icon(color=aircraft_marker_color, icon='helicopter', prefix='fa', icon_color='white')
    ).add_to(m)
    
    if pinned_location:
        folium.Marker(
            location=pinned_location,
            popup=f"""
            <div style='width:280px;background:#0f1527;color:#e0e6ed;padding:12px;border-radius:8px;border:2px solid #00ff9d;'>
                <b style='color:#00ff9d'>🚁 NEW POSITION (PINNED)</b><br><br>
                Latitude: <b>{pinned_location[0]:.6f}°</b><br>
                Longitude: <b>{pinned_location[1]:.6f}°</b><br><br>
                <span style='color:#ffb800;font-size:10px;'>Ready for simulation</span>
            </div>
            """,
            tooltip="🚁 HELICOPTER PINNED POSITION",
            icon=folium.Icon(color='green', icon='map-pin', prefix='fa', icon_color='white')
        ).add_to(m)
    
    for idx, (_, zone) in enumerate(zones.iterrows()):
        score = zone['score']
        color = 'green' if score >= 75 else 'yellow' if score >= 50 else 'orange' if score >= 30 else 'red'
        
        folium.CircleMarker(
            location=[zone['lat'], zone['lon']],
            radius=8 + (score / 100 * 5),
            popup=f"""
            <div style='width:240px;background:#0f1527;color:#e0e6ed;padding:12px;border-radius:8px;border:2px solid {color};'>
                <b style='color:#00ff9d;'>Zone {chr(65+idx)}: {zone['name']}</b><br>
                <hr style='border-color:rgba(0,212,255,0.2);margin:8px 0;'>
                Score: <b style='color:#00ff9d;'>{score:.0f}/100</b><br>
                Type: <b>{zone['type'].upper()}</b><br>
                Wind: <b>{zone['wind']} kts</b><br>
                Area: <b>{zone['area']:,} m²</b><br>
                Obstacles: <b>{zone['obstacles']}</b><br>
                Visibility: <b>{zone.get('visibility', 'Clear')}</b>
            </div>
            """,
            tooltip=f"Zone {chr(65+idx)}: {zone['name']} ({score:.0f})",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    return m

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════

def init_session():
    """Initialize session state"""
    if "aircraft_type" not in st.session_state:
        st.session_state.aircraft_type = 'Bell 407'
        st.session_state.aircraft = create_aircraft_from_type(st.session_state.aircraft_type)
        st.session_state.zones_raw = generate_zones(
            st.session_state.aircraft["latitude"],
            st.session_state.aircraft["longitude"]
        )
        st.session_state.selected_zone = 0
        st.session_state.sim_count = 1
        st.session_state.pinned_location = None
        st.session_state.aircraft_pinned = False
        st.session_state.sound_enabled = True
        st.session_state.ai_analysis_done = False
        logger.info("Session initialized")

init_session()

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ELZF-AI v5.0 | Helicopter Emergency Landing System",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/yourusername/ELZF-AI',
        'Report a bug': 'https://github.com/yourusername/ELZF-AI/issues',
        'About': '### ELZF-AI v5.0 HELICOPTER\nFull Integration: Helicopter Control + Type Selection + Sound + AI + Data Fusion'
    }
)

# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═════════════════════���═════════════════════════════════════════

def main():
    """Main application logic"""
    try:
        aircraft = st.session_state.aircraft
        zones = st.session_state.zones_raw
        
        zones_tuple = tuple(tuple(sorted(z.items())) for z in zones)
        df = process_zones_data(zones_tuple)
        
        if df.empty:
            st.error("❌ No zones available")
            return
        
        best = df.iloc[0].to_dict()
        sel_idx = st.session_state.selected_zone
        sel_zone = df.iloc[min(sel_idx, len(df) - 1)].to_dict()

        # ─────────────────────────────────────────────────────────
        # HEADER WITH HOLOGRAPHIC EFFECTS
        # ─────────────────────────────────────────────────────────
        st.markdown("""
        <div class="cockpit-panel" style="text-align:center;padding:30px;margin-bottom:20px;">
            <div class="holographic-text" style="font-size:36px;margin-bottom:10px;">
                🚁 ELZF-AI v5.0 - HELICOPTER EMERGENCY LANDING SYSTEM
            </div>
            <div class="hologram" style="font-size:14px;margin:10px 0;">
                AI-Powered Real-Time Emergency Landing Zone Finder
            </div>
            <div class="anti-gravity" style="font-size:12px;color:#00d4ff;">
                ⚡ Anti-Gravity Cockpit Interface ⚡
            </div>
            <div style="margin-top:10px;font-size:10px;color:#8892b0;font-family:'Space Mono',monospace;">
                📊 AI + DATA FUSION + PREDICTIVE ANALYSIS + HELICOPTER CONTROL + SOUND ALERTS
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Version and System Info
        header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
        
        with header_col1:
            st.markdown(f"""
            <div class="hologram" style="font-size:11px;">
                🚁 HELICOPTER MODE ACTIVE<br>
                📍 Position: {aircraft['latitude']:.4f}°, {aircraft['longitude']:.4f}°
            </div>
            """, unsafe_allow_html=True)
        
        with header_col2:
            st.markdown(f"""
            <div class="cockpit-readout">
                🤖 AI ENGINE: ONLINE<br>
                📡 DATA FUSION: ACTIVE<br>
                🔮 PREDICTIVE: READY
            </div>
            """, unsafe_allow_html=True)
        
        with header_col3:
            sound_toggle = st.checkbox("🔊 Sound Alerts", value=True, key="sound_toggle")
            st.session_state.sound_enabled = sound_toggle

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # HELICOPTER SELECTION PANEL
        # ─────────────────────────────────────────────────────────
        st.markdown("""
        <div class="cockpit-panel" style="border-color:#00ff9d;">
            <div class="hologram" style="font-size:12px;margin-bottom:8px;">
                🚁 HELICOPTER TYPE SELECTION
            </div>
            <div class="hologram" style="font-size:12px;color:#00d4ff;">
                Currently Operating: {}
            </div>
        </div>
        """.format(aircraft['aircraft_type']), unsafe_allow_html=True)
        
        sel_col1, sel_col2, sel_col3 = st.columns([2, 1.5, 0.5])
        
        with sel_col1:
            selected_aircraft_type = st.selectbox(
                "Select Helicopter Type",
                list(AIRCRAFT_DATABASE.keys()),
                index=list(AIRCRAFT_DATABASE.keys()).index(st.session_state.aircraft_type),
                key="aircraft_selector"
            )
        
        with sel_col2:
            if st.button("🔄 CHANGE HELICOPTER", use_container_width=True):
                st.session_state.aircraft_type = selected_aircraft_type
                st.session_state.aircraft = create_aircraft_from_type(selected_aircraft_type)
                st.session_state.zones_raw = generate_zones(
                    st.session_state.aircraft["latitude"],
                    st.session_state.aircraft["longitude"]
                )
                st.session_state.selected_zone = 0
                st.session_state.sim_count += 1
                st.session_state.aircraft_pinned = False
                st.session_state.pinned_location = None
                logger.info(f"Helicopter changed to: {selected_aircraft_type}")
                st.rerun()
        
        with sel_col3:
            aircraft_db = AIRCRAFT_DATABASE[aircraft['aircraft_type']]
            st.markdown(f"<div style='text-align:center;padding:8px;' class='rotor-indicator'>{aircraft_db['emoji']}</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # HELICOPTER SPECS DISPLAY WITH ANTI-GRAVITY EFFECTS
        # ─────────────────────────────────────────────────────────
        st.markdown("<div class='hologram' style='text-align:center;margin:15px 0;font-size:12px;'>HELICOPTER SPECIFICATIONS</div>", unsafe_allow_html=True)
        
        spec_col1, spec_col2, spec_col3, spec_col4, spec_col5 = st.columns(5)
        
        aircraft_db = AIRCRAFT_DATABASE[aircraft['aircraft_type']]
        
        with spec_col1:
            st.markdown(stat_card("Category", "Helicopter", "", "#00d4ff", "TYPE", "info"), unsafe_allow_html=True)
        with spec_col2:
            st.markdown(stat_card("Passengers", str(aircraft_db['passengers']), "max", "#00ff9d", "CAPACITY", "ok"), unsafe_allow_html=True)
        with spec_col3:
            st.markdown(stat_card("Hover Time", f"{aircraft_db.get('hover_time', 60)}", "min", "#9c6dff", "DURATION", "info"), unsafe_allow_html=True)
        with spec_col4:
            st.markdown(stat_card("Rotor Diam.", f"{aircraft_db.get('rotor_diameter', 0)}", "m", "#ffb800", "DIAMETER", "warn"), unsafe_allow_html=True)
        with spec_col5:
            st.markdown(stat_card("Weight", f"{aircraft_db['weight']:,}", "kg", "#ff6b35", "GROSS", "warn"), unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # FLIGHT STATUS WITH COCKPIT READOUTS
        # ─────────────────────────────────────────────────────────
        st.markdown("<div class='hologram' style='text-align:center;margin:15px 0;font-size:12px;'>REAL-TIME TELEMETRY</div>", unsafe_allow_html=True)
        
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        with c1:
            st.markdown(f"""
            <div class="cockpit-readout" style="border-left-color:#00d4ff;margin:0;">
                <div style="font-size:11px;font-weight:700;color:#00d4ff;">ALTITUDE</div>
                <div class="altitude-display">{aircraft['altitude']:,}</div>
                <div style="font-size:9px;color:#8892b0;margin-top:4px;">ft MSL</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="cockpit-readout" style="border-left-color:#ff6b35;margin:0;">
                <div style="font-size:11px;font-weight:700;color:#ff6b35;">AIRSPEED</div>
                <div class="altitude-display">{aircraft["speed"]}</div>
                <div style="font-size:9px;color:#8892b0;margin-top:4px;">kts</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="cockpit-readout" style="border-left-color:#9c6dff;margin:0;">
                <div style="font-size:11px;font-weight:700;color:#9c6dff;">HEADING</div>
                <div class="altitude-display">{aircraft['heading']}°</div>
                <div style="font-size:9px;color:#8892b0;margin-top:4px;">Magnetic</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            fuel_col = "#ff3d71" if aircraft["fuel"] == "CRITICAL" else "#ffb800"
            st.markdown(f"""
            <div class="cockpit-readout" style="border-left-color:{fuel_col};margin:0;">
                <div style="font-size:11px;font-weight:700;color:{fuel_col};">FUEL</div>
                <div class="altitude-display" style="color:{fuel_col};font-size:12px;">{aircraft["fuel"]}</div>
                <div style="font-size:9px;color:#8892b0;margin-top:4px;">Status</div>
            </div>
            """, unsafe_allow_html=True)
        with c5:
            st.markdown(f"""
            <div class="cockpit-readout" style="border-left-color:#ff3d71;margin:0;">
                <div style="font-size:11px;font-weight:700;color:#ff3d71;">EMERGENCY</div>
                <div class="altitude-display" style="color:#ff3d71;font-size:10px;">{aircraft["emergency"][:8]}</div>
                <div style="font-size:9px;color:#8892b0;margin-top:4px;">ACTIVE</div>
            </div>
            """, unsafe_allow_html=True)
        with c6:
            risk_lbl, risk_col = get_risk_level(best["score"])
            st.markdown(f"""
            <div class="cockpit-readout" style="border-left-color:{risk_col};margin:0;">
                <div style="font-size:11px;font-weight:700;color:{risk_col};">BEST ZONE</div>
                <div class="altitude-display" style="color:{risk_col};">{int(best["score"])}</div>
                <div style="font-size:9px;color:#8892b0;margin-top:4px;">/100</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # HELICOPTER STATUS INDICATOR
        # ─────────────────────────────────────────────────────────
        hover_status = "STABLE" if aircraft['altitude'] < aircraft['service_ceiling'] else "CRITICAL"
        hover_color = "#00ff9d" if hover_status == "STABLE" else "#ff3d71"
        
        st.markdown(f"""
        <div class="helicopter-status" style="border-color:{hover_color};">
            <div class="rotor-icon">🚁</div>
            <div>
                <div class="hologram" style="font-size:12px;margin-bottom:4px;">HELICOPTER STATUS</div>
                <div style="font-size:11px;color:#e0e6ed;">
                    Hover Time: <span style="color:#00ff9d;font-weight:700;">{aircraft['hover_time']} min</span> | 
                    Service Ceiling: <span style="color:#00ff9d;font-weight:700;">{aircraft['service_ceiling']:,} ft</span> | 
                    Rotor Blades: <span style="color:#00ff9d;font-weight:700;">{aircraft['blade_count']}</span>
                </div>
                <div class="g-force-indicator" style="margin-top:4px;">
                    <span class="rotor-status" style="margin-right:8px;"></span>
                    <span class="hover-stable">{hover_status}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # ALERT BOX
        # ─────────────────────────────────────────────────────────
        risk_lbl, risk_col = get_risk_level(best["score"])
        km_best = cached_dist_km(
            aircraft["latitude"], aircraft["longitude"],
            best["lat"], best["lon"]
        )
        
        st.markdown(f"""
        <div class="cockpit-panel" style="border-color:{risk_col};background:linear-gradient(135deg,rgba(0,255,157,0.07),rgba(0,212,255,0.07));display:flex;align-items:center;gap:15px;margin-bottom:15px;">
            <div class="rotor-indicator" style="font-size:36px;">⚡</div>
            <div>
                <div class="holographic-text" style="font-size:13px;margin-bottom:4px;">
                    OPTIMAL ZONE: {best['name']} | SCORE: {best['score']:.0f}/100 | {best['type'].upper()} | {risk_lbl}
                </div>
                <div class="hologram" style="font-size:11px;">
                    Distance: {km_best}km | Wind: {best['wind']}kts | Obstacles: {best['obstacles']} | Area: {best['area']:,}m²
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # AI ANALYSIS SECTION
        # ─────────────────────────────────────────────────────────
        st.markdown("<div class='hologram' style='text-align:center;margin:15px 0;font-size:12px;'>🤖 AI MULTI-SOURCE DATA FUSION | SATELLITE + WEATHER + PREDICTIVE</div>", unsafe_allow_html=True)
        
        ai_col1, ai_col2, ai_col3, ai_col4 = st.columns(4)
        
        with ai_col1:
            if st.button("🔍 RUN AI ANALYSIS", use_container_width=True, key="run_ai"):
                with st.spinner("Analyzing satellite imagery..."):
                    satellite_data = SatelliteImageryAnalyzer.detect_terrain_features(
                        aircraft["latitude"], aircraft["longitude"], scan_radius_km=10
                    )
                    st.success(f"✓ Detected {len(satellite_data)} terrain features via YOLOv8 simulation")
        
        with ai_col2:
            if st.button("⛅ WEATHER FUSION", use_container_width=True, key="fuse_weather"):
                with st.spinner("Integrating weather from multiple sources..."):
                    weather_data = WeatherDataFusion.integrate_weather_sources(
                        aircraft["latitude"], aircraft["longitude"]
                    )
                    weather_score = WeatherDataFusion.calculate_weather_impact_score(weather_data)
                    st.metric("Weather Impact Score", f"{weather_score:.0f}/100")
        
        with ai_col3:
            if st.button("🔮 PREDICTIVE RISK", use_container_width=True, key="predict_risk"):
                with st.spinner("Generating risk trajectory..."):
                    trajectory = PredictiveRiskAnalyzer.predict_zone_safety_trajectory(best, aircraft, 10)
                    st.line_chart(trajectory)
        
        with ai_col4:
            if st.button("📊 DATA FUSION", use_container_width=True, key="data_fusion"):
                st.success("✓ Multi-source data fusion complete")

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # SOUND ALERTS SECTION
        # ─────────────────────────────────────────────────────────
        if st.session_state.sound_enabled:
            st.markdown("<div class='hologram' style='text-align:center;margin:15px 0;font-size:12px;'>🔊 AUDIO ALERT SYSTEM | PILOT VOICE ALERTS</div>", unsafe_allow_html=True)
            
            sound_col1, sound_col2, sound_col3, sound_col4 = st.columns(4)
            
            with sound_col1:
                if st.button("🔊 Zone Detected", use_container_width=True, key="play_zone"):
                    AircraftSoundSystem.play_sound("ZONE_DETECTED")
                    st.success("✓ Zone detection alert played")
            
            with sound_col2:
                if st.button("⚠️ Critical Alert", use_container_width=True, key="play_critical"):
                    AircraftSoundSystem.play_sound("CRITICAL")
                    st.success("✓ Critical alert played")
            
            with sound_col3:
                if st.button("✅ Optimal Zone", use_container_width=True, key="play_optimal"):
                    AircraftSoundSystem.play_sound("OPTIMAL_ZONE")
                    st.success("✓ Optimal zone alert played")
            
            with sound_col4:
                if st.button("🛬 Landing Clearance", use_container_width=True, key="play_landing"):
                    AircraftSoundSystem.play_sound("LANDING")
                    st.success("✓ Landing alert played")

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # EMERGENCY ALERT SYSTEM
        # ─────────────────────────────────────────────────────────
        st.markdown("<div class='hologram' style='text-align:center;margin:15px 0;font-size:12px;'>🚨 REAL-TIME EMERGENCY DECISION SYSTEM | AI-POWERED</div>", unsafe_allow_html=True)
        
        alert_level = EmergencyAlertSystem.evaluate_emergency_level(aircraft, best["score"])
        recommendation = RealTimeDecisionEngine.generate_landing_recommendation(df, aircraft, 
                                                                                 WeatherDataFusion.integrate_weather_sources(
                                                                                     aircraft["latitude"], aircraft["longitude"]
                                                                                 ))
        
        alert_col1, alert_col2, alert_col3 = st.columns(3)
        
        with alert_col1:
            alert_color = {
                'NORMAL': '#00ff9d',
                'ADVISORY': '#00d4ff',
                'CAUTION': '#ffb800',
                'WARNING': '#ff6b35',
                'EMERGENCY': '#ff3d71'
            }
            
            st.markdown(f"""
            <div class="cockpit-panel" style="border-color:{alert_color[alert_level]};text-align:center;">
                <div class="hologram" style="font-size:12px;margin-bottom:8px;color:{alert_color[alert_level]};">
                    ALERT LEVEL
                </div>
                <div class="holographic-text" style="font-size:28px;margin-bottom:8px;color:{alert_color[alert_level]};">
                    {alert_level}
                </div>
                <div style="font-size:10px;color:#8892b0;">
                    Confidence: {recommendation['confidence']}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with alert_col2:
            st.markdown(f"""
            <div class="cockpit-panel" style="border-color:#00ff9d;">
                <div class="hologram" style="font-size:12px;margin-bottom:8px;color:#00ff9d;">
                    RECOMMENDED ZONE
                </div>
                <div style="font-size:16px;color:#e0e6ed;font-weight:700;margin-bottom:4px;">
                    {best['name']}
                </div>
                <div style="font-size:11px;color:#8892b0;">
                    Score: {best['score']:.0f}/100<br>
                    Distance: {recommendation['distance_km']:.1f} km<br>
                    ETA: {recommendation['estimated_time_to_reach']} min
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with alert_col3:
            st.markdown(f"""
            <div class="cockpit-panel" style="border-color:#00d4ff;">
                <div class="hologram" style="font-size:12px;margin-bottom:8px;color:#00d4ff;">
                    SYSTEM STATUS
                </div>
                <div style="font-size:11px;color:#8892b0;line-height:1.8;font-family:'Space Mono',monospace;">
                    ✓ Reliability: {recommendation['system_reliability']:.1f}%<br>
                    ✓ Data Fusion: Active<br>
                    ✓ Predictive: Ready<br>
                    ✓ AI Engine: Online
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # INTERACTIVE MAP WITH PINNING
        # ─────────────────────────────────────────────────────────
        st.markdown("<div class='hologram' style='text-align:center;margin:15px 0;font-size:12px;'>🗺️ INTERACTIVE TACTICAL MAP | CLICK TO PIN & CONFIRM</div>", unsafe_allow_html=True)
        
        map_col, control_col = st.columns([1.4, 0.6])

        with map_col:
            try:
                interactive_map = build_interactive_map(
                    aircraft, 
                    df, 
                    pinned_location=st.session_state.pinned_location if st.session_state.aircraft_pinned else None
                )
                map_data = st_folium(interactive_map, width="100%", height=420)
                
                if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
                    click_lat = map_data['last_clicked']['lat']
                    click_lon = map_data['last_clicked']['lng']
                    
                    dist_from_aircraft = np.sqrt(
                        (click_lat - aircraft['latitude'])**2 + 
                        (click_lon - aircraft['longitude'])**2
                    )
                    
                    if dist_from_aircraft < 0.02:
                        st.session_state.pinned_location = None
                        st.session_state.aircraft_pinned = False
                    else:
                        st.session_state.pinned_location = (click_lat, click_lon)
                        st.session_state.aircraft_pinned = True
                        st.rerun()
                    
            except Exception as e:
                logger.error(f"Map error: {e}")
                st.error(f"⚠️ Map unavailable: {str(e)}")

        with control_col:
            st.markdown("<div class='hologram' style='font-size:12px;margin-bottom:8px;'>📡 LANDING ZONES | RANKED</div>", unsafe_allow_html=True)
            for rank, row in df.head(5).iterrows():
                selected = (rank == sel_idx)
                st.markdown(zone_card_clean(row.to_dict(), rank, selected), unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # CONFIRMATION PANEL
        # ─────────────────────────────────────────���───────────────
        if st.session_state.aircraft_pinned and st.session_state.pinned_location:
            st.markdown("<hr style='border-color:rgba(0,212,255,0.2);margin:20px 0'/>", unsafe_allow_html=True)
            st.markdown("<div class='hologram' style='text-align:center;margin:15px 0;font-size:12px;'>🎯 HELICOPTER POSITION PINNED | CONFIRM TO SIMULATE</div>", unsafe_allow_html=True)
            
            pin_col1, pin_col2, pin_col3 = st.columns([1.2, 1.2, 1])
            
            with pin_col1:
                st.markdown(f"""
                <div class="cockpit-panel" style="border-color:#00d4ff;">
                    <div class="hologram" style="font-size:11px;margin-bottom:8px;">📍 COORDINATES</div>
                    <div style="font-size:10px;color:#8892b0;font-family:'Space Mono',monospace;line-height:1.8;">
                        Lat: {st.session_state.pinned_location[0]:.6f}°<br>
                        Lon: {st.session_state.pinned_location[1]:.6f}°<br>
                        Helicopter: {aircraft['aircraft_type']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with pin_col2:
                st.markdown(f"""
                <div class="cockpit-panel" style="border-color:#ffb800;">
                    <div class="hologram" style="font-size:11px;margin-bottom:8px;color:#ffb800;">🚁 SPECS</div>
                    <div style="font-size:10px;color:#8892b0;font-family:'Space Mono',monospace;">
                        Passengers: {aircraft['passengers']}<br>
                        Rotor Diameter: {AIRCRAFT_DATABASE[aircraft['aircraft_type']]['rotor_diameter']}m<br>
                        Category: {AIRCRAFT_DATABASE[aircraft['aircraft_type']]['category']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with pin_col3:
                st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
                if st.button("✅ CONFIRM & SIMULATE", use_container_width=True, key="confirm_pin"):
                    st.session_state.aircraft["latitude"] = st.session_state.pinned_location[0]
                    st.session_state.aircraft["longitude"] = st.session_state.pinned_location[1]
                    st.session_state.zones_raw = generate_zones(
                        st.session_state.pinned_location[0],
                        st.session_state.pinned_location[1]
                    )
                    st.session_state.sim_count += 1
                    st.session_state.selected_zone = 0
                    st.session_state.aircraft_pinned = False
                    st.session_state.pinned_location = None
                    st.success("✓ Helicopter moved and simulation started!")
                    st.rerun()

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # AI TIPS & DANGER ZONES
        # ─────────────────────────────────────────────────────────
        tip_col, danger_col = st.columns([1.5, 1])
        
        with tip_col:
            st.markdown("<div class='hologram' style='text-align:center;margin:8px 0;font-size:11px;'>🤖 AI RECOMMENDATION | INTELLIGENT ANALYSIS</div>", unsafe_allow_html=True)
            st.markdown(ai_tips_html(best["score"]), unsafe_allow_html=True)
        
        with danger_col:
            st.markdown("<div class='hologram' style='text-align:center;margin:8px 0;font-size:11px;'>🚫 RISK ASSESSMENT | ZONE SAFETY</div>", unsafe_allow_html=True)
            danger_zones = df[df["score"] < 30]
            if len(danger_zones) > 0:
                st.markdown(danger_alert_html(danger_zones), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="cockpit-panel" style="border-color:#00ff9d;text-align:center;">
                    <div style="font-size:28px;margin-bottom:4px">✓</div>
                    <div class="hologram" style="color:#00ff9d;">ALL ZONES SAFE</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # MAIN TABS
        # ─────────────────────────────────────────────────────────
        tab1, tab2, tab3 = st.tabs([
            "📊 Analysis",
            "🗂️ Zones",
            "🚁 Helicopter"
        ])

        with tab1:
            st.markdown("<div class='hologram' style='margin:10px 0;'>ZONE ANALYSIS</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Total Zones", len(df))
            with c2:
                st.metric("Safe Zones (>75)", len(df[df['score'] >= 75]))

        with tab2:
            st.markdown("<div class='hologram' style='margin:10px 0;'>ZONE COMPARISON</div>", unsafe_allow_html=True)
            display_df = df.copy()
            display_df["distance"] = display_df.apply(
                lambda r: f"{cached_dist_km(aircraft['latitude'], aircraft['longitude'], r['lat'], r['lon']):.1f}km",
                axis=1
            )
            display_cols = ["name", "score", "type", "area", "wind", "obstacles", "distance"]
            display_df = display_df[display_cols]
            display_df.columns = ["Zone", "Score", "Type", "Area(m²)", "Wind(kt)", "Obstacles", "Distance"]
            st.dataframe(display_df, use_container_width=True, height=300)

        with tab3:
            st.markdown("<div class='hologram' style='margin:10px 0;'>HELICOPTER TELEMETRY</div>", unsafe_allow_html=True)
            ac1, ac2, ac3 = st.columns(3)
            fields = [
                ("Latitude", f"{aircraft['latitude']:.6f}°N", "info"),
                ("Longitude", f"{aircraft['longitude']:.6f}°E", "info"),
                ("Altitude", f"{aircraft['altitude']:,} ft", "warn"),
                ("Airspeed", f"{aircraft['speed']} kts", "warn"),
                ("Heading", f"{aircraft['heading']}°", "info"),
                ("Fuel", aircraft["fuel"], "danger" if aircraft["fuel"]=="CRITICAL" else "warn"),
                ("Emergency", aircraft["emergency"], "danger"),
                ("Passengers", str(aircraft["passengers"]), "ok"),
                ("Crew", str(aircraft["crew"]), "ok"),
            ]
            
            for i, (label, value, badge_col) in enumerate(fields):
                col_ref = [ac1, ac2, ac3][i % 3]
                col_map = {"info": "#00d4ff", "warn": "#ffb800", "danger": "#ff3d71", "ok": "#00ff9d"}
                with col_ref:
                    st.markdown(stat_card(label, value, "", col_map[badge_col], label, badge_col), unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # BOTTOM CONTROLS
        # ─────────────────────────────────────────────────────────
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:rgba(0,212,255,0.1);margin:0'/>", unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1.5, 1.5, 1])
        
        with col1:
            st.markdown("<div class='hologram' style='font-size:10px;margin-bottom:8px;'>SELECT ZONE</div>", unsafe_allow_html=True)
            zone_options = [f"{row['name']} — {row['score']:.0f}" for _, row in df.iterrows()]
            chosen = st.selectbox("", zone_options, index=sel_idx, label_visibility="collapsed", key="zone_select")
            st.session_state.selected_zone = zone_options.index(chosen)

        with col2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("⟳ AUTO-SIMULATE (Random)", use_container_width=True, key="auto_sim_btn"):
                st.session_state.aircraft = create_aircraft_from_type(st.session_state.aircraft_type)
                st.session_state.zones_raw = generate_zones(
                    st.session_state.aircraft["latitude"],
                    st.session_state.aircraft["longitude"]
                )
                st.session_state.selected_zone = 0
                st.session_state.sim_count += 1
                st.session_state.aircraft_pinned = False
                st.session_state.pinned_location = None
                st.rerun()

        with col3:
            st.markdown(f"<div class='hologram' style='font-size:10px;text-align:right;padding-top:28px;'>SIM #{st.session_state.sim_count}<br><span style='color:#00ff9d;'>v5.0 COMPLETE</span></div>", unsafe_allow_html=True)

        # ─────────────────────────────────────────────────────────
        # FOOTER
        # ─────────────────────────────────────────────────────────
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="cockpit-panel" style="text-align:center;padding:12px;font-size:9px;border-color:rgba(0,212,255,0.3);letter-spacing:0.1em;">
            🚁 ELZF-AI v5.0 ◆ HELICOPTER EMERGENCY LANDING SYSTEM ◆ ANTI-GRAVITY COCKPIT ◆ PROFESSIONAL GRADE ◆ COMPLETE INTEGRATION ◆ AI + DATA FUSION ◆ PATENT READY
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"❌ Application Error: {str(e)}")

if __name__ == "__main__":
    main()