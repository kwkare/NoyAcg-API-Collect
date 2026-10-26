# fixtures

真实响应的脱敏快照，用途只有两个：给人对照字段、给测试当基准。

| 文件 | 接口 | 抓取时间 | 说明 |
| --- | --- | --- | --- |
| `home.json` | `POST /api/home` | 2026-03 | 全量快照：79 本书（`favDay` 20 + `readDay` 20 + `fs` 20 + `proportion` 19）、10 部番剧、9 个标签。**含已下线的 `stream` 字段**，是唯一能还原「当年有番剧推荐」的证据 |
| `home-2026-10-sample.json` | `POST /api/home` | 2026-10-26 | 精简快照（每榜 1 条，`allow-adult: false`）：用于展示当前的字段集——新增 `alias`、没有 `stream`、`Len` 的取值 |
| `userinfo.json` | `POST /api/v3/userinfo` | 2026-10-26 | 邮箱 / Uid / Uhash / 昵称 / 头图路径全部打码。**保留 `Badge[].Id` 全为 `0` 的真实形态**，这正是要记录的坑 |
| `badge.json` | `POST /api/badge` | 2026-10-26 | 5 枚徽章（`Id` 8–12），`show` 保留「字符串数组」的真实形态 |
| `ads.json` | `POST /api/v3/ads` | 2026-10-26 | 广告位。`img` 文件名与 `url` 全部替换为占位符，避免转发第三方推广链接 |
| `signin-record.json` | `POST /api/v4/signin/record` | 2026-10-26 | 签到记录。`uid` / `ip` / 记录 `id` 已打码；保留 `status` 是**数字** `200` 的形态 |
| `unauthorized.json` | 任意需要鉴权的接口 | 2026-10-26 | 会话失效时的统一响应 `{"status":"login"}` |

## 约定

- **不要**往这里放带 Cookie、邮箱、Uid、Uhash、IP 的数据。加新快照前先按上面的规则脱敏。
- 结构变了就新建一份带日期的文件（如 `home-2026-10-sample.json`），**别覆盖旧快照**——`home.json`（2026-03）和 `home-2026-10-sample.json` 的差异本身就是这次整理最有价值的结论之一。
- 快照代表**结构**，不代表内容：书名、榜单顺序、广告素材都会变。
- 大快照请保持「一条记录一行」的格式，git diff 才看得懂。
