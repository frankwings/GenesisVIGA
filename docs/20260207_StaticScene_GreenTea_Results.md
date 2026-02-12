# Static Scene: Green Tea Bottle - Run Results

**Date:** 2026-02-07
**Task:** `greentea` (static_scene)
**Output:** `output/static_scene/20260207_030656/greentea/`

---

## 1. Task Description

**Prompt:** "A green tea bottle sits upright on a wooden desk. Recreate this still life scene with accurate lighting and materials."

**Target Image:** An ITO EN green tea bottle (PET, lime-green label, white cap with clover logo) sitting on a wooden desk in front of an Alienware keyboard, headphones, envelopes, and a monitor.

**Available 3D Assets** (`data/static_scene/greentea/assets/`):

| Asset File | Description |
|------------|-------------|
| `green_tea_bottle.glb` | Green tea bottle model |
| `ito_en_bottle.glb` | ITO EN branded bottle |
| `alienware_keyboard.glb` | Alienware gaming keyboard |
| `headphones.glb` | Over-ear headphones |
| `envelope.glb` | Paper envelope |

---

## 2. Run Configuration

```bash
"python" runners/static_scene.py \
    --task=greentea \
    --model=gpt-5 \
    --blender-command="blender" \
    --blender-script="data/static_scene/generator_script_eevee.py" \
    --prompt-setting=none
```

| Parameter | Value |
|-----------|-------|
| Model | GPT-5 |
| Render Engine (iterations) | EEVEE (`BLENDER_EEVEE_NEXT`) |
| Render Engine (final) | CYCLES (GPU, 512 samples, 1024x1024) |
| Prompt Setting | `none` (base system prompt) |
| Max Rounds | 100 (default) |
| Memory Length | 12 |

**Duration:** ~4 hours (03:06 - 07:12)

---

## 3. Asset Usage Analysis

### Result: Assets were NOT used

The run did **not** import any of the pre-existing GLB assets. All scene objects were built from scratch using Blender primitives (`bpy.ops.mesh.primitive_*`) and procedural materials.

**Why:**

1. **`--prompt-setting=none`** uses the base system prompt, which does not instruct the agent to use local assets.

2. **The Generator tried to download assets** via `get_better_object` (Meshy API tool) but the tool initialization failed:
   ```
   'NoneType' object has no attribute 'check_previous_asset'
   ```

3. **Fallback:** After download failures, the Generator switched to fully procedural generation.

**How assets SHOULD work:**

The `get_better_object` tool has a `check_previous_asset()` method that performs fuzzy matching against the local `assets/` directory **before** calling the Meshy API. If a local GLB matches, it returns the local path directly — no API call needed. The failure was due to the `MeshyAPI` object not initializing (likely missing API key), which prevented even the local file check from running.

**Fix options:**
- Fix `MeshyAPI` initialization to allow local-only mode (no API key needed for cached assets)
- Or directly import GLBs in the Blender script: `bpy.ops.import_scene.gltf(filepath="path/to/asset.glb")`

---

## 4. Iteration Results (EEVEE)

The run produced **58 scripts** and **36 rendered Camera.png** frames across 58 render directories. Rounds 1-6 only saved `state.blend` (Blender script errors or no Camera object). Renders started appearing from Round 7.

### Output Statistics

| Metric | Value |
|--------|-------|
| Total scripts generated | 58 |
| Rounds with Camera.png | 36 |
| Rounds with state.blend only | 27 |
| Investigator scripts | 76 |
| Total generated Python code | ~18,800 lines |
| Total output size | 164 MB |
| Renders directory | 66 MB |
| Generator memory | 9 MB |
| Verifier memory | 34 MB |

### Target Image

![Target](../data/static_scene/greentea/target.png)

### Render Gallery (All Rounds)

#### Early Phase (Rounds 7-13): Scene Establishment

| Round 7 | Round 8 | Round 9 |
|---------|---------|---------|
| ![Round 7](../output/static_scene/20260207_030656/greentea/renders/7/Camera.png) | ![Round 8](../output/static_scene/20260207_030656/greentea/renders/8/Camera.png) | ![Round 9](../output/static_scene/20260207_030656/greentea/renders/9/Camera.png) |
| First successful render. Dark green bottle, teal keyboard bar, ring objects. | Bottle refined, similar composition. | Lime green bottle (closer to target). Improved lighting. |

| Round 12 | Round 13 |
|----------|----------|
| ![Round 12](../output/static_scene/20260207_030656/greentea/renders/12/Camera.png) | ![Round 13](../output/static_scene/20260207_030656/greentea/renders/13/Camera.png) |
| Camera angle changed. Teal keyboard with gray body. Small green-capped bottle. | Continued refinement of scene composition. |

