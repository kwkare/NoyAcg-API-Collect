# CHANGELOG

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)；本项目是文档项目，版本号取「整理批次（年.月.日）」而不是语义化版本。

## 2026.10.27-c — 编辑帖子与点赞实测

两个之前只有「从 bundle 挖到的参数」的写接口，现在都跑通了。

### 新增实测结论

- **`POST /api/v3/edit_community_post` 升 ✅**（`{id, title, content}`）：响应只有 `{"status":"ok"}`，要回读详情确认。实测把帖子正文从一个表情包改成两个：
  - `content` 更新成功，`time`（发布时间）**不变**、不会把帖子顶上去；
  - `edit` 字段由 `0` 变成当前时间戳 → 证实 `Post.edit` 是**最后编辑时间**、`0` 表示从未编辑；
  - **改不了图片和 `spoiler`**（实测 6 张图与模糊下标原样保留）。
- **`POST /api/v3/community_like` 升 ✅**（`{cid}`）：返回 `{"is_like":bool,"status":"ok"}`，是 **toggle**；`like` 计数与 `is_like` 同步 `0→1→0`。
  - ⚠️ **不校验 cid**：传 `999999999` 或不传都返回 `is_like:true`，但目标帖子毫无变化（不像 `set_badge_show` 会写脏数据）。别用返回值判断成功，回读帖子或自己保证 ID 正确。

### 变更

- `docs/community/post_detail.md` 新增「编辑帖子」「点赞」两节，含前后对比表。
- `docs/community/community_list.md`：`Post.edit` 语义从「未确认」改为「最后编辑时间戳」。
- `README.md` 状态表补两行，`openapi.yaml` 补 2 个 path（`LikeResult` schema）。
- `fixtures/like-result.json` 新增。

## 2026.10.27-b — 浏览与讯息实测

把「看」的部分补齐：楼中楼、消息中心三类讯息。

### 新增实测结论

- **楼中楼 `POST /api/v4/community/post/<id>/comment/<rid>/replies` 升 ✅**：`{data:{count, over, page, replies[]}}`，回复按时间**倒序**，`root_id` 恒为根评论、`reply_id` 指向被回复的那一条（两者可以不等）。内容通常已内联在详情接口的 `comments[].replies` 里，这个接口主要用于「加载更多」。
- **未读计数 `POST /api/v4/msg/count`**：`{count:{all, sys_msg, community_reply, comment_reply}, status}`，导航栏红点就用它。
- **讯息列表 `POST /api/v3/get_msg`**：`{page, type, v:3}`，`type` 三态对应消息页三个 tab：
  - `reply`（評論回覆）→ `{reply:{book:{bid:Book}, comment:[…], commentLen, count}}`，书籍单独放 map 里；
  - `community_reply`（社區回覆）→ `{community_reply:{community:{cid:Post}, community_reply:[…80 条/页], community_reply_len, count}}`；
  - `sysmsg`（系統訊息）→ `{sysmsg:{count, len, msg:[]}}`（该账号无系统消息，条目字段未知）。
- 三类消息条目里的头像路径字段是 **`avatarUrl`**，`avatar` 恒为空串；`reply` / `reply_text` 分别是被回复对象 ID 与内容节选。
- 没找到「标记已读」接口，`*_len` 疑似未读数。

### 新增文档

- `docs/user/messages.md`：讯息中心三个 tab 的完整结构、字典 join 方式、语义存疑点。
- `docs/community/post_detail.md` 补「楼中楼列表」章节。

### 新增 fixtures

- `comment-replies-sample.json`、`msg-count.json`、`msg-comment-reply-sample.json`、`msg-community-reply-sample.json`（uid / 用户名 / 头像全部打码，正文替换为占位文本）

## 2026.10.27 — 写操作链路实测（发帖 / 评论 / 签到）

在账号所有者确认后，把「会产生真实内容」的接口也跑了一遍，全部为一次真实操作 + 回读验证。

### 新增实测结论

