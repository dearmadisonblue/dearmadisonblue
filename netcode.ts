// An interpreter for a concatenative combinator language.
//
//            [a] Copy = [a] [a]
//            [a] Drop =
//        [a] [b] Swap = [b] [a]
//         [a] [b] Cat = [a b]
//             [a] Abs = [[a]]
//             [a] App = a
// [inl] [inr] [a] Inl = [a] inl
// [inl] [inr] [a] Inr = [a] inr
//    [fst] [snd] Pair = [[fst] [snd]]
//   [a] Shift b Reset = [b] a
//
// There are also words like:
//
// [body] "name" Define
// -- Add the word with the given name and body (unquoted) to the dictionary.
//
// "name" Delete
// -- Delete the word "name" from the dictionary.

import {
  serve,
} from "https://deno.land/std@0.190.0/http/mod.ts";

export abstract class Value {
  get name(): string {
    throw new NoSuchProperty("name", this);
  }

  get text(): string {
    throw new NoSuchProperty("string", this);
  }

  get prompt(): string {
    throw new NoSuchProperty("prompt", this);
  }

  get body(): Value {
    throw new NoSuchProperty("body", this);
  }

  get fst(): Value {
    throw new NoSuchProperty("fst", this);
  }

  get snd(): Value {
    throw new NoSuchProperty("snd", this);
  }

  get enum(): Value {
    throw new NoSuchProperty("enum", this);
  }

  get children(): Value[] {
    throw new NoSuchProperty("children", this);
  }

  abstract toString(): string;
}

export class Id extends Value {
  toString(): string {
    return "";
  }
}

export class Constant extends Value {
  private _name: string;

  constructor(name: string) {
    super();
    this._name = name;
  }

  override get name(): string {
    return this._name;
  }

  toString(): string {
    return this._name;
  }
}

export class Variable extends Value {
  private _name: string;

  constructor(name: string) {
    super();
    this._name = name;
  }

  override get name(): string {
    return this._name;
  }

  toString(): string {
    return this._name;
  }
}

export class Catenate extends Value {
  private _children: Value[];

  constructor(children: Value[]) {
    super();
    this._children = children;
  }

  override get children(): Value[] {
    return this._children;
  }

  toString(): string {
    return this._children.map(child => `${child}`).join(" ");
  }
}

export class Quote extends Value {
  private _body: Value;

  constructor(body: Value) {
    super();
    this._body = body;
  }

  override get body(): Value {
    return this._body;
  }

  toString(): string {
    return `[${this._body}]`;
  }
}

export class Text extends Value {
  private _value: string;

  constructor(value: string) {
    super();
    this._value = value;
  }

  override get text(): string {
    return this._value;
  }

  toString(): string {
    return `"${this._value}"`;
  }
}

export class Prompt extends Value {
  private _value: string;

  constructor(value: string) {
    super();
    this._value = value;
  }

  override get prompt(): string {
    return this._value;
  }

  toString(): string {
    return `{${this._value}}`;
  }
}

export class Panic extends Error {
  constructor(message?: string) {
    super(message);
    this.name = "Panic";
  }
}

export class NoMoreData extends Panic {
  constructor(public state: State) {
    super("No more data");
  }
}

export class NoMoreCode extends Panic {
  constructor(public state: State) {
    super("No more code");
  }
}

export class NoShift extends Panic {
  constructor(public state: State) {
    super("No shift");
  }
}

export class NoSuchProperty extends Panic {
  constructor(public property: string, public value: Value) {
    super(`No such property: ${property}`);
  }
}

export class Unreadable extends Panic {
  constructor(public source: string, message: string) {
    super(`Unreadable: ${message}`);
  }
}

export class Unexpected extends Panic {
  constructor(public expected: string, public actual: Value) {
    super(`Unexpected value`);
  }
}

export class Unknown extends Panic {
  constructor(public value: Value, public state: State) {
    super("Unknown value");
  }
}

function _isSeparator(char: string): boolean {
  return /\s|[\[\]]/.test(char);
}

export function id() {
  return new Id();
}

export function constant(name: string): Constant {
  return new Constant(name);
}

export function variable(name: string): Variable {
  return new Variable(name);
}

export function quote(value: Value): Quote {
  return new Quote(value);
}

export function text(value: string): Text {
  return new Text(value);
}

export function prompt(value: string): Prompt {
  return new Prompt(value);
}

export function catenate(...values: Value[]): Value {
  const buf: Value[] = [];
  for (const value of values) {
    if (value instanceof Id) {
      continue;
    } else if (value instanceof Catenate) {
      buf.push(...value.children);
    } else {
      buf.push(value);
    }
  }
  if (buf.length === 0) {
    return new Id();
  }
  return new Catenate(buf);
}

