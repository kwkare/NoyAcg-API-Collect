# 佩戴 / 取消佩戴徽章

**开关式**接口：同一个 `id` 调一次切换一次状态，没有显式的「设为佩戴/取消」参数。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/v3/set_badge_show` |
| Content-Type | `application/x-www-form-urlencoded` |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ⚠️ 2026-03 记录，未复测 |

## 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| `id` | int | 是 | 徽章 ID（来自 [`/api/badge`](./badge.md) 的 `data[].Id`） | `8` |

## 行为

| 调用前状态 | 调用后 |
| --- | --- |
| 未佩戴 | 佩戴 |
| 已佩戴 | 取消佩戴 |

> ⚠️ 因为是 toggle，**脚本重试会翻转两次**。要幂等就得先 `GET` 一次 `/api/badge` 读 `show`，再决定要不要调。
> ⚠️ 早期记录里，传入不存在的 `id`（如 `114514`）**也返回 `status: ok`**，说明它不校验 ID 合法性。这条未复测，写脚本时请顺手验证并在 PR 里更新。

## 响应

```json
{ "status": "ok" }
```

| 场景 | 响应 |
| --- | --- |
| 切换成功 / ID 不存在 | `{"status":"ok"}`（无法区分，见上） |
| 未登录 | `{"status":"login"}` ⚠️ 未实测 |
| 其他失败 | `{"status":"error"}` ⚠️ 未观察到 |

## 示例

```bash
BASE=https://noymanga.com

# 切换 8 号徽章的佩戴状态
curl -s -X POST "$BASE/api/v3/set_badge_show" \
  -b "NOY_SESSION=xxxx" \
  -H "accept: application/json" \
  -H "content-type: application/x-www-form-urlencoded" \
  --data-urlencode "id=8"
```

安全的切换方式（先读后写）：

```bash
# 1. 读当前佩戴列表
curl -s -X POST "$BASE/api/badge" -b "NOY_SESSION=xxxx" |
  python3 -c "import json,sys; print(json.load(sys.stdin).get('show'))"

# 2. 只有不在列表里才调
curl -s -X POST "$BASE/api/v3/set_badge_show" -b "NOY_SESSION=xxxx" -d "id=8"
```

## 备注

- 这是**写操作**，脚本里要限速；批量刷徽章没有意义，只会被风控。
- 前端每次点击调一次，没有批量接口（未观察到）。
- 修改成功后 `userinfo.Badge` 与 `/api/badge` 的 `show` 会同步更新，无需额外刷新接口。
