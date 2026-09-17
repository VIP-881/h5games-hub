#!/usr/bin/env python3
"""
R2 资产上传脚本（S3 兼容）— 将本地优化资产上传到 Cloudflare R2 桶
依赖：boto3（pip install boto3）
用法：
  export R2_ACCOUNT_ID=xxxx
  export R2_ACCESS_KEY=xxxx
  export R2_SECRET_KEY=xxxx
  export R2_BUCKET=h5-game-assets
  python3 upload_r2.py <本地文件> [R2对象Key]
"""
import os
import sys
import mimetypes
import boto3
from botocore.config import Config

# --- 网络/代理策略 -----------------------------------------------------
# 两种运行场景：
#  1) 生产/正常网络（默认）：直连 R2，清空可能被注入的 HTTP(S)_PROXY 并对
#     R2 主机设置 NO_PROXY，保持证书严格校验。
#  2) 受限/沙箱网络（设置 R2_SSL_VERIFY=false）：存在透明 TLS 拦截代理，
#     必须走显式 egress 代理并关闭证书校验才能连通（仅用于演示环境）。
_R2_SSL_VERIFY = os.environ.get("R2_SSL_VERIFY", "true").lower() != "false"

if _R2_SSL_VERIFY:
    for _p in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        os.environ.pop(_p, None)
    if ACCOUNT_ID := os.environ.get("R2_ACCOUNT_ID"):
        os.environ["NO_PROXY"] = f"*.r2.cloudflarestorage.com,{ACCOUNT_ID}.r2.cloudflarestorage.com"
        os.environ["no_proxy"] = os.environ["NO_PROXY"]
    _ssl_verify = True
else:
    # 保留代理环境变量，让 urllib3 走 egress 代理；关闭证书校验绕开 MITM。
    _ssl_verify = False
# ----------------------------------------------------------------------

ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
SECRET_KEY = os.environ["R2_SECRET_KEY"]
BUCKET = os.environ.get("R2_BUCKET", "h5-game-assets")
ENDPOINT = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="auto",
    verify=_ssl_verify,
    config=Config(signature_version="s3v4"),
)

if len(sys.argv) < 2:
    print("用法：python3 upload_r2.py <本地文件> [R2对象Key]")
    sys.exit(1)

local = sys.argv[1]
key = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(local)
ctype, _ = mimetypes.guess_type(local)
extra = {"ContentType": ctype} if ctype else {}

print(f"上传 {local} -> s3://{BUCKET}/{key}")
s3.upload_file(local, BUCKET, key, ExtraArgs=extra)

# 上传后校验对象确实存在
try:
    meta = s3.head_object(Bucket=BUCKET, Key=key)
    size = meta.get("ContentLength", "n/a")
    ctype_ok = meta.get("ContentType", ctype)
    print(f"校验通过：对象已存在，大小={size}B，ContentType={ctype_ok}")
except Exception as e:  # noqa: BLE001
    print("警告：上传可能成功但 head_object 校验失败：", repr(e))

print("完成。R2 对象：", f"{ENDPOINT}/{BUCKET}/{key}")
