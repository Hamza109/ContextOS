/** Public CLI modules for tests and programmatic use. */
export { buildAskRequest, runAsk, resolveBaseUrl, formatAskError, DEFAULT_TOP_K } from "./ask";
export { postContext, ContextClientError } from "./contextClient";
export { formatHumanAskReport } from "./humanRenderer";
export { formatMachineAskReport, PROPOSED_MACHINE_SCHEMA_NOTE } from "./machineRenderer";
export { parseArgv, helpText } from "./cli";
export type { ContextRequest, ContextResponse } from "./types";
