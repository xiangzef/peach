import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RiFileListLine } from '@remixicon/react';
import { Button } from '@/components/base/buttons/button';
import { errorMessage } from '../../api';
import { ErrorExcerpt } from '../activity/error-excerpt';
import { EmptyState } from '../components/empty-state';
import { useOverlayScrollbar } from '../components/overlay-scrollbar';
import { Note } from '../components/note';
import { Disclosure, Fact, FactList, Section, Stack } from '../settings/section';
import { busyProps, useAction } from '../settings/use-action';
import { DIAGNOSTICS_KEY, fetchDiagnostics, type DiagnosticCheck, type LibraryGroup } from './diagnostics';

const STATUS: Record<string, string> = { ok: '正常', warning: '需检查', failed: '需处理', unknown: '未取得', disabled: '未配置' };
const TARGET_LABELS: Record<string, string> = {
  '/settings/network': '打开网络与访问', '/settings/maintenance': '打开维护与更新', '/tasks': '查看任务',
};
const SECTIONS = [
  ['媒体库与挂载', ['media_mounts', 'data_root']],
  ['数据库与迁移', ['database', 'schema']],
  ['工具', ['ffmpeg']],
  ['配置与访问', ['configured', 'security', 'port', 'version']],
  ['后台任务', ['tasks']],
] as const;
const moment = (value: string) => new Date(value).toLocaleString();

export interface DiagnosticsProps {
  navigate(path: string): void; configure(section: string): void; openItem(id: number): void;
  receipt(message: string): void;
}

