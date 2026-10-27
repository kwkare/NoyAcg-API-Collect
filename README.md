# NoyAcg API Collect

[![ci](https://github.com/kwkare/NoyAcg-API-Collect/actions/workflows/ci.yml/badge.svg)](https://github.com/kwkare/NoyAcg-API-Collect/actions/workflows/ci.yml)

> NoyAcg（[noymanga.com](https://noymanga.com)，漫画・同人志社区）Web / App 客户端 HTTP API 的**非官方**整理笔记。
> 纯文档项目，没有官方支持，接口随时可能变更。
>
> 🔌 想要开箱即用的 agent 集成？见 **[NoyAcg-MCP](https://github.com/kwkare/NoyAcg-MCP)** —— 基于本仓库契约实现的 stdio MCP server（15 个工具 / 6 个资源 / 写操作审计）。

| 项目 | 内容 |
| --- | --- |
| Base URL | `https://noymanga.com` |
| 旧域名 | `beta.noyteam.online` 已 **302** 跳转至新域名（2026-10-26 实测），旧文档里的示例地址全部失效 |
| 鉴权 | Cookie `NOY_SESSION`，见 [会话机制](./docs/auth/session.md) |
| 请求风格 | 全部 `POST`，表单 `application/x-www-form-urlencoded`；图床上传为 `multipart/form-data` |
| 响应风格 | JSON，业务状态放在 `status` 字段：`ok` / `error` / `login`（签到接口是数字 `200`） |
| 内容分级 | 请求头 `allow-adult: true`、`false`、`both`，**`/api/home` 不传时默认返回 R18** |
| 版本号 | `v1`（无版本号）/ `v3` / `v4` 三套并存，按路径各自对待 |

> [!WARNING]
> **免责声明**：本项目仅供技术研究与学习参考。请勿利用本项目提供的接口进行任何形式的攻击、爬虫滥用或违反社区服务条款的操作。因使用本项目导致的任何后果，作者不承担任何法律责任。
>
> 上游原作 [cuteaplane/NoyAcg-API-Collect](https://github.com/cuteaplane/NoyAcg-API-Collect) 因作者高三**暂停维护**；本 fork 只做文档校正与工程化整理，不作功能扩展。

## 接口一览

「校验」列表示最近一次人工验证的状态：✅ 已实测 · 🟡 部分实测（只验证了鉴权/错误分支）· ⚠️ 沿用旧记录待复测。

| 接口 | 端点 | 鉴权 | 校验 | 文档 |
| --- | --- | --- | --- | --- |
| 登录 | `POST /api/login` | — | ✅ 2026-10-27（真实登录抓包核对） | [login](./docs/auth/login.md) |
| 注册 | `POST /api/v3/reg` | — | 🚧 参数已挖到，需极验验证码，未实测 | [login](./docs/auth/login.md) |
| 重置密码 | `POST /api/reset_passwd` | — | 🚧 参数已挖到，未实测 | [login](./docs/auth/login.md) |
| 登出 | `POST /api/logout` | Cookie | ✅ 2026-10-27（会吊销会话） | [session](./docs/auth/session.md) |
| 会话凭证 | Cookie `NOY_SESSION` | — | ✅ 2026-10-27（含 cookie 解剖 / 属性 / 吊销） | [session](./docs/auth/session.md) |
| 首页聚合 | `POST /api/home` | Cookie | ✅ 2026-10-26 | [home](./docs/home.md) |
| 首页广告位 | `POST /api/v3/ads` | Cookie | ✅ 2026-10-26 | [ads](./docs/ads.md) |
| 用户信息 | `POST /api/v3/userinfo` | Cookie | ✅ 2026-10-26 | [userinfo](./docs/user/userinfo.md) |
| 徽章列表 | `POST /api/badge` | Cookie | ✅ 2026-10-26 | [badge](./docs/user/badge.md) |
| 徽章佩戴开关 | `POST /api/v3/set_badge_show` | Cookie | ✅ 2026-10-26（toggle，且不校验 ID） | [set_badge_show](./docs/user/set_badge_show.md) |
| 签到记录 | `POST /api/v4/signin/record` | Cookie | ✅ 2026-10-27（跨零点实测） | [signin](./docs/task/signin.md) |
| 执行签到 | `POST /api/v4/signin/sign` | Cookie | ✅ 2026-10-27（真签了） | [signin](./docs/task/signin.md) |
| 图床上传凭证 | `POST /api/get_image_bucket_token` | Cookie | ✅ 2026-10-26 | [get_image_bucket_token](./docs/community/get_image_bucket_token.md) |
| 图片上传 | `POST bucket.noymanga.com/api/upload_image` | token | ✅ 2026-10-27（6 张真传成功） | [upload_image](./docs/community/upload_image.md) |
| 发帖 | `POST /api/v3/send_community` | Cookie | ✅ 2026-10-27（真发了一帖 6 图） | [send_community](./docs/community/send_community.md) |
| 帖子列表 | `POST /api/v3/community_list` | Cookie | ✅ 2026-10-27 | [community_list](./docs/community/community_list.md) |
| 帖子详情 / 评论列表 | `POST /api/v4/community/post/<id>` | Cookie | ✅ 2026-10-27 | [post_detail](./docs/community/post_detail.md) |
| 发评论 / 回复 | `POST /api/v4/community/post/<id>/reply` | Cookie | ✅ 2026-10-27（真发了一条） | [post_detail](./docs/community/post_detail.md) |
| 编辑帖子 | `POST /api/v3/edit_community_post` | Cookie | ✅ 2026-10-27（改了正文） | [post_detail](./docs/community/post_detail.md) |
| 点赞 | `POST /api/v3/community_like` | Cookie | ✅ 2026-10-27（点赞 + 取消） | [post_detail](./docs/community/post_detail.md) |
| 楼中楼列表 | `POST /api/v4/community/post/<id>/comment/<rid>/replies` | Cookie | ✅ 2026-10-27 | [post_detail](./docs/community/post_detail.md) |
| 未读计数 | `POST /api/v4/msg/count` | Cookie | ✅ 2026-10-27 | [messages](./docs/user/messages.md) |
| 讯息列表 | `POST /api/v3/get_msg`（`type=reply` / `community_reply` / `sysmsg`） | Cookie | ✅ 2026-10-27 | [messages](./docs/user/messages.md) |
| 表情包 | 无 API（前端硬编码） | — | ✅ 2026-10-27 | [stickers](./docs/community/stickers.md) |

机器可读版本：[`openapi.yaml`](./openapi.yaml)（OpenAPI 3.1，覆盖上面全部端点）。

## 快速开始

```bash
BASE=https://noymanga.com

# 1. 登录：成功时 NOY_SESSION 会落在 cookie jar 里
curl -s -c jar.txt "$BASE/api/login" \
  -H "content-type: application/x-www-form-urlencoded" \
  --data-urlencode "user=you@example.com" \
  --data-urlencode "pass=YOUR_PASSWORD"

# 2. 读自己：返回 {"status":"ok","userinfo":{...}}
curl -s -b jar.txt -X POST "$BASE/api/v3/userinfo" -H "allow-adult: false"

# 3. 读首页：不带头会拿到 R18，务必显式指定分级
curl -s -b jar.txt -X POST "$BASE/api/home" \
  -H "allow-adult: false" | head -c 400
```

脚本示例（Python，含登录、上传图片、发帖）：[`examples/python/noy_client.py`](./examples/python/noy_client.py)。

## 2026-10 实测的主要变化

登录态下把全部端点过了一遍，与原文档的差异（细节见各文档）：

| 变化 | 影响 |
| --- | --- |
| `/api/home` 的 **`stream` 要带 `v=3`** 才有 | 不带 `v=3` 时响应里根本没有这个 key，前端静默隐藏「動畫」区块——很像「功能下线」，其实是参数没带 |
| `allow-adult` **缺省 = R18** | 忘记带请求头就会拿到成人向榜单，测试时容易误判 |
| `Book` 新增 **`alias`** 字段 | 20 个字段了，解析器按固定下标取值会错位 |
| `Book.Len` 不是枚举 | 实测 R18 作品取到 `5`~`194`，是「长度/话数」而非「1=短/2=长」 |
| `userinfo.Integral` 是**小数** | 实测 `1090.7`，按 int 建模会丢精度 |
| `userinfo.Badge[].Id` **恒为 `0`** | 服务端不填这个字段，要真实 ID 只能查 `/api/badge` |
| `userinfo.Badge` **不是**佩戴中的徽章 | 它是全部徽章（实测 `show` 只有 4 项时仍返回 5 项），佩戴状态只看 `/api/badge.show` |
| `set_badge_show` **不校验 ID** | 任何字符串（包括 `114514`、空串）都会被写进 `show`，只能靠「再切一次」清掉 |
| 新增 `/api/v3/ads`、`/api/v4/signin/record` | 广告位与签到记录，此前完全没记录 |
| 登录接口可程序化使用 | `/api/login` 无验证码，账号密码直接换 30 天 Cookie；注册才需要极验 |
| 写操作链路跑通：发帖 6 图 / 评论 / 签到 | 发帖**不返帖 ID**、评论**不返评论 ID**，都要回列表查；`spoiler` 由服务端判定 |
| 徽章图床从 `bucket.239847.xyz` 换到 `bucket.noymanga.com` | 老文档里的图片 URL 全部失效 |

## 字段可信度

老文档最大的问题是「示例看起来像契约」，所以这里约定三种标记：

| 标记 | 含义 |
| --- | --- |
| ✅ | 有近期抓包或实测支撑 |
| 🟡 | 结构可信，但只验证了部分分支 |
| ⚠️ | 早期记录或语义不明，未复测 |

由抓包数据反推出的细节修正（原文档未覆盖）：

- `Book.publish_year` 常见空字符串 `""`，不是 `null`，也不是缺字段；R18 榜单里 80/80 全为空。
- `Book.RatingSUM` / `RatingCount` 同时为 `0` 表示「还没人评分」，不是评分为 0。
- `Book.Pname` 大量为占位符 `"未知"`，不要当作人物名使用。
- `Book.Mode` 与 `Book.Adult` 在本次抓取里一一对应（`Mode=1 ↔ Adult=0`），疑似同人志 / 连载漫画的区分，语义未确认 ⚠️。
- `Book.RatingBayes` 恒为 `0`，先按「未启用」对待。
- `allow-adult` 的 `false` / `true` 两套内容池**零交集**，`tags` 也跟着变（9 / 13 / 22 个）。
- 封面图不在接口里，前端按 `https://img.noymanga.com/<Bid>/m1.webp` 自己拼。

## 未收录 / 待整理

以下接口尚未整理（欢迎 PR，附 curl 或抓包即可）：

- 图床的 `/bucket/api/upload_avatar`、`/bucket/api/upload_bg`（同家族，未验证）
- 收藏、订阅、阅读进度、积分流水（bundle 里有 `daily_signin` / `store_purchase` 等动作枚举）
- 举报
- `type=sysmsg` 的消息条目字段（该账号没有系统消息，一直是空数组）
- 搜索、分类浏览、榜单分页（`/latest?sort=stream` 等路由存在）
- App（`platform=android`）专用接口

## 仓库结构

```text
.
├── README.md              本文件（索引 + 快速开始 + 可信度约定）
├── CHANGELOG.md           变更记录
├── CONTRIBUTING.md        如何校验、如何提交
├── openapi.yaml           OpenAPI 3.1 描述（可导入 Postman / 生成客户端）
├── docs/                  人读文档，按域划分
│   ├── home.md
│   ├── ads.md
│   ├── auth/              login / session（cookie 机制）
│   ├── user/              userinfo / badge / set_badge_show / messages
│   ├── task/              signin（记录查询 + 执行签到）
│   └── community/         图床 token / 上传 / 发帖 / 列表 / 详情与评论 / 表情包
├── fixtures/              原始响应样例（已脱敏，供测试与对比）
├── examples/              最小客户端
├── scripts/check_docs.py  本地/CI 自检：编码 / JSON / YAML / 站内链接 / fixture 引用 / 文档索引
└── .github/workflows/     CI：文档自检 + markdownlint + OpenAPI lint
```

## 生态

| 项目 | 说明 |
| --- | --- |
| [NoyAcg-MCP](https://github.com/kwkare/NoyAcg-MCP) | TypeScript MCP server，把本文档的接口封成 agent 可直接调用的工具（读帖 / 发帖 / 评论 / 签到 / 徽章），带审计日志与只读模式 |

## 贡献

见 [CONTRIBUTING.md](./CONTRIBUTING.md)。最低要求：文档一律 **UTF-8 无 BOM**、每改一个端点就更新「校验」列日期、样例必须脱敏（邮箱 / Uid / Uhash / **IP**）。

提交前跑一遍 `python3 scripts/check_docs.py`（CI 会跑同一套，外加 markdownlint 与 OpenAPI lint）。

## 许可

- 文档、`fixtures/`、`openapi.yaml`：**CC BY-NC 4.0**（见 [LICENSE](./LICENSE)），与上游一致。
- `examples/` 下的代码片段：视为 **MIT**，可自由取用。
- 本项目与 NoyAcg 官方无关，接口与内容版权归原站所有。
