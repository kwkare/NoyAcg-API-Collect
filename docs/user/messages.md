# 讯息中心（评论回覆 / 社區回覆 / 系統訊息）

站内消息页 `/user/message` 的三个 tab，各自对应 `get_msg` 的一个 `type`。

| 用途 | 端点 |
| --- | --- |
| 未读计数 | `POST /api/v4/msg/count` |
| 消息列表 | `POST /api/v3/get_msg`（`type` 区分三类） |
| 楼中楼（帖子评论的回复） | `POST /api/v4/community/post/<id>/comment/<rid>/replies` → 见 [post_detail.md](../community/post_detail.md) |

| 项目 | 内容 |
| --- | --- |
| Content-Type | `application/x-www-form-urlencoded` |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ✅ 2026-10-27 实测（只读） |

## 一、未读计数

```http
POST /api/v4/msg/count
```

```json
{
  "count": {
    "all": 0,
    "sys_msg": 0,
    "community_reply": 0,
    "comment_reply": 0
  },
  "status": "ok"
}
```

| 字段 | 说明 |
| --- | --- |
| `count.all` | 未读总数 |
| `count.comment_reply` | 评论回覆未读（书籍评论的回复） |
| `count.community_reply` | 社區回覆未读（帖子回复） |
| `count.sys_msg` | 系統訊息未读 |

前端就是靠这个接口在导航栏挂红点，轮询成本很低。

## 二、消息列表

```http
POST /api/v3/get_msg
page=1&type=community_reply&v=3
```

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `page` | 是 | 页码，从 `1` 开始 |
| `type` | 是 | `reply`（評論回覆）/ `community_reply`（社區回覆）/ `sysmsg`（系統訊息） |
| `v` | 是 | 固定 `3`（前端写死，含义未确认 ⚠️） |

响应的**顶层 key 跟着 `type` 走**，所以三个 type 是三种结构。

### type=reply（评论回覆）

别人回复了**你在书籍下的评论**。

```json
{
  "reply": {
    "book": { "15970": { "Bid": 15970, "Bookname": "…" } },
    "comment": [
      {
        "cid": 91290, "uid": 186894, "bid": 15970,
        "username": "…", "avatar": "", "avatarUrl": "avatar/186894-<sha>.webp",
        "area": "China mainland", "reply": 91263, "reply_text": "…",
        "platform": "android", "time": 1757223929, "content": "…"
      }
    ],
    "commentLen": 0,
    "count": 2
  },
  "status": "ok"
}
```

| 字段 | 说明 |
| --- | --- |
| `reply.book` | **书籍字典**，key 是 `Bid` 字符串；条目是精简版 `Book`（`Bid` / `Bookname` / `Time` / `Views` / `Favorites` / `Mode`），书被删时给 `{Bid:0, Bookname:"Deleted", …}` |
| `reply.comment` | 回复列表 |
| `reply.comment[].cid` | 这条回复的评论 ID（对应书籍评论，不是帖子） |
| `reply.comment[].bid` | 所属书籍 ID，用来去 `reply.book` 里查书名 |
| `reply.comment[].uid` / `username` / `avatarUrl` | 回复者 |
| `reply.comment[].reply` | 被回复的评论 ID |
| `reply.comment[].reply_text` | 被回复内容节选 |
| `reply.comment[].area` / `platform` / `time` | 地区 / 来源（`android` 居多）/ 时间 |
| `reply.comment[].content` | 回复正文 |
| `reply.commentLen` | 疑似**未读数** ⚠️ |
| `reply.count` | 该类消息总数（实测 2） |

### type=community_reply（社區回覆）

帖子下的回复动态。

```json
{
  "community_reply": {
    "community": { "78930": { "id": 78930, "title": "图", "…": "…" } },
    "community_reply": [
      {
        "rid": 460483, "uid": 38354, "cid": 78930,
        "username": "…", "avatar": "", "avatarUrl": "avatar/38354-<sha>.webp",
        "area": "Japan", "reply": -1, "reply_text": "",
        "platform": "", "time": 1793030863, "content": "…"
      }
    ],
    "community_reply_len": 0,
    "count": 1399
  },
  "status": "ok"
}
```

| 字段 | 说明 |
| --- | --- |
| `community_reply.community` | **帖子字典**，key 是帖子 `id` 字符串；条目是精简版 `Post`（`id` / `title` / `content` / `time` / `image` 等），帖子被删时给 `{title:"Deleted", content:"Undefined"}` |
| `community_reply.community_reply` | 回复列表，实测每页 80 条 |
| `community_reply.community_reply[].rid` | 回复的评论 ID |
| `…[].cid` | 所属帖子 ID（去 `community` 里查标题） |
| `…[].reply` | `-1` = 顶层回复；否则是父评论 `rid` |
| `…[].reply_text` | 父评论节选（顶层为空串） |
| `…[].content` | 回复正文 |
| `…[].avatar` / `avatarUrl` | `avatar` 恒为空串，头像路径在 **`avatarUrl`** |
| `community_reply_len` | 疑似**未读数** ⚠️（实测 0） |
| `count` | 总数（实测 1399） |

> ⚠️ 语义未坐实：返回的 80 条里既有自己的回复，也有别人的新回复，覆盖 14 个帖子（`77433`–`78930`），看起来是「我参与过的帖子的回复流」而不是「别人回复我」。三个 type 里只有这个的数据量大，做客户端时别按「未读消息」直接呈现。

### type=sysmsg（系統訊息）

```json
{ "sysmsg": { "count": 0, "len": 0, "msg": [] }, "status": "ok" }
```

实测该账号没有系统消息（`msg` 为空数组），所以**消息条目的字段未知** ⚠️。结构上 `msg` 是数组，`count` / `len` 与其它两类同义。

## 已实测的边界

- 三类都是「字典 + 列表」结构：把关联对象（书 / 帖子）单独放一个 map，避免重复，客户端要自己 join。
- 列表**不返回**已读状态字段，已读/未读只体现在 `*_len` 和 `/api/v4/msg/count`。
- 没找到「标记已读」的接口（前端 bundle 里只有 `get_msg` 和 `msg/count`）⚠️——推测打开列表即视为已读。
- 分页用 `page`，是否支持 `over` 之类的结束标记未验证 ⚠️。

## 示例

```bash
BASE=https://noymanga.com

# 未读数
curl -s -X POST "$BASE/api/v4/msg/count" -b "NOY_SESSION=xxxx" | jq .count

# 社区回覆第一页（80 条）
curl -s -X POST "$BASE/api/v3/get_msg" -b "NOY_SESSION=xxxx" \
  -d "page=1&type=community_reply&v=3" |
  python3 -c "
import json, sys
d = json.load(sys.stdin)['community_reply']
posts = d['community']
print('总数', d['count'], '本页', len(d['community_reply']))
for r in d['community_reply'][:5]:
    title = posts.get(str(r['cid']), {}).get('title', '?')
    print(f\"{r['username']} → 《{title[:16]}》: {r['content'][:20]}\")
"
```

Python 版：

```python
TYPES = {"comment": "reply", "community": "community_reply", "system": "sysmsg"}


def fetch_messages(session, base, kind: str, page: int = 1):
    data = session.post(f"{base}/api/v3/get_msg",
                        data={"page": page, "type": TYPES[kind], "v": 3}).json()
    return data[TYPES[kind]]
```

## 相关

- 帖子与评论：[post_detail.md](../community/post_detail.md)
- 帖子列表：[community_list.md](../community/community_list.md)