function DownloadReport() {
  const action = useAction();
  const download = () => void action.run('download', async () => {
    const response = await fetch('/api/diagnostics/bundle', { credentials: 'same-origin' });
    if (!response.ok) throw new Error(`诊断报告下载失败（HTTP ${response.status}）`);
    const url = URL.createObjectURL(await response.blob());
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = 'peach-support.zip';
    document.body.append(anchor);
    try { anchor.click() } finally {
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
  }, () => {});
  return <div className="flex flex-col items-end gap-2">
    <Button variant="secondary" onClick={download} {...busyProps(action.busy === 'download')}>下载诊断报告</Button>
    {action.error ? <Note tone="error">{action.error}</Note> : null}
  </div>;
}

function Check({ name, check, navigate, configure }: Pick<DiagnosticsProps, 'navigate' | 'configure'> & {
  name: string; check: DiagnosticCheck;
}) {
  const section = name === 'security' || name === 'port' ? '网络与访问' : '媒体库与入库';
  return <div className="flex flex-col gap-2 border-b border-separator-border py-4 pr-3 last:border-b-0">
    <div className="flex flex-wrap items-center justify-between gap-2">
      <h3 className="text-body-medium text-text-primary">{check.label}</h3>
      <span className="text-body-2-regular text-text-secondary">{STATUS[check.status] ?? '未取得'}</span>
    </div>
    <p className="text-body-regular text-text-primary break-words">{check.reason}</p>
    {check.action ? <p className="text-body-2-regular text-text-secondary">{check.action}</p> : null}
    {check.target ? <div><Button size="small" variant="secondary" onClick={() => check.target === '/settings/library'
      ? configure(section) : navigate(check.target!)}>{check.target === '/settings/library'
        ? `打开${section}` : TARGET_LABELS[check.target] ?? '打开相关页面'}</Button></div> : null}
  </div>;
}

function HealthList({ group, openItem, receipt }: Pick<DiagnosticsProps, 'openItem' | 'receipt'> & { group: LibraryGroup }) {
  const action = useAction();
  const scroll = useOverlayScrollbar<HTMLUListElement>();
  const list = group.items.map(row => row.code || `作品 #${row.id}`).join('\n');
  return <Disclosure summary={`${group.label} · ${group.count === null ? '未取得' : `${group.count.toLocaleString()} 项`}`}>
    {group.count === null ? <Note tone="neutral">清单未取得，请重新检查。</Note> : !group.items.length
      ? <EmptyState icon={RiFileListLine} title="清单为空" shell="plain">没有需要处理的作品。</EmptyState>
      : <Stack>
          <div className="flex flex-wrap items-center justify-between gap-2">
            {group.truncated ? <span className="text-body-2-regular text-text-secondary">当前显示 {group.items.length.toLocaleString()} 项</span> : null}
            <Button size="small" variant="secondary" {...busyProps(action.busy === 'copy')} onClick={() => void action.run('copy',
              () => navigator.clipboard.writeText(list), () => receipt('已复制清单'))}>复制当前清单</Button>
          </div>
          {action.error ? <Note tone="error">{action.error}</Note> : null}
          <div className="relative"><ul ref={scroll} className="flex max-h-80 flex-col gap-2 overflow-y-auto">
            {group.items.map(row => <li key={row.id}><Button size="small" variant="ghost" onClick={() => openItem(row.id)}>{row.code || `作品 #${row.id}`}</Button></li>)}
          </ul></div>
        </Stack>}
  </Disclosure>;
}

export function DiagnosticsPage(props: DiagnosticsProps) {
  const query = useQuery({ queryKey: DIAGNOSTICS_KEY, queryFn: ({ signal }) => fetchDiagnostics(signal), staleTime: 10_000 });
  const action = useAction();
  const [refreshError, setRefreshError] = useState('');
  const refresh = () => void action.run('refresh', async () => {
    const response = await query.refetch();
    if (response.error) throw response.error;
    return response.data;
  }, () => setRefreshError(''), cause => setRefreshError(errorMessage(cause)));
  const data = query.data;
  if (!data) return <div className="ui-configpage"><DownloadReport /><Note tone="error" title="诊断读取失败"
    action={<Button variant="secondary" onClick={refresh} {...busyProps(action.busy === 'refresh')}>重新检查</Button>}>
    {query.error ? errorMessage(query.error) : '诊断报告未取得。'}
  </Note></div>;
  const attention = Object.entries(data.checks).filter(([, check]) => ['warning', 'failed', 'unknown'].includes(check.status));
  const other = Object.entries(data.checks).filter(([, check]) => !['warning', 'failed', 'unknown'].includes(check.status));
  return <div className="ui-configpage flex flex-col gap-6">
    <div className="flex flex-wrap justify-end gap-2"><DownloadReport />
      <Button variant="secondary" onClick={refresh} {...busyProps(action.busy === 'refresh')}>重新检查</Button></div>
    {refreshError ? <Note tone="error">{refreshError}</Note> : null}
    {attention.length ? <Section title={`需要关注 · ${attention.length} 项`}>
      {attention.map(([key, check]) => <Check key={key} name={key} check={check} {...props} />)}
    </Section> : null}
    <Section title="库健康"><Stack>
      {data.library.issue_at ? <p className="text-body-2-regular text-text-secondary">处理记录 · {moment(data.library.issue_at)}</p> : null}
      {Object.entries(data.library.groups).map(([key, group]) => <HealthList key={key} group={group} {...props} />)}
    </Stack></Section>
    {other.length ? <Section title="系统检查"><Stack>
      <Disclosure summary={`其他检查 · ${other.length} 项`}>
        {SECTIONS.map(([title, keys]) => {
          const rows = other.filter(([key]) => keys.some(name => name === key));
          return rows.length ? <div key={title}>
            <p className="text-body-medium text-text-secondary">{title}</p>
            {rows.map(([key, check]) => <Check key={key} name={key} check={check} {...props} />)}
          </div> : null;
        })}
      </Disclosure>
    </Stack></Section> : null}
    <Section title="来源会话"><Stack>
      {data.sources.map(source => <div key={source.source} className="flex flex-col gap-2">
        <h3 className="text-body-medium text-text-primary">{source.label} · {STATUS[source.status] ?? '未取得'}</h3>
        {/* 原因常是整段堆栈：平时只露异常那一行，全文收在「查看详情」后面。 */}
        <ErrorExcerpt text={source.reason} className="text-body-regular text-text-primary" />
        <FactList>
          <Fact term="上次解析成功">{source.last_success_at ? moment(source.last_success_at) : '未取得'}</Fact>
          {source.last_check_at ? <Fact term="上次检查">{moment(source.last_check_at)}
            {source.elapsed_s !== undefined && source.elapsed_s !== null ? ` · ${source.elapsed_s.toFixed(2)} 秒` : ''}</Fact> : null}
          <Fact term="冷却截止">{source.cooldown_until ? moment(source.cooldown_until) : '未在冷却'}</Fact>
        </FactList>
      </div>)}
      <div><Button size="small" variant="secondary" onClick={() => props.navigate('/sources')}>打开来源和凭证</Button></div>
    </Stack></Section>
  </div>;
}
