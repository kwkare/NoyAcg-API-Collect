# 用户信息

读当前登录账户的资料、积分和「正在佩戴」的徽章。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/v3/userinfo` |
| Content-Type | `application/x-www-form-urlencoded`（无请求体，`Content-Length: 0`） |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | 🟡 未登录分支 2026-10-26 实测；字段沿用 2026-03 抓包 |

这个接口也是**最轻的会话探活方式**：无副作用、返回小，适合当心跳。

## 成功响应

```json
{
  "status": "ok",
  "userinfo": {
    "Email": "your@example.com",
    "Integral": 41,
    "Time": 1673114514,
    "Uhash": "1343a10d7",
    "Uid": 12345,
    "Username": "your-name",
    "Avatar": "avatar/91266-<sha>.webp",
    "Bg": "bg/91266-<sha>.webp",
    "CommentLen": 0,
    "Badge": [
      {
        "Id": 8,
        "Name": "諾莉亞的凝視",
        "Img": "https://bucket.239847.xyz/image/nry-bge.webp",
        "Minimg": "https://bucket.239847.xyz/image/nry-bgem.webp",
        "Des": "有這個徽章的人，應該積分都比較多"
      }
    ],
    "Su": 0
  }
}
```

> 完整脱敏样例：[`fixtures/userinfo.json`](../../fixtures/userinfo.json)。
> 原文档示例里 `Badge[].Id` 写成 `0`，同一枚徽章在 [`/api/badge`](./badge.md) 里是 `8`——**以 `/api/badge` 为准**，`userinfo` 里的 `Id` 待复测 ⚠️。

## 字段说明

| 路径 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | `ok` / `login` |
| `userinfo.Email` | string | 注册邮箱（明文返回，注意别截图泄漏） |
| `userinfo.Integral` | int | 当前积分余额 |
| `userinfo.Time` | int | 注册/首次登录时间（unix 秒），语义待确认 ⚠️ |
| `userinfo.Uhash` | string | 用户短哈希，出现在图片路径里当话题目录 |
| `userinfo.Uid` | int | 用户 ID |
| `userinfo.Username` | string | 昵称 |
| `userinfo.Avatar` | string | 头像**相对路径**（`avatar/xxx.webp`），需自行拼图床域名 |
| `userinfo.Bg` | string | 背景图**相对路径**（`bg/xxx.webp`） |
| `userinfo.CommentLen` | int | 评论数，样例为 `0` ⚠️ |
| `userinfo.Badge` | `Badge[]` | 当前**佩戴中**的徽章（与 `/api/badge` 的 `show` 对应） |
| `userinfo.Su` | int | 语义未知 ⚠️（样例恒为 `0`） |

`Avatar` / `Bg` 的正确拼法（样例里徽章用的图床域名）：

```text
https://bucket.239847.xyz/image/<Avatar>
```

但**不要硬编码**这个域名——它是图床，历史上换过（`bucket.noymanga.com` 也在用）。稳妥做法是先用徽章的 `Img` 反推基地址。

## 失败分支

| 场景 | HTTP | 响应 |
| --- | --- | --- |
| 未登录 / 会话失效 | `200` | `{"status":"login"}` |

没有 `error` 分支被观察到。

## 示例

```bash
BASE=https://noymanga.com

# 探活 + 看积分
curl -s -X POST "$BASE/api/v3/userinfo" \
  -b "NOY_SESSION=xxxx" \
  -H "allow-adult: false" |
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status'), d.get('userinfo',{}).get('Integral'))"

# 打印佩戴中的徽章
curl -s -X POST "$BASE/api/v3/userinfo" -b "NOY_SESSION=xxxx" |
  python3 -c "import json,sys; d=json.load(sys.stdin); [print(b['Id'], b['Name']) for b in d.get('userinfo',{}).get('Badge',[])]"
```

## 备注

- 邮箱是明文返回的，抓包分享前必须打码。
- 接口路径是 `v3`，但登录、首页仍是 `v1`（无版本号）——站点在做版本迁移，调用时按路径分别对待。
- 无缓存头，`CF-Cache-Status: DYNAMIC`，可以放心轮询（但别太频）。
