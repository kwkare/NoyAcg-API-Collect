# 会话机制（NOY_SESSION 是怎么认人的）

这套 API **没有任何「我是谁」参数**：所有请求的身份都由 Cookie `NOY_SESSION` 决定，服务端从中解出 `uid`。

本文是 2026-10-27 的实测解剖，包含 cookie 结构、下发属性、吊销行为，以及第三方软件该怎么接入。

| 项目 | 内容 |
| --- | --- |
| 凭证 | Cookie `NOY_SESSION=<opaque>` |
| 获取方式 | 浏览器登录，或程序调 [`POST /api/login`](./login.md) |
| 有效期 | 30 天（`Max-Age=2592000`），**不滑动续期** |
| 失效表现 | HTTP `200` + `{"status":"login"}`（全部端点一致，2026-10-27 实测 6 个写接口） |
| 校验 | ✅ 2026-10-27 实测（含登出吊销、属性抓取） |

## 一、请求里没有身份字段

抓遍全部写操作请求体，**没有一个带 `uid` / `user_id`**：

```text
send_community   {title, content, image, platform}
post/<id>/reply  {reply_id, text, platform, hide_ip}
community_like   {cid}
signin/sign      (空)
userinfo         (空)
```

身份 100% 由 Cookie 推导。`allow-adult` 只影响内容分级，不影响「你是谁」。

## 二、Cookie 解剖

去掉 URL-safe base64 后是 120 字节，三段，竖线分隔：

```text
1793033675|<base64(3 字节头 + 52 字符 base32)>|<32 字节签名>
   ①                    ②                        ③
```

| 段 | 长度 | 说明 |
| --- | --- | --- |
| ① 签发时间戳 | 10 位数字 | 实测 = 登录那一刻（如 `1793033675` → 2026-10-26 16:54:35 UTC），**之后不再变化** → 不支持滑动续期 |
| ② 载荷 | 76 字符 | base64 解码后是 3 字节头（`37 0c 00`）+ 52 字符 base32（≈32 字节随机 token）。**不含明文 uid** |
| ③ 签名 | 32 字节 | HMAC-SHA256，防篡改 |

整体 172 字符。形式上是「签名 cookie」，但服务端**同时维护会话表**——见下一节。

## 三、登出会真正吊销（实测）

```http
POST /api/logout        → 200 {"status":"logout"}
（同一 cookie 再用）     → {"status":"login"}
```

手动把旧 cookie 塞回浏览器也没用：**服务端已经作废这个 token**。所以丢设备后登出是有效的，这是好事。

反过来说：这也意味着服务端存了会话状态，不是纯无状态 JWT。

## 四、下发属性（登录响应头原文，token 已打码）

```http
set-cookie: NOY_SESSION=<opaque>; Path=/; Expires=Wed, 25 Nov 2026 16:54:35 GMT; Max-Age=2592000
```

| 属性 | 状态 | 影响 |
| --- | --- | --- |
| `Path=/` | ✅ 有 | 整站通用 |
| `Max-Age=2592000` | ✅ 有 | 30 天 |
| `HttpOnly` | ❌ **没有** | 页面 JS 能直接读到（实测 `document.cookie` 可见）→ **任何 XSS 都能偷走 30 天会话** |
| `SameSite` | ❌ 没写 | 现代浏览器默认按 `Lax` 处理，跨站 POST 不会带 cookie；但这是「靠默认值兜底」，不是显式防护 |
| `Secure` | ❌ 没写 | 站点有 HSTS（`strict-transport-security: max-age=31536000`），实际仍在 HTTPS 内传输 |

## 五、服务端从 Cookie 推出哪些身份

| 派生信息 | 出现在哪 |
| --- | --- |
| `Uid` | `/api/v3/userinfo`、`/api/v4/community/post/<id>` 里的 `data.uid`（**当前用户**，不是作者） |
| `Uhash` | 图床文件名前缀 `<Uhash>-<sha256>.webp`、头像/背景路径 |
| 佩戴徽章 | 评论对象的 `show_badge`（URL 逗号拼接，顺序同 `/api/badge.show`） |
| `area` | 帖子 / 评论上的地区，**服务端按 IP 判定，用户改不了** |
| 积分 | `userinfo.Integral` |
| 真实 IP | 签到记录 `data[].ip`（明文返回） |

## 六、第三方软件怎么接入

**推荐做法**：用户输一次邮箱密码 → 程序调 `/api/login` → 存下 `NOY_SESSION`（30 天）→ 过期后让用户重新登录。

```python
import requests

BASE = "https://noymanga.com"


def login(email: str, password: str) -> requests.Session:
    s = requests.Session()
    r = s.post(f"{BASE}/api/login", data={"user": email, "pass": password}, timeout=20)
    status = r.json().get("status")
    if status == "error":
        raise SystemExit("账号或密码错误")
    if status == "danger":
        raise SystemExit("输入包含不允许的字符")
    if "NOY_SESSION" not in s.cookies:
        raise SystemExit("登录成功但没拿到 Cookie")
    return s


# 后续请求全靠 s 自动带 Cookie
s = login("you@example.com", "YOUR_PASSWORD")
print(s.post(f"{BASE}/api/v3/userinfo").json()["status"])   # -> ok
```

要点：

1. **不要存明文密码**。cookie 能撑 30 天，没必要留密码。
2. **不要把 cookie 发给图床域**（`bucket.noymanga.com`）——那里只需要 upload token。脚本里用独立的 `requests.post` 上传，别共享 `Session`。
3. **cookie 就是账户**：写进日志、截图、Issue 等于送号。存储请加密（keyring / OS 凭据库）。
4. 站内**没有** OAuth、refresh token、设备管理，cookie 是唯一凭证——这是设计局限，客户端只能自己做好过期提示。

## 七、仍未知的点 ⚠️

| 问题 | 现状 |
| --- | --- |
| 改密码会不会踢掉旧会话 | 未验证 |
| 是否绑定 IP / UA | 观察到同一 cookie 在出口 IP 变化后仍可用（推测不绑定），但没做严格实验 |
| 并发会话数量上限 | 未知，多设备同时登录未见互踢 |
| 是否有服务端会话过期清理 | 未知 |
| 是否支持 HTTPS 之外的访问 | 站点强制 HTTPS + HSTS，`Secure` 属性缺失的影响有限 |

## 相关

- [login.md](./login.md)：登录接口、状态码、注册与重置密码端点
- [session 的实践示例](../../examples/python/noy_client.py)
