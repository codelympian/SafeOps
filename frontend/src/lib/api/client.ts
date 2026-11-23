import createClient, { type Middleware } from "openapi-fetch";

import type { components, paths } from "./schema";

export type Session = components["schemas"]["SessionOut"];
export type SystemInfo = components["schemas"]["SystemInfoOut"];

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const UNSAFE_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

/**
 * The CSRF token for the current session. It's kept in memory only, never in
 * localStorage, and is refreshed from every login/register/me response
 * (ADR-013). The session cookie itself is httpOnly and invisible to this code.
 */
let csrfToken: string | null = null;

export function setCsrfToken(token: string | null): void {
  csrfToken = token;
}

const csrfMiddleware: Middleware = {
  onRequest({ request }) {
    if (csrfToken && UNSAFE_METHODS.has(request.method)) {
      request.headers.set("X-CSRF-Token", csrfToken);
    }
    return request;
  },
};

/** Typed client generated from the backend's OpenAPI spec (`make api-types`). */
export const api = createClient<paths>({
  baseUrl: API_URL,
  credentials: "include", // send the httpOnly session cookie cross-origin (CORS allowlist)
});
api.use(csrfMiddleware);

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type ApiResult<T> = { data?: T; error?: unknown; response: Response };

/**
 * Return `data`, or throw an ApiError carrying the HTTP status and the API's message.
 * Taking the whole result object (instead of destructuring) keeps TypeScript from
 * narrowing `response` to `never` on endpoints that declare no error responses.
 */
export function unwrap<T>(result: ApiResult<T>, fallback?: string): T {
  if (result.data === undefined || result.error !== undefined) {
    throw new ApiError(result.response.status, errorMessage(result.error, fallback));
  }
  return result.data;
}

/** Turn a FastAPI error body (string or validation list) into one readable message. */
export function errorMessage(error: unknown, fallback = "Something went wrong"): string {
  if (error && typeof error === "object" && "detail" in error) {
    const detail = (error as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string; loc?: unknown[] };
      const field = Array.isArray(first.loc) ? first.loc.at(-1) : undefined;
      return field ? `${String(field)}: ${first.msg ?? "invalid"}` : (first.msg ?? fallback);
    }
  }
  return fallback;
}
