# 贡献指南

这是一个纯文档仓库，改动门槛低，但有两件事必须守住：**编码**和**可信度**。

## 提交前自检

```bash
python3 -m pip install pyyaml     # 让自检能顺带校验 YAML
python3 scripts/check_docs.py     # 编码 / BOM / 换行 / JSON / YAML / 站内链接 / 旧域名 / fixture 引用 / 文档索引
npx --yes @redocly/cli lint openapi.yaml   # 改过 openapi.yaml 时
npx --yes markdownlint-cli2       # 改过 markdown 时
```

CI 会跑同样的检查，另外还有 markdownlint。

## 硬性规则

1. **UTF-8，无 BOM，LF 换行**。Windows 上用 Notepad 保存很容易出问题（历史上 `docs/community/` 三份文件就因为这个整篇乱码）。`.editorconfig` 已配置，编辑器装插件即可。
2. **不要在代码块里放 Markdown 链接**。`url = "[https://a](https://a)"` 这种写法复制出来就是坏的。
3. **区分「请求」和「示例」**：示例要能直接粘贴运行，占位符统一写 `xxxx` / `YOUR_PASSWORD`。
4. **失败分支必须写**。每个端点至少有：成功、`status: error`、`status: login` 三种说明（该端点不支持某分支就注明"未观察到"）。
5. **不要贴真实 Cookie、邮箱、Uid、Uhash**。样例里的个人信息一律替换为占位符，或直接用 `fixtures/` 里已脱敏的版本。

## 抓包时的两条铁律

1. **照抄前端的请求参数**，包括那些看起来没用的 `v=3`、`platform=web`、`hide_ip=false`。反例：`/api/home` 不带 `v=3` 就不返回 `stream`，曾让我们误判「番剧推荐已下线」。
2. **区分「参数缺失」和「字段被删」**。字段消失时先怀疑参数，再怀疑服务端改版。

## 新增或修订一个端点

1. 用浏览器 DevTools（Network → 右键请求 → Copy as cURL）抓一条真实请求，注意把 `Cookie` 里只保留 `NOY_SESSION=xxx`。
2. 按 `docs/home.md` 的结构写：概览表 → 请求头 → 请求参数 → 响应结构 → 字段表 → 失败分支 → curl 示例 → 备注。
3. 原始响应脱敏后放进 `fixtures/<endpoint>.json`，文档里用相对链接引用，**不要**把几万字的 JSON 内联进 markdown。
4. 在 `openapi.yaml` 里补 path 和 schema，跑一次 `redocly lint`。
5. 更新三处日期/状态：文档头部的 `校验` 表、README 的「接口一览」表、`CHANGELOG.md`。

## 字段可信度标记

| 标记 | 用在什么情况 |
| --- | --- |
| ✅ | 你自己刚刚实测过，或 `fixtures/` 里有同期抓包 |
| 🟡 | 结构可信但只验证了一部分分支 |
| ⚠️ | 早期记录 / 语义不明，写明「待确认」而不是猜 |

宁可写「语义未确认」，也不要写一个看起来很像真的但没验证的解释——这份文档的价值全在可信度上。

## 伦理边界

- 只做**只读**抓包与文档化。批量写操作（发帖、签到、刷积分）的脚本不要提交到这个仓库。
- 发现接口存在安全问题，走 [上游仓库的 Issue](https://github.com/cuteaplane/NoyAcg-API-Collect/issues) 或以私下方式告知站点，不要在文档里写成操作指南。
- 本项目与 NoyAcg 官方无关，遵守站点服务条款是你的责任。
