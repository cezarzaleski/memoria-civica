export const MCP_BRASIL_COMMAND = "uvx";

export const MCP_BRASIL_ARGS = [
  "--with",
  "truststore",
  "--from",
  "mcp-brasil",
  "python",
  "-c",
  "import truststore; truststore.inject_into_ssl(); import runpy; runpy.run_module('mcp_brasil.server', run_name='__main__')"
];
