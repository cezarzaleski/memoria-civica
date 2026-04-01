import {
  buildGrayResponse,
  validateConsultCandidateRequest
} from "@/contracts/consultation";
import type {
  ConsultationResponse,
  EvidenceRecord,
  QueryExecutionRecord,
  ResolvedCandidate
} from "@/domain/models";
import {
  appendExecutionStep,
  finishQueryExecution,
  startQueryExecution
} from "@/observability/query-execution";
import {
  InMemoryIdentityResolver,
  type IdentityResolver
} from "@/services/identity-resolver";
import {
  InMemoryEvidenceStore,
  type EvidenceStore
} from "@/services/evidence-store";
import { CachedEvidenceCollector } from "@/services/cached-evidence-collector";
import { CachedSignalService } from "@/services/cached-signal-service";
import { EvidenceClassifier } from "@/services/evidence-classifier";
import { CollectionPlanner } from "@/services/collection-planner";
import { ResponseAssembler } from "@/services/response-assembler";
import { SignalEngine } from "@/services/signal-engine";
import {
  McpBrasilEvidenceCollector,
  type OfficialEvidenceCollector,
  McpBrasilIdentitySource,
  StdioMcpBrasilClient
} from "@/source-connectors/mcp-brasil";

interface QueryOrchestratorOptions {
  readonly collectionPlanner?: CollectionPlanner;
  readonly evidenceCollector?: OfficialEvidenceCollector;
  readonly evidenceStore?: EvidenceStore;
  readonly identityResolver?: IdentityResolver;
}

interface ConsultationResult {
  readonly execution: QueryExecutionRecord;
  readonly response: ConsultationResponse;
}

const NO_EVIDENCE_ALERT = "Nenhuma evidencia oficial foi coletada para a consulta.";
const PARTIAL_EVIDENCE_ALERT =
  "Coleta oficial ainda insuficiente para conclusao final.";
const COHERENCE_LIMITATION_ALERT =
  "Coherence usa atuacao formal, proposicoes autorais e votos nominais recentes da Camara; relatoria ainda nao foi integrada e votos nominais seguem parciais.";
const COHERENCE_COVERAGE_ALERT_PREFIX =
  "Cobertura atual de coherence na Camara";

function buildPlaceholderCandidate(name: string): ResolvedCandidate {
  return {
    ambiguity_level: "strong",
    canonical_name: name,
    office: "deputado_federal",
    official_ids: {},
    status: "challenger"
  };
}

export class QueryOrchestrator {
  private readonly collectionPlanner: CollectionPlanner;

  private readonly evidenceCollector: OfficialEvidenceCollector;

  private readonly evidenceStore: EvidenceStore;

  private readonly evidenceClassifier: EvidenceClassifier;

  private readonly identityResolver: IdentityResolver;

  private readonly responseAssembler: ResponseAssembler;

  private readonly signalEngine: SignalEngine;

  private readonly signalService: CachedSignalService;

  public constructor(options: QueryOrchestratorOptions = {}) {
    this.collectionPlanner = options.collectionPlanner ?? new CollectionPlanner();
    const client = new StdioMcpBrasilClient({
      cwd: process.cwd()
    });
    this.evidenceCollector =
      options.evidenceCollector ??
      new CachedEvidenceCollector(new McpBrasilEvidenceCollector(client));
    this.evidenceStore = options.evidenceStore ?? new InMemoryEvidenceStore();
    this.evidenceClassifier = new EvidenceClassifier();
    this.identityResolver =
      options.identityResolver ??
      new InMemoryIdentityResolver({
        sources: [
          new McpBrasilIdentitySource(
            client
          )
        ]
    });
    this.responseAssembler = new ResponseAssembler();
    this.signalEngine = new SignalEngine();
    this.signalService = new CachedSignalService(this.signalEngine);
  }

