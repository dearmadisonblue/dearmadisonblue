// server.ts
import { serve } from "https://deno.land/std@0.190.0/http/mod.ts";

const handler = (req: Request): Response => {
  if (req.headers.get("upgrade") !== "websocket") {
    return new Response("Not a WebSocket request", { status: 400 });
  }

  const { socket, response } = Deno.upgradeWebSocket(req);

  const worker = new Worker(new URL("./worker.ts", import.meta.url).href, {
    type: "module",
  });

  worker.onmessage = (e) => {
    socket.send(e.data);
  };

  worker.onerror = (e) => {
    socket.send(`Error: ${e.message}`);
  };

  socket.onmessage = async (event) => {
    const sourceCode = event.data.toString();
    worker.postMessage(sourceCode);
  };

  socket.onclose = () => {
    worker.terminate();
  };

  socket.onerror = () => {
    worker.terminate();
  };

  return response;
};

const port = 8080;
console.log(`WebSocket server running on ws://localhost:${port}`);
serve(handler, { port });
