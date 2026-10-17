# Peach 运行核验

最后核验：2026-10-17

查 `/healthz`；[待办](PRODUCT_BACKLOG.md)、[复用清单](REUSE.md)、[长期约定](HANDOFF.md)。

## 运行态

- [Docker](DOCKER.md)
- 名册：艺人（含动画作者）｜卖家｜在线；素人须有非职业出演证据，FC2 仅筛作品。
- 公司资料、FC2 卖家按来源补空；厂牌去重 6 组。回执 `peach-data/review/`。
- 核查：`peach-data/review/creator-boundary-delivery.md`；StraplessDildo 归厂牌。
- 关注作者 25 位、来源 111 条、身份关联 71 条、别名 30 条（ADR-0096）。
- 验收：`peach-data/review/entity-cold-missav-verification.json`。
- 身份合并 18 组；版本核查：`peach-data/review/version-evidence-review.md`。
- JAV 头像 817，水印待复核 38；档案 17、候选 253、官方封面 2；[选图规则](adr/0102-profile-avatar-priority.md)。
- 「整理」（ADR-0039）支持预览、执行、回滚；英文视频名分词 169 条。
- 产地是独立维度、JAV 是其投影：`region` 空时按厂牌、创作者、番号逐层推断，不落库；韩国 MIB 不算 JAV。
- Windows 托盘自动恢复；重启 `restart_windows_tray.py --source`；代码、数据在内置盘，媒体在外置盘。
- 托盘用普通权限：提权看不到 CloudDrive 的 `A:`/`B:`，误报脱盘。
- Windows：80→HTTPS、LAN:443；`peach-win`。重启、CA、桌面/手机通过。
- 封面2144，v13、人脸v4；JavDB 0。
- 收藏、续播、播放墙续页；[目录浏览](DIRECTORY_BROWSING.md)。
- `/healthz` 报 `configurable=true`；配置、选目录共用连接判据；托盘管理 HTTPS 地址、端口及重载。
- 首启恢复配置；更新保留数据，安装暂停采集，运行后续跑；见 [运行与配置](OPERATIONS.md)。
- 密码未开，局域网匿名可读；首启可跳过密码，配置页可改可关，登录可记住设备。
- macOS 是 reader，代码与 `peach-data` 在内置盘；`peach.local` 经 8900/8443 和 pf 提供 80/443，GET 正常、写入回 409。
- 两端用本机 CA，私钥、凭据不跨机；代码 Git、账本单写者复制、图片 Syncthing；坐标 `<数据根>/config.toml`。
- Windows ledger `0047`，78,520 行；字幕 195 行（孤立 19），175 部带字幕轨；R 盘暂缓。
- Mac ledger 使用已授权共享副本，`in-sync`；`sources` 在内置盘，`archive`、`tools` 可在外置盘。
- Windows doctor、诊断页通过 CA；本地目录缺失，115/PikPak 可读；密码未开、历史失败为警告。
- Python 最低与默认 3.14；Windows FFmpeg/ffprobe 在 `peach-data/tools/ffmpeg`，macOS 走 PATH。
- amane 0.20.0，安装一致；[功能与接入](reference-snapshots/upstream-review.md)。
- 发行名 `peach`、目录名 `peach-app`；Mac 维护与重启见待办 26。
- 扫描、采集 120 秒无进展预警；资料 90 秒、封面 240 秒超时可重试；见 `state/library-processing-<job_id>.issues.jsonl`。
- 口味、复核、关注按账本、文件版本缓存；女优资料后继每轮存量至多 16 条。
- 下载后处理：16 条旧失败任务保留，部分资产已移动；`task_run` 外键异常 242 条未清理。
- [标签归一](reference-snapshots/tag-vocabulary-audit.md)
- 种子 `2026-10-17.1`：1,199 实体、13 撤销（ADR-0106）；`0047` 已应用。
- 诊断报告操作、托盘重启与严格 CA HTTPS 通过。
- Windows 工具候选构建与 EXE 冒烟通过；未发布，安装/卸载未验证。
- 推送发现开：本地 watch 加 CloudDrive 云端前缀 `/115open→B:`、`/Pikpak→A:`；关注每 60 分钟轮询；自动更新关闭。
- Cloudflare 公网入口默认关，配置页启停前须设密码；临时链接写状态文件，命名隧道限源码部署、令牌存设置文件；整站 `noindex` 与 `/robots.txt`。
- FC2PPV-DB、JAVten、被拦的 minnano-av 经本机 Chrome 取页（ADR-0065），profile 在 `secrets/browser/`。

## 批处理进度

批处理见 `peach-data/state/job-status.md`；目录与垃圾回执见 `generated/library-organize/`，未知归属不填身份。
