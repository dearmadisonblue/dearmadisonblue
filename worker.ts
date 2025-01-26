// worker.ts
import * as script from "./script.ts";

let interpreter = new script.Interpreter();

self.onmessage = async (e: MessageEvent) => {
  try {
    const parsed = interpreter.read(e.data);
    const result = interpreter.rewrite(parsed);
    self.postMessage(result.toString());
  } catch (error) {
    self.postMessage(`Error: ${error.message}`);
  }
};
