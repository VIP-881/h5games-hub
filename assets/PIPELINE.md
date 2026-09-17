# 资产生产流水线：Blender MCP → WebP → R2 → 站点

本目录用于把 **Blender MCP**（仓库 `ahujasid/mcp-for-blender`，原名 `blender-mcp`）接入轻量静态游戏资产生产，
产出优化后的精灵图 / 封面，上传到 R2 存储桶（`h5-game-assets`），再在静态站点中引用。

> 定位：Blender MCP 是**资产生产工具**，不是游戏运行时依赖。游戏本身仍是无后端纯前端。

## 1. 安装 Blender MCP（本地一次性）
1. 安装 `uv`（不要用 pip 装 uv）：
   - Windows：`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Linux：`curl -LsSf https://astral.sh/uv/install.sh | sh`
2. 安装 Blender 插件：`uvx mcp-for-blender install-addon`
3. 在 Blender 中：`Edit → Preferences → Add-ons` 启用 **Interface: MCP for Blender**；
   3D 视图按 `N` → **MCP for Blender** 标签页 → **Start MCP Server**。

## 2. 接入 AI 客户端（示例：Claude Desktop）
编辑 `claude_desktop_config.json`：
```json
{
  "mcpServers": {
    "blender": { "command": "uvx", "args": ["mcp-for-blender"] }
  }
}
```
> 注意：同一时刻只运行一个 MCP 服务器实例（勿同时开 Cursor 与 Claude Desktop）。

## 3. 用自然语言生成资产（Prompt 示例）
- 2D 精灵：`"Create a low-poly isometric game icon: a neon blue game controller, transparent background"`
- 封面：`"Build a cyberpunk 1200x630 cover with the text H5 游戏合集, neon gradient"`
- 材质/灯光：`"Make it metallic red"`、`"Studio lighting, isometric camera"`

## 4. 导出为优化资源
- 3D 模型：用 `export_scene` 导出 **GLB**（轻量、Web 友好）。
- 2D 精灵：通过 `execute_blender_code` 在 Blender 内渲染到 PNG，再转 **WebP**（体积极小）：
```python
import bpy
bpy.context.scene.render.filepath = "/tmp/sprite.png"
bpy.ops.render.render(write_still=True)
```
随后用 Pillow / sharp 转 WebP：`python -c "from PIL import Image; Image.open('/tmp/sprite.png').save('sprite.webp', 'WEBP', quality=85)"`

## 5. 上传到 R2（可复用脚本 `upload_r2.py`）
```bash
export R2_ACCOUNT_ID="你的AccountID"
export R2_ACCESS_KEY="你的R2AccessKey"
export R2_SECRET_KEY="你的R2Secret"
export R2_BUCKET="h5-game-assets"
python upload_r2.py assets/sprite.webp covers/sprite.webp
```
脚本基于 `boto3` + R2 的 S3 兼容端点（`https://<ACCOUNT_ID>.r2.cloudflarestorage.com`）。

### 网络/代理策略（重要）
- **默认（生产/正常网络）**：脚本会清空被注入的 `HTTP(S)_PROXY` 并对 R2 主机设置 `NO_PROXY`，
  保持 **证书严格校验**（`verify=True`），直连 R2。
- **受限 / 沙箱网络**：若运行环境存在透明 TLS 拦截代理（典型表现：连接 `*.r2.cloudflarestorage.com`
  时返回 `SSL: SSLV3_ALERT_HANDSHAKE_FAILURE`），设置 `R2_SSL_VERIFY=false` 让流量走显式 egress 代理并
  关闭证书校验（仅用于演示/受限环境，非生产建议）：
  ```bash
  R2_SSL_VERIFY=false python upload_r2.py assets/sprite.webp covers/sprite.webp
  ```
> 判因技巧：若 `https://www.cloudflare.com` 可通但 R2 端点 TLS 握手失败，通常是沙箱出口对 R2 存储域名的
> 网络限制，而非脚本问题——请在可直连 R2 的真实环境中执行上传。

## 6. 在站点中引用
- 若 R2 桶开启公开访问或绑定自定义域：`<img src="https://<r2-public-domain>/covers/sprite.webp">`。
- 也可在 Cloudflare Pages 项目将 R2 绑定为 `/r2` 路径，本地路径引用，无需公网域名。

## 7. 安全
- R2 Access Key / Secret 仅通过环境变量 / Secrets 注入，不写入代码。
- Blender MCP 的 socket 无认证，**务必绑定 localhost**，远程连接需谨慎。
- 执行 `execute_blender_code` 前先保存工程。
