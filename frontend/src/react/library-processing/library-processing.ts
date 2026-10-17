/* 扫描与采集的数据契约、轮询节律与纯折算。
 *
 * 数据管理页卡片、目录横幅与缺预览提示读同一个 `queryKey`，使用同一份任务快照。
 * 轮询也由 Query 合成一份，进度、失败与完成状态由服务端统一提供。
 * 端点在 `frontend/src` 里只在这里声明一次（`tests/test_frontend_build.py` 盯着）。 */
import { apiGet } from '../../api';
import { elapsedText } from '../activity/tasks';
import { queryClient } from '../query';

export const LIBRARY_PROCESSING_URL = '/api/library-processing';

/** 卡片与横幅共用这一个键。 */
export const LIBRARY_PROCESSING_KEY = ['library-processing'] as const;

/** 处理过程中记下的一条问题。`asset_id` 为空时说的是媒体来源本身。 */
export interface LibraryProcessingIssue {
  asset_id: number | null;
  title?: string;
  path?: string;
  message: string;
  /** `paused` 是来源限流没轮到这一项，等来源放开再跑就有；`error` 是它自己出的事。 */
  severity?: 'info' | 'error' | 'paused';
}

/** 一趟扫描与采集的快照。字段以 `q_library_processing`（`src/peach/web_library_processing.py`）为准。 */
export interface LibraryProcessingData {
  /** `idle` | `running` | `complete` | `failed`。 */
  status: string;
  job_id?: string;
  stage?: string;
  requested_stage?: string;
  checked?: number;
  total?: number;
  scanned?: number;
  identified?: number;
  candidates?: number;
  auto_applied?: number;
  covers?: number;
  previews?: number;
  /* 落库之后补齐女优资料那一步的四个读数：别名、头像、交回人工的冲突、没取到的头像。 */
  performer_aliases?: number;
  performer_avatars?: number;
  performer_profile_conflicts?: number;
  performer_profile_failed?: number;
  error?: string;
  issue_count?: number;
  /** `issue_count` 里卡在来源限流上的那些，等来源放开再跑一次就有。 */
  paused_count?: number;
  issue_preview?: LibraryProcessingIssue[];
  issues_log?: string;
  issues_truncated?: boolean;
  retryable_asset_ids?: number[];
  notes?: Record<string, number>;
  current_asset_id?: number | null;
  current_asset_name?: string;
  current_action?: string;
  current_started_at?: number;
  last_progress_at?: number;
  stalled?: boolean;
  waited_seconds?: number;
  completed_at?: number;
}

/** 一次写操作的请求体：指定处理阶段与影片，或者按任务号重试失败项。 */
export type LibraryProcessingCommand =
  | Record<string, never>
  | { stage: 'scan' | 'collect' | 'previews' | 'metadata'; asset_ids?: number[] }
  | { job_id: string; retry: number[] };

export const fetchLibraryProcessing = (signal?: AbortSignal) =>
  apiGet<LibraryProcessingData>(LIBRARY_PROCESSING_URL, signal);

/** 首屏。中止时 `fetchQuery` 把 `AbortError` 抛回挂载方，它据此放弃这一次。 */
export async function prefetchLibraryProcessing(signal: AbortSignal): Promise<void> {
  await queryClient.fetchQuery({
    queryKey: LIBRARY_PROCESSING_KEY,
    queryFn: () => fetchLibraryProcessing(signal),
  });
}

/** 在跑的时候两秒问一次，和别的后台任务同一个节律。 */
export const RUNNING_POLL_MS = 2000;
/** 闲着时也接着问：任务由后台自己起，两个读者都要认出「现在跑起来了」。 */
export const IDLE_POLL_MS = 10_000;

/** 读失败时页面上留的那句话。上一份数据不撤，下一轮轮询自己会接上。 */
export const DISCONNECTED_TEXT = '连接中断，正在重新读取处理进度';

export function pollInterval(
  data: LibraryProcessingData | undefined, watching: boolean,
): number | false {
  if (data?.status === 'running') return RUNNING_POLL_MS;
  return watching ? IDLE_POLL_MS : false;
}

