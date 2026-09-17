# 轻量级静态游戏部署规划清单（H5 Games Hub）

> 目标：在你现有的 **Cloudflare Pages + Phaser + R2** 技术栈之上，继续扩充一套**纯 HTML/CSS/JS、无后端、体积小、加载快**的静态小游戏合集。
> 所有候选均满足：单文件或单目录即可运行、可直接 `file://` 打开或静态托管、无数据库/无服务端逻辑。
> 来源筛选自：Simple Game Tutorials、GitHub Trending、itch.io（open-source / MIT）、Ludum Dare、LibHunt canvas-game 榜单。

---

## 一、选型原则（为什么这些适合静态托管）

| 维度 | 要求 | 说明 |
|------|------|------|
| 技术栈 | 纯前端 | HTML5 Canvas / DOM + Vanilla JS，或轻量引擎（Phaser/LittleJS/melonJS） |
| 体积 | < 500KB / 游戏 | 单文件游戏常 < 50KB；引擎类整包 gzip 后 < 200KB |
| 加载 | 首屏 < 1s | 避免外部字体/大图；用 CSS 绘制或 emoji/WebP 精灵 |
| 存储 | localStorage | 最高分、进度存浏览器本地，无需后端 |
| 资源 | R2 / CDN | 共享精灵图、音效走你已有的 `h5-game-assets` R2 桶 |

---

## 二、推荐开源库速查（按用途）

| 用途 | 推荐 | 体量 | 备注 |
|------|------|------|------|
| 2D 引擎（通用） | **Phaser 3**（你已用） | ~1MB（可 tree-shake） | 已有经验，优先复用 |
| 极轻量 2D | **LittleJS** | ~100KB, 零依赖 WebGL | 适合做单文件小游戏 |
| 街机/原型 | **Kaplay**（原 Kaboom.js） | ~300KB | API 极简，做 demo 快 |
| 老牌 2D | **melonJS** | ~600KB | 瓦片地图/物理齐全 |
| 程序化音效 | **LittleJS 内置** / **ZzFX** | ~2KB | 运行时合成，免音频文件 |
| 音效播放 | **Howler.js** | ~20KB gzip | 统一播放/静音 |
| 物理 | **Matter.js** | ~85KB | 需要刚体/碰撞时引入 |
| 资产导出 | **Blender MCP** | — | 用自然语言在 Blender 生成精灵图/图标，导出 WebP 压体积 |

> Blender MCP 定位：不作为运行时依赖，而是**资产生产流水线**。用它生成角色/道具 sprite 或 icon，导出为 `https://github.com/ahujasid/blender-mcp` 工作流后量产 WebP/PNG，再走 R2 托管，避免手绘资源拖慢上线。

---

## 三、候选游戏清单（按玩法分类）

### 🧩 益智 / Puzzle

| # | 游戏 | 描述 | 技术难点 | 推荐方案 |
|---|------|------|----------|----------|
| 1 | **2048** | 滑动合并数字方块到 2048 | 网格旋转算法、平滑动画、撤销栈 | Vanilla JS + CSS transition（`josedasilva11/2048-game` 已验证） |
| 2 | **15-Puzzle** | 滑块还原数字方阵 | 可解性校验（逆序数）、空格移动 | Vanilla JS，复用 2048 网格逻辑 |
| 3 | **Tetris** | 俄罗斯方块落块消行 | 旋转碰撞（SRS）、行消除、锁定延迟 | Vanilla Canvas 或 Phaser |
| 4 | **Minesweeper（emoji）** | 经典扫雷 | 地雷分布、 Flood-fill 展开、旗标 | Vanilla JS（`emoji-minesweeper`） |
| 5 | **Memory Match** | 翻牌配对 | 洗牌算法、计时、配对判定 | Vanilla JS + CSS flip |
| 6 | **Tic-Tac-Toe（AI）** | 井字棋 | Minimax 必胜策略、难度档 | Vanilla JS，AI 用极小化极大 |

### 🎮 动作 / Action

| # | 游戏 | 描述 | 技术难点 | 推荐方案 |
|---|------|------|----------|----------|
| 7 | **Snake** | 贪吃蛇增长/障碍/关卡 | 方向校验（防 180° 掉头）、碰撞、触屏 | Vanilla 单文件（`linzi7211/snake-game`） |
| 8 | **Breakout** | 挡板打砖块 | 球拍反弹角度、砖块矩阵、关卡 | Vanilla Canvas |
| 9 | **Space Shooter** | 俯视飞机射击 | 对象池、弹幕、波次 spawn | Phaser / LittleJS |
| 10 | **Flappy Bird** | 穿越管道 | 重力积分、管道生成、碰撞 | Vanilla Canvas |
| 11 | **Galagon** | 固定射击街机（开源） | 编队飞行、护盾、挑战关 | 单 HTML 文件（Public Domain，可直接收编） |
| 12 | **Parkour / Runner** | 跑酷残影特效 | 残影渲染、4 职业、键鼠+触屏 | Vanilla（`RyanChen0311/parkour`） |

