import { test, expect } from "@playwright/test";
import { faker } from "@faker-js/faker";

test.describe("Authentication", () => {
  test("user can sign up", async ({ page }) => {
    page.on("console", (msg) => console.log(msg.text()));

    await page.goto("/auth");

    await expect(page.locator("button#button_submit")).toBeVisible();
    await expect(page.locator("button#button_toggle_mode")).toBeVisible();

    const username = faker.internet.username();
    const password = faker.internet.password({ length: 12 });
    await page.fill("#input_username", username);
    await page.fill("#input_password", password);
    await page.click("#button_submit");

    const cookies = await page.context().cookies();
    const session_cookie = cookies.find(
      (cookie) => cookie.name === "sessionid"
    );
    expect(session_cookie).toBeDefined();

    await expect(page).toHaveURL("/");
  });
});
