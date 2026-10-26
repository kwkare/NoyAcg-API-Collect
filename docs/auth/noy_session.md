# NOY_SESSION（会话凭证）

几乎所有接口都要它，是这套 API 的唯一鉴权手段。

| 项目 | 内容 |
| --- | --- |
| 载体 | HTTP 请求头 `Cookie: NOY_SESSION=<token>` |
| 来源 | `POST /api/login` 成功的响应头 `Set-Cookie` |
| 有效期 | 约 30 天（`Max-Age=2592000`），期间每次登录似乎会重新下发 ⚠️ |
| 失效表现 | 接口 HTTP `200`，响应体 `{"status":"login"}` |
| 校验 | 🟡 失效分支 2026-10-26 实测 |

## 典型形态

```http
Set-Cookie: NOY_SESSION=<opaque-token>; Path=/; Expires=Tue, 07 Apr 2026 11:45:14 GMT; Max-Age=2592000
```

- 值是**不透明字符串**，没有可解析的结构（不是 JWT）；
- 只在服务端有意义，别尝试自己构造或延长；
- `Path=/`，所以整站（含 `/api/v3/*`）通用。

## 用法

```bash
# 手动带
curl -s -X POST https://noymanga.com/api/v3/userinfo -H "Cookie: NOY_SESSION=xxxx"

# 或者交给 cookie jar
curl -s -c jar.txt -X POST https://noymanga.com/api/login --data "user=…&pass=…"
curl -s -b jar.txt -X POST https://noymanga.com/api/v3/userinfo
```

Python 里用 `requests.Session()` 自动挂载即可，见 [`examples/python/noy_client.py`](../../examples/python/noy_client.py)。

## 关于「已登录」的判断

别用 HTTP 状态码，永远用响应体：

```python
data = resp.json()
if data.get("status") == "login":
    # 会话过期，需要重新登录
```

`/api/v3/userinfo` 是最轻的探活接口（无请求体、无副作用），适合当心跳。

## 注意事项

- 这是**长期有效的账户凭证**：贴到 Issue、截图、日志里等于把账号送人。抓包分享时务必替换成 `xxxx`。
- 有效期 30 天意味着任何拿到它的脚本可以长期稳定访问；如果怀疑泄漏，改密码（是否会让旧会话失效未验证 ⚠️）。
- 图床域名 `bucket.noymanga.com` 是 `noymanga.com` 的子域，浏览器会在跨子域请求里带上这个 Cookie；自己写脚本上传图片时**不要**把会话 Cookie 发给图床（它只需要 token），见 [upload_image.md](../community/upload_image.md)。
