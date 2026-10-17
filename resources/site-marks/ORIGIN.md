# 来源图标

这五枚图标用于「来源和凭证」页的站点身份，归各站点所有，不用于 Peach 品牌。

| 文件 | 来源 | 获取原因 |
| --- | --- | --- |
| javten.png | JAVten 的公开图标缓存：`https://www.google.com/s2/favicons?domain=javten.com&sz=64` | 官方首页与图标端点返回 Cloudflare 403，favicon.ico 返回空文件 |
| fc2ppvdb.png | FC2PPV-DB 的公开图标缓存：`https://www.google.com/s2/favicons?domain=fc2ppv-db.com&sz=64` | 官方首页与图标端点返回 Cloudflare 403 |
| avwikidb.png | `https://avwikidb.com/apple-touch-icon.png` | 首页有验证页，公开图标可读取 |
| minnano-av.png | みんなのAV 的公开图标缓存：`https://www.google.com/s2/favicons?domain=minnano-av.com&sz=64`（缓存只有 32×32） | 官方 apple-touch-icon 与 favicon.ico 对 HTTP 客户端返回 Cloudflare 403 |
| github.png | `https://github.githubassets.com/favicons/favicon.svg` | 官方声明的矢量图标，经现有 `link_marks` 渲染 |

取证：javten、fc2ppvdb、avwikidb、github 为 2026-09-30，minnano-av 为 2026-10-01。资源经 `/site-icon/{name}.png` 提供，前端不向图标缓存服务发送访客请求；其余站点沿用 `/site-mark` 的发现与缓存。
