# 发帖

在社区发一条带图 / 不带图的帖子。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/v3/send_community` |
| Content-Type | `application/x-www-form-urlencoded` |
| 鉴权 | Cookie `NOY_SESSION` |
| 校验 | ✅ 2026-10-27 实测（真的发了一帖：标题「图」+ 6 张图 + 表情包正文） |

> ⚠️ 这是**写操作**，会在站点上产生真实内容。帖子**没有删除接口**（未发现），发之前想清楚；90 天后会随 `expired` 自动过期。
> 测试时请发到自己能删的地方，并遵守社区规则；不要用它刷帖。

## 请求参数（表单）

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `title` | string | 是 | 标题 |
| `content` | string | 是 | 正文 |
| `image` | string | 否 | **JSON 数组的字符串**，元素为 `image/<file>` |
| `platform` | string | 是 | `web`（网页端）/ `android`（App） |

### `image` 字段最容易踩坑

上传接口返回的是纯文件名：

```json
{ "file": "91266-xxx.webp", "status": "ok" }
```

发帖时必须自己拼上前缀、再序列化成 JSON 字符串：

| 单图 | `image=["image/91266-xxx.webp"]` |
| --- | --- |
| 多图 | `image=["image/a.webp","image/b.webp"]` |

常见错误：

- 只传文件名（漏 `image/` 前缀）→ 帖子发出去了但没图；
- 传真正的数组类型（`image[]=...`）→ 后端收不到；
- 传了 JSON 但没 url-encode → 服务端解析失败。

## 成功响应

```json
{ "status": "ok" }
```

**不返回帖子 ID**。想拿到自己刚发的帖子，得去 [`community_list`](./community_list.md) 里用 `type=new` 翻第一页找（按 `uid` + `title` 匹配）。

## 实测记录（2026-10-27）

一次真实发帖的参数与结果：

| 项 | 值 |
| --- | --- |
| `title` | `图` |
| `content` | `[noygirl:yeah]`（正文只有一条表情包代码，渲染正常） |
| `image` | 6 个 `image/<Uhash>-<sha256>.webp` |
| `platform` | `web` |
| 响应 | `{"status":"ok"}` |
| 落到列表后 | `id=78930`、`image` 6 项、`reply=0`、`like=0`、`expired = time + 7776000`（90 天） |

### 关于「模糊 / R18」

发帖请求里**没有任何成人向参数**，服务端自己判定：

```json
"spoiler": "0,1,2,3,4,5"
```

即便上传图片时带的是 `allow-adult: false`，这 6 张图仍被整体标记为「需模糊」（前端显示「點擊顯示」遮罩）。所以：

- 客户端**无法**手动指定 / 取消模糊；
- `spoiler` 是**服务端返回**的图片下标列表，作者只读不写。

### 图片数量

6 张一次发出正常；上限未知 ⚠️（前端画廊只展示前 9 张，`image` 数组本身似乎不限）。

| 场景 | 响应 |
| --- | --- |
| 发布成功 | `{"status":"ok"}` |
| 未登录 | `{"status":"login"}` ⚠️ 未实测 |
| 内容被拒（长度 / 敏感词 / 频率） | `{"status":"error"}` ⚠️ 具体原因不回传 |

接口**不返回新帖 ID**，要确认发布结果只能去社区列表页或自己的主页查。

## 示例

### curl（网页端）

```bash
BASE=https://noymanga.com

curl -s "$BASE/api/v3/send_community" \
  -X POST \
  -H "content-type: application/x-www-form-urlencoded" \
  -b "NOY_SESSION=xxxx" \
  --data-urlencode "title=测试标题" \
  --data-urlencode "content=一条纯文本帖" \
  --data-urlencode "image=[\"image/91266-13025882b9402bd576b628a1030433a6388156d5aaeccb40362960af47a4aa79.webp\"]" \
  --data-urlencode "platform=web"
```

### PowerShell

`curl.exe` 在 PowerShell 里要额外注意引号，`image` 的 JSON 里既有双引号又有方括号：

```powershell
$img = "91266-13025882b9402bd576b628a1030433a6388156d5aaeccb40362960af47a4aa79.webp"

curl.exe "https://noymanga.com/api/v3/send_community" `
  -X POST `
  -H "content-type: application/x-www-form-urlencoded" `
  -b "NOY_SESSION=xxxx" `
  --data-urlencode "title=测试标题" `
  --data-urlencode "content=一条纯文本帖" `
  --data-urlencode "image=[`"image/$img`"]" `
  --data-urlencode "platform=android"
```

### Python

```python
import json
import requests

BASE = "https://noymanga.com"


def send_community(session: requests.Session, title: str, content: str,
                   files: list[str] | None = None, platform: str = "web") -> bool:
    data = {"title": title, "content": content, "platform": platform}
    if files:
        data["image"] = json.dumps([f"image/{f}" for f in files])
    resp = session.post(f"{BASE}/api/v3/send_community", data=data, timeout=30)
    return resp.json().get("status") == "ok"
```

## 完整链路

```text
POST /api/get_image_bucket_token        → token
POST bucket.noymanga.com/api/upload_image (token + file) → file
POST /api/v3/send_community (image=["image/<file>"])     → ok
```

## 备注

- `platform` 目前只观察到 `web` / `android`，其他值未验证 ⚠️。
- 正文是否支持 Markdown / HTML 未确认；抓包时前端发的是纯文本 ⚠️。
- 标题和正文长度上限未测；超出后大概率为 `status: error`。
