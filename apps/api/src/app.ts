import { createServer, type IncomingMessage, type Server, type ServerResponse } from "node:http";

import { QueryOrchestrator } from "@/services/query-orchestrator";
import { executeConsultationRoute, type ConsultPort } from "./routes/consultas";
import { buildHealthPayload } from "./routes/health";

interface CreateApiServerOptions {
  readonly orchestrator?: ConsultPort;
}

interface ApiRouteInput {
  readonly method?: string;
  readonly payload?: unknown;
  readonly pathname: string;
}

interface ApiRouteOutput {
  readonly payload: unknown;
  readonly statusCode: number;
}

function writeJson(
  response: ServerResponse,
  statusCode: number,
  payload: unknown
): void {
  response.statusCode = statusCode;
  response.setHeader("content-type", "application/json; charset=utf-8");
  response.end(JSON.stringify(payload));
}

async function readJsonBody(request: IncomingMessage): Promise<unknown> {
  const chunks: string[] = [];

  for await (const chunk of request as AsyncIterable<Buffer | string>) {
    if (typeof chunk === "string") {
      chunks.push(chunk);
      continue;
    }

    chunks.push(chunk.toString("utf8"));
  }

  if (chunks.length === 0) {
    return {};
  }

  try {
    return JSON.parse(chunks.join(""));
  } catch {
    throw new Error("invalid_json");
  }
}

function isValidationError(error: unknown): error is Error {
  if (!(error instanceof Error)) {
    return false;
  }

  return (
    error.message === "candidate_name is required" ||
    error.message === "deputado_distrital requires uf=DF"
  );
}

export async function routeApiRequest(
  input: ApiRouteInput,
  orchestrator: ConsultPort
): Promise<ApiRouteOutput> {
  if (input.method === "GET" && input.pathname === "/health") {
    return {
      payload: buildHealthPayload(),
      statusCode: 200
    };
  }

  if (input.method === "POST" && input.pathname === "/consultas") {
    try {
      const consultation = await executeConsultationRoute(
        input.payload,
        orchestrator
      );

      return {
        payload: consultation,
        statusCode: 200
      };
    } catch (error) {
      if (error instanceof Error && error.message === "invalid_json") {
        return {
          payload: {
            error: {
              code: "INVALID_JSON",
              message: "Request body must be valid JSON."
            }
          }
          ,
          statusCode: 400
        };
      }

      if (isValidationError(error)) {
        return {
          payload: {
            error: {
              code: "VALIDATION_ERROR",
              message: error.message
            }
          }
          ,
          statusCode: 400
        };
      }

      return {
        payload: {
          error: {
            code: "INTERNAL_ERROR",
            message: "Falha interna ao processar consulta."
          }
        }
        ,
        statusCode: 500
      };
    }
  }

  return {
    payload: {
      error: {
        code: "NOT_FOUND",
        message: "Rota nao encontrada."
      }
    }
    ,
    statusCode: 404
  };
}

async function handleRequest(
  request: IncomingMessage,
  response: ServerResponse,
  orchestrator: ConsultPort
): Promise<void> {
  const url = new URL(request.url ?? "/", "http://localhost");
  const payload =
    request.method === "POST" ? await readJsonBody(request) : undefined;
  const result = await routeApiRequest(
    {
      method: request.method,
      pathname: url.pathname,
      payload
    },
    orchestrator
  );

  writeJson(response, result.statusCode, result.payload);
}

export function createApiServer(
  options: CreateApiServerOptions = {}
): Server {
  const orchestrator = options.orchestrator ?? new QueryOrchestrator();

  return createServer((request, response) => {
    void handleRequest(request, response, orchestrator);
  });
}
