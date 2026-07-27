/**
 * Workspace helpers — path/name only. No ignore policy, no packing.
 */

export interface WorkspaceFolderLike {
  uri: { fsPath: string };
  name: string;
}

export function resolvePrimaryWorkspace(
  folders: readonly WorkspaceFolderLike[] | undefined,
): { repo_path: string; repo_name: string } | undefined {
  if (!folders || folders.length === 0) {
    return undefined;
  }
  const folder = folders[0];
  return {
    repo_path: folder.uri.fsPath,
    repo_name: folder.name || basename(folder.uri.fsPath),
  };
}

function basename(p: string): string {
  const parts = p.replace(/\\/g, "/").split("/").filter(Boolean);
  return parts[parts.length - 1] ?? "workspace";
}

/**
 * Relative path of a saved file within the workspace (for Proposed files[] scope).
 * Returns undefined if outside workspace — caller should skip.
 */
export function relativeWorkspacePath(
  workspaceRoot: string,
  fileFsPath: string,
): string | undefined {
  const root = normalizeFs(workspaceRoot);
  const file = normalizeFs(fileFsPath);
  if (file === root) {
    return undefined;
  }
  const prefix = root.endsWith("/") ? root : `${root}/`;
  if (!file.startsWith(prefix) && file !== root) {
    // Windows drive letter case
    if (!file.toLowerCase().startsWith(prefix.toLowerCase())) {
      return undefined;
    }
    return file.slice(prefix.length);
  }
  return file.slice(prefix.length);
}

function normalizeFs(p: string): string {
  return p.replace(/\\/g, "/");
}
