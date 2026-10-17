<p align="center">
  <img src="resources/peach-logo.png" alt="Peach" width="96">
</p>

<h1 align="center">Peach</h1>

<p align="center">A private video library for yourself: local drives, cloud drives and the creators you follow, all in one place.</p>

<p align="center">
  <a href="https://github.com/peach-mitao/peach/releases">Download for Windows</a> ·
  <a href="https://demo.peach.video">Live demo</a> ·
  <a href="https://github.com/peach-mitao/peach/releases/tag/intro-video">Intro video</a> ·
  <a href="https://github.com/peach-mitao/peach/issues">Report a problem</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="README.md">中文</a>
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

> **18+** For adults managing their own adult-content collections. The repository contains no media or site data. When Peach connects to outside sites it uses your own accounts and access rights.

- **Already-organized videos just work**: scanning reads the NFO files and posters that already sit next to your videos, so nothing needs to be scraped again.
- **Your files stay put**: scanning is read-only and files stay where they are. Renaming or moving only happens when you start it, with a preview first and an undo afterwards.
- **Cloud and local together**: once 115 or PikPak is mounted as a local drive with CloudDrive2, its videos join the same library as your hard drives.
- **Mount status**: media directories are checked periodically. A failed read is checked again before the tray and video page show the affected source and reason. Scans skip NAS recycle bins and system folders.
- **Pick from the video wall**: drag through a full-screen cover wall, expand a work and play in place, with versions and parts available directly.
- **Cross-site following and new releases**: bring a creator's updates from multiple sites into one feed. Subscribe by performer name, including performers outside your library.
- **Your data stays on your computer**: watch history, favorites and settings are stored locally. When filling in details, Peach only sends the video code or performer name to source sites. With cloud download, a magnet link goes only to the cloud drive you pick.
- **Company profiles**: studio and agency pages can show company names, foundation dates, brand launch dates, locations and operating relationships when sourced information is available.
- **Direct links**: assets use `/assets/:id`, works use `/works/:code` and followed posts use `/posts/:id`. Entity profiles use stable IDs; settings sections live under `/settings`. See the [page routes](docs/ROUTES.md).

## Screenshots