  private buildCollectedGrayResponse(
    candidate: ResolvedCandidate,
    evidence: readonly EvidenceRecord[]
  ): ConsultationResponse {
    const classifications = this.evidenceClassifier.classify(evidence);
    const signalResult = this.signalService.compute(
      candidate,
      evidence,
      classifications
    );
    const evidenceLevel = signalResult.evidence_level;
    const coherence = signalResult.coherence;
    const coherenceCoverage = signalResult.coherenceCoverage;
    const integrity = signalResult.integrity;
    const alerts = [evidence.length > 0 ? PARTIAL_EVIDENCE_ALERT : NO_EVIDENCE_ALERT];

    if (
      candidate.office === "deputado_federal" &&
      candidate.status === "incumbent" &&
      evidence.some((record) => {
        return record.signal_type === "coherence";
      })
    ) {
      alerts.push(COHERENCE_LIMITATION_ALERT);
      alerts.push(
        `${COHERENCE_COVERAGE_ALERT_PREFIX}: coletados=${
          coherenceCoverage.collected_types.join(", ") || "nenhum"
        }; faltam=${coherenceCoverage.missing_types.join(", ") || "nenhum"}.`
      );
    }

    const base = buildGrayResponse({
      alerts,
      candidate,
      reasons:
        evidence.length > 0
          ? [`Foram coletadas ${evidence.length} evidencias oficiais iniciais.`]
          : ["Nao foi possivel coletar evidencias oficiais para sustentar uma conclusao."],
      summary:
        evidence.length > 0
          ? "A consulta coletou evidencias oficiais iniciais, mas ainda nao fecha uma leitura final."
          : "A consulta resolveu a identidade, mas nao encontrou evidencias oficiais suficientes."
    });

    return {
      ...this.responseAssembler.assemble({
        alerts: base.alerts,
        candidate,
        identity_metadata: {
          match_count: 1,
          resolution_kind: "resolved"
        },
        signals: {
        ...base.signals,
        coherence,
        integrity,
        evidence_level: evidenceLevel
      },
        sources: [...new Set(evidence.map((item) => item.source_url))]
      }),
      signals: {
        ...base.signals,
        coherence,
        integrity,
        evidence_level: evidenceLevel
      }
    };
  }

  public async consult(input: {
    readonly candidate_name?: string;
    readonly office?: "deputado_federal" | "deputado_distrital";
    readonly party?: string;
    readonly uf?: string;
    readonly user_priorities?: readonly string[];
  }): Promise<ConsultationResult> {
    const request = validateConsultCandidateRequest(input);
    let execution = startQueryExecution(request.candidate_name);
    execution = appendExecutionStep(execution, "request_validated");

    const identity = await this.identityResolver.resolve({
      name: request.candidate_name,
      office: request.office,
      party: request.party,
      uf: request.uf
    });

    if (identity.kind === "resolved") {
      execution = appendExecutionStep(execution, "identity_resolved");
      const plan = this.collectionPlanner.plan({
        candidate: identity.candidate,
        requested_signals: ["evidence_level", "integrity", "coherence", "values_fit"],
        user_priorities: request.user_priorities
      });
      execution = appendExecutionStep(execution, "collection_planned");

      const rawEvidence = await this.evidenceCollector.collect(
        identity.candidate,
        plan
      );
      execution = appendExecutionStep(execution, "evidence_collected");
      const evidence = await this.evidenceStore.save(rawEvidence);
      execution = appendExecutionStep(execution, "evidence_stored");
      execution = appendExecutionStep(execution, "evidence_classified");
      execution = appendExecutionStep(execution, "signals_computed");

      const response = this.buildCollectedGrayResponse(identity.candidate, evidence);

      execution = appendExecutionStep(execution, "response_assembled");

      return {
        execution: finishQueryExecution(execution),
        response
      };
    }

    const alerts =
      identity.kind === "ambiguous"
        ? [
            `Identidade ambigua. Informe ${identity.requires.join(" e ")} para continuar.`
          ]
        : ["Nenhuma identidade oficial foi encontrada para a consulta informada."];

    execution = appendExecutionStep(
      execution,
      identity.kind === "ambiguous" ? "identity_ambiguous" : "identity_not_found"
    );

    const response = buildGrayResponse({
      alerts,
      candidate: buildPlaceholderCandidate(request.candidate_name),
      identity_metadata: {
        match_count: identity.match_count,
        requires: identity.kind === "ambiguous" ? identity.requires : undefined,
        resolution_kind: identity.kind
      },
      reasons:
        identity.kind === "ambiguous"
          ? ["A consulta precisa de mais contexto para desambiguar o nome informado."]
          : ["Nao foi possivel resolver a identidade do candidato com seguranca."],
      summary:
        identity.kind === "ambiguous"
          ? "A consulta parou na etapa de identidade por ambiguidade forte."
          : "A consulta parou porque nenhuma identidade oficial foi localizada."
    });

    execution = appendExecutionStep(execution, "response_assembled");

    return {
      execution: finishQueryExecution(execution),
      response
    };
  }
}
