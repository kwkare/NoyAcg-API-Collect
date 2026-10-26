# 首页聚合数据

返回首页一次渲染所需的全部数据：公告、四个榜单、番剧推荐、标签。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/home` |
| Content-Type | `application/x-www-form-urlencoded`（无请求体，`Content-Length: 0`） |
| 返回 | `application/json;charset=utf-8` |
| 鉴权 | Cookie `NOY_SESSION`，**必需** |
| 分级 | 请求头 `allow-adult` |
| 校验 | 🟡 鉴权分支 2026-10-26 实测；字段沿用 2026-03 抓包 |

## 请求头

| 字段 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- |
| `Cookie` | 是 | `NOY_SESSION=xxxx` | 未带或失效时返回 `{"status":"login"}`，HTTP 仍是 `200` |
| `allow-adult` | 否 | `false` | 见下表；不传时的默认行为未确认 ⚠️ |
| `Origin` / `Referer` | 否 | `https://noymanga.com` | 浏览器会自动带，脚本可以不带（实测无影响） |

### `allow-adult` 取值

| 值 | 返回内容 |
| --- | --- |
| `true` | 仅 R18 |
| `false` | 仅全年龄 |
| `both` | 全部 |

> 这是**按请求生效**的，不是账户级设置：同一个 Cookie 换个头就能拿到不同分级的数据。抓包时如果发现榜单对不上，先看这个头。

## 响应结构

| 字段 | 类型 | 说明 | 样例条目数 |
| --- | --- | --- | --- |
| `bulletin` | `Bulletin` | 顶部公告（前端目前已隐藏） | 1 |
| `favDay` | `Book[]` | 日收藏榜 | 20 |
| `readDay` | `Book[]` | 日阅读榜 | 20 |
| `fs` | `Book[]` | 推荐位，具体排序规则未确认 ⚠️ | 20 |
| `proportion` | `Book[]` | 高质 / 编辑推荐，规则未确认 ⚠️ | 19 |
| `stream` | `Stream[]` | 番剧 / 流媒体推荐 | 10 |
| `tags` | `string[]` | 首页可用标签 | 9 |
| `status` | `string` | `ok` / `error` / `login` | — |

条目数取自 2026-03 的样例，只用来表示数量级，不是固定长度。完整样例见 [`fixtures/home.json`](../fixtures/home.json)（79 本书 + 10 部番剧，已脱敏，只含公开榜单字段）。

## Bulletin

| 字段 | 类型 | 说明 | 示例 |
| --- | --- | --- | --- |
| `text` | string | 公告文案 | `"點擊廣告，救救Noy！"` |
| `show` | bool | 是否展示 | `true` |

## Book

漫画 / 轻小说条目，四个榜单共用同一结构。

| 字段 | 类型 | 说明 | 示例 |
| --- | --- | --- | --- |
| `Bid` | int | 书籍 ID | `15969` |
| `Mode` | int | 内容类型，样例中恒为 `1` ⚠️ | `1` |
| `Bookname` | string | 书名 | `"敗北女角太多了！"` |
| `Description` | string | 简介，常见为空串 | `""` |
| `Author` | string | 作者，可能含空格分隔的多人 | `"いたち 雨森たきび"` |
| `Pname` | string | 主角色，大量为占位符 `"未知"` | `"綾小路清隆"` |
| `Ptag` | string | 标签，**空格分隔** | `"戀愛 校園 輕小說"` |
| `Otag` | string | 来源类型 | `"原創"` |
| `Time` | int | 更新时间（unix 秒） | `1772638599` |
| `Views` | int | 浏览量 | `10522` |
| `Favorites` | int | 收藏数 | `1170` |
| `F` | bool | 当前用户是否已收藏 | `false` |
| `Len` | int | 篇幅类型，出现过 `0 / 1 / 2`，语义未确认 ⚠️ | `1` |
| `Adult` | int | `0` 全年龄 / `1` R18 | `0` |
| `Status` | int | `0` 连载 / `1` 完结 | `1` |
| `publish_year` | string | 发布年份；**可能为空串**，不是 null | `"2024"` |
| `RatingSUM` | float | 平均评分（并非求和，命名有误导性） | `9.8` |
| `RatingCount` | int | 评分人数 | `65` |
| `RatingBayes` | float | 样例中恒为 `0`，疑似未启用 ⚠️ | `0` |

字段实测备注（由 `fixtures/home.json` 反推，原文档未覆盖）：

- `Len`：样例值域 `{0, 1, 2}`，早期文档只写了 `1 / 2`。
- `publish_year`：可为 `""`，解析时别直接 `int()`。
- `Pname`：79 本里 72 本是 `"未知"`，当成人名字段用会出错。
- `Ptag` 用空格分隔，`Stream.tags` 用逗号分隔——两者不一致，别写同一个 split。

## Stream

番剧 / 流媒体条目。

| 字段 | 类型 | 说明 | 示例 |
| --- | --- | --- | --- |
| `sid` | int | 剧集 ID | `75` |
| `name` | string | 剧名 | `"咒術迴戰 死滅迴游 前篇"` |
| `des` | string | 剧情简介 | `"經歷了澀谷事變…"` |
| `tags` | string | 标签，**逗号分隔** | `"動作,冒險,奇幻"` |
| `pages` | string | 可观看集数，逗号分隔的集号 | `"1,2,3,4,5"` |
| `type` | int | 类型标识，样例中恒为 `0` ⚠️ | `0` |
| `count` | int | 总集数 | `9` |
| `time` | int | 创建时间（unix 秒） | `1768034642` |
| `up_time` | int | 最后更新（unix 秒） | `1772806735` |
| `f` | bool | 当前用户是否收藏（注意是小写 `f`） | `false` |
| `views` | int | 播放量 | `989` |
| `favorites` | int | 收藏数 | `41` |

> `Book` 用大写字段名（`F`、`Views`），`Stream` 用小写（`f`、`views`），这是服务端原样返回，不是笔误。

## 失败分支

| 场景 | HTTP | 响应 |
| --- | --- | --- |
| 未登录 / Cookie 过期 | `200` | `{"status":"login"}` |
| 其他业务失败 | `200` | `{"status":"error"}`（未观察到触发条件 ⚠️） |
| 直接访问旧域名并用 `-L` 跟随 | `405` | 302 把 POST 降级成 GET 后的结果 |

## 请求示例

```bash
BASE=https://noymanga.com

# 全年龄榜
curl -s -X POST "$BASE/api/home" \
  -b "NOY_SESSION=xxxx" \
  -H "allow-adult: false" \
  -H "content-type: application/x-www-form-urlencoded"

# 只看 R18，顺便看看结构有没有变化
curl -s -X POST "$BASE/api/home" \
  -b "NOY_SESSION=xxxx" \
  -H "allow-adult: true" \
  -H "content-type: application/x-www-form-urlencoded" |
  python3 -c "import json,sys; d=json.load(sys.stdin); print({k: len(v) if isinstance(v, list) else v for k, v in d.items()})"
```

## 备注

- 无分页、无缓存参数；一次返回约 40 KB JSON。
- `bulletin.text` 是运营活动文案，可能频繁变更，不要做字符串匹配。
- 榜单每次返回的条目数不保证一致，翻页/无限滚动由其他接口负责（未整理 🚧）。