Want to look around before installing? The [live demo](https://demo.peach.video) is a ready-made library where you can try search, performer pages, filters and stats. The demo is read-only, so nothing you do is saved.

The original screenshots are lossless 3840×2160 PNGs; click to view them. You can also try the video wall in the demo.

**Home: filter by source, length and tags**

<a href="https://peach.video/assets/screenshots/home-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/home-20261014.webp" alt="Home: performer and studio navigation, filters and work cards" width="1200"></a>

**Video wall: drag to explore, play in place, switch versions and parts.**

<a href="https://peach.video/assets/screenshots/wall-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/wall-20261014-readme.webp" alt="Video wall: full-screen covers and browsing controls" width="1200"></a>

**Performer page: profile, aliases, links and every video**

<a href="https://peach.video/assets/screenshots/profile-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/profile-20261014.webp" alt="Performer profile: portrait, details and works" width="1200"></a>

**Following: one creator's updates from several sites in one feed**

<a href="https://peach.video/assets/screenshots/follow-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/follow-20261014.webp" alt="Following: creator navigation, filters and image updates" width="1200"></a>

**Statistics: where your videos live and how much you have watched**

<a href="https://peach.video/assets/screenshots/stats-20261014.png" target="_blank" rel="noopener"><img src="https://peach.video/assets/screenshots/stats-20261014.webp" alt="Statistics: library totals, storage and content distributions" width="1200"></a>

## What it does

- **Browse folders**: the right side of the library filter bar offers card and list views and a folder mode switch. List view supports sorting across all matching items, pagination with 20 items per page by default, and selection across pages. Search, filters, and details share the same library. Keep personal categories or confirm a folder as a person, creator account, seller, or studio. Preview the affected items before saving, optionally apply the rule to future files, and remove the rule when needed. Conflicting assignments stay in place. See [folder browsing](docs/DIRECTORY_BROWSING.md).

- **Search**: focus the search field to browse library works, JAV releases, followed videos and images, and subscribed releases by cover; enter performer and followed creator pages through their avatars. Follow and new release subscriptions are also available from the menu. Type a few characters to search performers, codes and videos together.
- **My Favorites**: use the star beside a profile name to favorite people, makers, labels, series and tags; a solid yellow star shows a favorite. The star button in library, discovery, follow and profile filters opens My Favorites, with type and name search and profile images, label logos or creator avatars. The dialog shares the settings glass navigation, keeps saved filters in their own tab, and links to Marked and Watch Later at the bottom of navigation. On library pages, name the current filter to open or delete it later.
- **Source checks**: choose direct access or the Peach proxy per source, and inspect failure reasons, elapsed time and cooldowns. Configure, preview and enable public JSON metadata APIs on the sources page; see [custom sources](docs/CUSTOM_SOURCES.md). Review images load when requested and can be retried.
- **External players and VR**: generate a temporary network playback link from a work's detail, download an M3U playlist, or open VLC on iPhone/iPad and IINA on Mac; see [external players](docs/EXTERNAL_PLAYERS.md).
- **Identity categories**: performers are grouped by identity and release market into JAV performers, amateurs, Western performers, adult bloggers and animation authors. Amateurs are performers with trusted evidence of non-professional appearances, or whose every video is an amateur release (an FC2-PPV code, or a 素人 tag that does not come from the vision model); JAV and Western performers are never filed as amateurs, and other genres only filter videos. The roster has three side-by-side entries, Performers, Sellers and Online, and sellers are matched to their works by source account. The filter bar only shows categories that have entries, and profile pages show the category with an icon left of the video count.
- **Video counts**: clearly segmented parts of the same FC2 collection count as one video, while the part files and cast credits are kept in full. Identities confirmed as merged share their profile and videos, and old profile URLs lead to the canonical identity.
- **Versions and parts**: subtitle, uncensored, resolution and restored versions of the same release share one card. Each version keeps its own parts and continues to its next part when playback ends.
- **Trash**: cards show whether an item was moved manually, marked as junk or a duplicate, or had a missing file. Videos and other resources can be restored directly. Items without a recorded reason show “Reason not recorded”.
- **Account identity**: the adult blogger category needs an identity or account source; unverified entries remain visible in the full roster. Account avatars prefer saved images. A personal blogger with evidence of their own identity gets an avatar automatically once the same face is cut from frames of two videos; other accounts show a frame from a representative video, marked as not the person. Aliases on profile pages carry identity names only; quality and bundle labels stay in the file details.
- **Western image sources**: performers and adult bloggers can use a Babepedia gallery portrait. For Vixen network titles such as Tushy, official covers are matched by performer and release date and shared by cards, details and avatar cropping; titles without a unique match wait for review.
- **Performer pages**: aliases, birthday and measurements, social accounts and JavDB and MISSAV links on one page, above every video of hers in your library and her photos. When changing the avatar, gallery portraits, video covers, local images and image URLs can all be cropped with a box first, or used whole.
- **Filling in details**: by video code, Peach fills in titles, performers and studios from studio sites, DMM, JavBus, JavDB and others. Covers favor larger official originals; JavDB images are used only for verification. Metadata collection only fills empty fields and never overwrites your edits.
- **Covers and previews**: when videos lack artwork, library lists and details offer **补全资料与预览** to collect covers and generate frame previews for local videos. Its menu offers **只生成本地预览** (local previews) and **只采集在线资料** (online metadata). Process the whole library under **数据管理 → 扫描与采集**.
- **Playback**: play in the browser and pick up where you left off. Like, rate, save for later, add to a playlist, or "log a climax". Library and followed-post details offer a horizontally scrolling recommendation row; choose a card to switch directly.
- **Video wall**: the persistent entry at the top right opens a dedicated full-screen wall of works with covers. Drag in any direction to explore automatically loaded, unseen works. Expand a tile in place as nearby tiles rearrange; the selected tile is highlighted and the others dimmed. Play and switch parts or versions on the wall, or open the shared details; playback can continue in the miniplayer when collapsed. Full sleeves and front panels adapt to tile proportions and face framing, with a thumbnail option. Playback blurs the cover background and moves the title to the top. The wall inherits library search, filters and profile scope. A notice at the top clears work filters while retaining the JAV and source context. The button beside Back changes the batch with a gray, blurred wall while waiting, and the corner tools provide search, image choice and zoom.
- **New releases**: subscribe on a performer page or by name in follow management, including performers not yet in your library. Peach checks for new titles regularly. Cards show performer avatars and open an in-site work detail with metadata, preview images, comments and resources; click an avatar with a saved profile to open it. Follow creators across sites such as FANBOX, Patreon and Kemono; the same work on different sites appears as one card.
- **Media cache**: followed images, work previews and fully received video content are saved locally for reuse. Avatars refresh every 3 months and favicons yearly. Follow management shows Retry failed sources when enabled sources have failed checks.
- **Online creators**: creator pages show local works and online updates separately, with video and image views and filters. Choose and crop an avatar from social profiles, online covers or post images, or use a local image or image URL.
- **JAV**: Library shows acquired titles; Discover uses your taste records to explore known titles outside your library and little-watched titles within it, regardless of release date, with tag filters and large or small covers; Wanted tracks titles to find, with magnet availability filters and saved resource results. Click a discovery card to open its details. Mark a work card or followed post as wanted, or enter a video code. Files scanned into your library are marked as acquired.
  Registered studios open their profiles; unregistered studios display their names. Theater mode expands within the detail dialog and hides thumbnails and pagination. Library titles without registered sample images load source previews on demand.
  Discovery cards share the home page's avatar and byline styles and use locally registered names. Cached recommendations appear immediately and update in the background; the filter toolbar's refresh icon updates work metadata. Closing details preserves filters, sorting and scroll position. Theater mode fills the available area and hides thumbnails and pagination below the video; exiting restores the regular view. Image navigation buttons stay at the media area's left and right edges.
  Work details, comments and resources survive restarts. New releases update on demand once a day; a complete snapshot acquired more than one month after release is retained, with manual refresh available.
- **Cloud download**: open Find resources from JAV or a quality goal, search a video code or paste a magnet link, then submit the selected resource to 115 or PikPak. Once it lands, Peach selects the main video, isolates promotional attachments that meet the automatic threshold, collects metadata and applies that source's organization template. Progress and failed-step retries show up in Activity.
- **Find a release**: direct cloud downloads search `manko.fun → JavDB → Sukebei` first and stop when manko.fun has a 1080p or 2160p match; without one, they continue through your configured Prowlarr or Jackett indexers. Wanted titles collect candidates from multiple sources so you can compare versions. Available covers and title details appear with the resource candidates.
- **Statistics**: which drive holds what, how much you have watched and which tags dominate, on one page.
- **Taste**: combines viewing, feedback, accumulated library titles, browsing history and followed accounts. Read local Aside, Chrome, Edge or Firefox profiles, or add another browser's profile directory. Stopping sync and deleting imported records are separate controls. Social visits are associated with registered accounts and known identities.
- **Settings**: the dialog groups appearance and navigation, browsing and playback, JAV and new releases, search and recommendations, and content display. Peach configuration groups media intake, sources and subscriptions, download channels, network access, and application maintenance.
- **Any screen**: works in the browser on desktop, tablet and phone.

## Download and use

### Windows

1. Download one of the two packages from [Releases](https://github.com/peach-mitao/peach/releases):
   - Installer `Peach-<version>-windows-x64-setup.exe`: double-click to install and choose an installation folder. No administrator rights needed; Peach appears in the Start menu and can be uninstalled from Windows Settings.
   - Portable `Peach-<version>-windows-x64.zip`: right-click it, choose "Extract All", then double-click `Peach.exe` inside.
2. Your browser opens the first-run setup page.
3. Pick your media folders and who may access Peach, then start the scan.

If you already have a library but see first-run setup, choose **使用已有数据目录** and enter its `peach-data` folder. Peach keeps the existing settings, ledger and access password, and remembers the folder.

Windows standalone builds can check for and download updates under **应用与维护** in Configuration. Confirm a restart to install a downloaded update. Automatic checks and downloads are off by default and can be enabled there.

Downloading an update leaves tasks running. Installing an update saves progress and pauses scraping and preview generation; collection requests made during installation wait for it to finish. After installation finishes or is cancelled, a running Peach service resumes the tasks automatically. If Peach has exited, it resumes unfinished library metadata, local previews, timeline thumbnails and cover tasks on the next launch, reusing completed results. Turning thumbnail collection off explicitly keeps it stopped.

Both the Windows installer and portable ZIP include FFmpeg, ffprobe and untrunc for transcoding, thumbnails and MP4 index recovery. Corresponding source is available in the same Release; the tools directory contains licenses and build notes. See [Windows test build](docs/TESTING_DESKTOP.md). The test package is not code-signed yet. If Windows says "Windows protected your PC", make sure the file came from this project's Releases, then choose "More info → Run anyway".

On Windows, the tray runs independently. Closing the Codex, Claude, or terminal session that started it keeps Peach running. Peach attempts to recover after an unexpected tray exit, up to three times within five minutes. Choosing “Quit Peach” keeps it closed. Exit reasons and recovery results are recorded in `tray-lifecycle.log` in the logs folder.

Startup error dialogs show where a diagnostic report was saved. While Peach is running, choose “Export diagnostic report” in the tray menu or “Download diagnostic report” on the diagnostics page to collect a redacted ZIP for feedback. The tray export dialog can open the report folder, open the file, or close.

### Run from source (Windows, macOS)

You need Git, [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.14 or newer (`.python-version` selects Python 3.14 for production; uv downloads a missing interpreter for you):

```powershell
git clone https://github.com/peach-mitao/peach.git peach-app
cd peach-app
uv sync --locked --python 3.14
& .\.venv\Scripts\peach-tray.exe
```

On macOS, replace the last two lines with `uv sync --locked --python 3.14 --extra macos` and `./.venv/bin/peach-tray`.

LAN access, access passwords, updates and uninstalling are covered in [Operations](docs/OPERATIONS.md).

Open System diagnostics under Peach configuration → Application and maintenance to view library health lists, source parsing and cooldowns. `peach doctor` provides the same report; `--json` returns redacted JSON. See [Local diagnostics](docs/OPERATIONS.md#本机诊断) for status and actions.

### Docker (VPS / NAS)

The headless Linux image runs alongside CloudDrive2, with separate mounts for media and application data. See [Docker deployment](docs/DOCKER.md) for setup, access boundaries and validation status.

## FAQ

- **Will it change my files?**
  - Scanning and filling in details never touch the original files.
  - Only three things do:
    - Running an organize job you started: rename or move, with a preview first and an undo for the last batch.
    - Emptying the trash: this really deletes.
    - Confirming a cleanup in resource sync: folders that are already empty on disk are deleted; each source's root folder stays.
- **I already organized my videos with another scraper. Can Peach use that?**
  - Peach reads the Kodi and Jellyfin layout:
    - an `.nfo` named after the video;
    - posters such as `<title>-poster.jpg`.
  - Existing titles, performers, studios and posters show up right away.
- **Which cloud drives are supported?**
  - 115 and PikPak, mounted as local drives with CloudDrive2.
  - CloudDrive2 can also run on a NAS such as Synology. Map the shared folder to a Windows drive letter, then select that folder in Peach; this setup does not require CloudDrive2 or WinFsp on Windows.
  - For playback, Peach reads them like ordinary folders and does not store your cloud account.
  - For cloud download, the CloudDrive2 API token and the PikPak sign-in token are kept in this computer's credential file.
  - For PikPak, "Sign in with browser" is the recommended way: you sign in inside the window it opens, and Peach never sees your password. Signing in with your account and password also works; the password is saved only if you tick "Save password".
- **How do I watch on my phone?**
  - Choose "devices on the same network" during first-run setup.
  - Connect your phone to the same network and open the address shown on the setup page.
  - Setting an access password is a good idea.
- **Where is my data?**
  - In the `peach-data` folder on your computer.
  - The Windows build keeps it in `%LOCALAPPDATA%\Peach\peach-data` by default.

## Reporting problems

Open an [issue](https://github.com/peach-mitao/peach/issues) with the version, what you did, what you expected and what actually happened, ideally with a screenshot. Before taking screenshots, hide passwords, cookies, LAN addresses and full file paths, and do not upload database files or media. Report security issues privately as described in the [security policy](SECURITY.md).

## Documentation

Using Peach: [Windows test build](docs/TESTING_DESKTOP.md) · [Operations](docs/OPERATIONS.md) · [Sourcing](docs/SOURCING.md) · [Cloud drive mounts](docs/CLOUDDRIVE.md) · [Changelog](CHANGELOG.md)

Contributing: [Development guide](AGENTS.md) · [Architecture](docs/ARCHITECTURE.md) · [Testing and dependencies](docs/TESTING.md) · [Frontend](docs/FRONTEND.md) · [Reuse inventory](docs/REUSE.md) · [README maintenance](docs/README_MAINTENANCE.md) · [Documentation and UI copy](docs/WRITING.md). Verify changes with Windows `& .\scripts\test.ps1` or macOS/Linux `./scripts/test.sh`.

## Related projects

- [amane](https://github.com/sqzw-x/amane): Peach reaches studio sites and other sources through it.
- [Gfriends](https://github.com/gfriends/gfriends): performer avatar collection.
- [CloudDrive2](https://www.clouddrive2.com/): mounts cloud drives as local disks.
- [OpenAver](https://github.com/slive777/OpenAver), [Javinizer-Go](https://github.com/javinizer/javinizer-go), [MetaTube](https://github.com/metatube-community/metatube-sdk-go), [MDCx](https://github.com/sqzw-x/mdcx): Peach learned from their source parsing and recommendation approaches.

The full reuse and credits list is in the [reuse inventory](docs/REUSE.md).

## Star history

<a href="https://www.star-history.com/?repos=peach-mitao%2Fpeach&amp;type=date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=peach-mitao/peach&amp;type=date&amp;theme=dark">
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=peach-mitao/peach&amp;type=date">
    <img alt="Peach Star history" src="https://api.star-history.com/chart?repos=peach-mitao/peach&amp;type=date">
  </picture>
</a>

## License

[AGPL-3.0-or-later](LICENSE) · Copyright (C) 2026 longmeidao. Third-party frontend files keep their own licenses. The [dependency manifest](package.json) records versions, and the [vendor script](scripts/vendor_web_dependencies.mjs) records file and license locations in `web/vendor/`.
