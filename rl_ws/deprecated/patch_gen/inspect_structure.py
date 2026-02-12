"""Inspect USD structure."""
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
parser = argparse.ArgumentParser(description="Inspect USD structure.")
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()
# force headless
args_cli.headless = True

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

try:
    from pxr import Usd, UsdPhysics, UsdGeom, PhysxSchema
except ImportError:
    pass

def main():
    # Default path
    usd_path = "/isaac-sim/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/custom_quadruped/robot.usd"
    
    if not os.path.exists(usd_path):
        print(f"File not found: {usd_path}")
        return

    stage = Usd.Stage.Open(usd_path)
    if not stage:
        print(f"Failed to open stage: {usd_path}")
        return

    print(f"Inspecting stage: {usd_path}")
    sys.stdout.flush()
    
    rigid_bodies = []
    joints = []
    
    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            rigid_bodies.append(prim.GetPath())
        
        if prim.IsA(UsdPhysics.Joint):
            joints.append(prim)

    print(f"\nFound {len(rigid_bodies)} Rigid Bodies:")
    for rb in rigid_bodies:
        prim = stage.GetPrimAtPath(rb)
        has_contact_api = prim.HasAPI(PhysxSchema.PhysxContactReportAPI)
        print(f"  {rb} (PhysxContactReportAPI: {has_contact_api})")
    sys.stdout.flush()

    print(f"\nFound {len(joints)} Joints:")
    for joint in joints:
        # Get body0 and body1 targets
        joint_api = UsdPhysics.Joint(joint)
        body0 = joint_api.GetBody0Rel().GetTargets()
        body1 = joint_api.GetBody1Rel().GetTargets()
        
        b0_str = str(body0[0]) if body0 else "None"
        b1_str = str(body1[0]) if body1 else "None"
        
        # Get joint type (by checking API schemas applied)
        # Or just checking the type of the prim
        type_name = joint.GetTypeName()
        
        print(f"  {joint.GetPath()} ({type_name}) connects {b0_str} -> {b1_str}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
    simulation_app.close()
