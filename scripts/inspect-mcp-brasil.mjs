import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: "uvx",
  args: ["--from", "mcp-brasil", "python", "-m", "mcp_brasil.server"],
  cwd: process.cwd(),
  env: { ...process.env },
  stderr: "pipe"
});

const client = new Client({
  name: "memoria-civica-probe",
  version: "0.1.0"
});

if (transport.stderr) {
  transport.stderr.on("data", (chunk) => {
    process.stderr.write(String(chunk));
  });
}

await client.connect(transport);

const tools = await client.listTools();

console.log(
  JSON.stringify(
    tools.tools.map((tool) => ({
      description: tool.description ?? "",
      inputSchema: tool.inputSchema,
      name: tool.name
    })),
    null,
    2
  )
);

await transport.close();
