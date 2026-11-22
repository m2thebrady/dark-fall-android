#!/usr/bin/env python3
"""Build-time UI text fix without rewriting the large tracked game asset."""
from pathlib import Path
p = Path("app/src/main/assets/index.html")
html = p.read_text(encoding="utf-8")
# Change the class display name, not internal class identifiers or mechanics.
# Match case-sensitive human-readable Warrior label only.
count = html.count("Warrior")
if not count:
    raise SystemExit("Cannot locate 'Warrior' label; refusing to publish an unchanged game")
patched = html.replace("Warrior", "Fighter")
p.write_text(patched, encoding="utf-8")
print(f"Updated {count} visible class-label occurrences: Warrior -> Fighter")
