import { createApiClient } from "@hrs/api-client";

/** 利用者アプリが叩くHRS API。 */
export const api = createApiClient(
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080",
);
