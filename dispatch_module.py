# dispatch_module.py
"""
Emergency dispatch message generator. No external calls by default.
Use st.secrets and secure senders (Twilio/SMTP) if you enable transmission.
"""
from typing import Dict, List

def generate_dispatch_message(mission: Dict, recipients: List[str]) -> Dict:
    subj = f"Emergency Dispatch: landing at {mission.get('dest')}"
    body = (
        f"EMERGENCY - Mission\nStart: {mission.get('start')}\n"
        f"Dest: {mission.get('dest')}\nETA: {int(mission.get('travel_time',0))}s\n"
        f"Recommended zone: {mission.get('zone_name','N/A')}\n\nTelemetry snapshot:\n"
        + "\n".join([f"t={t['t']} lat={t['lat']} lon={t['lon']} alt={t['alt']}" for t in mission.get('telemetry',[])[:6]])
    )
    return {"subject": subj, "body": body, "recipients": recipients}