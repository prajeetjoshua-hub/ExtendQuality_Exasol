import assert from "node:assert/strict";
import test from "node:test";

async function render(path = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}-${path}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request(`http://localhost${path}`, {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the EXtendQuality inspector dashboard", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>EXtendQuality \| Intelligent Bearing Inspection<\/title>/i);
  assert.match(html, /Inspection intelligence/);
  assert.match(html, /Camera Feed/);
  assert.match(html, /Processing Analysis/);
  assert.match(html, /VLM Recommendation/);
  assert.match(html, /Inspection Analytics/);
  assert.match(html, /DECISION ROUTING/);
  assert.match(html, /RECENT MODEL EVIDENCE/);
  assert.match(html, /Visual trace/i);
  assert.doesNotMatch(html, /Your site is taking shape|Building your site/);
});

test("renders the connected inspection controls and safety messaging", async () => {
  const response = await render();
  const html = await response.text();
  assert.match(html, /Run inspection/);
  assert.match(html, /CAMERA SOURCE/);
  assert.match(html, /CAPTURE ZOOM/);
  assert.match(html, /Start selected camera/);
  assert.match(html, /OpenCV preprocessing/);
  assert.match(html, /Inspector decision recorded/);
  assert.match(html, /CONNECTED PHONE CAMERA/);
  assert.doesNotMatch(html, /MODULE LOCKED/);
});

test("server-renders the evidence-linked visualizer", async () => {
  const response = await render("/inspection-visualizer");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /INSPECTION DIGITAL TWIN/);
  assert.match(html, /LIVE PROCESS TRACE/);
  assert.match(html, /SELECTIVE VLM/);
  assert.match(html, /HUMAN AUTHORITY/);
  assert.match(html, /not a live 3D reconstruction/i);
});
