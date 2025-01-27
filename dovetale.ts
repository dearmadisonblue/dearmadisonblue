import {
  Server,
} from "./dovetale/server.ts";

let server = new Server();
let port = 8080;
server.listen(port);
