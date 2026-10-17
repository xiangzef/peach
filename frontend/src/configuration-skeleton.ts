import { islandButton } from './island-skeleton';

// 首屏在 React 包到达前绘制，几何与 settings/section.tsx、BoardUI SettingsRow 共用类名。
const section = (title: string, content: string) => `<section aria-label="${title}" class="flex w-full flex-col gap-2"><p class="w-full px-3 text-body-2-medium text-text-secondary">${title}</p><div class="flex w-full flex-col rounded-2xl bg-background-secondary-default pl-3">${content}<div class="-ml-3 flex flex-wrap items-center justify-end gap-3 rounded-b-2xl border-t border-separator-border bg-card-footer px-3 py-3">${islandButton({ label: '保存配置', attrs: 'disabled data-skeleton-action' })}</div></div></section>`;
const row = (label: string, description = '', control = 'ui-configuration-skeleton-toggle') => `<div class="flex min-h-[52px] w-full items-center justify-between gap-4 py-2.5 pr-2.5 border-b border-separator-border last:border-b-0"><div class="flex min-w-0 flex-col"><p class="text-body-regular text-text-primary">${label}</p>${description ? `<p class="text-body-2-regular text-text-secondary">${description}</p>` : ''}</div><span class="skeleton ${control}"></span></div>`;

export function configurationSkeleton(): string {
  const nav = `<div class="ui-board-local-nav" data-section-nav data-section-items>${['媒体库与入库', '来源与订阅', '下载渠道', '网络与访问', '应用与维护'].map((title, i) => `<button type="button" tabindex="-1" aria-selected="${i === 0}">${title}</button>`).join('')}</div>`;
  const media = section('媒体文件夹', `<div class="flex flex-col gap-3 py-4 pr-3">${row('媒体文件夹', '', 'ui-configuration-skeleton-select')}${row('媒体库名称', '', 'ui-configuration-skeleton-select')}</div>`);
  return `<div class="peach-react"><div class="ui-configpage">${nav}<div class="flex flex-col gap-6">${media}</div></div></div>`;
}
