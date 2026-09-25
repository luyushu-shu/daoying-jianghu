# 刀影江湖

横版武侠 ARPG。买断制、无抽卡。引擎为 **团结引擎 1.10.2**（对应 Unity 2022.3.62t14）。

| 项 | 内容 |
|---|---|
| 类型 | 横版动作角色扮演 |
| 主角 | 青锋剑客 |
| 工程 | `New Tuanjie Project/` |
| 设计 | `设计/` |
| 仓库 | https://github.com/luyushu-shu/daoying-jianghu |

---

## 本次进展（青锋剑客动作系统：待机 / 行走 / 奔跑 / 闪避 / 跳跃 / 轻攻击三连斩 / 重刺 / 三段式格挡）

待机和奔跑来自六秒循环视频的去背帧：待机取 01–08，奔跑取能接回的 15–23。行走仍是用户提供的 15 帧。闪避动作共 8 帧大幅度极速残影瞬步。跳跃动作共 8 帧全新国风轻功凌空纵跃。重刺动作共 8 帧（源自概念图第 2 框：沉腰蓄势 → 剑意引弓 → 踏步蹬发 → 破空贯穿 → 剑芒爆鸣 → 弓步急刹 → 抽剑回撤 → 敛意归正），破防削盾，带 0.40 单位突进。轻攻击三连斩共 12 帧（平斩、挑刺、回旋力劈），由 `generate2dsprite` 工作流高质量生成并完成自适应无损切割与洋红色彩溢消除（Despill）。**格挡系统共分为三段层次**（源自概念图招架动作：1. 没挡刀纯身姿架势 7 帧；2. 普通格挡成功刃口微光火星 4 帧；3. 完美弹反刺目星芒与水墨爆裂 6 帧），支持起手 0.18s 精准弹反判定窗、顿帧与大硬直破绽机制。轴心统一使用自定义脚底（`spritePivot.y = 0.09`），各动作 PPU 均已对齐。

Animator：`Speed > 0.1` 切行走，`Speed > 0.55` 切奔跑，`Dodge` Trigger 触发闪避，`Jump` Trigger 触发跳跃，`Attack1/2/3` Trigger 触发轻击三连斩，`HeavyThrust` Trigger 触发重刺，`Block` Bool 控制防御架势，`BlockHit` Trigger 触发普通格挡受击微光，`ParrySuccess` Trigger 触发完美弹反大特效。预览场景 `Assets/Scenes/SpritePreview.unity`，**A / D** 走，**Shift + A / D** 跑，**W / 向上键 / W + Space** 跳跃，**Space** 闪避（可配合 A/D 指定方向），**J / 鼠标左键** 轻击连斩，**K / 鼠标右键** 重刺（支持轻击 1/2 段中直接接重刺派生终结），按住 **F** 纯格挡防守架势，单击 **G** 测试普通格挡微光，单击 **T** 测试完美弹反大特效；轻攻击与格挡期间支持 **Space** 闪避打断取消（重刺不可被闪避打断）。

帧序列图：

| 动作 | 序列 |
|---|---|
| 待机 8 帧 | [设计/青锋帧序列/idle-sequence.png](设计/青锋帧序列/idle-sequence.png) |
| 行走 15 帧 | [设计/青锋帧序列/walk-sequence.png](设计/青锋帧序列/walk-sequence.png) |
| 奔跑 9 帧 | [设计/青锋帧序列/run-sequence.png](设计/青锋帧序列/run-sequence.png) |
| 闪避 8 帧 | [设计/青锋帧序列/dodge-sequence.png](设计/青锋帧序列/dodge-sequence.png) |
| 跳跃 8 帧 | [设计/青锋帧序列/jump-sequence.png](设计/青锋帧序列/jump-sequence.png) |
| 重刺 8 帧 | [设计/青锋帧序列/heavy-sequence.png](设计/青锋帧序列/heavy-sequence.png) |
| 轻攻击三连斩 12 帧 | [设计/青锋帧序列/attack-sequence.png](设计/青锋帧序列/attack-sequence.png) |
| 格挡 8 帧综合 | [设计/青锋帧序列/block-sequence.png](设计/青锋帧序列/block-sequence.png) |
| 格挡·纯架势 7 帧 | [设计/青锋帧序列/guard-sequence.png](设计/青锋帧序列/guard-sequence.png) |
| 格挡·普通微光 4 帧 | [设计/青锋帧序列/hit-sequence.png](设计/青锋帧序列/hit-sequence.png) |
| 格挡·完美弹反 6 帧 | [设计/青锋帧序列/parry-sequence.png](设计/青锋帧序列/parry-sequence.png) |

