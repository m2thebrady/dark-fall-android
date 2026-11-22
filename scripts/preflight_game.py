#!/usr/bin/env python3
"""Fail-closed preflight for the bundled Dark Fall HTML and Android version."""
from html.parser import HTMLParser
from pathlib import Path
import re, subprocess, tempfile, hashlib

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
GRADLE = (ROOT / "app/build.gradle").read_text()
VALIDATOR = (ROOT / "scripts/validate_project.py").read_text()
PUBLISH = (ROOT / ".github/workflows/publish-update.yml").read_text()
class ScriptCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts, self.active, self.parts = [], None, []
    def handle_starttag(self, tag, attrs):
        if tag == "script":
            attrs = dict(attrs)
            self.active = attrs.get("type", "").lower() if not attrs.get("src") else "external"
            self.parts = []
    def handle_data(self, data):
        if self.active is not None:
            self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == "script" and self.active is not None:
            if self.active in ("", "text/javascript", "application/javascript", "module"):
                self.scripts.append((self.active, "".join(self.parts)))
            self.active = None
            self.parts = []

assert HTML.stat().st_size > 1_000_000, "Game asset missing/truncated"
html = HTML.read_text(encoding="utf-8")
assert html.lower().count("<html") >= 1 and "</html>" in html.lower(), "Malformed HTML document"
assert "Fighter" in html, "Fighter class label missing after patch"
version = re.search(r"\\bversionCode\\s+(\\d+)\\b", GRADLE)
name = re.search(r"\\bversionName\\s+['\"]([^'\"]+)['\"]", GRADLE)
assert version and name, "Missing Android version metadata"
assert name.group(1) == "0." + version.group(1), "Android versionName/versionCode mismatch"
assert f'versionCode {version.group(1)}' in VALIDATOR, "Static validator version mismatch"
assert "gh release create" in PUBLISH, "Signed release publishing step missing"
collector = ScriptCollector()
collector.feed(html)
assert collector.scripts, "No inline executable scripts found"
checked = 0
with tempfile.TemporaryDirectory() as folder:
    for idx, (kind, js) in enumerate(collector.scripts):
        if not js.strip():
            continue
        path = Path(folder) / f"inline_{idx}.{'mjs' if kind == 'module' else 'js'}"
        path.write_text(js, encoding="utf-8")
        result = subprocess.run(["node", "--check", str(path)], text=True, capture_output=True)
        if result.returncode:
            raise SystemExit(f"JavaScript syntax error in inline script {idx}:\\n{result.stderr[:2000]}")
        checked += 1
print(f"Preflight PASS: V{version.group(1)}, {checked} JS scripts, HTML SHA256 {hashlib.sha256(HTML.read_bytes()).hexdigest()}")
