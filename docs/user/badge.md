# 徽章列表

列出账户可用的全部徽章，以及哪些正在展示。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/badge` |
| Content-Type | `application/x-www-form-urlencoded`（无请求体） |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ⚠️ 未登录分支 2026-10-26 实测；字段沿用 2026-03 记录 |

## 请求头

| 字段 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `Cookie` | 是 | `NOY_SESSION=xxxx` | 失效时返回 `{"status":"login"}` |
| `allow-adult` | 否 | `false` | 与首页一致，是否影响徽章未确认 ⚠️ |

## 成功响应

```json
{
  "data": [
    {
      "Id": 8,
      "Name": "諾莉亞的凝視",
      "Img": "https://bucket.239847.xyz/image/nry-bge.webp",
      "Minimg": "https://bucket.239847.xyz/image/nry-bgem.webp",
      "Des": "有這個徽章的人，應該積分都比較多"
    },
    {
      "Id": 9,
      "Name": "丸",
      "Img": "https://bucket.239847.xyz/image/kimeemaru.webp",
      "Minimg": "https://bucket.239847.xyz/image/kimeemaru-m.webp",
      "Des": "2025 愚人節限定徽章"
    }
  ],
  "show": ["9", "8"],
  "status": "ok"
}
```

脱敏样例：[`fixtures/badge.json`](../../fixtures/badge.json)。

## 字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `Badge[]` | 账户可用的全部徽章 |
| `show` | `string[]` | 正在展示的徽章 **Id，注意是字符串** |
| `status` | string | `ok` / `login` / `error` |

### Badge

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Id` | int | 徽章 ID，**是数字**（与 `show` 里的字符串要互相转换） |
| `Name` | string | 徽章名 |
| `Img` | string | 展示用大图 |
| `Minimg` | string | 列表用缩略图 |
| `Des` | string | 获得条件 / 说明文案 |

## 失败分支

| 场景 | HTTP | 响应 |
| --- | --- | --- |
| 未登录 / 会话失效 | `200` | `{"status":"login"}` |
| 其他失败 | `200` | `{"status":"error"}`（未观察到触发条件 ⚠️） |

## 示例

```bash
BASE=https://noymanga.com

curl -s -X POST "$BASE/api/badge" -b "NOY_SESSION=xxxx" |
  python3 -c "
import json, sys
d = json.load(sys.stdin)
shown = {int(i) for i in d.get('show', [])}
for b in d.get('data', []):
    print('佩戴中' if b['Id'] in shown else '未佩戴', b['Id'], b['Name'])
"
```

## 备注

- `data` 与 `show` 的关系是「集合 + 子集」，佩戴状态不要自己另存一份，直接看 `show`。
- 佩戴开关见 [set_badge_show.md](./set_badge_show.md)。
- 徽章图片托管在 `bucket.239847.xyz`，与社区图床 `bucket.noymanga.com` 不是同一个域名，别混用。
