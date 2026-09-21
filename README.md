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

## 本次进展（青锋剑客精灵）

按青袍侧视设定，用 generate2dsprite 做出可进游戏的待机 / 行走 / 奔跑帧，并接到 Animator：`Speed > 0.1` 切行走，`Speed > 0.55` 切奔跑。预览场景 `Assets/Scenes/SpritePreview.unity`，**A / D** 走，**Shift + A / D** 跑。战斗原型里玩家移动播奔跑。三套动作共用待机 scale profile `qingfeng-swordsman`，身形一致。

行走当前进游戏的是用户提供的 15 帧循环（每帧 140ms，周期 2.1s），按待机尺度缩放后替换原 8 关键。奔跑仍按帧设计表抽 8 关键；前倾约 20°–25°（表内巡航角 8°–12° 在精灵尺寸上不够清楚）。奔跑循环必须左右腿交替：R1 近靴在前 / R5 远靴在前。

| 文档 | 说明 |
|---|---|
| [行走动作帧设计表](设计/刀影江湖-行走动作帧设计表.md) | 60fps 起版。青锋 36 帧 / 0.60s，抽成 8 关键 |
| [跑步动作帧设计表](设计/刀影江湖-跑步动作帧设计表.md) | 60fps 起版。青锋 26 帧 / 0.43s，抽成 8 关键 |

参考设定：

![青锋剑客设定](设计/刀影江湖-概念图/人物设定/00-青锋剑客-模板原图.png)

![青锋动作设计](设计/刀影江湖-概念图/人物设定/动作设计/01-青锋剑客-动作设计.png)

![青锋移动循环](设计/刀影江湖-概念图/人物设定/动作设计/11-青锋剑客-移动循环.jpg)

### 待机 · 6 帧（2×3）

侧视持剑站立，只做呼吸与衣发微动。脚底对齐，尺度配置写在 `character-scale-profile.json`，后续动作共用。

![待机循环](New%20Tuanjie%20Project/Assets/Sprites/Player/Idle/animation.gif)

| 文件 | 说明 |
|---|---|
| `New Tuanjie Project/Assets/Sprites/Player/Idle/idle-1.png` … `idle-6.png` | 单帧 |
| `Idle/sheet-transparent.png` | 透明图集 |
| `Idle/PlayerIdle.anim` | 循环剪辑 |
| `Idle/PlayerIdle.controller` | Idle ↔ Walk ↔ Run 状态机 |

### 行走 · 15 帧（3×5，每帧 140ms）

用户提供的 15 帧侧视行走，未重画。按待机 scale profile 缩到 256、脚底对齐，去掉原图脚下浅色投影。周期 2.1s；接触帧靴距约 43px，两步一个循环。

![行走循环](New%20Tuanjie%20Project/Assets/Sprites/Player/Walk/animation.gif)

![行走图集](New%20Tuanjie%20Project/Assets/Sprites/Player/Walk/sheet-transparent.png)

| 文件 | 说明 |
|---|---|
| `Walk/walk-1.png` … `walk-15.png` | 单帧 |
| `Walk/walk-stride.json` | 接触帧靴距约 42.8px，设计移速约 0.407 单位/秒 |
| `Walk/PlayerWalk.anim` | 循环剪辑（每帧 140ms） |

行走时世界移速必须和脚步后移匹配，否则会打滑。预览按设计移速平移；战斗里 `CharacterFootskateFix` 按「实际移速 / 当前动作设计移速」缩放 Animator。

### 奔跑 · 8 帧（2×4，约 18.5 FPS）

按 [跑步动作帧设计表](设计/刀影江湖-跑步动作帧设计表.md) 的青锋 26 帧 / 0.43s 周期抽 8 关键：Contact / Push-off / Flight / Prep ×2。压剑疾行，双手按鞘，原地跑步机循环。R1 近处三分之四靴在前，R5 外侧暗靴在前；R3 / R7 收对侧膝。

![奔跑循环](New%20Tuanjie%20Project/Assets/Sprites/Player/Run/animation.gif)

![奔跑图集](New%20Tuanjie%20Project/Assets/Sprites/Player/Run/sheet-transparent.png)

| 关键帧 | 相位 | 支撑 / 腾空 |
|---|---|---|
| R1 | 右脚接触 Contact | 右脚短接触，近靴在前 |
| R2 | 右脚蹬离 Push-off | 右将离地 |
| R3 | 腾空 · 左腿折叠 Flight | 双脚离地，左膝收起 |
| R4 | 左脚将落 Prep | 远靴前伸将落 |
| R5 | 左脚接触 | 左短接触，远靴在前（对偶 R1） |
| R6 | 左脚蹬离 | 对偶 R2 |
| R7 | 腾空 · 右腿折叠 | 双脚离地，右膝收起（对偶 R3） |
| R8 | 右脚将落 | 近靴前伸，回到 R1 |

| 文件 | 说明 |
|---|---|
| `Run/run-1.png` … `run-8.png` | 单帧 |
| `Run/run-stride.json` | 接触帧靴距约 72.8px，设计移速约 3.37 单位/秒 |
| `Run/PlayerRun.anim` | 循环剪辑（每帧 54ms，周期 0.43s） |

菜单 **刀影江湖 → 生成待机行走奔跑帧动画** 会把 png 重新写成剪辑并挂到控制器。

---

## 帧设计表（全文）

60fps 侧面横版、右向为正方向。表内覆盖青锋、三门、杂兵与 Boss 的 Walk / Run 周期；青锋精灵按其中 8 关键落地。

- 行走全文：[设计/刀影江湖-行走动作帧设计表.md](设计/刀影江湖-行走动作帧设计表.md)
  - 青锋：36 帧、0.60s、短步轻走、Walk 前倾 0–3°
  - 挂点：K1/K5 脚步，K3/K7 身形最高
- 跑步全文：[设计/刀影江湖-跑步动作帧设计表.md](设计/刀影江湖-跑步动作帧设计表.md)
  - 青锋：26 帧、0.43s、中长快步、腾空约 40–45%
  - 表内巡航前倾 8–12°；急停先立直再滑
  - 挂点：R1/R5 重脚步，R3/R7 衣袂极值

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

---

## 工程入口

- 团结工程：`New Tuanjie Project/`
- 玩家脚本：`Assets/Scripts/Player/`、`Assets/Scripts/Combat/`
- 预览输入：`PlayerSpriteLocomotion.cs`（A/D 走，Shift+A/D 跑）
- 打滑修正：`CharacterFootskateFix.cs`、`QingfengWalkStride.cs`、`QingfengRunStride.cs`
- 战斗里玩家精灵：`CombatActor` 加载 `PlayerIdle.controller`
