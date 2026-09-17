#!/usr/bin/env bash
# H5 Games Hub — 可复用一键部署脚本（Cloudflare Pages）
# 用法（在 h5games-hub 目录中执行）：
#   export CF_ACCOUNT_ID=xxxx
#   export CF_API_TOKEN=cfat_xxxx
#   bash deploy.sh
# 可选环境变量：PROJECT_NAME, PROD_BRANCH, DOMAIN, WRANGLER_BIN
#
# 说明：
# - 规范域名已绑定 game24.vip88.qzz.io（2026-09-17），故 DOMAIN 默认值已更新；
#   双域名均可访问，重复内容由 canonical 收敛（Pages 的 _redirects 不支持域名级 301）。
# - WRANGLER_BIN 默认 `npx wrangler`；若 npx 不可用（如便携 Node 环境），
#   可指定 JS 入口直连：WRANGLER_BIN="node /path/to/node_modules/wrangler/bin/wrangler.js"
# - 部署后完整校验请运行：python verify.py "$DOMAIN"
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-h5games-hub}"
PROD_BRANCH="${PROD_BRANCH:-main}"
DOMAIN="${DOMAIN:-https://game24.vip88.qzz.io}"
ACCOUNT_ID="${CF_ACCOUNT_ID:-}"
API_TOKEN="${CF_API_TOKEN:-}"
WRANGLER_BIN="${WRANGLER_BIN:-npx wrangler}"

if [[ -z "$ACCOUNT_ID" || -z "$API_TOKEN" ]]; then
  echo "错误：请先设置环境变量 CF_ACCOUNT_ID 与 CF_API_TOKEN" >&2
  exit 1
fi
export CLOUDFLARE_API_TOKEN="$API_TOKEN"
export CLOUDFLARE_ACCOUNT_ID="$ACCOUNT_ID"

echo "== 1/4 验证 API Token =="
if ! curl -s -X GET "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/tokens/verify" \
     -H "Authorization: Bearer $API_TOKEN" | grep -q '"success":true'; then
  echo "Token 验证失败，终止部署" >&2; exit 1
fi
echo "Token OK"

echo "== 2/4 创建 Pages 项目（若已存在返回 400，忽略即可）=="
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  --data "{\"name\":\"$PROJECT_NAME\",\"production_branch\":\"$PROD_BRANCH\"}" \
  -o /dev/null -w "create status: %{http_code}\n" || true

echo "== 3/4 部署 =="
$WRANGLER_BIN pages deploy . --project-name="$PROJECT_NAME" --commit-dirty

echo "== 4/4 部署后冒烟测试（详细校验见 verify.py）=="
for p in / /games/snake/ /games/puzzle15/ /games/whackamole/ /games/hanoi/ /games/pong/ /games/sudoku/ /games/gomoku/ /games/lightsout/ /games/maze/ /games/dino/ /games/game24/ /llms.txt /robots.txt /sitemap.xml; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$DOMAIN$p")
  echo "$code  $DOMAIN$p"
done
echo "部署完成。规范域名：$DOMAIN"
echo "完整 SEO/GEO 校验：python verify.py \"$DOMAIN\""
