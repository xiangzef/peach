# Peach 产品待办

最后核验：2026-10-07。这里只记还没做完的需求和待执行的操作；做完就删，历史去 Git 查。运行数字以 `peach-data/state/job-status.md` 的自动区块为准。

## 待复核的元数据

- amane 0.21.0 桥升级待在独立工作树验证 MGStage 数字前缀搜索、站点字段与失败契约；Peach 独立 DMM 链路的目录与 CID 规则另测，采用范围见 [上游复核](reference-snapshots/upstream-review.md)。

- JAV 发现的历史目录候选、年代与时长偏好、质量参考、近期偏好衰减及可撤回的负向探索反馈待取得并验证，范围与有界采集方案见 [JAV 发现](JAV_DISCOVERY.md)。

- 有码内容标签按 ADR-0100 优先 JavDB；真实馆藏回填待逐资产来源归属预览与同轮授权。歧义词 `口爆/吞精`、`車站性交`、`觸摸打字` 等保留原文复核；已核对的类别身份与译名见 [来源词复核](reference-snapshots/javdb-category-translations.md)。
- 未收录的标签来源词保留出处；「其他内容」分组的 24 个名称见 [标签词表审查](reference-snapshots/tag-vocabulary-audit.md)。
- 新作缓存有 8 种词待复核：受孕、女检察官、性感的、恋物癖、教学、淫乱真实、礼仪小姐、美少女电影。繁简别名已全表覆盖，未知词保留来源原文；逐词表见 [JAV 发现](JAV_DISCOVERY.md)。
- 账号身份来源待复核，当前名册见 `peach-data/review/creators-current-inventory-2.csv`；候选与查询记录见同目录 `creator-identity-findings.json`、`creator-identity-lookups.json`。「しらたま」「ひな」短名不能唯一对应艺人，保留独立身份。
- HIP-ANGEL、Zipang、Kuchiku * Reverse Bunny 与 `gachincoppv-1009-HD` 的对应来源未取得，见 `peach-data/review/identity-simple-source-gaps.json`；JAV 资料补查缺口见同目录 `cached-minnano-identity-audit.json`。未取得来源不构成人物职业证据。
- `FC2-PPV-1625020` 的资产 `6562`：账号「音梓」来自 `legacy:asset`，没有卖家来源证据；女优关系来自 FC2PPV-DB 和 JavDB。待取得发布账号证据或用户复核结论。

## 优先级

数字不带前缀的指「其他开放需求」的编号，「骨架 N」指「已有骨架、尚未完成」的编号，「操作 N」指「待执行的操作」的编号。编号保持稳定，空号不复用；下表按执行顺序排列。每项开工前核对当前主线与验收证据。

| 顺序 | 优先级与范围 | 剩余工作与依赖 |
| --- | --- | --- |
| 1 | P1 搜索与下载 | 43 的资源搜索接已有云下载；42 与 57 的本地下载、续传依赖操作 12 的流量与磁盘预算；骨架 1 还缺 51 的相似匹配、去重与人工替换确认 |
| 2 | P1 诊断 | 46 挂载探测 → 21 doctor 与分级健康检查 → 26 诊断页；12 的生产异常场景验收单列 |
| 3 | P2 元数据质量 | 44 → 操作 36 → 54 → 29；45 的回放与 58 的来源缺陷记录随解析器做；65、61 先核对成本与预算 |
| 4 | P2 前端与交付 | BoardUI 每批一到两页、随功能迁移；23 先量 Windows CI 瓶颈；11、20 的安装验收与 14 的制品支持按依赖推进，再做 15 的教程 |
| 5 | P2 维护与便利功能 | 32 缓存清理、56 源图指纹、59 清洗语料、操作 28 链接失败分类；49、53、62、69 随后；操作 31 的代码清理随相关模块做 |
| 6 | P3 收益待验证 | AI、推荐、向量、镜像、小文件打包、新媒介、原生客户端与浏览器扩展；51 仅把支撑骨架 1 的小样本验证提前，其余未列需求按区块顺序 |

### 已核对的实施状态

待办核对覆盖主线 `e22486f3` 及后续合入，已对照 Claude 文档整理的合入提交 `f215289f` 与后续修订 `e092470c`。下表只覆盖已取得证据的项目，其余条目保留待办状态，不能据此视为逐项验收通过。

| 项目 | 核对结果 | 证据 |
| --- | --- | --- |
| 开发流程 | 隔离工作树自动同步 Python 依赖，主检出只读核对；commit-msg 检查署名、已有 README 声明和分段 | `scripts/test_environment.py`、`scripts/test.ps1`、`scripts/test.sh`、`scripts/check_commit_message.py`、`scripts/githooks/` |
| 首次前端导入 | React 导入钩子各有 30 秒上限，普通用例沿用默认超时 | `frontend/test/islands.test.ts` |
| JAV 与设置结构 | JAV 包含馆藏、按出演者口味匹配的新作与想要；查找资源展示作品资料并保留搜索和磁力输入。设置弹窗管理偏好，Peach 配置按用途分类 | [ADR-0103](adr/0103-jav-hub-and-settings-groups.md)、`frontend/src/react/jav/`、设置与配置组件及回归 |
| 42、43 | 云下载、manko.fun → JavDB → sukebei 直查与 Torznab 后备、体积和质量筛选、入库后正片绑定／定向采集／推广附件隔离／模板整理已具备；本地下载、非 manko 候选到盘水印抽查、JavBus 直连接口与真实索引器验收仍待补 | `src/peach/magnet_chain.py`、`src/peach/download_postprocess.py`、云下载弹层的资源搜索与来源配置 |
| 46 | 周期挂载快照、故障分类、托盘提示和 NAS 目录过滤已合入，正式全量、桌面、手机与 Windows 生产 HTTPS 核验通过；本地来源目录不存在，115 与 PikPak 可读取；Mac 挂载验收待补 | `src/peach/mount_reachability.py`、`src/peach/platform.py`、API、扫描与托盘回归 |
| 21、26 | doctor、分级健康检查和系统诊断页已在 Windows 上线，全量 5959 项、浏览器 389 项及严格 CA 核验通过；库健康清单、来源证据和冷却可查，Mac 验收待补 | `src/peach/diagnostics.py`、`src/peach/library_diagnostics.py`、诊断页面与回归 |
| 11、20 | CI 已有不检出源码的 wheel 消费冒烟；完整矩阵结果、minimal source 与 artifact-only 验收仍待补齐 | `.github/workflows/test.yml`、`scripts/smoke_wheel.py` |
| 14 | 自动检查与自动下载已实现，默认关闭，安装重启仍由用户确认；macOS 包、签名与局域网配对仍待做 | `src/peach/automatic_updates.py`、配置 API、`maintenance-settings.tsx`、对应后端与前端测试 |
| 操作 1 | 当前实验未复现：备份前、备份内、备份后均为 6164 行，集合摘要一致、逐行差异 0、备份完整性 ok；历史原因未取得 | `attic/evidence/20261002-tag-backup-audit/report-20261002T092121Z.json` 与同目录差异 CSV |

### 等待条件

等待条件与开发优先级分开；条件满足后再安排批次，不把历史数字直接用作执行计划。

- 真实账号验收：操作 43 需要用户完成 PikPak 浏览器登录，另验磁力提交与两小时以上的过期续期。
- 真实索引器验收：本机 Prowlarr（9696）接 sukebei 的番号搜索已在生产跑通；OneJAV、Free JAV Torrent 经种子换 infohash 后接入。0Magnet 被 Cloudflare 拦，需 FlareSolverr。
- 预算与产品决定：操作 12 的本地下载预算；25 的 NFO 写入边界；前端全局文字亮度与图标选择。
- 真实写入与维护窗口：操作 3、4、5、8、14、19、24、26、42；先刷新预览，涉及账本、生产入口或凭据时取得当轮授权。
- 人工复核与证据：操作 2、9、17、18、27、30、32、33、34、37、38、41；32 的形状决定影响 35。操作 1 等历史逐行证据，有新增证据再追溯。
- Mac 状态核对：操作 10、11、24、26 与 `STATUS.md` 的 in-sync 记录交叉核对，只执行仍缺的步骤。
- 挂载跨平台验收：本机未取得 `peach.local` 的 mDNS 应答，等待可用 Mac 连接；第 46 条保留 Mac 挂载验收，Windows 定向通过不能关闭该项。

## BoardUI 正式前端迁移

主界面由 `frontend/src/react/bootstrap.tsx` 启动 Application，页面、详情与常驻面由 React 路由树渲染。目录、关注、实体和选择控制器按域组织，命令式 DOM 适配器保留在 `frontend/src/application/`，共享历史、查询与设置只初始化一份。后续按 [ADR-0031](adr/0031-frontend-react-boardui-tailwind.md) 清退无消费者的样式和 DOM 适配器。控件映射见 [Board 适配](BOARD_UI.md)。迁移不包含版本号或其他分支发布工作。

