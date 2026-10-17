import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/base/buttons/button';
import { Input } from '@/components/base/input/input';
import { confirmModal } from '@peach/legacy/ui';
import { errorMessage } from '../../api';
import { cardClass } from '../components/card';
import { Note } from '../components/note';
import { queryClient } from '../query';
import { busyProps } from '../settings/use-action';
import { configureTasteBrowser, tasteKey, type BrowserSource } from './taste';

export function BrowserSources({ browsers, range }: { browsers: BrowserSource[]; range: string }) {
  const [adding, setAdding] = useState(false);
  const [name, setName] = useState('');
  const [path, setPath] = useState('');
  const change = useMutation({
    mutationFn: (body: Parameters<typeof configureTasteBrowser>[0]) => configureTasteBrowser(body, range),
    onSuccess: result => {
      queryClient.setQueryData(tasteKey(range), result.dashboard);
      setAdding(false); setName(''); setPath('');
    },
  });
  return <section className={`${cardClass()} flex flex-col gap-4`} aria-label="浏览器同步">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <h3 className="text-title-2-medium text-text-primary">浏览器同步</h3>
      <Button variant="secondary" size="small" onClick={() => setAdding(true)} disabled={adding}>添加浏览器</Button>
    </div>
    <p className="text-body-2-regular text-text-secondary">读取已启用的本机浏览器。移除浏览器后，已导入记录仍保留。</p>
    {change.error ? <Note tone="error">{errorMessage(change.error)}</Note> : null}
    {adding ? <form className="flex flex-col gap-3" onSubmit={event => {
      event.preventDefault(); if (!change.isPending) change.mutate({ operation: 'add', name, path });
    }}>
      <Input label="浏览器名称" value={name} onChange={setName} maxLength={80} isRequired isDisabled={change.isPending} />
      <Input label="资料目录或历史文件" value={path} onChange={setPath} maxLength={1024} isRequired isDisabled={change.isPending}
        hint="请选择运行 Peach 的电脑上的浏览器资料。" />
      <div className="flex gap-2">
        <Button type="submit" variant="secondary" disabled={!name.trim() || !path.trim()} {...busyProps(change.isPending)}>添加</Button>
        <Button variant="ghost" disabled={change.isPending} onClick={() => { setAdding(false); change.reset() }}>取消</Button>
      </div>
    </form> : null}
    <div className="flex min-w-0 flex-col gap-3">
      {browsers.map(browser => <div key={browser.id} className="flex min-w-0 items-center justify-between gap-3">
        <div className="flex min-w-0 flex-col gap-1">
          <b className="text-body-2-medium text-text-primary">{browser.name}</b>
          <span className="break-all text-caption-1-regular text-text-secondary">{browser.path}</span>
          <span className="text-caption-1-regular text-text-secondary">{!browser.enabled ? '已停止读取' : !browser.available ? '资料目录不可用' : `${browser.profiles} 个资料`}</span>
        </div>
        <Button variant="secondary" size="small" className="shrink-0" {...busyProps(change.isPending)}
          aria-label={`${browser.enabled ? '移除' : '启用'} ${browser.name}`} onClick={() => {
            if (!browser.enabled) change.mutate({ operation: 'enable', id: browser.id });
            else void confirmModal({ title: `停止读取 ${browser.name}`, body: '已导入的浏览记录仍用于口味分析。', confirmLabel: '停止读取',
              onConfirm: () => change.mutateAsync({ operation: 'disable', id: browser.id }) });
          }}>{browser.enabled ? '移除' : '启用'}</Button>
      </div>)}
    </div>
  </section>;
}
