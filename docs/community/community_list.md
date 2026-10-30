# 社区帖子列表

社区首页 / 排序切换用的列表接口。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/v3/community_list` |
| Content-Type | `application/x-www-form-urlencoded` |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ✅ 2026-10-27 实测 |

## 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| `page` | int | 是 | 页码，从 `1` 开始 | `1` |
| `type` | string | 否 | 排序 / 范围，见下表 | `new` |
| `filter` | string | 否 | 过滤条件，实测空串；其它取值未验证 ⚠️ | `""` |

### `type` 取值（实测）

| 值 | 行为 |
| --- | --- |
| `new` | 最新（按发帖时间倒序） |
| `latest` | 与 `new` 结果一致（疑似别名） |
| `like` | 按点赞 / 热门排序，条目数会少一条（置顶帖被排除） |
| `""`（空） | 等同 `new` |

## 响应

```json
{
  "info": [ { "id": 78930, "title": "图", "…": "…" } ],
  "len": 70086,
  "over": false,
  "top": true,
  "status": "ok"
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `info` | `Post[]` | 当前页帖子，实测每页 40~42 条（第 1 页会多带一条置顶） |
| `len` | int | **近似全站帖子总数**（不是本页条数，也不是页数）。实测第 1 页 `70107`、后续页 `70106`，`type=like` 也比 `new` 少 1 —— 差值来自置顶帖的处理，**别拿它做精确分页计算** |
| `over` | bool | 是否已到末页 |
| `top` | bool | 是否包含置顶帖 |
| `status` | string | `ok` |

> `len` 这个命名很容易误用：它是总量统计而不是「剩余条数」，而且会因为置顶 / 筛选浮动一两条。**判断翻页结束用 `over`。**
>
> 另外第 1 页的 `info[0]` 是置顶帖（实测 `id=41029`，发布时间远早于其它条目），后续页不会重复出现。

## 帖子对象（Post）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | int | 帖子 ID（详情 / 评论 / 点赞都用它） |
| `uid` | int | 作者 UID |
| `username` | string | 作者昵称 |
| `avatar` | string | 作者头像相对路径 |
| `title` | string | 标题 |
| `content` | string | 正文（表情包是 `[noygirl:yeah]` 这种代码文本，见 [stickers.md](./stickers.md)） |
| `image` | string[] | 图片路径数组，元素形如 `image/<file>.webp`；无图时为空数组。**图床有防盗链**：直接抓 URL 会 403，必须带 `Referer: https://noymanga.com/` |
| `time` | int | 发帖时间（unix 秒） |
| `expired` | int | **过期时间**，实测 = `time + 7776000`（正好 **90 天**）。到期后帖子**不会被删除**，但会从过滤 / 搜索结果里隐藏（站内用户实测，2026-10-27） |
| `area` | string | 发帖地区，由服务端根据 IP 判定（如 `Japan`），非用户自填 |
| `platform` | string | 客户端来源，`web` / `android` |
| `like` | int | 点赞数 |
| `reply` | int | 回复数 |
| `is_like` | bool | 当前用户是否点过赞 |
| `su` | int | 语义未知，样例恒为 `0` ⚠️ |
| `spoiler` | string | **需要模糊的图片下标**，逗号分隔（如 `"0,1,2,3,4,5"`）；空串代表不模糊。由服务端判定，发帖时无法指定 |
| `edit` | int | **最后编辑时间戳**（unix 秒），`0` = 从未编辑（实测：编辑一次后变成当前时间） |

脱敏样例：[`fixtures/community-list-sample.json`](../../fixtures/community-list-sample.json)。

## 示例

```bash
BASE=https://noymanga.com

# 最新一页
curl -s -X POST "$BASE/api/v3/community_list" \
  -b "NOY_SESSION=xxxx" \
  -d "page=1&type=new&filter=" |
  python3 -c "
import json, sys
d = json.load(sys.stdin)
print('总数', d['len'], '本页', len(d['info']), '末页', d['over'])
for p in d['info'][:5]:
    print(p['id'], p['time'], p['title'][:24])
"
```

## 备注

- 列表里拿不到评论内容，要看评论得请求详情（[post_detail.md](./post_detail.md)）。
- 想找自己刚发的帖子：用 `type=new` 翻第一页基本就能看到。
- 帖子 90 天后过期（`expired`）。过期不等于删除：链接仍可访问，只是不再出现在列表 / 搜索结果里。