- 前端基础库随页面引入，取舍与时机见 ADR-0031「前端基础库」一节。TanStack Query、TanStack Table 与 React Router 已在用，路由共用一份浏览器历史；馆藏网格已在 React 里、不用 TanStack Virtual，屏外卡靠 `content-visibility` 跳过渲染；要不要上虚拟列表按下一条的实测决定。
- `bg-card-footer` 与 `bg-card-hover` 取的是 `.peach-react` 里的真值，数据管理页整理卡、统计、活动、关注管理与设置的卡片页脚带都有底色，这几页还要逐页截图核对。
- 索引页取 BoardUI 的控件尺寸：过滤框 36px 高、底色与边框是 BoardUI 输入框那一档，遗留页的 Geist 搜索框是 38px；版式切换 66px 宽，遗留页的同类开关是 78px；名册格悬停掺 5% 主文字色，资料页名册格掺 6%。读数的逐位滚动（`frontend/src/ui-kit/motion.ts` 的 `popCount`）、骨架换内容的淡入（`ui-kit/skeleton.ts` 的 `revealSkeleton`）与版式切换的弹簧滑块还没接进 React 那一侧。
- React 子树深色下的次要文字取 BoardUI 的 neutral-500（115），遗留页的 `--muted`、`--ink-2` 是 163 与 212。已迁各页都是这一档，要不要把 `text-secondary` 调亮是一次全局决定，不在单页里改。
- Remix Icon 候选在预览页 `/icon-review.html` 审查，用户筛选完之前保留现有已选图标。
- 安装后教程：右下角那张卡和清单由 `frontend/src/application/tutorial.js` 的 DOM 适配器渲染，状态层（三个本地键、签名、请求代际）在 `frontend/src/onboarding/post-setup-tutorial.ts`。后续将渲染接入 React 组件。
- 厂牌资料页视频视图卡片多时（如 Prestige，339 张卡），侧栏展开那一帧最长约 37ms。屏外卡已跳过封面与元信息区的渲染，剩下的开销在卡片盒本身的排版；作品区已在 `catalog-grid` island 里，要上虚拟列表就在岛里做。

## 已有骨架、尚未完成（7 项）

实施顺序按下列依赖关系（候选实现与生产验收分开）：

- 运行与一致性：HTTP 只跳转 HTTPS；业务与调度由单一应用拥有；成功提交后失效缓存；缓存有界；可更新图片可复验；列表参数有上下界。
- 数据与查询：随机排序的唯一次序按需再做；重复索引与外键启用先做副本验证；补固定规模基准。
- 安装与诊断：「非 editable 安装的跨平台验收」「健康检查生产验收」「全新安装的自动门槛」「`peach doctor` 与分级 `/healthz`」「性能基准」按依赖实施，覆盖最小源码安装、wheel 资源、仓库外启动、就绪检查。独立桌面制品及操作系统 VM 验收按「制品与更新渠道」和「全新安装的自动门槛」推进。
- 抓取可复现性：按 [ADR-0024](adr/0024-mark-manifest-not-bundled-bytes.md) 落地来源配置与清单。
  `/scraping` 已有定点高清封面、FC2 Cookie 粘贴／文件导入和封面来源网络配置；剩余来源还要接入
  统一配置、会话有效性验证与完整批量 GUI，清单导入导出与标准模式待实施。
  Instagram 成熟解析器须有独立用户会话 POC；交付条件是 Windows/macOS 干净安装能跑、二次运行命中缓存。
- 后续结构：显式 API 模型、前端构建与高频页面迁移、候选分页、任务持久化按垂直功能实施；不为 AppContext 或文件尺寸单独做全仓搬迁。
- Linux 无桌面容器使用正式锁定依赖，部署边界见 [Docker 部署](DOCKER.md) 与 ADR-0105；ARM、NAS 实机与真实 CloudDrive2 挂载仍需分别验收。

真实 ledger 迁移、双机复制取消和系统级安装另有明确授权边界。

1. **寻找更好版本**：已能逐条标记「高清 / 无水印 / 完整版」等目标，并带番号和目标进入资源搜索；还缺相似内容匹配（第 51 条）、跨版本候选去重、第 43 条的剩余来源发现和人工替换确认。替换完成后旧版的个人记录与目标按 ADR-0087 接到新版上，目标标「已替换」关闭。
2. **现代自适应播放**：Video.js、Range、统计面板和 115/PikPak 原生 MP4 的按需 HLS 清单已上线；还缺自适应码率、多路清单、快速首帧和来源层大块预取；做完后补 HLS 首帧、seek、自适应码率与双端视觉验收。
3. **在线追更**：`src/peach/follow_providers.py` 登记的 12 个来源已上线（发现更新、跨站重复判定、`/follow` 与 `/follow-manage` 两页、writer 自动轮询、在线资产就地播放），关注条目的磁力可交云下载（ADR-0089）。还缺两件：关注来源附件的直链下载，归第 42 条的本地下载通道，流量与磁盘预算见「待执行的操作」第 12 条；SimpCity 多图楼层的图片轮播：`SimpCityConnector` 只把图片地址存进 `extra["images"]`，没投影成 `media_items`，归档站（`KemonoConnector._media_items`）与 f95zone（`f95_attachment_media_items`）已经投影。
4. **首尾帧出处与不完整候选**：已有受限 FFmpeg 首尾抽帧、Windows 内置 OCR、证据帧缓存、来源/Full version 候选和 `/review`；仍需决定全库批次范围，并把用户批准后的不完整版判断接到更好版本目标。
5. **厂牌 Logo 补齐与持续校验**：14 个已确认社交 handle 已有内容缓存、provenance、精确/感知哈希、质量与重复门槛及健康报告。仍有 32 家厂牌没有标识，合计 87 部作品（`peach-data/review/logo-coverage-20260924.csv`），缺的是官网链接而不是日文别名：MGStage 名录 402 条只对上账本 45 家，宽松判据翻出的疑似配对逐条看全是假的；FANZA 厂牌一览 839 家只补出 `Baltan`→`バルタン` 一条，且详情页没有标识图。下一步按「待执行的操作」第 21 条的厂牌官网扫描补链接，不能猜账号。
6. **口味证据持续刷新**：ledger 已实时记录搜索、播放、高潮、喜欢/理由、不合口味和稍后看；浏览器历史现可用 SQLite 一致性副本增量进入私有源库，并生成不含 URL/标题的 creator/tag candidate 与聚合报告。旧 2026-08-13 原始包已确认不在 Windows 外置盘；仍需在 Mac 开启 iCloud Safari、完成首次导入，并把两端每周刷新装成系统计划任务。AI 结论不得直接改真相字段。
7. **扫描与采集任务的参数标定**：无进展预警的 120 秒与单项动作预算（资料 90 秒、封面 240 秒）目前按最坏请求时长取的保守值；等一轮真实任务记录各阶段实测耗时后标定，同时确定完整问题文件的保留周期。

## 其他开放需求（67 项）

本区包含尚未开始和部分已实现的需求；每项正文说明剩余工作，验收状态见「已核对的实施状态」。

1. AI Provider 的真实调用、能力协商、Credential Manager 凭据和候选审核 UI。
2. 剩余单一创作者风格板复核、无标签内容补标。
3. 缺时长资源补 probe 后再生成九宫格。
4. PikPak 计费抽样与下载边缘质量核验。
5. 复用 CommunityScrapers 一类公开刮削规则做元数据导入：只当只读规则语料，不重新引入 Stash 运行时依赖（ADR-0021）。
6. 把常跑批处理折进 `peach` CLI：`probe`、`sheets`、`scrape_codes`、`fetch_jav_covers`、`taste_history`、`traffic_watch` 现在各是一个脚本入口，参数、限流与健康报告口径不统一。
7. 开源通用化的发布准备（ADR-0023 第 4 阶段）：把只对一台机器成立的运行态移出仓库；`tests/test_repo_hygiene.py` 的机器坐标门槛已扫全树。许可证、贡献与安全说明、issue/PR 模板在仓库里；设置层、来源挂载点 ID 与可整体关闭的复制功能在 Windows 生效，macOS 待跑 `peach init --from-existing --mount local=<落点>`。
   - 本文件待清的位置：「待执行的操作」里引用的仓库外 `attic/` 路径与本机 `peach-data/` 复核产物。
   - 公开分发：待项目相对稳定，安装、升级、数据迁移及跨平台回归稳定后，同批推进 PyPI 包发布和 WinGet 登记；现阶段仅记录计划，不上传或登记。发布前确认发行名，调整禁止上传标记，完善自动构建、版本发布与两端安装验收。
   - 发行名与 WinGet 应用 ID 未定案也未注册，发布前确认并复核可用性；产品显示名继续使用 Peach。
8. 女优高清头像的写入侧：`scripts/audit_performer_portraits.py` 出候选与实测证据，资料页上人可以逐个换掉任何一张（图库同名候选、用过的图、本机文件、https 地址），`scripts/fill_portrait_gaps.py` 把图库里只命中一张的批量装上、其余产对照表。仍缺换源那一轮（在位的封面裁片挡住更好的源），以及实体合并后孤立头像的 relink（如 `8022 <- 8168`：只有旧 ID 的 provenance 名唯一命中当前实体、当前目标又不存在时才算候选，不覆盖、不删除旧文件）。relink 按 ADR-0088 的合并墓碑（`entity_redirect`）查表。
9. 文件名与网盘目录整理：按模板的那一路已落地（ADR-0039）：数据管理页的「整理」与 `scripts/organize_media.py` 共用 `peach.organize`，预览出计划 CSV、执行前 SQLite backup、逐条 rename 并同步账本 path/name、失败回滚、事后完整性与外键检查，只动视频、只在同卷内、目标已存在整行跳过，批次可整批退回。`scripts/clean_names.py`（域名噪声）与 `scripts/flatten_release_dirs.py`（冗余目录层）两条专门形态默认出 dry-run CSV，带 `--apply --backup` 才落盘，真实批次见「待执行的操作」第 3 条。仍缺三件：
   - 旁挂封面与字幕不跟着主文件改名。
   - 真实库上还没执行过任何一批（2026-09-22 只读预览：115 会改 1484、跳过 8627，PikPak 会改 167、跳过 10436，`local` 因外置盘未挂载整批跳过）。
   - 按演员归档的模板变量：目录模板可按演员名归档（NeoAVDC v0.0.4 的演员目录命名与按演员归档开关）。
