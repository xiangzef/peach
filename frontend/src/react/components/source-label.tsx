import { MEDIA_SOURCE_ICONS } from '@peach/legacy/ui';
import { SourceMark } from '../settings/section';

function Cloud115Icon({ className }: { className?: string }) {
  return <span className={className}><SourceMark mark={MEDIA_SOURCE_ICONS['115']} /></span>;
}
function PikPakIcon({ className }: { className?: string }) {
  return <span className={className}><SourceMark mark={MEDIA_SOURCE_ICONS.pikpak} /></span>;
}
export const PROVIDER_ICONS = { '115': Cloud115Icon, pikpak: PikPakIcon };

/** 网盘与本地来源共用已登记的标识。 */
export function SourceLabel({ source, label }: { source: string; label: string }) {
  return <span className="inline-flex min-w-0 items-center gap-1.5">
    <SourceMark mark={MEDIA_SOURCE_ICONS[source] || (source === 'local' ? 'hard-drive' : 'database')} />
    <span>{label}</span>
  </span>;
}