| 文档 | 说明 |
|---|---|
| [行走动作帧设计表](设计/刀影江湖-行走动作帧设计表.md) | 60fps 起版。青锋 36 帧 / 0.60s，抽成 8 关键 |
| [跑步动作帧设计表](设计/刀影江湖-跑步动作帧设计表.md) | 60fps 起版。青锋 26 帧 / 0.43s，抽成 8 关键 |
| [闪避动作帧设计表](设计/刀影江湖-闪避动作帧设计表.md) | 60fps 起版。青锋 18 帧 / 0.30s，8 关键帧，无敌帧 3–12，位移约 0.45 单位 |
| [跳跃动作帧设计表](设计/刀影江湖-跳跃动作帧设计表.md) | 60fps 起版。青锋 8 关键相位 / 40–44f 腾空，高度 2.2 身，起跳深蹲 3f，落地缓冲 4f |
| [重刺动作帧设计表](设计/刀影江湖-重刺动作帧设计表.md) | 60fps 起版。青锋 8 关键相位 / 47f 全长，破防削盾，突进位移约 0.40 单位 |
| [格挡动作帧设计表](设计/刀影江湖-格挡动作帧设计表.md) | 60fps 起版。青锋三段式防御体系：纯架势 7 帧循环 / 普通格挡 4 帧刃口微光 / 完美弹反 6 帧星芒水墨爆裂，前 0.18s 判定窗 |

参考设定：

![青锋剑客设定](设计/刀影江湖-概念图/人物设定/00-青锋剑客-模板原图.png)

![青锋动作设计](设计/刀影江湖-概念图/人物设定/动作设计/01-青锋剑客-动作设计.png)

![青锋移动循环](设计/刀影江湖-概念图/人物设定/动作设计/11-青锋剑客-移动循环.jpg)

### 待机 · 8 帧（每帧 160ms）

侧视持剑站立，呼吸与衣发微动。源序列 01–08。下半脸暗斑已提亮。脚底对齐到轴心。

![待机帧序列](设计/青锋帧序列/idle-sequence.png)

![待机循环](New%20Tuanjie%20Project/Assets/Sprites/Player/Idle/animation.gif)

| 文件 | 说明 |
|---|---|
| `Idle/idle-1.png` … `idle-8.png` | 单帧，PPU 214 |
| `设计/青锋帧序列/idle-sequence.png` | 8 帧序列图 |
| `Idle/PlayerIdle.anim` | 循环剪辑（每帧 160ms） |
| `Idle/PlayerIdle.controller` | Idle ↔ Walk ↔ Run 状态机 |

### 行走 · 15 帧（每帧 140ms）

用户提供的 15 帧侧视行走。画布 256，PPU 100。周期 2.1s；接触帧靴距约 42.8px，两步一个循环。外袍青绿是待机 / 奔跑对色的基准。

![行走帧序列](设计/青锋帧序列/walk-sequence.png)

![行走循环](New%20Tuanjie%20Project/Assets/Sprites/Player/Walk/animation.gif)

![行走图集](New%20Tuanjie%20Project/Assets/Sprites/Player/Walk/sheet-transparent.png)

| 文件 | 说明 |
|---|---|
| `Walk/walk-1.png` … `walk-15.png` | 单帧 |
| `Walk/walk-stride.json` | 接触帧靴距约 42.8px，设计移速约 0.407 单位/秒 |
| `Walk/PlayerWalk.anim` | 循环剪辑（每帧 140ms） |

行走时世界移速必须和脚步后移匹配，否则会打滑。预览按设计移速平移；战斗里 `CharacterFootskateFix` 按「实际移速 / 当前动作设计移速」缩放 Animator。

