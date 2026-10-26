# 首页广告位

首页渲染时和 `/api/home` 一起调用，返回轮播 / 侧栏的广告图。

| 项目 | 内容 |
| --- | --- |
| Endpoint | `POST https://noymanga.com/api/v3/ads` |
| Content-Type | `application/x-www-form-urlencoded`（无请求体） |
| 鉴权 | Cookie `NOY_SESSION`（带登录态时均正常返回；未登录未测 ⚠️） |
| 校验 | ✅ 2026-10-26 实测（3 次） |

## 响应

```json
{
  "data": [
    { "img": "https://bucket.noymanga.com/image/<ad>.webp", "url": "https://example.com/ad-1" }
  ],
  "status": "ok"
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `data` | object[] | 广告列表，实测 3 条 |
| `data[].img` | string | 广告图（托管在图床域名） |
| `data[].url` | string | 点击跳转地址，带推广追踪参数 |
| `status` | string | `ok` |

脱敏样例：[`fixtures/ads.json`](../fixtures/ads.json)。

## 分级

| `allow-adult` | 结果 |
| --- | --- |
| `false` | 3 条 |
| `true` | 3 条，内容与 `false` **不同**（顺序 / 条目有差异） |
| 不传 | 与 `false` 一致（3 条） |

> 和 `/api/home` 相反：这里不带头不会拿到成人向素材。

## 备注

- 广告 `url` 带第三方推广参数，**不要**在文档或示例里原样转发真实广告链接（本仓库的 fixture 已打码）。
- 广告内容时效性强，抓包只用于确认结构。
- 未观察到的行为：未登录是否返回 `login`、`data` 是否可能为空数组 ⚠️。
