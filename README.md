# H5 Games Hub — 轻量级静态游戏合集

纯 HTML / CSS / JavaScript 构建的轻量级网页小游戏合集，无后端、即点即玩，部署于 Cloudflare Pages。
本仓库同时是一套**可复用部署流程**与**SEO / GEO 优化样板**。

## 线上地址
| 类型 | 地址 | 状态 |
|------|------|------|
| 生产（规范域名） | https://game24.vip88.qzz.io | ✅ 已绑定并激活（2026-09-17） |
| Pages 默认域名 | https://h5games-hub.pages.dev | ✅ 可访问，已 301 收敛到规范域名 |
| HTTPS | Pages 默认强制 HTTPS + HSTS | ✅ 无需额外配置 |

## 一键校验（部署后自检）
```bash
python verify.py                              # 默认校验 https://game24.vip88.qzz.io
python verify.py https://h5games-hub.pages.dev # 校验 Pages 默认域名（canonical 断言按传入域名比对）
```
覆盖三类检查：**部署**（缓存头 / HSTS / 软 404 防护）、**SEO**（title / description / canonical / OG / Twitter / favicon / 语义化 / 标题层级 / 移动端）、**GEO**（JSON-LD / 事实型文案 / llms.txt / sitemap 覆盖率）。

## 目录结构
```
h5games-hub/
├── index.html            # SEO+GEO 优化聚合主页
├── games/snake/          # 单文件游戏：贪吃蛇
├── games/2048/           # 单文件游戏：2048
├── assets/css|js/        # 全局样式与交互
├── GAME_PLAN.md          # 游戏候选清单与选型规划
├── llms.txt              # 机器友好站点摘要（GEO）
├── robots.txt            # 爬虫指引
├── sitemap.xml           # 站点地图
├── _headers              # 缓存与安全响应头
├── _redirects            # 重定向规则
├── wrangler.toml         # Pages 部署配置
├── deploy.sh             # 一键部署脚本（可复用）
└── .github/workflows/    # GitHub Actions CI 部署
```

## 一、本地预览
```bash
cd h5games-hub
python3 -m http.server 8000      # 或 npx serve
# 打开 http://localhost:8000
```

## 二、部署（完整可复用流程）
### 方式 A：一键脚本（推荐本地）
```bash
export CF_ACCOUNT_ID="你的AccountID"
export CF_API_TOKEN="你的API Token"   # 仅含 Pages:Edit 权限的最小化 Token
bash deploy.sh
```
脚本依次执行：① 验证 Token → ② 创建 Pages 项目（若不存在）→ ③ `wrangler pages deploy` → ④ 部署后冒烟测试。

### 方式 B：GitHub Actions（推荐团队 / 持续交付）
1. 将仓库推到 GitHub。
2. 仓库 Settings → Secrets 添加 `CF_API_TOKEN` 与 `CF_ACCOUNT_ID`。
3. 推送到 `main` 分支即自动部署（`.github/workflows/deploy.yml`）。

### 方式 C：wrangler 直连（适合 CI / 受限 Shell 环境）
某些环境下 `npx` 或 npm 生成的 `.bin/wrangler` 脚本不可用（依赖 `dirname`/`cd` 等命令），
可直接调用 wrangler 的 JS 入口，并用**绝对路径**指定要部署的目录（无需 `cd`）：

```bash
export CLOUDFLARE_API_TOKEN="你的API Token"
export CLOUDFLARE_ACCOUNT_ID="你的AccountID"

node <node_modules 路径>/wrangler/bin/wrangler.js pages deploy <项目目录绝对路径> \
  --project-name=h5games-hub --commit-dirty
```