export function read(src: string): Value {
  let build: Value[] = [];
  let stack: Value[][] = [];
  let index = 0;
  while (index < src.length) {
    if (/\s/.test(src[index])) {
      while (index < src.length && /\s/.test(src[index])) {
        index++;
      }
    } else if (src[index] === "[") {
      stack.push(build);
      build = [];
      index++;
    } else if (src[index] === "]") {
      if (stack.length === 0) {
        throw new Unreadable(src, "Unbalanced brackets");
      }
      let value = quote(catenate(...build));
      build = stack.pop()!;
      build.push(value);
      index++;
    } else if (src[index] === '"') {
      index++;
      const start = index;
      while (index < src.length && src[index] !== '"') {
        index++;
      }
      if (index >= src.length) {
        throw new Unreadable(src, "Unbalanced quotes");
      }
      build.push(text(src.slice(start, index)));
      index++;
    } else if (src[index] === "{") {
      index++;
      const start = index;
      while (index < src.length && src[index] !== "}") {
        index++;
      }
      if (index >= src.length) {
        throw new Unreadable(src, "Unbalanced braces");
      }
      build.push(prompt(src.slice(start, index)));
      index++;
    } else if (/[A-Z]/.test(src[index])) {
      const start = index++;
      while (
        index < src.length && !_isSeparator(src[index])) {
        index++;
      }
      const name = src.slice(start, index);
      if (!/^[A-Z][\w-]*$/.test(name)) {
        throw new Unreadable(
          src, `Unknown symbol: ${name}`);
      }
      build.push(constant(name));
    } else {
      const start = index++;
      while (
        index < src.length && !_isSeparator(src[index])) {
        index++;
      }
      const name = src.slice(start, index);
      if (!/^[a-z][\w-]*$/.test(name)) {
        throw new Unreadable(
          src, `Unknown symbol: ${name}`);
      }
      build.push(variable(name));
    }
  }
  if (stack.length > 0) {
    throw new Unreadable(src, "Unbalanced brackets");
  }
  return catenate(...build);
}

