import type {
  CacheScope,
  CacheTelemetryStatus,
  QueryExecutionRecord
} from "@/domain/models";

interface MutableExecutionState {
  readonly record: QueryExecutionRecord;
}

function createFingerprint(input: string): string {
  return Buffer.from(input).toString("base64url");
}

export function startQueryExecution(requestName: string): MutableExecutionState {
  const startedAt = new Date().toISOString();

  return {
    record: {
      duration_ms: 0,
      request_fingerprint: createFingerprint(requestName.toLowerCase()),
      started_at: startedAt,
      status: "completed",
      steps: [],
      trace_id: `consulta-${Date.now().toString(36)}`
    }
  };
}

export function appendExecutionStep(
  state: MutableExecutionState,
  step: string
): MutableExecutionState {
  return {
    record: {
      ...state.record,
      steps: [...state.record.steps, step]
    }
  };
}

export function recordExecutionCacheTelemetry(
  state: MutableExecutionState,
  scope: CacheScope,
  status: CacheTelemetryStatus
): MutableExecutionState {
  return {
    record: {
      ...state.record,
      observability: {
        ...state.record.observability,
        cache: {
          ...state.record.observability?.cache,
          [scope]: status
        }
      }
    }
  };
}

export function finishQueryExecution(
  state: MutableExecutionState,
  status: QueryExecutionRecord["status"] = "completed"
): QueryExecutionRecord {
  const finishedAt = new Date().toISOString();
  const durationMs =
    Date.parse(finishedAt) - Date.parse(state.record.started_at);

  return {
    ...state.record,
    duration_ms: Math.max(durationMs, 0),
    finished_at: finishedAt,
    status
  };
}
