import type { Page } from "@playwright/test";

import { faker } from "@faker-js/faker";

export function get_username(): string {
  let username = "";
  while (username.length < 6 || username.length > 18) {
    username = faker.internet
      .username()
      .toLowerCase()
      .replace(/[^a-z0-9_.@+-]/g, "");
  }
  return username;
}

export function get_password(): string {
  return (
    faker.string.alphanumeric(12) +
    faker.number.int({ min: 10, max: 99 }).toString()
  );
}

export function get_url(): string {
  const unique_id = `${Date.now()}-${faker.string.alphanumeric(8)}`;
  return `https://google.com/?test=${unique_id}`;
}

export async function signup_and_login(page: Page) {
  const username = get_username();
  const password = get_password();

  await page.goto("/auth");
  await page.fill("#input_username", username);
  await page.fill("#input_password", password);
  await page.click("#button_submit");
  await page.waitForURL("/");

  // Wait for CSRF token to be fetched on home page
  await page.waitForResponse((response) =>
    response.url().includes("/api/csrf")
  );

  return { username, password };
}