10. 来源与默认值通用化（ADR-0023 第 5 阶段候选）：`peach init` 的问答已按本机路径只声明 `local`，非交互路径写出的 `DEFAULT_LOCATION_ROOTS`（`R:\media`、`B:/`、`A:/`）仍是维护者的示例盘符。剩两件事：来源用「本地 / 远端挂载」类型字段代替代码里按 `local`/`115`/`pikpak` 名字点名（`web_resource_sync.py` 的 SQL、`media.py` 的 HLS 规则）；复制功能支持 win↔win、mac↔mac 与任意一台当写者，目前只验证过 Windows 写者 + macOS 读者。
11. 非 editable 安装的跨平台验收：wheel 资源与 Windows Python 3.14 源码树外独立安装已验证；Windows/macOS 的正式 3.14 消费任务结果以 CI 为准。
12. 健康检查生产验收：`db` 区分 missing、empty、available、unavailable，`?ready=1` 检查 schema 校验和；待部署后用项目 CA 验证 HTTPS 与损坏／未初始化状态。
13. 界面国际化：界面目前只有中文，先补英文。
14. 制品与更新渠道：剩余 macOS 独立包、代码签名、局域网配对和更完整的配置管理。已有的部分是 Windows 独立测试包（免安装 zip 与当前用户安装包两种）、首次引导与本机配置表单、按构建身份自行重建的打包托盘、由 `release_tag.py` 在发布点独家发出的版本号与标签（每个版本号对应一份制品并在 `CHANGELOG.md` 有一节），以及退出程序后完整解压新版、数据目录保持独立的测试包更新。自动检查与自动下载已有持久设置，默认关闭；下载只准备安装，重启由用户确认。关闭判据见 ADR-0012「1.0 门槛」第 8 项。
15. 「第一个小时」教程与故障排查文档：init → 声明来源根 → scan → 打开页面 → 手机信任 CA → 托盘/菜单栏自启动，每一步写清失败表现与对应的排查动作；截图用一套小的 SFW 演示数据集生成，不取自真实馆藏。演示数据集由 `scripts/demo_dataset.py` 生成，用法见 [docs/README_MAINTENANCE.md](README_MAINTENANCE.md)「演示数据集」；教程正文与截图仍待做。
17. 口味导入引导：`/taste` 上传（Takeout ZIP、browserexport 兼容文件）与 `scripts/taste_history.py` 直读本机浏览器库两条路都能用，首次设置和口味页也有简短指南，但没有面向陌生人的完整文档。需要一页「各浏览器怎么导出、多台设备怎么各自刷新」教程，把脚本折进 `peach` CLI（见「把常跑批处理折进 `peach` CLI」一条），并写明定时刷新的安装方式。
19. 局域网配对：仍需一次性配对码或 HTTPS 地址二维码，减少设备首次访问时手输口令；现有口令生成、取用与非回环无口令拒绝启动不重复实现。Windows 的 HTTP 跳转与 HTTPS 单一业务入口已有生产核验记录，见 [运行态](STATUS.md)；Mac 的入口验收并入操作 24、26。配对码参照 Javdex `docs/LAN_WEB.md`（MIT）：新设备领一个六位码，桌面端核对后批准，可记住设备、逐台撤销。
20. 全新安装的自动门槛：CI 的 `wheel-build` 已用 `uv build --wheel` 生成制品，`wheel-smoke` 不检出源码、用 `--no-cache-dir` 安装 wheel，并离开仓库目录运行 `scripts/smoke_wheel.py`。剩余验收分三路：
    - minimal source：全新 venv 只装默认依赖、`peach init` 连跑两次验幂等、`migrate status`、离开仓库根目录再 `peach serve`，请求 `/healthz`、`/`、`/api/items`；覆盖 Python 3.14 的 Windows/macOS 及缺 FFmpeg／OpenSSL／Node 的环境。
    - wheel：核对第 11 条的 Windows/macOS Python 3.14 消费结果与失败场景；消费方保持不检出源码。
    - artifact-only：只下载刚构建的桌面制品、不检出源码地启动，依赖第 14 条。失败场景覆盖数据根不可写、端口被占、账本损坏、未配置媒体目录、无 FFmpeg、非回环监听但无口令、两个 writer 同时启动。
21. `peach doctor` 与分级 `/healthz`：`doctor`（另带 `--json`）逐项报版本、数据根可写性、配置文件合法性、数据库能否打开、schema 版本与待执行迁移、FFmpeg／ffprobe／OpenSSL 路径、挂载点可达性、端口占用、是否处在「局域网暴露但无口令」状态、后台任务最近一次失败；输出脱敏，不带口令、cookie、站点凭据和完整媒体路径。`/healthz` 相应从布尔改成分项状态（`database`／`schema`／`configured`／`ffmpeg`／`media_mounts`／`security`），与「健康检查生产验收」一起做。
    - Windows 已完成正式全量、集成、源码托盘重启及项目 CA 严格 HTTPS 核验；本机 CLI 与 API 报告一致。Mac 验收待取得连接。
22. 性能基准：用 SFW 合成数据生成 1k／10k／100k／500k 四档库，nightly 测冷启动到 `/healthz`、目录页与详情页 p95、两字以上搜索 p95、本地 SSD 与网盘挂载的 Range 首字节、空闲 RSS、后台扫描时前台退化倍数、备份期间读请求不失败。门槛用「相对上一次基线下降超过 20%」，不给绝对毫秒数，因为不同机器不可比。数据集与「第一个小时」教程的演示数据集共用：`scripts/demo_dataset.py --video stub` 出规模档（2000 条约 9 秒，海报按扩展名复用一张），基准脚本与 nightly 任务待做。已有一条基线记录：关系筛选上线后在真实库上只读对照，七轮中位数为标签 195.5→25.5 ms、创作者 148.8→45.6 ms、女优 162.7→15.7 ms、厂牌 162.0→19.6 ms，返回 ID 与总数一致；这是服务端耗时，不是浏览器端延迟。
23. CI 的 Windows job 太慢，一次 push 的墙钟由它决定。同一批 2786 个用例在 `macos-latest`（arm64）上 57 秒，在 `windows-latest` 上 1475 秒，本机 Windows 是 324 秒，runner 比开发机还慢 4.6 倍。按时间戳差算，250 个用例（9%）吃掉 1119 秒，每个稳定在 4.5 秒上下，形状像每建一个临时文件被 Defender 扫一遍。矩阵分片那一半已经在跑：`ci_plan.py` 按域与 `shard_index` 展开矩阵，入口默认 `--jobs auto` 在每个分片内再并行。剩下的一半是在 Windows job 里对 runner 的临时目录加 `Add-MpPreference -ExclusionPath`，先量一轮确认是不是 Defender。不要为了缩短墙钟把 Windows job 从矩阵里去掉：它是生产平台，也是唯一能拦住 Windows 独有回归的地方。
24. 借鉴 vercel.com/<team>/~/deployments 的令牌式筛选与排序。那一行不是一排互斥药丸，而是「Add Filter + 若干条已添加的维度令牌（Author／Environment／Status）」，每个令牌自带下拉，维度可叠加、可逐个摘掉，另有独立的日期区间与状态汇总（`6/7`）。2026-09-05 实测它的三态：未生效 `1px dashed rgba(0,0,0,.21)` 透明底，悬停／聚焦换成 `#FFFFFF` 实底加 `1px solid rgba(0,0,0,.08)`，下拉展开时 `gray-200` 底配实线。虚线读作「建议但没应用」，实心读作「已生效」。
    首页大概率不合适：`.tagbar` 那一排是单选（`全部`／`没看过`／`稍后看` 恒有一个生效），把没选中的三个画成虚线会读成「三个待处理的筛选」；而且这套「填亮 = 生效」要成立，页面底色得比控件低一档：Vercel 的仪表盘底是 `#FAFAFA`，Peach 的 `--ground` 是纯白，没有可填的更亮档。真正对得上的是多维叠加的场景：`/follow-manage` 的来源／状态／WIP 组合筛选，和 `/review` 的候选筛选。先在这两处试，别动首页。
