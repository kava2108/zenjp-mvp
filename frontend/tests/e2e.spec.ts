import { test, expect } from '@playwright/test';

const baseUrl = process.env.E2E_BASE_URL || 'http://localhost:3000';

test.describe('ZenJP MVP E2E Tests', () => {
  test('ページが正常に読み込まれる', async ({ page }) => {
    await page.goto(baseUrl);
    await expect(page).toHaveTitle(/ZenJP/);
  });

  test('3銘柄のスコアカードが表示される', async ({ page }) => {
    await page.goto(baseUrl);
    const cards = page.locator('[data-testid="score-card"]');
    await expect(cards).toHaveCount(3, { timeout: 15000 });
  });
});