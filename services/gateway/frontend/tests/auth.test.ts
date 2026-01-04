import { test, expect } from "@playwright/test";
import { get_username, get_password } from "./index";

test.describe("Auth Page", () => {
  test("User can sign up", async ({ page }) => {
    await page.goto("/auth");

    await expect(page.locator("button#button_submit")).toBeVisible();
    await expect(page.locator("button#button_toggle_mode")).toBeVisible();

    const username = get_username();
    const password = get_password();
    await page.fill("#input_username", username);
    await page.fill("#input_password", password);
    await page.click("#button_submit");

    await page.waitForURL("/");

    await expect(page).toHaveURL("/");

    const cookies = await page.context().cookies();
    const session_cookie = cookies.find(
      (cookie) => cookie.name === "sessionid"
    );
    expect(session_cookie).toBeDefined();
  });

  test("User can login with valid credentials", async ({ page }) => {
    const username = get_username();
    const password = get_password();

    await page.goto("/auth");
    await page.fill("#input_username", username);
    await page.fill("#input_password", password);
    await page.click("#button_submit");
    await page.waitForURL("/");

    await page.context().clearCookies();

    await page.goto("/auth?mode=login");
    await expect(page.locator("button#button_submit")).toHaveText("Log In");

    await page.fill("#input_username", username);
    await page.fill("#input_password", password);
    await page.click("#button_submit");

    await page.waitForURL("/");
    await expect(page).toHaveURL("/");

    const cookies = await page.context().cookies();
    const session_cookie = cookies.find(
      (cookie) => cookie.name === "sessionid"
    );
    expect(session_cookie).toBeDefined();
  });

  test("User can toggle between login/signup modes", async ({ page }) => {
    await page.goto("/auth");

    await expect(page.locator("button#button_submit")).toHaveText("Sign Up");
    await expect(page.locator("button#button_toggle_mode")).toHaveText(
      "Log In"
    );
    await expect(page).toHaveURL("/auth?mode=signup");

    await page.click("#button_toggle_mode");

    await expect(page.locator("button#button_submit")).toHaveText("Log In");
    await expect(page.locator("button#button_toggle_mode")).toHaveText(
      "Sign Up"
    );
    await expect(page).toHaveURL("/auth?mode=login");

    await page.click("#button_toggle_mode");

    await expect(page.locator("button#button_submit")).toHaveText("Sign Up");
    await expect(page.locator("button#button_toggle_mode")).toHaveText(
      "Log In"
    );
    await expect(page).toHaveURL("/auth?mode=signup");
  });

  test("Already logged-in user gets redirected to home", async ({ page }) => {
    const username = get_username();
    const password = get_password();

    await page.goto("/auth");
    await page.fill("#input_username", username);
    await page.fill("#input_password", password);
    await page.click("#button_submit");
    await page.waitForURL("/");

    await page.goto("/auth");

    await page.waitForURL("/");
    await expect(page).toHaveURL("/");
  });

  test("Login with invalid credentials shows error and clears password", async ({ page }) => {
    await page.goto("/auth?mode=login");

    await expect(page.locator("button#button_submit")).toBeVisible();
    await expect(page.locator("button#button_submit")).toHaveText("Log In");

    await page.fill("#input_username", "nonexistent");
    await page.fill("#input_password", "wrongpassword123");
    await page.click("#button_submit");
    await page.waitForResponse((response) =>
      response.url().includes("/api/login")
    );

    await expect(page.locator("form")).toContainText(
      "Invalid credentials, failed to login. Try again."
    );
    await expect(page.locator("#input_password")).toHaveValue("");
  });

  test("Signup with duplicate username shows error and clears password", async ({ page }) => {
    const username = get_username();
    const password = get_password();

    await page.goto("/auth");
    await page.fill("#input_username", username);
    await page.fill("#input_password", password);
    await page.click("#button_submit");
    await page.waitForURL("/");

    await page.context().clearCookies();

    await page.goto("/auth");
    await page.fill("#input_username", username);
    await page.fill("#input_password", password);
    await page.click("#button_submit");
    await page.waitForResponse((response) =>
      response.url().includes("/api/signup")
    );

    await expect(page.locator("form")).toContainText(
      "A user with that username already exists. Login instead."
    );
    await expect(page.locator("#input_password")).toHaveValue("");
  });

  test("Username too short shows validation error", async ({ page }) => {
    await page.goto("/auth");
    await page.fill("#input_username", "short");
    await page.fill("#input_password", "validpassword123");
    await page.click("#button_submit");

    await expect(page.locator("form")).toContainText(
      "Username must be at least 6 characters"
    );
  });

  test("Username too long shows validation error", async ({ page }) => {
    await page.goto("/auth");
    await page.fill("#input_username", "thisusernameiswaytoolong");
    await page.fill("#input_password", "validpassword123");
    await page.click("#button_submit");

    await expect(page.locator("form")).toContainText(
      "Username must be at most 18 characters"
    );
  });

  test("Username with invalid characters shows validation error", async ({ page }) => {
    await page.goto("/auth");
    await page.fill("#input_username", "user!@#$%");
    await page.fill("#input_password", "validpassword123");
    await page.click("#button_submit");

    await expect(page.locator("form")).toContainText(
      "Username may contain only letters, numbers, and @/./+/-/_ characters"
    );
  });

  test("Password too short shows validation error", async ({ page }) => {
    await page.goto("/auth");
    await page.fill("#input_username", "validusername");
    await page.fill("#input_password", "short");
    await page.click("#button_submit");

    await expect(page.locator("form")).toContainText(
      "Password must be at least 8 characters"
    );
  });

  test("Password too long shows validation error", async ({ page }) => {
    await page.goto("/auth");
    await page.fill("#input_username", "validusername");
    await page.fill("#input_password", "a".repeat(65));
    await page.click("#button_submit");

    await expect(page.locator("form")).toContainText(
      "Password must be at most 64 characters"
    );
  });

  test("Empty form submission shows both validation errors", async ({ page }) => {
    await page.goto("/auth");
    await expect(page.locator("button#button_submit")).toBeVisible();
    await page.click("#button_submit");

    await expect(page.locator("form")).toContainText(
      "Username may contain only letters, numbers, and @/./+/-/_ characters"
    );
    await expect(page.locator("form")).toContainText(
      "Password must be at least 8 characters"
    );
  });
});
