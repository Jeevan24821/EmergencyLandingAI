# record_demo.py
"""
Automated demo recorder for the EmergencyLandingAI simulator.

Usage:
1) Start your Streamlit app (in another terminal):
   streamlit run app_advanced_update.py

2) Run this recorder (after installing dependencies described below):
   python record_demo.py

What it does:
- Opens http://localhost:8501
- Clicks Prepare Mission, then Start Mission (Server-trigger)
- Attempts to read ETA from the HUD and records the page for ETA + buffer seconds
- Saves a recorded .webm under ./videos/ and prints path for conversion
"""

import re
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

APP_URL = "http://localhost:8501"
OUTPUT_DIR = Path("videos")
OUTPUT_DIR.mkdir(exist_ok=True)

def parse_eta_seconds(text: str) -> int:
    # Looks for ETA: HH:MM:SS or H:MM:SS
    m = re.search(r"ETA:\s*([0-9]{1,2}):([0-9]{2}):([0-9]{2})", text)
    if not m:
        return 30  # fallback
    h, mm, ss = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return h * 3600 + mm * 60 + ss

def main():
    print("Recorder starting. Ensure streamlit server is already running at", APP_URL)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set headless=False to watch
        context = browser.new_context(record_video_dir=str(OUTPUT_DIR), viewport={"width":1280, "height":720})
        page = context.new_page()
        print("Opening app...")
        try:
            page.goto(APP_URL, timeout=60000)
        except PWTimeoutError:
            print("Timeout loading app. Is your Streamlit server running? Exiting.")
            context.close()
            browser.close()
            return

        # Wait a bit for the page to settle
        page.wait_for_timeout(2000)

        # Click Prepare Mission (if present)
        try:
            if page.locator("text='Prepare Mission'").count() > 0:
                page.click("text='Prepare Mission'")
                print("Clicked 'Prepare Mission'")
                page.wait_for_timeout(1000)
        except Exception as e:
            print("Could not click Prepare Mission:", e)

        # Click Start Mission (Server-trigger) to autostart simulator via server re-render
        try:
            if page.locator("text='Start Mission (Server-trigger)'").count() > 0:
                page.click("text='Start Mission (Server-trigger)'")
                print("Clicked 'Start Mission (Server-trigger)'")
            else:
                # fallback: click the in-page HUD Start Mission (client-side). Buttons inside component are plain text buttons.
                if page.locator("text='Start Mission'").count() > 0:
                    page.click("text='Start Mission'")
                    print("Clicked HUD 'Start Mission' (client-side)")
        except Exception as e:
            print("Could not click Start Mission button:", e)

        # Allow the simulator to render and update the telemetry
        page.wait_for_timeout(1200)

        # Try to read ETA from the telemetry HUD
        eta_seconds = 30
        try:
            telemetry_text = page.locator("#telemetry").inner_text(timeout=5000)
            print("Telemetry HUD text:", telemetry_text)
            eta_seconds = parse_eta_seconds(telemetry_text)
            print(f"Parsed ETA seconds: {eta_seconds}")
        except Exception as e:
            print("Could not read ETA HUD, defaulting to 30s. Error:", e)
            eta_seconds = 30

        # Add buffer time for replay/landing
        record_for = max(15, int(eta_seconds) + 6)
        print(f"Recording for {record_for} seconds...")

        # Wait for the duration while the context records the video
        page.wait_for_timeout(record_for * 1000)

        # Close context so Playwright writes the video file
        context.close()
        browser.close()

        # Find the latest created webm file in OUTPUT_DIR
        webms = sorted(OUTPUT_DIR.glob("*.webm"), key=lambda p: p.stat().st_mtime, reverse=True)
        if webms:
            print("Recorded video saved to:", webms[0].resolve())
            print("Convert to mp4 (optional):")
            print(f"ffmpeg -i \"{webms[0]}\" -c:v libx264 -crf 18 -preset veryfast \"{webms[0].with_suffix('.mp4')}\"")
        else:
            print("No video file found in", OUTPUT_DIR)

if __name__ == "__main__":
    main()