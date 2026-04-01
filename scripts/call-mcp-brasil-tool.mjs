import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { MCP_BRASIL_ARGS, MCP_BRASIL_COMMAND } from "./mcp-brasil-transport.mjs";

const [toolName, rawArguments = "{}"] = process.argv.slice(2);

if (!toolName) {
  throw new Error(
    "Usage: node scripts/call-mcp-brasil-tool.mjs <tool-name> '<json-args>'"
  );
}

const args = JSON.parse(rawArguments);

const transport = new StdioClientTransport({
  command: MCP_BRASIL_COMMAND,
  args: MCP_BRASIL_ARGS,
  cwd: process.cwd(),
  env: { ...process.env },
  stderr: "pipe"
});

const client = new Client({
  name: "memoria-civica-tool-call",
  version: "0.1.0"
});

if (transport.stderr) {
  transport.stderr.on("data", (chunk) => {
    process.stderr.write(String(chunk));
  });
}

await client.connect(transport);

const result = await client.callTool({
  name: "call_tool",
  arguments: {
    arguments: args,
    name: toolName
  }
});

console.log(JSON.stringify(result, null, 2));

await transport.close();
