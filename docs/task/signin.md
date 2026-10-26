# 任务系统 · 签到

首页加载时会顺带查一次签到记录（`/api/v4/signin/record`）。这是本仓库首次记录任务系统的接口，**执行签到**的那个端点还没整理 🚧。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/v4/signin/record` |
| Content-Type | `application/x-www-form-urlencoded`（无请求体） |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ✅ 2026-10-26 实测（1 次，只读） |

## 响应

```json
{
  "continuous": 140,
  "data": [
    {
      "id": 6648564,
      "uid": 38354,
      "continuous": 140,
      "ip": "116.248.98.173",
      "time": "2026-10-26T00:00:00+08:00",
      "weekday": 1
    }
  ],
  "status": 200,
  "today": true
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `continuous` | int | 当前连续签到天数 |
| `data` | object[] | 签到记录，实测只返回最近 1 条 |
| `data[].id` | int | 记录 ID |
| `data[].uid` | int | 用户 ID |
| `data[].continuous` | int | 该次签到时累计的连续天数 |
| `data[].ip` | string | **签到时的 IP**，敏感字段 |
| `data[].time` | string | 签到时间，带时区的 ISO 8601（`+08:00`） |
| `data[].weekday` | int | 星期（`1` = 周一？未验证 ⚠️） |
| `status` | **int** | `200` 表示成功——注意这里是**数字**，和别的接口的字符串 `"ok"` 不同 |
| `today` | bool | 今天是否已签到；`true` 时前端不再显示签到按钮 |

脱敏样例（uid / ip / 记录 id 已打码）：[`fixtures/signin-record.json`](../../fixtures/signin-record.json)。

## 坑

1. **`status` 是数字**。统一按 `status === "ok"` 判断的代码会在这个接口上误判，建议先看 `typeof status`。
2. **返回 IP**：`data[].ip` 是明文字段，抓包截图前必须处理，否则等于公开自己的出口 IP。
3. **`v4`**：其他接口是 `v1`（无版本号）或 `v3`，签到已经跑到 `v4` 了，站点在持续迁移。

## 尚未整理

| 待补 | 已知线索 |
| --- | --- |
| 执行签到 | 预计在 `/api/v4/signin*` 家族下，名字可能是 `signin` / `signin/do`，未验证 🚧 |
| 签到奖励规则 | 积分奖励、连续天数加成、断签重置条件全部未知 🚧 |
| 任务列表 / 每日任务 | 未观察到相关请求 🚧 |

如果你抓到了执行签到的请求，欢迎按 `CONTRIBUTING.md` 补一份（**只读优先**，别提交自动签到的脚本）。
