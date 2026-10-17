# Docker 部署

Peach 的 Linux 无桌面镜像用于单人 VPS 与 NAS，镜像仓库为 [longmeidao/peach](https://hub.docker.com/r/longmeidao/peach)。`edge` 是主线候选，版本号标签对应发布提交。当前镜像目标为 `linux/amd64`；ARM NAS 尚未验收。2026-10-15 在 WSL 的独立 Docker Engine 中，用正式锁定依赖通过空数据卷初始化、非 root、鉴权、配置保存、合成视频扫描、HTTP Range、配置重载与重启持久化验收。

## 数据与媒体

`/data` 保存配置、SQLite 账本、凭据和图片缓存，必须持久化。媒体通过 `/media` 单独挂入；默认只读，扫描和播放不需要媒体写权限。整理、移动与删除需要使用者明确提供可写挂载。

CloudDrive2 与 Peach 分别运行。NAS 已有 CloudDrive2 时直接复用；全新机器按 [CloudDrive2 官方 Docker 指南](https://www.clouddrive2.com/docker.html) 安装并绑定网盘。宿主机必须支持 FUSE，CloudDrive2 的挂载目录需要共享传播；Peach 用 `rslave` 接收挂载，不需要 FUSE 或特权容器。挂载目录的权限必须允许 UID 1000 读取。

需要云下载或推送发现时，Peach 配置中的 CloudDrive2 API 地址使用同一容器网络的服务名或可达的宿主机地址；容器里的 `127.0.0.1` 只指向 Peach 自己。

仓库根的 `compose.yaml` 使用 `PEACH_MEDIA_ROOT` 指定宿主机已有媒体根；容器中固定为 `/media`。先完成 CloudDrive2 挂载，再启动 Peach。命名卷 `peach-data` 保存 `/data`，不要执行删除该卷的操作。需要绑定现有数据目录时，先做完整备份并确保 UID 1000 可写；不要让另一台 Peach 同时写这份账本。

## 首次运行与访问

使用 Compose 启动后，无桌面入口会为全新数据卷初始化配置、账本和随机内部口令。它不覆盖已有配置；发现只有账本而没有配置时拒绝启动。初始化日志只显示口令文件位置。

在容器终端运行 `peach token` 取得登录口令，在浏览器登录后设置访问密码。配置页接受经过鉴权的回环或私有网络连接，带转发头的管理请求会被拒绝。配置页添加媒体文件夹时填容器内路径，例如 `/media/115`；对应声明根沿用 `B:\`，PikPak 沿用 `A:\`。配置保存会自动重载服务；勾选扫描时使用既有资料处理入口。

容器内 HTTP 端口固定为 8900，访问端口在 Compose 设置。默认只发布到宿主机 `127.0.0.1`，远程访问使用私有 VPN 或 SSH 隧道。需要局域网访问时，通过 `PEACH_BIND` 绑定宿主机的局域网地址，并设置访问密码。公网托管边界见 [安全说明](../SECURITY.md)。Docker 镜像不提供多人账号或租户隔离。

## 更新与范围

更新镜像并重建容器时保留 `/data`。数据库有待执行迁移时，先备份并按 [运行与配置](OPERATIONS.md) 的迁移流程处理；无桌面入口不会自动迁移已有账本。健康检查使用 `/healthz?ready=1`。

Linux 容器不读取用户电脑上的浏览历史，也不包含交互式浏览器；需要本机浏览器完成验证的来源在此环境不可用。CloudDrive2 的真实账号登录、网盘流量与 NAS 实机挂载需在目标机器验证。

## 镜像发布

构建使用官方 Python `3.14.8-slim-trixie` 与 uv `0.13.1`，依赖由 `uv.lock` 锁定，应用以非 editable 包安装，包含 Web 与迁移资源。镜像以 UID/GID 1000 运行，内置 FFmpeg、FFprobe 和 OpenSSL。构建上下文只允许代码与资源，不包含工作树、媒体、真实账本或凭据。

GitHub Actions 的 `Docker` 工作流先构建并运行临时卷验收，通过后发布。仓库变量 `DOCKERHUB_USERNAME` 和机密 `DOCKERHUB_TOKEN` 用于 Docker Hub 发布；机密只保存在 GitHub，不进入项目文件。未配置发布身份时仍执行构建验收。ARM 镜像需通过同等运行验收后再加入发布。
