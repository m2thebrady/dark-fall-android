#!/usr/bin/env python3
"""One-command character asset checks and non-destructive preview preparation."""
import argparse,json,sys
from pathlib import Path
from validate_body_profile import validate as validate_profile
from check_animation_coverage import check as check_coverage
from inspect_palette import inspect as inspect_palette

def run(profile_path,manifest_path,image_path,output):
    profile=json.loads(Path(profile_path).read_text())
    manifest=json.loads(Path(manifest_path).read_text())
    errors=validate_profile(profile)+check_coverage(profile,manifest)
    if errors:raise ValueError("; ".join(errors))
    # The established validator loads the sprite sheet from the manifest image path.\n    resolved_image=(Path(manifest_path).parent / manifest.get("image","")).resolve()\n    if resolved_image!=Path(image_path).resolve():raise ValueError("image argument does not match manifest image path")
    import subprocess
    result=subprocess.run([sys.executable,str(Path(__file__).with_name("validate_asset.py")),str(manifest_path)],capture_output=True,text=True)
    if result.returncode:raise ValueError("sprite validation failed: "+result.stdout+result.stderr)
    palette=inspect_palette(image_path,profile_path)
    output=Path(output)
    if output.exists():raise FileExistsError(f"Refusing to overwrite {output}")
    output.mkdir(parents=True)
    report={"profile":str(profile_path),"manifest":str(manifest_path),"image":str(image_path),"palette":palette,"sprite_validation":"passed","coverage_validation":"passed"}
    (output/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("profile",type=Path)
    parser.add_argument("manifest",type=Path)
    parser.add_argument("image",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    try:print(json.dumps(run(args.profile,args.manifest,args.image,args.output),indent=2))
    except (ValueError,OSError) as e:print(e,file=sys.stderr);raise SystemExit(1)
if __name__=="__main__":main()