25. **写 NFO 与目录收纳，先定产品边界再动手**。参考 NeoAVDC 的 `nfoWriter.ts` 与 `organizeMedia.ts`（MIT，副本在 `attic/tools/20260911-参考项目/`）：Kodi `<movie>` 带 `<customnumber>`、`<mpaa>`、`<set>`、`<art>`，演员 `<thumb>` 指向 `.actors/` 相对路径；Infuse 认不出隐藏目录，要换成平铺的 `actor-<名>.jpg`；`extrafanart/` 两边都安全。收纳的判据值得原样搬：目标已存在时先比 realpath 再决定拒绝覆盖，跨卷 `EXDEV` 回退成复制加删除，已在番号目录内不再套娃，NFO／海报／背景随视频改名，只删空目录。
    Peach 至今不写媒体目录，头像与取景 sidecar 都在 `peach-data`；写 NFO 意味着复核结论对 Emby 与 Infuse 可见，代价是媒体目录多出文件、CloudDrive 挂载上的写入要走第 9 条那种维护窗口。三个可选边界：① 不写媒体目录，导出到用户指定的独立目录，播放器把它当第二个媒体源；② 按来源根逐个开启写入，默认全关；③ 全量写入。建议从 ① 起步，它不碰第 9 条的前置条件。用户拍板前不实现。
26. **系统诊断页**：第 21 条的 `peach doctor` 与分级 `/healthz` 有了输出之后做这一页，`doctor --json` 是唯一数据源，页面不另算一遍。合并五家做法：
    - Windows 已实现并上线，桌面、390×844 手机、正式全量及生产严格 CA 核验通过；CLI 与 API 库健康及来源报告一致，Mac 验收待取得连接。
    - 每项带「原因、修法、跳转」三元组（sakuramedia `lib/features/system_diagnostics/presentation/hints/`），修法只给动作不给命令，跳转到配置页的具体分栏；修法在路由器或系统侧的项不给跳转。提示文案守它的四条规矩：一句话、只用界面上看得见的名词、不猜原因、不写影响；「列表为空」与「请求失败」是两条不同的提示。
    - 库健康计数：识别失败、补资料失败、缺封面、缺时长，每个数字点开是番号清单、可复制（javm `docs/plans/库健康诊断-方案.md`、OpenAver 0.16.7）。
    - 来源健康：真抓对一位女优才算健康，HTTP 200 不算（OpenAver 0.16.7）；minnano-av、javdb 的冷却状态与截止时间在这里显示。
    - 挂载可达性取第 46 条的探测结果。
    - 分类为媒体库根与挂载、数据库与待执行迁移、FFmpeg／OpenSSL、来源会话、最近一次后台任务失败五类。sakuramedia 是前端逐个调探针拼出来的，没有统一后端接口，这一点不照搬。
27. **开放 API 与按文件哈希查找**：AMMDS 的 API 文档给出了单人媒体库对外的最小形态：独立于登录口令的 `x-api-key`（可多把、可单独吊销）、`{code, message, data, timestamp}` 统一信封、按番号或文件哈希查本地影片 id、跨已开启来源联合检索。只在出现外部消费者（Emby 插件、脚本、AI 工具）时做，起点是 OpenAver 的 `/api/capabilities`：一份清单列出全部端点，AI 发起的写入一律先预览、再提交。翻译接口不做。
    - 先做的是指纹。扫描时只算 osHash（文件大小加首尾各 64 KiB），进 `asset.hash_kind`，让改名后的重复识别不依赖路径。sakuramedia 的采样指纹（`sakuramedia_local_provider/storage.py` 的 `compute_file_hash`：8 MiB 以下全文 SHA-1，否则头尾各 3 MiB 加两段由头尾哈希决定位置的 1 MiB 中段）抗伪造更好，但每个文件读约 8 MiB：按 115 约 1.0 万、PikPak 约 1.06 万个视频算，全量要读约 160 GiB 网络流量，osHash 约 2.5 GiB。采样指纹只对「同番号 + 同时长」已聚出的重复候选按需算，不做全量。Windows 网盘挂载上 `st_ino` 不稳定，读前读后只比 size 与 mtime。
28. **「今天看什么」推荐分**：`related.py` 已有 Tag-IDF 加 MMR 与可解释理由，口味画像与观看记录各自成页，缺的是揉进一个分数。sakuramedia `daily_recommendation_service.py` 的三档权重：
    - 常规档：相似度 8、关注女优 3、想要的影片 2、热度 4、榜单 2（共 19），没有新鲜度。
    - 冷启动档：热度 11、榜单 5、新鲜度 2（共 18）；极冷启动只看新鲜度。
    - 热度用正值的 P95 归一，参考值写死为一次 P99 实测防历史漂移，重算只更新分数变了的行。榜单信号按名次衰减（窗口 100），日、周、月榜权重 1.0、0.7、0.4。
    - 每条推荐落 `reason_codes` 与 `signal_scores`，整表快照替换，界面能说「因为你关注了她」。
    Peach 的口味画像是连续信号，比它「关注了 / 没关注」的二值强，作为 Peach 自己的一项保留。Peach 没有热度与榜单数据，先只用相似度、口味画像、关注、新鲜度四项；榜单接第 48 条。
    - 推荐时刻（第 47 条的时刻）每片至多 3 条，按画面、相似作品、热门三路并行取（SakuraMedia）。
29. **JavDB 官方 App 私有 API 作为元数据来源，做成默认关闭、用户自己开启的来源**：2026-09-11 探测已取得（`attic/evidence/20260911-javdb-api-probe/`）：签名是 `md5(时间戳 + 固定密钥)`，搜索与详情不需要账号，详情一次给出标题、原题、简介、片商、发行商、导演、系列、演员（含头像 URL）、标签、预览图、时长、评分、评论数、磁力数、是否有中字，图片走 `tp.spfcas.com`。它比 javdb.com 的 HTML 抓取稳定，也不受网页端的限速规则约束。OpenAver 0.15.1 与 JavBoss（2026-09-25，#347）都已接入。它伪装成官方 App，开关旁写明这一点，按 `metadata_policy.py` 定级为 community；开关旁的性质标注见第 64 条。
30. **内封字幕轨**：外挂 sidecar 已随 `asset_subtitle` 落库并挂进播放器，内封的字幕流则完全没登记：`scripts/probe.py` 只探 `v:0` 一路，`transcodes.py` 挑流时只认 video 与 audio。要支持得给探测加 `-select_streams s` 一路、把语言与编码写进同一张表（`pairing` 加一档 `embedded`），播放侧转 WebVTT 需要 FFmpeg 子进程抽流，与外挂那条纯 Python 路径不同，按需求出现再做。
31. **创作者昵称撞番号形态，判据待定**：`catalog_rules` 的番号提取已按 `CODE_BODY_STOPWORDS`、`_QUALITY_HEAD`、`REPOST_SITE_LABELS` 三层名单剥噪声，剩下的一类没有名单能覆盖：「昵称 + 数字」和厂牌番号完全同形。2026-09-12 在本机账本 26265 条 video 上只读盘点，`sumwall95 long sex video_18.mp4` → `SUMWALL-095` 19 条、`marie 2409a.mp4` 这类「角色名 + YYMM + 卷号」约 80 条、`dao01(1).mp4` → `DAO-001`、`wen66s.mp4` → `WEN-066`、`UWFr85dczsVeysGg.mp4` → `UWFR-085` 各若干。它们全部住在 `A:\创作者\`、`B:\云下载\` 和 `R:\Media\` 下，`is_jav_asset` 的发行证据门槛拦住了它们进 JAV 视图，但 `asset.code` 这一列仍然是个假值。逐个昵称进名单不收敛，可选判据是「所在目录已被判定为创作者」，这需要把目录级判定接进解析层，接口边界未定，先不做。

32. **系统清理与瘦身**：一个统一入口，先按类别列出各自占多少、删掉会失去什么，再由用户挑着清。可清的有头像与 Logo 的候选缓存（`provider-cache/` 下的 `objects/`、`requests/`）、抽帧与九宫格、HLS 分片与转码产物、复核 CSV 与标注图、日志与 state 快照。分档判据是「删了之后要重做一遍什么」：请求快照删了只是下次重取，`evidence/` 是「这个人用过哪些图」的历史、删了换头像就再也找不回旧图，两者不能同档。账本、真实媒体、备份和 `avatars-superseded/` 不在清理范围内。
    起因是换头像功能把取到的每一张图都留在候选缓存里，盘上只增不减；但入口本身要按上面整张清单做，不是只清头像。
33. **闲置时段跑后台任务**：判定用户此刻没在用 Peach，把不赶时间的活挪到那段时间自己跑，用户回来就让出资源。现在这类任务都要手点一下才动，媒体修复是第一个（`src/peach/web_media_repair.py`），抽帧、九宫格补齐、封面重探、probe 补时长都是同一类。要定的是闲不闲怎么判（最近一次播放与请求的间隔、是否有别的长跑任务在占盘）、哪些任务愿意进这个队列、抢占之后怎么记断点，以及计费来源要不要单独设闸。
34. **社区来源一家答上就丢掉其余几家的失败**：`library_processing._ask_community` 有一家给了资料就返回，冷却、403、超时的那几家不再被记起；`community_catalog._pictures` 里图片下载失败也静默跳过。结果是 `.scraping.json` 里 `verified_by` 为空的封面永远不知道还有谁没问到。2026-09-25 查 CWPBD／SMBD 六张宽封套时发现，但那六张 javdb 给的是剧照不是封套，补问反而会因两源不同图被 `_unverified` 拒收（ADR-0030／0032）。要改的是印证规则本身：两源给的不是同一张图时该取哪张、还是都不取，属于新 ADR。
36. **女优所属与官网链接主机对不上的复核清单**：minnano-av 的所属会过时，官网链接却还指着旧事务所（2026-09-26 查 Cruse Group 时发现神宫寺已转 ARM）。只能出人工清单、不能自动判错：prestige-av.com 是片商给专属女优开的页，lightpro.jp 下挂着几个子品牌，主机与所属不一致很常见。清单列女优、所属、链接主机与出演期间，进 `peach-data/review/`。

第 42–71 条来自 2026-10-01 对 SakuraMedia、OpenAver、JavBoss、Javdex、javm、mdcz、Javinizer-Go、AMMDS、javranking、Cuelume 等 16 个项目最新版的调研；最新代码浅克隆在仓库外 `attic/tools/20261001-参考项目/`，下文路径相对各项目根。

42. **本地下载：走用户自己的 BT 客户端与直链**：BT 通过用户本机下载器的 Web API 提交，Peach 不实现 BT 协议：qBittorrent 用 `/api/v2/auth/login`、`torrents/add`（`urls`、`savepath`、`category`／`tags`）、`torrents/info?hashes=`、`torrents/delete`；Transmission 用 `torrent-add`、`torrent-get`、`torrent-remove`，首个请求回 409 后带 `X-Transmission-Session-Id` 重发。保存路径必须落在某个本地来源根之内，watchdog 才看得到。关注来源附件（FANBOX、Patreon、Gofile 等）的直链由 Peach 自己下载。写新文件、不碰已有文件；占本机流量与磁盘，复用 `jobs.py` 的计费来源与磁盘闸门，预算见「待执行的操作」第 12 条。长下载用第 57 条的续传与停滞看门狗。
    - 复用云下载的任务表、状态机与九类失败分类（`src/peach/downloads.py`，ADR-0089），只有瞬时网络自动重试；qB `metaDL`／`stalledDL` 归「无源或停滞」，落地未见时定向触发 `ingest_path`。
43. **资源搜索与候选筛选**：Torznab 是协议不是平台，基于 Newznab 扩展（`https://torznab.github.io/spec-1.3-draft/`）；Jackett、Prowlarr 是把它翻译成各站请求的代理，Sonarr／Radarr 是客户端。Peach 作客户端接用户自己配置的 Prowlarr／Jackett，不内置站点定义：先 `t=caps`，再 `t=search&q=<番号>&cat=6000`，解析 `item` 的 `title`、`size`、`pubDate` 与 `torznab:attr` 的 `seeders`、`peers`、`magneturl`、`infohash`；磁力可能在 `magneturl`、`link` 或 `guid` 任一处，按内容判断（SakuraMedia `src/service/transfers/downloads/clients/torznab.py`，FC2 番号只搜纯数字，部分索引器失败不算整体失败）。
    - 自配 Torznab、凭据本机保存、候选筛选与填入云下载弹层已实现；直查链先问 manko.fun，取得 1080p／2160p 即短路，否则问 JavDB、sukebei，再由索引器覆盖 JavBus、16mag、OneJAV 与 Free JAV Torrent。论坛只作线索。真实索引器验收、非 manko 候选到盘水印抽查与 JavBus 作品页直连接口仍待补齐；逐条确认提交下载。
    - Jackett 与 Prowlarr 都内置 `sukebeinyaasi`、`onejav`、`freejavtorrent`（公开）与 `clearjav-api`（私有，只收官方片商作品）的定义。sukebei 没有清晰度分类，Jackett 把它整站映射成 6000，4K 只能在 `q` 里加关键词，再从标题解析；索引器名单里没有专收 4K 的公开源。
    - 作品页资源还需接 JavBus：从详情页脚本取 `gid`、`uc` 后请求 `ajax/uncledatoolsbyajax.php`（带 Referer），每行有名称、大小、日期与「高清」「字幕」标记（garage `garage_jav/javbus.go`、Atlas `services/jav-utils.ts` 的 `parseMagnets`）。
    - 候选筛选取 SakuraMedia `auto_download_service.py` 的判据并加强：标题解析出的番号对不上就剔除、体积区间、做种数大于 0、infohash 黑名单、最多试 5 个；Peach 另从标题与标签解析分辨率（`4K`、`2160p`）、编码、中字与无码标记，按「寻找更好版本」的目标排序，不只按体积。
