import assert from 'node:assert/strict';
import { after, before, describe, it } from 'node:test';
import type { Browser } from 'playwright-core';
import { launch, layout, settle, visit, VIEWPORTS } from './harness.ts';

describe('口味浏览器来源', () => {
  let browser: Browser;
  before(async () => { browser = await launch(); });
  after(async () => { await browser?.close(); });
  for (const viewport of VIEWPORTS) it(`${viewport.name}：添加、停止和恢复读取保留已导入记录`, { timeout: 60_000 }, async () => {
    const opened = await visit(browser, '/taste', viewport);
    const { page } = opened;
    const browsers = [{ id: 'aside', name: 'Aside', path: 'C:/Demo/Aside/User Data', enabled: true, available: true, profiles: 1 }];
    const data = () => ({ summary: { history_visits: 25 }, rankings: {}, sources: [], browsers: [...browsers] });
    const requests: string[] = [];
    try {
      await page.route('**/api/taste?*', route => route.fulfill({ json: data() }));
      await page.route('**/api/taste/refresh', route => route.fulfill({ json: { status: 'idle' } }));
      await page.route('**/api/taste/source', async route => {
        const body = route.request().postDataJSON(); requests.push(body.operation);
        if (body.operation === 'add') browsers.push({ ...browsers[0], id: 'custom', name: body.name, path: body.path });
        else browsers.find(row => row.id === body.id)!.enabled = body.operation === 'enable';
        await route.fulfill({ json: { dashboard: data() } });
      });
      await page.reload(); await settle(page);
      const sources = page.getByRole('region', { name: '浏览器同步', exact: true });
      await sources.getByRole('button', { name: '添加浏览器', exact: true }).click();
      await sources.getByRole('textbox', { name: '浏览器名称', exact: true }).fill('演示浏览器');
      await sources.getByRole('textbox', { name: '资料目录或历史文件', exact: true }).fill('C:/Demo/Custom/User Data');
      await sources.getByRole('button', { name: '添加', exact: true }).click();
      await sources.getByText('演示浏览器', { exact: true }).waitFor();
      await sources.getByRole('button', { name: '移除 Aside', exact: true }).click();
      const dialog = page.getByRole('dialog', { name: '停止读取 Aside', exact: true });
      await dialog.getByRole('button', { name: '停止读取', exact: true }).click();
      await sources.getByText('已停止读取', { exact: true }).waitFor();
      await sources.getByRole('button', { name: '启用 Aside', exact: true }).click();
      await sources.getByRole('button', { name: '移除 Aside', exact: true }).waitFor();
      assert.deepEqual(requests, ['add', 'disable', 'enable']);
      const geometry = await layout(page);
      assert.ok(geometry.scrollWidth <= geometry.viewportWidth, JSON.stringify(geometry));
      await page.screenshot({ path: `../build/taste-browsers-${viewport.name}.png` });
      assert.deepEqual(opened.problems, []);
    } finally { await opened.page.context().close(); }
  });
});
