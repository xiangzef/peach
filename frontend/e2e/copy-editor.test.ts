import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { after, before, describe, it } from 'node:test';
import type { Browser } from 'playwright-core';
import { launch, VIEWPORTS } from './harness.ts';

describe('原位改字', () => {
  let browser: Browser;
  before(async () => { browser = await launch(); });
  after(async () => { await browser?.close(); });
  for (const viewport of VIEWPORTS) {
    it(`回车、失焦保存与 Esc 取消（${viewport.name}）`, async () => {
      const context = await browser.newContext({ viewport });
      try {
        const page = await context.newPage();
        await page.route('https://copy.example/**', route => route.fulfill({
          contentType: 'text/html; charset=utf-8', body: '<meta charset="utf-8"><body data-peach-copy-mode="local"><main style="margin:80px 20px"><p id="copy" style="width:max-content">原位说明</p><button id="action">操作名称</button><div id="other" style="height:60px"></div></main></body>',
        }));
        await page.goto('https://copy.example/?edit');
        await page.addScriptTag({ content: await readFile(new URL('../../scripts/dev/copy-editor.js', import.meta.url), 'utf8') });
        await page.locator('#copy').click();
        const inline = page.locator('#copy [contenteditable]');
        await inline.waitFor();
        await inline.fill('新的说明');
        await inline.press('Escape');
        assert.equal(await page.locator('#copy').innerText(), '原位说明');
        assert.equal(await page.evaluate(() => localStorage.getItem('peach.copy-edits.v1')), null);
        await page.locator('#copy').click();
        await inline.fill('新的说明');
        await inline.press('Enter');
        assert.equal(await page.locator('#copy').innerText(), '新的说明');
        await page.locator('#copy').click();
        await inline.fill('点别处保存');
        await page.locator('#other').click();
        assert.equal(await page.locator('#copy').innerText(), '点别处保存');
        await page.locator('#action').click();
        const input = page.locator('input[data-copy-editor]');
        await input.waitFor();
        const a = await page.locator('#action').boundingBox(), b = await input.boundingBox();
        assert.ok(a && b && Math.abs(a.y - b.y) < 20, '按钮输入框位于文字处');
        await input.fill('修改按钮');
        await input.press('Enter');
        assert.equal(await page.locator('#action').innerText(), '修改按钮');
        await page.getByRole('button', { name: '暂停编辑', exact: true }).click();
        await page.locator('#copy').click();
        assert.equal(await page.locator('[contenteditable]').count(), 0);
        await page.getByRole('button', { name: '继续编辑', exact: true }).click();
        const edits = await page.evaluate(() => JSON.parse(localStorage.getItem('peach.copy-edits.v1')!));
        assert.equal(edits['原位说明'], '点别处保存');
      } finally { await context.close(); }
    });
  }
});
