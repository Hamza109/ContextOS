/**
 * React Flow webview app (EP-007 / US-020).
 * Renders nodes/edges posted from the extension (FastAPI blast-derived).
 * Does not call orchestrator or compute blast locally.
 */

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
  type NodeMouseHandler,
} from "@xyflow/react";

declare function acquireVsCodeApi(): {
  postMessage(msg: unknown): void;
};

type Kind = "target" | "direct" | "transitive";

interface IncomingNode {
  id: string;
  label: string;
  kind: Kind;
}

interface IncomingEdge {
  id: string;
  source: string;
  target: string;
}

const KIND_COLOR: Record<Kind, string> = {
  target: "#38bdf8",
  direct: "#64748b",
  transitive: "#475569",
};

function layoutNodes(incoming: IncomingNode[]): Node[] {
  const target = incoming.find((n) => n.kind === "target");
  const others = incoming.filter((n) => n.kind !== "target");
  const nodes: Node[] = [];
  if (target) {
    nodes.push({
      id: target.id,
      position: { x: 280, y: 200 },
      data: { label: target.label },
      style: {
        background: KIND_COLOR.target,
        color: "#0f172a",
        border: "1px solid #e2e8f0",
        borderRadius: 6,
        padding: 8,
        fontSize: 12,
      },
    });
  }
  others.forEach((n, i) => {
    const col = i % 4;
    const row = Math.floor(i / 4);
    nodes.push({
      id: n.id,
      position: { x: 40 + col * 160, y: 40 + row * 80 },
      data: { label: n.label },
      style: {
        background: KIND_COLOR[n.kind],
        color: "#e2e8f0",
        border: "1px solid #334155",
        borderRadius: 6,
        padding: 6,
        fontSize: 11,
        maxWidth: 140,
      },
    });
  });
  return nodes;
}

function App(): React.ReactElement {
  const vscode = useMemo(() => acquireVsCodeApi(), []);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [banner, setBanner] = useState("Waiting for FastAPI blast payload…");
  const [bannerClass, setBannerClass] = useState("");
  const [stale, setStale] = useState(false);
  const [badge, setBadge] = useState("");

  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      const data = event.data as Record<string, unknown> | null;
      if (!data || typeof data.type !== "string") return;

      if (data.type === "status" && typeof data.message === "string") {
        setBanner(data.message);
        setBannerClass("");
        return;
      }
      if (data.type === "error" && typeof data.message === "string") {
        setBanner(data.message);
        setBannerClass("error");
        setNodes([]);
        setEdges([]);
        return;
      }
      if (data.type === "empty" && typeof data.message === "string") {
        setBanner(data.message);
        setBannerClass("empty");
        return;
      }
      if (data.type === "staleness") {
        setStale(data.stale === true);
        setBadge(typeof data.badge === "string" ? data.badge : "");
        return;
      }
      if (data.type === "blastGraph") {
        const fileName = typeof data.fileName === "string" ? data.fileName : "";
        const risk = typeof data.risk === "string" ? data.risk : "";
        const inNodes = Array.isArray(data.nodes) ? (data.nodes as IncomingNode[]) : [];
        const inEdges = Array.isArray(data.edges) ? (data.edges as IncomingEdge[]) : [];
        setNodes(layoutNodes(inNodes));
        setEdges(
          inEdges.map((e) => ({
            id: e.id,
            source: e.source,
            target: e.target,
            style: { stroke: "#64748b" },
            animated: false,
          })),
        );
        setStale(data.stale === true);
        setBadge(typeof data.badge === "string" ? data.badge : "");
        setBanner(`Blast: ${fileName} · risk=${risk} · nodes=${inNodes.length} (FastAPI)`);
        setBannerClass("");
      }
    };
    window.addEventListener("message", onMessage);
    vscode.postMessage({ type: "ready" });
    return () => window.removeEventListener("message", onMessage);
  }, [vscode]);

  useEffect(() => {
    const el = document.getElementById("badge");
    const bannerEl = document.getElementById("banner");
    if (bannerEl) {
      bannerEl.textContent = banner;
      bannerEl.className = bannerClass;
    }
    if (el) {
      if (stale && badge) {
        el.textContent = badge;
        el.classList.add("visible");
      } else {
        el.textContent = "";
        el.classList.remove("visible");
      }
    }
  }, [banner, bannerClass, stale, badge]);

  const onNodeClick: NodeMouseHandler = useCallback(
    (_event, node) => {
      vscode.postMessage({ type: "openFile", path: node.id });
    },
    [vscode],
  );

  if (nodes.length === 0) {
    return <div style={{ padding: 16, color: "#94a3b8" }}>No graph data yet.</div>;
  }

  return (
    <div style={{ width: "100%", height: "calc(100% - 36px)" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        onNodeClick={onNodeClick}
        nodesDraggable
        nodesConnectable={false}
        elementsSelectable
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#334155" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={() => "#64748b"}
          maskColor="rgba(15,23,42,0.7)"
          style={{ background: "#1e293b" }}
        />
      </ReactFlow>
    </div>
  );
}

const rootEl = document.getElementById("root");
if (rootEl) {
  createRoot(rootEl).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}
