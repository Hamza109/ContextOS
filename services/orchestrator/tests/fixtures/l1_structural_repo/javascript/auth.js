import token from "./token.js";

export class Auth {
  validate() {
    return checkToken(token);
  }
}
