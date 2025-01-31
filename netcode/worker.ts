// worker.ts
import * as netcode from "../netcode.ts";

let dictionary = new Map();

self.onmessage = async (event: MessageEvent) => {
  let { id, code } = event.data;
  try {
    let parsed = netcode.read(code);
    let result = netcode.evaluate(parsed, dictionary).toString();
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