const ACTION_LABELS: Record<string, string> = {
  reading_local: '读取本地资料',
  querying_metadata: '查询外部资料',
  fetching_cover: '采集缺失封面',
  generating_preview: '生成视频预览',
  writing_candidates: '保存资料候选',
};

/* 来源说「没有」按类型报一个数，不进问题清单：馆藏里大量独立资源和创作者作品
   任何目录站都收不到，它们不是待办。键与 `library_processing.MISS_MESSAGES` 同源。 */
const NOTE_LABELS: Record<string, string> = {
  querying_metadata: '没有资料',
  fetching_cover: '没有封面',
};

export function notesLine(notes: Record<string, number>): string {
  const parts = Object.entries(notes)
    .filter(([key, count]) => NOTE_LABELS[key] && count > 0)
    .map(([key, count]) => `${NOTE_LABELS[key]} ${count.toLocaleString()} 部`);
  return parts.length ? `外部来源${parts.join('、')}，7 天内不再问。` : '';
}

/** 此刻在做什么：哪个文件、哪一步、等了多久。 */
export function currentLine(state: LibraryProcessingData): string {
  const action = ACTION_LABELS[state.current_action || ''] || state.stage || '正在处理';
  const waited = state.waited_seconds ? ` · 已等待 ${elapsedText(state.waited_seconds)}` : '';
  return state.current_asset_name
    ? `当前：${state.current_asset_name} · ${action}${waited}`
    : action + waited;
}

/** 折叠起来的问题清单：一句结论 + 逐条明细 + 完整日志的地址。没有问题时是 `null`。 */
export interface IssueDetails {
  label: string;
  items: { key: string; label: string; href: string; note: string; hint: string }[];
  /** 完整记录的本机路径，原样一串：前缀文字和打开它的那颗键归页面，那里才知道摆在哪。 */
  log: string;
}

export function issueDetails(state: LibraryProcessingData): IssueDetails | null {
  const issues = state.issue_preview || [];
  if (!issues.length) return null;
  return {
    label: state.issues_truncated
      ? `问题清单：共 ${state.issue_count || 0} 项，展开查看前 ${issues.length} 项`
      : `问题清单：共 ${state.issue_count || 0} 项`,
    items: issues.map((issue, at) => ({
      key: `${issue.asset_id ?? 'source'}-${at}`,
      label: issue.title || (issue.asset_id ? `视频 ${issue.asset_id}` : '媒体来源'),
      href: issue.asset_id ? `/assets/${issue.asset_id}` : '',
      note: issue.message,
      hint: issue.path || '',
    })),
    log: state.issues_log || '',
  };
}

/* 完成用通知报一次。目录页的横幅和数据管理页的卡片看的是同一个任务，谁先看到结束谁报，
   另一处按任务号认出来就不再报。首次引导添加文件夹后那一趟常在跳到目录页之前就跑完
   （一个文件一秒），横幅从没见过「运行中」，所以刚结束的任务第一次读到时也报。 */
const ANNOUNCED_KEY = 'peach.library-processing.announced';
const FRESH_COMPLETION_SECONDS = 120;

export function announceCompletion(
  state: LibraryProcessingData, toast: (message: string) => void, witnessed: boolean,
): void {
  if (state.status !== 'complete') return;
  const fresh = !!state.job_id && !!state.completed_at
    && Date.now() / 1000 - state.completed_at < FRESH_COMPLETION_SECONDS;
  if (!witnessed && !fresh) return;
  try {
    if (state.job_id && localStorage.getItem(ANNOUNCED_KEY) === state.job_id) return;
    if (state.job_id) localStorage.setItem(ANNOUNCED_KEY, state.job_id);
  } catch { /* 存储不可用时照常提示，最多重复一次 */ }
  if (state.requested_stage === 'previews') {
    toast(`视频预览已生成：${state.previews || 0} 部`);
    return;
  }
  toast(`扫描与资料采集已完成：识别 ${state.identified || 0} 个番号，`
    + `整理 ${state.candidates || 0} 组资料候选，自动落库 ${state.auto_applied || 0} 条`
    + (state.previews ? `，生成 ${state.previews} 部视频预览` : ''));
}
