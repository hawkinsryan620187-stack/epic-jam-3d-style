# EPIC JAM · 3D 美术风格 Skill

供本项目制作组使用的 3D 美术风格约束与 AI 建模提示词。以低多边形大切面、厚实形体、克制细节和低饱和固有色为基调；场景光照由下游在 UE 中调整。

![风格参考](assets/style-reference.png)

**[下载可安装 ZIP](https://github.com/hawkinsryan620187-stack/epic-jam-3d-style/releases/latest/download/epic-jam-3d-style.zip)** · [版本与下载](https://github.com/hawkinsryan620187-stack/epic-jam-3d-style/releases) · [Skill 主文件](SKILL.md)

## 安装到 Codex

下载并解压 ZIP，将里面完整的 `epic-jam-3d-style` 文件夹放入：

- macOS / Linux：`~/.codex/skills/`
- Windows：`%USERPROFILE%\.codex\skills\`
- 若设置了 `CODEX_HOME`：放入该目录下的 `skills/`。

保留 `assets`、`references` 和 `agents` 子目录。重新打开聊天，确认技能已被发现；也可以直接指定 `SKILL.md` 文件让助手读取。

使用 Git 也可以安装（目标目录不存在时）：

```bash
git clone https://github.com/hawkinsryan620187-stack/epic-jam-3d-style.git ~/.codex/skills/epic-jam-3d-style
```

## 使用示例

```text
使用 $epic-jam-3d-style，为一台复古电脑生成 AI 建模提示词。
包括厚实切角机身、独立键盘、低饱和配色，给出分件和材质要求。
```

```text
使用 $epic-jam-3d-style，制作一盏可调节桌灯的模型与正、侧、背三视图。
采用木底座、靛灰灯臂、黄铜转轴，保持几何切面清楚、装饰克制。
```

```text
使用 $epic-jam-3d-style，检查我提供的模型是否符合风格，
具体指出剪影、分面、细节密度、材质和配色需要修改的部位。
```

普通建模平台可直接复制 [提示词配方](references/prompt-recipes.md) 中的完整示例。支持参考图的工具可附 `assets/style-reference.png`，说明它用于风格参考；单件造型另外提供。

## 内容

| 文件 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 技能入口、共用约束和执行方式 |
| [风格基线](references/style-baseline.md) | 各类造型规则、工作色板及材质约定 |
| [提示词配方](references/prompt-recipes.md) | 11 类配方、4 条完整示例和输出模式 |
| [交付与复核](references/asset-handoff.md) | 分件、UV、实际模型检查与交付记录 |
| [参考图](assets/style-reference.png) | 1672×941 原始风格参考，未插值 |
| [界面配置](agents/openai.yaml) | Codex 技能名称与默认调用示例 |

本 Skill 提供风格约束与复核方法。实际生成图片或 3D 文件，需要使用环境中可用的对应工具；它本身不包含建模引擎、模型权重或 API 密钥。

当前版本为首版工作基线 v0.1，色值与比例属于工作建议，后续以制作组确认的样板为准。
