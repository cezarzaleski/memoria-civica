import {
  buildGrayResponse,
  validateConsultCandidateRequest
} from "@/contracts/consultation";
import type {
  ConsultationObservability,
  ConsultationResponse,
  EvidenceRecord,
  QueryExecutionRecord,
  ResolvedCandidate,
  ReviewQueueEntry
} from "@/domain/models";
import {
  appendExecutionReviewQueueEntry,
  appendExecutionStep,
  finishQueryExecution,
  recordExecutionCacheTelemetry,
  startQueryExecution
} from "@/observability/query-execution";
import {
  ObservedCacheStore,
  type CacheStore,
  InMemoryCacheStore
} from "@/services/cache-store";
import {
  type CacheTtlPolicy,
  DEFAULT_CACHE_TTL_POLICY
} from "@/services/cache-policy";
import {
  InMemoryIdentityResolver,
  type IdentityResolver
} from "@/services/identity-resolver";
import { InMemoryEvidenceStore, type EvidenceStore } from "@/services/evidence-store";
import { CachedEvidenceCollector } from "@/services/cached-evidence-collector";
import { CachedSignalService } from "@/services/cached-signal-service";
import { EvidenceClassifier } from "@/services/evidence-classifier";
import { CollectionPlanner } from "@/services/collection-planner";
import { ResponseAssembler } from "@/services/response-assembler";
import {
  EXPECTED_CAMARA_COHERENCE_EVIDENCE_TYPES,
  SignalEngine
} from "@/services/signal-engine";
import {
  McpBrasilEvidenceCollector,
  type OfficialEvidenceCollector,
  type OfficialIdentitySource,
  McpBrasilIdentitySource,
  StdioMcpBrasilClient
} from "@/source-connectors/mcp-brasil";

interface QueryOrchestratorOptions {
  readonly cachePolicy?: CacheTtlPolicy;
  readonly cacheStore?: CacheStore;
  readonly collectionPlanner?: CollectionPlanner;
  readonly evidenceCollector?: OfficialEvidenceCollector;
  readonly evidenceStore?: EvidenceStore;
  readonly identityCatalog?: readonly ResolvedCandidate[];
  readonly identityResolver?: IdentityResolver;
  readonly identitySources?: readonly OfficialIdentitySource[];
  readonly mcpBrasilClient?: StdioMcpBrasilClient;
  readonly rawEvidenceCollector?: OfficialEvidenceCollector;
  readonly signalEngine?: SignalEngine;
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
const INTEGRITY_SENSITIVE_TERMS = [
  "sancao",
  "processo",
  "controversia",
  "representacao"
] as const;
const JOURNALISM_MARKERS = [
  "jornal",
  "noticia",
  "noticias",
  "news",
  "reportagem",
  "midia",
  "media"
] as const;

function normalizeForMatch(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();
}

function formatIdentityRequirement(requirement: "uf" | "party"): string {
  return requirement === "uf" ? "UF" : "o partido";
}

function formatIdentityDisambiguationMessage(
  requires: readonly ("uf" | "party")[]
): string {
  if (requires.length === 0) {
    return "Faltou contexto para identificar a pessoa certa.";
  }

  const formattedRequirements = requires.map(formatIdentityRequirement);

  if (formattedRequirements.length === 1) {
    return `Faltou contexto para identificar a pessoa certa. Informe ${formattedRequirements[0]} para continuar.`;
  }

  if (formattedRequirements.length === 2) {
    return `Faltou contexto para identificar a pessoa certa. Informe ${formattedRequirements[0]} e ${formattedRequirements[1]} para continuar.`;
  }

  return `Faltou contexto para identificar a pessoa certa. Informe ${formattedRequirements.join(", ")} para continuar.`;
}

function isSensitiveIntegrityEvidence(record: EvidenceRecord): boolean {
  if (record.signal_type !== "integrity") {
    return false;
  }

  if (record.evidence_type === "integrity_alert") {
    return true;
  }

  const haystack = normalizeForMatch(
    `${record.evidence_type} ${record.summary}`
  );

  return INTEGRITY_SENSITIVE_TERMS.some((term) => {
    return haystack.includes(term);
  });
}

function usesComplementaryJournalism(record: EvidenceRecord): boolean {
  const haystack = normalizeForMatch(
    `${record.evidence_type} ${record.source_name} ${record.source_url}`
  );

  return (
    record.strength === "complementary" &&
    (record.signal_type === "integrity" || record.signal_type === "values_fit") &&
    JOURNALISM_MARKERS.some((marker) => {
      return haystack.includes(marker);
    })
  );
}

function buildResolvedReviewQueueEntries(
  evidence: readonly EvidenceRecord[]
): readonly ReviewQueueEntry[] {
  const entries: ReviewQueueEntry[] = [];
  const sensitiveIntegrityEvidence = evidence.filter(isSensitiveIntegrityEvidence);

  if (sensitiveIntegrityEvidence.length > 0) {
    entries.push({
      evidence_ids: sensitiveIntegrityEvidence.map((record) => record.evidence_id),
      message:
        "Consulta marcada para revisao por caso sensivel de integridade detectado nas evidencias coletadas.",
      reason: "integrity_sensitive_case"
    });
  }

  const complementaryEvidence = evidence.filter(usesComplementaryJournalism);

  if (complementaryEvidence.length > 0) {
    entries.push({
      evidence_ids: complementaryEvidence.map((record) => record.evidence_id),
      message:
        "Consulta marcada para revisao editorial por uso de evidencia complementar como apoio de sinal.",
      reason: "complementary_journalism"
    });
  }

  return entries;
}

function buildCoherenceObservability(input: {
  readonly candidate: ResolvedCandidate;
  readonly coherence: ReturnType<CachedSignalService["compute"]>["coherence"];
  readonly coherenceCoverage: ReturnType<CachedSignalService["compute"]>["coherenceCoverage"];
}): ConsultationObservability | undefined {
  if (
    input.candidate.office !== "deputado_federal" ||
    input.candidate.status !== "incumbent"
  ) {
    return undefined;
  }

  return {
    coherence: {
      collected_evidence_ids: input.coherence.evidence_ids,
      collected_types: input.coherenceCoverage.collected_types,
      expected_types: [...EXPECTED_CAMARA_COHERENCE_EVIDENCE_TYPES],
      limitation: COHERENCE_LIMITATION_ALERT,
      missing_types: input.coherenceCoverage.missing_types,
      scope: "camara",
      status_basis: input.coherence.status
    }
  };
}

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
  private readonly cachePolicy: CacheTtlPolicy;

