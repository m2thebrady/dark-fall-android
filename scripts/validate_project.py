#!/usr/bin/env python3
"""Pre-build static checks. Does not replace an Android build or phone test."""
from pathlib import Path
import re, sys, hashlib, json
root=Path(__file__).resolve().parents[1]
html=root/'app/src/main/assets/index.html'
gradle=(root/'app/build.gradle').read_text()
manifest=(root/'app/src/main/AndroidManifest.xml').read_text()
activity=(root/'app/src/main/java/com/darkfall/game/MainActivity.java').read_text()
assert html.is_file() and html.stat().st_size>1_000_000, 'Bundled game is missing or too small'
bundle = json.loads((root/'game-bundle/manifest.json').read_text())
assert f"versionCode {bundle['version']}" in gradle
assert f"versionName '0.{bundle['version']}'" in gradle
assert html.stat().st_size == bundle['bytes'], 'Game bundle size mismatch'
assert hashlib.sha256(html.read_bytes()).hexdigest() == bundle['sha256'], 'Game bundle checksum mismatch'
assert f"<title>Dark Fall V{bundle['version']}</title>" in html.read_text(encoding='utf-8')[:10000], 'Displayed version mismatch'
assert "applicationId 'com.darkfall.game'" in gradle
assert 'android:screenOrientation="sensorLandscape"' in manifest
assert 'file:///android_asset/index.html' in activity
assert '<html' in html.read_text(errors='replace')[:10000].lower(), 'HTML entry point missing'
print('Project validation PASS')
print('Bundled game bytes:',html.stat().st_size)
print('Bundled game SHA-256:',hashlib.sha256(html.read_bytes()).hexdigest())
