"""Fix nested articulation roots in robot.usd."""
import argparse
import os
import sys

# isaaclab imports
try:
    from isaaclab.app import AppLauncher
except ImportError:
    print("Error: 'isaaclab' module not found. Make sure you are running this with isaaclab.sh -p")
    sys.exit(1)

# create argparser
parser = argparse.ArgumentParser(description="Fix USD.")
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()
# force headless
args_cli.headless = True

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# Now imports are safe
try:
    from pxr import Usd, UsdPhysics, Sdf, PhysxSchema
except ImportError:
    print("Error: 'pxr' module not found even after AppLauncher. This is unexpected.")
    simulation_app.close()
    sys.exit(1)

def main():
    # Define likely paths for the robot.usd file inside the container
    # The log indicated the file was found at:
    # /isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/custom_quadruped/robot.usd
    
    paths_to_check = [
        "/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/custom_quadruped/robot.usd",
        # Fallback relative to current dir if running in workspace
        os.path.abspath("robot.usd"), 
    ]

    target_usd_path = None
    for path in paths_to_check:
        if os.path.exists(path):
            target_usd_path = path
            break

    if not target_usd_path:
        print("Error: Could not locate robot.usd in the following paths:")
        for path in paths_to_check:
            print(f"  - {path}")
        return

    print(f"Found robot.usd at: {target_usd_path}")
    sys.stdout.flush()

    # Open the stage
    stage = Usd.Stage.Open(target_usd_path)
    if not stage:
        print(f"Error: Could not open stage {target_usd_path}")
        sys.stdout.flush()
        return

    print(f"Opened stage successfully.")
    sys.stdout.flush()

    # Traverse and find all Articulation Roots
    articulation_roots = []
    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
            articulation_roots.append(prim)

    if not articulation_roots:
        print("No articulation roots found.")
        sys.stdout.flush()
        return

    print(f"Found {len(articulation_roots)} articulation roots:")
    for prim in articulation_roots:
        print(f"  - {prim.GetPath()}")
    sys.stdout.flush()

    # Logic to fix:
    # If we have nested roots (one is descendant of another), remove the descendant's API.
    # We also prefer the top-most root usually.
    
    # Sort by path length to process parents first (though for removal we might want to be careful)
    # Actually, if A is parent of B, and both are roots. We usually want A to be the root.
    
    for prim in articulation_roots:
        path = prim.GetPath()
        # Check if this prim is a child of another root
        is_nested = False
        parent_root = None
        for other in articulation_roots:
            if other == prim:
                continue
            other_path = other.GetPath()
            if str(path).startswith(str(other_path) + "/"):
                is_nested = True
                parent_root = other_path
                break
        
        if is_nested:
            print(f"Prim {path} is nested under {parent_root}. Removing ArticulationRootAPI...")
            prim.RemoveAPI(UsdPhysics.ArticulationRootAPI)
            prim.RemoveAPI(UsdPhysics.RigidBodyAPI) # Sometimes RigidBodyAPI also causes issues if double defined on root/base
            # Specifically the error mentioned ArticulationRoot.
            print("API removed.")
            
            # Save the stage
            try:
                stage.GetRootLayer().Save()
                print(f"Stage saved to {target_usd_path}")
            except Exception as e:
                print(f"Error saving stage: {e}")
            sys.stdout.flush()

    # FIX: Add RigidBodyAPI to base if missing
    base_prim_path = "/SpotMicroAI/base" # Assuming standard path based on logs
    # Find base prim dynamically if needed, but logs showed /World/SpotMicroAI/base
    # The stage path is root relative inside the stage, so /SpotMicroAI/base (without /World if opened directly? No, stage open opens the file content).
    # Inspect showed /World/SpotMicroAI/base but usually /World is the default prim.
    # Let's search for "base" prim under the articulation root.
    
    # We found roots earlier. Let's pick the top one.
    root_prim = articulation_roots[0] if articulation_roots else None
    if root_prim:
         # Check if root_prim has a child named 'base'
         base_prim = stage.GetPrimAtPath(root_prim.GetPath().AppendChild("base"))
         if base_prim.IsValid():
             print(f"Checking base prim: {base_prim.GetPath()}")
             if not base_prim.HasAPI(UsdPhysics.RigidBodyAPI):
                 print(f"Adding RigidBodyAPI to {base_prim.GetPath()} to unify articulation...")
                 UsdPhysics.RigidBodyAPI.Apply(base_prim)
                 
                 # Also add MassAPI
                 mass_api = UsdPhysics.MassAPI.Apply(base_prim)
                 mass_api.CreateMassAttr(1.0) # 1kg dummy mass
                 
                 # Save
                 stage.GetRootLayer().Save()
                 print("Base fixed.")
             else:
                 print("Base already has RigidBodyAPI.")
         else:
             print("Base prim not found under root.")

    # FIX: Increase calf joint limits
    # The config requests 1.745 rad (100 deg) but limit is 1.5 rad (86 deg).
    # We will increase limits for all *calf_joint prims to [-150, 150] degrees.
    print("Checking calf joint limits...")
    for prim in stage.Traverse():
        if prim.IsA(UsdPhysics.Joint) and "calf_joint" in prim.GetName():
            joint = UsdPhysics.RevoluteJoint(prim)
            if joint:
                lower = joint.GetLowerLimitAttr().Get()
                upper = joint.GetUpperLimitAttr().Get()
                print(f"Joint {prim.GetName()} current limits: [{lower}, {upper}]")
                
                # Expand limits if necessary (assuming degrees if values are large)
                # If values are small (< 2*pi), they might be radians, but inspect said 85.9 which is degrees.
                
                target_limit = 150.0
                
                if lower > -100.0 or upper < 100.0:
                     print(f"Expanding limits for {prim.GetName()} to [{-target_limit}, {target_limit}]")
                     joint.GetLowerLimitAttr().Set(-target_limit)
                     joint.GetUpperLimitAttr().Set(target_limit)
                     
                     try:
                        stage.GetRootLayer().Save()
                     except Exception as e:
                        print(f"Error saving stage: {e}")

    # FIX: Add PhysxContactReportAPI to trunk and feet
    # This is needed because Isaac Lab's spawner seems to fail adding it, or the sensors expect it.
    bodies_needing_contact = ["trunk", "FL_foot", "FR_foot", "RL_foot", "RR_foot"]
    print("Checking contact reporting APIs...")
    for prim in stage.Traverse():
        name = prim.GetName()
        if name in bodies_needing_contact:
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                
                # Add CollisionAPI if missing (might be needed for detection)
                if not prim.HasAPI(UsdPhysics.CollisionAPI):
                     print(f"Adding CollisionAPI to {prim.GetPath()}")
                     UsdPhysics.CollisionAPI.Apply(prim)

                if not prim.HasAPI(PhysxSchema.PhysxContactReportAPI):
                    print(f"Adding PhysxContactReportAPI to {prim.GetPath()}")
                    PhysxSchema.PhysxContactReportAPI.Apply(prim)
                    try:
                        stage.GetRootLayer().Save()
                    except Exception as e:
                        print(f"Error saving stage: {e}")
                else:
                    print(f"{name} already has PhysxContactReportAPI.")

    print("Done.")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
    simulation_app.close()