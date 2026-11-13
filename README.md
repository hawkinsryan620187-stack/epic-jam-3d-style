# EPIC JAM · 低模风格到 UE 资产工作流

将文字、参考图或已有模型，沿项目统一的低多边形风格，推进到实际模型、三视图和 UE 导入包。

**[下载最新 Skill ZIP](https://github.com/hawkinsryan620187-stack/epic-jam-3d-style/releases/latest/download/epic-jam-3d-style.zip)** · [完整工作流](references/workflow.md) · [运行说明](references/running-pipeline.md) · [版本](https://github.com/hawkinsryan620187-stack/epic-jam-3d-style/releases)

![项目风格参考](assets/style-reference.png)

## 一句话调用

```text
使用 $epic-jam-3d-style，把这张参考图中的台灯转换为项目低多边形风格，
制作真实模型、正侧背三视图和 UE 导入包。灯臂需要独立旋转。
```

```text
使用 $epic-jam-3d-style，处理这个已有模型：
按项目色板统一材质，面数控制在 3000 三角面以内，保留主要轮廓，
导出 UE 用 FBX 和预览 GLB，并报告实际验证结果。
```

## 流程

```mermaid
flowchart LR
  A[文字 / 参考图] --> B[统一造型与配色]
  B --> C[实际建模工具]
  D[已有模型] --> E[模型检查与风格调整]
  C --> E
  E --> F[分件 / 材质 / UV / 三视图]
  F --> G[逐件 FBX / GLB / 回读检查]
  G --> H[UE 导入 / 材质接线 / 尺寸检查]
  H --> I[视觉与玩法验收]
```

## v0.2 能做什么

- 沿用项目风格基线、原始参考图、11 类配方和 4 条完整提示词。
- 用一条命令处理已有静态模型：项目色板映射、可选减面、分件、UV、实际网格三视图和导出。
- 按实际层级保留活动部件枢轴，逐件导出 FBX，避免把所有活动部件焊成一体。
- 可选粗略包围盒碰撞；检查封闭几何、面数预算，并重新导入 FBX/GLB 核对尺寸、面数与材质槽。
- 随模型生成 UE Python 导入脚本，按参数重建材质并检查厘米尺寸。

**实测范围**：本地脚本用电脑与台灯验证，详见 [验证记录](references/validation.md)。UE 导入脚本尚未在目标 UE 项目运行；图生 3D 需要已接通的建模服务，简单道具也可由助手用 Blender 配方制作。

“转换风格”包括造型判断与调整。整理脚本的平面着色、色板映射与减面不能替代语义造型设计。当前自动整理器适用于常量 PBR 材质的封闭静态组件；复杂纹理、透明材质、开放网格和角色绑定走专门分支。

## 安装

下载 ZIP，将完整 `epic-jam-3d-style` 文件夹放入：

- macOS / Linux：`~/.codex/skills/`
- Windows：`%USERPROFILE%\.codex\skills\`
- 设置了 `CODEX_HOME` 时：该目录下的 `skills/`。

重新打开聊天后使用 `$epic-jam-3d-style`。也可直接让助手读取 `SKILL.md`。已安装旧版时保留自己的修改，再用新版完整文件夹更新。

首次 Git 安装：

```bash
git clone https://github.com/hawkinsryan620187-stack/epic-jam-3d-style.git ~/.codex/skills/epic-jam-3d-style
```

## 本地一条命令

安装 Blender，填写 [任务模板](templates/static-prop.json) 后运行：

```bash
python scripts/run_pipeline.py --job /path/to/job.json --blender /path/to/blender
```

相对路径以任务 JSON 所在目录为基准。活动道具参考 [分件模板](templates/articulated-prop.json)。输出新版本文件夹，包含模型、四个视角、清单和 `ue_import.py`；UE 端用法见 [引擎交接](references/ue-handoff.md)。

## 文档

| 内容 | 链接 |
|---|---|
| 技能入口 | [SKILL.md](SKILL.md) |
| 造型、色板与材质 | [风格基线](references/style-baseline.md) |
| 生成提示词 | [配方](references/prompt-recipes.md) |
| 流程与工具选择 | [完整工作流](references/workflow.md) |
| 执行参数和能力范围 | [运行说明](references/running-pipeline.md) |
| UE 导入与实测要求 | [UE 交接](references/ue-handoff.md) |
| 研究的公开 skill 与管线 | [来源与取舍](references/research-sources.md) |
| 本版本实际验证 | [验证记录](references/validation.md) |

本包不包含第三方模型权重、Blender 安装包或服务密钥。首次风格基线中的色值与比例仍为工作建议，以制作组确认的样板优先。