#### Mid Phase (Rounds 15-26): Refinement & Early Drift

| Round 15 | Round 16 | Round 18 |
|----------|----------|----------|
| ![Round 15](../output/static_scene/20260207_030656/greentea/renders/15/Camera.png) | ![Round 16](../output/static_scene/20260207_030656/greentea/renders/16/Camera.png) | ![Round 18](../output/static_scene/20260207_030656/greentea/renders/18/Camera.png) |
| Scene evolving. | Keyboard prominent. White papers added. Bottle pushed aside. | Continued iteration. |

| Round 19 | Round 21 | Round 23 |
|----------|----------|----------|
| ![Round 19](../output/static_scene/20260207_030656/greentea/renders/19/Camera.png) | ![Round 21](../output/static_scene/20260207_030656/greentea/renders/21/Camera.png) | ![Round 23](../output/static_scene/20260207_030656/greentea/renders/23/Camera.png) |
| Scene restructured. | Yellow-green bottle returns with white cap. Shadow on desk. | Bottle with bands and cap. |

| Round 25 | Round 26 |
|----------|----------|
| ![Round 25](../output/static_scene/20260207_030656/greentea/renders/25/Camera.png) | ![Round 26](../output/static_scene/20260207_030656/greentea/renders/26/Camera.png) |
| Green bottle with horizontal bands. Teal screen corner. Good color match. | Continued refinement. |

#### Late Phase (Rounds 28-44): Scene Drift

| Round 28 | Round 30 | Round 33 |
|----------|----------|----------|
| ![Round 28](../output/static_scene/20260207_030656/greentea/renders/28/Camera.png) | ![Round 30](../output/static_scene/20260207_030656/greentea/renders/30/Camera.png) | ![Round 33](../output/static_scene/20260207_030656/greentea/renders/33/Camera.png) |
| Scene changing. | Extreme camera angle. Bottle at corner. Overexposed. | Scene restructured again. |

| Round 34 | Round 36 | Round 38 |
|----------|----------|----------|
| ![Round 34](../output/static_scene/20260207_030656/greentea/renders/34/Camera.png) | ![Round 36](../output/static_scene/20260207_030656/greentea/renders/36/Camera.png) | ![Round 38](../output/static_scene/20260207_030656/greentea/renders/38/Camera.png) |
| Continued drift. | Further changes. | Monitor, keyboard with gray keycaps, ring objects. Small bottle. |

| Round 41 | Round 42 | Round 43 |
|----------|----------|----------|
| ![Round 41](../output/static_scene/20260207_030656/greentea/renders/41/Camera.png) | ![Round 42](../output/static_scene/20260207_030656/greentea/renders/42/Camera.png) | ![Round 43](../output/static_scene/20260207_030656/greentea/renders/43/Camera.png) |
| Scene iteration. | Green-yellow bottle with keyboard and monitor. Bottle is secondary. | Continued changes. |

| Round 44 |
|----------|
| ![Round 44](../output/static_scene/20260207_030656/greentea/renders/44/Camera.png) |
| Further drift from target. |

#### Final Phase (Rounds 45-58): Divergence

| Round 45 | Round 46 | Round 47 |
|----------|----------|----------|
| ![Round 45](../output/static_scene/20260207_030656/greentea/renders/45/Camera.png) | ![Round 46](../output/static_scene/20260207_030656/greentea/renders/46/Camera.png) | ![Round 47](../output/static_scene/20260207_030656/greentea/renders/47/Camera.png) |
| Scene heavily modified. | Continued iteration. | Further changes. |

| Round 48 | Round 49 | Round 50 |
|----------|----------|----------|
| ![Round 48](../output/static_scene/20260207_030656/greentea/renders/48/Camera.png) | ![Round 49](../output/static_scene/20260207_030656/greentea/renders/49/Camera.png) | ![Round 50](../output/static_scene/20260207_030656/greentea/renders/50/Camera.png) |
| Desk setup focus. | Continued drift. | Scene diverged from target. |

| Round 51 | Round 52 | Round 53 |
|----------|----------|----------|
| ![Round 51](../output/static_scene/20260207_030656/greentea/renders/51/Camera.png) | ![Round 52](../output/static_scene/20260207_030656/greentea/renders/52/Camera.png) | ![Round 53](../output/static_scene/20260207_030656/greentea/renders/53/Camera.png) |
| Near-final state. | "ALIENWARE" text on keyboard. Bottle no longer focus. | Continued. |

| Round 55 | Round 56 | Round 57 |
|----------|----------|----------|
| ![Round 55](../output/static_scene/20260207_030656/greentea/renders/55/Camera.png) | ![Round 56](../output/static_scene/20260207_030656/greentea/renders/56/Camera.png) | ![Round 57](../output/static_scene/20260207_030656/greentea/renders/57/Camera.png) |
| Late iteration. | Near end. | Almost final. |

