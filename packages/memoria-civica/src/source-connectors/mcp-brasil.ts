import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

import type {
  CollectionPlan,
  RawEvidence,
  ResolvedCandidate,
  IdentityQuery
} from "@/domain/models";
import { buildTseIdentityStrategy } from "@/source-connectors/tse-identity-strategy";

export interface OfficialIdentitySource {
  readonly source_name: string;

  searchCandidates(query: IdentityQuery): Promise<readonly ResolvedCandidate[]>;
}

export interface OfficialEvidenceCollector {
  collect(
    candidate: ResolvedCandidate,
    plan: CollectionPlan
  ): Promise<readonly RawEvidence[]>;
}

export interface McpBrasilToolClient {
  callTool(
    name: string,
    args: Record<string, unknown>
  ): Promise<string>;
}

interface StdioMcpBrasilClientOptions {
  readonly args?: readonly string[];
  readonly command?: string;
  readonly cwd?: string;
  readonly env?: NodeJS.ProcessEnv;
}

const DEFAULT_MCP_BRASIL_COMMAND = "uvx";
const DEFAULT_MCP_BRASIL_ENTRYPOINT = [
  "--with",
  "truststore",
  "--from",
  "mcp-brasil",
  "python",
  "-c",
  "import truststore; truststore.inject_into_ssl(); import runpy; runpy.run_module('mcp_brasil.server', run_name='__main__')"
] as const;

function readProperty(payload: object, key: string): unknown {
  return Reflect.get(payload, key) as unknown;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function toStringRecord(
  input: NodeJS.ProcessEnv | undefined
): Record<string, string> {
  return Object.entries(input ?? {}).reduce<Record<string, string>>(
    (record, [key, value]) => {
      if (typeof value === "string") {
        record[key] = value;
      }

      return record;
    },
    {}
  );
}

function extractTextResult(payload: unknown): string {
  if (typeof payload !== "object" || payload === null) {
    return "";
  }

  const structuredContent = readProperty(payload, "structuredContent");

  if (typeof structuredContent === "object" && structuredContent !== null) {
    const result = readProperty(structuredContent, "result");

    if (typeof result === "string") {
      return result;
    }
  }

  const content = readProperty(payload, "content");

  if (Array.isArray(content)) {
    const firstTextBlock = content.filter(isRecord).find((item) => {
      return readProperty(item, "type") === "text";
    });

    if (isRecord(firstTextBlock)) {
      const text = readProperty(firstTextBlock, "text");

      if (typeof text === "string") {
        return text;
      }
    }
  }

  return "";
}

function parseMarkdownTable(raw: string): Array<Record<string, string>> {
  const lines = raw
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("|"));

  if (lines.length < 3) {
    return [];
  }

  const headers = lines[0]
    .split("|")
    .map((cell) => cell.trim())
    .filter(Boolean);
  const rows = lines.slice(2);

  return rows.map((line) => {
    const cells = line
      .split("|")
      .map((cell) => cell.trim())
      .filter(Boolean);

    return headers.reduce<Record<string, string>>((record, header, index) => {
      record[header] = cells[index] ?? "";
      return record;
    }, {});
  });
}

function normalizeLabel(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .replace(/\s+/g, "_")
    .trim();
}

function readCell(
  row: Record<string, string>,
  aliases: readonly string[]
): string | undefined {
  const normalizedEntries = Object.entries(row).map(([key, value]) => {
    return [normalizeLabel(key), value] as const;
  });

  for (const alias of aliases) {
    const match = normalizedEntries.find(([key]) => key === normalizeLabel(alias));

    if (match?.[1]) {
      return match[1];
    }
  }

  return undefined;
}

function mapCamaraRowToCandidate(
  row: Record<string, string>
): ResolvedCandidate | null {
  const name = row.Nome;
  const camaraId = row.ID;

  if (!name || !camaraId) {
    return null;
  }

  return {
    ambiguity_level: "none",
    canonical_name: name,
    office: "deputado_federal",
    official_ids: {
      camara_id: camaraId
    },
    party: row.Partido || undefined,
    status: "incumbent",
    uf: row.UF || undefined
  };
}