### 奔跑 · 9 帧（每帧 45ms）

源序列 15–23 为一整圈（下一帧与 15 同姿），原地持剑奔跑。外袍饱和度对齐行走。PPU 214，与行走世界身高一致。拉开时前后靴心距约 140px，两步一个循环，设计移速约 3.23 单位/秒。

![奔跑帧序列](设计/青锋帧序列/run-sequence.png)

![奔跑循环](New%20Tuanjie%20Project/Assets/Sprites/Player/Run/animation.gif)

| 文件 | 说明 |
|---|---|
| `Run/run-1.png` … `run-9.png` | 单帧，PPU 214 |
| `设计/青锋帧序列/run-sequence.png` | 9 帧序列图 |
| `Run/run-stride.json` | 靴距约 140px，设计移速约 3.23 单位/秒 |
| `Run/PlayerRun.anim` | 循环剪辑（每帧 45ms，周期 0.405s） |

### 闪避 · 8 帧（全新大幅度极速残影瞬步，每帧 75ms，总长 0.60s）

大幅度极速残影瞬步（Phantom Dash）：大幅极速下潜蓄势（地面震开青白环形激波） → 破空暴冲贴地弹射（身后拉出水墨残影与锥形破空风痕） → 极速残影瞬步（巅峰爆发，身后拖曳 2~3 重水墨虚化残影与炽烈青白电光剑芒） → 疾速掠影穿梭 → 低姿触地滑行擦地（脚底擦出长条青白火花与泼墨刹车痕） → 侧身横向急刹拧腰减速 → 顺势起身回升（衣袍回落，残光消散） → 凝神回正收招备战。

- **动作与特效设计**：大幅度肢体张力与贴地穿梭，融合浓郁饱和的青白流光剑痕与国风水墨拖影，告别平淡短闪，爆发力与轻功飘逸感拉满。
- **规格对齐**：画布统一为 680×480 px，基准站姿人体高度严格保持 328px（与 Idle/Run/Attack 100% 统一），脚底基线锁定在 Y=437，PPU 214，Pivot (0.5, 0.09)。

![闪避帧序列](设计/青锋帧序列/dodge-sequence.png)

![闪避动图](New%20Tuanjie%20Project/Assets/Sprites/Player/Dodge/animation.gif)

![闪避图集](New%20Tuanjie%20Project/Assets/Sprites/Player/Dodge/sheet-transparent.png)

| 文件 | 说明 |
|---|---|
| `Dodge/dodge-1.png` … `dodge-8.png` | 8 帧单帧（680×480），PPU 214，0 边缘切边，0 洋红紫溢 |
| `设计/青锋帧序列/dodge-sequence.png` | 8 帧横向全景长条图（5440×480） |
| `Dodge/animation.gif` | 闪避完整循环动图（75ms/帧，13.33fps） |
| `Dodge/PlayerDodge.anim` | 团结引擎单次动画剪辑（总长 0.60s） |
| `Dodge/sheet-transparent.png` | 4×2 透明精灵图集（2720×960） |

### 跳跃 · 8 帧（全新国风轻功凌空纵跃，每帧 85ms，总长约 0.68s）

国风武侠轻功凌空纵跃（Cloud-stepping Leap）：深蹲提气蓄势（脚底凝结微弱水墨气旋与青白剑芒） → 踏空离地爆发（双足猛蹬身姿拔挺，地面震开青白环形微波与墨浪） → 穿云拔升高飞（单腿微屈，身后拉出淡墨气流尾迹） → 滞空极点悬停（横剑胸前蓄势如白鹤收翅，微重力浮空，空中出招与闪避最高灵敏窗） → 俯身寻地下落（剑尖斜引，外袍翻卷） → 破风急坠俯冲（风压呼啸，周身掠影） → 前掌触地吸震（靴底踏地激起小朵墨花轻尘） → 屈膝回正收招（缓冲弹起归位，4f 内无缝接入行走/奔跑/出剑/闪避）。

- **动作与特效设计**：身形修长挺拔，提气拔空轻灵飘逸，融合青白流光与国风水墨拖影，告别笨拙物理抛物线。
- **规格对齐**：画布统一为 680×480 px，立正基准身高严格保持 328px（与 Idle/Walk/Run/Dodge/Attack 100% 统一），脚底基线锁定在 Y=437，PPU 214，Pivot (0.5, 0.09)。

