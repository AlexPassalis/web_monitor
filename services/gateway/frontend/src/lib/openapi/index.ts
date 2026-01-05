import type { paths } from "@/lib/openapi/schema"

import createClient from "openapi-fetch"

const hostname =
  window.location.hostname === "localhost" ? "localhost" : "alexpassalis.com"

export const fetch = createClient<paths>({
  baseUrl: `https://${hostname}`,
  credentials: "include",
})

export type Fetch = typeof fetch;