function mapOfficeToTseCargo(query: IdentityQuery): string {
  return query.office === "deputado_distrital"
    ? "deputado_distrital"
    : "deputado_federal";
}

function buildPersonId(candidate: ResolvedCandidate): string {
  return (
    candidate.official_ids.camara_id ??
    candidate.official_ids.tse_id ??
    candidate.official_ids.mcp_brasil_id ??
    `${candidate.office}:${candidate.uf ?? "BR"}:${candidate.canonical_name}`
  );
}

function summarizeRawResult(raw: string): string {
  const normalized = raw.replace(/\s+/g, " ").trim();

  if (normalized === "") {
    return "Coleta oficial sem conteudo textual.";
  }

  return normalized.slice(0, 280);
}

function summarizeFormalActivityRecord(raw: string): string {
  const summary = summarizeRawResult(raw);

  return `${summary} Limitacao: o mcp-brasil atual ainda nao vincula autoria, relatoria ou voto nominal diretamente ao deputado neste fluxo.`;
}

function summarizeVotingSummary(name: string, raw: string): string {
  const summary = summarizeRawResult(raw);

  return `Participacao nominal recente identificada para ${name}. ${summary}`;
}

function parseInteger(value: unknown): number | null {
  if (typeof value === "number" && Number.isInteger(value)) {
    return value;
  }

  if (typeof value === "string" && /^\d+$/.test(value)) {
    return Number.parseInt(value, 10);
  }

  return null;
}

function hasNoSanctionsMatch(raw: string): boolean {
  return /nenhuma san[cç][aã]o encontrada/i.test(raw);
}

function formatIsoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function buildRecentVotingWindow(days: number): { readonly data_fim: string; readonly data_inicio: string } {
  const end = new Date();
  const start = new Date(end);
  start.setUTCDate(start.getUTCDate() - days);

  return {
    data_fim: formatIsoDate(end),
    data_inicio: formatIsoDate(start)
  };
}

function parseVotingIds(raw: string): readonly string[] {
  return parseMarkdownTable(raw)
    .map((row) => readCell(row, ["id", "id votacao", "votacao_id"]))
    .filter((value): value is string => typeof value === "string" && value.trim() !== "");
}

function normalizeSearchText(value: string): string {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase();
}

function buildCandidateNameVariants(candidate: ResolvedCandidate): readonly string[] {
  return [
    candidate.canonical_name,
    ...(candidate.aliases ?? [])
  ]
    .map((item) => item.trim())
    .filter((item, index, array) => item !== "" && array.indexOf(item) === index);
}

function includesCandidateName(raw: string, candidate: ResolvedCandidate): boolean {
  const normalizedRaw = normalizeSearchText(raw);

  return buildCandidateNameVariants(candidate).some((variant) => {
    return normalizedRaw.includes(normalizeSearchText(variant));
  });
}

function mapTseRowToCandidate(
  row: Record<string, string>,
  query: IdentityQuery
): ResolvedCandidate | null {
  const name = readCell(row, ["nome", "candidato"]);

  if (!name) {
    return null;
  }

  const candidateNumber = readCell(row, ["numero", "número"]);

  return {
    ambiguity_level: "none",
    canonical_name: name,
    office: query.office,
    official_ids: candidateNumber
      ? {
          mcp_brasil_id: `tse:2022:${query.uf ?? "BR"}:${query.office}:${candidateNumber}`
        }
      : {},
    party: readCell(row, ["partido", "sigla_partido"]),
    status: "challenger",
    uf: query.uf
  };
}

export class StdioMcpBrasilClient implements McpBrasilToolClient {
  private client?: Client;

  private readonly options: StdioMcpBrasilClientOptions;

  private transport?: StdioClientTransport;

  public constructor(options: StdioMcpBrasilClientOptions = {}) {
    this.options = {
      ...options,
      args: options.args ?? DEFAULT_MCP_BRASIL_ENTRYPOINT,
      command: options.command ?? DEFAULT_MCP_BRASIL_COMMAND
    };
  }

