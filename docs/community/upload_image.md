# 图片上传（图床）

把本地图片传到独立图床，拿回一个文件名；发帖时只引用文件名，**不会二次上传**。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://bucket.noymanga.com/api/upload_image` |
| Content-Type | `multipart/form-data` |
| 鉴权 | 表单里的 `token`（来自 [get_image_bucket_token](./get_image_bucket_token.md)），**不用 Cookie** |
| 校验 | ✅ 2026-10-27 实测（6 张图全部上传成功） |

图床是独立域名，跨域限制严格，所以这个接口基本只能服务端 / 本地脚本调用。网页端自己走的是主域代理路径
`https://noymanga.com/bucket/api/upload_image`（同一套参数），脚本用哪个都行。

同家族还有两个接口，用于设置头像 / 背景图（✅ 2026-10-27 背景图实测）：

| 路径 | 用途 | 参数 |
| --- | --- | --- |
| `POST /bucket/api/upload_avatar` | 设置头像 | `token` + `file`，与 `upload_image` 完全相同 |
| `POST /bucket/api/upload_bg` | 设置主页背景图 | 同上 |

- 前端把三者封装成同一个通用上传函数（先换 token，再 multipart），只是路径不同；
- **响应和发帖图片不一样**：只有 `{"status":"ok"}`，**没有 `file` 字段**——服务端在上传时直接把文件写进 `userinfo.Avatar` / `userinfo.Bg`，前端上传完只重新拉了一次 `userinfo`；
- 实测（把一张 1920×1088 的 PNG 传到 `upload_bg`）：返回 `{"status":"ok"}`，`userinfo.Bg` **立刻**变成 `bg/<Uhash>-<sha256>.webp`，文件被转成 webp（109 KB），旧文件仍留在图床上；
- 错误码比发帖图片多两种：`size`（超过大小限制）、`ext`（不支持的格式），外加通用的 `token_error` / `token_format_error`。

> 头像（`upload_avatar`）与背景图走同一套函数，除路径外结构一致；头像本身未单独实测 ⚠️。

## 请求头

> ⚠️ **图床有防盗链**：不带 `Referer: https://noymanga.com/` 直接访问图片 URL（GET，不是这个上传接口）会返回 **403**。
> 浏览器能正常显示是因为它自动带了 Referer；脚本 / agent 读图时需要自己补上，或先把图片下载到本地。

| 字段 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `Origin` | 建议 | `https://noymanga.com` | 模拟网页端来源；不刷可能被拒 ⚠️ |
| `Referer` | 建议 | `https://noymanga.com/` | 同上 |
| `allow-adult` | 否 | `false` | 与前端一致 |

> **不要**带 `Cookie: NOY_SESSION`。图床只认 `token`，多带凭据既无必要，也等于把会话交给另一个域。

## 请求参数（multipart）

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `token` | string | 是 | 上一步换到的凭证 |
| `file` | file | 是 | 图片文件，字段名必须是 `file` |

支持 `jpg / png / webp / gif` 等常见格式，服务端会**统一转成 `.webp`**（实测 6/6 全部转码，包括原本就是 webp 的）。

实测通过的规格：4.66 MB / 2894×4093 的 webp 原图照收，没有被压缩或拒绝；6 张图串行上传耗时约 42 秒。

## 成功响应

```json
{
  "file": "91266-13025882b9402bd576b628a1030433a6388156d5aaeccb40362960af47a4aa79.webp",
  "status": "ok"
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `file` | string | 图床文件名，格式 `<Uhash>-<sha256>.webp` |
| `status` | string | `ok` |

文件名里就是 `userinfo.Uhash`，所以同一个用户的图片能按前缀归组。`<sha256>` 部分看起来是内容哈希（同图重传是否复用同一文件名未验证 ⚠️）。

## 失败分支

| 场景 | 表现 | 原因 |
| --- | --- | --- |
| token 过期 / 格式不对 / 字段名不对 | `{"status":"token_format_error"}` | 最常见，重新换 token |
| 完全没带 token | HTTP `403` | 2026-10-26 实测 |
| 服务端异常 | HTTP `500` | Cloudflare 或后端抖动，重试即可 |

排查顺序：

1. 重新调一次 `get_image_bucket_token`，别复用旧 token；
2. 确认表单字段名是 `token` + `file`；
3. 让 `curl` / `requests` 自己生成 boundary，不要手拼；
4. 补上 `Origin` / `Referer`。

## 示例

### curl

```bash
BASE=https://noymanga.com
TOKEN=$(curl -s -X POST "$BASE/api/get_image_bucket_token" \
  -b "NOY_SESSION=xxxx" -H "content-type: application/x-www-form-urlencoded" |
  python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")

curl -s "https://bucket.noymanga.com/api/upload_image" \
  -X POST \
  -H "origin: https://noymanga.com" \
  -H "referer: https://noymanga.com/" \
  -F "token=$TOKEN" \
  -F "file=@/path/to/any-photo.jpg"
```

> 上游曾在仓库根目录塞了两张验证用的测试图（一张白菜 webp、一张 378×306 的 jpg），本次整理已删除——测试这个接口用你本地任意一张图片即可。

### Python

```python
import requests

BASE = "https://noymanga.com"


def upload_image(session: requests.Session, path: str) -> str:
    token = session.post(f"{BASE}/api/get_image_bucket_token", timeout=20).json()["token"]

    with open(path, "rb") as fh:
        resp = requests.post(   # 注意：用干净的 requests，不共享 session，避免把 Cookie 发给图床
            "https://bucket.noymanga.com/api/upload_image",
            headers={"origin": BASE, "referer": f"{BASE}/"},
            data={"token": token},
            files={"file": (path.rsplit("/", 1)[-1], fh)},
            timeout=60,
        )

    payload = resp.json()
    if payload.get("status") != "ok":
        raise RuntimeError(f"上传失败: {payload}")
    return payload["file"]
```

拿到 `file` 后继续：[send_community.md](./send_community.md)。
