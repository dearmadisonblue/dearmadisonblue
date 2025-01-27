// server.ts

import {
  serve,
} from "https://deno.land/std@0.190.0/http/mod.ts";

interface PromiseLike {
  resolve: (value) => void;
  reject: (reason) => void;
}

function workerAddress() {
  return new URL('./worker.ts', import.meta.url).href;
}

class Client {
  // TODO: Replace these with the actual type names for Deno's web
  // sockets and web workers.
  socket: WebSocket;
  worker: any;
  readQueue: string[];
  pendingRead: PromiseLike | null;
  pendingEval: Map<int, PromiseLike>;
  nextId: number = 0;
  isSocketClosed: boolean;

  constructor(socket) {
    this.socket = socket;
    this.worker = new Worker(workerAddress(), { type: 'module' });
    this.readQueue = [];
    this.pendingRead = null;
    this.pendingEval = new Map();
    this.isSocketClosed = false;
    this.socket.onmessage = this.onSocketMessage.bind(this);
    this.socket.onerror = this.onSocketError.bind(this);
    this.socket.onclose = this.onSocketClose.bind(this);
    this.worker.onmessage = this.onWorkerMessage.bind(this);
    this.worker.onerror = this.onWorkerError.bind(this);
  }

  async read(returnType='string'): string {
    if (this.isSocketClosed) {
      throw new Error('WebSocket is closed');
    }
    if (this.readQueue.length > 0) {
      console.log('read: returning a message from the queue');
      return this.readQueue.shift();
    }
    console.log('read: no messages, returning a promise');
    return new Promise((resolve, reject) => {
      this.pendingRead = {
        reject,
        resolve: (source) => {
          console.log(`read: resolving message with ${source}`);
          switch (returnType) {
            case 'string':
              resolve(source);
              break;
            case 'value':
              try {
                let value = script.read(source);
                console.log(`read: got the value ${value}`);
                resolve(value);
              } catch(error) {
                reject(error);
              }
              break;
            default:
              break;
          }
        },
      };
    });
  }

  async evaluate(code: string): string {
    let id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pendingEval.set(id, { resolve, reject });
      this.worker.postMessage({ id, code });
    });
  }

  send(message: string) {
    this.socket.send(message || '{ Okay }');
  }

  close() {
    this.socket.close();
    this.worker.terminate();
  }

  onSocketMessage(event) {
    let code = event.data.toString();
    if (this.pendingRead) {
      let { resolve, reject } = this.pendingRead;
      this.pendingRead = null;
      resolve(code);
    } else {
      this.readQueue.push(code);
    }
  }

  onWorkerMessage(event) {
    const { id, result, error } = event.data;
    console.log(`Worker message: ${id} ${result} ${error}`);
    if (this.pendingEval.has(id)) {
      const { resolve, reject } = this.pendingEval.get(id);
      this.pendingEval.delete(id);
      error? reject(error) : resolve(result);
    }
  }

  onSocketError(error) {
    this.worker.terminate();
  }

  onWorkerError(error) {
    this.socket.close();
    this.worker.terminate();
  }

  onSocketClose() {
    this.worker.terminate();
  }
}

async function listen(client) {
  console.log('Listening to a new client');
  while (true) {
    let source = await client.read();
    console.log(`Got source code: ${source}`);
    if (source.trim() in ['{Quit}','{ Quit }']) {
      return client.close();
    }
    let target = await client.evaluate(source);
    console.log(`Evaluated to ${target}`);
    client.send(target);
  }
}

const port = 8080;
console.log(`Listening on ${port}`);
serve((request: Request): Response => {
  if (request.headers.get("upgrade") !== "websocket") {
    return new Response("No", { status: 400 });
  }
  const { socket, response } = Deno.upgradeWebSocket(request);
  let client = new Client(socket);
  listen(client);
  return response;
}, { port });