  private readonly cacheStore: CacheStore;

  private readonly client: StdioMcpBrasilClient;

  private readonly collectionPlanner: CollectionPlanner;

  private readonly evidenceCollector?: OfficialEvidenceCollector;

  private readonly evidenceStore: EvidenceStore;

  private readonly evidenceClassifier: EvidenceClassifier;

  private readonly identityResolver?: IdentityResolver;

  private readonly identityCatalog: readonly ResolvedCandidate[];

  private readonly identitySources?: readonly OfficialIdentitySource[];

  private readonly rawEvidenceCollector?: OfficialEvidenceCollector;

  private readonly responseAssembler: ResponseAssembler;

  private readonly signalEngine: SignalEngine;

  public constructor(options: QueryOrchestratorOptions = {}) {
    this.collectionPlanner = options.collectionPlanner ?? new CollectionPlanner();
    this.cachePolicy = options.cachePolicy ?? DEFAULT_CACHE_TTL_POLICY;
    this.cacheStore = options.cacheStore ?? new InMemoryCacheStore();
    this.client =
      options.mcpBrasilClient ??
      new StdioMcpBrasilClient({
        cwd: process.cwd()
      });
    this.evidenceCollector = options.evidenceCollector;
    this.evidenceStore = options.evidenceStore ?? new InMemoryEvidenceStore();
    this.evidenceClassifier = new EvidenceClassifier();
    this.identityResolver = options.identityResolver;
    this.identityCatalog = options.identityCatalog ?? [];
    this.identitySources = options.identitySources;
    this.rawEvidenceCollector = options.rawEvidenceCollector;
    this.responseAssembler = new ResponseAssembler();
    this.signalEngine = options.signalEngine ?? new SignalEngine();
  }

  private buildEvidenceCollector(cacheStore: CacheStore): OfficialEvidenceCollector {
    return (
      this.evidenceCollector ??
      new CachedEvidenceCollector(
        this.rawEvidenceCollector ?? new McpBrasilEvidenceCollector(this.client),
        {
          cacheStore,
          ttlMs: this.cachePolicy.evidence_ms
        }
      )
    );
  }

