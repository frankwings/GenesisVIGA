# Static Scene: Green Tea — Run 9 (Meshy API Text-to-3D Generated Assets)

**Date:** 2026-02-08
**Task:** `greentea` (static_scene)
**Output:** `output/static_scene/20260208_224146/greentea/`
**Previous Runs:** Run 7 (SAM3D assets), Run 8 (SAM3D assets, Meshy key configured but unused)

---

## 1. Run Configuration

First run using **Meshy API text-to-3D generation** for all assets. SAM3D assets were backed up to `data/static_scene/greentea/assets_sam3d_backup/` so the local fuzzy matcher could not intercept.

| Parameter | Value |
|-----------|-------|
| Model | GPT-5 |
| Render Engine | EEVEE (`BLENDER_EEVEE_NEXT`) |
| Prompt Setting | `get_asset_simple` |
| Max Rounds | 15 |
| Duration | ~56 minutes (3364 seconds) |
| Meshy API Key | Active — all 5 assets generated via API |
| Asset Source | **Meshy text-to-3D** (NOT local fuzzy match) |

---

## 2. Asset Acquisition (Meshy API)

GPT-5 wrote detailed text descriptions for each object, which Meshy converted to 3D GLB models:

| Round | Object | Meshy Description (abbreviated) | Generation Time |
|-------|--------|--------------------------------|-----------------|
| 1 | Table | "Simple modern rectangular desk, 1.2m x 0.6m x 0.75m, light gray wood/laminate, four straight legs" | ~3 min |
| 2 | Bottle | "500ml Ito En Oi Ocha Green Tea PET bottle, cylindrical with vertical paneling, green shrink-sleeve label" | ~3 min |
| 3 | Keyboard | "Full-size ANSI 104-key mechanical keyboard, black matte, floating keycap, per-key RGB backlighting" | ~5 min |
| 4 | Headphones | "Over-ear closed-back headphones, dark gray/black plastics, faux-leather cushions, metallic accents" | ~5 min |
| 5 | Envelope | "Standard #10 business envelope, off-white matte paper, fiber texture, closed flap" | ~5 min |

**Total asset generation time:** ~20 minutes (out of 56 total)

**Error:** Round 2 logged `"Error adding downloaded assets: list index out of range"` but the bottle GLB was still downloaded successfully. Round 6 re-fetched it.

---

## 3. Render Results

### Round 3 — First Successful Render (All Objects)
![Round 3](../output/static_scene/20260208_224146/greentea/renders/3/Camera.png)

**Observations:** All 5 Meshy-generated objects visible. The green tea bottle is translucent green with correct PET bottle shape. Keyboard shows individual keys with RGB backlighting — a massive improvement over the SAM3D flat panel. Headphones have proper over-ear form with coiled cable. Envelope is a white geometric shape floating above the bottle (placement error). Table surface is white/light gray with rounded edges. Objects imported at normalized scale, arranged on tabletop.

### Round 4 — Table Scaled Up
![Round 4](../output/static_scene/20260208_224146/greentea/renders/4/Camera.png)

**Observations:** Table scaled 1.8x and now dominates the frame as a proper desk. Bottle visible (small) at back-left. Headphones barely visible at right edge. Keyboard and envelope lost from frame — camera too high/far. The table itself looks excellent: proper desk shape with legs, light wood texture.

### Round 5 — Best Composition
![Round 5](../output/static_scene/20260208_224146/greentea/renders/5/Camera.png)

**Observations:** Best overall render of the run. Table with four legs clearly visible as a proper desk. Bottle on the table surface (correct green color), keyboard with colorful RGB keys beside it. Headphones hanging off the right edge (partially visible). Envelope not visible in this framing. Clean, well-lit scene with good camera angle.

### Round 6 — Regression (Only Bottle)
![Round 6](../output/static_scene/20260208_224146/greentea/renders/6/Camera.png)

**Observations:** Camera moved to show only bottle at the table edge with one leg visible. Most objects lost from frame. Typical VIGA oscillation where the Verifier's corrections overshoot.

### Round 7 — Extreme Close-Up (Blurry)
![Round 7](../output/static_scene/20260208_224146/greentea/renders/7/Camera.png)

**Observations:** Extremely close camera angle with strong DoF blur. Only white table surface visible. Non-useful render — camera too close.

### Round 8 — Final Scene (Portrait with DoF)
![Round 8](../output/static_scene/20260208_224146/greentea/renders/8/Camera.png)

**Observations:** Final composition. Portrait orientation (768x1024), 30mm lens with DoF focused on the green tea bottle. Bottle is the hero element — clearly recognizable as a green PET bottle with cap. Keyboard visible behind it with dark keycaps and RGB glow. Artistic, cinematic framing. Only 2 of 5 objects visible, but the two that are shown look excellent. Warm key light, cool fill light (color-tinted 3-point lighting).

---

## 4. 360° Rotation GIFs

| Round | GIF |
|-------|-----|
| Round 3 | ![Round 3 Rotation](../output/static_scene/20260208_224146/greentea/rotation_gif/round_3.gif) |
| Round 5 | ![Round 5 Rotation](../output/static_scene/20260208_224146/greentea/rotation_gif/round_5.gif) |
| Round 8 (Final) | ![Round 8 Rotation](../output/static_scene/20260208_224146/greentea/rotation_gif/round_8.gif) |

