# examples

## python/noy_client.py

零依赖之外只用 `requests` 的最小客户端，同时当 CLI 用。

```bash
pip install requests

# 凭证：二选一
export NOY_SESSION=xxxx
# 或者
export NOY_EMAIL=you@example.com NOY_PASS=YOUR_PASSWORD

# 只读
python noy_client.py whoami
python noy_client.py home --adult false --out home.json       # 默认带 v=3，含 stream
python noy_client.py badges
python noy_client.py signin                                   # 签到记录
python noy_client.py list --type new                          # 社区列表
python noy_client.py post 78930                               # 帖子详情 + 评论
python noy_client.py msg --kind community                     # 讯息
python noy_client.py replies 41029 445567                     # 楼中楼

# 写操作（默认 dry-run，加 --yes 才真的执行）
python noy_client.py checkin --yes
python noy_client.py upload ./test.jpg                        # 上传本身即写操作
python noy_client.py send --title 测试 --content 你好 --yes
python noy_client.py reply 78930 "你好" --yes
python noy_client.py edit 78930 --title 图 --content "[noygirl:yeah]" --yes
python noy_client.py like 78930 --yes
python noy_client.py logout --yes                             # ⚠️ 会吊销当前会话
```

设计上的几个刻意选择：

| 选择 | 原因 |
| --- | --- |
| 写操作默认 dry-run | `send` / `reply` / `edit` / `like` / `logout` 不加 `--yes` 只打印将要做什么 |
| 干跑不需要凭证 | dry-run 分支不构造客户端，没有 `NOY_SESSION` 也能先看计划 |
| 上传用独立的 `requests.post` | 不共享 `Session`，避免把 `NOY_SESSION` 发给 `bucket.noymanga.com` |
| 只判断响应体的 `status` | 这套 API 的 HTTP 码几乎恒为 200，看状态码会误判 |
| `AuthRequired` 单独一类异常 | `status: login` 需要重新登录，和业务失败不是一回事 |
| 不做重试 | 发帖 / 徽章开关都不幂等，自动重试会翻转或重复发布 |

## 约定

- 这里只放**只读为主**的示例。批量签到、刷积分、自动发帖这类东西不要提交（见根目录 `CONTRIBUTING.md` 的「伦理边界」）。
- 示例代码视为 MIT，可自由取用；文档本身是 CC BY-NC 4.0。
- 接口行为以 `docs/` 为准，示例与文档冲突时先修示例。
