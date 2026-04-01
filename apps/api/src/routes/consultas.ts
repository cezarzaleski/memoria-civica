import { validateConsultCandidateRequest } from "@/contracts/consultation";
import type { ConsultationResponse } from "@/domain/models";

export interface ConsultPort {
  consult(input: {
    readonly candidate_name?: string;
    readonly office?: "deputado_federal" | "deputado_distrital";
    readonly party?: string;
    readonly uf?: string;
    readonly user_priorities?: readonly string[];
  }): Promise<{
    readonly execution: {
      readonly duration_ms: number;
      readonly started_at: string;
      readonly status: string;
      readonly steps: readonly string[];
      readonly trace_id: string;
    };
    readonly response: ConsultationResponse;
  }>;
}

export async function executeConsultationRoute(
  payload: unknown,
  orchestrator: ConsultPort
): Promise<ConsultationResponse> {
  const request = validateConsultCandidateRequest(
    (typeof payload === "object" && payload !== null ? payload : {}) as {
      readonly candidate_name?: string;
      readonly office?: "deputado_federal" | "deputado_distrital";
      readonly party?: string;
      readonly uf?: string;
      readonly user_priorities?: readonly string[];
    }
  );

  const result = await orchestrator.consult(request);
  return result.response;
}
