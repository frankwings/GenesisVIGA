# SAM3D + Meshy Combined Pipeline

**Date:** 2026-02-10
**Status:** Implemented and tested

## Overview

VIGA originally used SAM3D and Meshy as independent asset sources — SAM3D reconstructs 3D objects from a target photo, Meshy generates 3D objects from text descriptions. This update combines them into a single pipeline where SAM3D initializes the scene from the target image, and Meshy replaces any poor-quality reconstructions.

## Motivation

- **SAM3D** excels at capturing the exact appearance of objects from a photo (e.g., the green tea bottle label), but can produce blobs or flat meshes for complex objects
- **Meshy** generates clean, well-formed 3D models from text, but can't match photo-specific details
- Combining them gives the best of both: SAM3D captures what it can, Meshy fills the gaps

## Architecture

```
Target Image
    |
    v
SAM Segmentation (sam env) --> 6 object masks
    |
    v
SAM3D Reconstruction (sam3d_py311 env) --> GLB files per object
    |
    v
Generator receives SAM3D GLB paths in memory
    |
    v
Phase 1: Render SAM3D scene, evaluate each object quality
    |
    v
Phase 1: Call get_better_object (Meshy) for poor-quality objects only
    |
    v
Phase 2: Compose final scene using best GLB (SAM3D or Meshy) for each object
    |
    v
Phase 2: Iterate with Verifier feedback
```

## Changes Made

### 1. `utils/_path.py` — Fix SAM3D worker env mapping

**Problem:** `sam3d_worker.py` was mapped to the `sam3d` conda env which has PyTorch 2.10.0. Kaolin 0.18.0 was compiled against PyTorch 2.8.0, causing a DLL import error.

**Fix:** Changed mapping from `"sam3d"` to `"sam3d_py311"`:
```python
"tools/sam3d/sam3d_worker.py": "sam3d_py311",
```

**Environment versions:**
| Env | PyTorch | Kaolin | Status |
|-----|---------|--------|--------|
| `sam3d` | 2.10.0+cu128 | 0.18.0 | BROKEN (DLL mismatch) |
| `sam3d_py311` | 2.8.0+cu128 | 0.18.0 | WORKING |

The docs (`20260205_SAM3D_Pipeline_Complete.html`) confirmed `sam3d_py311` with PyTorch 2.8.0 was the original working environment.

### 2. `agents/generator.py` — Capture SAM3D results in Generator memory

Previously, the `reconstruct_full_scene` result was discarded (`_ = ...`). Now it:
- Captures the result dict from SAM3D
- Extracts GLB paths and object names
- Injects them into `self.memory[1]['content']` as a text entry
- The Generator LLM can then reference these paths in its Blender scripts

```python
result = await self.tool_client.call_tool("reconstruct_full_scene", {})
if result.get("status") == "success" and result.get("output", {}).get("data"):
    data = result["output"]["data"]
    glb_paths = data.get("glb_paths", [])
    sam3d_info = f"SAM3D reconstructed {data.get('num_objects', 0)} objects:\n"
    for p in glb_paths:
        name = os.path.splitext(os.path.basename(p))[0]
        sam3d_info += f"- {name}: {p}\n"
    self.memory[1]['content'].append({"type": "text", "text": sam3d_info})
```

### 3. `prompts/static_scene/generator.py` — New combined prompt

Added `static_scene_generator_system_get_asset_sam3d` with two phases:

**Phase 1 — Evaluate SAM3D & Replace with Meshy:**
- Import all SAM3D GLBs into Blender and render
- Examine quality of each reconstruction
- Call `get_better_object` (Meshy) only for poor-quality objects
- Max 5 rounds on replacement

**Phase 2 — Scene Composition:**
- Import the BEST version of each object (SAM3D or Meshy)
- Position, scale, rotate to match target scene
- Iterate with Verifier feedback

### 4. `prompts/__init__.py` — Register new prompt

```python
'generator_get_asset_sam3d': static_scene_generator_system_get_asset_sam3d,
'verifier_get_asset_sam3d': static_scene_verifier_system,
```

### 5. `runners/static_scene.py` & `main.py` — CLI choice

Added `"get_asset_sam3d"` to `--prompt-setting` choices.

## Run Command

```bash
python runners/static_scene.py \
  --task=greentea \
  --model=gpt-5 \
  --blender-command=blender \
  --blender-script="data/static_scene/generator_script_eevee.py" \
  --prompt-setting=get_asset_sam3d \
  --generator-tools="tools/blender/exec.py,tools/generator_base.py,tools/assets/meshy.py,tools/sam3d/init.py,tools/initialize_plan.py" \
  --max-rounds=25
```

Key: `--generator-tools` includes both `tools/assets/meshy.py` AND `tools/sam3d/init.py`.

## Conda Environments

VIGA uses multiple isolated conda environments to manage conflicting dependencies (especially PyTorch/CUDA versions). Each tool script is mapped to its environment in `utils/_path.py`.

### `agent` — Main Orchestrator (Python 3.10)

Runs the runner, Generator/Verifier LLM agents, and Meshy API client.

| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.10.19 | Base interpreter |
| OpenAI | 2.6.1 | GPT-5 API calls (Generator + Verifier) |
| MCP | 1.20.0 | Model Context Protocol — tool server framework |
| httpx | 0.28.1 | Async HTTP client (used by OpenAI SDK + MCP) |
| Pydantic | 2.12.3 | Data validation for MCP messages |
| Pillow | 12.0.0 | Image loading/processing (renders, target images) |
| NumPy | 2.2.6 | Array operations (mask processing) |
| Requests | 2.32.5 | Meshy API HTTP calls |

**Tool scripts:** `tools/generator_base.py`, `tools/initialize_plan.py`, `tools/assets/meshy.py`, `tools/verifier_base.py`, `tools/undo.py`

### `sam` — SAM Segmentation (Python 3.10)

Runs Meta's Segment Anything Model (SAM) for object detection and mask generation from the target image.

| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.10.19 | Base interpreter |
| PyTorch | 2.10.0+cu128 | GPU inference for SAM ViT-H |
| NumPy | 2.2.6 | Mask array operations |
| Pillow | 12.0.0 | Target image loading |
| OpenCV | 4.13.0 | Image preprocessing, mask manipulation |
| segment_anything | — | Meta SAM model (ViT-H checkpoint: `sam_vit_h_4b8939.pth`) |

**Tool scripts:** `tools/sam3d/sam_worker.py`

### `sam3d_py311` — SAM3D 3D Reconstruction (Python 3.11)

Runs the SAM3D single-image-to-3D reconstruction pipeline using NVIDIA Kaolin and diffusion models. Requires PyTorch 2.8.0 specifically — Kaolin 0.18.0 was compiled against this version.

| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.11.14 | Base interpreter |
| PyTorch | 2.8.0+cu128 | GPU inference (must match Kaolin build) |
| Kaolin | 0.18.0 | NVIDIA 3D deep learning — mesh/voxel ops, differentiable rendering |
| NumPy | 2.4.1 | Point cloud and mesh data |
| Trimesh | 4.11.1 | GLB/OBJ mesh I/O |
| OmegaConf | 2.3.0 | Config loading (`pipeline.yaml`) |
| Diffusers | 0.36.0 | Zero123++ diffusion model for multi-view generation |
| Transformers | 5.0.0 | Model loading and tokenization |
| Pillow | 12.0.0 | Image processing for diffusion pipeline |

**Tool scripts:** `tools/sam3d/sam3d_worker.py`

**Note:** The `sam3d` env (PyTorch 2.10.0+cu128) is **broken** — Kaolin 0.18.0 DLL was compiled against PyTorch 2.8.0 and fails with `ImportError: DLL load failed while importing _C`. Always use `sam3d_py311`.

### `blender` — Blender MCP Server (Python 3.11)

Runs the MCP tool servers that communicate with Blender via subprocess. Does NOT run inside Blender itself — Blender uses its own bundled Python 3.11.

| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.11.14 | Base interpreter |
| MCP | 1.26.0 | Model Context Protocol — serves Blender tools |
| httpx | 0.28.1 | Async HTTP |
| Pydantic | 2.12.5 | MCP message validation |
| Pillow | 12.1.0 | Render image handling |

**Tool scripts:** `tools/blender/exec.py`, `tools/blender/investigator.py`

### External: Blender 4.5.5 LTS

Blender runs as a separate process (`--background` mode) with its own bundled Python 3.11. VIGA invokes it via subprocess, passing Blender Python scripts that import GLBs, set up scenes, and render images.

- **Executable:** `blender`
- **Render engine:** EEVEE Next (`BLENDER_EEVEE_NEXT`)
- **Script:** `data/static_scene/generator_script_eevee.py`

### Environment Mapping (`utils/_path.py`)

```
tools/blender/exec.py          → blender
tools/blender/investigator.py  → blender
tools/generator_base.py        → agent
tools/initialize_plan.py       → agent
tools/assets/meshy.py           → agent
tools/verifier_base.py         → agent
tools/undo.py                  → agent
tools/sam3d/sam_worker.py      → sam
tools/sam3d/sam3d_worker.py    → sam3d_py311
tools/sam3d/init.py            → sam3d
tools/sam3d/bridge.py          → sam3d
```

## Previous Failed Run (2026-02-09 21:17)

- SAM segmentation succeeded: detected 6 objects
- SAM3D reconstruction failed for ALL 6 objects due to kaolin DLL error (wrong env)
- Pipeline gracefully degraded to Meshy-only mode
- Generated 2 new Meshy assets (tea_bottle, monitor_stand) before being stopped

## Additional Fix: pipeline.yaml Path

**Problem:** `init.py` and `bridge.py` looked for `pipeline.yaml` at `checkpoints/hf/pipeline.yaml`, but the HuggingFace repo nests it under an extra `checkpoints/` subdirectory.

**Fix:** Updated both `tools/sam3d/init.py` and `tools/sam3d/bridge.py`:
```python
# Before:
ROOT, "utils", "third_party", "sam3d", "checkpoints", "hf", "pipeline.yaml"
# After:
ROOT, "utils", "third_party", "sam3d", "checkpoints", "hf", "checkpoints", "pipeline.yaml"
```

## Run Results

See [20260210_SAM3D_Meshy_Run1_Results.md](20260210_SAM3D_Meshy_Run1_Results.md) for Run 1 results with rendered images.
