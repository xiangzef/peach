import { afterEach, expect, it, vi } from 'vitest';

afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); vi.resetModules() });

it('浏览器异常有上限、去重，网络失败不会触发递归上报', async () => {
  const listeners = new Map<string, (event: unknown) => void>();
  vi.spyOn(window, 'addEventListener').mockImplementation((name, callback) => {
    listeners.set(name, callback as (event: unknown) => void);
  });
  const fetch = vi.fn().mockRejectedValue(new Error('offline'));
  vi.stubGlobal('fetch', fetch);
  const { installErrorReporting } = await import('../src/error-reporting');
  installErrorReporting(); installErrorReporting();
  expect(listeners.size).toBe(2);
  const error = new Error('render failed');
  listeners.get('error')!({ error, message: error.message });
  listeners.get('error')!({ error, message: error.message });
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch.mock.calls[0]![0]).toBe('/api/diagnostics/client-error');
  expect(JSON.parse(fetch.mock.calls[0]![1].body)).toMatchObject({ kind: 'error', message: 'render failed' });
  for (let i = 0; i < 30; i += 1) listeners.get('unhandledrejection')!({ reason: `failure ${i}` });
  expect(fetch).toHaveBeenCalledTimes(10);
  await Promise.resolve();
  expect(fetch).toHaveBeenCalledTimes(10);
});
