"""Render round 19 of dynamic artist run 2:
1. Animation GIF: all 180 frames of the physics simulation
2. 360 Rotation GIF: camera orbits around frame-1 pose
"""
import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

BLENDER_CMD = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
BLEND_FILE = Path(r"D:\Projects\ProjectGenesis\GenesisVIGA\output\dynamic_scene\20260211_035101\artist\renders\19\state.blend")
OUTPUT_BASE = Path(r"D:\Projects\ProjectGenesis\GenesisVIGA\docs\test_results_images\dynamic_artist_run2")

ANIM_FRAMES_DIR = OUTPUT_BASE / "animation_frames_r19"
ANIM_GIF = OUTPUT_BASE / "gifs" / "round_19_animation.gif"
ROTATION_FRAMES_DIR = OUTPUT_BASE / "rotation_frames_r19"
ROTATION_GIF = OUTPUT_BASE / "gifs" / "round_19_rotation.gif"

RESOLUTION = 512
NUM_ROTATION_FRAMES = 36

# ── Blender script: render all animation frames ──
ANIM_SCRIPT = '''
import bpy
import sys
import os

argv = sys.argv
args = argv[argv.index("--") + 1:]
output_dir = args[0]
res = int(args[1])

os.makedirs(output_dir, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = res
scene.render.resolution_y = res
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False

start = scene.frame_start
end = scene.frame_end
print(f"Rendering animation frames {start} to {end}")

for frame in range(start, end + 1):
    scene.frame_set(frame)
    scene.render.filepath = os.path.join(output_dir, f"frame_{frame:04d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered frame {frame}/{end}")

print("Animation rendering complete!")
'''

# ── Blender script: 360 rotation at frame 1 ──
ROTATION_SCRIPT = '''
import bpy
import math
import sys
import os
import statistics
from mathutils import Vector

argv = sys.argv
args = argv[argv.index("--") + 1:]
output_dir = args[0]
num_frames = int(args[1])
res = int(args[2])

os.makedirs(output_dir, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = res
scene.render.resolution_y = res
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False

# Set to frame 1 — initial pose before physics
scene.frame_set(1)

camera = scene.camera
if camera is None:
    print("ERROR: No camera in scene!")
    sys.exit(1)

print(f"Camera lens: {camera.data.lens}mm")

# Ray-casting anchor point from original camera
depsgraph = bpy.context.evaluated_depsgraph_get()

cam_pos = camera.matrix_world.translation.copy()
cam_forward = (camera.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
cam_right = (camera.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
cam_up = (camera.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()

mesh_objects = [obj for obj in bpy.data.objects
                if obj.type == 'MESH' and obj != camera]

# Cast a grid of rays from the camera position
spread_angles_deg = [0, -10, 10, -20, 20, -5, 5, -15, 15]
hit_depths = []

for h_deg in spread_angles_deg:
    for v_deg in spread_angles_deg:
        h_rad = math.radians(h_deg)
        v_rad = math.radians(v_deg)
        ray_dir = (cam_forward
                   + math.tan(h_rad) * cam_right
                   + math.tan(v_rad) * cam_up).normalized()
        result, location, normal, index, obj, matrix = scene.ray_cast(
            depsgraph, cam_pos, ray_dir, distance=1000.0
        )
        if result:
            depth = (location - cam_pos).length
            hit_depths.append(depth)

if hit_depths:
    median_depth = statistics.median(hit_depths)
else:
    all_corners = []
    for obj in mesh_objects:
        if hasattr(obj, 'bound_box') and obj.bound_box:
            all_corners.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
    if all_corners:
        bb_center = sum(all_corners, Vector()) / len(all_corners)
        median_depth = (bb_center - cam_pos).length
    else:
        median_depth = 5.0

anchor = cam_pos + cam_forward * median_depth

offset = cam_pos - anchor
radius = max(min(offset.length, 30.0), 1.0)
horiz_dist = math.sqrt(offset.x**2 + offset.y**2)
elevation = math.atan2(offset.z, horiz_dist)
start_angle = math.atan2(offset.y, offset.x)

print(f"Anchor: {anchor}, radius: {radius:.2f}, elevation: {math.degrees(elevation):.1f}")

for i in range(num_frames):
    angle = start_angle + (2 * math.pi * i) / num_frames
    x = anchor.x + radius * math.cos(elevation) * math.cos(angle)
    y = anchor.y + radius * math.cos(elevation) * math.sin(angle)
    z = anchor.z + radius * math.sin(elevation)
    camera.location = Vector((x, y, z))
    direction = anchor - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    scene.render.filepath = os.path.join(output_dir, f"frame_{i:03d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered rotation frame {i+1}/{num_frames}")

print("Rotation rendering complete!")
'''


def run_blender(script_content, args_list):
    """Run a Blender Python script in background mode."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        script_path = f.name
    try:
        cmd = [
            BLENDER_CMD,
            "--background", str(BLEND_FILE),
            "--python", script_path,
            "--",
        ] + [str(a) for a in args_list]
        cmd_str = ' '.join(f'"{c}"' if ' ' in c else c for c in cmd)
        env = os.environ.copy()
        env['AL_LIB_LOGLEVEL'] = '0'
        result = subprocess.run(cmd_str, shell=True, stdin=subprocess.DEVNULL, env=env, timeout=1800)
        return result.returncode == 0
    finally:
        os.unlink(script_path)


def frames_to_gif(frames_dir, gif_path, duration_ms=80, size=384):
    """Convert PNG frames to animated GIF."""
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    if not frame_files:
        print(f"  No frames in {frames_dir}")
        return False
    frames = []
    for fp in frame_files:
        img = Image.open(fp)
        if img.mode == 'RGBA':
            bg = Image.new('RGB', img.size, (0, 0, 0))
            bg.paste(img, mask=img.split()[-1])
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((size, size), Image.LANCZOS)
        frames.append(img)
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(gif_path, save_all=True, append_images=frames[1:],
                   duration=duration_ms, loop=0, optimize=True)
    print(f"  GIF: {gif_path} ({len(frames)} frames, {gif_path.stat().st_size/1024:.0f} KB)")
    return True


def main():
    print("=" * 60)
    print("Step 1: Render animation frames (all 180 physics frames)")
    print("=" * 60)
    ANIM_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    ok = run_blender(ANIM_SCRIPT, [str(ANIM_FRAMES_DIR), RESOLUTION])
    if not ok:
        print("ERROR: Animation render failed!")
        return
    frames_to_gif(ANIM_FRAMES_DIR, ANIM_GIF, duration_ms=50, size=384)

    print()
    print("=" * 60)
    print("Step 2: Render 360 rotation at frame 1")
    print("=" * 60)
    ROTATION_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    ok = run_blender(ROTATION_SCRIPT, [str(ROTATION_FRAMES_DIR), NUM_ROTATION_FRAMES, RESOLUTION])
    if not ok:
        print("ERROR: Rotation render failed!")
        return
    frames_to_gif(ROTATION_FRAMES_DIR, ROTATION_GIF, duration_ms=100, size=384)

    print()
    print("Done! Output files:")
    print(f"  Animation GIF: {ANIM_GIF}")
    print(f"  Rotation GIF:  {ROTATION_GIF}")


if __name__ == "__main__":
    main()
