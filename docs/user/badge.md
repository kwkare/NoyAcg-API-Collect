# 徽章列表

列出账户可用的全部徽章，以及哪些正在展示。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/badge` |
| Content-Type | `application/x-www-form-urlencoded`（无请求体） |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ✅ 2026-10-26 带登录态实测 |

## 请求头

| 字段 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `Cookie` | 是 | `NOY_SESSION=xxxx` | 失效时返回 `{"status":"login"}` |
| `allow-adult` | 否 | `false` | 实测不影响返回内容 |

## 成功响应

```json
{
  "data": [
    {
      "Id": 8,
      "Name": "諾莉亞的凝視",
      "Img": "https://bucket.noymanga.com/image/nry-bge.webp",
      "Minimg": "https://bucket.noymanga.com/image/nry-bgem.webp",
      "Des": "有這個徽章的人，應該積分都比較多"
    }
  ],
  "show": ["10", "11", "9", "8"],
  "status": "ok"
}
```

完整样例（5 枚）：[`fixtures/badge.json`](../../fixtures/badge.json)。

## 字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | `Badge[]` | 账户可用的全部徽章（实测 5 枚，数量随账号不同） |
| `show` | `string[]` | 正在展示的徽章 **Id，是字符串**；顺序是「佩戴操作顺序」（新增的追加在末尾），不是按 ID 排序；实测 4 个 |
| `status` | string | `ok` / `login` / `error` |

### Badge

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Id` | int | 徽章 ID，**是数字**（与 `show` 里的字符串互为同一 ID） |
| `Name` | string | 徽章名（如「100 天簽到紀念」） |
| `Img` | string | 展示用大图 |
| `Minimg` | string | 列表用缩略图 |
| `Des` | string | 获得条件 / 说明 |

实测的 ID 段：`8`（積分徽章）、`9`（愚人節限定）、`10`（連續 100 天簽到）、`11` / `12`（五週年纪念 + 其 H 版）。看起来 ID 是按上线顺序自增的。

## ⚠️ 与 `userinfo.Badge` 的区别

| | `userinfo.Badge` | `/api/badge` 的 `data` |
| --- | --- | --- |
| 内容 | 只有**佩戴中**的徽章 | **全部**可用徽章 |
| `Id` | **恒为 `0`**（服务端不填） | 真实 ID |
| 用途 | 展示 | 取 ID、查佩戴状态 |

需要徽章 ID 时**只能**用 `/api/badge`。详见 [userinfo.md](./userinfo.md)。

## 怎么算「正在佩戴」

```python
payload = session.post("https://noymanga.com/api/badge").json()
shown = {int(i) for i in payload["show"]}          # show 是字符串，转成 int 才能和 Id 比
worn = [b for b in payload["data"] if b["Id"] in shown]
```

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

- `data` 与 `show` 是「集合 + 子集」关系，佩戴状态直接读 `show`，别自己另存。
- 徽章图片全部在 `bucket.noymanga.com`，老文档写的 `bucket.239847.xyz` 已废弃。
- 佩戴开关见 [set_badge_show.md](./set_badge_show.md)。注意那个接口不校验 ID，任何字符串都会被写进 `show`。
