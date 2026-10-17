# 抓取复用与复现审计

这份审计回答两个问题：抓取脚本有没有重复造轮子；换一台干净机器、换一个用户，能不能复现同样的抓取结果。

核验日期：2026-09-05；审计基线：`349048f`。架构方案见 [ADR-0024](adr/0024-mark-manifest-not-bundled-bytes.md)，逐入口的基线结论见 [审计 CSV](scraping-audit.csv)。CSV 记的是基线时的问题，哪些已经修好以下一节为准。

## 实施状态

基线指出的复用问题已按下面的方式收敛：

- 5 个内部重复入口改用共享限流：封面的 `HostLimitedTransport` 建在 `scripting.HostLimiter` 上；事务所名册、人物链接、厂牌社媒头像三个入口用 `scripting.RateLimiter`；图标下载走共享的 16 MiB 有界 transport，保留首页单次请求缓存和图像策略。
- 域名归属用离线 tldextract 5.3.2（实现在 `peach.link_repair`），GitHub Pages／Blogspot 独立租户与日本域名 POC 通过。
- 官网探测与 page_cache 显式持有自建 client 的关闭所有权。
- `/scraping` 接入了定点高清封面、来源网络和 FC2 Cookie 配置。完整下载后重新核对实际尺寸，保留原图字节，拒绝低清覆盖。接口、凭据隔离与实际消费范围见 [来源采集](SOURCING.md)。

仍然开放的：

- Instagram：Instaloader 4.15.3 的 Bambi／LINX 匿名 POC 均为 ConnectionException，独立登录会话未取得。匿名失败不能解释为所有登录用户都失败，库里有接口也不能解释为能稳定成功。
- `studio_icons.Fetcher` 仍自带重试与退避，错误分类和缓存作用域还没并进共享实现。
- ADR-0024 整体还缺来源清单、完整批量 GUI、标准模式、子进程网络统一，以及跨用户／平台验收，见「新用户复现差距」。

## 审计基线范围与结论

扫描 `scripts/harvest_*.py`、`fetch_*.py`、`scrape_*.py`，加上有来源请求的头像审计、厂牌本地化、Babepedia 匹配与链接重发现，共 **17 个业务入口**。同时核对共享 HTTP、页面缓存、图像候选缓存、Javinizer-Go 适配、关注连接器和凭据 GUI。发布检查、连通性验收、纯离线导入／安装脚本不计入业务抓取入口；这个分母不代表 Git 历史中的全部脚本或所有 provider 类。

按每个脚本的最高风险归类，互不重复：

| 分类 | 数量 | 判定含义 |
| --- | --- | --- |
| 外部成熟能力复用缺口 | 2 | Instagram 未完成成熟头像接口验证；域名归属使用自写后缀算法且有反例 |
| 内部基础能力重复 | 5 | 封面、图标、名册、人物链接与厂牌社媒头像各自计算请求节拍，与共享能力并存 |
| 复现／生命周期缺口 | 2 | FC2 Cookie 仅 CLI 接入；官网探测的 client 关闭边界有缺陷 |
| 未发现足以判为重复造轮子的证据 | 8 | 有直接复用、固定上游参考或明确领域差异；不是永久豁免 |

基线时能具体指认的复用问题涉及 **7/17 个入口**，另有 2 个入口有复现或运行缺口。「写了 Python 脚本」「使用站点专用选择器」「没有直接依赖整个下载器」都不算错误。

## 基线问题留下的判据

问题本身已修的，这里只留以后还用得上的判断规则。

### 社媒头像：缺的是成熟能力验证

`harvest_social_avatars.py` 对 Instagram 只记录链接，`studio_icons.named_avatars` 消费人工提供的 CDN 地址。源码和 REUSE 里都没有 Instaloader／gallery-dl 头像解析的成功 POC 或拒绝证据，所以不能拿局部 `web_profile_info` 429 和页面小图推出「自动解析不可行」。

Instaloader 4.15.3 的 `Profile.profile_pic_url` 实现含 `hd_profile_pic_url_info` 与 `profile_pic_url_hd` 分支；gallery-dl 也有 `InstagramAvatarExtractor`，支持 `/USER/avatar/` 与登录／匿名分支。两者都是应比较的成熟能力，但登录态跨账号 POC 未执行（未读取 Cookie），「已有接口」只等于接口存在。

人工提供的 Bambi 图片直链与本机 `agency-avatars.json` 的图片文件编号一致：不带 Cookie、严格 TLS 请求返回 200、JPEG、1000×1000、92,068 字节，原图 SHA-256 为 `fc004f50edd9a3d684582eacf72b0521883ba42d40307304db062dc0cc931c1f`。文档不保存临时签名 URL。这只说明该直链当时可下载，地址发现本身没有测过。