  private async connect(): Promise<Client> {
    if (this.client) {
      return this.client;
    }

    this.transport = new StdioClientTransport({
      args: [...(this.options.args ?? DEFAULT_MCP_BRASIL_ENTRYPOINT)],
      command: this.options.command ?? DEFAULT_MCP_BRASIL_COMMAND,
      cwd: this.options.cwd,
      env: {
        ...toStringRecord(process.env),
        ...toStringRecord(this.options.env)
      },
      stderr: "inherit"
    });

    this.client = new Client({
      name: "memoria-civica",
      version: "0.1.0"
    });

    await this.client.connect(this.transport);

    return this.client;
  }

  public async callTool(
    name: string,
    args: Record<string, unknown>
  ): Promise<string> {
    const client = await this.connect();
    const result = await client.callTool({
      name: "call_tool",
      arguments: {
        arguments: args,
        name
      }
    });

    return extractTextResult(result);
  }
}

export class McpBrasilIdentitySource implements OfficialIdentitySource {
  public readonly source_name = "mcp-brasil";

  public constructor(private readonly client: McpBrasilToolClient) {}

  public async searchCandidates(
    query: IdentityQuery
  ): Promise<readonly ResolvedCandidate[]> {
    if (query.office === "deputado_distrital") {
      return this.searchTseStateResults(query);
    }

    if (query.office !== "deputado_federal") {
      return [];
    }

    const raw = await this.client.callTool("camara_listar_deputados", {
      nome: query.name,
      sigla_partido: query.party,
      sigla_uf: query.uf
    });

    const camaraMatches = parseMarkdownTable(raw)
      .map(mapCamaraRowToCandidate)
      .filter((candidate): candidate is ResolvedCandidate => candidate !== null);

    if (camaraMatches.length > 0 || query.uf === undefined) {
      return camaraMatches;
    }

    return this.searchTseStateResults(query);
  }

  private async searchTseStateResults(
    query: IdentityQuery
  ): Promise<readonly ResolvedCandidate[]> {
    if (query.uf === undefined) {
      return [];
    }

    buildTseIdentityStrategy(query);

    const raw = await this.client.callTool("tse_resultado_por_estado", {
      ano: 2022,
      cargo: mapOfficeToTseCargo(query),
      uf: query.uf
    });

    return parseMarkdownTable(raw)
      .map((row) => mapTseRowToCandidate(row, query))
      .filter((candidate): candidate is ResolvedCandidate => candidate !== null);
  }
}

export class McpBrasilEvidenceCollector implements OfficialEvidenceCollector {
  private static readonly MAX_NOMINAL_VOTING_CHECKS = 3;

  public constructor(private readonly client: McpBrasilToolClient) {}

  private async collectLegislativeProfile(
    candidate: ResolvedCandidate,
    task: CollectionPlan["tasks"][number]
  ): Promise<RawEvidence | null> {
    const deputadoId = parseInteger(task.params.camara_id);

    const raw =
      deputadoId === null
        ? await this.client.callTool("camara_listar_deputados", {
            nome: task.params.name,
            sigla_partido: task.params.party,
            sigla_uf: task.params.uf
          })
        : await this.client.callTool("camara_buscar_deputado", {
            deputado_id: deputadoId
          });

    if (raw.trim() === "") {
      return null;
    }

    if (deputadoId === null && parseMarkdownTable(raw).length === 0) {
      return null;
    }

    return {
      collected_at: new Date().toISOString(),
      evidence_type: "legislative_profile",
      person_id: buildPersonId(candidate),
      signal_type: "evidence_level",
      source_name: "camara",
      source_url:
        deputadoId === null
          ? "https://dadosabertos.camara.leg.br/api/v2/deputados"
          : `https://dadosabertos.camara.leg.br/api/v2/deputados/${deputadoId}`,
      strength: "strong_official",
      summary: summarizeRawResult(raw)
    } satisfies RawEvidence;
  }

