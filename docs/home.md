# 首页聚合数据

返回首页一次渲染所需的数据：公告、四个榜单、标签。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/home` |
| Content-Type | `application/x-www-form-urlencoded`（无请求体，`Content-Length: 0`） |
| 返回 | `application/json;charset=utf-8` |
| 鉴权 | Cookie `NOY_SESSION`，**必需** |
| 分级 | 请求头 `allow-adult`（默认值有坑，见下） |
| 校验 | ✅ 2026-10-26 带登录态实测（8 次请求） |

## 请求头

| 字段 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `Cookie` | 是 | `NOY_SESSION=xxxx` | 未带或失效时返回 `{"status":"login"}`，HTTP 仍是 `200` |
| `allow-adult` | 否 | `false` | **不传时等同 `true`**，见下表 |
| `Origin` / `Referer` | 否 | `https://noymanga.com` | 浏览器会自动带，脚本可以不带 |

### `allow-adult` 取值（2026-10-26 实测）

| 值 | 行为 | 实测数据 |
| --- | --- | --- |
| `false` | 只返回全年龄 | 77 本，`Adult` 全为 `0`，`tags` 9 个 |
| `true` | 只返回 R18 | 80 本，`Adult` 全为 `1`，`tags` 13 个 |
| `both` | 混合返回 | 75 本，`Adult` 出现 `0` 和 `1`，`tags` 22 个 |
| 不传 | **等同 `true`** | 与 `true` 的响应逐字节一致（80 本、全 R18） |

两个必须知道的结论：

- **默认返回 R18**。抓包时忘了带头，会以为站点首页全是成人向内容。
- `false` 与 `true` 的书单**零交集**（59 / 60 个 `Bid` 无重叠），不是「过滤掉一部分」，而是两套互斥内容池。
- `tags` 跟着分级变，`false` 得到「冒險 / 奇幻 / 科幻…」，`true` 得到「蘿莉 / 全彩 / 長筒襪…」，`both` 是并集。做标签筛选时不能假设标签集合固定。

## 响应结构

2026-10-26 实测的顶层字段：

| 字段 | 类型 | 说明 | 条数（false / true） |
| --- | --- | --- | --- |
| `bulletin` | `Bulletin` | 顶部公告 | 1 / 1 |
| `favDay` | `Book[]` | 日收藏榜 | 20 / 20 |
| `readDay` | `Book[]` | 日阅读榜 | 20 / 20 |
| `fs` | `Book[]` | 推荐位，排序规则未确认 ⚠️ | 20 / 20 |
| `proportion` | `Book[]` | 高质 / 编辑推荐，规则未确认 ⚠️ | 17 / 20 |
| `tags` | `string[]` | 当前分级下可用的标签 | 9 / 13 |
| `status` | `string` | `ok` / `login` | — |

> **`stream` 已经没有了。** 2026-03 的文档里它是「番剧 / 流媒体推荐」，现在 `/api/home` 不再返回这个 key（连续 7 次抓取确认）。前端代码仍写着 `f.stream ?? []`，取不到就整块不渲染——所以首页的「動畫」区块目前是空的，不是你的解析写错了。
> 旧的完整快照（含 `stream`、79 本书）留在 [`fixtures/home.json`](../fixtures/home.json)，2026-10 的精简快照见 [`fixtures/home-2026-10-sample.json`](../fixtures/home-2026-10-sample.json)。

条目数**不固定**：同一个账号连续请求，`proportion` 在 16~20 之间波动。不要用长度做断言。

## Bulletin

| 字段 | 类型 | 说明 | 示例 |
| --- | --- | --- | --- |
| `text` | string | 公告文案 | `"點擊廣告，救救Noy！"` |
| `show` | bool | 是否展示（前端目前隐藏该区域） | `true` |

## Book

漫画 / 同人志条目，四个榜单共用同一结构（19 → **20 个字段**，本次新增 `alias`）。