  private buildIdentityResolver(cacheStore: CacheStore): IdentityResolver {
    return (
      this.identityResolver ??
      new InMemoryIdentityResolver({
        catalog: this.identityCatalog,
        cacheStore,
        cacheTtlMs: this.cachePolicy.identity_ms,
        sources:
          this.identitySources ?? [new McpBrasilIdentitySource(this.client)]
      })
    );
  }

  private buildSignalService(cacheStore: CacheStore): CachedSignalService {
    return new CachedSignalService(this.signalEngine, {
      cacheStore,
      ttlMs: this.cachePolicy.signal_ms
    });
  }

  private buildCollectedGrayResponse(
    candidate: ResolvedCandidate,
    evidence: readonly EvidenceRecord[],
    signalService: CachedSignalService,
    userPriorities: readonly string[]
  ): ConsultationResponse {
    const classifications = this.evidenceClassifier.classify(evidence);
    const signalResult = signalService.compute(
      candidate,
      evidence,
      classifications,
      userPriorities
    );
    const evidenceLevel = signalResult.evidence_level;
    const coherence = signalResult.coherence;
    const coherenceCoverage = signalResult.coherenceCoverage;
    const integrity = signalResult.integrity;
    const valuesFit = signalResult.values_fit;
    const observability = buildCoherenceObservability({
      candidate,
      coherence,
      coherenceCoverage
    });
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
        observability,
        signals: {
          ...base.signals,
          coherence,
          integrity,
          evidence_level: evidenceLevel,
          values_fit: valuesFit
        },
        sources: [...new Set(evidence.map((item) => item.source_url))]
      }),
      signals: {
        ...base.signals,
        coherence,
        integrity,
        evidence_level: evidenceLevel,
        values_fit: valuesFit
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
    const observedCacheStore = new ObservedCacheStore(this.cacheStore, {
      onGet: (scope, status) => {
        execution = recordExecutionCacheTelemetry(execution, scope, status);
      }
    });
    const identityResolver = this.buildIdentityResolver(observedCacheStore);
    const evidenceCollector = this.buildEvidenceCollector(observedCacheStore);
    const signalService = this.buildSignalService(observedCacheStore);

    const identity = await identityResolver.resolve({
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

      const rawEvidence = await evidenceCollector.collect(
        identity.candidate,
        plan
      );
      execution = appendExecutionStep(execution, "evidence_collected");
      const evidence = await this.evidenceStore.save(rawEvidence);
      execution = appendExecutionStep(execution, "evidence_stored");
      for (const entry of buildResolvedReviewQueueEntries(evidence)) {
        execution = appendExecutionReviewQueueEntry(execution, entry);
      }
      execution = appendExecutionStep(execution, "evidence_classified");
      execution = appendExecutionStep(execution, "signals_computed");

      const response = this.buildCollectedGrayResponse(
        identity.candidate,
        evidence,
        signalService,
        request.user_priorities
      );

      execution = appendExecutionStep(execution, "response_assembled");

      return {
        execution: finishQueryExecution(execution),
        response
      };
    }

    const alerts =
      identity.kind === "ambiguous"
        ? [formatIdentityDisambiguationMessage(identity.requires)]
        : ["Nenhuma identidade oficial foi encontrada para a consulta informada."];

    execution = appendExecutionStep(
      execution,
      identity.kind === "ambiguous" ? "identity_ambiguous" : "identity_not_found"
    );

    if (identity.kind === "ambiguous") {
      execution = appendExecutionReviewQueueEntry(execution, {
        message:
          "Consulta parada por ambiguidade forte de identidade; revisao humana necessaria.",
        reason: "identity_ambiguity",
        requires: identity.requires
      });
    }

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
          ? [formatIdentityDisambiguationMessage(identity.requires)]
          : ["Nao foi possivel resolver a identidade do candidato com seguranca."],
      summary:
        identity.kind === "ambiguous"
          ? "A consulta parou na etapa de identidade porque faltou contexto para identificar a pessoa certa."
          : "A consulta parou porque nenhuma identidade oficial foi localizada."
    });

    execution = appendExecutionStep(execution, "response_assembled");

    return {
      execution: finishQueryExecution(execution),
      response
    };
  }
}
