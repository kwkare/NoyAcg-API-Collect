# 登录

用邮箱 + 密码换一枚 `NOY_SESSION` Cookie。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/login` |
| Content-Type | `application/x-www-form-urlencoded` |
| 返回 | `application/json` + 成功时附带 `Set-Cookie` |
| 鉴权 | 无 |
| 校验 | 🟡 失败分支 2026-10-26 实测 |

## 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| `user` | string | 是 | 注册邮箱 | `example@outlook.com` |
| `pass` | string | 是 | 密码明文（依赖 TLS 保护，无签名/时间戳） | `YOUR_PASSWORD` |

没有验证码、没有 2FA、也没有 CSRF token——意味着任何能发起请求的地方都能暴力尝试，所以站点一定有频率限制（见下文）。

## 响应

成功（HTTP `200`）：

```http
Set-Cookie: NOY_SESSION=<opaque-token>; Path=/; Expires=Tue, 07 Apr 2026 11:45:14 GMT; Max-Age=2592000
```

```json
{ "status": "ok" }
```

失败（HTTP 仍是 `200`，只能看 `status`）：

```json
{ "status": "error" }
```

| 可能原因 | 说明 |
| --- | --- |
| 账号不存在 | 与密码错误返回相同结果，无法枚举账号 ✅ |
| 密码错误 | 同上 |
| 频率限制 | 提示"请求频率过快"（具体阈值未测 ⚠️），短时间内多次失败后触发 |

> 失败时**没有**错误码、没有剩余次数提示，调用方只能按 `status` 二分。

## 示例

### curl

```bash
BASE=https://noymanga.com

curl -s -c jar.txt "$BASE/api/login" \
  -H "content-type: application/x-www-form-urlencoded" \
  --data-urlencode "user=you@example.com" \
  --data-urlencode "pass=YOUR_PASSWORD"

# 成功后 NOY_SESSION 就在 jar.txt 里
grep NOY_SESSION jar.txt
```

### Python

用 `requests.Session()`，Cookie 自动管理，后续请求不用手动拼头：

```python
import requests

BASE = "https://noymanga.com"


def login(email: str, password: str) -> requests.Session | None:
    session = requests.Session()
    session.headers.update({
        "accept": "application/json",
        "origin": BASE,
        "referer": f"{BASE}/login",
    })

    resp = session.post(
        f"{BASE}/api/login",
        data={"user": email, "pass": password},
        timeout=20,
    )
    payload = resp.json()

    if payload.get("status") != "ok":
        return None   # 凭据错误 / 被限流，二者无法区分
    if "NOY_SESSION" not in session.cookies:
        return None   # 防御：status=ok 但没拿到 Cookie 的异常情况
    return session
```

## 备注

- 请求体是表单，不是 JSON。用 `json=` 会拿到 `status: error`。
- **不要**把凭据写进代码或提交进仓库；本仓库的示例一律用占位符。
- 登录成功后是否需要额外「激活/签到」不确认；`/api/v3/userinfo` 能直接读即视为可用。
