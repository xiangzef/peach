import { afterEach, expect, it, vi } from 'vitest';
import { confirmModal } from '../src/ui-kit';

afterEach(() => document.body.replaceChildren());
it('危险操作聚焦取消，取消不写入，关闭归还焦点', async () => {
  const trigger = document.createElement('button'); document.body.append(trigger); trigger.focus();
  const write = vi.fn();
  const pending = confirmModal({title:'清理记录',body:'清理 2 项',confirmLabel:'清理记录',danger:true,onConfirm:write});
  const cancel = document.querySelector<HTMLButtonElement>('[data-modal-cancel]')!;
  expect(document.activeElement).toBe(cancel);
  cancel.click();
  expect((await pending).confirmed).toBe(false);
  expect(write).not.toHaveBeenCalled(); expect(document.activeElement).toBe(trigger);
});
it('等待写入时阻止重复提交和关闭，失败保留弹层可重试', async () => {
  let reject!: (error: Error) => void;
  const write = vi.fn().mockImplementationOnce(() => new Promise((_, fail) => { reject = fail; })).mockResolvedValueOnce('done');
  const pending = confirmModal({title:'清理记录',body:'清理 2 项',confirmLabel:'清理记录',onConfirm:write});
  const dialog = document.querySelector('dialog')!;
  const accept = dialog.querySelector<HTMLButtonElement>('[data-modal-confirm]')!;
  accept.click(); accept.click();
  dialog.querySelector<HTMLButtonElement>('[data-modal-cancel]')!.click();
  const escape = new Event('cancel', {cancelable: true}); dialog.dispatchEvent(escape);
  expect(escape.defaultPrevented).toBe(true); expect(dialog.open).toBe(true); expect(write).toHaveBeenCalledTimes(1);
  reject(new Error('磁盘离线')); await new Promise(resolve => setTimeout(resolve, 0));
  expect(dialog.textContent).toContain('磁盘离线'); expect(dialog.open).toBe(true);
  accept.click(); expect((await pending).result).toBe('done'); expect(write).toHaveBeenCalledTimes(2);
});
