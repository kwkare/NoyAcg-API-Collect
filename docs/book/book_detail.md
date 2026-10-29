# 漫画详情与评论

单部漫画的完整资料（简介、章节、售价、推荐）和评论。**这两个接口是 `GET`**，和社区那套 `POST` 不一样。

| 用途 | 端点 | 方法 |
| --- | --- | --- |
| 书籍详情 | `/api/v4/book/<bid>` | `GET` |
| 书籍评论（分页） | `/api/v4/comment/book/<bid>/comments?page=<n>` | `GET` |
| 阅读进度（未整理） | `/api/v4/sync/reading/<bid>` | `GET` |

| 项目 | 内容 |
| --- | --- |
| 鉴权 | Cookie `NOY_SESSION`，**必需**（未登录返回 `{"status":"login"}`） |
| 分级 | 请求头 `allow-adult` |
| 校验 | ✅ 2026-10-27 实测（Bid 54485 / 14623） |

> 书籍页路由是 `/manga/<bid>`（不是 `/book/`、`/comic/`，那几个都是 404）。
> 详情接口把**章节列表**和**首屏评论**都内联返回了，一次请求就能画出整页。

## 书籍详情

```http
GET /api/v4/book/54485
```

响应结构：

```json
{
  "book": {
    "info": { "Bid": 54485, "Bookname": "…", "…": "…" },
    "recommend": [ { "bid": 14623, "bookname": "…", "tags": "…", "views": 4806, "favorites": 522, "mode": true, "status": true } ],
    "translate": ""
  },
  "chapters": {
    "categories": [ { "id": 7, "name": "番外篇" }, { "id": 5, "name": "單話" }, { "id": 6, "name": "單行本" } ],
    "data": { "5": [ { "id": 503603, "name": "第01話", "count": 17, "sort": 0, "created_at": 1769535592 } ] }
  },
  "comment": { "count": 19, "data": [ { "cid": 1, "uid": 0, "…": "…" } ] },
  "points": { "book_price": "2", "user_balance": "1086.70" },
  "uid": 12345,
  "status": "ok"
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `book.info` | `Book` | 与 [首页榜单](../home.md#book) 同一个结构（20 个字段） |
| `book.recommend` | `Recommend[]` | 同类推荐，实测 6 条。字段是小写下划线风格，`mode` / `status` 是**布尔**值，和 `Book.Mode` / `Book.Status` 的整数不同 |
| `book.translate` | string | 实测为空串，用途未知 ⚠️ |
| `chapters.categories` | `{id,name}[]` | 章节分类（如 番外篇 / 單話 / 單行本） |
| `chapters.data` | `{ [categoryId]: Chapter[] }` | **以分类 id 为 key 的字典**，不是数组；`Chapter` = `{id,name,count,sort,created_at}` |
| `comment.count` | int | 评论总数（**不含**官方置顶评论，见下） |
| `comment.data` | `BookComment[]` | 首屏评论，实测 20 条（其中 1 条是官方置顶） |
| `points.book_price` | **string** | 阅读所需积分（`"2"`），免费书可能是 `"0"` |
| `points.user_balance` | **string** | 当前用户积分余额（明文，截图前打码） |
| `uid` | int | 当前登录用户 UID |

### 官方置顶评论

`comment.data` 的第一条常常是官方公告（`uid: 0`、`username: "Noriya (NoyAcg Support)"`、`area: "官方公告"`），
它**不计入** `comment.count`。实测 `count = 19` 而 `data` 有 20 条。

### 章节字典

同一本书的全部章节都在这一个响应里（实测 228 话：番外篇 26 / 單話 190 / 單行本 12），不需要再请求章节接口。
`Chapter.count` 是这一话的**页数**；`sort` 是分类内排序。

## 书籍评论

```http
GET /api/v4/comment/book/54485/comments?page=1
```

```json
{
  "data": {
    "comments": [ { "cid": 145683, "uid": 329182, "bid": 54485, "content": "…", "replies": [] } ],
    "page": 1,
    "over": true,
    "top_count": 17
  },
  "status": "ok"
}
```

| 字段 | 说明 |
| --- | --- |
| `data.comments` | 评论列表，结构与[帖子评论](../community/post_detail.md#评论对象comment)一致，但**主键字段叫 `cid`**（帖子评论是 `rid`） |
| `data.over` | 是否已到最后一页 |
| `data.page` | 当前页码 |
| `data.top_count` | 语义未确认 ⚠️：实测这本书返回 `17`，不是「置顶条数」 |

评论里的 `[noygirl:yeah]` 是表情包代码，`replies` 是楼中楼。

## 评分是 10 分制

`Book.RatingSUM`（首页榜单里的字段）是 **10 分制平均分**，不是 5 分制：

| 接口值 | 站点界面显示 |
| --- | --- |
| `RatingSUM: 10`、`RatingCount: 47` | `5.0 (47 人)` |
| `RatingSUM: 9.7`、`RatingCount: 14` | `4.8 (14 人)` |

即前端把 `RatingSUM` **除以 2** 再当 5 星展示。`RatingCount` 是评分人数；为 `0` 时 `RatingSUM` 也是 `0`（表示还没人评分）。

## 示例

```bash
BASE=https://noymanga.com

# 详情（GET 也要带 Cookie）
curl -s "$BASE/api/v4/book/54485" -b "NOY_SESSION=xxxx" |
  jq '{name: .book.info.Bookname, chapters: (.chapters.data | map_values(length)), comments: .comment.count}'

# 评论第一页
curl -s "$BASE/api/v4/comment/book/54485/comments?page=1" -b "NOY_SESSION=xxxx" |
  jq '.data | {page, over, count: (.comments | length)}'
```

脱敏样例：[`fixtures/book-detail-sample.json`](../../fixtures/book-detail-sample.json)、
[`fixtures/book-comments-sample.json`](../../fixtures/book-comments-sample.json)。

## 相关

- 书籍字段：[home.md](../home.md#book)
- 评论结构：[post_detail.md](../community/post_detail.md#评论对象comment)
- 消息里的书籍评论回覆：[messages.md](../user/messages.md)
