# 佩戴 / 取消佩戴徽章

**开关式**接口：同一个 `id` 调一次切换一次状态，没有显式的「设为佩戴 / 取消佩戴」参数。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/v3/set_badge_show` |
| Content-Type | `application/x-www-form-urlencoded` |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ✅ 2026-10-26 带登录态实测（含往返恢复） |

## 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| `id` | int | 是 | 徽章 ID，来自 [`/api/badge`](./badge.md) 的 `data[].Id` | `8` |

## 实测行为

在 `show = ["10","11","9","8"]` 的账号上做了完整往返，结果如下：

| 操作 | `show` 变化 |
| --- | --- |
| `id=12`（未佩戴） | `["10","11","9","8"]` → `["10","11","9","8","12"]`（**追加到末尾**） |
| 再次 `id=12` | `["10","11","9","8","12"]` → `["10","11","9","8"]`（**移除**） |

也就是「**有则删，无则加**」，比较的是数组里字符串的相等，不是徽章表。

## ⚠️ 它完全不校验 ID

这是本次实测最需要记录的坑。服务端不检查 `id` 是否是合法徽章，**任何字符串都会被原样写进 `show` 数组**：

| 请求 | 响应 | `show` 结果 |
| --- | --- | --- |
| `id=12`（合法但未佩戴） | `{"status":"ok"}` | 追加 `"12"` |
| `id=114514`（不存在） | `{"status":"ok"}` | 追加 `"114514"` |
| 不带 `id` | `{"status":"ok"}` | 追加 `""`（空字符串） |

所以：

1. 以为「传个不存在的 ID 反正无效」是**错的**——它会留下脏数据（前端按 `show` 渲染，可能出现空白的徽章位）；
2. 清理办法就是**再切一次同样的值**（它会把那个垃圾值删掉）。三秒内可还原，本次实测结束后 `show` 已恢复为 `["10","11","9","8"]`，与操作前完全一致；
3. 脚本里务必先读 `/api/badge` 校验 `id ∈ data[].Id`，再做切换。

## 响应

成功、失败、垃圾值——一律是：

```json
{ "status": "ok" }
```

| 场景 | HTTP | 响应 |
| --- | --- | --- |
| 切换成功 | `200` | `{"status":"ok"}` |
| ID 不存在 / 空 ID | `200` | `{"status":"ok"}`（无法区分） |
| 未登录 | 未实测 ⚠️ | 推测 `{"status":"login"}` |

## 幂等性与重试

**不幂等**。重试一次 = 翻转两次 = 白干。要做幂等就得「先读后写」：

```bash
BASE=https://noymanga.com

# 1. 读当前佩戴列表
curl -s -X POST "$BASE/api/badge" -b "NOY_SESSION=xxxx" |
  python3 -c "import json,sys; print(json.load(sys.stdin).get('show'))"

# 2. 只有不在列表里才调
curl -s -X POST "$BASE/api/v3/set_badge_show" \
  -b "NOY_SESSION=xxxx" \
  -H "accept: application/json" \
  -H "content-type: application/x-www-form-urlencoded" \
  --data-urlencode "id=8"
```

Python 版的安全封装：

```python
def wear(session, base, badge_id: int) -> bool:
    payload = session.post(f"{base}/api/badge").json()
    show = payload.get("show", [])
    valid = {b["Id"] for b in payload.get("data", [])}
    if badge_id not in valid:
        raise ValueError(f"{badge_id} 不是可用的徽章 ID")
    if str(badge_id) in show:
        return False  # 已经戴着
    session.post(f"{base}/api/v3/set_badge_show", data={"id": badge_id})
    return True
```

## 备注

- 写操作，脚本里必须限速；批量刷没意义，只会被风控。
- 没有批量接口（未观察到）。
- 修改成功后 `/api/badge` 的 `show` 立刻生效；`userinfo.Badge` 反映的是**全部徽章集合**，不反映佩戴状态（见 [userinfo.md](./userinfo.md)）。
- `show` 的顺序就是操作顺序（新佩戴的追加在末尾），不是按 ID 排序。