### 🎲 休闲 / 街机 Casual

| # | 游戏 | 描述 | 技术难点 | 推荐方案 |
|---|------|------|----------|----------|
| 13 | **Simon Says** | 记忆闪光序列 | 音频/视觉反馈、序列增长 | Vanilla（`Rajaabpro/simon-game`） |
| 14 | **Whack-a-Mole** | 打地鼠 | 随机出现/计时、命中判定 | Vanilla JS |
| 15 | **Reaction Timer** | 反应测速 | 随机延迟、毫秒计时 | Vanilla，极简 |
| 16 | **Typing Test** | 打字速度测试 | 词库、WPM 计算、错误高亮 | Vanilla |
| 17 | **Balloon Pop / Catch** | 气球/落球 | 物理抛物、点击判定 | Vanilla Canvas |

### ♟ 策略 / Strategy

| # | 游戏 | 描述 | 技术难点 | 推荐方案 |
|---|------|------|----------|----------|
| 18 | **Nim（AI）** | 尼姆博弈对战不可败 AI | 博弈论、必败态计算 | Vanilla（`Nimix`，零依赖） |
| 19 | **Game of Life** | 康威生命游戏 | 网格状态演化、规则引擎 | Vanilla Canvas，赛博风好看 |
| 20 | **Tower Stack** | 叠塔物理 | 刚体平衡、晃动角度、计分 | Phaser / Matter.js（`iamkun/tower_game`） |

### 📜 文字 / 冒险 Adventure

| # | 游戏 | 描述 | 技术难点 | 推荐方案 |
|---|------|------|----------|----------|
| 21 | **Bitsy 小游戏** | 像素探索（无代码生成） | 导出为单 HTML | Bitsy 工具链 |
| 22 | **Twine 互动小说** | 分支叙事 | 节点图、变量状态 | Twine 导出 HTML |
| 23 | **D&D 文字冒险** | 你已有的 CF 项目 | 剧情状态机（可静态化） | 现有 Cloudflare Workers/R2，或静态化前端 |

---

## 四、首期落地建议（MVP 路线）

**Phase A — 合集骨架（本次交付）**
- SEO/GEO 聚合主页 `index.html`（含结构化数据、FAQ、llms.txt）
- 植入 **Snake + 2048** 两个已验证的纯前端单文件游戏作为种子
- 生产配置：`wrangler.toml` / `_headers` / `robots.txt` / `sitemap.xml`

**Phase B — 快速扩充（复用模板）— ✅ 已完成（10 款已上线）**
- 按 `games/<name>/index.html` 单目录模板，已全部落地（均为零依赖单文件纯前端）：
  - 贪吃蛇 Snake、2048（Phase A 种子）
  - Memory 记忆翻牌、Breakout 打砖块、Simon 西蒙记忆、Tetris 俄罗斯方块、Tic-Tac-Toe 井字棋(AI)
  - Space Shooter 太空射击（改用轻量 Canvas 实现，未引入 Phaser/LittleJS，保持零依赖）
  - Minesweeper 扫雷、Flappy Bird 像素飞鸟（额外扩充）
- 每款均含：localStorage 最高分/最佳成绩、键盘 + 触屏支持、赛博朋克主题、返回合集入口
- 引擎类（Parkour/Tower）如需再扩充，才考虑 Phaser/LittleJS 接 R2 资源

**Phase C — 资产流水线**
- 用 Blender MCP 批量生成 sprite/icon → WebP → 上传 `h5-game-assets` R2 桶
- 统一音效用 ZzFX/Howler，去除大音频文件

---

## 五、GEO（生成式引擎优化）要点

让 ChatGPT / Perplexity / Gemini 等 AI 搜索**更愿意引用**你的站点：

1. **直接答案优先**：FAQ 段落用一句话给出确切答案（已被 FAQPage JSON-LD 标注）。
2. **实体清晰**：站点/游戏用 `ItemList` + `Game` 类型结构化数据，机器可读。
3. **可抓文本**：核心内容全部写在 HTML 文本中（非 JS 注入），保证无头抓取可读。
4. **`llms.txt`**：根目录提供机器友好的站点摘要，供 AI agent 直接读取。
5. **快 + 稳**：首屏 < 1s、HTTPS、规范 URL，提升被引用可信度。
6. **权威外链**：对开源来源（itch.io / GitHub）做合规署名链接，增强 E-E-A-T。

---

## 六、参考来源

- Simple Game Tutorials: https://simplegametutorials.github.io/
- GitHub canvas-game 榜单: https://www.libhunt.com/topic/canvas-game
- itch.io 开源/ MIT: https://itch.io/games/code-mit/html5
- Ludum Dare 官方: https://github.com/LudumDare
- 单文件 2048: https://github.com/josedasilva11/2048-game
- 单文件 Snake: https://github.com/linzi7211/snake-game
- Blender MCP: https://github.com/ahujasid/blender-mcp
