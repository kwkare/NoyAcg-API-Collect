# NoyAcg API Collect

[![ci](https://github.com/kwkare/NoyAcg-API-Collect/actions/workflows/ci.yml/badge.svg)](https://github.com/kwkare/NoyAcg-API-Collect/actions/workflows/ci.yml)

> NoyAcg（[noymanga.com](https://noymanga.com)，漫画・同人志社区）Web / App 客户端 HTTP API 的**非官方**整理笔记。
> 纯文档项目，没有官方支持，接口随时可能变更。

| 项目 | 内容 |
| --- | --- |
| Base URL | `https://noymanga.com` |
| 旧域名 | `beta.noyteam.online` 已 **302** 跳转至新域名（2026-10-26 实测），旧文档里的示例地址全部失效 |
| 鉴权 | Cookie `NOY_SESSION`，见 [NOY_SESSION](./docs/auth/noy_session.md) |
| 请求风格 | 全部 `POST`，表单 `application/x-www-form-urlencoded`；图床上传为 `multipart/form-data` |
| 响应风格 | JSON，业务状态放在 `status` 字段：`ok` / `error` / `login` |
| 内容分级 | 请求头 `allow-adult: true`、`false`、`both` |

> [!WARNING]
> **免责声明**：本项目仅供技术研究与学习参考。请勿利用本项目提供的接口进行任何形式的攻击、爬虫滥用或违反社区服务条款的操作。因使用本项目导致的任何后果，作者不承担任何法律责任。
>
> 上游原作 [cuteaplane/NoyAcg-API-Collect](https://github.com/cuteaplane/NoyAcg-API-Collect) 因作者高三**暂停维护**；本 fork 只做文档校正与工程化整理，不作功能扩展。

## 接口一览

「校验」列表示最近一次人工验证的状态：✅ 已实测可用 · 🟡 部分实测（只验证了鉴权/错误分支）· ⚠️ 沿用旧记录待复测。

| 接口 | 端点 | 鉴权 | 校验 | 文档 |
| --- | --- | --- | --- | --- |
| 登录 | `POST /api/login` | — | 🟡 无效凭据返回 `status: error`（2026-10-26） | [login.md](./docs/auth/login.md) |
| 会话凭证 | Cookie `NOY_SESSION` | — | 🟡 未登录返回 `status: login`（2026-10-26） | [noy_session.md](./docs/auth/noy_session.md) |
| 首页聚合 | `POST /api/home` | Cookie | 🟡 数据字段沿用 2026-03 抓包 | [home.md](./docs/home.md) |
| 用户信息 | `POST /api/v3/userinfo` | Cookie | 🟡 未登录分支实测 | [userinfo.md](./docs/user/userinfo.md) |
| 徽章列表 | `POST /api/badge` | Cookie | ⚠️ 待复测 | [badge.md](./docs/user/badge.md) |
| 徽章佩戴开关 | `POST /api/v3/set_badge_show` | Cookie | ⚠️ 待复测 | [set_badge_show.md](./docs/user/set_badge_show.md) |
| 图床上传凭证 | `POST /api/get_image_bucket_token` | Cookie | 🟡 未登录分支实测 | [get_image_bucket_token.md](./docs/community/get_image_bucket_token.md) |
| 图片上传 | `POST bucket.noymanga.com/api/upload_image` | token | 🟡 空 token 返回 403（2026-10-26） | [upload_image.md](./docs/community/upload_image.md) |
| 发帖 | `POST /api/v3/send_community` | Cookie | ⚠️ 待复测 | [send_community.md](./docs/community/send_community.md) |

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

# 3. 读首页：直接看 JSON 顶层结构
curl -s -b jar.txt -X POST "$BASE/api/home" \
  -H "allow-adult: false" | head -c 400
```

脚本示例（Python，含登录、上传图片、发帖）：[`examples/python/noy_client.py`](./examples/python/noy_client.py)。

## 字段可信度

老文档最大的问题是「示例看起来像契约」，所以这里约定三种标记：

| 标记 | 含义 |
| --- | --- |
| ✅ | 有近期抓包或实测支撑 |
| 🟡 | 结构可信，但只验证了部分分支 |
| ⚠️ | 早期记录，未复测，可能已变更 |

已知的、由抓包数据反推出的细节修正（原文档未覆盖）：

- `Book.Len` 出现过 `0`（原文档只写了 `1 / 2`），语义待确认 ⚠️。
- `Book.publish_year` 可能为空字符串 `""`，不是 `null`，也不是缺字段。
- `Book.Pname` 大量为占位符 `"未知"`（79 本样例中 72 本），不要当作人物名使用。
- `Book.RatingBayes` 样例中恒为 `0`，先按「未启用」对待。
- `userinfo.Badge[].Id` 在原示例里是 `0`，而 `badge.md` 里同一枚徽章是 `8` / `9`；**以 `/api/badge` 返回的 `Id` 为准** ⚠️。
- 所有接口的 `status` 都有第三个值 `login`（会话失效），原文档只写了 `ok` / `error`。

## 未收录 / 待整理

以下接口尚未整理（欢迎 PR，附 curl 或抓包即可）：

- 每日签到 / 任务系统
- 收藏、订阅、阅读进度
- 评论、回复、举报
- 搜索、分类浏览、榜单分页
- 通知 / 消息
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
│   ├── auth/              login / NOY_SESSION
│   ├── user/              userinfo / badge / set_badge_show
│   └── community/         图床 token / 上传 / 发帖
├── fixtures/              原始响应样例（已脱敏，供测试与对比）
├── examples/              最小客户端
├── scripts/check_docs.py  本地/CI 自检：编码、JSON 有效性、站内链接、旧域名残留
└── .github/workflows/     CI：文档自检 + markdownlint + OpenAPI lint
```

## 贡献

见 [CONTRIBUTING.md](./CONTRIBUTING.md)。最低要求：文档一律 **UTF-8 无 BOM**、每改一个端点就更新「校验」列日期。

## 许可

- 文档、`fixtures/`、`openapi.yaml`：**CC BY-NC 4.0**（见 [LICENSE](./LICENSE)），与上游一致。
- `examples/` 下的代码片段：视为 **MIT**，可自由取用。
- 本项目与 NoyAcg 官方无关，接口与内容版权归原站所有。
