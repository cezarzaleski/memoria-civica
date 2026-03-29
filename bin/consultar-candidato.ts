#!/usr/bin/env node

import { runConsultaEntrypoint } from "@/cli/consulta-entrypoint";

await runConsultaEntrypoint(process.argv.slice(2));
