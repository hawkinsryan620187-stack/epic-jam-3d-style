# UE 导入和最后一段验证

## 已实现的导入器

在目标项目启用 Python Editor Script Plugin。把完整导出文件夹放到制作组机器，在 UE 菜单执行该文件夹内 `ue_import.py`；默认导入 `/Game/EPICJam/Generated/<资产名>`。需要自定义目标目录时，可在 UE Python 控制台运行：

```python
import runpy
module = runpy.run_path(r"D:\Assets\output_v01\ue_import.py", run_name="skill_module")
module["run"](r"D:\Assets\output_v01\asset-manifest.json", "/Game/EPICJam/GeneratedV02")
```

每次使用新目标目录；脚本拒绝覆盖现有目录。失败时生成报告并保留已导入部分，修正后换新目录或人工整理失败目录。

导入器通过 UE 的 FBX 工厂读取逐件网格，保留法线、请求生成 lightmap UV，按 JSON 中的线性 Base Color、Roughness、Metallic 创建并分配 UE 材质。检查导入网格数、材质槽对应关系和厘米尺寸，写 `ue-import-report.json`。

此脚本已做 Python 语法检查，当前交付环境没有可执行的目标 UE 项目，**尚未实测 UE API 调用**。若项目的 Interchange/FBX 工厂或 API 与脚本不同，以目标版本日志为准调整；不修改整个项目的导入器设置来掩盖问题。

## 必须在引擎内看的结果

1. 在真实关卡放入资产，用尺寸参照检查比例与正面方向。导入器按排序后的包围尺寸判断单位倍率，不能识别朝向错误。
2. 用统一中性灯光复核色板、分面法线、粗糙度与金属度。避免将原图光影烘到本色。
3. 转动活动部件，检查枢轴与装配位置；结合 manifest 的源空间矩阵建立组件层级，注意 UE 坐标转换。当前导入器只创建独立 Static Mesh，不创建装配 Blueprint。
4. 打开碰撞显示并做角色行走/射线/交互试验。包围盒适合简单实体，门洞和凹槽需分解碰撞。`none` 代表没有自定义碰撞，不代表碰撞验收通过。
5. 若使用烘焙静态光照，检查生成的 lightmap UV 和分辨率；再按当前玩法测试。

## 官方约束与本实现的取舍

- Epic 的 FBX 管线支持 UV、法线、材质槽及自定义碰撞；碰撞按 `UCX_<网格名>_00` 命名。多个网格及自定义碰撞放在同一个 FBX 有导入限制，所以本实现逐件导出。[Epic FBX 静态网格管线](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine)
- Epic 文档写明管线基于 FBX 2020.2；Blender 自带导出器不是因此自动变成 2020.2。本地 FBX 回读通过不代表所有 UE 版本兼容，仍需目标项目导入验证。[同一官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine)
- UE Python 用于编辑器资产处理，不是运行时玩法脚本。[Epic 编辑器 Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)

接通并验证过的 Send to Unreal 可以代替本导入步骤，继续保留同样的交付记录；它并不替代建模、材质转换和风格复核。
