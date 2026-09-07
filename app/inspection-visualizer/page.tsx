"use client";

import { useCallback, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type Record = {
  id: string; created_at: string; bearing_type: string; status: string;
  image_quality: { score: number; issues: string[] };
  geometry_result?: { capture_source?: "upload" | "camera" };
  yolo_result: { model_ready: boolean; model_version: string; classification: { label: string; confidence: number } | null };
  decision: { disposition: string; score: number; needs_vlm: boolean; reasons: string[] };
  vlm_result: { invoked: boolean; mode: string; analysis: string; recommendation: string };
  review_status: string; human_decision: string | null; processing_time_ms: number;
};

const balls = Array.from({ length: 8 }, (_, index) => index);

function percent(value?: number) { return value == null ? "--" : `${Math.round(value * 100)}%`; }
function conditionLabel(label: string) { return label === "rust" ? "SURFACE CONDITION (RUST / GREASE)" : label === "displaced" ? "ABNORMAL BALL ARRANGEMENT" : label.toUpperCase(); }

export default function InspectionVisualizer() {
  const [inspection, setInspection] = useState<Record | null>(null);
  const [connected, setConnected] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/inspections?limit=1`, { cache: "no-store" });
      if (!response.ok) throw new Error("API unavailable");
      const records = await response.json() as Record[];
      setInspection(records[0] ?? null);
      setConnected(true);
    } catch {
      setConnected(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 2000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  const label = inspection?.yolo_result.classification?.label ?? "awaiting inspection";
  const confidence = inspection?.yolo_result.classification?.confidence;
  const displaced = label.toLowerCase() === "displaced";
  const rust = label.toLowerCase() === "rust";

  return <main className="visualizer-shell">
    <header className="visualizer-topbar">
      <a href="/" className="visualizer-brand"><i>EQ</i><span>EXtendQuality<small>INSPECTION DIGITAL TWIN</small></span></a>
      <div className={connected ? "system-link system-link--online" : "system-link"}><i/>{connected ? "LIVE EVIDENCE LINK" : "BACKEND OFFLINE"}</div>
      <a href="/" className="back-link">Inspector dashboard</a>
    </header>

    <section className="visualizer-grid">
      <div className="bearing-visual">
        <div className="visual-heading"><span>BEARING / {inspection?.bearing_type ?? "UNASSIGNED"}</span><strong>{inspection ? inspection.id.slice(0, 12).toUpperCase() : "NO INSPECTION"}</strong></div>
        <div className={`bearing-model ${rust ? "bearing-model--rust" : ""}`}>
          <div className="outer-ring"/><div className="inner-ring"/><div className="bearing-core"/>
          <div className="ball-track">{balls.map((ball) => <i key={ball} className={displaced && ball === 1 ? "ball ball--displaced" : "ball"} style={{ "--ball-index": ball } as React.CSSProperties}/>)}</div>
          {(displaced || rust) && <div className={`defect-beacon ${rust ? "defect-beacon--rust" : ""}`}><i/><span>{rust ? "RUST / GREASE CANNOT BE SEPARATED" : "SPACING ANOMALY"}<strong>{conditionLabel(label)} · {percent(confidence)}</strong></span></div>}
        </div>
        <div className="visual-disclaimer">Evidence-linked visual representation — not a live 3D reconstruction or calibrated dimensional measurement.</div>
      </div>

      <aside className="pipeline-panel">
        <header><span>LIVE PROCESS TRACE</span><strong>{inspection?.status ?? "STANDBY"}</strong></header>
        <ol className="pipeline-list">
          <li className={inspection ? "is-complete" : ""}><i>01</i><div><span>CAPTURE</span><strong>{inspection ? "Frame acquired" : "Awaiting frame"}</strong><small>{inspection ? new Date(inspection.created_at).toLocaleTimeString() : "Camera or file input"}</small></div></li>
          <li className={inspection ? "is-complete" : ""}><i>02</i><div><span>OPENCV QUALITY GATE</span><strong>{inspection ? `${percent(inspection.image_quality.score)} usable` : "Not evaluated"}</strong><small>{inspection?.image_quality.issues[0] ?? "Focus, exposure, contrast and resolution"}</small></div></li>
          <li className={inspection?.yolo_result.model_ready ? "is-complete" : ""}><i>03</i><div><span>YOLO CLASSIFIER - EVIDENCE ONLY</span><strong>{inspection ? `${conditionLabel(label)} · ${percent(confidence)}` : "Model waiting"}</strong><small>{inspection?.geometry_result?.capture_source === "camera" ? "Live-camera transfer is not validated" : inspection?.yolo_result.model_version ?? "Local three-class model"}</small></div></li>
          <li className={inspection ? "is-complete" : ""}><i>04</i><div><span>DECISION ENGINE</span><strong>{inspection?.decision.disposition ?? "No decision"}</strong><small>{inspection?.decision.reasons[0] ?? "Quality + confidence thresholds"}</small></div></li>
          <li className={inspection?.decision.needs_vlm ? "is-active" : inspection ? "is-skipped" : ""}><i>05</i><div><span>SELECTIVE VLM</span><strong>{inspection?.decision.needs_vlm ? inspection.vlm_result.mode.replaceAll("_", " ").toUpperCase() : "NOT INVOKED"}</strong><small>{inspection?.decision.needs_vlm ? inspection.vlm_result.analysis : "Confident cases remain local"}</small></div></li>
          <li className={inspection?.review_status === "reviewed" ? "is-complete" : inspection ? "is-active" : ""}><i>06</i><div><span>HUMAN AUTHORITY</span><strong>{inspection?.human_decision ?? (inspection ? "CONFIRMATION PENDING" : "WAITING")}</strong><small>Final accept/reject remains with the inspector</small></div></li>
        </ol>
        <div className="trace-footer"><span>PROCESSING LATENCY</span><strong>{Math.round(inspection?.processing_time_ms ?? 0)} ms</strong><small>Local capture-to-recommendation measurement</small></div>
      </aside>
    </section>
  </main>;
}
