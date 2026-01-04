import { signup_and_login, get_url } from "./index";

import { test, expect } from "@playwright/test";

test.describe("Home Page", () => {
  test("Unauthenticated user gets redirected to login", async ({ page }) => {
    await page.goto("/");

    await page.waitForURL("/auth?mode=login");
    await expect(page).toHaveURL("/auth?mode=login");
  });

  test("User can add a new webpage", async ({ page }) => {
    await signup_and_login(page);

    await expect(page).toHaveURL("/");

    const test_url = get_url();

    const url_input = page.locator('input[placeholder="https://example.com/"]');
    await url_input.fill(test_url);

    const form_row = page.locator("tr").last();
    const interval_input = form_row.locator("td").nth(1).getByRole("textbox");
    await expect(interval_input).toHaveValue("minute");

    const submit_button = page.locator(
      'button[type="submit"][form="form_create_webpage"]'
    );
    const response_promise = page.waitForResponse(
      (response) =>
        response.url().includes("/api/webpage") &&
        response.request().method() === "POST"
    );
    await submit_button.click();
    await response_promise;

    const new_row = page.locator("tr").filter({ hasText: test_url }).first();
    await expect(new_row.locator("td").nth(2)).toHaveText("0");
  });

  test("User can delete a webpage", async ({ page }) => {
    await signup_and_login(page);

    const test_url = get_url();
    await page.fill('input[placeholder="https://example.com/"]', test_url);
    const submit_button = page.locator(
      'button[type="submit"][form="form_create_webpage"]'
    );
    const response_promise = page.waitForResponse(
      (response) =>
        response.url().includes("/api/webpage") &&
        response.request().method() === "POST"
    );
    await submit_button.click();
    const response = await response_promise;

    expect(response.status()).toBe(201);

    await expect(
      page.locator(`a[href="${test_url}"][target="_blank"]`)
    ).toBeVisible();

    const row = page.locator("tr").filter({ hasText: test_url }).first();
    const delete_button = row.locator("td").nth(3).getByRole("button");
    await delete_button.click();

    await expect(
      page.locator('text="Webpage removal confirmation"')
    ).toBeVisible();

    const confirm_delete_button = page.getByRole("button", {
      name: "Delete",
      exact: true,
    });
    await confirm_delete_button.click();

    const escaped_url = test_url.replace(/[.*+?^${}()|[\]\\\/]/g, "\\$&");
    await expect(
      page.locator(
        `text=/Webpage "${escaped_url}" has successfully been removed/`
      )
    ).toBeVisible();

    await expect(
      page.locator(`a[href="${test_url}"][target="_blank"]`)
    ).not.toBeVisible();
  });

  test("user can change monitoring interval", async ({ page }) => {
    await signup_and_login(page);

    const test_url = get_url();
    await page.fill('input[placeholder="https://example.com/"]', test_url);
    const submit_button = page.locator(
      'button[type="submit"][form="form_create_webpage"]'
    );
    const response_promise = page.waitForResponse(
      (response) =>
        response.url().includes("/api/webpage") &&
        response.request().method() === "POST"
    );
    await submit_button.click();
    const response = await response_promise;

    expect(response.status()).toBe(201);

    await expect(
      page.locator(`a[href="${test_url}"][target="_blank"]`)
    ).toBeVisible();

    const row = page.locator("tr").filter({ hasText: test_url }).first();
    const interval_select = row.locator("td").nth(1).getByRole("textbox");

    const escaped_url = test_url.replace(/[.*+?^${}()|[\]\\\/]/g, "\\$&");

    await interval_select.click();
    await page.getByRole("option", { name: "hour" }).click();

    await expect(
      page.locator(
        `text=/Webpage "${escaped_url}" is now being monitored every "hour"/`
      )
    ).toBeVisible();

    await interval_select.click();
    await page.getByRole("option", { name: "day" }).click();

    await expect(
      page.locator(
        `text=/Webpage "${escaped_url}" is now being monitored every "day"/`
      )
    ).toBeVisible();
  });

  test("user can view screenshots in carousel modal", async ({ page }) => {
    await signup_and_login(page);

    const test_url = get_url();
    await page.fill('input[placeholder="https://example.com/"]', test_url);
    const submit_button = page.locator(
      'button[type="submit"][form="form_create_webpage"]'
    );
    const response_promise = page.waitForResponse(
      (response) =>
        response.url().includes("/api/webpage") &&
        response.request().method() === "POST"
    );
    await submit_button.click();
    const response = await response_promise;

    expect(response.status()).toBe(201);

    const row = page.locator("tr").filter({ hasText: test_url }).first();

    await expect(row.locator("td").nth(2)).toHaveText("0");

    await expect(async () => {
      await page.reload();
      const updated_row = page
        .locator("tr")
        .filter({ hasText: test_url })
        .first();
      await expect(updated_row.locator("td").nth(2)).toHaveText("1");
    }).toPass({ timeout: 60000, intervals: [1000] }); // TODO update the test. Waiting a whole minute is stupid

    const updated_row = page
      .locator("tr")
      .filter({ hasText: test_url })
      .first();

    await updated_row.click();

    const escaped_url = test_url.replace(/[.*+?^${}()|[\]\\\/]/g, "\\$&");
    await expect(
      page.locator(`text=/Screenshots of.*${escaped_url}/`)
    ).toBeVisible();
  });
});
