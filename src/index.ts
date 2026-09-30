import { node } from "@elysiajs/node";
import { Elysia } from "elysia";

const port = Number(process.env.PORT) || 3000;

const app = new Elysia({ adapter: "Bun" in globalThis ? undefined : node() })
  .get("/", () => ({ message: "Hello from tts-be!" }))
  .listen(port);

console.log(`Server running at http://localhost:${app.server?.port ?? port}`);
