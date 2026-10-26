# 帖子详情与评论

一篇帖子的完整内容（正文 + 图片 + 评论），以及**发评论 / 回复**。

| 用途 | 端点 |
| --- | --- |
| 帖子详情 | `POST /api/v4/community/post/<id>` |
| 评论列表 | `POST /api/v4/community/post/<id>/comments` |
| 发评论 / 回复 | `POST /api/v4/community/post/<id>/reply` |
| 楼中楼列表 | `POST /api/v4/community/post/<id>/comment/<rid>/replies`（✅ 已实测） |

| 项目 | 内容 |
| --- | --- |
| Content-Type | `application/x-www-form-urlencoded` |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ✅ 2026-10-27 实测（含真发一条评论） |

## 一、帖子详情

```http
POST /api/v4/community/post/78930
```

响应结构：

```json
{
  "data": {
    "post": { "id": 78930, "title": "图", "…": "…" },
    "comments": [ { "rid": 460483, "content": "…", "…": "…" } ],
    "comment_count": 1,
    "top_count": 1,
    "uid": 12345
  },
  "status": "ok"
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `data.post` | `Post` | 帖子本身，字段同 [community_list.md](./community_list.md#帖子对象post) |
| `data.comments` | `Comment[]` | 评论（实测直接带出，首屏约 40 条） |
| `data.comment_count` | int | 评论总数 |
| `data.top_count` | int | 置顶评论数 |
| `data.uid` | int | 当前登录用户 UID（用于判断「我的帖子/评论」） |

注意详情里的 `data.uid` 是**当前登录用户**，不是帖子作者（作者在 `data.post.uid`）。

## 二、评论列表（分页）

```http
POST /api/v4/community/post/78930/comments
page=1
```

```json
{
  "data": {
    "comments": [ { "rid": 460483, "…": "…" } ],
    "page": 1,
    "over": true,
    "top_count": 1
  },
  "status": "ok"
}
```

分页判断用 `data.over`；`comments` 里每条自带 `replies`（楼中楼）与 `reply_more`（还有更多回复）。

## 二·五、楼中楼列表

```http
POST /api/v4/community/post/41029/comment/445567/replies
page=1
```

```json
{
  "data": {
    "count": 6,
    "over": true,
    "page": 1,
    "replies": [ { "rid": 456401, "reply_id": 450225, "root_id": 445567, "…": "…" } ]
  },
  "status": "ok"
}
```

| 字段 | 说明 |
| --- | --- |
| `data.count` | 该根评论下的回复总数（与 `comments[].reply_num` 一致） |
| `data.page` / `data.over` | 分页信息 |
| `data.replies` | 回复列表，元素结构与评论对象完全相同（见下表） |

实测（根评论 `445567`，6 条回复）：

- 回复**按时间倒序**返回（最新在前）；
- `root_id` 恒为该根评论的 `rid`，`reply_id` 指向**被回复的那一条**（可能不等于 `root_id`）；
- 楼中楼通常已经在详情接口的 `comments[].replies` 里内联带出（实测 6/6 全带），这个接口主要用于「加载更多」。

## 三、发评论 / 回复

```http
POST /api/v4/community/post/<id>/reply
reply_id=-1
text=pixiv: 133916454, 135484571
platform=web
hide_ip=false
```

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `reply_id` | int | 是 | `-1` = 发顶层评论；填某个评论的 `rid` = 回复该评论（楼中楼） |
| `text` | string | 是 | 正文，支持表情包代码 `[noygirl:yeah]` 和 `NID<id>` 书籍引用 |
| `platform` | string | 是 | `web` / `android` |
| `hide_ip` | string | 是 | 前端固定传 `"false"`；实测**不影响**返回内容（评论对象里根本没有 `ip` 字段） |

响应：

```json
{ "status": "ok" }
```

**不返回评论 ID**，要确认得再拉一次列表。

## 四、评论对象（Comment）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `rid` | int | 评论 ID（回复别人时作为 `reply_id`） |
| `cid` | int | 所属帖子 ID |
| `uid` / `username` / `avatar` | int / string / string | 作者 |
| `content` | string | 正文（表情包为代码文本） |
| `reply_id` | int | 顶层评论为 `-1` |
| `root_id` | int | 楼中楼时指向根评论的 `rid`；顶层为 `0` |
| `reply_uid` / `reply_username` / `reply` | int / string / string | 被回复者信息与原文摘要（顶层为空） |
| `area` | string | 地区（服务端按 IP 判定，如 `Japan`） |
| `time` / `updated_at` | int | 发送 / 编辑时间（unix 秒） |
| `platform` | string | `web` / `android` |
| `show_badge` | string | 佩戴徽章缩略图 URL，**逗号拼接**，顺序与 `/api/badge` 的 `show` 一致 |
| `su` | int | 语义未知 ⚠️ |
| `replies` | `Comment[]` | 楼中楼回复（可能只带前几条） |
| `reply_more` | bool | 楼中楼是否还有更多 |
| `reply_num` | int | 楼中楼回复总数 |

脱敏样例：[`fixtures/post-detail-sample.json`](../../fixtures/post-detail-sample.json)。

## 已实测的边界

- 顶层评论：`reply_id=-1`、`root_id=0`；发完帖子 `reply` 计数 `0 → 1`。
- 评论**不暴露 IP**，只有粗粒度 `area`。
- 帖子正文只写一个表情包代码（如 `[noygirl:yeah]`）完全可以，渲染成图片。
- 评论/帖子都可以含多行文本（`text` 直接放 `\n` 未测 ⚠️）。

## 示例

```bash
BASE=https://noymanga.com