| Round 58 |
|----------|
| ![Round 58](../output/static_scene/20260207_030656/greentea/renders/58/Camera.png) |
| Last EEVEE render before termination. |

### Final CYCLES Render

| CYCLES Final |
|-------------|
| ![CYCLES Final](../output/static_scene/20260207_030656/greentea/CYCLES_final_Camera.png) |
| CYCLES GPU render (512 samples, 1024x1024) of the final scene state. |

### Key Observations

1. **Best results around Rounds 9-25**: The green tea bottle was most prominent and closest to the target color/shape in this range.

2. **Scene drift after Round 25**: The Generator progressively focused on desk accessories (keyboard, monitor, rings) while the bottle became less prominent or was occasionally lost from the frame entirely.

3. **No convergence**: With `max_rounds=100`, the iterative loop kept modifying the scene without converging. The Verifier kept requesting improvements, and the Generator kept restructuring the scene.

4. **Camera instability**: Camera position and angle changed across rounds, sometimes dramatically (Round 30 showed an extreme top-down angle).

---

## 5. Final CYCLES Render

After stopping the EEVEE iteration run at Round 58, a final CYCLES render was performed on the last `blender_file.blend`.

| Setting | Value |
|---------|-------|
| Engine | CYCLES |
| Device | GPU (CUDA) |
| Samples | 512 |
| Resolution | 1024 x 1024 |
| Render time | ~6 seconds |
| Output | `CYCLES_final_Camera.png` |

The CYCLES render provides significantly better material quality compared to EEVEE — translucent bottle, soft shadows, and realistic lighting.

---

## 6. Directory Structure

```
output/static_scene/20260207_030656/greentea/
├── blender_file.blend              # Final scene state (1.1 MB)
├── render_cycles_final.py          # CYCLES render script
├── CYCLES_final_Camera.png         # Final CYCLES render (1024x1024)
├── generator_memory.json           # Generator conversation history (9 MB)
├── verifier_memory.json            # Verifier conversation history (34 MB)
├── _tool_call.json                 # Initial tool call config
├── scripts/                        # Generator Blender scripts (1-58)
│   ├── 1.py                        # First script (~350 lines)
│   ├── 2.py
│   ├── ...
│   └── 58.py
├── renders/                        # Per-round render output (66 MB)
│   ├── 1/state.blend               # Rounds 1-6: blend only (no Camera.png)
│   ├── ...
│   ├── 7/Camera.png + state.blend  # Rounds 7+: renders appear
│   ├── ...
│   └── 52/Camera.png + state.blend
├── investigator/                   # Verifier analysis data (38 MB)
│   ├── current_scene.blend
│   ├── renders/                    # Investigator renders per round
│   ├── scripts/                    # Investigator Blender scripts (1-76)
│   └── tmp/
│       ├── camera_info.json
│       ├── rotate_info.json
│       └── scene_info.json
└── tmp/                            # Temporary files
```

---

## 7. Lessons Learned

### 1. `--max-rounds` should be capped
Default is 100, which is far too many. The scene drifted significantly after ~25 rounds. Recommended: `--max-rounds 20-30`.

### 2. `--prompt-setting=none` skips asset usage
To use pre-existing GLB assets, use `--prompt-setting=get_asset`. However, the `get_better_object` tool must be properly initialized (requires `MeshyAPI` object, which failed in this run).

### 3. Local assets don't need Meshy API
The `check_previous_asset()` method does local fuzzy matching before calling the API. The initialization bug prevented this local-only path from working. Fixing the tool to initialize without an API key would enable local asset usage.

### 4. EEVEE is fast enough for iteration
EEVEE renders completed in seconds vs. CYCLES which would take much longer per frame. The EEVEE-for-iteration, CYCLES-for-final approach is validated.

### 5. Scene drift is a real problem
Without a mechanism to "lock" successfully placed objects, the Generator may restructure the entire scene each round. A more constrained prompt or incremental-edit approach would help prevent drift.

### 6. Blender scripts start with CYCLES by default
The first generated script (1.py) used `scene.render.engine = 'CYCLES'` despite the EEVEE override in `generator_script_eevee.py`. The EEVEE script correctly overrides the engine after the user script runs, so this is not an issue.

---

## 8. Recommended Next Steps

1. **Fix `MeshyAPI` initialization** to support local-only mode (no API key required for cached assets)
2. **Re-run with assets**: `--prompt-setting=get_asset --max-rounds=25`
3. **Or manually import GLBs**: Write a custom init script that imports the local GLB files before the Generator starts iterating
4. **Add rotation GIF**: Use `tools/render_rounds_gif.py` on the render outputs to visualize the scene progression
