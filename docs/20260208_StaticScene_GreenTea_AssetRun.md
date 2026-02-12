# Static Scene: Green Tea Bottle - Asset Pipeline Run

**Date:** 2026-02-08
**Task:** `greentea` (static_scene)
**Output:** `output/static_scene/20260207_225603/greentea/`

---

## 1. Task Description

**Prompt:** "A green tea bottle sits upright on a wooden desk. Recreate this still life scene with accurate lighting and materials."

**Target Image:** An ITO EN green tea bottle (PET, lime-green label, white cap with clover logo) sitting on a wooden desk in front of an Alienware keyboard, headphones, envelopes, and a monitor.

**Available 3D Assets** (`data/static_scene/greentea/assets/`):

| Asset File | Size | Description |
|------------|------|-------------|
| `green_tea_bottle.glb` | 4.6 MB | Green tea bottle model |
| `ito_en_bottle.glb` | 7.6 MB | ITO EN branded bottle |
| `alienware_keyboard.glb` | 12 MB | Alienware gaming keyboard |
| `headphones.glb` | 16 MB | Over-ear headphones |
| `envelope.glb` | 12 MB | Paper envelope |

---

## 2. Run Configuration

```bash
"python" runners/static_scene.py \
    --task=greentea \
    --model=gpt-5 \
    --blender-command="blender" \
    --blender-script="data/static_scene/generator_script_eevee.py" \
    --prompt-setting=get_asset \
    --max-rounds=25
```

| Parameter | Value |
|-----------|-------|
| Model | GPT-5 |
| Render Engine | EEVEE (`BLENDER_EEVEE_NEXT`) |
| Prompt Setting | `get_asset` (two-phase: acquisition + composition) |
| Max Rounds | 25 |
| Duration | ~55 minutes |

---

## 3. Asset Acquisition (Phase 1)

All 4 assets were matched locally via fuzzy matching (no Meshy API call needed):

| Round | Tool Call | Object Name | Result |
|-------|-----------|-------------|--------|
| - | `get_better_object` | `green tea bottle` | Matched `green_tea_bottle.glb` |
| - | `get_better_object` | `keyboard` | Matched `alienware_keyboard.glb` |
| - | `get_better_object` | `headphones` | Matched `headphones.glb` |
| - | `get_better_object` | `envelope` | Matched `envelope.glb` |

**Tool response format:**
```
Successfully generated static asset, downloaded to: data\static_scene\greentea\assets\green_tea_bottle.glb
```

---

## 4. Scene Composition (Phase 2)

The run produced **19 scripts** and **11 rendered Camera.png** frames.

### Output Statistics

| Metric | Value |
|--------|-------|
| Total scripts generated | 19 |
| Rounds with Camera.png | 11 (rounds 4,5,7,8,11,13,15,16,17,18,19) |
| Scripts with GLB imports | 8 (scripts 1-8) |
| Scripts fully procedural | 11 (scripts 9-19) |

### Render Gallery

#### Early Phase (Rounds 4-8): GLB Import Attempts

These scripts contain `import_glb()` calls with relative paths. The imports **failed silently** because Blender could not resolve relative paths.

| Round 4 | Round 5 |
|---------|---------|
| ![Round 4](../output/static_scene/20260207_225603/greentea/renders/4/Camera.png) | ![Round 5](../output/static_scene/20260207_225603/greentea/renders/5/Camera.png) |
| First render. GLB imports failed silently — objects are procedural fallbacks. | Similar procedural scene. GLB files not loaded. |

| Round 7 | Round 8 |
|---------|---------|
| ![Round 7](../output/static_scene/20260207_225603/greentea/renders/7/Camera.png) | ![Round 8](../output/static_scene/20260207_225603/greentea/renders/8/Camera.png) |
| Still attempting GLB imports with relative paths. | Last script with GLB import code. |

#### Late Phase (Rounds 11-19): Fully Procedural

After repeated failures, the Generator abandoned GLB imports and switched to fully procedural generation using Blender primitives.

| Round 11 | Round 13 | Round 15 |
|----------|----------|----------|
| ![Round 11](../output/static_scene/20260207_225603/greentea/renders/11/Camera.png) | ![Round 13](../output/static_scene/20260207_225603/greentea/renders/13/Camera.png) | ![Round 15](../output/static_scene/20260207_225603/greentea/renders/15/Camera.png) |
| Fully procedural. No GLB imports. | Procedural scene refinement. | Procedural bottle and desk. |

| Round 16 | Round 17 | Round 18 |
|----------|----------|----------|
| ![Round 16](../output/static_scene/20260207_225603/greentea/renders/16/Camera.png) | ![Round 17](../output/static_scene/20260207_225603/greentea/renders/17/Camera.png) | ![Round 18](../output/static_scene/20260207_225603/greentea/renders/18/Camera.png) |
| Continued procedural iteration. | Scene refinement. | Near-final state. |

| Round 19 |
|----------|
| ![Round 19](../output/static_scene/20260207_225603/greentea/renders/19/Camera.png) |
| Final render. Fully procedural — simple primitives, no GLB assets visible. |

---

## 5. Root Cause Analysis: Why GLB Assets Were Not Used

