import { checkToken } from "./token";

export class Auth {
  validate(token: string): boolean {
    return checkToken(token);
  }
}