44. **DMM cid 前缀表与失败分类**：Javinizer-Go 从 r18.dev dump 生成了 24279 行「系列 → DMM cid 前缀」表（`content_id_prefixes.go`，MIT），`START-575 → 1start00575` 这类数字前缀 cid 不必再搜索；`sources/dmm.py` 注释写着它们「只有搜索答得出」，`jav_cover_fetch.py` 有几条手写映射。表随版本发布，查不到再搜索；AMMDS v1.6.71 的规则覆盖（正则、前缀、后缀、包含，`{brand}`、`{num2}`～`{num8}` 占位）作用户补丁层。不在本机自学前缀：OpenAver 0.15.3 本机自学的 53 条里 21 条是错的且无声。另移植 mdcz `crawler/sites/dmm/failureClassifier.ts`（GPL-3.0，可并入 AGPL）的分类：地区封锁、登录墙、未渲染的 Next.js 空壳、404 各成一个契约 reason，空壳判据也用于浏览器取页。
45. **来源测试录制回放**：mdcz v0.16.0 的做法（`docs/testing-fixtures.md`）：每个番号一份 manifest，图片按 sha256 内容寻址、不进 Git，缺 blob 用同尺寸同字节数的生成图顶上；Cookie、CSRF、token 替换成固定值；回放缺一条交互就判失败，不回落公网。`sources/library-metadata/*.json` 的快照可当录制源，先拿 DMM 与 javbus 两个解析器试。
46. **挂载可达性探测**：参照 OpenAver `core/source_reachability.py`：正常 600 秒、异常 60 秒探一次，连续两次失败才报，提示里写来源名；分开报「没有权限读取」与「不存在」（0.16.12），扫描跳过 `#recycle`、`@eaDir`、`@*` 这类 NAS 系统目录。结果给第 26 条诊断页与托盘状态用。
    - 周期快照、在途去重、故障分类、来源接口与托盘提示已实现；Windows 完整回归、桌面、390 像素手机及生产核验通过。Mac 挂载验收待补，第 26 条诊断页仍待接入，不能关闭本项。
47. **时刻、合集与片段导出**：「记一次高潮」已写 `activity_event.position_seconds`，推广成通用的「时刻」（时间点 + 一帧缩略图 + 可选备注），加时刻合集页；SakuraMedia 分播放列表、时刻、切片三层，各自成合集（`src/model/collections/`）。片段导出用 FFmpeg 拷流、不重编码，切点落在关键帧上，文件放 `peach-data`。时刻随个人记录按 ADR-0087 接到新版本。
    - 推荐时刻每片至多 3 条，与第 28 条的推荐分同批做。
48. **上榜标记**：javranking-extension 的公开静态索引（先拉不到 200 B 的版本清单，变了才拉 1.26 MB `search-index.json`；schemaVersion 2，1769 部，JavDB TOP250、2020–2025 年榜、JavLibrary TOP250）每周读一次，给馆藏标「上榜」并喂给第 28 条。索引没有许可条款（未取得），只读引用并在界面标明来源；按来源存成候选标签。
49. **播放器画面条**：播放器已有进度条悬停预览（`frontend/src/player/controls.ts` 的 `mountPlayerSeekPreview`）；参照 SakuraMedia「先看画面再决定看什么」（`wiki/guide/watch-from-a-frame.md`），把已有抽帧做成播放器旁可滚动的一列缩略图，点即跳转。
50. **女优身份冲突的四个动作**：Javinizer-Go v1.6.0（`a2ddd00`）把女优身份与逐片署名拆开：刮削只写署名、不写身份，解析不出的身份先隔离；冲突用 keep、adopt-canonical、adopt-alias、reassign 四个固定动作解决，`scrape.collision_policy` 可设无人值守的 auto_keep／auto_alias。`/review` 的女优冲突用这套动作词表，合并留 ADR-0088 的墓碑。
51. **画面向量**：给抽帧算图像嵌入，服务「寻找更好版本」的跨编码相似匹配、不同编码的重复片、给没署名的作品认人、「更多像这一帧的」。SakuraMedia 用 SigLIP2 + Qdrant；Peach 用 SQLite 扩展 `sqlite-vec`，不多起服务，与头像匹配的人脸向量共用设施。模型几百 MB 到 1 GB 多，全库约 8 万资产的嵌入要分批跑，进第 33 条的闲置队列。先拿第 1 条验证收益。
53. **女优体型筛选**：`performer_profile` 已有身高三围，女优列表加按年龄、身高、罩杯筛选（JAV_MovieManager）。
    - 作品加「发行时年龄」字段（发行日减生日）与按它筛选（OpenAver 0.16.1）。
