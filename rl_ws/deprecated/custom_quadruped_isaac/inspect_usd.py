from pxr import Usd, UsdPhysics
import sys
import os

if len(sys.argv) < 2:
    print("Usage: python inspect_usd.py <path_to_usd>")
    sys.exit(1)

stage_path = sys.argv[1]
if not os.path.exists(stage_path):
    print(f"File not found: {stage_path}")
    sys.exit(1)

stage = Usd.Stage.Open(stage_path)
if not stage:
    print(f"Failed to open stage: {stage_path}")
    sys.exit(1)

print(f"Opened stage: {stage_path}")
found_roots = []
for prim in stage.Traverse():
    if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
        print(f"Articulation Root found at: {prim.GetPath()}")
        found_roots.append(prim.GetPath())

if not found_roots:
    print("No Articulation Roots found.")
