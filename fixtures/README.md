# fixtures

真实响应的脱敏快照，用途只有两个：给人对照字段、给测试当基准。

| 文件 | 来源 | 说明 |
| --- | --- | --- |
| `home.json` | `POST /api/home`，2026-03 抓包 | 79 本书（`favDay` 20 + `readDay` 20 + `fs` 20 + `proportion` 19）、10 部番剧、9 个标签。抓取时 `allow-adult: false`，所以 `Adult` 全为 `0` |
| `userinfo.json` | `POST /api/v3/userinfo` | 邮箱 / Uid / 昵称 / 哈希全部替换为占位符 |
| `badge.json` | `POST /api/badge` | 两枚徽章，`show` 保留字符串与数字混用的真实形态 |
| `unauthorized.json` | 任意需要鉴权的接口 | 会话失效时的统一响应 |

## 约定

- **不要**往这里放带 Cookie、邮箱、Uid、Uhash 的数据。要加新的，先按上面几条规则脱敏。
- 结构变了就新建一份带日期的副本（如 `home-2026-10.json`），别直接覆盖——旧快照本身是有价值的对照物。
- `home.json` 里的书名、榜单顺序是抓取当时的真实状态，会随时间变化；它代表**结构**，不代表内容。