采用前的做法：首选验证 Instaloader，不同时加入两套正式 Instagram 运行时。记录 Python／桌面包兼容性、依赖体积、会话导入、限流与账号身份结果后再决定；GUI 会话导入不是手工维护 CDN URL。

### 链接归属：可注册域相同不等于同一实体

基线的自写后缀判断把 `a.github.io` 与 `b.github.io` 都判成 `github.io`，独立租户因此被当成同站；只测常见日文域名证明不了通用正确。tldextract 必须开 private suffix 处理并固定可离线使用的 PSL 快照，不能照搬默认参数。即使可注册域相同，账号页与共享主机路径仍要独立核验身份。

### JAV 封面：该复用的是限流，不是高清策略

限流扩展共享的 `HostLimiter`，不能直接替换成会让未配置主机不限速的写法。高清候选聚合本身有充分复用依据：REUSE 登记了 Javinizer-Go 固定 revision 的 DMM 映射和 MDCX 的 Prestige 协议模型。离线快照、严格番号核对、Range 尺寸探测和像素比较是 Peach 的质量策略，保留。

### 厂牌图标与页面缓存

一次首页解析产生多个候选、图片判形和候选质量策略归 Peach；下载、错误分类、字节上限和缓存作用域应走共享实现。`page_cache.Site` 只适合公共页面缓存，不加作用域和 TTL 就不能拿来缓存登录资料。统一不是把所有调用硬塞进现有类，而是在已用模块上补齐共用契约。

### 什么算重复的请求节拍

只有独立的节拍实现（「interval 减去 monotonic 时间差，再 sleep」）才计为重复，`scripting.RateLimiter.wait` 已覆盖这件事。来源特有的退避策略、单纯调用 sleep 或小型 HTTP 包装不自动计入：Babepedia 的失败策略留给统一错误语义处理，不凭它出现 sleep 就算重复。一个限流重复也不是重写整个入口的理由。

### FC2 与官网探测

- `fetch_fc2_metadata.py` 复用了 HTTPX 与按来源的连接配置；评论里的跨号关系与分片判断是领域逻辑，没有成熟依赖能完整覆盖。基线时的问题是网络错误、预算和续跑没接入 GUI／共享服务，不是整套解析在造轮子。
- 官网探测的连接释放问题先修所有权、复测原失败序列，再判断要不要每请求独立 client；不能只凭文字断言 HTTPX 连接池必然泄漏。

## 已有复用与历史证据

- `scrape_codes.py` 调 `JavinizerGoProvider`，由外部 Javinizer-Go v1.5.2 查询，Peach 只做身份、字段候选、来源健康和复核。不是自研整套 JAV scraper。
- `fetch_studio_avatar_candidates.py` 使用 unavatar 解析地址、平台 CDN 下载及 `LogoCandidateCache`。unavatar 是公共服务，随时可能改规则或收费，所以要有无 API key 的可用性测试和服务失败测试。
- Gfriends 索引与头像审计复用原始索引、Pillow 和 `AvatarCandidateCache`；目录名录／本地化入口复用 `page_cache.Site`、`minnano_av`、`javdb`、名字链和 OpenCC。身份消歧仍需 Peach 承担。
- FANBOX 使用 curl_cffi 和 PixivUtil2 固定正文模型；Rule34Video 部分使用 yt-dlp；其余归档／booru 官方接口及 Gofile 边界已在 REUSE 登记。这里只核对复用入口，没有对在线 provider 做端到端验收。
- Git 中可指认的共享基础设施合并包括 `80b04d2`（UA／主机限流）、`053aed5`（番号归一化）、`c374601`（CSV）、`bdeddbc`（头像档位）。存在历史重复与后续合并证据，但不能把已删除实现重复算进当前 17 个入口。 <!-- copy-lint-disable-line -->

## 无代理刮削的实际机制

结论先说：**可用的聚合数据／本地缓存能减少访问每个原站，不会让被阻断的原站凭空可达。**

Javinizer-Go v1.5.2 示例配置默认启用 r18dev，使用面向刮削器的 JSON 与专用 UA；支持按来源代理、CDN Referer、缓存和 r18 dump。dump 需要先取得，缓存中的封面 URL 与原图字节也是两种资源。Peach 没有证明已经接入其 dump 管理。

Movie Data Capture 的配置提供代理开关、超时／重试、来源优先级和仅补缺图；这些是选源与缓存策略，不保证任意地区无代理可达。这里只用其配置作行为对照，不把整个应用加入 Peach；上游绕过验证的可选分支不在 Peach 采用范围内。

高清与代理没有必然关系。多问几个高清源会增加遇到地域或网络限制的机会；普通用户可以先用可达源填齐。即使需要代理，也应由来源连接诊断决定，不能降低已能直接取得的高清图。

### 本机小样本

