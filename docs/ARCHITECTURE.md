# 总体架构

这份文档讲 Peach 由哪几块组成、各块管什么、数据怎么流动，以及哪些方向明确不做。每项取舍的理由在 `docs/adr/`。

## 产品形态

Peach 是一个 FastAPI 模块化单体：逻辑上前后端分离，部署时仍是一个进程。默认单用户、本地自托管；在线追更、外部元数据和可插拔 AI 都是正式能力。

应用端口不直接暴露到公网。远程访问走 VPN、Cloudflare Tunnel（默认关闭，须先设访问密码，见 [docs/OPERATIONS.md](OPERATIONS.md)），或 DDNS + 反代 + HTTPS。

## 核心边界

每一块只管一件事，跨块只走下面写明的接口。

1. **Ledger**：资产、行为、来源和知识的唯一真相源，用 SQLite，单用户规模够用。硬盘上那份是权威副本，两台机器各持本地工作副本，由 `peach.sync` 做单写者复制：拉取、回写，冲突时转只读，**不做多主合并**。
2. **API / 应用层**：FastAPI 承载页面、JSON、媒体响应和写入边界。`api.py` 只负责组装，路由分 `routes_auth`、`routes_pages`、`routes_media`、`routes_configuration`、`routes_api` 五个 APIRouter；`/api/{route}` 由 `web_router` 的 handler 表分派到 `web_catalog`、`web_entity`、`web_stats`、`web_batch`、`web_follow` 等域模块。
3. **平台层**：`peach.platform` 是账本路径与本机挂载点之间唯一的翻译层。账本只用 Windows 盘符记路径，读取时按「来源的声明根 → 本机挂载点」翻译：来源即 `asset.location`，两侧由设置文件的 `[media.locations]` 与 `[media.mounts]` 给出，`PEACH_MEDIA_MOUNTS` 可临时覆盖。没有挂载点的来源落到不可达根，整体按脱盘处理。CloudDrive 在 Windows 是盘符、在 macOS 是 macFUSE 挂载点，差异全部收在这一层。
4. **Media Engine**：FastAPI 只持有一个 `MediaEngine`，本地文件与挂载网盘都是原生后端。远端 MP4 默认走标准 Range；`stream-plan` 只在显式开启时给出按时间生成的 HLS 片段。HLS 是例外而不是默认，因为 HEVC-in-TS 会静默黑屏（ADR-0016）。
5. **Web**：单页、移动端优先。页面按 ADR-0031 从无构建步骤的 `web/` 逐页迁往 `frontend/` 的 React + Tailwind v4 + BoardUI 源码，构建产物提交进 `web/dist/`。只做逐页替换（strangler），不做整站重写，细节见 [docs/FRONTEND.md](FRONTEND.md)。
6. **AI Provider**：`InferenceProvider` 与 `AgentProvider` 分开。AI 只产出带来源和置信度的候选。
7. **Profile**：默认单用户，数据模型预留 user/profile，不引入完整账号体系。
8. **追更来源**：RSS/Atom 等成熟协议先归一化为只读候选；原始证据、复核和 ledger 写入分层。「想要」清单 `want_item` 按番号登记库外作品，入库时按番号自动对账（ADR-0090）。
9. **任务系统**：来源成本、磁盘闸门、进程归属、进度和来源证据由 Peach 自己定义；HTTP、调度、媒体探测、图片与协议解析用成熟组件。
10. **下载**：Peach 只把磁力交给网盘离线（115 经 CloudDrive2 gRPC，PikPak 直连），文件落地后仍由推送发现与扫描登记入库（ADR-0089）。
11. **HTTP / 搜索**：网络适配器默认共用长生命周期的 HTTPX transport。例外有三个，都有证据登记：FANBOX 公开 `post.info` 用固定版本的 `curl_cffi` 保留 Firefox TLS/HTTP2 传输特征，但不求解质询、不登录、不读付费内容；Cloudflare 后面的来源经 `peach.browser_transport` 驱动本机浏览器取页（ADR-0065）；115 云下载经 CloudDrive2 的 gRPC 接口提交，`grpcio` 精确固定版本（ADR-0089）。作品全文搜索用 SQLite FTS5 trigram，短查询回退 LIKE。

## 数据流

```text
本地/网盘/在线来源 -> 索引/探测 -> ledger.db
                                  -> FastAPI -> Web/播放器
AI/外部元数据 -> 经复核的候选 -> ledger
```

## 明确不做

- 微服务、消息总线、PostgreSQL
- 一次性整站重写前端（只按 ADR-0031 逐页迁移）
- 抓取或保存 ChatGPT/Claude OAuth token
- 把 Stash 私有目录或 GPL 构建当作 Peach 的稳定打包依赖

Stash 遗留的数据缺陷与许可证边界见 [docs/STASH.md](STASH.md)；复用与自研的边界、旧脚本的继任关系见 [docs/REUSE.md](REUSE.md)。

## 运行数据目录

Windows 与 macOS 各自在内置盘持有代码、`peach-data`、`.venv` 和 worktree；外置盘只提供
`R:\media` / `/Volumes/RESOURCES/media`。跨机只有三条通道，各走各的，一条出故障不由另一条代替：

- 代码与任务分支走 GitHub，worktree 目录各机本地重建；
- 账本走 Peach 单写者复制；
- 图片等生成产物走 Syncthing 单向同步。

其余运行数据按 durable artifact 与本机状态拆开，禁止整体同步，边界见 ADR-0017。

`peach-data` 与代码仓库分开放：默认取仓库同级的 `peach-data/`，`peach init --data-root` 可改，
环境变量 `PEACH_DATA_ROOT` 覆盖它；本机坐标写在 `<数据根>/config.toml`。目录分层如下：

- `database/`：SQLite 真相库。本地是工作副本，血缘记在同目录的 `ledger.db.sync.json`
- `generated/`：快照、海报、头像和厂牌 Logo；`follow-assets/` 与 `link-marks/` 是关注头像、来源图标与外链圆标的可重建缓存
- `sources/`：浏览器、追更、盘点和导出等不可变原始输入
- `state/`：人工维护的本机状态和锁
- `secrets/`：仅本机保存的凭据材料
- `logs/`：当前运行日志
- `archive/`：历史迁移证据和备份
- `inbox/`：等待处理的临时导入
- `tools/`：FFmpeg 等本机托管运行时；二进制和许可证不进入 Git

这是约定的分层，不是每台机器的实测形状。Mac 上 `generated` 是指向 `artifacts` 的符号链接，
另有 `review`、`tmp`，且 `archive`/`sources`/`tools` 指向外置盘。动手前以 [docs/STATUS.md](STATUS.md) 为准。