| 字段 | 类型 | 说明 | 示例 |
| --- | --- | --- | --- |
| `Bid` | int | 书籍 ID，也是封面图路径的一段 | `54485` |
| `Mode` | int | 内容类型：实测全年龄为 `1`、R18 为 `0` ⚠️ | `1` |
| `Bookname` | string | 书名 | `"腦洞學生會"` |
| `alias` | string | 别名 / 罗马音，**2026-10 新增**，样例多为空串 | `""` |
| `Description` | string | 简介，常见为空串 | `""` |
| `Author` | string | 作者，多人时以空格分隔 | `"むちまろ（无知麻吕）"` |
| `Pname` | string | 主角色，大量为占位符 `"未知"` | `"未知"` |
| `Ptag` | string | 标签，**空格分隔** | `"搞笑 校園 戀愛 日常 四格"` |
| `Otag` | string | 来源类型 | `"原創"` |
| `Time` | int | 更新时间（unix 秒） | `1792832711` |
| `Views` | int | 浏览量 | `6364` |
| `Favorites` | int | 收藏数 | `1120` |
| `F` | bool | 当前用户是否已收藏 | `false` |
| `Len` | int | 长度 / 话数，取值随内容类型差异极大 ⚠️ | `1` 或 `78` |
| `Adult` | int | `0` 全年龄 / `1` R18 | `0` |
| `Status` | int | `0` 连载 / `1` 完结 | `0` |
| `publish_year` | string | 发布年份；**常见空串**，不是 null | `"2022"` |
| `RatingSUM` | number | 平均评分（并非求和，命名有误导性），无评分时为 `0` | `10` |
| `RatingCount` | int | 评分人数，无评分时为 `0` | `43` |
| `RatingBayes` | number | 实测恒为 `0`，疑似未启用 | `0` |

**字段实测备注**（2026-10-26，由 156 条榜单数据反推）：

- `Len` 不是「篇幅类型枚举」：全年龄作品多为 `0 / 1 / 2`，R18 作品从 `5` 一直到 `194`。更可能是「话数 / 长度」，但 `0` 的含义仍未确认 ⚠️。
- `Mode` 与 `Adult` 在本次抓取中完全一一对应（`Mode=1 ↔ Adult=0`，`Mode=0 ↔ Adult=1`），疑似同人志 / 连载漫画的分类，不要当作分级字段的替代品。
- `publish_year` 空串很普遍：`allow-adult=true` 的 80 本里 **80 本全为空**，全年龄里也有约一半为空。解析时别直接 `int()`。
- `RatingSUM` / `RatingCount` 同时为 `0` 表示「还没有人评分」，不是评分为 0。
- `Pname` 在新样例里几乎全是 `"未知"`，当成人名字段用会出错。
- `Ptag` 用空格分隔；`Stream.tags`（已下线）当年用逗号分隔。

### 封面图

接口**不返回**封面 URL，前端按下面的规律自己拼（实测可用）：

```text
https://img.noymanga.com/<Bid>/m1.webp
```

番剧封面在另一套域名 `stream.noyteam.online/<sid>/cover.webp`（随 `stream` 下线一起失效）。

## 失败分支

| 场景 | HTTP | 响应 |
| --- | --- | --- |
| 未登录 / Cookie 过期 | `200` | `{"status":"login"}` |
| 其他业务失败 | `200` | `{"status":"error"}`（未观察到触发条件 ⚠️） |
| 访问旧域名并 `curl -L` | `405` | 302 把 POST 降级成 GET 的结果 |

## 请求示例

```bash
BASE=https://noymanga.com

# 全年龄榜（务必显式带头，否则拿到的是 R18）
curl -s -X POST "$BASE/api/home" \
  -b "NOY_SESSION=xxxx" \
  -H "allow-adult: false" \
  -H "content-type: application/x-www-form-urlencoded"

# 对比两种分级的条目数与标签数
for lvl in false true both; do
  printf '%-6s ' "$lvl"
  curl -s -X POST "$BASE/api/home" -b "NOY_SESSION=xxxx" -H "allow-adult: $lvl" |
    python3 -c "import json,sys; d=json.load(sys.stdin); print({k: len(v) for k, v in d.items() if isinstance(v, list)}, d.get('status'))"
done
```

## 备注

- 无分页、无缓存参数，一次约 40 KB。
- 榜单条目数会变，`proportion` 尤其不稳定。
- `bulletin.text` 是运营文案，可能频繁变更，不要做字符串匹配。
- 首页同时会调 [`/api/v3/ads`](./ads.md) 拿广告位数据。
