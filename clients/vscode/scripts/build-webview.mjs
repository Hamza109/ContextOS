/**
 * Bundle React Flow webview → media/graphBlast.js (+ CSS).
 * Extension host stays CommonJS/tsc; webview is a separate IIFE bundle.
 */
import * as esbuild from "esbuild";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const mediaDir = path.join(root, "media");
const entry = path.join(root, "webview-src", "graphBlastApp.tsx");

fs.mkdirSync(mediaDir, { recursive: true });

await esbuild.build({
  entryPoints: [entry],
  bundle: true,
  outfile: path.join(mediaDir, "graphBlast.js"),
  format: "iife",
  platform: "browser",
  target: ["es2020"],
  jsx: "automatic",
  minify: true,
  sourcemap: true,
  loader: { ".css": "css" },
  // Pull React Flow styles into the JS bundle via side-effect import in app —
  // also copy CSS file for <link> in CSP-friendly HTML.
});

// Copy @xyflow/react stylesheet for <link> (CSP style-src webview.cspSource).
const xyflowCss = path.join(
  root,
  "node_modules",
  "@xyflow",
  "react",
  "dist",
  "style.css",
);
const outCss = path.join(mediaDir, "graphBlast.css");
if (fs.existsSync(xyflowCss)) {
  fs.copyFileSync(xyflowCss, outCss);
} else {
  fs.writeFileSync(
    outCss,
    "/* @xyflow/react style.css missing — run npm install */\n",
    "utf8",
  );
}

console.log("[build-webview] wrote media/graphBlast.js + graphBlast.css");
