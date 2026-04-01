import { createApiServer } from "./app";

function readPort(value: string | undefined): number {
  const parsed = Number.parseInt(value ?? "3000", 10);

  if (Number.isNaN(parsed) || parsed <= 0) {
    throw new Error("PORT must be a positive integer");
  }

  return parsed;
}

const host = process.env.HOST ?? "0.0.0.0";
const port = readPort(process.env.PORT);
const server = createApiServer();

server.listen(port, host, () => {
  process.stdout.write(`API listening on http://${host}:${port}\n`);
});