- **发帖 `POST /api/v3/send_community` 升 ✅**：标题「图」+ 6 张图 + 正文只放一个表情包代码（`[noygirl:yeah]`）成功发布，`image` 数组元素为 `image/<Uhash>-<sha256>.webp`。响应只有 `{"status":"ok"}`，**不返回帖子 ID**。
- **模糊（`spoiler`）由服务端判定**：上传时带 `allow-adult: false`、发帖请求里没有任何成人向参数，6 张图仍被标成 `"spoiler":"0,1,2,3,4,5"`。客户端无法手动指定或取消。
- **帖子 90 天过期**：`expired = time + 7776000`（正好 90 天）。
- **表情包没有 API**：4 组 57 个硬编码在前端 bundle，图片是静态资源 `/stickers/<file>`，正文里写 `[noygirl:yeah]` 这类代码文本即可；同一正则还解析 `NID<id>` 书籍引用。
- **签到 `POST /api/v4/signin/sign`**：空表单，成功 `{continuous, msg:"success", status:200}`，**积分 +1**；同日重复签到返回 `{msg:"Please do not sign in too frequently", status:500}`（HTTP 仍 200）。
- **签到每天 00:00（UTC+8）刷新**：跨零点实测 `record.today` 由 `true` → `false` → 签到后 `true`；未签到时顶层 `continuous` 是 `-1`，`data[].weekday` 为 1（周一）…7（周日）。
- **评论 `POST /api/v4/community/post/<id>/reply` 升 ✅**：`reply_id=-1` 为顶层评论（`root_id=0`），响应只有 `{"status":"ok"}`、**不返回评论 ID**；回读确认 `reply 0 → 1`。评论对象**不含 IP**，只有粗粒度 `area`。

### 新增文档

- `docs/community/community_list.md`：`POST /api/v3/community_list`（`type` 实测 `new` / `latest` / `like` / 空；`len` 是**全站帖子总数**，翻页看 `over`）。
- `docs/community/post_detail.md`：详情 / 评论列表 / 发评论 / 楼中楼，含 `Post` 与 `Comment` 完整字段表。
- `docs/community/stickers.md`：表情包代码全表（Noy Girl 12 / SB 11 / Kimeemaru 23 / Vik 11）与 `NID` 引用机制。
- `fixtures/` 新增 `signin-success.json`、`signin-record-pending.json`、`signin-too-frequent.json`、`community-list-sample.json`、`post-detail-sample.json`，并更新 `signin-record.json`。

### 变更

- `docs/task/signin.md` 重写：补执行签到、刷新时间、`continuous=-1` 的坑、积分奖励、重复签到错误。
- `docs/community/upload_image.md` 升 ✅：4.66 MB 原图照收、统一转 `.webp`、6 张约 42 秒。
- `README.md` 状态表与「未收录」清单同步（`edit_community_post` / `community_like` 已挖到参数但未实测）。

### 隐私说明

本次实测涉及的真实内容（帖子、评论）已经公开发布；所有 fixture 中的 Uid / 用户名 / 头像 / IP / 图床真实文件名均已打码。

## 2026.10.26-b — 登录态实测校正

拿到可用会话后把全部端点重新过了一遍（只读，未触发任何写操作），推翻了上游文档里几条关键结论。

### 修正（有实测支撑）

- **`/api/home` 不再返回 `stream`**：连续 7 次请求都没有这个 key，前端仍写 `f.stream ?? []`，所以首页「動畫」区块是静默隐藏。旧快照（含 `stream`）保留在 `fixtures/home.json`。
- **`allow-adult` 缺省值 = `true`**：不传请求头时响应与 `allow-adult: true` 逐字节一致（80 本、全部 R18、13 个标签）。原文档只写了三个取值，没写默认行为。
- **`Book.Len` 不是「篇幅类型 1/2」**：实测 R18 作品从 `5` 到 `194`，全年龄多为 `0/1/2`。改为「长度 / 话数，语义待确认」。
- **`Book.Mode` 与 `Adult` 一一对应**（`Mode=1 ↔ Adult=0`、`Mode=0 ↔ Adult=1`），原文档写「内容类型 1」不完整。
- **`userinfo.Integral` 是浮点数**：实测 `1090.7`，schema 从 `integer` 改为 `number`。
- **`userinfo.Badge[].Id` 恒为 `0`**：5 枚徽章全为 0，而 `/api/badge` 里是 8–12。不是老文档笔误，是服务端确实不填 → 补了「只能用 `/api/badge` 取 ID」的说明与对照表。
- **徽章图床改为 `bucket.noymanga.com`**：老文档的 `bucket.239847.xyz` 已失效；同时补充封面图规律 `img.noymanga.com/<Bid>/m1.webp`。
- 登录、userinfo、badge、home、图床 token 的「校验」状态由 🟡/⚠️ 升为 ✅（2026-10-26）。

### 新增

- `docs/ads.md`：`POST /api/v3/ads`（首页广告位，`data[].img` / `data[].url`）。
- `docs/task/signin.md`：`POST /api/v4/signin/record`（签到记录）。注意它的 `status` 是**数字** `200`，且返回明文 IP；执行签到的端点仍未找到 🚧。
- `Book.alias` 字段（2026-10 新增，样例多为空串）。
- `fixtures/` 新增 `home-2026-10-sample.json`、`ads.json`、`signin-record.json`，并按新实测更新 `badge.json`、`userinfo.json`。
- 图床家族的两个未验证端点线索：`/bucket/api/upload_avatar`、`/bucket/api/upload_bg`。

