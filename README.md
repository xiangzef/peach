<p align="center">
  <img src="resources/peach-logo.png" alt="Peach" width="96">
</p>

<h1 align="center">Peach</h1>

<p align="center">给自己用的私人影片馆藏：本地硬盘、网盘和关注的创作者，放在一个地方看。</p>

<p align="center">
  <a href="https://github.com/peach-mitao/peach/releases">下载 Windows 版</a> ·
  <a href="https://demo.peach.video">在线演示</a> ·
  <a href="https://github.com/peach-mitao/peach/releases/tag/intro-video">介绍视频</a> ·
  <a href="https://github.com/peach-mitao/peach/issues">问题反馈</a> ·
  <a href="#文档">文档</a> ·
  <a href="README.en.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/peach-mitao/peach/actions/workflows/test.yml"><img src="https://img.shields.io/github/actions/workflow/status/peach-mitao/peach/test.yml?branch=master&amp;label=tests&amp;logo=githubactions&amp;logoColor=white" alt="tests"></a>
  <a href="https://github.com/peach-mitao/peach/releases"><img src="https://img.shields.io/github/v/release/peach-mitao/peach?include_prereleases&amp;filter=v*&amp;sort=semver&amp;label=release" alt="release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0--or--later-blue?logo=gnu&amp;logoColor=white" alt="license"></a>
  <img src="https://img.shields.io/badge/python-3.14%2B-3776AB?logo=python&logoColor=white" alt="Python 3.14+">
  <img src="https://img.shields.io/badge/platform-Windows-0078D4?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0xIDFoMTB2MTBIMXptMTIgMGgxMHYxMEgxM3pNMSAxM2gxMHYxMEgxem0xMiAwaDEwdjEwSDEzeiIvPjwvc3ZnPg%3D%3D" alt="Windows">
  <img src="https://img.shields.io/badge/platform-macOS-555555?logo=apple&amp;logoColor=white" alt="macOS">
  <img src="https://img.shields.io/badge/18%2B-adult%20content-critical?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIj48cGF0aCBkPSJNMTIgMiAzIDZ2NmMwIDUgOSAxMCA5IDEwczktNSA5LTEwVjZ6TTEyIDd2Nm0wIDN2MSIvPjwvc3ZnPg%3D%3D" alt="18+ adult content">
</p>

https://github.com/user-attachments/assets/a5610874-e611-41bb-be22-7d99f0d64b62

> **18+** 仅供成年人管理自己的成人内容馆藏。仓库不含任何媒体或站点数据；连接外部站点时用的是你自己的账号和访问权。

- **整理过的片子直接用**：扫描时读取片子旁边已有的 NFO 和海报，不用重新刮削。
- **不动你的文件**：扫描只读，文件留在原处；改名、移动由你手动发起，先看预览，做完可以撤回。
- **网盘和本地一起看**：115、PikPak 用 CloudDrive2 挂载成本地磁盘后，和硬盘里的片子进同一个馆藏。
- **挂载状态**：定期检查媒体目录；读取失败会复查，确认后在托盘和作品页说明来源及原因。扫描跳过 NAS 回收站与系统目录。
- **播放墙挑片**：拖动全屏封面墙浏览，点开作品就在墙内播放；同一番号的版本和分卷可以直接切换。
- **跨站关注与追新作**：把同一创作者在多个站点的更新汇到一起；按女优名订阅新作，尚未入库也能追。
- **数据留在自己电脑上**：观看记录、收藏和设置都存在本机；补资料时只向来源站点发送番号或女优名；用云下载时，磁力只交给你选的网盘。
- **公司资料**：厂牌和事务所可显示公司名称、成立日期、品牌启动日期、所在地及运营归属；只显示有来源的资料。
- **可直达的详情与设置**：资产用 `/assets/:id`，作品用 `/works/:code`，关注条目用 `/posts/:id`；实体资料用稳定 ID，设置分区从 `/settings` 进入。地址清单见[页面路由](docs/ROUTES.md)。

## 截图

