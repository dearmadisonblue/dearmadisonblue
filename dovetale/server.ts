// server.ts

import {
  serve,
} from "https://deno.land/std@0.190.0/http/mod.ts";

import * as script from "./script.ts";

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

  async listen() {
    while (true) {
      let source = await this.read();
      if (/^{\s*Quit\s*}/.test(source)) {
        this.send('Bye');
        return this.close();
      }
      let target = await this.evaluate(source);
      this.send(target);
    }
  }

  async read(returnType='string'): string {
    if (this.isSocketClosed) {
      throw new Error('WebSocket is closed');
    }
    if (this.readQueue.length > 0) {
      return this.readQueue.shift();
    }
    return new Promise((resolve, reject) => {
      this.pendingRead = {
        reject,
        resolve: (source) => {
          switch (returnType) {
            case 'string':
              resolve(source);
              break;
            case 'value':
              try {
                let value = script.read(source);
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

export class Server {
  listen(port: number = 8080) {
    serve((request: Request): Response => {
      if (request.headers.get("upgrade") !== "websocket") {
        return new Response("No", { status: 400 });
      }
      const { socket, response } = Deno.upgradeWebSocket(request);
      let client = new Client(socket);
      client.listen(client);
      return response;
    }, { port });
  }
}