---

## 5. Meshy vs SAM3D Asset Quality Comparison

| Object | SAM3D (Runs 7-8) | Meshy API (Run 9) |
|--------|------------------|-------------------|
| **Table** | Low-poly L-shaped bracket, no legs, used as proxy | Proper 4-legged desk with wood texture, correct proportions |
| **Green Tea Bottle** | Blobby green cylinder, no label, no cap detail | Translucent green PET bottle with cap, paneling, correct shape |
| **Keyboard** | Flat gray/green rectangle with no keys | Full keyboard with individual keycaps and RGB backlighting |
| **Headphones** | Teal/turquoise ring shape, unrecognizable | Over-ear headphones with band, earcups, and coiled cable |
| **Envelope** | Flat white rectangle (acceptable) | White geometric envelope with fiber texture (comparable) |
| **Overall** | Low-quality point cloud reconstructions | **Significantly better** — recognizable objects with PBR textures |

### Key Quality Improvements with Meshy:
1. **Bottle**: Went from a blobby cylinder to an actual PET bottle shape — the single most recognizable improvement
2. **Keyboard**: From a flat panel to individual keycaps with RGB — unrecognizable vs recognizable
3. **Table**: From an L-bracket to a proper desk — fundamental improvement for scene composition
4. **Headphones**: From a teal ring to actual over-ear headphones with cable — massive improvement
5. **Envelope**: Comparable quality (both are simple flat geometry)

---

## 6. Comparison: Run 7 (SAM3D) vs Run 9 (Meshy)

| Aspect | Run 7 (SAM3D) | Run 9 (Meshy API) |
|--------|---------------|-------------------|
| Asset source | SAM3D point cloud reconstruction | Meshy text-to-3D generation |
| Asset generation time | Pre-computed (offline) | ~20 min via API |
| Duration | 42 min (2508s) | 56 min (3364s) |
| Scripts | 9 | 8 |
| Renders with Camera.png | 8 | 6 (rounds 3-8) |
| Object recognizability | Low — blobby shapes | **High — correct geometry and textures** |
| Best render | Round 9 (tabletop with 5 objects) | Round 5 (desk with 3 objects) |
| Final render style | Tabletop close-up, 32mm | Portrait DoF hero shot, 30mm |
| Objects in final render | 5 (all visible) | 2 (bottle + keyboard) |
| Scene composition quality | Better spatial arrangement | More artistic/cinematic framing |

### Analysis

1. **Meshy API produces dramatically better 3D models.** Every object except the envelope is vastly improved. The green tea bottle, keyboard, and headphones are now recognizable as their real-world counterparts, whereas the SAM3D versions were abstract shapes.

2. **Scene composition had more volatility.** Run 9 oscillated more between rounds (scaling the table 1.8x caused objects to shrink relative to it, then the camera kept losing objects). Run 7 had a more stable progression.

3. **Artistic quality vs completeness trade-off.** Run 9's final render (Round 8) is more cinematic — portrait DoF with bottle as hero — but only shows 2 objects. Run 7's final render shows all 5 objects but with lower-quality assets. For a "product photo" aesthetic, Run 9 wins; for "show all objects on a desk," Run 7 wins.

4. **The VIGA feedback loop worked well with Meshy assets.** GPT-5 wrote increasingly sophisticated scripts: from basic import-and-place (Round 3) to scale adjustments, rotation, table-clamping, color-tinted lighting, DoF, and portrait framing (Round 8). The Verifier gave actionable feedback about scale ratios and camera positioning.

5. **Meshy API generation added ~20 minutes** to the total run time (each asset takes 3-5 min for preview + refine + download). This is a reasonable cost for the quality improvement.

---

## 7. Recommendations

1. **Use Meshy API for production runs.** The asset quality improvement is substantial and worth the extra generation time.
2. **Reduce camera volatility.** The Verifier should penalize losing objects more aggressively to prevent the oscillation seen in Rounds 6-7.
3. **Combine best of both approaches.** A wider initial view (like Run 5) followed by a tighter hero shot (like Run 8) would showcase both the scene layout and individual asset quality.
4. **Consider caching Meshy assets.** Once generated, Meshy GLBs should be reused across runs (current architecture already supports this via the fuzzy matcher).

---

## 8. File Listing

```
output/static_scene/20260208_224146/greentea/    # Run 9 (Meshy API assets)
├── scripts/ (1-8.py)
├── renders/ (1-8, Camera.png in 3-8)
└── rotation_gif/ (round_3, round_5, round_8 GIFs)

data/static_scene/greentea/
├── assets/                      # Current: Meshy-generated GLBs
│   ├── table.glb
│   ├── ito en bottle.glb
│   ├── keyboard.glb
│   ├── headphones.glb
│   └── envelope.glb
│
└── assets_sam3d_backup/         # Backup: SAM3D reconstructions
    ├── table.glb
    ├── ito_en_bottle.glb
    ├── alienware_keyboard.glb
    ├── headphones.glb
    └── envelope.glb
```

---

*Generated by VIGA (Vision-as-Inverse-Graphics Agent) with GPT-5 Generator + Verifier*
*Analysis by Claude Opus 4.6*
