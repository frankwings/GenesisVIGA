# VIGA DynamicScene Windows 运行经验与修改记录

**日期:** 2026-02-06
**环境:** Windows 11 + Blender 4.5 + Miniconda (agent env) + GPT-5
**任务:** `runners/dynamic_scene.py --task=artist` — 从零重建 Cezanne 静物画为 3D Blender 场景

---

## 目录

1. [环境配置](#1-环境配置)
2. [运行命令](#2-运行命令)
3. [遇到的问题与修复](#3-遇到的问题与修复)
   - [3.1 路径解析错误 — 渲染输出到错误盘符](#31-路径解析错误--渲染输出到错误盘符)
   - [3.2 Windows 路径空格导致命令解析失败](#32-windows-路径空格导致命令解析失败)
   - [3.3 管道死锁 — subprocess 卡住](#33-管道死锁--subprocess-卡住)
   - [3.4 编码错误 — cp1252 无法编码 Unicode 字符](#34-编码错误--cp1252-无法编码-unicode-字符)
4. [修改文件汇总](#4-修改文件汇总)
5. [运行结果](#5-运行结果)
6. [渲染旋转 GIF](#6-渲染旋转-gif)
7. [经验总结](#7-经验总结)

---

## 1. 环境配置

| 项目 | 路径/值 |
|------|---------|
| Blender | `blender` |
| Python | `python` |
| 项目根目录 | `GenesisVIGA` (project root) |
| 模型 | GPT-5 (通过 OpenAI API) |
| EEVEE 引擎 | `BLENDER_EEVEE_NEXT` (Blender 4.x) |

## 2. 运行命令

```bash
"python" runners/dynamic_scene.py --task=artist --model=gpt-5 --blender-command="blender"
```

**注意:** 在 bash/terminal 中使用正斜杠 (`/`) 路径，不要用反斜杠。

## 3. 遇到的问题与修复

### 3.1 路径解析错误 — 渲染输出到错误盘符

**现象:** Blender 渲染的图片保存到了 `C:\output\...` 而不是 `<project root>\output\...`

**原因:** Blender 在 `--background` 模式下，`scene.render.filepath` 如果是相对路径，会相对于 Blender 自身的工作目录解析（即 `<blender install dir>`），而不是 Python 脚本的工作目录。

**修复:** 在 `exec.py` 和 `investigator_core.py` 的 `__init__` 中，对所有 `Path` 对象调用 `.resolve()` 转为绝对路径：

**`tools/blender/exec.py` — Executor.__init__:**
```python
# 修改前
self.blender_file = blender_file
self.blender_script = blender_script
self.script_path = Path(script_save)
self.render_path = Path(render_save)
self.blender_save = blender_save

# 修改后
self.blender_file = str(Path(blender_file).resolve())
self.blender_script = str(Path(blender_script).resolve())
self.script_path = Path(script_save).resolve()
self.render_path = Path(render_save).resolve()
self.blender_save = str(Path(blender_save).resolve()) if blender_save else blender_save
```

**`tools/blender/investigator_core.py` — Executor.__init__:**
```python
# 同样的修改
self.blender_file = str(Path(blender_file).resolve())
self.blender_script = str(Path(blender_script).resolve())
self.script_path = Path(script_save).resolve()
self.render_path = Path(render_save).resolve()
self.blender_save = str(Path(blender_save).resolve()) if blender_save else blender_save
```

**`tools/blender/investigator_core.py` — Investigator3D.__init__:**
```python
# 修改前
self.base = save_dir

# 修改后
self.base = Path(save_dir).resolve()
```

同时在 `exec.py` 的 `_execute_blender` 方法中也要 resolve 传入的参数：
```python
script_path = str(Path(script_path).resolve())
if render_path:
    render_path = str(Path(render_path).resolve())
```

---

### 3.2 Windows 路径空格导致命令解析失败

**现象:** 错误信息 `'C:/Program' is not recognized as an internal or external command`

**原因:** `investigator_core.py` 使用 `" ".join(cmd)` 构建命令字符串，但 Blender 路径包含空格 (`C:\Program Files\...`)，没有加引号。

**修复:** 根据平台条件添加引号处理：

**`tools/blender/investigator_core.py` — Executor._execute_blender:**
```python
# 修改前
cmd_str = ' '.join(cmd)

# 修改后
import sys as _sys
if _sys.platform == "win32":
    cmd_str = ' '.join(f'"{c}"' if ' ' in c else c for c in cmd)
else:
    cmd_str = ' '.join(cmd)
```

**`tools/blender/exec.py` — Executor._execute_blender:**
```python
# 修改前（使用 list 传参给 subprocess.run）
proc = subprocess.run(cmd, check=True, ...)

# 修改后
if sys.platform == "win32":
    cmd_str = ' '.join(f'"{c}"' if ' ' in c else c for c in cmd)
    proc = subprocess.run(cmd_str, shell=True, check=True, ...)
else:
    proc = subprocess.run(cmd, check=True, ...)
```

---

### 3.3 管道死锁 — subprocess 卡住

**现象:** `subprocess.run(..., capture_output=True)` 导致进程无限挂起，不返回

**原因:** Windows 下 `capture_output=True`（即 `stdout=PIPE, stderr=PIPE`）当输出量大时会导致管道缓冲区满，子进程写入阻塞，父进程等待子进程结束，形成死锁。Blender 在 background 模式下产生大量日志输出。

**修复:** 改用临时文件捕获输出：

**`tools/blender/investigator_core.py` — Executor._execute_blender:**
```python
# 修改前
proc = subprocess.run(cmd_str, shell=True, check=True,
                       capture_output=True, text=True, env=env, timeout=300)
out = proc.stdout
err = proc.stderr

# 修改后
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='_stdout.txt', delete=False, encoding='utf-8') as f_out, \
     tempfile.NamedTemporaryFile(mode='w', suffix='_stderr.txt', delete=False, encoding='utf-8') as f_err:
    stdout_file, stderr_file = f_out.name, f_err.name
with open(stdout_file, 'w', encoding='utf-8') as f_out, open(stderr_file, 'w', encoding='utf-8') as f_err:
    proc = subprocess.run(cmd_str, shell=True, check=True,
                          stdin=subprocess.DEVNULL, stdout=f_out, stderr=f_err,
                          env=env, timeout=300)
with open(stdout_file, 'r', encoding='utf-8', errors='replace') as f:
    out = f.read()
with open(stderr_file, 'r', encoding='utf-8', errors='replace') as f:
    err = f.read()
os.unlink(stdout_file)
os.unlink(stderr_file)
```

**`tools/blender/exec.py`** 也做了同样的修改。

---

### 3.4 编码错误 — cp1252 无法编码 Unicode 字符

**现象:** `UnicodeEncodeError: 'charmap' codec can't encode character '\u2011' in position 1234: character maps to <undefined>`

**原因:** Windows 默认编码是 `cp1252`，GPT 生成的响应中包含 Unicode 字符（如 `\u2011` 非断行连字符、中文字符等），写入文件时 Python 的 `open()` 默认用系统编码，无法处理这些字符。

**修复:** 在所有 `open()` 写文件的地方添加 `encoding="utf-8"`：

**`agents/generator.py` — GeneratorAgent._save_memory (第245行):**
```python
# 修改前
with open(output_file, "w") as f:
    json.dump(self.memory, f, indent=4)

# 修改后
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(self.memory, f, indent=4, ensure_ascii=False)
```

**`agents/verifier.py` — VerifierAgent._save_memory (第211行):**
```python
# 修改前
with open(output_file, "w") as f:
    json.dump(self.saved_memory, f, indent=4)

# 修改后
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(self.saved_memory, f, indent=4, ensure_ascii=False)
```

**`utils/common.py` — save_thought_process (第203行):**
```python
# 修改前
with open(filename, "w") as f:
    json.dump(memory, f, indent=4)

# 修改后
with open(filename, "w", encoding="utf-8") as f:
    json.dump(memory, f, indent=4, ensure_ascii=False)
```

**`tools/blender/exec.py` — Executor.execute (第233行):**
```python
with open(code_file, "w", encoding="utf-8") as f:
    f.write(code)
```

**`tools/blender/investigator_core.py` — Executor.execute (第178行):**
```python
with open(code_file, "w", encoding="utf-8") as f:
    f.write(full_code)
```

---

## 4. 修改文件汇总

| 文件 | 修改内容 |
|------|----------|
| `tools/blender/exec.py` | Path.resolve()、Windows 引号处理、临时文件替代管道、UTF-8 编码 |
| `tools/blender/investigator_core.py` | Path.resolve()、Windows 引号处理、临时文件替代管道、UTF-8 编码 |
| `agents/generator.py` | `_save_memory` 添加 `encoding="utf-8"` 和 `ensure_ascii=False` |
| `agents/verifier.py` | `_save_memory` 添加 `encoding="utf-8"` 和 `ensure_ascii=False` |
| `utils/common.py` | `save_thought_process` 添加 `encoding="utf-8"` 和 `ensure_ascii=False` |

## 5. 运行结果

- **总轮次:** 13 轮（Round 0-12）
- **成功渲染:** 12 轮（Round 1 Blender 执行失败，Round 2-12 正常）
- **总耗时:** 约 80 分钟
- **输出目录:** `output/dynamic_scene/20260206_011742/artist/`

目录结构：
```
output/dynamic_scene/20260206_011742/artist/
├── renders/
│   ├── 1/         # state.blend only (渲染失败)
│   ├── 2/         # state.blend + Camera_f0001.png, Camera_f0090.png, Camera_f0180.png
│   ├── 3/         # state.blend only (无 keyframe 渲染)
│   ├── 4/         # state.blend only
│   ├── 5-12/      # state.blend + 3个关键帧 PNG
│   └── ...
├── scripts/        # 每轮生成的 Blender Python 脚本
├── gifs/           # 旋转 GIF（后期生成）
├── generator_memory.json
├── verifier_memory.json
└── RESULTS.md
```

## 6. 渲染旋转 GIF

为了可视化每一轮的 3D 场景，创建了 `render_rounds_gif.py` 脚本：

- 打开每轮的 `state.blend` 文件
- **第一帧 (frame_000):** 从原始相机位置渲染（GPT 设定的视角）
- **后续帧 (frame_001~036):** 用 Blender EEVEE 引擎渲染 36 帧旋转视角（每帧 10°）
- 使用 PIL 生成 GIF 动画（384x384, 100ms/帧，共 37 帧）
- 生成 `RESULTS.md` 汇总文档

### 旋转相机锚点 — Ray-casting 方案

GPT 生成的 Blender 场景尺度不可控，基于包围盒的方法不可靠。最终采用 **ray-casting** 确定旋转锚点：

1. **从相机发射射线网格:** 以相机位置为起点，沿相机前方 ±20° 范围内发射 9×9 = 81 条射线
2. **收集命中深度:** 每条射线通过 `scene.ray_cast()` 检测与场景的交点，记录深度 `(hit_location - cam_pos).length`
3. **取 median 深度 D:** 用 `statistics.median()` 取中位数，过滤极端值（近处小物体、远处背景墙）
4. **计算锚点:** `anchor = cam_pos + cam_forward * D`，即相机中心射线方向、深度为 D 的点
5. **围绕锚点旋转:** 以 `radius = D`（clamp 到 1.0~30.0）为轨道半径，相机在球面上做 360° 旋转

```python
# 射线网格
for h_deg in [0, -10, 10, -20, 20, -5, 5, -15, 15]:
    for v_deg in [0, -10, 10, -20, 20, -5, 5, -15, 15]:
        ray_dir = (cam_forward + tan(h_rad)*cam_right + tan(v_rad)*cam_up).normalized()
        result, location, _, _, obj, _ = scene.ray_cast(depsgraph, cam_pos, ray_dir)
        if result:
            hit_depths.append((location - cam_pos).length)

anchor = cam_pos + cam_forward * median(hit_depths)
```

**实际效果:** 81 条射线中 75~81 条命中，median 深度稳定在 8.7~9.4 单位范围，无需硬上限修正。

### 旋转相机定位的迭代历程

1. **包围盒方法:** 基于所有 mesh 对象包围盒计算中心和半径 → 地板/墙壁达数百单位，相机太远（灰色画面）
2. **名称过滤 + 平面检测:** 过滤 floor/wall/plane 等名称 + 最小维度 < 0.01 的平面物体 → GPT 命名不标准，效果差
3. **硬上限:** `radius = min(radius, 15.0)` → 可用但不够精确
4. **Ray-casting（最终方案）:** 从相机视角出发，直接测量场景深度 → 自然得到合理的轨道半径，无需任何启发式过滤

## 7. 经验总结

### Windows 兼容性要点

1. **始终使用绝对路径:** Blender background 模式下相对路径基于 Blender 安装目录，必须用 `Path.resolve()` 转绝对路径
2. **路径空格处理:** Windows 下程序路径常含空格（`Program Files`），构建 shell 命令时必须加引号
3. **避免管道捕获:** Windows 下 `capture_output=True` 对大输出有死锁风险，改用临时文件
4. **指定 UTF-8 编码:** Windows 默认编码 `cp1252` 无法处理 Unicode，所有 `open()` 都要加 `encoding="utf-8"`
5. **使用正斜杠:** 在命令行和 shell 命令中优先使用 `/` 而不是 `\`

### Blender 相关

- EEVEE 引擎在 Blender 4.x 中的名称是 `BLENDER_EEVEE_NEXT`
- 设置 `AL_LIB_LOGLEVEL=0` 可以屏蔽 OpenAL 音频库的报错
- 添加 `stdin=subprocess.DEVNULL` 防止 Blender 等待标准输入

### GPT 生成场景的特点

- 对象命名不标准，不能依赖名称进行分类
- 场景尺度变化极大（从几个单位到数百单位）
- 地板/墙壁对象可能非常大，影响包围盒计算
- 确定旋转锚点最可靠的方法是 **ray-casting**：从相机发射射线取 median 深度，而非依赖包围盒或名称过滤

---

*记录于 2026-02-06，GenesisVIGA 项目*