![跳跃帧序列](设计/青锋帧序列/jump-sequence.png)

![跳跃动图](New%20Tuanjie%20Project/Assets/Sprites/Player/Jump/animation.gif)

![跳跃图集](New%20Tuanjie%20Project/Assets/Sprites/Player/Jump/sheet-transparent.png)

| 文件 | 说明 |
|---|---|
| `Jump/jump-1.png` … `jump-8.png` | 8 帧单帧（680×480），PPU 214，0 边缘切边，0 洋红紫溢 |
| `设计/青锋帧序列/jump-sequence.png` | 8 帧横向全景长条图（5440×480） |
| `Jump/animation.gif` | 跳跃完整循环动图（85ms/帧） |
| `Jump/PlayerJump.anim` | 团结引擎单次动画剪辑（总长约 0.68s） |
| `Jump/sheet-transparent.png` | 4×2 透明精灵图集（2720×960） |

### 轻攻击三连斩 · 12 帧（三段连斩，每段 4 帧，每帧 85ms）

由 `generate2dsprite` 工作流高质量生成，分为流畅递进的三段刀剑武学招式。经自适应投影切割算法与洋红色彩溢消除（Despill）处理，保证伸展前挑时剑尖 100% 完整无截断，且人物轮廓 0 洋红杂边。

- **一段 · 拔剑平斩**（`attack-1` ~ `attack-4`）：起剑斜上挑起，带 0.15 单位踏步前压；
- **二段 · 顺势突刺**（`attack-5` ~ `attack-8`）：剑锋平直破风前突，带 0.20 单位疾进位移；
- **三段 · 旋身下劈**（`attack-9` ~ `attack-12`）：沉身提剑力劈华山，带 0.25 单位重力踏步压制。

![轻击三连斩帧序列](设计/青锋帧序列/attack-sequence.png)

![三连斩循环动图](New%20Tuanjie%20Project/Assets/Sprites/Player/Attack/animation.gif)

三段独立剪辑预览：

| 一段 · 拔剑平斩 | 二段 · 顺势突刺 | 三段 · 旋身下劈 |
|:---:|:---:|:---:|
| ![一段](New%20Tuanjie%20Project/Assets/Sprites/Player/Attack/attack-hit1.gif) | ![二段](New%20Tuanjie%20Project/Assets/Sprites/Player/Attack/attack-hit2.gif) | ![三段](New%20Tuanjie%20Project/Assets/Sprites/Player/Attack/attack-hit3.gif) |

![轻击透明图集](New%20Tuanjie%20Project/Assets/Sprites/Player/Attack/sheet-transparent.png)

| 文件 | 说明 |
|---|---|
| `Attack/attack-1.png` … `attack-12.png` | 12 帧单帧，PPU 214，剑尖完整无截断，0 洋红紫晕 |
| `设计/青锋帧序列/attack-sequence.png` | 12 帧横向长序列图 |
| `Attack/animation.gif` | 三连斩完整循环动图 |
| `Attack/attack-hit1.gif` ~ `hit3.gif` | 各分段连招动图 |
| `Attack/sheet-transparent.png` | 3×4 矩阵透明精灵图集 |
| `Attack/PlayerAttack1.anim` ~ `Attack3.anim` | 团结引擎单次动画剪辑（每帧 85ms） |

### 重刺 · 8 帧（概念图复刻 · 强力破防突刺，每帧 95ms，总长约 0.76s）

严格基于动作设计概念图（`01-青锋剑客-动作设计.png` §2「重刺」）绘制与打磨：沉腰蓄势（侧身半蹲收剑入怀，周身聚气） → 剑意引弓（重心压至极限，剑身蓄满炽烈青白流光与墨滴） → 踏步蹬发（后腿猛蹬碎石，身形如离弦之箭贴地暴冲） → 破空贯穿（弓步完全展开，右臂笔直向前刺出，剑化青白破空激光） → 剑芒爆鸣（刺穿目标，剑尖炸开高密度青白十字爆闪与水墨穿透溅射，造成 22 点削盾破防与 22f 强力受击硬直） → 弓步急刹滑定（前弓步踏实化解冲击，脚底擦出墨痕刹车线） → 抽剑回撤（沿中轴平稳抽回青锋剑，22–30f 允许直接按技能取消后摇） → 敛意归正（顺势回弹起立归入战斗站姿）。