54. **无码官方站**：caribbeancom、tokyohot（Javinizer-Go，MIT）与 h0930、h4610（mdcz，GPL-3.0），放在无码链的 1pondo 之后，每站独立解析器与测试。
55. **字段策略两条**：简介取最长；落选的封面与剧照连同来源留作备选，供 `/review` 换图（mdcz `scrape/fieldAggregation.ts` 的 `FIELD_STRATEGIES` 与 `imageAlternatives`）。进 `metadata_policy.py`（ADR-0038）。
56. **头像裁剪记源图指纹**：从封面裁女优头像时记源图指纹，源图换了就拒绝复用旧裁剪框（Javinizer-Go PR #251，`internal/downloader/poster_identity.go`）。
57. **长下载续传与停滞看门狗**：大文件与长流用 Range + If-Range 续传，原响应没有强 ETag 或 Last-Modified 就拒绝拼接；固定期限换成「多久没有进度」的看门狗（Javinizer-Go v1.6.1，`b9b73640`）。第 42 条与头像、封面下载共用。
58. **来源缺陷台账**：逐站记数据缺陷（字段缺失、错配、图片规格），写进 `docs/SOURCING.md`（JavBoss `source_quality.md`）。
59. **番号清洗语料**：NeoAVDC `number/parseNumber.ts` 先整段剥发布组域名再剥分辨率，另有 `PREFIX_BLACKLIST`；`hhd800.com` 那类样例已在 `tests/test_jav_code_domain.py`，补 NeoAVDC 剩下的脏文件名样例进 `catalog_rules` 的番号测试。
60. **结果提示音**：Cuelume（MIT，npm 0.2.4，零依赖、Web Audio 现场合成）只给长任务完成与失败配音，点击、输入、悬停不响；默认关，设置面板加开关与音量，偏好存 Peach 设置。按依赖策略精确钉版本并登记 Dependabot。
61. **r18.dev dump 本地镜像**（需新 ADR）：Javinizer-Go `internal/r18devdump/` 与 AMMDS 都导入 r18.dev dump 建本地库，有码链首站零请求，在线结果反过来校验它。dump 大小未取得（`https://r18.dev/dumps/latest` 回 307），先定磁盘预算与更新频率。
62. **智能列表与只读查询**：保存一组组合筛选，结果随馆藏自动更新；另给高级入口跑只读 SQL（只读连接，写不进去）。JAV_MovieManager 直接执行用户 SQL，读写不分，这一点不照搬。
63. **可选遥测，默认关闭**：开启后只上报版本号与平台，上报内容在设置页逐字列出、可随时关。SakuraMedia 默认开启并上报实例 ID、插件、CPU、内存、媒体数与总字节（`src/service/system/telemetry_service.py`），javm 写死上报地址，两者都不照搬。默认关闭时看 GitHub Releases 下载计数。
64. **不标来源性质**：追更、采集、凭据与资源搜索都不显示「公开页面」「归档站」这类渠道性质小字。同一站点的每一行写的都是同一句，用户 2026-10-08 判为冗余；站点图标和名字已经说明来源。
65. **javinfo.dev 作可选来源**：用户自带 API key 才启用。`/movie` 每千次 0.80 美元，只收成功响应；前五家来自自建目录库、毫秒级（`docs/providers`）；FC2 与无码只经 missav、sextb 两个流媒体源，没有 FC2 专门来源。接入前用新账号送的 0.02 美元（约 25 次 `/movie`）对一组已复核番号跑对照，比字段准确率与速度。归档的 legacy 仓库没有许可证，只借思路不借代码，且 r18 旧 API 已失效，没有 Peach 缺的解析器。
66. **小文件打包**（低）：SakuraMedia v0.9.0 把影片图片与时间轴缩略图打进 `assets.zip`、`thumbnails.zip`（`ZIP_STORED`，`src/common/image_store.py` 包条目优先、单文件兜底），为的是文件数与备份速度，不影响扫描与采集速度。`peach-data` 下 `sources/` 约 9 万、`generated/` 约 6 万个文件；收益在 Syncthing 图片同步与备份。要求能解包回原样，和第 32 条一起设计。
67. **站点互联**（观察）：AMMDS v1.6.80 让好友站点当只读数据源。单人自用时只对自己的几台机器有意义，Windows 写、Mac 读的复制已覆盖；出现第二个使用者再议。
68. **漫画与同人本**（低）：一站式馆藏的下一类媒介。需要阅读器、来源与元数据模型（AMMDS v1.6.80 已加漫画库）；Peach 已有图片与写真类资产，在其上扩展。
69. **PWA**：加 manifest 与 Service Worker，手机、平板可安装到主屏、全屏播放。
70. **原生客户端**（远期）：SakuraMedia 用 Flutter 出 Windows、macOS、iOS、Android 客户端。维护成本高，PWA 不够用时再议。
71. **「已拥有」标记的浏览器扩展**（低）：在 javdb、javbus、javlibrary 页面上给馆藏已有的番号标「已拥有」（JavBoss `content/jav-ownership.js`，凭 API 令牌查询）。Peach 侧要一个只读的按番号查询接口与独立令牌，和第 27 条的开放 API 同批设计。
72. **关注页往回抓键的忙态闪动**（低）：按下「抓更早的一页」后，忙态由 `starting`、`olderRun`、`running` 三者推出；POST 返回时 `starting` 先清，首次轮询回来前 `running` 仍是 false，按钮文字会短暂回到「抓更早的一页」。浏览器 e2e「检查更新与往回抓」偶发红就是撞上这一拍。忙态应从按下一直保持到首次轮询确认任务在跑或已结束。
73. **关注链路剩下的两处重复回源**（低）：一是直连图床的卡面缩略图，浏览器取一份，`FollowFaceIndex` 为算画面签名在服务端再取一份（每个地址一次，经按站冷却）；要只取一次，得让卡面缩略图改经 Peach 代理并落盘，影响整个 `_thumb_url` 投影与远程访问的流量。二是 kemono 系判定为非资源帖的帖子不落库，每次检查仍会重探详情（每次最多 12 帖）；要记住这类判定，需要在来源 metadata 里存一份有界的拒绝清单。
74. **关注作者建档的后续**（ADR-0096）：名册「创作者」档只列有入库作品的实体，纯在线作者只在「在线」档，两档要合成一份；coomer 与 simpcity 来源的作者和发布账号之间补 `operates_account` 关系；Gumroad、Fantia 的归档 id 形状核实后再还原原站账号；已有 F95 来源按新的名片白名单重新解析一次；绑定后删除别名时，已绑的来源要能拆开。
75. **关注读数和卡片数的口径**（低）：关注页与创作者资料页在线视图的「N 项更新」按条目数统计；卡片按已加载的发布组折叠，并按视频或图片过滤，只有外链的条目不出现在两档中。读数改为发布组、当前媒体数量，或并列显示「M 组」的产品口径待确定。

76. **单影片的在线站点入口**：详情页按同片身份展示 MissAV、Jable 等站点的真实影片页面，多个站点与字幕、破解等版次分别保存。复用已有番号归一、版本判据、来源传输与失败状态；界面语言 `cn` 不等于中文字幕，模板地址仅为候选。保存原 href、最终地址、返回番号、版次与语言证据、核验时间和状态。NASSAV 的五源解析可作参照，但其首个命中下载、仅存流地址的模型不能作为已验证入口。完整功能、依赖、许可证与源码差异见 `peach-data/review/nassav-functional-review.md`；本轮仅审阅，尚未实施。

合计：**74 项开放需求**，其中 7 项已有骨架，67 项其他开放需求。已完成的需求不在这里留痕，去 Git 历史查。

## 待执行的操作（42 项）

这里包含可直接开发的修复，以及需要另行授权、外部条件或人工判断的操作与复核批次，比上面的需求细一层；做完就删，不在这里留痕。待办只放这一处：[docs/STATUS.md](STATUS.md) 每次会话开头都要读，队列不该常驻在那种入口文件里。

