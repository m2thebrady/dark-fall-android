#!/usr/bin/env python3
import copy,hashlib,json,tempfile
from pathlib import Path
from validate_art_reference_lock import validate
profile=json.loads(Path("assets/profiles/warden.json").read_text())
with tempfile.TemporaryDirectory() as temp:
    base=Path(temp)
    (base/"master.png").write_bytes(b"synthetic reference bytes")
    digest=hashlib.sha256((base/"master.png").read_bytes()).hexdigest()
    lock={"character":"warden","status":"draft","frame":profile["frame"],"references":[{"path":"master.png","sha256":digest}]}
    assert validate(lock,base,profile)==[]
    approved=copy.deepcopy(lock);approved["status"]="approved"
    assert "approved lock requires approver" in validate(approved,base,profile)
    approved["approved_by"]="human reviewer"
    assert validate(approved,base,profile)==[]
    (base/"master.png").write_bytes(b"changed artwork")
    assert any("hash changed" in issue for issue in validate(approved,base,profile))
    unsafe=copy.deepcopy(lock);unsafe["references"][0]["path"]="../master.png"
    assert "unsafe reference path" in validate(unsafe,base,profile)
print("Reference lock tests passed")
