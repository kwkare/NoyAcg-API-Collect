# CHANGELOG

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)；本项目是文档项目，版本号取「整理批次（年.月.日）」而不是语义化版本。

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

### 未完成

- `/api/v3/set_badge_show`、`/api/v3/send_community` 仍是 ⚠️：都是写操作，本轮刻意没有触发（需要账号所有者同意后做一次往返验证）。
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
