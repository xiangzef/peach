# Peach 交接与长期工作约定

接手时先读这份：跨任务长期成立的判据与约定。运行态见 `STATUS.md`，部署与设置见 `OPERATIONS.md`。

首次设置服务只负责配置，不启动账本任务恢复、关注和订阅轮询、推送发现、云下载对账或挂载检查。`tray-setup.err.log` 中的 `sqlite3.OperationalError: unable to open database file` 可由尚无账本时启动下载对账触发，不能据此判断媒体目录不可读。设置完成后仍回到首启页时，核对实际数据目录：启动落点通过 `state/data-root.txt` 定位自选目录，托盘切换服务时同时迁移单实例锁，并更新迁移检查与查看日志的路径。CloudDrive2 可部署在 NAS，Windows 通过映射盘符读取共享目录，本机软件安装检测只作提示。

## 界面、媒体与复核的既定判据

界面门槛见 `.claude/skills/peach-web-ui/SKILL.md`，这里只留代码外的判据。

- NFO 见 [docs/REUSE.md](REUSE.md)；[Banner](https://vercel.com/geist/banner) 取证见 `vercel-geist-library-banner.md`。
- 凭据焦点外扩 3px，正文左右留 4px；输入框可收缩，验收所有裁切祖先。
- 截图与视觉验收的画面保护：SFW 模式（设置面板「内容显示」组，`#censorSetting`，localStorage `peach-censor`）默认关闭、不在导航栏。只在截图要交给会审查内容的模型（自动视觉审查或外发工具）时开启，用完关掉；普通个人浏览一律不遮挡。
- 卡片实体链接必须由同一个 `{kind,name}` 结构生成，不许先独立选显示名、再按别的字段推断类型；账本 `size` 为空或 0 时显示「大小未知」，不伪装成 `0 MB`。
- 排除竖屏是首页取景而不是全局过滤器：`exclude_vertical` 进搜索或实体列表会让按名字搜竖屏视频返回 0 结果，`test_only_the_default_home_list_drops_portrait_videos` 守这条线。
- 竖屏带整行占位，插在本页新增那几行的某个行边界上（`frontend/src/react/catalog-grid/catalog-grid.ts` 的 `shortsBoundaries`），首尾各留至少一行，不额外拉视频补余位。
- 关注卡片、标题和 Mix 集合行都先打开站内详情层，可播放媒体走 `/follow-stream`，关闭详情必须停止播放；外部来源页只作详情侧栏的次要入口。
- HLS 分片必须切在真实关键帧上，关键帧表由 `peach.mp4index.keyframe_seconds` 直接读 MP4 的 `moov/stss`；禁止用 `ffprobe -skip_frame nokey`，那会把整个文件解复用一遍，在挂载网盘上等于把片子重拉一遍，读不出关键帧就回退标准 Range。
- 分片用 `-copyts -muxdelay 0 -muxpreload 0` 保持时间戳连续，不用 `-avoid_negative_ts make_zero`（每段都自称从 0 秒开始，拖动进度条会跳错位置）；缓存写在 `stream_root/<asset>/<size>-<mtime>-<秒数>/<index>.ts` 并按最后访问时间淘汰，FFmpeg 并发闸门默认 CPU 核数一半。
- 回收站的物理删除只有 `purge_assets()` 一条实现：先删媒体文件再删账本行，删不掉的整条跳过并在 `blocked` 里回报、前端必须显示；`asset_search` 的 FTS 行由迁移 `0004` 的触发器负责。
- 复核候选文件名带批次日期，代码只认前缀并按实际修改时间取最新一份，不按文件名字典序；候选行必须有稳定主键，缺主键的跳过并计数，绝不退化成行号；候选目录走 `PeachSettings.candidate_root`，不是模块常量。
- `metadata_fields` 的 `item_key` 不带候选身份，一条旧 approved 会盖住之后抓到的新来源值，所以判据是 `review_decision.note` 里记的 `candidate_key` 是否还在这一组：不在就清掉旧判定重新入队，读不出指向的自由文本一律放过。
- 批准的权威值只能来自候选文件本身，请求体里的 `creator`／`tags` 只当确认，不一致直接拒绝；只有 `status=candidate` 的行可批准，未勾选即整条通过但受 `REVIEW_APPLY_LIMIT` 约束。
- 命中推广词不算广告，剥完还剩不剩内容才算：判据在 `web_contract.promo_residue`，`tests/test_ad_judgement.py` 守这条线。`disposal` 同时承载「这是广告」和「这个来源我不喜欢」，不能当纯广告标注集来标定判据。
- 目录多余层的判据是名字冗余而不是「父目录只有一个子目录」，广告标记只剥头尾（`scripts/flatten_release_dirs.py`）；账本只记文件不记目录，任何目录计划落地前都要用真实文件系统复核父目录里有没有旁挂的封面、字幕和空目录。
- 抽帧的 bt709 覆盖只在 stderr 命中坏色彩元数据时重试，无条件重试会让网盘超时的文件每帧白跑第二次，所以不能丢弃 `capture_output` 的错误流。
- Logo 与头像都渲染成方框，候选按实测像素判定，只有 URL 没有实测尺寸不算候选；取源方向、门槛值与站点判据见 [docs/SOURCING.md](SOURCING.md)。
- 小圆标与厂牌大 logo 是两个位置、两种资产：圆标取站点自己声明的那一份并过内容外接框闸门，宽扁字标不参加圆标竞选，`/logo` 的 `variant` 只在真有两份时才分岔（细节见 [docs/SOURCING.md](SOURCING.md)）。
- 改了圆标的取图规则或合成方式必须同时加 `link_marks.RENDER_VERSION`：缓存保鲜期 30 天，不换键的话代码换了用户看到的仍是旧那张。
- 图集就是目录：账本没有图集实体，`/api/photos` 按 `path` 去掉文件名分组、ID 取该目录里最小的资产 ID，同名目录在两个来源下算两个图集。图片墙只读 `/photo-thumb`（Pillow 缩到 640 宽、每张回源一次），原图只在灯箱读；灯箱复用 Swiper，必须等其 CSS 与 JS 都就绪再构造，否则首次打开多图会重叠。
- 人工复核入口固定为 `/review`，候选来自 writer 本机 `generated` 下的 CSV，状态写 `review_decision`；封面抓取的成功、尺寸和缺失，以及九宫格未抽出，都是机械状态，不进人工复核。
- reader 只通过 Peach CA 严格校验的 HTTPS 读 writer 已归一化的 JSON 并原子缓存到本机，先确认目标 `/healthz` 是 `ledger_sync=writer`，writer 离线只展示上次缓存；reader 永久禁用批准、跳过、拒绝和关注管理的写入，不得为修空页面而同步整个 `generated`、SQLite/WAL 或放宽写端点白名单。
- 转载站水印域名不是番号：剥掉 TLD 后与 `IPX219C`、`MEYD911` 同形，`normalise_code_key` 会替它补连字符（`HHD800` → `HHD-800`），JAV 过滤、`display_code` 和 `clean_names` 重命名就全把水印当成作品标识。形态分不开，只有实证名单 `catalog_rules.REPOST_SITE_LABELS` 能分，存压缩形让 `BEI88` 与 `BEI-088` 同命中；加条目先用 `scripts/audit_domain_codes.py` 在真实 ledger 取 `<label>.<tld>` 或 `<label>@` 的路径证据。
- 「什么算番号」只在 `catalog_rules` 一份，脚本一律 import，同一条排除规则只加在其中一份上等于没加；改 `code` 走 `audit_domain_codes.py --apply --backup`，只写复核过的那份 CSV、按原值 `WHERE` 挡住漂移、存疑档不写，FTS 由 `AFTER UPDATE OF name,code` 触发器重建但要核对真跑过。
- 日文标题只认官方源会漏掉 DMM 未收录的作品，这类番号用 `--sources javbus` 单独补候选并写进分区文件，不另起通用批次：复核页只读最新一个通用批次，新文件会把上一批未复核的行挤掉。

## 无摩擦接手

- uv 安装见 README；复用决策见 REUSE。
- Codex 读取 `AGENTS.md`，Claude 通过 `CLAUDE.md` 导入；项目技能共用 `.claude/skills/`，Codex 按入口索引读取。
- 测试入口为 Windows `& .\scripts\test.ps1`、macOS/Linux `./scripts/test.sh`。选测与 CI 见 `TESTING.md`；证据、集成互斥和锁定见 `peach-worktree`。
- 指令维护：按任务读取，缩小技能触发，保留事故边界，用文档、行为与数据任务复核，静态检查不证明效率改善。方法见 [OpenAI](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)。
- 改变运行事实的任务同时更新 [docs/STATUS.md](STATUS.md)；长期规则更新本文件、[docs/REUSE.md](REUSE.md) 或 ADR；可执行流程写成 `.claude/skills/<name>/SKILL.md`。分层判据见 ADR-0015，步骤见 `peach-context-rules`。
- 触发是概率性的：必须每次成立的规则要由脚本、测试或 hook 强制，不能只写成技能。
- 结论、进度、待办和证据写进共享文档或机器可读产物，不靠人转述。
- 用户默认授权 Peach 对话发送项目协调消息，无需重复询问；只处理实际依赖，不唤醒已结束对话收确认。执行与验证见 [执行效率](VERIFICATION_EFFICIENCY.md)、[测试](TESTING.md)。

## 并行智能体与 Git 工作树

操作步骤与平台陷阱见 `.claude/skills/peach-worktree/SKILL.md` 和
`.claude/skills/peach-cross-platform/SKILL.md`。事故证据是 `bba0b77`：测试先提交、实现漏暂存，
所以隔离工作树、逐文件暂存复核、实现与测试原子提交是强制边界；其余复盘已由脚本或测试守住。

## 只存在于聊天中的结论等于不存在

- 复核结论写入带证据和来源的 CSV 或其他持久产物；真实 ledger 写入须另满足授权与备份门槛，执行后对账。
- 结论被修正时所有派生产物必须重建，只改说明文字不够：过期的删除清单比没有清单更危险。
- 直接证据：视觉逐条任务在聊天里说「已保存」但 `asset_tag` 的 `source='vision'` 为 0，根本没有写入步骤；`disposal-candidates.csv` 在 `BNST033` 修正后未重建，把真实 3.2 GB 正片列为待删。
- 解析固定件只用抓回来的那份 HTML，判据与实例见 [docs/SOURCING.md](SOURCING.md)「缓存与重试」。
- Claude 的 `.claude/settings.json` 配了 Stop、StopFailure、SessionEnd hook，用 `${CLAUDE_PROJECT_DIR}/.venv/Scripts/python.exe` 调 `scripts/job_status.py --write --hook-event`：只记脱敏生命周期摘要，从 ledger 与产物重算数字后原子写入 `peach-data/state/job-status.md`，不复制 prompt、response 或凭据。
- 那份产物不进 Git，[docs/STATUS.md](STATUS.md) 只留一行指针；只有主检出的会话写这份状态，隔离工作树里的不写。强制杀进程或断电时 hook 不运行，下次调用会补上。

## 中文文档写作规范

- 全部中文内容（README、`docs/`、ADR、技能正文、界面文案）按用户级技能 tech-doc-style-chinese 写作：
  事实优先、可扫读、不新增原文没有的数字与结论；规则只作用于可见正文，代码、路径、字段和命令原样保留。
- 来源 https://github.com/Fenng/Tech-Doc-Style-Chinese （MIT），每台机器用 `npx skills add Fenng/Tech-Doc-Style-Chinese -g` 装一份，Claude 与 Codex 共用，`npx skills update -g` 升级。
- 分类与界面表达见 [文档与界面文案](WRITING.md)。正式入口执行 seiso 稳定规则与 `scripts/check_copy_final_state.py`；实验规则与风格由人工复核。
- Peach 覆盖上游默认三处：智能体入口文件保留称呼「你」（术语表已定义其含义）；`DOM/CSS/JS` 是证据 <!-- copy-lint-disable-line -->
  三元组的固定写法，不展开成 JavaScript；`对齐`、`复盘` 是已注册的项目术语与技能触发词，不替换。
  其余上游黑话词（兜底、落盘、闭环、链路）一律改写成具体机制。

## 参考产品证据登记

- 目录树与面包屑：2026-10-17 取得 BoardUI registry 源码，版本、SHA-256 与适配见 [BoardUI 适配](BOARD_UI.md#目录浏览)。保留首页结构，目录用途由用户确认。官方实时示例未取得。

- Open Claude UI：[设计准则](DESIGN_GUIDELINES.md)与[取舍证据](reference-snapshots/open-claude-ui.md)。

- 收藏窗口：[BoardUI 核验](BOARD_UI.md)。

- Folia 播放墙（AGPL-3.0）：[源码与适配](reference-snapshots/folia-video-wall.md)。独立 `/wall` 的排布、动效、媒体交接与验收见取证正文；原文登记为 `folia-wall-blocks`／`folia-wall-reflows`／`folia-wall-motion`／`folia-wall-style`。上游实时交互未取得。

- 依赖与参考来源的本轮判断见 [上游复核](reference-snapshots/upstream-review.md)：原文快照按哈希与 revision 接受，人工取证笔记保留；amane 桥只消费站点与网络层。
- amane 的实体收藏与按需比较图只作产品语义参考；收藏、保存筛选复用当前 profile。自定义来源采用 OpenAver 的声明式边界，主动收窄为[单步 JSON](CUSTOM_SOURCES.md)；[外部播放](EXTERNAL_PLAYERS.md)通过客户端网络地址，媒体不改名、不移动。
- BoardUI：[创作者别名表格与关注分页](BOARD_UI.md#创作者别名与扫描操作)、[Board、Link Button 与搜索动效](BOARD_UI.md)、[复核与配置灰色 Pills](reference-snapshots/board-review-layout.md#次级分类组件)；React 源码 `frontend/src/react/boardui/ORIGIN.md`。
- [Geist 控件](reference-snapshots/vercel-geist-controls-measured.md)；[复核操作](reference-snapshots/vercel-review-actions.md)；[README 维护](README_MAINTENANCE.md)；设置：`reference-snapshots/geist-settings.md`。

版本与差异见 `docs/reference-sources.json`、`docs/reference-snapshots/`，流程见
`.claude/skills/peach-reference-evidence/SKILL.md`。本节只索引快照，不复制测量值；给不出可重抓
字节的实测不登记，理由写进快照正文（`tests/test_reference_updates.py` 拒收没说明的快照）。

- PikPak 网页端会话、刷新请求与签名常量，以及用户脚本的取法：`pikpak-web-session-measured`（ADR-0093）。
- 渐变参数模型、`in oklab` 插值与噪点叠层：`feralui-gradients-measured`；工作台与配色圆钮：`feralui-studio-boardui-accent-measured`。
- 相关推荐算法：`openaver-related-ranking`，固定 revision，只参考 Tag IDF 与结构化共同点，MMR 和稳定破同分是 Peach 自加，不复制上游界面或源码。
- 网格、控件半径、语义 token 与中间省略：`vercel-geist-grid`、`vercel-geist-controls-measured`、`vercel-geist-middle-truncate`；中间省略的适用范围见 [docs/REUSE.md](REUSE.md)。
- 统计与口味层级，Note／Progress／Gauge／Context Card 等控件：`vercel-geist-semantics-measured`、`vercel-geist-note-progress-switch-analytics`、`vercel-geist-fieldset-scroller-empty-state`。
- 分类切换条属于 Tabs 的 secondary 变体而不是分段器：`vercel-geist-tabs-secondary-measured`。
- 表格、排行与面包屑：`vercel-geist-table-ranking`、`vercel-geist-breadcrumbs`；同形可比较数据才用语义 `table` 并用 tabular numerals，内容标签是固定 Top 排行和直接筛选，不伪装成可排序数据表。
- 设置 Dialog 动效、搜索期 Spinner、后台 Loading Dots 与 busy 按钮：`vercel-geist-command-search-loading`；中性说明 Note：`vercel-notifications-note`；具名动作 Toast：`vercel-geist-toast`；确认弹层（2026-09-06）：`vercel-geist-modal-measured`。
- 资料页阅读顺序与照片入口：`beeg-profile-layout`；只凭用户截图：JAV 标题 `jav-title-user-screenshot`、悬停快退／快进 `hover-seek-controls-user-screenshot`、搜索下拉 `search-dropdown-user-screenshot`。
- 播放器控制栏、设置浮层与全屏几何：`youtube-player-controls-user-screenshot`；沉浸页版式：`youtube-shorts-immersive-user-screenshot`；统计历史：`youtube-stats-buffer-measured`；小窗与右键菜单：`youtube-miniplayer-measured`；手机顶栏：`youtube-mobile-topbar-measured`。不复制字幕、睡眠定时与自动播放按钮。
- 追更与文件站的凭据与解析边界：`f95-masked-gofile-media`、`follow-fanbox-gofile-paheal`、`fanbox-browser-transport`、`rule34-follow-tags-and-collections`；厂牌 Logo 候选发现：`fiu758-studio-logo-discovery`，只作发现来源不作真相源。
- 通用评审清单与报告型页面版式：`vercel-web-interface-guidelines`、`vercel-report-design`。
- 按内容类型的来源链与逐站取舍：`amane-content-routes`，链上只放 Peach 已接的解析器，候选复核与不生成 NFO 是差异；同类馆藏管理器的信息组织：`readme-yingku`，源码未公开，据 README、5 张演示图与论坛 8 张截图测读。
- 默认 Note、只读提示和 info 入口复用本地 Lucide 圆圈 `i`（2px 描边、圆端点），不复制未开放许可的 Geist 私有 SVG。
- 原地换态动效的形态与参数（字形、读数、骨架、开关、成功、失败）：`transitions-dev-measured`。
- 统计与口味页的柱状、径向、雷达图：`evilcharts-registry`，逐字复制与差异见 `frontend/src/react/evilcharts/ORIGIN.md`；热力与流向图自绘（ADR-0076）。

## 批处理边界

失败值、磁盘闸门、限流、续跑、流量与进程规则统一见
`.claude/skills/peach-batch-jobs/SKILL.md`；当前批次数量与运行进度只写 `peach-data/state/job-status.md`。
采集脚本的整页缓存、限速与传输重试集中在 `peach.page_cache.Site`，判据见 [docs/SOURCING.md](SOURCING.md)「缓存与重试」。

## 身份、来源与标识采集

采集只出复核 CSV、规范名与别名、实体合并、取证判据与 Cloudflare 站的取页边界都在 [docs/SOURCING.md](SOURCING.md)「采集判据」「命名与身份合并」等节，这里不另写。

## 流量与代理诊断工具

- 抓取入口的复用与复现缺口见 [审计](SCRAPING_AUDIT.md)。
- Windows 用 FlowLens（`http://127.0.0.1:9091/`；API `/api/v1/connections`、`/summary`、`/status`）查流量。经 Mihomo 的 `DIRECT` 可观测；绕过它的记「未观测」，不推断为零。
- macOS 的流量诊断统一使用 Stash Dashboard。

## 数据安全

- 真实 ledger 是写入者本机 `peach-data/database/ledger.db`（WAL），正常浏览会合法写入播放与行为字段；平台绝对路径以 [docs/STATUS.md](STATUS.md) 为准。
- 测试必须使用临时 SQLite、媒体和全部缓存根，不得写真实 ledger 或 `generated`；FastAPI 测试须显式传入 snapshots、posters、photo-thumbs、transcodes、stream-segments、按 asset 生成的头像与 covers。
- 可重建缓存的删除边界、已应用迁移不可改写与真实迁移的操作序列见 [docs/OPERATIONS.md](OPERATIONS.md)「迁移、备份与运维脚本」。
- 外键 `ON DELETE` 是安全网不是删除路径：运行时连接不开 `PRAGMA foreign_keys`，物理删除仍走 `ASSET_REFERENCE_TABLES` 与 `web_playlists` 的显式 DELETE；重建被别人引用的父表要在迁移首行写 `-- peach:foreign_keys=off`，改名那步开 `PRAGMA legacy_alter_table=ON`，判据见 `0025`。
- 外置盘目标只保存 `media`，代码、运行数据、venv 和 worktree 在两台机器各自的内置盘；`peach-data` 不进入仓库，也不整体交给文件同步，分通道边界见 ADR-0017。

## 运行与部署

CloudDrive 见 [docs/CLOUDDRIVE.md](CLOUDDRIVE.md)；部署、托盘重启、双机同步、版本与更新、网络与进程边界、验证口径见 [docs/OPERATIONS.md](OPERATIONS.md)。

- 两台机器可同时跑服务，但同时写入会很快冲突转只读；「接管 Ledger 写入」的短路与拒绝条件见 OPERATIONS。
- 网盘目录整理后的对账、两档清理与孤儿记录见 OPERATIONS「资源同步」。

## 当前架构真相

- Ledger 拥有真相和行为；服务运行期媒体只从文件系统解析，Stash 只剩账本里的溯源数据（ADR-0021、`STASH.md`）。
- 规范女优、厂牌、标签、创作者进入 `entity`、`entity_external_ref`、`asset_entity`；扁平 `asset_tag` 和 creator/studio 字段只是兼容投影。按实体 id 取数先过 `entities.resolve_entity_id`：合并留下的墓碑把旧 id 指到目标（ADR-0088）。
- `asset.disposal` 只有三个值：空是在库，`trash` 是用户丢进回收站，`vanished` 是文件已不在盘上但带着个人记录；判在库时两者都排除（ADR-0087）。
- FastAPI 与前端保持单体部署，在线来源和 AI 只通过显式适配器进入；AI runtime 与推理 API 的协议边界见 ADR-0003。
- 前端按 ADR-0031 走 strangler 迁移：新页面进 `frontend/src/react/`（React + Tailwind + BoardUI 源码），逐页替换，不做整站重写；分发阶段见 ADR-0023。
- 页面与交互的已定型行为写 [docs/REUSE.md](REUSE.md)，由 API 与测试守住；版本号、像素值、批量大小与性能测量是实现快照，留在测试或参考快照，本文件不抄。
- `/taste` 只读合并 Peach 行为与本机私有浏览历史，明确以浏览器记录为主要画像、Peach 内部为辅助证据，分别排序，不把「不合口味」自动归因或降权到 Tag。
- 查询词里的负号项整体排除，下划线是组合词边界的一部分，不得把 `-ai_generated` 拆成正向 `generated`；模糊时长旧 Tag 只作兼容识别，不进入口味、索引、详情和筛选状态。
- 原始 URL 与标题不进入页面或 ledger；上传原件存 `sources/taste-history/imports`，移除数据源只清理规范化分析库，不删原件。浏览器数据库解析固定复用 `browserexport==0.4.4`，运行中浏览器先由 SQLite backup API 取一致快照。本机发现不等于跨机同步，跨机数据要显式导出、传输并按来源去重合并。
- 追更连接器、凭据、变体和跨站归组以 ADR-0019 为准；关注页顶部标签筛选与卡片只用来源明确标记为 `general` 的内容标签，详情页与在线索引保留全部来源标签并按类型着色，未知类型不猜成 `general`。
- FANBOX 正文统一经过 `peach.fanbox.normalize_fanbox_post`，边界见 [docs/REUSE.md](REUSE.md)「必须复用的成熟实现」。
- FANBOX Cookie 与 Gofile token 都是本机可选凭据，只进各自站点的请求头，不进 URL、证据、ledger 公开投影或浏览器 JSON；只允许公开 JSON，不解机器人质询、不执行网页脚本、不读付费内容。
- 云下载的 CloudDrive2 令牌与 PikPak refresh token 存本机 `CredentialStore`，不列为可同步字段，不进 URL、日志与 ledger（ADR-0089）；PikPak 浏览器登录的专用 profile 在凭据根下 `browser-pikpak/`，取完会话即关窗，续期只归 Peach（ADR-0093）。
- Gofile 把 contents API 限给 Premium：`error-notPremium` 按套餐限制报告，不误报成 token 无效；没取得文件列表时保留分享页，不得声称已取得视频。
- 同一篇 FANBOX 可含多个 Gofile 文件夹：作品级仍是一个来源合集，媒体保留文件夹 id 与正文标签并在详情队列内分段，不拆作品也不压平混排。
- 自动追更用 APScheduler，只在 ledger writer 启动，频率存 `peach-data/state/follow-schedule.json`，默认每小时且启动后等满一个间隔，不要改成启动即抓；单实例、与手动检查互斥见 [docs/REUSE.md](REUSE.md)「必须复用的成熟实现」，reader 只显示不可用状态。
- 账本路径兼容和抽帧失败处理统一见 `.claude/skills/peach-cross-platform/SKILL.md` 与 `.claude/skills/peach-batch-jobs/SKILL.md`。

## Web 性能边界

- 列表必须分批构建；首批才计算总数，后续多取一条判断是否还有下一页。无限滚动同一时间只允许一个追加请求。
- 聚合查询禁止按实体发 N+1 SQL；相邻请求可复用缓存，但异步响应必须核对请求序号和当前路由，旧响应不得覆盖新页面。
- 远端媒体 hover 只读本地预览。沉浸与详情每次加载都带独立 `session`，切片、关闭、失败、换页或替换 DOM 时停止播放并取消旧会话：只清浏览器的 `src` 停不住 CloudDrive 预读或 FFmpeg。
- Mix 只按已解析且可播放的视频计数，不按回复数或网盘页数计数。

## 恢复入口

重构时从活动目录删除的 deprecated 脚本与按日期文档，Git 历史仍可恢复。旧 `_SHARED_STATE` 与重构前的
根仓库元数据备份在各机 `peach-data` 的 `state`／`archive` 下，只作恢复证据；位置以
[docs/STATUS.md](STATUS.md) 为准，Mac 的 `archive` 是指向外置盘的符号链接，盘不在时读不到不等于备份没了。