1. 历史证据待取得：2026-09-02 的 191 行 `javinizer:%:tag` 差异（javbus −172、r18dev −19）仍缺可归因的写入者与逐行差异。2026-10-02 的「读计数 → sqlite_backup → 再读计数」实测未复现，6164 行逐行一致，备份完整性 ok。证据在 `attic/evidence/20261002-tag-backup-audit/`；取得历史快照或写入记录后继续追溯，不据此修复真实账本。
2. 在 `/review` 处理 5 个被跳过的标题偏移值：`MY-101`～`MY-104`、`SAR-103`。
3. 另行授权后跑 `scripts/flatten_release_dirs.py --apply --backup <落点>`：296 个目录操作（collapse 167、rename 129）落在 CloudDrive 挂载上，影响账本路径 3374 条。执行前重跑 dry-run，191 条未挂载的随挂载状态变化。
4. 另行授权后先备份 ledger，修正 2 组已核实姓名：恢复 `平沢すず` 的规范名；`かわいゆい` 移除错误的 `河合ゆい` 别名与 r18 外部引用，清退错误头像及 provenance 后重新生成候选；同步 actor tag 与检索投影。
5. 另行授权后先备份 ledger，把 `follow_item` 181、184、185 从 `seen` 恢复为 `new`，复核状态计数、完整性与新哈希。
6. 按复用审计依次替换 PID 锁和 Rule34Video 媒体页；每项固定版本/revision、首个消费者和隔离测试同批落地。
7. 分类剩余 44 个无预览变体：确无图片还是解析遗漏。
8. 另行确认后在生产关注页检查 LazyProcrastinator FANBOX，把已验证的 6 图、正文与 Gofile `OS2Qz9` 资源页写入关注候选；Gofile token 未配置且账户不是 Premium，21 个视频仍未取得。
9. 在 `/review` 人工处理 JAV 日文系列名、现有创作者标签、FC2、Javinizer、Logo 和头像候选；未经批准不写真相字段。
10. 将 Windows writer 的最新副本同步到共享传输点，再让 Mac reader 拉取；同步前后核对迁移版本、计数、完整性与 writer 身份。
11. 在 Mac Finder 以 `smb://peach-writer.local/peach-sync` 连接一次并保存钥匙串记录，再重启菜单栏进程，核对自动挂载、reader 锁定、HTTPS 与 mDNS。
12. 在实现本地下载（BT 与直链）前先确定本机流量与磁盘预算；云下载的网盘成本已由用户 2026-10-01 接受（ADR-0089）。
13. Windows writer 运行 PikPak 夜跑前重算 probe/抽帧队列，并按 `peach-batch-jobs` 设置流量与系统盘闸门。
14. 外置盘挂载后先只读盘点 `R:\Media\<名字>\P\...` 图片规模；扫描写真 ledger，需另行授权。
15. 重做品味分析页的视觉再决定是否合入：提交 `cd3effe` 功能可用但版式不过关，以该提交里 `taste_history.py` 的分析逻辑为底。
16. 在真实浏览器验收 `/link-mark` 的清晰度与边缘（账本里的 twitter 写法已收成 x.com）。
17. 用户复核 `directory-links-<日期>.csv` 后用 `install_entity_links.py` 装入社媒链接；`conflict` 且账本旧号「疑似失效」的行由用户决定换号，随后可对账本现有全部 X 链接跑同样的验活。
18. `studio-names-<日期>.csv` 的厂牌改名已执行，剩 3 条不一致按「一个账本名混了两家」处理，5 条 404 未取得，改用搜索查找要先有一个能用的搜索出口。
19. 厂牌标识规则：logo 文件一律不透明方图（位图 `images.bake_square`、矢量 `images.bake_square_vector`），产物再过 `images.refit_plate` 摆到圆形图位里看得全的位置，页面三处一律 cover。另行授权后跑一次 `normalize_studio_logos.py --apply --backup <落点>`，2026-09-08 dry-run 报 52 张待改：46 张重新摆位（自带大留白的裁掉、顶到边的补到外接圆）、4 张 SVG 包方底（DarkRoomVR、TeamSkeetXReislin、TeenFidelity、VirtualTaboo，前两张白字标配深底）、HEYZO 从备份原图重烤改配深底、pikpak 重补方。
20. 把 javdatabase 的 idol 页接进社媒／官网候选：183 页缓存里 139 页带 X 链接、138 页带另一个官方站，由番号定位、不必离线比名。复用 `peach.social_links` 的判据与 `install_entity_links.py` 的 `FIELDS`，排掉四个整站广告主机。
21. 其他厂牌官网的厂标与演员资料广度扫描（SOD、FALENO、Attackers、S1、Moodyz 等），排在第 20 条 javdatabase idol 页接入之后。
22. 用 javtiful 的 `/ja/actress/<slug>` 补演员的罗马字↔日文配对：315 页约 7560 位，切语言前缀就出日文名。厂牌名不随语言切换，这条只服务演员别名。
23. 37 位演员在 javdb 上只有日文名（`同形`），另有 5 位未取得，中文名要换来源：javtiful 的 `/ja/actress/<slug>`（第 22 条）或 javdatabase 的 idol 页。复核产物 `peach-data/review/javdb-cn-names-20260904.csv` 逐行带 verdict 和证据，可直接筛。
24. macOS 标识 `io.github.longmeidao.peach.*` 在 Mac 上生效：代码已在 master（`src/peach/appid.py` 是唯一来源，`install_macos_agent.py` 与 `setup_macos_port80.sh` 会自己清掉遗留标签），命令与四项核对见 [docs/OPERATIONS.md](OPERATIONS.md)「桌面入口与发布」。放进第 26 条的维护窗口一起做；两台机器都跑过之后删掉 `peach.appid` 里的遗留标签表和用到它的分支。这是换生产入口，执行前须当场授权。
26. Mac 追上 master 的一组操作，按顺序做完再重启菜单栏。做完之前不要重启：master 上的 `peach serve --host 0.0.0.0` 没有口令会拒绝启动，reader 会直接消失。① `git pull` 到 master；② `pip uninstall -y peach-app && pip install -e ".[macos]"`；③ 先把 Windows 的 `peach-data/secrets/auth-token` 复制到 Mac 数据根的同一路径，因为 reader 取 writer 复核结果发的是自己的口令，两边必须是同一份，而 `--from-existing` 找不到文件会自己生成一份不同的；④ `peach init --from-existing --mount local=<落点>`；⑤ 重启菜单栏，核对 `/healthz`、`/review` 能读到 writer，手机与 Mac 浏览器各登录一次。第 24 条的标签改名可以放进同一个维护窗口。
27. 事务所改名复核：Wish/GIRFY、LiStarPRO/GRANZPRO 缺可核验官网；LIGHT 与 ELTRA/EST 存在分流，不能整体合并；Prime Agency/GG 有歧义，Cruse Group 官网证书链未取得。原始请求与逐条结论位于顶层 `attic/reviews/20260906-portrait-agency/agency-review.csv`。只对取得证据且获用户批准的记录执行合并。
    2026-09-06 核对 wish-promotion.jp 已是其他内容站，不能作为现官网。15 条现官网链接使用共用 Chrome UA 重查，13 条返回 200；Cruse Group 证书链与 Prime Agency TLS 连接仍未取得。
28. `install_entity_links.py` 的 `prune` 已按 `is_gone()` 分「确证没了」与「取不到但不算证据」两档，安装路径的 `check_links` 仍按「非 200 就跳过」执行。首批 703 条里 137 条因此没装，其中 31 条 twitter.com、23 条 t-powers.co.jp。安装路径照 `prune` 分两档：后者留进待复查队列，配合 `rediscover_entity_links.py` 对 t-powers／nax-pro／mines-pro 这些已经搬家的域名上溯找新锚，再装一次。
30. 封面来源头像逐条复核：37 张仍来自 `cover-fallback`，其中 3 人在图库里本来就有人像，资料页上一点就能换掉；完整初始清单位于 `attic/reviews/20260906-portrait-agency/remaining-cover-avatars.csv`。41 张被封面覆盖的 Gfriends 人像已从备份恢复，包括日向真凛，恢复记录见同目录 `cover-restore-result.json`。采集器将封面保留为未验证候选，安装函数拒绝把整张封面写成人物头像；补头像后继在这批人的作品换上新封面时截封面上的脸替换它们（`cover-face`），还没轮到的仍待逐条换。DMM 女优一览页已排除为换源候选：头像只有 125×125，且同批图 Gfriends 已收在最后一档（2026-09-11 实测，结论与取证位置见 [docs/SOURCING.md](SOURCING.md)）。
31. 2026-09-07 首要原则审查（覆盖整个 `peach-app`）的剩余清理项，完整报告与判断依据在顶层 `attic/reviews/20260907-first-principles/review.md`。下面每条独立，可单独派工作树：
    - follow：`connector_headers` 形参、`blocked_reason` 基类钩子、`FollowCandidate.version` 输入字段只有测试在用；`KemonoConnector.HOSTS`／`SubscribeStarConnector.HOSTS` 与登记表 `url_hosts` 是同一份主机表的第二份；Rule34Video 自带的探测循环可并入 `enrich()`；425／429 进 `_send` 的可重试集后两段手写重试可删。
    - follow 弱假设：六处「读时修旧行」兼容层（`archive_file_url`、`_legacy_history_end`、`_f95_has_resource`、`split_posts`、`author_display_text` 修正、`f95_attachment_media_items`）换成一次带备份的迁移，需 ledger 写授权。ETag／304 机制保留：2026-09-08 只读核查，45 条来源 `etag` 全空、从未回过 304，但 f95zone 有 7 条存下 `last_modified`，条件头有站点在回。
    - Web：`serve --no-ledger-sync`／`--ledger-sync-seconds` 处理代码已删、参数还在，托盘五处与 [docs/OPERATIONS.md](OPERATIONS.md) 仍在传。这一项必须和托盘重建同批做，旧 EXE 拉起新代码的窗口期会被 argparse 拒收；四个域 Protocol（`LinkContract`、`PlaylistContract`、`ResourceSyncContract`、`ReviewContract`）换成直接用 `WebContract`，`ContractConformanceTests` 随之删；来源在线判定、回环判定各有三份，各留一份；`_read_answers`／`_validate` 里「只发 media_dirs」的旧表单分支生产不可达，只靠测试活着；access `legacy` 模式的 `tok` cookie 只被接受不被升级，定截止日删接受分支。
    - 桌面：换 EXE 两条路径（`replace_windows_tray.py` + `windows_update` 内联备份，与 `windows_restart.swap_tray_binary`）留校验更强的后者；`sync.py` 的 `PUSH_INTERVAL_SECONDS`／`push_if_needed`／`interval` 生产只传 0；`scripts/manage_tray_startup.ps1` 已由 `desktop_startup.py` 接管（同时改 ADR-0011 与 [docs/OPERATIONS.md](OPERATIONS.md)）；三张「哪些路径算运行时」清单合成一处。
    - 领域层：`catalog_rules` 里站名交替串、TLD 列表各写两份；`transcodes.requires_conversion`／`browser_path` 是同一段缓存逻辑；`library_processing` 是第三条 r18 请求路径且跨模块拿私有 `_fetch`。
    - scripts：`audit_creator_attributions.py`（查的 `legacy:asset` 已无写入者）、`apply_metadata_tags.py`（绕过 `/review`）、`creator_tags.py --apply-review`（与 `web_review` 判据不同的第二条写路，`--export-review` 要留）建议删；7 处绕开 `scripting.open_for_write`、5 处自拼只读 URI、5 处手写线性重试要接上共享实现；`audit_video_endcards.py`、`audit_fc2_similarity.py`、`localize_series_names.py` 还会用但文档没登记，归到 `peach-batch-jobs` 或 [docs/SOURCING.md](SOURCING.md)。
    - tests：2026-10-08 按 `test_source_assertion_ratchet.py` 实测有 148 处源码文本断言，其中 `test_frontend_build.py` 32 处、`test_dependency_policy.py` 26 处多为产物、CI 与依赖门槛；棘轮只许减少，保留范围与清退判据见 [docs/TESTING.md](TESTING.md)「写什么测试」。手写 schema 与临时表按触碰范围核对并迁到 `fresh_ledger()`，不整体重写；`check_copy_final_state.py` 的词表不拦「过去／此前」。
    - 文档：同一条规则最多写在 19 个文件里（测试入口）。