export function evaluate(
  init: string | Value,
  dictionary?: Map<string, Value>,
  gas: number = 1_000_000,
): Value {
  if (typeof(init) === 'string') {
    init = read(init);
  }
  let state = new State(init);
  while (state.code.length > 0 && gas > 0) {
    gas--;
    const hand = state.getCode(0);
    if (hand instanceof Catenate) {
      state.popCode();
      state.pushCode(hand.children);
    } else if (hand instanceof Variable) {
      if (!dictionary || !dictionary.has(hand.name)) {
        state.thunk();
        gas = 0;
        continue;
      }
      const binding = dictionary.get(hand.name)!;
      state.popCode();
      state.pushCode(binding);
    } else if (
      hand instanceof Quote || hand instanceof Text) {
      state.popCode();
      state.pushData(hand);
    } else if (hand instanceof Prompt) {
      state.thunk();
      gas = 0;
      continue;
    } else if (hand instanceof Constant) {
      switch (hand.name) {
        case "Copy":
          var value;
          try {
            value = state.getData(0);
          } catch (err) {
            if (err instanceof Panic) {
              state.thunk();
              continue;
            }
            throw err;
          }
          state.popCode();
          state.pushData(value);
          break;
        case "Drop":
          var value;
          try {
            value = state.getData(0);
          } catch (err) {
            if (err instanceof Panic) {
              state.thunk();
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData();
          break;
        case "Swap":
          var fst;
          var snd;
          try {
            fst = state.getData(0);
            snd = state.getData(1);
          } catch (err) {
            if (err instanceof Panic) {
              state.thunk();
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData(2);
          state.pushData(fst);
          state.pushData(snd);
          break;
        case "Cat":
          var lhs;
          var rhs;
          try {
            lhs = state.getData(1).body;
            rhs = state.getData(0).body;
          } catch (err) {
            if (err instanceof Panic) {
              state.thunk();
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData(2);
          state.pushCode(quote(catenate(lhs, rhs)));
          break;
        case "Abs":
          var value;
          try {
            value = state.getData(0);
          } catch (err) {
            if (err instanceof Panic) {
              state.thunk();
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData();
          state.pushData(quote(value));
          break;
        case "App":
          var body;
          try {
            body = state.getData(0).body;
          } catch (err) {
            if (err instanceof Panic) {
              state.thunk();
              gas = 0;
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData();
          state.pushCode(body);
          break;
        case "Inl":
          var value;
          var inl;
          var inr;
          try {
            value = state.getData(0);
            inl = state.getData(2).body;
            inr = state.getData(1).body;
          } catch (err) {
            if (err instanceof Panic) {
              state.thunk();
              gas = 0;
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData(3);
          state.pushCode(inl);
          state.pushData(value);
          break;
        case "Inr":
          var value;
          var inl;
          var inr;
          try {
            value = state.getData(0);
            inl = state.getData(2).body;
            inr = state.getData(1).body;
          } catch (err) {
            if (err instanceof Panic) {
              state.thunk();
              gas = 0;
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData(3);
          state.pushCode(inr);
          state.pushData(value);
          break;
        case "Pair":
          var fst;
          var snd;
          try {
            fst = state.getData(1);
            snd = state.getData(0);
          } catch (err) {
            if (err instanceof Panic) {
              state.thunk();
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData(2);
          state.pushData(quote(catenate(fst, snd)));
          break;
        case "Shift":
          var buf = [];
          try {
            let handler = state.getData(0).body;
            let index = 1;
            while (index < state.numCode) {
              let code = state.getCode(index);
              if (code instanceof Constant) {
                if (code.name === 'Reset') {
                  break;
                } else {
                  buf.push(code);
                }
              } else {
                buf.push(code);
              }
              index++;
            }
            if (index >= state.numCode) {
              throw new NoShift(state);
            }
            let continuation = quote(catenate(...buf));
            state.popCode(index+1);
            state.popData();
            state.pushData(continuation);
            state.pushCode(handler);
          } catch(err) {
            if (err instanceof Panic) {
              state.thunk();
              gas = 0;
              continue;
            }
            throw err;
          }
          break;
        case "Reset":
          state.thunk();
          gas = 0;
          break;
        case "Define":
          if (dictionary == null) {
            state.thunk();
            gas = 0;
            continue;
          }
          var name;
          var body;
          try {
            name = state.getData(0).text;
            body = state.getData(1).body;
          } catch(err) {
            if (err instanceof Panic) {
              state.thunk();
              gas = 0;
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData(2);
          dictionary!.set(name, body);
          break;
        case "Delete":
          if (dictionary == null) {
            state.thunk();
            gas = 0;
            continue;
          }
          var name;
          try {
            name = state.getData(0).text;
          } catch(err) {
            if (err instanceof Panic) {
              state.thunk();
              gas = 0;
              continue;
            }
            throw err;
          }
          state.popCode();
          state.popData();
          dictionary!.delete(name);
          break;
      }
    } else {
      throw new Unknown(hand, state);
    }
  }
  return catenate(
    ...state.sink,
    ...state.data,
    ...state.code.toReversed(),
  );
}

export class State {
  code: Value[];
  data: Value[];
  sink: Value[];

  constructor(value: Value) {
    this.code = [value];
    this.data = [];
    this.sink = [];
  }

  get hasCode(): boolean {
    return this.code.length > 0;
  }

  getData(index: number): Value {
    if (index < 0 || index >= this.data.length) {
      throw new NoMoreData(this);
    }
    return this.data[this.data.length - 1 - index];
  }

  popData(length: number = 1): void {
    if (length > this.data.length) {
      throw new NoMoreData(this);
    }
    this.data.splice(-length, length);
  }

  pushData(value: Value | Value[]): void {
    if (Array.isArray(value)) {
      this.data.push(...value.reverse());
    } else {
      this.data.push(value);
    }
  }

  get numCode(): number {
    return this.code.length;
  }

  getCode(index: number): Value {
    if (index >= this.code.length) {
      throw new NoMoreCode(this);
    }
    return this.code[this.code.length - 1 - index];
  }

  popCode(length: number = 1): void {
    if (length > this.code.length) {
      throw new NoMoreCode(this);
    }
    this.code.splice(-length, length);
  }

  pushCode(value: Value | Value[]): void {
    if (Array.isArray(value)) {
      this.code.push(...value.reverse());
    } else {
      this.code.push(value);
    }
  }

  thunk(): void {
    this.sink.push(...this.data);
    this.data = [];
    if (this.code.length > 0) {
      this.sink.push(this.code.pop()!);
    }
  }
}

interface PromiseLike {
  resolve: (value) => void;
  reject: (reason) => void;
}

function workerAddress() {
  return new URL('./netcode/worker.ts', import.meta.url).href;
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
                let value = read(source);
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

if (import.meta.main) {
  let server = new Server();
  let port = 8080;
  server.listen(port);

}
