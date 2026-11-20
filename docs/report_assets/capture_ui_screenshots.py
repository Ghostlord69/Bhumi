"""Seed demo cases through the live API and capture real Bhumi UI screenshots for Chapter 5.

Requires the AI service (8000), backend (8090) and Vite (5173) running.
Run: /tmp/shotvenv/bin/python docs/report_assets/capture_ui_screenshots.py
"""
import json
import mimetypes
import urllib.request
import uuid
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "report_assets" / "figures"
SHEETS = ROOT / "samples" / "handwritten" / "manual_tests"
API = "http://127.0.0.1:8090"
UI = "http://localhost:5173"

USER = ("user@bhumi.test", "User@123")
OFFICER = ("auth.ballabgarh@bhumi.gov.in", "Auth@123")
ADMIN = ("HR12345RH@bhumi.gov.in", "AdminHR123@")


def post_json(path, body, token=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    return json.loads(urllib.request.urlopen(req).read())


def post_multipart(path, token, payload, papers, photos):
    boundary = uuid.uuid4().hex
    parts = [(b'Content-Disposition: form-data; name="payload"\r\nContent-Type: application/json\r\n\r\n'
              + json.dumps(payload).encode())]
    for field, files in (("papers", papers), ("photos", photos)):
        for f in files:
            mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            parts.append(f'Content-Disposition: form-data; name="{field}"; filename="{f.name}"\r\n'
                         f'Content-Type: {mime}\r\n\r\n'.encode() + f.read_bytes())
    body = b"".join(b"--" + boundary.encode() + b"\r\n" + p + b"\r\n" for p in parts)
    body += b"--" + boundary.encode() + b"--\r\n"
    req = urllib.request.Request(API + path, data=body, method="POST", headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Authorization": f"Bearer {token}"})
    return json.loads(urllib.request.urlopen(req).read())


def seed():
    token = post_json("/api/auth/login", {"email": USER[0], "password": USER[1]})["token"]
    photos = [SHEETS / "1.jpg", SHEETS / "2.jpg", SHEETS / "3.jpg"]
    base = {"type": "LAND", "state": "Haryana", "district": "Faridabad", "city": "Ballabgarh",
            "latitude": 28.3426, "longitude": 77.3254}
    cases = [
        dict(base, purpose="SALE", title="Agricultural plot, Palla village", address="Palla, Ballabgarh",
             askingPrice=4200000, measurements="1,800 sq. yd.", khasraNumber="88/1"),
        dict(base, purpose="SALE", title="Farm land near Sihi road", address="Sihi, Ballabgarh",
             askingPrice=2750000, measurements="1.1 acres", khasraNumber="555/9"),
        dict(base, purpose="REGISTRY", title="Ancestral land registration", address="Sihi, Ballabgarh",
             askingPrice=0, measurements="1.2 acres", khasraNumber="999/1"),
    ]
    papers = [SHEETS / "2.jpg", SHEETS / "3.jpg", SHEETS / "1.jpg"]
    for case, paper in zip(cases, papers):
        view = post_multipart("/api/properties", token, case, [paper], photos)
        print(case["khasraNumber"], "->", view.get("status"))


def login(page, creds):
    page.goto(f"{UI}/login")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    page.fill('input[placeholder="Email"]', creds[0])
    page.fill('input[placeholder="Password"]', creds[1])
    page.click('button[type="submit"]')
    page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
    page.wait_for_timeout(800)


def shot(page, url, name, full=False):
    page.goto(UI + url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1200)
    page.screenshot(path=str(OUT / name), full_page=full)
    print("saved", name)


def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)

        def ctx():
            return browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)

        guest = ctx().new_page()
        shot(guest, "/", "ch5_ui_01_guest_home.png")
        shot(guest, "/properties/101", "ch5_ui_02_property_detail.png", full=True)
        shot(guest, "/login", "ch5_ui_03_login.png")
        shot(guest, "/sell", "ch5_ui_04_guard_redirect.png")

        user = ctx().new_page()
        login(user, USER)
        shot(user, "/sell", "ch5_ui_05_post_property.png", full=True)
        shot(user, "/track", "ch5_ui_06_track.png", full=True)

        officer = ctx().new_page()
        login(officer, OFFICER)
        shot(officer, "/officer", "ch5_ui_07_officer_desk.png", full=True)

        admin = ctx().new_page()
        login(admin, ADMIN)
        shot(admin, "/admin", "ch5_ui_08_admin_desk.png", full=True)
        browser.close()


if __name__ == "__main__":
    import sys
    if "--no-seed" not in sys.argv:
        seed()
    capture()
