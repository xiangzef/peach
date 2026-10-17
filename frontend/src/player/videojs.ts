/* Video.js 的按需加载器：主脚本、中文语言包与样式表。
 *
 * 和灯箱的 Swiper 同一个理由：video.js 676KB、样式表 48KB，只有真的开始看片才用得上，进首屏就是
 * 每次开页都白下一遍。主脚本与语言包有依赖——`videojs.addLanguage` 得先有 videojs——必须串行；
 * 样式表与它们并行，三样都到了才交出 `videojs`，播放器的控件从第一帧起就带着样式。版本只钉在这里，
 * `tests/test_dependency_policy.py` 核它与 `package.json` 一致。 */
import type { VideojsFactory } from './types';

const VIDEOJS = '/vendor/videojs/8.24.2/';
const STYLESHEET = `${VIDEOJS}video-js.min.css`;

const loadScript = (src: string): Promise<void> => new Promise((resolve, reject) => {
  /* 已插入的脚本复用加载状态，不重复请求；data-loaded 表示已完成。 */
  const existing = document.head.querySelector<HTMLScriptElement>(`script[src="${src}"]`);
  if (existing?.dataset.loaded) { resolve(); return }
  const script = existing ?? document.createElement('script');
  script.addEventListener('load', () => { script.dataset.loaded = '1'; resolve() }, { once: true });
  script.addEventListener('error', () => { script.remove(); reject(new Error(`script unavailable: ${src}`)) }, { once: true });
  if (!existing) { script.src = src; document.head.appendChild(script) }
});

/* 样式表插在页面第一张样式表前面，占住它在 `<head>` 里的层叠位置：`peach-app.css` 里的 `player.css`
   与 `/app.css`、`/board.css` 按同样的特指度覆盖 Video.js 的默认样式，靠的是排在它后面。已插入的不重复添加；已经生效的（`sheet` 在）直接算好。样式表取不回来不拦播放器，控件照样挂上。 */
const loadStylesheet = (href: string): Promise<void> => new Promise((resolve) => {
  const existing = document.head.querySelector<HTMLLinkElement>(`link[rel="stylesheet"][href="${href}"]`);
  if (existing?.sheet) { resolve(); return }
  const link = existing ?? document.createElement('link');
  link.addEventListener('load', () => resolve(), { once: true });
  link.addEventListener('error', () => { link.remove(); resolve() }, { once: true });
  if (!existing) {
    link.rel = 'stylesheet';
    link.href = href;
    document.head.insertBefore(link, document.head.querySelector('link[rel="stylesheet"]'));
  }
});

const current = (): VideojsFactory | undefined => (globalThis as { videojs?: VideojsFactory }).videojs;

let loader: Promise<VideojsFactory> | null = null;

/** 取全局 `videojs`；没有就装样式表，同时按顺序装主脚本与中文语言包。失败把加载器清空，一次网络抖动
 *  之后这一整页还挂得上播放器。 */
export function ensureVideojs(): Promise<VideojsFactory> {
  const ready = current();
  if (ready) return Promise.resolve(ready);
  loader ??= Promise.all([
    loadStylesheet(STYLESHEET),
    loadScript(`${VIDEOJS}video.min.js`).then(() => loadScript(`${VIDEOJS}lang/zh-CN.js`)),
  ])
    .then(() => {
      const factory = current();
      if (!factory) throw new Error('videojs unavailable');
      return factory;
    })
    .catch((error: unknown) => { loader = null; throw error });
  return loader;
}