首次部署若项目尚未创建，先建项目：
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/pages/projects" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"h5games-hub","production_branch":"main"}'
```

部署后自检：`python verify.py`

> 令牌通过环境变量 / Secrets 注入，**绝不写入代码或交付文件**。

## 三、SEO 优化项（已实现）
| 项目 | 位置 | 说明 |
|------|------|------|
| 语义化结构 | `index.html` | header/nav/main/section/article/footer，利于抓取 |
| 元数据 | `<head>` | title / description / keywords / canonical / robots |
| Open Graph / Twitter | `<head>` | 社交分享卡片 |
| 结构化数据 | JSON-LD | WebSite、Organization、ItemList(Game)、FAQPage |
| 站点地图 | `sitemap.xml` | 提交给搜索引擎 |
| 爬虫指引 | `robots.txt` | 指向 sitemap |
| 缓存 / 安全头 | `_headers` | 静态资源长缓存 + HSTS / X-Frame-Options 等；每条路径**只命中一条** Cache-Control 规则（`/*` 仅放安全头，避免出现重复 max-age） |
| 404 页 / 软 404 防护 | `404.html` | 未知路径返回**真 404**（此前会返回 200+首页，属严重 SEO 问题） |
| 语义化与标题层级 | `index.html` | header/nav/main/section/article/footer，且**有且仅有一个 h1** |
| 移动端适配 | `index.html` + `style.css` | `viewport` + 窄屏 media query（头部导航自动换行） |
| 首屏性能 | 全站 | 零外部字体、零大图依赖，仅 1 个 CSS + 1 个极小的 JS，无阻塞渲染资源 |

### 校验方式
```bash
python verify.py
```

## 四、GEO 优化（生成式引擎 + 地理/区域）
### 4.1 生成式引擎优化（让 AI 搜索引用）

**事实型文案（机器与人都可读）**
- 「游戏玩法与操作方式」：逐款给出**玩法介绍 + 操作方式**（键盘与触屏分开说明），AI 引擎可直接摘引。
- 「适用场景」：明确列出碎片时间、免安装、弱网低配、记忆/反应训练、亲子课堂、前端教学等场景。
- 「常见问题」：一句话直接给答案，与 FAQPage 结构化数据一一对应。
- 全部为核心 HTML 文本（非 JS 注入），保证无头抓取可读。

**结构化数据（JSON-LD）**
| 类型 | 作用 |
|------|------|
| `WebSite` | 站点实体，含 `SearchAction`、`areaServed` |
| `Organization` | 发布方实体，含 `GeoCoordinates` / `PostalAddress` |
| `ItemList`(Game) | 10 款游戏，每项含 `name`/`url`/`description`/`gameGenre`/`playMode`/`numberOfPlayers`/`isAccessibleForFree` |
| `FAQPage` | 直接答案，提升被引用概率 |
| `BreadcrumbList` | 首页 → 游戏库，帮助引擎理解站点层级 |
| `HowTo` | 「如何开始游玩」三步，可被对话式引擎直接复述 |

**AI 友好文件**
- `llms.txt`：根目录机器友好摘要，供 ChatGPT / Perplexity / Gemini 等直接读取。

### 4.2 地理 / 区域定位优化
- **geo 元标签**：`geo.region=CN`、`geo.placename`、`geo.position`(经纬度)、`ICBM`。
- **语言/区域适配**：`<link rel="alternate" hreflang="zh-CN">` + `x-default`；`<html lang="zh-CN">`；Schema 中 `availableLanguage` / `areaServed`。
- **边缘就近分发**：Cloudflare Pages 全球 CDN，自动就近回源。
- **可选区域路由**（真·按国家分流内容）：在 Pages 项目绑定一个 Cloudflare Worker，按 `request.cf.country` 重定向或注入本地化内容，例如：
```js
export default {
  async fetch(request) {
    const country = request.cf?.country || 'XX';
    const url = new URL(request.url);
    if (country === 'CN' && url.pathname === '/') {
      url.pathname = '/index.zh-CN.html';           // 或注入 locale
      return Response.redirect(url.toString(), 302);
    }
    return fetch(request);
  }
}
```

## 五、自定义域名（已完成示例：game24.vip88.qzz.io）
本次绑定已于 2026-09-17 通过 API 完成，步骤留档可复用（目标域名父 zone 必须在同一 Cloudflare 账号内）：
1. API 向 Pages 项目添加域名：`POST /accounts/{account}/pages/projects/h5games-hub/domains`，body `{"name":"game24.vip88.qzz.io"}`。
2. 在父 zone（vip88.qzz.io）添加 `CNAME game24 → h5games-hub.pages.dev`（开启橙云代理）。
3. **全局替换**以下位置的域名为真实域名（本次已批量替换 48 处）：
   - `index.html`：`canonical`、`og:url`、`og:image`、`twitter:image`、所有 JSON-LD 里的 `url`
   - `robots.txt`：`Sitemap:` 行（**容易遗漏，会导致站点地图指向错误域名**）
   - `sitemap.xml`、`404.html`（rel=canonical）、`llms.txt`
   - `_redirects`：无需改（平台不支持域名级 301，重复内容由 canonical 收敛）
4. 重新部署（`bash deploy.sh`、方式 C 命令，或推送 main）。
5. 轮询域名状态直至 `active`（证书签发约 1–3 分钟）：`GET /accounts/{account}/pages/projects/h5games-hub/domains/{domain}`。
6. 自检：`python verify.py`（默认校验规范域名，脚本会校验 canonical 与 robots 的 Sitemap 是否指向新域名）。

## 六、扩展新游戏
在 `games/<name>/index.html` 放置单目录纯前端游戏，主页 `<ul class="grid">` 中加一张卡片即可。引擎类（Shooter/Parkour）可用 Phaser/LittleJS，素材走 R2 桶。

**新游戏页 SEO 模板（必须携带，否则 verify.py 会 FAIL）**：每个游戏页 `<head>` 内需包含——
1. `<meta name="robots" content="index, follow" />`（**禁止 noindex**，页面需被收录）
2. `<link rel="canonical" href="https://game24.vip88.qzz.io/games/<name>/" />`（指向自身路径，双域名防重复收录）
3. OG 标签（`og:title` / `og:description` / `og:url` / `og:image`）+ `twitter:card`
4. `VideoGame` JSON-LD（name/url/description/gamePlatform/genre/playMode 等字段）
主页侧同步：卡片链接、ItemList JSON-LD +1 项、FAQ 双写、`sitemap.xml` +1 URL、`llms.txt` +1 行、`verify.py` paths +1。

## 七、安全提示
- API Token、R2 Key、GitHub Token 均为敏感凭证，仅在环境变量 / Secrets 中使用。
- 建议为部署单独签发**仅含 Pages:Edit** 的最小权限 Token，并定期轮换。
- 本仓库不含任何明文密钥。