### 写操作实测（经账号所有者同意）

- `/api/v3/set_badge_show` 升为 ✅：完整做了 `12` 号的「开 → 读 → 关 → 读」往返，确认它是**数组 toggle**（有则删、无则加，新增追加到末尾），响应恒为 `{"status":"ok"}`。
- 顺带查出上游文档没写的坑：**服务端完全不校验 ID**。`id=114514`、甚至不带 `id`（等于空串）都会被原样写进 `show` 数组。测试时这两个值确实进了数组，已用「再切一次」全部清除，最终 `show` 与操作前逐项一致（`["10","11","9","8"]`）。
- 因此 `userinfo.Badge` 的语义也被修正：它是**全部徽章**，不是佩戴中的（实测 `show` 4 项时 `Badge` 仍 5 项）。

### 未完成

- `/api/v3/send_community` 仍是 ⚠️：会在站点产生真实内容，本轮没有触发。
- 执行签到、积分明细、任务列表仍未找到。

## 2026.10.26-a — 文档校正与工程化整理（本 fork 首个版本）

### 修复

- **域名迁移**：全部示例从 `https://beta.noyteam.online` 换成 `https://noymanga.com`。旧域名已 302 跳转，`curl -L` 会因 302 把 POST 退化为 GET 而拿到 `405`。
- **编码统一**：`docs/community/*.md` 三份文件原本是 GBK（GitHub 上整篇乱码）改为 UTF-8；`README.md` 去掉 BOM。
- **`status` 枚举补全**：新增第三个值 `login`（会话失效），此前只写了 `ok` / `error`。
- **示例语法**：修掉 `docs/home.md` 中 `-H "allow-adult: "false"` 的引号嵌套错误。
- **可复制性**：`login.md`、`userinfo.md` 里被误写成 Markdown 链接的 URL（`url = "[https://…](https://…)"`）改回纯文本。
- **站内死链**：README 里指向不存在的 `docs/task/signin.md` 的链接移除，改为「未收录 / 待整理」清单。

### 变更

- **目录重排**：`docs/auths/` → `docs/auth/`，文件名统一小写（`Login.md` → `login.md`，`NOY_SESSION.md` → `noy_session.md`）。
- **`docs/home.md` 瘦身**：从 2050 行降到 ~200 行。原本 91% 的篇幅（40 KB）是一坨原始 JSON，已抽到 `fixtures/home.json`，文档只保留字段表 + 修正后的示例。
- **清理仓库根目录**：删掉两张与项目无关的上传测试图（`images.webp` 白菜图、`b57f….jpg`），测试接口用本地图片即可，顺带省掉 400 KB。

### 新增

- `openapi.yaml`：OpenAPI 3.1 描述，覆盖 9 个端点，含 `Book` / `Stream` / `Badge` / `UserInfo` 等 schema。
- `fixtures/`：`home.json`、`userinfo.json`、`badge.json` 等脱敏样例，可做解析测试的基准。
- `examples/python/noy_client.py`：最小客户端（登录、首页、用户信息、徽章、换图床 token、上传图片、发帖），带 CLI。
- `scripts/check_docs.py` + `.github/workflows/ci.yml`：编码 / BOM / JSON 有效性 / 站内链接 / 旧域名残留自检，markdownlint 与 OpenAPI lint。
- 每份文档顶部的「校验」字段与 README 的状态表，把「谁在什么时候验证过」写清楚。
- `CONTRIBUTING.md`、`.editorconfig`、`.markdownlint.jsonc`。

### 已知问题

- 首页、徽章、发帖等端点的**数据字段**仍沿用 2026-03 的上游抓包，本次只验证了鉴权和错误分支（无可用登录态）。
- `userinfo.Badge[].Id` 与 `badge.md` 的 ID 不一致（`0` vs `8`/`9`），需带登录态复测。
- `Book.Len = 0`、`Book.RatingBayes` 的语义未确认。

## 上游历史（cuteaplane/NoyAcg-API-Collect，2026-03-09 ~ 2026-05-06）

- 2026-05-06 `Update README with disclaimer and maintenance notice`：标注高三暂停维护。
- 2026-03-13 社区接口（图床 token / 上传 / 发帖）文档补齐，移除根目录重复的 `docs/upload_image.md`。
- 2026-03-11 徽章接口（`/api/badge`、`/api/v3/set_badge_show`）文档。
- 2026-03-09 项目起步：`NOY_SESSION`、登录、用户信息、首页聚合。
