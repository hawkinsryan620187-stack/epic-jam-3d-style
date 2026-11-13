# 提示词模板与类别配方

以下文本是生成约束，具体服务可能不能逐条实现。模型结果仍按 [交付要求](asset-handoff.md) 检查。图片工具只产生参考图；可导入的模型必须另有实际网格文件。

## 共用风格段

中文含义：低多边形幻想游戏资产，清楚的几何切面、稳重的大形体、适量切角，靠剪影与功能结构识别。低饱和材质本色，表面细节稀疏；石木布哑光，少量金属保留反射。材质颜色不含固定的光照与投影。

英文共用段：

```text
Stylized low-poly fantasy game asset matching the supplied project style reference. Clear silhouette, substantial primary volumes, broad readable planar facets, selective chamfered edges, restrained secondary shapes and sparse purposeful detail. Controlled faceted shading that follows the designed forms. Muted material-local colors with subtle low-frequency variation. Mostly matte stone, wood and cloth where applicable; rough metal response only on actual metal parts. Clean base color without baked directional illumination, cast shadows, specular highlights or ambient-occlusion stains. Consistent geometry and material detail at gameplay viewing distance.
```

如果工具没有接收到参考图片，把第一句中的 `matching the supplied project style reference` 去掉；后面的文字约束仍保留。不把“low-poly”理解成所有三角形都用不同颜色，也不把“game asset”当成质量验收证明。

## 组合方式

```text
[One asset: name, function and essential silhouette.]
[Shared style block.]
[Category block from the table below.]
[Specific components, local colors and required moving/separate parts.]
[Output mode: 3D model, reference image, or consistent multiple views.]
```

在真实输出中用具体内容替换方括号，消除冲突后提供完整提示词。先遵循用户已有资产设计；新增细节以支持功能和风格为限。没有参考依据的背面与内部结构写入资产备注。

## 类别段：选择相关行

| 类别 | 英文类别约束 |
|---|---|
| 角色 | `Stylized adult proportions with a small simplified head, readable limbs and a strong coat or cape silhouette. Broad garment folds, simple facial features and grouped hair masses. Clear elbow, knee and hip articulation. Avoid infant-like chibi proportions and realistic skin or fabric microdetail.` |
| 墙柱、门窗 | `Thick modular masonry, substantial squared pillars, broad chamfers and a few large structural divisions. Readable wall thickness and openings. Keep module interfaces straight and consistent; sparse brackets only where structurally useful.` |
| 地板、台阶 | `Large stone slabs, shallow readable seams, broad step treads and restrained edge wear. Coherent slab thickness, stable proportions and few large color variations. Keep walking surfaces clean and level where required.` |
| 家具 | `Thick wooden boards, sturdy supports, simple construction and restrained edge chamfers. A small number of large components, minimal wood grain and sparse functional fittings.` |
| 箱柜 | `A clear lid-or-door silhouette, thick panels and a few broad reinforcing straps. Keep moving lids or doors distinct from the body and preserve plausible hinge placement. One simple latch or handle as the focal detail.` |
| 陶器、遗物 | `A recognizable silhouette built from a small number of polygonal volumes. A faceted cross-section, substantial rim or edge thickness and one primary identifying feature. Sparse ornament, no fine engraved clutter.` |
| 器械、灯具 | `A simplified functional mechanism with robust arms, a readable base and a small number of large joints. Enlarge essential handles and hinges enough to remain readable. Avoid cables and tiny mechanical greebles unless required.` |
| 树木 | `An irregular broad canopy made from a few large faceted foliage masses, supported by a tapered polygonal trunk with simple branching. Muted olive and yellow-green foliage variation, subdued brown trunk, no individual leaf detail.` |
| 草花 | `A compact cluster of a few broad angular grass blades with sparse simplified flower heads. Clear grouped silhouette, restrained olive greens and small warm-white flower accents. No dense realistic grass fibers.` |
| 岩石、地形 | `An irregular solid mass with a few broad angular planes and restrained chipped corners. Muted gray-violet or gray-brown stone colors, subtle face variation, no granular noise or dense fractures. Keep the top surface and side masses readable.` |
| 布旗、软装 | `A clear cloth silhouette with a few broad fold planes, a restrained hem and a simple attachment structure. One dominant muted cloth color and, only if requested, a single broad geometric emblem. No fine weave texture.` |

如角色没有长外套或道具没有金属，删除不适用部分，不为了套模板添加部件。角色头身、面数、尺寸、材质槽和贴图分辨率按任务填写；缺少制作预算时不编造“官方统一上限”。

## 输出模式段

### 直接生成 3D

```text
Create one complete standalone 3D asset with coherent geometry on all sides and a finished underside where visible. Preserve intended openings and separate moving components where specified. Assign clear material regions with relightable base colors. Do not add a presentation pedestal, ground plane or surrounding scene. Export the actual mesh and supported material data in the requested format.
```

“完整”允许合理的多网格组件；不要为了水密而封死杯口、窗洞或服装开口。实际导出格式和可用功能由目标服务决定。关节拓扑、枢轴、分件、绑定和纹理状态需独立检查。

### 单件建模参考图

```text
Show one complete isolated asset, centered and fully visible with comfortable margins, in a clear three-quarter view on a plain neutral background. Neutral white illumination with soft, minimal shadows, readable form and accurate local colors. No dramatic perspective, scenery, text, watermark, decorative pedestal or cinematic effects.
```

要保留透明背景时使用工具真实的透明输出选项；仅写“transparent”不保证 alpha 通道。对图生 3D 服务，优先用单件清楚视图；仅在服务明确支持多视图时输入多张对应视图，不把拼图当作默认的单图输入。

### 正侧背建模参考