# 看帖 + 评论
curl -s -X POST "$BASE/api/v4/community/post/78930" -b "NOY_SESSION=xxxx" |
  python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(d['post']['title'], d['comment_count']); [print('-', c['username'], c['content'][:40]) for c in d['comments'][:5]]"

# 发一条顶层评论（写操作）
curl -s -X POST "$BASE/api/v4/community/post/78930/reply" \
  -b "NOY_SESSION=xxxx" \
  -d "reply_id=-1" \
  --data-urlencode "text=测试评论" \
  -d "platform=web" -d "hide_ip=false"
```

## 五、编辑帖子

```http
POST /api/v3/edit_community_post
id=78930
title=图
content=[noygirl:yeah][noygirl:haha]
```

响应：`{"status":"ok"}`，**不返回帖子内容**，要回读详情确认。

实测（把自己的帖子正文从一个表情包改成两个）：

| 字段 | 编辑前 | 编辑后 |
| --- | --- | --- |
| `content` | `[noygirl:yeah]` | `[noygirl:yeah][noygirl:haha]` |
| `edit` | `0` | `1793033067`（**当前时间戳**） |
| `time`（发布时间） | `1793030753` | 不变 |
| `image` / `spoiler` | 6 张 / `"0,1,2,3,4,5"` | 不变 |

结论：

- `edit = 0` 表示**从未编辑**，否则是**最后编辑时间**——这解释了列表里那个语义不明的字段；
- 只能改 `title` / `content`，**改不了图片和 `spoiler`**；
- 编辑不会把帖子顶到前面（`time` 不变）。

## 六、点赞

```http
POST /api/v3/community_like
cid=78930
```

```json
{ "is_like": true, "status": "ok" }
```

- **开关式**：再调一次就取消点赞，返回 `{"is_like":false,"status":"ok"}`；
- 帖子对象的 `like` 计数随之 `0 → 1 → 0`，`is_like` 同步翻转；
- ⚠️ **不校验 `cid`**：传 `999999999` 或不传 `cid` 都返回 `{"is_like":true,"status":"ok"}`，但目标帖子的 `like` / `is_like` **没有任何变化**（比 `set_badge_show` 干净，不会污染数据）。所以别用返回值判断「点赞成功」，要么回读帖子，要么信任自己没传错 ID。

## 相关

- 发帖：[send_community.md](./send_community.md)
- 帖子列表：[community_list.md](./community_list.md)