- **招式定位与机制**：伤害 2.2×（轻击连招派生时达 2.4×），破盾削韧主力；不可被常规闪避打断（承担出招破绽风险），但 22–30f 允许直接接入技能（如破空刺）。出招伴随 0.40 单位大幅度踏步突进位移。
- **规格对齐**：画布统一为 680×480 px，立正基准身高严格保持 328px，脚底基线锁定在 Y=437，PPU 214，Pivot (0.5, 0.09)。

![重刺帧序列](设计/青锋帧序列/heavy-sequence.png)

![重刺动图](New%20Tuanjie%20Project/Assets/Sprites/Player/HeavyThrust/animation.gif)

![重刺图集](New%20Tuanjie%20Project/Assets/Sprites/Player/HeavyThrust/sheet-transparent.png)

| 文件 | 说明 |
|---|---|
| `HeavyThrust/heavy-1.png` … `heavy-8.png` | 8 帧单帧（680×480），PPU 214，剑尖完整无截断，0 洋红紫溢 |
| `设计/青锋帧序列/heavy-sequence.png` | 8 帧横向全景长条图（5440×480） |
| `HeavyThrust/animation.gif` | 重刺完整动画动图（95ms/帧） |
| `HeavyThrust/PlayerHeavyThrust.anim` | 团结引擎单次动画剪辑（总长约 0.76s） |
| `HeavyThrust/sheet-transparent.png` | 4×2 透明精灵图集（2720×960） |

### 格挡与弹反 · 三段式防御体系（概念图复刻 · 武者纯姿态 / 普通受击微光 / 完美弹反星芒大特效）

严格基于动作设计概念图（`01-青锋剑客-动作设计.png` §3「招架」）与横版硬核动作攻防反馈需求，将防御系统拆分为**三种互为补充的递进层次**：

1. **一、没挡刀（纯姿势 · 7 帧循环，每帧 85ms）**：**纯武者架势，零受击火花**。沉腰拔势 → 举剑横胸 → 稳步固守（按住持续固守） → 翻腕卸劲收剑回正。按住 **`F` 键** 进入固守态，防御时移动速度降至 0.35×；松手自动收剑回待机；防守期间可随时按 **`Space` 键** 侧闪脱困。
2. **二、普通格挡成功（微弱亮光 · 4 帧，每帧 75ms）**：**刃口相交微弱亮光**。剑身受击点泛起柔和青白十字微光与细碎溅射火星，身形微后错 3px 稳健卸力，随后迅速回正固守。受到常规攻击时触发，减免 70% 伤害，消耗少量耐力，轻微顿帧 3 帧。
3. **三、完美格挡成功（暴烈大特效 · 6 帧，每帧 85ms）**：**刺目白金星芒爆花 + 墨浪四射大反震**。剑气交激剧烈迸发，霸体挺立抗击。在按下 `F` 起手前 **0.18s**（约 10 帧）精准弹反窗内受击触发：**100% 免疫伤害**，触发 **8 帧强烈顿帧（Hitstop）** 与全屏震颤；**强行打断敌方招式并打入 28 帧破绽大硬直**；己方内力 +8，自第 6 帧起允许无缝衔接轻连斩或重刺追击破杀！

三段视觉对比演示：

| 1. 没挡刀（纯姿势） | 2. 普通格挡成功（微弱亮光） | 3. 完美格挡成功（暴烈大特效） |
|:---:|:---:|:---:|
| ![纯姿态](New%20Tuanjie%20Project/Assets/Sprites/Player/Block/Guard/animation.gif) | ![普通微光](New%20Tuanjie%20Project/Assets/Sprites/Player/Block/Hit/animation.gif) | ![完美弹反](New%20Tuanjie%20Project/Assets/Sprites/Player/Block/Parry/animation.gif) |

