// worker.ts
import * as script from "./script.ts";

let dictionary = new Map();

self.onmessage = async (event: MessageEvent) => {
  let { id, code } = event.data;
  try {
    let parsed = script.read(code);
    let result = script.evaluate(parsed, dictionary).toString();
    self.postMessage({ id, result });
  } catch (panic) {
    let error = `
While evaluating the expression:

${code}

The following error occurred:

${panic}
`.trim();
    self.postMessage({ id, error });
  }
};