  private async collectFormalActivityRecord(
    candidate: ResolvedCandidate,
    task: CollectionPlan["tasks"][number]
  ): Promise<RawEvidence | null> {
    const deputadoId = parseInteger(task.params.camara_id);

    if (deputadoId === null) {
      return null;
    }

    const raw = await this.client.callTool("camara_buscar_deputado", {
      deputado_id: deputadoId
    });

    if (raw.trim() === "") {
      return null;
    }

    return {
      collected_at: new Date().toISOString(),
      evidence_type: "formal_activity_record",
      person_id: buildPersonId(candidate),
      signal_type: "coherence",
      source_name: "camara",
      source_url: `https://dadosabertos.camara.leg.br/api/v2/deputados/${deputadoId}`,
      strength: "strong_official",
      summary: summarizeFormalActivityRecord(raw)
    };
  }

  private async collectIntegrityScreening(
    candidate: ResolvedCandidate
  ): Promise<RawEvidence | null> {
    const raw = await this.client.callTool("transparencia_buscar_sancoes", {
      bases: ["ceis", "cnep"],
      consulta: candidate.canonical_name,
      pagina: 1
    });

    if (!hasNoSanctionsMatch(raw)) {
      return null;
    }

    return {
      collected_at: new Date().toISOString(),
      evidence_type: "integrity_screening",
      person_id: buildPersonId(candidate),
      signal_type: "integrity",
      source_name: "transparencia",
      source_url: "https://api.portaldatransparencia.gov.br/api-de-dados/ceis",
      strength: "strong_official",
      summary:
        "Consulta nominal na Transparencia nao encontrou sancoes nas bases CEIS/CNEP. Limitacao: depende do nome informado e pode nao cobrir homonimos."
    };
  }

  private async collectVotingSummary(
    candidate: ResolvedCandidate
  ): Promise<RawEvidence | null> {
    const window = buildRecentVotingWindow(30);
    const rawVotingList = await this.client.callTool("camara_buscar_votacao", {
      data_fim: window.data_fim,
      data_inicio: window.data_inicio,
      pagina: 1
    });
    const votingIds = parseVotingIds(rawVotingList).slice(
      0,
      McpBrasilEvidenceCollector.MAX_NOMINAL_VOTING_CHECKS
    );

    for (const votingId of votingIds) {
      const rawNominalVotes = await this.client.callTool("camara_votos_nominais", {
        votacao_id: votingId
      });

      if (!includesCandidateName(rawNominalVotes, candidate)) {
        continue;
      }

      return {
        collected_at: new Date().toISOString(),
        evidence_type: "voting_summary",
        person_id: buildPersonId(candidate),
        signal_type: "coherence",
        source_name: "camara",
        source_url: "https://dadosabertos.camara.leg.br/api/v2/votacoes",
        strength: "strong_official",
        summary: summarizeVotingSummary(candidate.canonical_name, rawNominalVotes)
      };
    }

    return null;
  }

  public async collect(
    candidate: ResolvedCandidate,
    plan: CollectionPlan
  ): Promise<readonly RawEvidence[]> {
    const taskEvidencePromises = plan.tasks.map(async (task) => {
      if (task.source === "camara") {
        if (task.objective === "coletar_atuacao_formal") {
          return this.collectFormalActivityRecord(candidate, task);
        }

        if (task.objective === "coletar_votacoes_nominais") {
          return this.collectVotingSummary(candidate);
        }

        return this.collectLegislativeProfile(candidate, task);
      }

      const raw = await this.client.callTool("tse_resultado_por_estado", {
        ano: 2022,
        cargo: task.params.office ?? candidate.office,
        uf: task.params.uf ?? candidate.uf
      });

      if (parseMarkdownTable(raw).length === 0) {
        return null;
      }

      return {
        collected_at: new Date().toISOString(),
        evidence_type: "electoral_registry",
        person_id: buildPersonId(candidate),
        signal_type: "evidence_level",
        source_name: "tse",
        source_url: "https://resultados.tse.jus.br/oficial/app/index.html#/eleicao/resultados",
        strength: "strong_official",
        summary: summarizeRawResult(raw)
      } satisfies RawEvidence;
    });

    const integrityEvidencePromise = plan.requested_signals.includes("integrity")
      ? this.collectIntegrityScreening(candidate)
      : Promise.resolve(null);

    const evidence: Array<RawEvidence | null> = await Promise.all([
      ...taskEvidencePromises,
      integrityEvidencePromise
    ]);

    return evidence.filter((item): item is RawEvidence => item !== null);
  }
}
