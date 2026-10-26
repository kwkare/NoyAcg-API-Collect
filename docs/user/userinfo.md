# 用户信息

读当前登录账户的资料、积分与徽章列表。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/v3/userinfo` |
| Content-Type | `application/x-www-form-urlencoded`（无请求体，`Content-Length: 0`） |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ✅ 2026-10-26 带登录态实测 |

这个接口也是**最轻的会话探活方式**：无副作用、返回小，适合当心跳。

## 成功响应

```json
{
  "status": "ok",
  "userinfo": {
    "Email": "your@example.com",
    "Integral": 1090.7,
    "Time": 1655471118,
    "Uhash": "1343a10d7",
    "Uid": 12345,
    "Username": "your-name",
    "Avatar": "avatar/91266-<sha>.webp",
    "Bg": "bg/91266-<sha>.webp",
    "CommentLen": 0,
    "Badge": [
      {
        "Id": 0,
        "Name": "諾莉亞的凝視",
        "Img": "https://bucket.noymanga.com/image/nry-bge.webp",
        "Minimg": "https://bucket.noymanga.com/image/nry-bgem.webp",
        "Des": "有這個徽章的人，應該積分都比較多"
      }
    ],
    "Su": 0
  }
}
```

完整脱敏样例（5 枚徽章）：[`fixtures/userinfo.json`](../../fixtures/userinfo.json)。

## 字段说明

| 路径 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | `ok` / `login` |
| `userinfo.Email` | string | 注册邮箱（明文返回，截图前打码） |
| `userinfo.Integral` | **number** | 积分余额，**可能是小数**（实测 `1090.7`），别按 int 建模 |
| `userinfo.Time` | int | 账号创建时间（unix 秒），实测 `1655471118` = 2022-06-17 |
| `userinfo.Uhash` | string | 用户短哈希，出现在头像路径与图床文件名里 |
| `userinfo.Uid` | int | 用户 ID |
| `userinfo.Username` | string | 昵称 |
| `userinfo.Avatar` | string | 头像**相对路径**（`avatar/xxx.webp`），需自行拼图床域名 |
| `userinfo.Bg` | string | 背景图**相对路径**（`bg/xxx.webp`） |
| `userinfo.CommentLen` | int | 评论数（实测 `0`） |
| `userinfo.Badge` | `Badge[]` | **全部可用徽章**（与 `/api/badge` 的 `data` 同集合），**不反映佩戴状态** |
| `userinfo.Su` | int | 语义未知，实测恒为 `0` ⚠️ |

### ⚠️ 两个坑：`Id` 恒为 `0`，且不含佩戴状态

坑一：`userinfo.Badge` 里的每一项 `Id` **都是 `0`**，即使同一枚徽章在 [`/api/badge`](./badge.md) 里明明是 `8`。

坑二：这个数组是**全部徽章**，不是佩戴中的。实测在 `show` 只有 4 项时，`Badge` 依然返回 5 项；因此不能拿它判断戴没戴，要看 `/api/badge` 的 `show`。

实测对照（同一次请求）：

| 徽章 | `userinfo.Badge[].Id` | `/api/badge` 的 `Id` |
| --- | --- | --- |
| 諾莉亞的凝視 | `0` | `8` |
| 丸 | `0` | `9` |
| 100 天簽到紀念 | `0` | `10` |
| 5st 紀念徽章 | `0` | `11` |
| 5st 紀念徽章 H | `0` | `12` |

所以这不是老文档写错，而是**服务端确实不填这个字段**。要拿真实 ID：

- 用 `/api/badge` 的 `data[].Id`；
- 或者用 `Name` / `Img` 在 `data` 里做匹配（`Img` URL 是稳定的）。

## 头像 / 背景图地址

接口只给相对路径，实测拼法：

```text
https://bucket.noymanga.com/image/<Avatar>
https://bucket.noymanga.com/image/<Bg>
```

徽章图同样托管在这个图床（老文档写的 `bucket.239847.xyz` 已换成 `bucket.noymanga.com`）。**不要硬编码**域名，历史上一换就全挂，可以从任意一个徽章的 `Img` 反推基地址。

## 失败分支

| 场景 | HTTP | 响应 |
| --- | --- | --- |
| 未登录 / 会话失效 | `200` | `{"status":"login"}` |

没有 `error` 分支被观察到。

## 示例

```bash
BASE=https://noymanga.com

# 探活 + 看积分（注意可能是小数）
curl -s -X POST "$BASE/api/v3/userinfo" -b "NOY_SESSION=xxxx" |
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status'), d.get('userinfo',{}).get('Integral'))"

# 徽章列表（Id 全是 0；是否佩戴要看 /api/badge 的 show）
curl -s -X POST "$BASE/api/v3/userinfo" -b "NOY_SESSION=xxxx" |
  python3 -c "import json,sys; d=json.load(sys.stdin); [print(b['Id'], b['Name']) for b in d.get('userinfo',{}).get('Badge',[])]"
```

## 备注

- 邮箱明文返回，抓包分享前必须打码。
- 路径是 `v3`，而登录、首页仍是 `v1`（无版本号），签到已经到 `v4` —— 三套版本号并存，别指望统一。
- 无缓存头（`CF-Cache-Status: DYNAMIC`），可以轮询，但别太频。