```text
Consistent orthographic front, side and back reference views of the same exact asset, at identical scale, aligned to the same ground line. Preserve silhouette, dimensions, component count, materials and attachments across all views. Plain neutral background, even white illumination, minimal shadows. No perspective distortion or decorative environment.
```

动画角色姿势使用制作组指定的 A/T pose；未指定时可先给 A pose 参考并注明。多视图生成后检查对应关系，无法确认的结构不宣称一致。

## 共用排除项

用于独立负向栏，或转换成普通语言限制：

```text
photorealism, scanned surface detail, skin pores, dense scratches, fine wood grain, realistic fabric weave, tiny decorative clutter, random noisy triangulation, excessively rounded toy shapes, glossy plastic, exaggerated chibi anatomy, busy ornamental engravings, heavy grunge, baked sunlight, baked cast shadows, painted specular highlights, heavy baked AO, dramatic rim lighting, bloom, depth of field, text, watermark, surrounding scenery, presentation pedestal
```

只保留相关项；若任务需要碑文或真实使用的底座，允许这些设计内容。针对参考图模式才使用光照/景深等摄影排除词，直接 3D 建模时优先强调几何、材质与分件。

## 可直接粘贴的示例

下面四条已经合并主体、风格、类别和输出模式。未附图片时删掉第一句对参考图的指代。角色默认比例和材质色彩均来自工作基线，不是既有角色定稿。

### A. 直接生成：可开合旧物箱

资产说明：灰褐木箱，宽旧黄铜包角，单锁扣。箱盖和箱体独立。后台若无法输出分件，成品标记“待拆件”。

```text
Create one standalone stylized low-poly wooden storage chest, matching the supplied project style reference. Use a clear substantial silhouette, broad planar facets, selective chamfered corners and sparse purposeful detail. Build a thick rectangular wooden body and a distinct solid lid, with two broad reinforcing straps and one simple front latch. Keep the lid separate from the body for opening, with a plausible hinge line along the rear edge. Use muted gray-brown wood and small areas of aged brass, minimal wood grain, mostly matte wood and rough metallic fittings. Base colors must remain relightable, free of baked sunlight, cast shadows, painted highlights and heavy AO. Complete the back and underside; preserve the opening seam. Avoid tiny rivet patterns, dense scratches, ornate carving, glossy plastic and random noisy triangulation. Deliver the actual 3D mesh and supported material data. Do not add a ground plane, display pedestal or scene.
```

### B. 生成参考图：长外套修复师

资产说明：成人体态，靛蓝长外套、米白领口、灰褐靴子，小面积黄铜腰饰；腰饰只作示例设计，可按角色设定替换。输出建模参考图。

```text
Create a 3D modeling reference image of one adult repair artisan in the stylized low-poly visual language of the supplied project reference. Use approximately six-and-a-half-head proportions as a working design, a small simplified head with understated facial features, readable limbs and a strong long-coat silhouette. Broad planar facets, selective angular edges, grouped hair masses and a few large cloth folds; clear elbows and knees. Use a muted indigo coat, warm off-white collar, subdued brown boots and a small aged-brass belt accessory. Materials have clean local colors and low surface detail, with matte cloth and restrained metal response. Show the entire character in a relaxed A pose from a clear three-quarter angle, with hands separated from the body, on a plain neutral background under even white illumination. Avoid chibi proportions, robot-like reinterpretation, skin pores, dense fabric weave, oversized ornaments, dramatic shadows, bloom, scenery, text and a display pedestal.
```

### C. 直接生成：低多边形树

资产说明：三组不规则主树冠，简化树干分叉，灰橄榄绿；树冠数量是本件设计，可按剪影调整。

```text
Create one standalone stylized low-poly tree matching the supplied project style reference. Build an irregular broad canopy from three large angular foliage masses with readable planar facets, supported by a tapered polygonal trunk and a few sturdy branches. Keep the silhouette clear, the main volumes substantial and secondary detail sparse. Use muted olive green with a little yellow-green variation on the foliage and subdued gray-brown on the trunk. Use clean matte local colors without baked directional shading, cast shadows or specular highlights. Finish the tree on all sides. Avoid individual leaves, fine bark texture, spherical lollipop foliage, dense tiny canopy clusters and random noisy triangles. Deliver the actual 3D mesh with clear trunk and foliage material regions. Do not add terrain, a planter, roots sprawling across a display base or surrounding scenery.
```

### D. 生成参考图：遗迹墙柱模块

资产说明：一个有壁厚的墙段与端柱，切角石面，少量结构性金属件；尺寸由关卡网格另定。

```text
Create a 3D modeling reference image of one modular ruin wall segment with one substantial end pillar, matching the supplied project style reference. Use thick masonry, large calm planar surfaces, broad selective chamfers, a simple pillar cap and few structural divisions. Keep the module connection surfaces straight and the wall thickness consistent. Use muted warm-beige wall stone, subdued gray-violet pillar stone and a few small aged-brass brackets only where structurally useful. Mostly matte surfaces, subtle low-frequency color variation, sparse wear and no dense cracks or carved ornament. Show the complete module in a clear three-quarter view on a plain neutral background under even white illumination, with the thickness, base and connection edge visible. Avoid dramatic perspective, baked-looking sunlight, purple environmental fog, plants, characters, text, extra architecture and a presentation pedestal.
```

## 给协作 AI 的任务示例

```text
使用 $epic-jam-3d-style。为一盏可交互的桌面台灯写 AI 建模提示词：
木底座，黄铜转轴，深灰灯罩，灯臂需要旋转。
输出中文资产说明、英文正向词、必要排除项，以及活动部件和枢轴备注。
```

```text
使用 $epic-jam-3d-style。根据我提供的箱子模型预览复核风格，
具体指出轮廓、切面、细节、材质和配色的偏差，并给一条修订提示词。
```
