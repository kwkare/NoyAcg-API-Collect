# CHANGELOG

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)；本项目是文档项目，版本号取「整理批次（年.月.日）」而不是语义化版本。

## 2026.10.26 — 文档校正与工程化整理（本 fork 首个版本）

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