![格挡帧序列](设计/青锋帧序列/block-sequence.png)

![格挡透明图集](New%20Tuanjie%20Project/Assets/Sprites/Player/Block/sheet-transparent.png)

| 文件 | 说明 |
|---|---|
| `Block/Guard/guard-1.png` … `guard-7.png` | 纯姿势 7 帧（680×480），PPU 214，零受击特效，脚底锁定 Y=437 |
| `Block/Hit/hit-1.png` … `hit-4.png` | 普通格挡 4 帧（680×480），微弱青白十字微光与细碎火星，后错 3px 卸力 |
| `Block/Parry/parry-1.png` … `parry-6.png` | 完美弹反 6 帧（680×480），刺目白金星芒爆花与四溅水墨波纹 |
| `设计/青锋帧序列/block-sequence.png` | 8 帧横向长序列图（5440×480） |
| `设计/青锋帧序列/guard-sequence.png` | 纯姿势横向序列图（4760×480） |
| `设计/青锋帧序列/hit-sequence.png` | 普通微光横向序列图（2720×480） |
| `设计/青锋帧序列/parry-sequence.png` | 完美弹反横向序列图（4080×480） |
| `Block/PlayerBlockGuard.anim` | 团结引擎纯姿态动画剪辑（支持按住循环） |
| `Block/PlayerBlockHit.anim` | 团结引擎普通受击动画剪辑（微光后错） |
| `Block/PlayerParrySuccess.anim` | 团结引擎完美弹反动画剪辑（星芒水墨爆发） |
| `Block/PlayerBlock.anim` | 兼容旧版格挡剪辑映射 |
| `Block/sheet-transparent.png` | 4×2 透明精灵图集（2720×960） |

菜单 **刀影江湖 → 生成待机行走奔跑闪避攻击跳跃重刺格挡帧动画** 会自动将贴图设置为精灵、写成动画剪辑、挂载到 `PlayerIdle.controller` 状态机并与预览角色绑定。

---

## 帧设计表（全文）

60fps 侧面横版、右向为正方向。表内覆盖青锋、三门、杂兵与 Boss 的动作周期与战斗设计。

- 行走全文：[设计/刀影江湖-行走动作帧设计表.md](设计/刀影江湖-行走动作帧设计表.md)
  - 青锋：36 帧、0.60s、短步轻走、Walk 前倾 0–3°
  - 挂点：K1/K5 脚步，K3/K7 身形最高
- 跑步全文：[设计/刀影江湖-跑步动作帧设计表.md](设计/刀影江湖-跑步动作帧设计表.md)
  - 青锋：26 帧、0.43s、中长快步、腾空约 40–45%
  - 表内巡航前倾 8–12°；急停先立直再滑
  - 挂点：R1/R5 重脚步，R3/R7 衣袂极值
- 闪避全文：[设计/刀影江湖-闪避动作帧设计表.md](设计/刀影江湖-闪避动作帧设计表.md)
  - 青锋：18 帧、0.30s、8 关键帧，无敌帧 3–12，位移约 0.45 单位
- 跳跃全文：[设计/刀影江湖-跳跃动作帧设计表.md](设计/刀影江湖-跳跃动作帧设计表.md)
  - 青锋：8 关键相位、40–44f 腾空，高度 2.2 身，起跳深蹲 3f，落地缓冲 4f
- 重刺全文：[设计/刀影江湖-重刺动作帧设计表.md](设计/刀影江湖-重刺动作帧设计表.md)
  - 青锋：8 关键相位、47f 全长，概念图复刻，破防削盾，突进位移约 0.40 单位
- 格挡全文：[设计/刀影江湖-格挡动作帧设计表.md](设计/刀影江湖-格挡动作帧设计表.md)
  - 青锋：三段式防御与弹反体系（纯架势 7 帧循环 / 普通受击 4 帧微光 / 完美弹反 6 帧星芒大爆发，前 0.18s 精准弹反判定窗）

---

## 概念图

目录：`设计/刀影江湖-概念图/`（主视觉 01–42、人物设定表、动作设计、场景地图）。索引见同目录 `README-概念图索引.md`。

