# 表情包（Sticker）

站内表情包**没有 API**：分组、代码和图片全部硬编码在前端 bundle 里，服务端只存你发的那串**代码文本**。

| 项目 | 内容 |
| --- | --- |
| 数据来源 | `assets/sticker-text-*.js`（前端打包产物） |
| 图片地址 | `https://noymanga.com/stickers/<file>`（静态资源，实测 200 / `image/webp`） |
| 用法 | 在正文 / 评论里写 `[组名:代号]` |
| 校验 | ✅ 2026-10-27 实测（发帖正文用 `[noygirl:yeah]`，正常渲染） |

## 怎么工作的

1. 前端有个写死的映射表：`[noygirl:yeah]` → `noy8.webp`
2. 你发的正文里保留这串**纯文本**，服务端原样存储
3. 渲染时用正则匹配并替换成图片：

```text
/(?<sticker>\[[a-z]+:[a-z0-9]+\])|(?<nidPrefix>NID|nid)(?<nid>\d+)/gi
```

所以：

- 代码拼错 → 原样显示成文字（不会报错）；
- 想加新表情包 = 改前端发版，跟后端无关；
- 同一个正则还负责 `NID<id>`（书籍引用，渲染成书名链接，走 `/api/v4/book/name_by_ids?i=<id>`）。

## 全部分组（4 组 / 57 个）

### Noy Girl（12）

| 代码 | 图片 |
| --- | --- |
| `[noygirl:happy]` | `noy1.webp` |
| `[noygirl:wtf]` | `noy2.webp` |
| `[noygirl:speechless]` | `noy3.webp` |
| `[noygirl:call]` | `noy4.webp` |
| `[noygirl:eat]` | `noy5.webp` |
| `[noygirl:no]` | `noy6.webp` |
| `[noygirl:watermelon]` | `noy7.webp` |
| `[noygirl:yeah]` | `noy8.webp` |
| `[noygirl:hum]` | `noy9.webp` |
| `[noygirl:haha]` | `noy10.webp` |
| `[noygirl:see]` | `noy11.webp` |
| `[noygirl:what]` | `noy12.webp` |

### SB（11）

`[sb:a]` `[sb:eh]` `[sb:what]` `[sb:u]` `[sb:ok]` `[sb:haa]` `[sb:good]` `[sb:pu]` `[sb:yes]` `[sb:aa]` `[sb:no]`
（依次对应 `sb1.webp` … `sb11.webp`）

### Kimeemaru（23）

`[kmaru:1]` … `[kmaru:23]` → `kmaru1.webp` … `kmaru23.webp`

### Vik（11）

`[vik:1]` … `[vik:11]` → `vik1.webp` … `vik11.webp`

## 示例

```bash
BASE=https://noymanga.com

# 发一条只有表情包的评论
curl -s -X POST "$BASE/api/v4/community/post/78930/reply" \
  -b "NOY_SESSION=xxxx" \
  -d "reply_id=-1" \
  --data-urlencode "text=[noygirl:yeah]" \
  -d "platform=web" -d "hide_ip=false"
```

正文里也可以混排：`今天好耶 [noygirl:yeah] 顺便看 NID15969`。

## 已知的坑

- 代码是**小写**，`[NoyGirl:Yeah]` 不会被识别（正则带 `i` 标记，理论上大小写都行，但未实测 ⚠️）。
- 表情表是前端静态数据，站点换表情包时本页会过时——以 bundle 里的 `sticker-text-*.js` 为准。
- 直接抓 `https://noymanga.com/stickers/noy8.webp` 就能拿到原图（用于预览）。
