# 任务系统 · 签到

每日签到（+ 连续签到天数）相关接口，共两个：

| 用途 | 端点 | 方法 |
| --- | --- | --- |
| 查记录 | `POST /api/v4/signin/record` | 只读 |
| 执行签到 | `POST /api/v4/signin/sign` | **写操作** |

| 项目 | 内容 |
| --- | --- |
| Content-Type | `application/x-www-form-urlencoded`（两者都是空表单） |
| 鉴权 | Cookie `NOY_SESSION` |
| 刷新时间 | **每天 00:00（UTC+8）** 重置「今天」 |
| 校验 | ✅ 2026-10-27 00:10（UTC+8）跨零点实测 |

## 刷新时间怎么测出来的

在 `2026-10-27 00:10 (+08:00)` 这个时间点连续观察：

| 时刻 | `record.today` | 说明 |
| --- | --- | --- |
| 00:09（零点前） | `true` | 昨天已经签过 |
| 00:10（零点后） | **`false`** | 新的一天，可以签了 |
| 签到后 | `true` | 新记录 `time` = `2026-10-27T00:00:00+08:00` |

记录时间戳也不带实际签到时刻，一律写当天 `00:00:00+08:00`——所以「几点签的」查不出来，只能看出签了哪天。

## 一、查签到记录

```http
POST /api/v4/signin/record
```

成功响应：

```json
{
  "continuous": 141,
  "data": [
    {
      "id": 6660439,
      "uid": 12345,
      "continuous": 141,
      "ip": "0.0.0.0",
      "time": "2026-10-27T00:00:00+08:00",
      "weekday": 2
    },
    {
      "id": 6648564,
      "uid": 12345,
      "continuous": 140,
      "ip": "0.0.0.0",
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
| `status` | **int** | `200` = 成功。注意是**数字**，别的接口是字符串 `"ok"` |
| `today` | bool | 今天是否已签到；`false` 时前端才显示签到按钮 |
| `continuous` | int | 当前连续天数；**今天没签时返回 `-1`**（不是 0，也不是 `data[0].continuous`） |
| `data` | object[] | 最近若干天记录，**新的在前**（实测返回 2 条，是否只保留 2 条未确认 ⚠️） |
| `data[].id` | int | 记录 ID |
| `data[].uid` | int | 用户 ID |
| `data[].continuous` | int | **那一天签完**的连续天数 |
| `data[].ip` | string | 签到时的 IP（明文返回，敏感） |
| `data[].time` | string | 固定为当天 `00:00:00+08:00` |
| `data[].weekday` | int | 星期几，**1 = 周一 … 7 = 周日**（实测 10-26 周一 → 1，10-27 周二 → 2） |

脱敏样例：[`fixtures/signin-record.json`](../../fixtures/signin-record.json)。

## 二、执行签到

```http
POST /api/v4/signin/sign
```

空表单，没有参数。响应：

```json
{ "continuous": 141, "msg": "success", "status": 200 }
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `status` | **int** | `200` 成功 / `500` 失败 |
| `msg` | string | `success` 或错误文案（英文） |
| `continuous` | int | 签完之后的连续天数 |

### 重复签到

```json
{ "msg": "Please do not sign in too frequently", "status": 500 }
```

- HTTP 状态码仍然是 **200**，只有业务 `status` 是 `500`；
- 同一自然日内第二次调用必定失败（幂等，不会重复加分）；
- 提示文案是英文、且措辞是「不要太频繁」而不是「今天签过了」——判断时看 `today` 字段比看文案可靠。

### 奖励

实测积分：`1091.7` → `1092.7`，即**每次 +1**。

奖励是否随连续天数递增、断签是否清零、有没有额外道具——全部未验证 ⚠️。唯一能确定的是响应里**不含**奖励信息，要看积分得自己再查一次 `/api/v3/userinfo`。

## 失败分支汇总

| 场景 | HTTP | 响应 |
| --- | --- | --- |
| 签到成功 | `200` | `{"continuous":N,"msg":"success","status":200}` |
| 今天已签过 | `200` | `{"msg":"Please do not sign in too frequently","status":500}` |
| 未登录 | 未实测 ⚠️ | 推测 `{"status":"login"}`（或数字） |

## 示例

```bash
BASE=https://noymanga.com

# 今天签了吗
curl -s -X POST "$BASE/api/v4/signin/record" -b "NOY_SESSION=xxxx" |
  python3 -c "import json,sys; d=json.load(sys.stdin); print('today=',d['today'],'continuous=',d['continuous'])"

# 签到（今天没签才会成功）
curl -s -X POST "$BASE/api/v4/signin/sign" -b "NOY_SESSION=xxxx"
```

Python 版（只在没签时调用）：

```python
def sign_in(session, base):
    rec = session.post(f"{base}/api/v4/signin/record").json()
    if rec.get("today"):
        return {"skipped": True, "continuous": rec.get("continuous")}
    return session.post(f"{base}/api/v4/signin/sign").json()
```

## 踩坑清单

1. **`status` 是数字**，`status == "ok"` 的通用判断在这里会误判。
2. **未签到时 `continuous` 是 `-1`**，别拿它当历史连续天数用（要用 `data[0].continuous`）。
3. **返回明文 IP**：`data[].ip` 是你每次签到的出口 IP，抓包截图前务必打码。
4. 签到后积分不会出现在响应里，要另外查。
5. 记录时间恒为当天 0 点，别用来算「几点签的」。
