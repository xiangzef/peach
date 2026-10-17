import { useRef, useState } from 'react';
import { RiArrowDownSLine, RiDatabase2Line, RiGlobalLine, RiHardDrive2Line } from '@remixicon/react';
import { Popover } from 'react-aria-components';

import { Button } from '@/components/base/buttons/button';
import { MENU_ITEM, MENU_ITEM_INTERACTIVE, MENU_POPOVER_SURFACE } from '@/components/base/dropdown/menu-styles';
import { cx } from '@/utils/cx';

import { MenuDialog } from '../components/menu-dialog';
import { busyProps } from '../settings/use-action';
import type { LibraryProcessingCommand } from './library-processing';

const COMPLETE = { label: '补全资料与预览', icon: RiDatabase2Line, command: { stage: 'collect' } } as const;
const PREVIEWS = { label: '只生成本地预览', icon: RiHardDrive2Line, command: { stage: 'previews' } } as const;
const METADATA = { label: '只采集在线资料', icon: RiGlobalLine, command: { stage: 'metadata' } } as const;
const SCAN_OPTIONS = [
  { label: '扫描并补全资料', icon: RiDatabase2Line, command: {} }, COMPLETE,
  { label: '只扫描', icon: RiHardDrive2Line, command: { stage: 'scan' } }, PREVIEWS, METADATA,
] as const;
const COMPLETE_OPTIONS = [COMPLETE, PREVIEWS, METADATA] as const;

/** 馆藏补全与扫描共用同一组操作，菜单第一项始终是主动作。 */
export function ProcessingActions({ busy, scan = false, onRun }: {
  busy: boolean; scan?: boolean; onRun(command: LibraryProcessingCommand): void;
}) {
  const trigger = useRef<HTMLButtonElement>(null);
  const [open, setOpen] = useState(false);
  const options = scan ? SCAN_OPTIONS : COMPLETE_OPTIONS;
  const primary = options[0];
  const run = (command: LibraryProcessingCommand) => {
    if (busy) return;
    setOpen(false);
    onRun(command);
  };
  return <>
    <span data-button-group data-split-button data-variant="primary">
      <Button leadingIcon={primary.icon} onClick={() => run(primary.command)} {...busyProps(busy)}>
        {primary.label}
      </Button>
      <Button ref={trigger} iconOnly leadingIcon={RiArrowDownSLine}
        aria-label={scan ? '更多扫描与采集方式' : '更多资料与预览补全方式'}
        aria-haspopup="dialog" aria-expanded={open} {...busyProps(busy)} onClick={() => { if (!busy) setOpen(!open) }} />
    </span>
    <Popover triggerRef={trigger} isOpen={open} onOpenChange={setOpen} placement="bottom end" offset={4}
      className={MENU_POPOVER_SURFACE}>
      <MenuDialog aria-label={scan ? '扫描与采集方式' : '资料与预览补全方式'}
        className="flex w-56 flex-col gap-1 outline-none">
        {options.map(({ label, icon: Icon, command }) => <button key={label} type="button"
          className={cx(MENU_ITEM, MENU_ITEM_INTERACTIVE, 'text-body-2-medium')} onClick={() => run(command)}>
          <Icon aria-hidden className="size-4 shrink-0" />{label}
        </button>)}
      </MenuDialog>
    </Popover>
  </>;
}
