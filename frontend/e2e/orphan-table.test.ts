import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import { after, before, describe, it } from 'node:test';
import type { Browser } from 'playwright-core';
import { launch, layout, settle, VIEWPORTS, visit } from './harness.ts';

describe('孤儿记录数据表', () => {
  let browser: Browser;
  before(async () => { browser = await launch(); await mkdir('../build/table-evidence', { recursive: true }); });
  after(async () => { await browser.close(); });
  for (const viewport of VIEWPORTS) it(`${viewport.name}：面板内标题、共用分页与选中后的批量操作`, async () => {
    const opened = await visit(browser, '/data-cleanup', viewport);
    const { page } = opened;
    try {
      const items = Array.from({ length: 23 }, (_, index) => ({
        id: index + 1, name: `作品 ${23 - index}・很长的作品名称用于复核截断和操作区域`,
        code: '', location: 'pikpak', duration: 600, size: 10, vanished_at: 100,
        has_thumb: false, records: { watch_queue: 1, last_played: 1 }, candidates: [],
      }));
      await page.route('**/api/orphan-records', (route) => route.fulfill({
        status: 200, contentType: 'application/json', body: JSON.stringify({ total: items.length, items }),
      }));
      const writes: unknown[] = [];
      await page.route('**/api/batch', async (route) => {
        writes.push(route.request().postDataJSON());
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true, purged: 2, blocked: [] }) });
      });
      await page.reload({ waitUntil: 'load' });
      const section = page.locator('#orphan-records');
      const table = page.getByRole('grid', { name: '文件已消失的作品', exact: true });
      await table.waitFor();
      await settle(page);
      assert.equal(await section.locator('[data-data-table-panel] #orphan-records-title').count(), 1);
      assert.equal(await table.locator('tbody tr').count(), 20);
      assert.equal(await section.getByRole('button', { name: '彻底删除所选（0）', exact: true }).count(), 0);
      const pagination = section.locator('[data-table-pagination]');
      assert.ok((await pagination.textContent())?.includes('1–20 / 23 条作品'));
      await pagination.getByRole('button', { name: /每页显示数量/ }).waitFor();
      await section.getByRole('button', { name: /文件已消失的作品排序/ }).waitFor();
      await page.setViewportSize({ width: viewport.width, height: 2400 });
      await section.evaluate((element) => window.scrollTo(0, element.getBoundingClientRect().top + window.scrollY - 100));
      await section.screenshot({ path: `../build/table-evidence/orphan-${viewport.name}.png` });
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await table.locator('tbody tr').first().locator('label:has(input[type="checkbox"])').click();
      await section.locator('[data-selection-dock]').waitFor();
      await section.getByRole('button', { name: '下一页', exact: true }).click();
      await table.locator('tbody tr').first().locator('label:has(input[type="checkbox"])').click();
      await table.getByRole('columnheader', { name: '作品', exact: true }).click();
      assert.ok((await table.locator('tbody tr').first().textContent())?.includes('作品 1・'));
      await pagination.scrollIntoViewIfNeeded();
      await page.screenshot({ path: `../build/table-evidence/orphan-selected-${viewport.name}.png` });
      await section.getByRole('button', { name: '彻底删除所选（2）', exact: true }).click();
      await page.getByRole('dialog').getByRole('button', { name: '取消', exact: true }).click();
      assert.deepEqual(writes, []);
      const geometry = await layout(page);
      assert.ok(geometry.scrollWidth <= geometry.viewportWidth + 1, JSON.stringify(geometry));
      assert.deepEqual(geometry.offenders, []);
      assert.deepEqual(opened.problems, []);
    } finally { await opened.close(); }
  });
});