32. 归一后要用户判的 10 张厂牌标识：AttractiveLLC ×3、C-more_Entertainment ×3、Bambi_Promotion ×2、Deep_s、Tameike_Goro。补到内容外接圆这条规则在「设计上就出血到边」的标识上会把内容推离边缘，逐张判词在 `peach-data/review/refit-review-20260908.csv`，原图在 `peach-data/archive/logos-pre-refit-20260908/`，对比页 `build/logo_compare.html` 的第一节。占宽和圆外损失都分不开 C-more（0.98／0.97）与 MARRION（0.95／0.94），所以没加窄化条件，先由用户定还原哪几张，再按定下来的形状写判据和测试。
33. 补底到 64 的 7 张还没写入：`normalize_studio_logos.py --apply` 要用户自己跑（DorcelClub.img、Flower 三张、LINX.img、HEYZO.icon、Prestige.icon，逐张前后见对比页第三节）。
34. 头像去水印的人工复核与执行：`scripts/scrub_avatar_watermarks.py` 已跑完 620 张的检出，候选在
    `peach-data/generated/watermark-candidates.csv`，左右对照的标注图在同目录 `watermark-review/`。
    23 张待处理（16 张纯裁切、1 张裁切加修补、6 张只能修补），看图确认后带 `--apply` 执行；检出器
    抓不到半透明水印（`NUBILES.NET`、`MATTIEDOLL.DEVIANTART.COM` 那几张），漏的往 `--marks` 的 CSV
    里补 `file,x,y,w,h`。另有 14 张检出超过 4 处被判为画面文字放过，它们是第 30 项那批封面误装，
    去水印不适用，要的是换源。
35. `/link-mark` 的「成品图标原样用」通道有 19 与 32 号同一个毛病，只是资产不同：站点给的 apple-touch-icon 是照方角设计的，四边一圈高光裁成圆之后沿圆周露白。`site_icons.py` 对 ≥96 px 的设计图只做等比缩放，那圈高光是人家设计的一部分、抠不掉。涉及 8 个主机共 149 条链接：t-powers.co.jp 59、blog.livedoor.jp 49、bambi.ne.jp 16、mines-pro.jp 15、life-promotion.com 5、mgstage.com 3、moodyz.com 1、adult.contents.fc2.com 1。可走的路子是把 `images.refit_plate` 那套摆位判据接到这条通道上（32 号定下来的形状同样适用），或者对这一类直接退回字形合成。常见社媒已经改走内联品牌标记，不在此列。
36. 女优名字的日文字形例外表：Atlas（MIT，`attic/tools/20260911-参考项目/Atlas/backend/src/services/actress-name-map.ts`）
    对照 minnano-av 三个榜单实测出一批 OpenCC `cn→jp` 处理不了或会转错的字：`々`（佐佐木→佐々木）、篠／筱、
    庄／荘、里／裏、怜／憐、凛／凜、條／条、澤／沢。`peach.social_links.name_key` 目前不做简繁与日文字形转换，
    搜 javdb 与 minnano-av 时只搜规范名会漏（`三上悠亚` 对 `三上悠亜`）。把这份例外表做成 `name_key` 生成
    日文键的显式例外加测试，优先级「显式例外 → OpenCC → 原文透传」；一名多人的消歧仍按现有「需人工消歧」规则。
37. 逐对判定 `115` 来源的 11 对路径大小写重复：2026-09-12 只读盘点，成因与 `local` 那次不同，是 `.MP4` 与 `.mp4`、`MIDE-950-C` 与 `mide-950-C` 这类扩展名与目录名的大小写，且多数两侧都挂着标签与快照（例如 `86263` 有 5 条标签、`28608` 有 6 条）。不能像 `local` 那样机械地保旧删新，要一对一看哪侧的标签与快照更全，合并后再删另一侧。
38. 图库同名多张、却没有可比封面人脸的女优：两家目录的两张不同照片彼此过线且占多数时已按 ADR-0062 装上，小图也作证、只有小图时装小图（ADR-0066）。仍装不上的是名下只有同一张照片的两份、或只有一张提得出脸的；可选的参照是片商或事务所资料页人像、单人作品的九宫格抽帧。
39. 接入 avwikidb（`https://avwikidb.com/`）作为「截图 → 女优」候选来源。官方截图本身已按番号落库、在女优页照片档展示（ADR-0068，直取 DMM 与 MGS，不经 avwikidb）；剩下的是把逐张标注接到样张上，让多人作品的样张只进出场那位的照片档。2026-09-24 只读核实，作品页 `/work/{番号}/` 服务端渲染，`movie.sampleImageActors` 按截图序号给 FANZA 女优 ID；接入时读 Next.js 的 `_next/data/<buildId>/…json`（buildId 缓存、失效后重取，mdcz `avwikidb.ts`），不解析页面里的 `__NEXT_DATA__`。FANZA 截图原图 `pics.dmm.co.jp/digital/video/{cid}/{cid}jp-N.jpg` 与缩略 `awsimgsrc.dmm.co.jp/pics_dig/…?f=webp&w=600` 都无签名可外链；标注是人工逐步补的，4 部样本覆盖六到八成，每张最多标一人，MGS 作品只给站内 `/mgsimg/` 代理路径（不用，走现有 MGS 抓取）。女优页 `/actor/{FANZA id}/` 的增量是 `alias[].fanzaAvActressId`（同一人多个 FANZA 旧 ID）、事务所与其官方页、社媒账号、逐字段来源核对记录；头像与作品元数据与现有 DMM 来源同源，无增量。带查询串的地址（分页、筛选）被 Cloudflare Turnstile 拦，只读无参数页；robots 禁 `/api/`，不接。结论只进候选。
41. r18 英文写法建出的实体还剩两位素人女优的日文名未取得：8645 `Mana(23)`（413INST-168，标题 `まな`，年龄后缀的日文写法没有原文，`まな` 又常见，不猜）与 8629 `* Kuchiku`（POW-040，r18dev 原文 `Kuchiku * Reverse Bunny`，与标题 `べりさ` 对不上）。DMM 商品页的演员栏已空、演员页 404，取得原文后再改名，英文留作别名。`PREMIUM BEST`、`1VS1`、`NOZOMI` 是厂牌或官方自己的拉丁写法，保留。
42. 合并转址回填：2026-10-01 只读盘点出 127 对 ADR-0088 之前的旧合并，126 对可按 ADR-0088 补 `entity_redirect`，1 对目标已不在、链条也接不上；孤立实体图 47 张，其中 19 张可按回填对跳到活实体。盘点脚本在仓库外 `attic/tools/20261001-entity-redirect-backfill/inventory_merge_redirects.py`（`mode=ro`、只打标准输出）。写账本需另行授权，按 `peach-ledger-write` 先备份。
43. PikPak 用浏览器登录的真实账号验收（ADR-0093）：用户在设置页点「用浏览器登录」并在窗口里登录，确认窗口自动关闭、卡片显示「浏览器登录，由 Peach 续期」；再提交一条磁力，确认签名通过、任务落到 PikPak。隔两小时以上、access token 过期后再提交一次，确认服务端接受不带 secret 的网页 client 刷新。任一步被拒时按报错区分「登录失效」还是「网页端常量已更新」，后者重新取证并更新 `ClientProfile`。
44. 磁力抓取链的完整验收：直连实现是 manko.fun、JavDB、Sukebei，其余来源由已配置索引器兜底，尚未保证 JavBus、16mag、OneJAV、Free JAV Torrent 的固定次序。`watermark_check` 只保存 `pending`／`bypassed`，下载后的实际水印检验未接入；Manko 绕过按用户指定偏好保留。来源可用性、版本质量与到盘后检查须分别取证。
45. 种子来源与身份复核：本轮 13 项撤销已有历史证据并进入 v2；另有 5 项去重事项保留在 `attic/reviews/20261017-seed-corrections/withdrawal-review.csv`。其中 2 项规范名更正不由种子自动改名，1 项身份未取得，2 项仅有本机 Stash 别名来源并已从新导出排除。来源置信度与差异见同目录 `candidate-risks.csv` 和 `entity-diff.csv`；结构校验不代替事实复核，不依据缺席撤销旧断言。资料上传暂不实施。
