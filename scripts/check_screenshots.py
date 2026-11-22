#!/usr/bin/env python3
"""Validate browser screenshot audit artifacts; do not claim visual correctness."""
from pathlib import Path
import json, re
folder = Path("browser-smoke-results")
audit = json.loads((folder / "screenshot-audit.json").read_text())
for name in ("startup", "probe"):
    key = "startup" if name == "startup" else "probe"
    assert re.fullmatch(r"[a-f0-9]{64}", audit[key + "Hash"]), "Invalid image hash"
    assert audit[key + "Bytes"] > 1000, "Screenshot too small"
assert (folder / "startup.png").is_file()
assert (folder / "keyboard-probe.png").is_file()
print("Screenshot artifact integrity PASS; visual correctness not yet asserted")