主机权限下执行公开请求，每个目标每条路线一次，传输失败重试一次，严格 TLS，最多读取 64 KiB，不带 Cookie、不写 ledger。图片尺寸取自真实图片头，未用 URL 字样推断，也未把这次头部探测当作整图完整性校验。

| 目标 | 不使用应用环境代理 | 使用当前环境代理 | 已测图片尺寸 |
| --- | --- | --- | --- |
| r18.dev：ABW-232 JSON | ConnectError，2 次 | 403 HTML，1 次 | 未取得元数据 |
| DMM mono：ABW-232 | 200，1 次 | 200，1 次 | 800×539 |
| DMM 高清：GYAN-017 | 206，1 次 | 206，1 次 | 2184×1464 |
| Prestige：ABW-232 图片 | ConnectTimeout，2 次 | 206，1 次 | 1024×690 |

读这张表要知道的限制：

- 进程存在 HTTP_PROXY／HTTPS_PROXY／ALL_PROXY，但不输出其值。沙箱中的无代理请求均连接失败，所以上表以主机权限复测结果为准；这仍未排除 TUN 或上游路由。FlowLens 的出口证据未取得，不能称「物理无代理」。
- r18 用的是有界通用 UA HTTP 探测，未取得 Javinizer-Go 专用 UA／dump 的等价现场结果，不据此宣称其 provider 不可用。
- 结果绑定当时那台主机和那条线路，换地区或换出口就要重测。取证脚本和脱敏 JSON 在仓库外的 `attic/evidence/20260905-scraping-reproducibility/`，不随仓库分发。

## 新用户复现差距

这张表是 ADR-0024 还没做完的部分：左列是能力，中列是当前源码做到哪一步，右列是要求。

| 能力 | 当前源码 | ADR-0024 要求 |
| --- | --- | --- |
| Cookie GUI 粘贴／撤销 | `/follow-manage` 已有表单；写入运行 Peach 的主机；GET 只返回状态 | 共用该存储与接口扩展来源，避免第二套密钥文件格式 |
| Cookie 有效性 | 已配置主要是字段存在性 | 保存与有效分开；独立有界验证、过期和需验证状态 |
| Cookie 文件导入 | FC2 CLI 使用 Netscape 文件 | GUI 域限制导入、说明会话位置；不接受不可信 pickle |
| 浏览器直接导入 | 未发现统一 GUI | 经用户选择后调用成熟库；平台不支持则文件／粘贴回退 |
| 网络选项 | `Site.via_proxy`、HTTPX 环境、CLI 子进程等多条路径 | 按来源明确网络模式，各 transport 与子进程一致 |
| 高清模式 | 封面脚本有 Range 和全候选比较，图标有够用线 | 标准与最高可得画质独立选择；共享候选、预算和缓存 |
| 工具安装 | `resolve_javinizer_binary` 查版本固定目录、环境变量或 PATH | 干净机器 GUI 诊断依赖并安装经校验的平台制品，失败保留公开来源 |
| 一次性映射／日志 | 部分路径依赖本机候选 CSV、人工 handle 和成功 URL | 导出可公开来源定位与身份线索，缺失可从原站重新发现 |

实施顺序：连接生命周期与归属正确性 → 共用网络／缓存／预算 → GUI 配置与依赖诊断 → Instagram POC → 清单导出和干净机器验收。不得先批量引入新依赖或重写全部站点解析器。

## 外部核验入口

- [Javinizer-Go v1.5.2 配置](https://github.com/javinizer/javinizer-go/blob/v1.5.2/configs/config.yaml.example)：来源、代理与 CDN Referer；固定 revision 的高清差异见 REUSE。
- [Instaloader 4.15.3 头像实现](https://github.com/instaloader/instaloader/blob/v4.15.3/instaloader/structures.py)、[安装依赖](https://github.com/instaloader/instaloader/blob/v4.15.3/setup.py)、[MIT 许可证](https://github.com/instaloader/instaloader/blob/v4.15.3/LICENSE)、[会话导入](https://instaloader.github.io/cli-options.html#login-download-private-profiles)、[429 限制](https://instaloader.github.io/troubleshooting.html)。
- [gallery-dl Instagram 提取器](https://github.com/mikf/gallery-dl/blob/master/gallery_dl/extractor/instagram.py)：GPL-2.0，对照源码，未复制或引入；采用前锁定 revision 与真实输入验证。
- [Movie Data Capture 配置](https://github.com/mvdctop/Movie_Data_Capture/blob/master/config.ini)：只作策略对照，不作为安装推荐或当前站点可达性证据。
- [HTTPX 环境变量](https://www.python-httpx.org/environment_variables/)、[代理](https://www.python-httpx.org/advanced/proxies/)：环境和显式代理的语义。
- [Public Suffix List](https://publicsuffix.org/list/)、[tldextract](https://github.com/john-kurkowski/tldextract)：域归属的成熟实现。