![主视觉](设计/刀影江湖-概念图/01-主视觉-青峰剑客.png)

![主角三视图](设计/刀影江湖-概念图/07-主角三视图与细节.png)

### 动作设计

`设计/刀影江湖-概念图/人物设定/动作设计/`

| 文件 | 内容 |
|---|---|
| `01-青锋剑客-动作设计.png` | 待机 / 轻连 / 重刺 / 招架 / 闪避等 |
| `11-青锋剑客-移动循环.jpg` | 本次行走帧的姿势参考 |
| `02`–`10` | 魔刀、落云、Boss、敌人、NPC |
| `12`–`15` | 各势力移动循环 |

### 人物设定表

`设计/刀影江湖-概念图/人物设定/`：青锋模板、三门弟子、杂兵、Boss、NPC 三视图。

### 场景地图

`设计/刀影江湖-概念图/场景地图/`：清河、夜奔官道、雁门、南屿等枢纽与 Boss 场。

---

## 设计文档

| 文件 | 内容 |
|---|---|
| `设计/刀影江湖-游戏设计文档.md` | GDD v1.0 |
| `设计/刀影江湖-任务流程.md` | 任务流程 |
| `设计/刀影江湖-战斗帧数据表-v0.1.md` | 战斗帧 |
| `设计/刀影江湖-剧情对白旁白全本.md` | 对白旁白 |
| `设计/刀影江湖-场景镜头描述本.md` | 镜头 |
| `设计/刀影江湖-行走动作帧设计表.md` | 全角色行走 8 关键 / 周期 |
| `设计/刀影江湖-跑步动作帧设计表.md` | 全角色奔跑 8 关键 / 前倾 / 周期 |
| `设计/刀影江湖-闪避动作帧设计表.md` | 全角色闪避 8 相位 / 无敌帧 / 位移手感 |
| `设计/刀影江湖-跳跃动作帧设计表.md` | 全角色跳跃 8 相位 / 运动学物理 / 空战派生 / 落地取消 |
| `设计/刀影江湖-重刺动作帧设计表.md` | 全角色重击 8 相位 / 概念图复刻 / 破防削盾 / 技能取消 |
| `设计/刀影江湖-格挡动作帧设计表.md` | 全角色格挡 8 相位 / 三段式防御体系 / 精准弹反判定窗 / 反击破绽 |

---

## 工程入口

- 团结工程：`New Tuanjie Project/`
- 玩家脚本：`Assets/Scripts/Player/`、`Assets/Scripts/Combat/`
- 预览输入：`PlayerSpriteLocomotion.cs`
  - **A / D**：地面行走（移速 0.407 单位/秒）
  - **Shift + A / D**：快步疾跑（移速 3.23 单位/秒）
  - **W / 向上键 / W + Space**：凌空起跳纵跃
  - **Space**：残影瞬步闪避（带无敌帧与擦地刹车，支持指定方向）
  - **J / 鼠标左键**：轻攻击三连斩（平斩、挑刺、回旋力劈）
  - **K / 鼠标右键**：概念图重刺（破防削盾突进，支持轻击 1/2 段派生终结）
  - **按住 F**：纯武者格挡架势（按住持续固守防御，移速 0.35×，松手翻腕收剑）
  - **单击 G**：测试普通格挡受击（青白十字微光与火星，微后错 3px 卸力，减伤 70%）
  - **单击 T**：测试完美格挡弹反（刺目星芒与水墨爆裂大特效，100% 免疫，顿帧 8 帧，破敌破绽）
  - **取消规则**：轻攻击与防守架势中可随时按 **Space** 闪避打断脱困
- 判定与代码接口：
  - `IsBlocking`：查询是否处于格挡防守中
  - `IsParryWindow`：查询是否处于起手 0.18s 精准弹反窗口内
  - `TriggerBlockHit()`：常规受击时触发普通微光格挡
  - `TriggerParrySuccess()`：精准受击时触发完美弹反大特效与反击窗口
- 打滑修正：`CharacterFootskateFix.cs`、`QingfengWalkStride.cs`、`QingfengRunStride.cs`
- 战斗里玩家精灵：`CombatActor` 加载 `PlayerIdle.controller`
