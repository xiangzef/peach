# ADR-0023：开源为通用自托管单人媒体应用的路线

- 状态：Accepted（路线；各阶段实施仍需按 `peach-ledger-write` 单独授权）
- 日期：2026-09-02
- 关系：延续 ADR-0017（双主机本地运行）与 ADR-0004（网络边界）；把它们从「用户的两台机器」推广为「任意用户的一到两台机器」。

## 背景

Peach 要发布到 GitHub 供所有人维护与使用。使用形态不变：每个部署仍是单人、本地优先、ledger 是唯一真相源。但代码和文档里嵌着只对当前用户成立的事实：

- `src/peach/config.py` 用 `Path.home()/Desktop/peach`、`Desktop/<用户目录>/peach`、写者主机的 mDNS 名、SMB 账号名等字面量给默认值；代理与局域网 IP 散在 HANDOFF、STATUS 与技能文件里。
- ledger 路径固定写成 Windows 盘符形状（`R:\Media\...`、`A:\`、`B:\`），由 `peach.platform` 在读取时翻译成本机挂载点；盘符含义只在文档里说明。
- Windows 写者 / macOS 读者的单写者复制（SMB 共享、mDNS 名、钥匙串账号）默认开启、无法绕开，而多数用户只有一台机器。
- [docs/STATUS.md](../STATUS.md)、[docs/HANDOFF.md](../HANDOFF.md) 与多份技能文件记录了个人运行态、真实 IP、备份文件名与磁盘布局。

不属于本 ADR 的事：多用户与账号系统、云托管、第三方登录。它们改变产品形态，另立 ADR。

## 决策

分四个阶段推进，每个阶段独立可验收；未完成前一阶段不进入下一阶段的真实写入。

1. **配置层与首次运行**
   - 新增 `peach-data/config.toml`（或同等设置文件）承载数据根、媒体根、监听地址、代理、复制开关；环境变量继续作为覆盖，`config.py` 只保留读取与校验逻辑，不再含个人路径与主机名。
   - 新增 `peach init` 子命令：创建数据目录、跑迁移、生成设置文件与自签 CA，并输出下一步。
   - 不带参数的 `peach init` 在终端里问答（数据根、一个本地媒体目录、监听范围、端口、局域网名字），写出只声明 `local` 的设置文件并可选地首次扫描；问答逻辑在 `peach.onboarding`，托盘设置页复用（2026-09-04 落地）。
   - 「未配置」是明确状态：服务能启动并在页面提示去设置，而不是因缺目录崩掉。

2. **来源挂载点取代盘符**
   - ledger 中的路径形状不动（迁移成本与风险最高，且现有翻译层可用），但每个盘符前缀在设置文件里声明为「挂载点 ID → 本机路径」的映射，`peach.platform` 按映射翻译。
   - 新导入的资产用挂载点 ID 前缀写入；现有行的重写是一次真实迁移，需备份与前后计数，单独授权。

3. **复制功能可关闭**
   - 单写者复制（ADR-0017/0020）改为设置项 `replication.enabled`，默认关闭；关闭时不启动同步线程、不探测 SMB、不发布 mDNS。
   - 托盘与 macOS 端的挂载逻辑只在开启时装配。

4. **发布准备**
   - 清扫文档与技能中的个人信息：IP、主机名、账号名、磁盘序列、备份文件名、个人目录。`tests/test_repo_hygiene.py` 增加对已知个人字面量的拒绝门槛。
   - 增加 `LICENSE`（AGPL-3.0-or-later，2026-09-04 定稿）、`CONTRIBUTING.md`（指向 AGENTS.md 与测试入口）、`SECURITY.md`（凭据存储与网络暴露说明）。
   - README 改为面向陌生用户：是什么、怎么装、怎么跑、怎么贡献；个人运行态从 STATUS 移出仓库。
   - 第三方依赖许可证核对：FFmpeg 构建、Video.js、前端依赖（ADR-0022）。

## 勘误（2026-09-03，实施第 2、3 阶段时核对）

原文第 2 阶段写的「每个盘符前缀声明为挂载点 ID」和「现有行的重写是一次真实迁移」都不成立，
因为它把两件事看混了。核对账本后的事实与实际做法：

- `asset.location` **本来就是**挂载点 ID：`local`、`115`、`pikpak`、`online` 四个值，
  不是盘符。盘符只出现在 `asset.path` 里，而那是 AGENTS.md 的不变量（账本一律 Windows 形态），
  本来就不该动。**第 2 阶段因此不重写任何账本行，也没有对应迁移**；ADR-0025 不存在。
- 第 2 阶段真正做的是把「本机挂载点」这一层从盘符改成 location ID：
  设置文件用 `[media.mounts] <location-id> = <本机路径>` 取代第 1 阶段的
  `[media] <盘符> = <本机路径>`，`[media.locations]` 继续声明每个 ID 的账本口径根
  （`local = 'R:\media'`、`115 = 'B:/'`、`pikpak = 'A:/'`）。`peach.platform` 按
  「声明根前缀 → 本机挂载点」翻译，不再按盘符字母。挂载点的语义是**声明根在本机的落点**，
  所以 `R:\media\x` 在 macOS 上等于 `<mounts.local>/x`。
- Windows 上盘符本身就是挂载点，`translate_ledger_path` 原样返回，`[media.mounts]` 整表可空。
- 第 2 阶段同时补上了写入侧的一致性门槛：`peach scan <location> <root>` 现在拒绝
  与 `[media.locations]` 声明根不一致的组合，新导入的行不可能再落到别的来源名下。
- 诊断用的 `PEACH_DRIVE_MAP` 键空间是盘符，与新方案不兼容，已删除；替代品是同样语法、
  按 ID 键的 `PEACH_MEDIA_MOUNTS`（`local=/mnt/res,115=/mnt/115`）。

第 3 阶段有一处与原文不同，是刻意的：

- **mDNS 发布不随 `replication.enabled` 一起关**。原文把「不发布 mDNS」列进了关闭清单，
  但 mDNS 是这台机器自己的局域网入口（ADR-0009），和单写者复制没有关系：单机用户正是
  靠 `peach.local` 从手机访问自己的库，跟着复制开关一起关掉等于把通用化最想服务的那类
  用户的访问入口砍了。mDNS 继续由它自己的判据决定：`--no-mdns` 与「只绑回环就不发布」。
  关闭复制时不装配的是 ledger 同步观察器、SMB 探测与挂载、托盘的两个 Ledger 菜单项，
  以及追更凭据往共享副本写的那一份。

## 边界与不变量

- ledger 仍是唯一真相源；AI 与刮削结果仍是候选，不因通用化放宽。
- 单进程 FastAPI 模块化单体不变；不引入 PostgreSQL、微服务或多账号。
- Windows 与 macOS 都是一等运行平台；Linux 不在支持范围，未测试（2026-09-04 决定）。
- 任何阶段都不允许把当前用户的数据形状写死为默认值；默认值必须对一个全新用户成立。

## 后果

- 短期新增一层设置文件读取与校验代码，换来删除 `config.py` 中所有个人字面量。
- 现有部署首次升级需要一次 `peach init --from-existing` 把当前环境写成设置文件；步骤写进 HANDOFF。
- 阶段 2 的真实迁移与阶段 3 的默认关闭会改变当前用户的运行方式，实施前必须在同一轮拿到明确授权并保留回退路径。

## 第 4 阶段实施记录（2026-09-04）

本节是交接面：任何智能体接手开源发布，只读本节加 [docs/PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md) 即可，不需要对话记录。

### 用户已定的决定

- 许可证 **AGPL-3.0-or-later**。`LICENSE` 全文、`pyproject.toml` 的 `license`、README 双语「许可证」节与本 ADR 四处一致，`tests/test_repo_hygiene.py::ReleaseFilesTests` 钉住前两处。
- **Git 历史不重写**。历史提交里保留局域网 IP、本机用户名、主机名与共享账号名，用户接受这一代价；当前树由 `MachineCoordinateTests` 全树门槛保证不含个人坐标，例子一律用 RFC 5737 地址与中性主机名。
- 接受 issue 与 PR，大改动先开 issue 讨论；模板在 `.github/`，规则在 `CONTRIBUTING.md`。
- `AGENTS.md`、`CLAUDE.md` 与 `.claude/skills/` 随仓库公开，术语表的「我 / 用户」指任何部署者。
- Linux 不在支持范围；界面只有中文，国际化在待办；Python 下限 3.12（本机 3.14），CI 测两端，3.12 只靠 CI 验证、本机没有该解释器。
- 仓库定位直说成人内容个人馆藏；README、文档与网站截图一律用 SFW 演示数据（数据集在待办）。
- 制品：`.github/workflows/release.yml` 在 `v*.*.*` tag 时产出 Windows 与 macOS 压缩包，但两者都是托盘外壳，运行仍依赖本机源码安装；独立发行版是待办中「可下载制品」条目的剩余部分。

### 已实测的事实

- 全新 venv 里 `pip install -e .` 约 16 秒；`peach init` 25 个迁移、CA、`config.toml` 一次落地；`peach serve` 后 `/healthz`、`GET /`、`/api/items` 均 200。
- `pip install .`（非 editable）装出的环境缺 `migrations/` 与 `web/`，`migrations.discover()` 对缺失目录抛 `FileNotFoundError`，init 因此报错而不是静默建空账本。
- `peach-tray --help` 只打印帮助，未知参数退出 2，都不触碰数据根。
- 三个来源的默认声明根仍是示例盘符，来源 ID `local/115/pikpak` 在 `web_resource_sync.py` 与 `media.py` 里被点名；单机多本地目录做不到。这是第 5 阶段候选，见待办「来源与默认值通用化」。

### 翻公开前的验收清单

1. 本机 `& .\scripts\test.ps1`（full）全绿，且 `.claude/worktrees/` 下无未注册目录。
2. master 推到 origin 后，`Test` 工作流在 windows/macos × 3.12/3.14 与两个 web job 全绿。这是唯一能证明「没有 peach-data 的干净机器可跑」的证据；本机 master 领先 origin 数百个提交时，旧的绿结果不算。
3. `workflow_dispatch` 跑一次 `Release`，两个 build job 成功上传 artifact。
4. `MachineCoordinateTests` 通过，等价于全树 grep 个人坐标为零。
5. `README.md` 与 `README.en.md` 章节一一对应，「前置条件」「安装」「范围与免责声明」「许可证」四节都在。
6. `pip show peach` 的 `License-Expression` 为 `AGPL-3.0-or-later`。
7. 在全新 venv 里重跑一遍上面「已实测的事实」第一条。

### 翻公开的操作顺序

标【授权】的动作须当场取得明确授权。

1. 【授权】`git push origin master`。推送前确认网络出口能稳定连 GitHub：2026-09-04 一次 `git fetch` 遇到 TLS 连接中途断开。
2. 等 `Test` 工作流绿，红则先修再继续。
3. 【授权】`workflow_dispatch` 试跑 `Release`；通过后打 annotated tag `v<version>`（与 `peach.__version__` 一致）并推送。
4. 【授权】GitHub Settings → General → Change visibility → Public。
5. 【授权】随即开启：Secret scanning 与 Push protection、master 分支保护、Private vulnerability reporting；Discussions 视需要。
6. 发布后第一周只处理 issue，不改架构边界。

### 执行记录（2026-09-04）

- 仓库 `longmeidao/peach` 已 Public；第 1 至 5 步全部完成，打 tag 与正式 Release 留待独立发行版可用时一起做。
- `Test` 在 windows/macos × 3.12/3.14 与两个 web job 全绿的提交是 `4ca8433`；靶机上暴露并修掉的测试缺陷有两类：契约测试没显式传 `configured=True`（无 peach-data 的机器会拿到首次运行页），脚本测试的临时目录没 `.resolve()`。`npm audit` 对 registry 503 退避重试三次。
- 分支规则集 `protect-master`（id 22263433）：默认分支禁删除、禁强推。Secret scanning、Push protection、Private vulnerability reporting、Dependabot alerts 已开启；Dependabot security updates 未开，是否让它自动开 PR 另行决定。
- 公开后的补漏（同日）：`MachineCoordinateTests` 改成只写形状不点名的门槛（家目录路径、私网 IP、`.local` 主机名、本机账号与主机名运行时派生）；发行名定为 `peach`，目录名 `peach-app` 不变；macOS bundle ID 改中性 ID 由用户定为待办「待执行的操作」第 24 条。
- 开箱引导的顺序由用户定：先 CLI 问答（`peach init` 无参数进入问答并可首扫，逻辑在 `peach.onboarding`，已在 master），再 GUI 引导（托盘首启打开首次运行页升级成的表单，调同一组函数），两者都已在 master。
- GUI 引导已落地：未配置的机器上 `peach-tray` 起一条只绑回环的 `peach serve --setup` 引导服务并打开浏览器，首次运行页是表单，`POST /setup` 调与 CLI 同一个 `onboarding.apply()`；`tray.SetupGate` 在健康轮询里新鲜读设置文件，完成后不重启托盘进程就切到正常服务，并消费 `<数据根>/state/first-scan.request` 用子进程跑首扫。需要设置的判据是「没有 config.toml 且没有账本」，端口与失败形态见 [docs/OPERATIONS.md](../OPERATIONS.md)「首次运行与设置文件」。
- 剩余工作只在 [docs/PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)：独立发行版、口味导入引导、README 瘦身到 `CONTRIBUTING.md` 与 `docs/`，以及「待执行的操作」里 Mac 侧的第 24 与 26 条。

### 外部评审的取舍（2026-09-05）

用户带来一份外部模型对本仓库的评审。逐条对过代码后，采纳的四条已进 [docs/PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md)
第 20 至 23 条（局域网默认鉴权、全新安装冒烟、`peach doctor`、性能基准），其中第 20 条是发布口径下
唯一真正的缺陷；它的口令层已经落地（`src/peach/auth.py` 与 `cli._serve_token`），条目里只剩
局域网明文口与手机端配对码。以下三类不采纳，记在这里是为了不被反复重提：

- **已经是这样，评审读错了**：目录页默认排序用的是按日期取种的 `((a.id * seed) % 99991)` 而不是
  `ORDER BY RANDOM()`（`RANDOM()` 只在用户显式选「随机」时用）；`/api/items` 已支持 `count=0` 跳过
  精确总数；索引已按真实 ledger 的查询计划验证过。
- **方向已定，不重开**：微服务、PostgreSQL、Redis、换前端框架、容器化公网部署，见本 ADR「决策」节
  与 ADR-0022；Linux 与 Intel Mac 不在支持范围，CI 不加 `macos-*-intel`。
- **顺手做，不立专项**：`AppContext` 组合根替换 `config.py` 的模块级全局量、拆 `follow_sources.py`
  一类超大模块、主浏览流从 OFFSET 换 keyset 分页。都成立，但都属于改到那块时一并做，单独立项只会
  在待办里长期挂着。
