# 公开方案研究与融合取舍

核查日期：2026-11-13。下面是公开工作流的设计参考；本包的自动化脚本为本项目编写，没有复制或随包安装第三方脚本。外部 skill 的提示词只作为研究材料，不覆盖用户授权与本项目规则。

| 来源 | 采用的思路 | 项目适配 |
|---|---|---|
| [blender-LPM-skill](https://github.com/ozanzeng/blender-LPM-skill) | 从部件、尺度和预算出发，渲染后检查 | 保留咱们的材质分区与选择性分面；不套用它的 Unity 导出轴向和 MaskMap |
| [blender-game-skills](https://github.com/majidmanzarpour/blender-game-skills) | 概念图到模型分阶段验证，导出清单与重新导入 | 对单图未知背面保留推断记录；按任务需要验证，不强制每阶段向用户索要批准 |
| [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) | 让助手操作 Blender 并查看结果 | 作为可选执行通道；当前默认使用已验证的后台 Blender，不强制安装 MCP |
| [Send to Unreal](https://epicgames.github.io/BlenderTools/send2ue/) | 将确定的导出范围与引擎传输结合 | 可选替代导入通道；默认可搬运的 FBX 包和 UE Python 导入器 |
| [Meshy 图生 3D 文档](https://docs.meshy.ai/en/api/image-to-3d) | 单件图进入异步模型生成任务，再取回真实网格 | 只在实际服务可用时接入；不固化会退役的模型名，不自动开户或消费 |
| [Epic FBX 管线](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine) | 枢轴、三角化、UV、自定义碰撞及材质交接 | 一个部件一个 FBX，材质参数另存，引擎端检查 |

前三个 GitHub 项目核查时均标注 MIT；本次只融合流程思想，没有纳入其代码。可追溯版本：

- `ozanzeng/blender-LPM-skill`：`687d0a46f1280bc7d11dbf83539840100ec909dc`
- `majidmanzarpour/blender-game-skills`：`f0ef29385a03de139957e6f700b801cdc00b7e29`
- `ahujasid/mcp-for-blender`：`8f40787fbde8e6d8fe51c5a3553e5635fff40d2b`

## 实际选择

1. 风格由本项目原图、规则和样板控制，工具路线可以替换。
2. 图片风格化、真实建模、低模整理、UE 验证是不同阶段，记录各自状态。
3. 可自动重复的工作写脚本，造型与材质意义由助手结合图片判断。
4. 默认可运行范围是常量材质的封闭静态组件；纹理资产、角色变形和复杂碰撞进入专门处理分支。
5. 不承诺任意图片都能无人工修正地变成游戏成品。外部生成服务能力、收费和模型名按使用时的官方信息核实。
