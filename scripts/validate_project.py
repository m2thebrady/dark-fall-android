#!/usr/bin/env python3
"""Pre-build static checks. Does not replace an Android build or phone test."""
from pathlib import Path
import re, sys, hashlib
root=Path(__file__).resolve().parents[1]
html=root/'app/src/main/assets/index.html'
gradle=(root/'app/build.gradle').read_text()
manifest=(root/'app/src/main/AndroidManifest.xml').read_text()
activity=(root/'app/src/main/java/com/darkfall/game/MainActivity.java').read_text()
assert html.is_file() and html.stat().st_size>1_000_000, 'Bundled game is missing or too small'
assert "versionCode 994" in gradle and "versionName '0.994'" in gradle
assert "applicationId 'com.darkfall.game'" in gradle
assert 'android:screenOrientation="sensorLandscape"' in manifest
assert 'file:///android_asset/index.html' in activity
assert '<html' in html.read_text(errors='replace')[:10000].lower(), 'HTML entry point missing'
print('Project validation PASS')
print('Bundled game bytes:',html.stat().st_size)
print('Bundled game SHA-256:',hashlib.sha256(html.read_bytes()).hexdigest())
