import type { paths } from "../schema/schema";
import { ApiError } from "./ApiError";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:5002";

type Method = "get" | "post";
type Path = keyof paths;
type Operation<P extends Path, M extends Method> = NonNullable<paths[P][M]>;

type Json<R> = R extends { content: { "application/json": infer T } } ? T : never;
type Success<O> = O extends { responses: infer R }
  ? { [S in keyof R]: S extends 200 | 201 ? Json<R[S]> : never }[keyof R]
  : never;

type PathInput<O> = O extends { parameters: { path: infer P } } ? { path: P } : unknown;
type BodyInput<O> = O extends { requestBody: { content: { "application/json": infer B } } }
  ? { body: B }
  : unknown;
type Input<O> = PathInput<O> & BodyInput<O>;

function toUrl(path: string, params: Record<string, string> | undefined): string {
  const filled = path.replace(/\{(\w+)\}/g, (_, name: string) =>
    encodeURIComponent(params?.[name] ?? ""),
  );
  return `${API_URL}${filled}`;
}

async function errorCode(response: Response): Promise<string> {
  const payload: unknown = await response.json().catch(() => null);
  if (typeof payload === "object" && payload !== null && "detail" in payload) {
    return typeof payload.detail === "string" ? payload.detail : "VALIDATION_ERROR";
  }
  return "UNKNOWN_ERROR";
}

export async function request<P extends Path, M extends Method>(
  method: M,
  path: P,
  input: Input<Operation<P, M>>,
): Promise<Success<Operation<P, M>>> {
  const { path: params, body } = input as { path?: Record<string, string>; body?: unknown };
  const response = await fetch(toUrl(path, params), {
    method: method.toUpperCase(),
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? null : JSON.stringify(body),
  });
  if (!response.ok) {
    throw new ApiError(response.status, await errorCode(response));
  }
  return (await response.json()) as Success<Operation<P, M>>;
}