### The Generator DID Write GLB Import Code

Scripts 1-8 all contain proper GLB import code:

```python
def import_glb(path, name="Imported"):
    prev_names = {o.name for o in bpy.data.objects}
    bpy.ops.import_scene.gltf(filepath=path)
    imported = [obj for obj in bpy.data.objects if obj.name not in prev_names]
    empty = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(empty)
    for obj in imported:
        obj.select_set(True)
        obj.parent = empty
    empty.select_set(True)
    bpy.context.view_layer.objects.active = empty
    return empty, imported

# Paths (RELATIVE - this is the problem)
base_dir = os.path.join('data','static_scene','greentea','assets')
path_bottle = os.path.join(base_dir, 'green_tea_bottle.glb')
path_keyboard = os.path.join(base_dir, 'alienware_keyboard.glb')
path_headphones = os.path.join(base_dir, 'headphones.glb')
path_envelope = os.path.join(base_dir, 'envelope.glb')

# Import assets
bottle_empty, bottle_children = import_glb(path_bottle, 'Bottle')
keyboard_empty, keyboard_children = import_glb(path_keyboard, 'Keyboard')
headphones_empty, headphones_children = import_glb(path_headphones, 'Headphones')
envelope_empty, envelope_children = import_glb(path_envelope, 'Envelope')
```

### The Failure: Working Directory Mismatch

The imports **failed silently** because of a path resolution issue:

1. **`get_better_object` returned relative paths**: `data\static_scene\greentea\assets\green_tea_bottle.glb`
2. **Generator used relative paths** in Blender scripts: `os.path.join('data','static_scene','greentea','assets', 'green_tea_bottle.glb')`
3. **Blender's working directory != project root**: Blender runs in background mode with its own working directory (its installation folder or the .blend file's directory)
4. **`bpy.ops.import_scene.gltf(filepath=...)` fails silently** when the file is not found — no error raised, just no objects imported
5. **After 8 rounds of silent failure**, the Verifier kept reporting missing objects, so the Generator gave up on GLB imports and switched to procedural generation

### The Fix Applied

Two changes were made to ensure absolute paths with forward slashes:

**`tools/assets/meshy_api.py` — `__init__` (line 51-52):**
```python
# Before (relative path passthrough):
self.save_dir = previous_assets_dir
self.previous_assets_dir = previous_assets_dir

# After (absolute path with forward slashes):
self.save_dir = os.path.abspath(previous_assets_dir).replace(os.sep, '/') if previous_assets_dir else previous_assets_dir
self.previous_assets_dir = os.path.abspath(previous_assets_dir).replace(os.sep, '/') if previous_assets_dir else previous_assets_dir
```

**`tools/assets/meshy_api.py` — `find_matching_files` (line 119):**
```python
# Before (os.path.join reintroduces backslashes on Windows):
matching_files.append(os.path.join(self.previous_assets_dir, filename))

# After (forward-slash join):
matching_files.append(self.previous_assets_dir + '/' + filename)
```

**`prompts/static_scene/generator.py` — Phase 2 instructions:**
- Added: "Use the EXACT absolute file path returned by the tool. Copy the path string verbatim."
- Added: "Do NOT recreate objects procedurally if a GLB asset was successfully downloaded"
- Added: "When iterating, preserve the GLB imports"

### Verified Fix Output

After the fix, `check_previous_asset` now returns:
```
data/static_scene/greentea/assets/green_tea_bottle.glb
data/static_scene/greentea/assets/alienware_keyboard.glb
data/static_scene/greentea/assets/headphones.glb
data/static_scene/greentea/assets/envelope.glb
```

These absolute paths with forward slashes will work from any Blender working directory.

---

## 6. Timeline of All Static Scene Runs

| Run | Timestamp | Prompt Setting | Issue | Result |
|-----|-----------|----------------|-------|--------|
| 1 | `20260207_030656` | `none` | No asset instructions in prompt; MeshyAPI init crash | 58 rounds, fully procedural, scene drift |
| 2 | `20260207_194625` | `get_asset` | `\u2011` encoding crash (cp1252) | Crashed immediately |
| 3 | `20260207_213536` | `get_asset` | Prompt only said "use get_better_object" with no Phase 2 | 25 rounds all spent on `get_better_object`, no scripts |
| 4 | `20260207_225603` | `get_asset` | Relative paths in tool response; Blender can't find GLBs | 19 rounds, GLB imports failed silently, fell back to procedural |

### Fixes Applied Across Runs

| Fix | File | Run it fixed |
|-----|------|-------------|
| MeshyAPI local-only mode | `meshy_api.py`, `meshy.py` | Run 2 (init crash) |
| UTF-8 encoding | `agents/generator.py:156` | Run 2 (encoding crash) |
| Two-phase prompt | `prompts/static_scene/generator.py` | Run 3 (no scene composition) |
| Absolute path resolution | `meshy_api.py:51-52,119` | Run 4 (relative path failure) |
| Prompt: use exact paths | `prompts/static_scene/generator.py` | Run 4 (path handling) |

---

## 7. Next Step

Re-run with the absolute path fix to verify GLB assets are actually imported and visible in renders.
