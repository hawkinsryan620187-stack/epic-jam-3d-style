# 本地自动处理：静态网格

需要 Python 3 与 Blender；脚本使用 Blender 自带 `bpy`，无需 pip 安装建模依赖。v0.2.0 实测环境为 Blender 4.5.0 Apple Silicon。Windows/Linux 使用对应 Blender 可执行文件；其他版本需验证 API 与导出结果。

## 一条命令

复制 [静态道具模板](../templates/static-prop.json)，填好路径与名称后执行：

```bash
python scripts/run_pipeline.py --job /absolute/path/job.json --blender /path/to/blender
```

Windows 示例：

```powershell
python scripts/run_pipeline.py --job "D:\Assets\job.json" --blender "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
```

`--blender` 可省略，届时依次查 `BLENDER_BIN`、PATH、macOS 默认路径。JSON 中的相对输入/输出路径以 JSON 文件所在目录为基准。输出目录必须为空或不存在，原模型不会改写。

## 参数含义

| 字段 | 用法 |
|---|---|
| `input` | 实际 `.blend/.glb/.gltf/.fbx/.obj` 文件；图片先走建模阶段 |
| `output` | 新的版本目录 |
| `asset_name` | 英文数字下划线，字母开头，用于 UE 命名 |
| `style_mode` | `project`：项目色板和大面着色；`preserve`：保留可支持的常量材质与着色 |
| `triangle_budget` | 整个资产的上限，超限报错；模板值是示例，不是官方预算 |
| `decimate_ratio` | 0 到 1，默认 1；用户/助手明确选择后才减面，随后看实际轮廓 |
| `meters_per_unit` | 可选；未填时 BLEND 用场景单位，其他输入按正常导入的米制网格处理。尺寸异常需明确纠正 |
| `material_map` | 源材质名 → 项目角色名；看预览和材质信息后填写 |
| `collision` | `none` 默认；`box` 为粗略包围盒，仅用于允许覆盖整个外包围体的实体摆件 |
| `parts` | 可选；部件名和源层级根节点，详见下文 |
| `render` | 默认 true，输出实际模型的正、右、背及三分之四视角，原生 1920×1080 |

色板角色：`warm_stone`、`gray_stone`、`wood`、`terracotta`、`indigo`、`ochre`、`ivory`、`brass`、`olive`、`yellow_green`、`dark`、`screen`。数值来自项目色板；dark/screen 用于功能部位。

未映射的简单材质会按原颜色匹配接近的项目色，金属优先匹配黄铜。这是候选映射，需要视觉复核。需要保留某个金属颜色时选 `preserve` 或完善材料方案，不把所有金属硬改金色。

## 材质和拓扑边界

本自动整理器服务于**封闭组件 + 常量 PBR** 的低模路线。含纹理、透明、复杂节点的材质要求先烘焙并走独立材质流程，或在 `material_map` 中明确同意简化成指定常量材质。不会悄悄丢弃贴图细节。平面叶片、开放衣服等合法开放网格应走专门分支，当前脚本会拒绝非封闭组件。

它会重建每个导出部件的 UV0（适用于这里的常量材质），保留源文件。需要沿用纹理 UV 的资产不要用此整理器。它不会自动生成 lightmap UV；UE 导入脚本请求引擎生成，结果仍需检查。

包围盒碰撞可能堵住门洞、遮住灯罩开口或覆盖空隙。此类物体使用 `none`，随后按功能制作多凸包碰撞；不要为了让检查通过而给所有物体套同一种碰撞。

## 活动部件

使用 [台灯模板](../templates/articulated-prop.json)。每个 `root` 必须是源模型实际存在的网格或父级节点。嵌套层级采用最近的已声明根节点归属，所有渲染网格都必须属于一个部件。

每个部件导出为以该节点为局部原点的独立 FBX/GLB；一个 FBX 只包含一个渲染网格及其碰撞。整体另存 `master.blend` 与 `assembly.glb`，保存组合位置与父子层级；`asset-manifest.json` 保存米制 Blender 空间的枢轴矩阵。UE 中的运动装配需要 Blueprint/组件层级，导入脚本不会凭空建立交互逻辑。

## 输出

- `master.blend`、`assembly.glb`：整理后的完整资产与层级。
- `SM_<资产>_<部件>.fbx/.glb`：每件网格单独导出。
- `front/right/back/hero_1920x1080.png`：同一真实模型的视图；三张正交视图使用同一缩放。
- `asset-manifest.json`：面数、尺寸、材质参数、部件矩阵、导出回读结果。
- `ue_import.py`：可复制到 UE 端执行的导入器。
- `pipeline.log`、`resolved-job.json`：本次执行记录；后者含本机绝对路径，分享公开包时移除或脱敏。

成功导出只会标记 `export_roundtrip=passed`，视觉与 UE 检查保留未验证状态。失败目录保留用于排错；修改后使用新版本目录，不把残留导出文件单独当作成功产物。
