/**
 * contextos CLI entrypoint (Proposed packaging under clients/cli/).
 */

import { runAsk } from "./ask";
import { helpText, parseArgv } from "./cli";

export async function main(argv: string[] = process.argv.slice(2)): Promise<number> {
  const parsed = parseArgv(argv);
  if (parsed.help) {
    process.stdout.write(`${helpText()}\n`);
    return 0;
  }
  if (parsed.error) {
    process.stderr.write(`Error: ${parsed.error}\n\n${helpText()}\n`);
    return 2;
  }
  if (!parsed.ask) {
    process.stderr.write(`Error: nothing to do\n\n${helpText()}\n`);
    return 2;
  }

  try {
    await runAsk(parsed.ask);
    return 0;
  } catch {
    return 1;
  }
}

if (require.main === module) {
  void main().then((code) => {
    process.exit(code);
  });
}
