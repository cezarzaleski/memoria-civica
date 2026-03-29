import type { ConsultationResponse } from "@/domain/models";
import { QueryOrchestrator } from "@/services/query-orchestrator";

interface WritableStreamLike {
  write(chunk: string): void;
}

interface ConsoleStreams {
  readonly stderr: WritableStreamLike;
  readonly stdout: WritableStreamLike;
}

interface ConsultPort {
  consult(input: {
    readonly candidate_name?: string;
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

function readFlagValue(args: readonly string[], index: number): string {
  const value = args[index + 1];

  if (value === undefined || value.startsWith("--")) {
    throw new Error(`Missing value for ${args[index]}`);
  }

  return value;
}

export function parseConsultaCliArgs(args: readonly string[]): {
  readonly candidate_name?: string;
  readonly party?: string;
  readonly uf?: string;
  readonly user_priorities?: readonly string[];
} {
  const userPriorities: string[] = [];
  let candidateName: string | undefined;
  let party: string | undefined;
  let uf: string | undefined;

  for (let index = 0; index < args.length; index += 1) {
    const current = args[index];

    if (current === "--candidate") {
      candidateName = readFlagValue(args, index);
      index += 1;
      continue;
    }

    if (current === "--uf") {
      uf = readFlagValue(args, index);
      index += 1;
      continue;
    }

    if (current === "--party") {
      party = readFlagValue(args, index);
      index += 1;
      continue;
    }

    if (current === "--priority") {
      userPriorities.push(readFlagValue(args, index));
      index += 1;
    }
  }

  return {
    candidate_name: candidateName,
    party,
    uf,
    user_priorities: userPriorities
  };
}

export async function runConsultaEntrypoint(
  args: readonly string[],
  streams: ConsoleStreams = {
    stderr: process.stderr,
    stdout: process.stdout
  },
  orchestrator: ConsultPort = new QueryOrchestrator()
): Promise<void> {
  const request = parseConsultaCliArgs(args);
  const result = await orchestrator.consult(request);

  streams.stdout.write(`${JSON.stringify(result.response, null, 2)}\n`);
  streams.stderr.write(
    `[trace=${result.execution.trace_id}] status=${result.execution.status} duration_ms=${result.execution.duration_ms}\n`
  );
}