不想先装？[在线演示](https://demo.peach.video) 里是一份现成的馆藏，搜索、女优页、筛选和统计都能直接点；演示站只读，操作不会保存。

下面的截图原图均为 3840×2160 无损 PNG，点击查看；播放墙也能在演示站体验。

**首页：按来源、时长、标签筛选**

<a href="https://peach.video/assets/screenshots/home-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/home-20261014.webp" alt="首页：人物和厂牌导航、筛选与作品卡片" width="1200"></a>

**播放墙：拖动挑片，原位播放，切换版本和分卷。**

<a href="https://peach.video/assets/screenshots/wall-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/wall-20261014-readme.webp" alt="播放墙：全屏作品封面与浏览控件" width="1200"></a>

**女优页：资料、别名、外部链接和全部作品**

<a href="https://peach.video/assets/screenshots/profile-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/profile-20261014.webp" alt="艺人资料页：人像、资料与全部作品" width="1200"></a>

**关注：一个创作者在多个站点的更新汇到一起**

<a href="https://peach.video/assets/screenshots/follow-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/follow-20261014.webp" alt="关注：创作者导航、筛选和图片更新" width="1200"></a>

**统计：片子存在哪、看了多少**

<a href="https://peach.video/assets/screenshots/stats-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/stats-20261014.webp" alt="统计：馆藏读数、存储与内容分布" width="1200"></a>

## 能做什么

- **按文件夹浏览**：馆藏筛选条右侧可切换卡片、列表与文件夹模式，搜索、标签和详情沿用首页。列表支持全集排序、分页和跨页选择，默认每页 20 部。目录用途可指定为个人分类、人物、创作者／账号、卖家或厂牌；先预览影响，再保存归属，并可单独启用新文件沿用。已有归属冲突保留，规则可移除。见[目录浏览](docs/DIRECTORY_BROWSING.md)。

- **搜索**：聚焦搜索框可按封面浏览作品、JAV、关注视频、关注图片与订阅新作，按头像进入艺人和关注作者；可直接进入关注与新作订阅。输入几个字，女优、番号和影片一起出来。
- **我的收藏**：资料页名字旁的星星收藏常用人物、片商、厂牌、系列和标签，黄色实心表示已收藏。馆藏、发现、关注和资料页筛选条的星形按钮打开「我的收藏」，按类型和名称查找，显示资料图、厂牌标识或作者头像。窗口采用设置弹层的玻璃导航，保存的筛选单独一页，导航底部提供已标记和稍后看清单。馆藏页可给当前筛选起个名字，随时打开或删除。
- **来源检查**：逐站选择直连或 Peach 代理，查看连接失败原因、耗时与冷却状态；公开 JSON 接口可在来源页配置、试查和启停，见[自定义来源](docs/CUSTOM_SOURCES.md)。复核来源图片点击后才加载，失败可重试。
- **外部播放器与 VR**：作品详情可生成限时网络播放链接，下载 M3U，或在 VLC（iPhone / iPad）、IINA（Mac）打开；使用方式见[外部播放器](docs/EXTERNAL_PLAYERS.md)。
- **身份分类**：艺人按身份与发行范围分为女优、素人、西方、网黄博主和动画作者。素人指有可信非职业出演证据，或全部出演作品都是素人发行（FC2-PPV 番号，或带非视觉模型来源的「素人」标签）的艺人，女优与西方出演者不归为素人；其他作品题材只用于作品筛选。名册使用「艺人、卖家、在线」三个并列入口，卖家按来源账号与作品对应。筛选条只显示有内容的分类，资料页在视频数量左侧显示分类与图标。
- **作品计数**：明确分段的同一 FC2 合集计为一个视频，分段文件和出演归属完整保留。已确认合并的身份共用资料与作品，旧资料页地址通往规范身份。
- **版本与分卷**：同一番号的中字、无码、清晰度和修复版汇在一张作品卡里；各版本保留自己的分卷，播完一卷接着播放同版下一卷。
- **回收站**：卡片显示手动、垃圾、重复或文件缺失的归入原因；视频和其它资源均可直接还原。未记录原因的条目显示「原因未记录」。
- **账号身份**：网黄博主分类需要身份或账号来源；未核实的条目可在全部名册查看。账号头像优先使用保存的图片；有本人身份依据的个人博主，在两部作品画面截到同一张脸时自动装上头像；其余账号以代表作画面占位，并标明非本人。资料页中的别名只承载身份名称，画质和资源包规格保留在文件信息中。
- **西方图片来源**：出演者与网黄博主可选 Babepedia 主图库人像；Tushy 等 Vixen 网络作品以出演者和发行日匹配官方封面，卡片、详情和头像框选共用原图，无法唯一匹配时留待核验。
- **女优页**：别名、生日身材、社媒和 JavDB、MISSAV 链接汇在一页，下面是她在你馆藏里的全部作品和照片；换头像时图库人像、作品封面、本机图片和图片地址都能先框一块，也能整张使用。
- **补资料**：按番号从片商官网、DMM、JavBus、JavDB 等站点补标题、女优和厂牌；封面优先选择尺寸更大的官方原图，JavDB 图片只用于核验。只填空着的资料，不覆盖你改过的。
- **补全预览**：影片缺图时，列表和详情提供「补全资料与预览」按钮，自动补封面并为本机影片生成抽帧预览。下拉可选「只生成本地预览」或「只采集在线资料」；全库处理在数据管理的「扫描与采集」。
- **播放**：在浏览器里直接播放，记下看到哪；可以点喜欢、打分、稍后看、加进播放列表，也能「记一次高潮」。馆藏和关注详情的「接着看」可横向浏览推荐内容，点卡片直接切换。
- **播放墙**：右上角常驻入口打开独立的全屏封面墙，拖动上下左右浏览有封面的作品，探索时自动接续未展示作品，图片可切换为缩略图。点击作品原位展开并高亮，其余磁贴变暗，同块磁贴同步让位；可在墙内播放、切换分卷与版本或打开共用详情，收起时可继续在小窗播放。封面按磁贴比例选择全封或正封，跟随人脸取景；播放时背景模糊、标题移到上方。继承馆藏搜索、筛选及资料页作品范围，顶部提示可清除作品筛选并继续浏览当前 JAV 与来源范围。左上角返回键旁可换一批，等待时墙面变灰、变糊，右下角可搜索和调整图片与缩放。
- **追新作**：在女优页打开订阅，或在关注管理里按名字订阅，馆藏中尚未收录的女优也可订阅。Peach 会定期检查新作；新作卡显示人物头像，点击卡片打开站内作品详情，查看资料、预览图、评论和资源；点击已建档人物的头像可进入资料页。创作者可跨 FANBOX、Patreon、Kemono 等站点关注，不同站点的同一作品合成一张卡。
- **媒体缓存**：关注图片、作品预览图和已取得的视频内容保存在本机，后续直接复用；头像每 3 个月、favicon 每年刷新。关注管理有失败来源时显示「检查失败项」，可单独重试。
- **在线作者**：创作者资料页分别显示本地作品与在线更新，在线内容可切换视频、图片并筛选；头像可从社媒头像、在线作品封面和正文图片中框选，也可用本机图片或图片地址。
- **JAV**：「馆藏」浏览已入库作品；「发现」按口味探索已知的库外作品和少看的馆藏，不限发行时间，可筛选标签、切换大小图；「想要」管理待找作品，可按有磁链、没磁链切换，已查到的资源会保留。点击发现卡打开作品详情，在作品卡或关注内容上点「想要」，也可输入番号添加，文件扫进馆藏后自动标为已入库。
  发现卡与首页共用头像和署名样式，使用本地已登记的规范姓名；已有推荐先显示并在后台更新，筛选栏的刷新图标用于更新作品资料。关闭详情保留筛选、排序和浏览位置。已登记厂牌可打开资料页，未登记厂牌只显示名称。影院模式在详情框体内展开，隐藏下方缩略图和分页，退出后恢复；图片翻页键固定在媒体区两侧，馆藏缺少已登记样图时按需读取来源图片。
  作品资料、评论和资源跨重启保存；新作每天按需更新，发行超过一个月后补齐并固定保存，仍可手动重新查询。
- **云下载**：在 JAV 或高清版目标打开「查找资源」，搜索番号或粘贴磁力，选择资源后提交到 115 或 PikPak。落地后自动选择正片、隔离达到自动线的推广附件、采集资料并按该来源模板整理；进度和失败重试都在活动页看。
- **按番号找资源**：云下载直接添加先按 `manko.fun → JavDB → Sukebei` 查磁力，`manko.fun` 命中 1080p 或 2160p 就停止；没有高清命中时再接配置的 Prowlarr 或 Jackett 索引器。「想要」的待找清单继续汇集多个来源，方便比较版本。取得的封面和作品资料与候选资源一起展示。
- **统计**：片子存在哪块盘、看过多少、标签分布，一页看完。
- **口味**：综合观看、反馈、馆藏积累、浏览记录及关注关系。可读取 Aside、Chrome、Edge、Firefox 等本机浏览器，也可添加其他浏览器的资料目录；停止同步与删除已导入记录分别管理。社媒访问按已登记账号和人物身份判断。
- **设置**：弹窗按外观与导航、浏览与播放、JAV 与新作、搜索与推荐、内容显示分类；「Peach 配置」集中管理媒体入库、来源订阅、下载渠道、网络访问与应用维护。
- **多端**：电脑、平板、手机的浏览器都能用。

## 下载与使用

### Windows

1. 从 [Releases](https://github.com/peach-mitao/peach/releases) 下载其中一种：
   - 安装包 `Peach-<版本>-windows-x64-setup.exe`：双击安装，可选择安装目录，不需要管理员权限，开始菜单里有 Peach，可以在系统设置里卸载。
   - 免安装包 `Peach-<版本>-windows-x64.zip`：右键「全部解压」，双击里面的 `Peach.exe`。
2. 浏览器会打开首次设置页。
3. 选好媒体文件夹和谁能访问，开始扫描。

已有馆藏却出现首次设置页时，点「使用已有数据目录」，填入保存馆藏的 `peach-data` 目录。程序会沿用其中的设置、账本和访问密码，并记住位置。

Windows 独立包可在配置页「应用与维护」检查并下载更新；下载完成后确认重启安装。自动检查与下载默认关闭，可在同一处开启。

下载更新不会停止任务。应用内重启安装和安装包覆盖安装会保存采集进度、暂停刮削与抽帧；安装期间发起的采集任务会等待安装完成。安装完成或取消后，仍在运行的 Peach 会自动续跑；如果 Peach 已退出，则在下次启动时恢复未完成的馆藏资料、本地预览、时间轴缩略图和封面任务，复用已完成结果。主动关闭缩略图采集则不恢复。

Windows 安装包和免安装包均携带 FFmpeg、ffprobe、untrunc，转码、缩略图和缺索引 MP4 修复可直接使用。对应源码随同一 Release 提供，工具目录包含许可证和构建说明，见 [Windows 测试版](docs/TESTING_DESKTOP.md)。测试包还没有代码签名。Windows 提示「已保护你的电脑」时，确认文件来自本项目的 Release，再点「更多信息 → 仍要运行」。

Windows 托盘独立运行，关闭启动它的 Codex、Claude 或终端不会退出 Peach。托盘异常退出后会自动尝试恢复；5 分钟内最多恢复 3 次。主动选择「退出 Peach」会保持关闭。退出原因和恢复结果可在日志目录的 `tray-lifecycle.log` 中查看。

启动失败弹窗会给出诊断报告位置。程序能运行时，可从托盘「导出诊断报告」或系统诊断页「下载诊断报告」取得脱敏 ZIP，用于问题反馈。托盘导出完成后可打开报告所在目录、打开文件或关闭提示。

### 从源码运行（Windows、macOS）

需要 Git、[uv](https://docs.astral.sh/uv/getting-started/installation/) 和 Python 3.14 或更高（正式运行版本由 `.python-version` 固定为 3.14，uv 会自动下载缺的解释器）：

```powershell
git clone https://github.com/peach-mitao/peach.git peach-app
cd peach-app
uv sync --locked --python 3.14
& .\.venv\Scripts\peach-tray.exe
```

macOS 把后两条换成 `uv sync --locked --python 3.14 --extra macos` 和 `./.venv/bin/peach-tray`。

局域网访问、访问密码、更新和卸载见 [运行与配置](docs/OPERATIONS.md)。

在Peach 配置「应用与维护」打开系统诊断，可查看库健康清单、来源解析与冷却状态。运行 `peach doctor` 可取得同一份报告；`--json` 输出脱敏 JSON。状态与处理方式见 [本机诊断](docs/OPERATIONS.md#本机诊断)。

### Docker（VPS / NAS）

Linux 无桌面镜像与 CloudDrive2 分别部署，媒体目录与运行数据独立挂载。部署方式、访问范围和验收状态见 [Docker 部署](docs/DOCKER.md)。

## 常见问题

- **会改我的文件吗？**
  - 扫描、补资料都不碰原文件。
  - 只有三件事会动文件：
    - 你在整理里点了执行：改名或移动，先给预览，可以撤回上一批。
    - 你清空回收站：真的删除。
    - 你在资源同步里确认清理：删除盘上已经空了的文件夹，来源的根目录保留。
- **之前用别的刮削器整理过，能直接用吗？**
  - 能读的是 Kodi、Jellyfin 那种格式：
    - 和视频同名的 `.nfo`；
    - `<片名>-poster.jpg` 这样的海报。
  - 已有的标题、女优、厂牌和海报会直接显示。
- **支持哪些网盘？**
  - 支持通过 CloudDrive2 挂载的 115 和 PikPak。
  - CloudDrive2 也可运行在群晖等 NAS 上。Windows 先把共享目录映射为盘符，再在 Peach 中选择对应文件夹；这种方式无需在 Windows 安装 CloudDrive2 或 WinFsp。
  - 看片时 Peach 只把它当普通文件夹读，不保存网盘账号。
  - 用云下载时，CloudDrive2 的 API 令牌和 PikPak 的登录令牌存在这台电脑的凭据文件里。
  - PikPak 推荐点「用浏览器登录」，在弹出的窗口里登录，Peach 不经手密码；也可以用账号密码登录，密码只在你勾选「保存密码」时保存。
- **手机上怎么看？**
  - 首次设置时选「同一局域网的设备」。
  - 手机和电脑连同一个网络，用浏览器打开设置页给出的地址。
  - 建议顺手设一个访问密码。
- **数据存在哪？**
  - 都在本机的 `peach-data` 文件夹里。
  - Windows 版默认在 `%LOCALAPPDATA%\Peach\peach-data`。

## 问题反馈

在 [Issues](https://github.com/peach-mitao/peach/issues) 里写清楚版本号、做了什么、想要的结果和实际看到的结果，最好附截图。截图前遮掉密码、Cookie、局域网地址和文件完整路径，不要上传数据库文件或媒体。安全问题请按 [安全政策](SECURITY.md) 私下报告。

## 文档

使用：[Windows 测试版](docs/TESTING_DESKTOP.md) · [运行与配置](docs/OPERATIONS.md) · [来源采集](docs/SOURCING.md) · [网盘挂载](docs/CLOUDDRIVE.md) · [变更日志](CHANGELOG.md)

参与开发：[开发约定](AGENTS.md) · [总体架构](docs/ARCHITECTURE.md) · [测试与依赖](docs/TESTING.md) · [前端开发](docs/FRONTEND.md) · [复用清单](docs/REUSE.md) · [README 维护](docs/README_MAINTENANCE.md) · [文档与界面文案](docs/WRITING.md)。改完用 Windows `& .\scripts\test.ps1` 或 macOS/Linux `./scripts/test.sh` 验证。

## 相关项目

- [amane](https://github.com/sqzw-x/amane)：Peach 通过它接入片商官网等来源。
- [Gfriends](https://github.com/gfriends/gfriends)：女优头像图库。
- [CloudDrive2](https://www.clouddrive2.com/)：把网盘挂载成本地磁盘。
- [OpenAver](https://github.com/slive777/OpenAver)、[Javinizer-Go](https://github.com/javinizer/javinizer-go)、[MetaTube](https://github.com/metatube-community/metatube-sdk-go)、[MDCx](https://github.com/sqzw-x/mdcx)：Peach 参考过它们的来源解析和推荐做法。

各项目的复用位置与取舍见 [复用清单](docs/REUSE.md)。

## Star 历史

<a href="https://www.star-history.com/?repos=peach-mitao%2Fpeach&amp;type=date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=peach-mitao/peach&amp;type=date&amp;theme=dark">
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=peach-mitao/peach&amp;type=date">
    <img alt="Peach Star 历史" src="https://api.star-history.com/chart?repos=peach-mitao/peach&amp;type=date">
  </picture>
</a>

## 许可证

[AGPL-3.0-or-later](LICENSE) · Copyright (C) 2026 longmeidao。第三方前端文件保留各自的许可证；[依赖清单](package.json) 登记版本，[生成脚本](scripts/vendor_web_dependencies.mjs) 登记 `web/vendor/` 中的文件与许可证位置。
