# 图床上传凭证

发帖带图是两步：**先换 token，再拿 token 去图床上传**。这个接口负责第一步。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/get_image_bucket_token` |
| Content-Type | `application/x-www-form-urlencoded`（空表单） |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | 🟡 未登录分支 2026-10-26 实测；成功分支沿用 2026-03 记录 |

## 请求头

| 字段 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `Cookie` | 是 | `NOY_SESSION=xxxx` | 失效时 `{"status":"login"}` |
| `Content-Type` | 是 | `application/x-www-form-urlencoded` | 空表单也要带 |
| `Origin` | 否 | `https://noymanga.com` | 浏览器会带 |
| `Referer` | 否 | `https://noymanga.com/community/create` | 浏览器会带 |
| `allow-adult` | 否 | `false` | 前端会带，是否影响 token 未确认 ⚠️ |

## 成功响应

```json
{
  "status": "ok",
  "token": "nx6rVgk1PxqPE7fU15CjsoiY...=="
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | `ok` / `login` |
| `token` | string | 上传凭证，形如 URL-safe base64 |

## 关键特性

- **短时效**：换到就立刻用，别缓存到下一个小时（具体 TTL 未测 ⚠️）。
- **一次性倾向**：重复使用同一 token 上传多张图是否可行未验证；批量上传建议每张换一次。
- **与 Cookie 解耦**：图床只认 token，不认 `NOY_SESSION`，所以上传请求不需要带 Cookie（也不该带）。

## 失败分支

| 场景 | HTTP | 响应 |
| --- | --- | --- |
| 未登录 / 会话失效 | `200` | `{"status":"login"}` |

## 示例

```bash
BASE=https://noymanga.com

curl -s -X POST "$BASE/api/get_image_bucket_token" \
  -b "NOY_SESSION=xxxx" \
  -H "content-type: application/x-www-form-urlencoded" |
  python3 -c "import json,sys; print(json.load(sys.stdin)['token'])"
```

拿到 token 后继续：[upload_image.md](./upload_image.md)。
