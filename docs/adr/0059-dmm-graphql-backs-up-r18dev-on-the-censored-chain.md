# ADR-0059：DMM 的 GraphQL 目录在有码链上给 r18.dev 兜底

- 状态：Accepted
- 日期：2026-09-24
- 修订：ADR-0048「被排除的站」里 dmm 那一行（排除的是 amane 的 HTML 爬虫，不是 DMM 这个来源）

## 背景

有码链的官方档是片商官网加 r18.dev。r18.dev 是 DMM 数字版目录的镜像，但不是全份：2026-09-24
对账本里资料最弱的 275 部抽 40 部实测，FKOS-006、FKOS-002、FNS-061、SUKE-073 在 r18.dev 是 404，
DMM 自己有；当月新片 START-640、START-639 同样 r18.dev 404、DMM 有。这些片在链上直接落到综合索引，
官方值一个都拿不到。

ADR-0048 把 dmm 排除在 amane 官方档之外，理由是那只爬虫走 `mono/dvd` 页面：答 BOD 版、发行日是
配信开始日、一次 3～14 秒。那是页面爬虫的问题，不是 DMM 这个来源的问题。DMM 新版商品页
（video.dmm.co.jp）背后是一个 GraphQL 接口 `https://api.video.dmm.co.jp/graphql`，OpenAver
（`core/scrapers/dmm.py`）已经拿它做主来源。

用户的判据是「dmm 直连可以加，但先判断要不要日本出口，需要的话就做兜底」。

## 实测

| 项 | 结果 |
| --- | --- |
| 出口 | 中国电信直连与香港出口都回 200；无年龄门、无 Cookie；不需要日本出口 |
| 速度 | 一次 0.3～1 秒 |
| 方法 | 只收 POST；GET 回 `transport not supported` |
| 详情 | `ppvContent(id)`：title、description、makerContentId、makerReleasedAt、duration（秒）、maker／label／series、actresses、directors、genres、packageImage.largeUrl、sampleImages.imageUrl |
| 搜索 | `legacySearchPPV(limit, sort: RELEASE_DATE, queryWord: "SSIS 057")`；结果只有 id，`makerContentId` 不在搜索类型上 |
| 发售日 | `makerReleasedAt` 是发售日，以 UTC 写日本时间零点：SSIS-057 答 `2021-05-06T15:00:00Z`，账本与 r18.dev 都是 2021-05-07 |
| 厂牌 | 日文名（`エスワン ナンバーワンスタイル`），r18.dev 是品牌英文名（`S1 NO.1 STYLE`） |
| 不收 | Prestige（搜 `ABW 032` 零结果，已从 FANZA 撤下）、MGS 素人号（`MIUM 1239`、`LUXU 1475` 零结果） |
| 40 部弱资料样本 | 解析到 10 部：按 cid 猜中 5、搜索到 4、只靠前缀表 1 |

## 决策

**一、自写解析器，套站点契约。** `sources/dmm.py`，来源名沿用 `dmm`（账本里 `javinizer:dmm:*` 的历史
provenance 归同一个名字，`SOURCE_SPECS` 里它本来就是 `official`），解析器名 `dmm-graphql`。不经 amane 桥：
ADR-0048 的判据是每个站只有一个归属，DMM 归 Peach。

**二、只在有码链，排在 r18.dev 之后。** r18.dev 一次请求给英文加日文两份写法与罗马字演员名，DMM
只有日文；r18.dev 答上就不问。素人链不加：目录上没有 MGS 素人号，多问只多两次白请求。
`OFFICIAL_STAGE` 加一档 `dmm`；缺标签多问一家的例外（ADR-0048）不延伸到它：两家是同一份目录，
r18.dev 答了标量没给标签，再问 DMM 拿回的还是那一套 genre。片商站没给标签而 r18.dev 落空时，
链照常走到 DMM，标签由它补。

**三、cid 由番号推，身份两道核。** 先猜 `{字母}{五位补零数字}`，猜不中再搜「字母段 数字」，搜索结果
只收字母段与数字都对得上的 cid（搜 `SSIS 057` 排前面的是 `ssis00570`，搜 `ERK 116` 会带出 `gerk116`），
带厂牌数字前缀的 cid（`h_1721fkos00006`、`1fns00061`）只有搜索答得出；取到详情再用 `makerContentId`
核一次。AI 重制版（`48midv00012ai`）排在原版之后，最多核两条。不引入 OpenAver 的 `dmm_prefix_table`：
它只命中账本 14 个前缀，样本里只多解析出 1 部，搜索覆盖了它。

**四、`Session` 加 `post`。** 契约里的传输原来只有 `get`；`_fetch` 加 `method` 与 `body` 两个参数，
重试、动作预算、404 与 403 分档同一条路。`HttpRequest` 本来就有这两个字段，两个传输层都透传。

**五、厂牌不翻。** DMM 给日文厂牌名，账本的厂牌实体靠 `entity_alias` 归一（ADR-0038）；结算顺序里
dmm 本来就排在 r18.dev 之前（`FIELD_SOURCE_ORDER`），不为这次改动。两家同时答的情形只有「r18.dev 答了
标量但没给标签」那一种，届时厂牌名分歧由结算与复核处理。

## 后果

- 有码链多一档，只在 r18.dev 落空时发请求，一部片一到三次。
- 接口是非公开的，字段名会变：过期时接口回 `errors` 且没有 `data`，归 `parse_error`、措辞带上站方那句话，
  不会被读成「没有」冻进七天记忆。
- 地区限制下 `legacySearchPPV` 回 200 加空列表，与「没收」长得一样；本机出口实测不受限，若日后受限，
  表现是猜不中 cid 的番号全部「没有」，判据写在 `sources/dmm.py` 的 `search`。
- ADR-0048 那一行的排除仍成立，只是范围收窄到 amane 的 HTML 爬虫。
