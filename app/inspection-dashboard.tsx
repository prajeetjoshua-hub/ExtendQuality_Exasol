"use client";
/* eslint-disable @next/next/no-img-element -- webcam blobs and local FastAPI artifacts are runtime-only URLs */

import { type ChangeEvent, type CSSProperties, useCallback, useEffect, useRef, useState } from "react";
import ExasolAnalytics from "./exasol-analytics";

type InspectionResult = {
  exasol_status?: string;
  id: string;
  capture_source: "upload" | "camera";
  status: "ACCEPT" | "REJECT" | "RECAPTURE" | "REVIEW" | "SYSTEM_HOLD";
  image_quality: { score: number; blur_score: number; exposure_score: number; contrast_score: number; width: number; height: number; issues: string[] };
  vision_result: { mode: "yolo" | "yolo_classifier" | "opencv_contour_fallback"; model_ready: boolean; model_version: string; detections: Array<{ label: string; confidence: number; box: number[] }>; classification: { label: string; confidence: number; probabilities: Record<string, number> } | null; note: string };
  decision: { disposition: string; score: number; needs_vlm: boolean; reasons: string[] };
  vlm_result: { invoked: boolean; mode: "not_required" | "gemini" | "offline_fallback" | "not_configured"; analysis: string; recommendation: string; disclaimer: string };
  artifacts: { processed: string; overlay: string };
  review_status: string;
  processing_time_ms: number;
};

type InspectionRecord = {
  id: string; created_at: string; bearing_type: string; status: InspectionResult["status"];
  review_status: string; human_decision: string | null; processing_time_ms: number;
  yolo_result: InspectionResult["vision_result"] | null;
};

type InspectionSummary = {
  total: number; status_counts: Record<InspectionResult["status"], number>;
  class_counts: Record<string, number>; reviewed: number; pending_review: number;
  average_processing_time_ms: number;
};

type SystemStatus = { vlm_provider: string; vlm_configured: boolean };

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const percentage = (value?: number) => value === undefined ? "--" : `${Math.round(value * 100)}%`;
const conditionLabel = (label?: string) => label === "rust" ? "SURFACE CONDITION (RUST / GREASE)" : label === "displaced" ? "ABNORMAL BALL ARRANGEMENT" : label?.toUpperCase() ?? "UNVERIFIED";

export default function InspectionDashboard() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const captureUrlRef = useRef<string | null>(null);
  const [bearingType, setBearingType] = useState("6204");
  const [batchId, setBatchId] = useState("UNASSIGNED");
  const [machineId, setMachineId] = useState("UNASSIGNED");
  const [componentId, setComponentId] = useState("");
  const [analyticsRevision, setAnalyticsRevision] = useState(0);
  const [reviewBusy, setReviewBusy] = useState(false);
  const [capture, setCapture] = useState<{ blob: Blob; url: string; name: string; source: "upload" | "camera" } | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraDevices, setCameraDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState("");
  const [cameraZoom, setCameraZoom] = useState(1);
  const [result, setResult] = useState<InspectionResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [reviewMessage, setReviewMessage] = useState("");
  const [summary, setSummary] = useState<InspectionSummary | null>(null);
  const [history, setHistory] = useState<InspectionRecord[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  const refreshAnalytics = useCallback(async () => {
    try {
      const [summaryResponse, historyResponse, healthResponse] = await Promise.all([
        fetch(`${API_BASE}/api/inspections/summary`),
        fetch(`${API_BASE}/api/inspections?limit=8`),
        fetch(`${API_BASE}/api/health`),
      ]);
      if (summaryResponse.ok) setSummary(await summaryResponse.json() as InspectionSummary);
      if (historyResponse.ok) setHistory(await historyResponse.json() as InspectionRecord[]);
      if (healthResponse.ok) setSystemStatus(await healthResponse.json() as SystemStatus);
    } catch {
      // Core inspection remains usable if analytics are temporarily unavailable.
    }
  }, []);

  useEffect(() => {
    void refreshAnalytics();
    const handleDeviceChange = () => { void refreshCameras(); };
    navigator.mediaDevices?.addEventListener?.("devicechange", handleDeviceChange);
    return () => {
      navigator.mediaDevices?.removeEventListener?.("devicechange", handleDeviceChange);
      streamRef.current?.getTracks().forEach((track) => track.stop());
      if (captureUrlRef.current) URL.revokeObjectURL(captureUrlRef.current);
    };
  }, [refreshAnalytics]);

  async function refreshCameras() {
    if (!navigator.mediaDevices?.enumerateDevices) return;
    const devices = (await navigator.mediaDevices.enumerateDevices()).filter((device) => device.kind === "videoinput");
    setCameraDevices(devices);
    if (!selectedCameraId && devices[0]) setSelectedCameraId(devices[0].deviceId);
  }

  function replaceCapture(blob: Blob, name: string, source: "upload" | "camera") {
    if (captureUrlRef.current) URL.revokeObjectURL(captureUrlRef.current);
    const url = URL.createObjectURL(blob);
    captureUrlRef.current = url;
    setCapture({ blob, name, url, source });
    setResult(null);
    setReviewMessage("");
    setError("");
  }

  function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) replaceCapture(file, file.name, "upload");
  }

  async function startCamera() {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1920 }, height: { ideal: 1080 }, ...(selectedCameraId ? { deviceId: { exact: selectedCameraId } } : { facingMode: "environment" }) }, audio: false });
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraActive(true);
      const devices = (await navigator.mediaDevices.enumerateDevices()).filter((device) => device.kind === "videoinput");
      setCameraDevices(devices);
      const activeId = stream.getVideoTracks()[0]?.getSettings().deviceId;
      if (activeId) setSelectedCameraId(activeId);
    } catch {
      setError("Camera access was unavailable. Allow camera permission or upload an image instead.");
    }
  }

  function stopCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setCameraActive(false);
  }

  function captureFrame() {
    const video = videoRef.current;
    if (!video?.videoWidth) return setError("The camera is still starting. Wait a moment and capture again.");
    const canvas = document.createElement("canvas");
    const sourceWidth = video.videoWidth / cameraZoom;
    const sourceHeight = video.videoHeight / cameraZoom;
    const sourceX = (video.videoWidth - sourceWidth) / 2;
    const sourceY = (video.videoHeight - sourceHeight) / 2;
    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    canvas.getContext("2d")?.drawImage(video, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => { if (blob) replaceCapture(blob, `bearing-${Date.now()}.jpg`, "camera"); }, "image/jpeg", 0.94);
  }

  async function inspectBearing() {
    if (!capture) return setError("Capture a camera frame or choose a bearing image first.");
    setBusy(true); setError(""); setResult(null); setReviewMessage("");
    const form = new FormData();
    form.append("image", capture.blob, capture.name);
    form.append("bearing_type", bearingType.trim() || "6204");
    form.append("capture_source", capture.source);
    form.append("batch_id", batchId.trim() || "UNASSIGNED");
    form.append("machine_id", machineId.trim() || "UNASSIGNED");
    form.append("component_id", componentId.trim());
    try {
      const response = await fetch(`${API_BASE}/api/inspections`, { method: "POST", body: form });
      const payload = await response.json() as InspectionResult & { detail?: string };
      if (!response.ok) throw new Error(payload.detail || `Inspection failed (${response.status}).`);
      setResult(payload as InspectionResult);
      setAnalyticsRevision(value => value + 1);
      void refreshAnalytics();
    } catch (cause) {
      setError(cause instanceof TypeError ? "Cannot reach the backend. Keep FastAPI running on port 8000." : cause instanceof Error ? cause.message : "Inspection failed.");
    } finally { setBusy(false); }
  }

  async function submitReview(decision: "ACCEPT" | "REJECT") {
    if (!result || reviewBusy) return;
    const reviewedId = result.id;
    setReviewBusy(true);
    setReviewMessage("Saving inspector decision…");
    try {
      const response = await fetch(`${API_BASE}/api/inspections/${result.id}/review`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ decision, reason: "Confirmed from inspector dashboard" }) });
      if (!response.ok) throw new Error();
      const reviewed = await response.json() as { status: "ACCEPT" | "REJECT"; exasol_status: string };
      setResult(current => current?.id === reviewedId ? { ...current, status: reviewed.status, review_status: "reviewed", exasol_status: reviewed.exasol_status } : current);
      setAnalyticsRevision(value => value + 1);
      setReviewMessage(`Inspector marked this bearing ${decision}.`);
      void refreshAnalytics();
    } catch { setReviewMessage("Could not save the review. Check the backend connection."); }
    finally { setReviewBusy(false); }
  }

  const overlayUrl = result ? `${API_BASE}${result.artifacts.overlay}` : null;
  const statusClass = result ? `decision decision--${result.status.toLowerCase()}` : "decision";
  const statusOrder: InspectionResult["status"][] = ["ACCEPT", "REJECT", "REVIEW", "RECAPTURE", "SYSTEM_HOLD"];
  const recentTrend = [...history].reverse();
  const maxProcessingTime = Math.max(1, ...recentTrend.map((item) => item.processing_time_ms));

  return <main className="app-shell">
    <aside className="sidebar" aria-label="Dashboard navigation">
      <div className="brand-mark" aria-label="EXtendQuality"><span>EX</span><i /></div>
      <nav className="side-nav"><span className="nav-section">INSPECTION</span><button className="nav-item nav-item--active" type="button"><span className="nav-grid"><i/><i/><i/><i/></span><span>Live inspection</span></button><a className="nav-item" href="/inspection-visualizer"><span className="nav-clock"/><span>Visual trace</span><small>LIVE</small></a></nav>
      <div className="sidebar-foot"><span className="pulse-dot"/><div><strong>LINE 04</strong><span>Prototype mode</span></div></div>
    </aside>
    <section className="workspace">
      <header className="topbar"><div className="wordmark"><span>EX</span>tendQuality<small>INTELLIGENT INSPECTION SYSTEM</small></div><div className="topbar-meta"><span className="system-tag"><i/> {systemStatus?.vlm_configured ? "GEMINI READY" : "LOCAL FALLBACK READY"}</span><span className="operator">EQ</span></div></header>
      <div className="content">
        <section className="hero-row"><div><p className="kicker"><span>QUALITY CONTROL</span> / BEARING MANUFACTURING</p><h1>Inspection intelligence,<br/><em>now connected.</em></h1></div><div className={statusClass}><span>CURRENT DISPOSITION</span><strong>{result?.status ?? "AWAITING CAPTURE"}</strong><small>{result ? `${result.processing_time_ms} ms processing` : "OpenCV · YOLO · Decision · VLM"}</small></div></section>
        <section className="control-strip" aria-label="Batch identity"><label className="bearing-field"><span>BATCH ID</span><input value={batchId} onChange={event => setBatchId(event.target.value)} maxLength={80}/></label><label className="bearing-field"><span>MACHINE ID</span><input value={machineId} onChange={event => setMachineId(event.target.value)} maxLength={80}/></label><label className="bearing-field"><span>COMPONENT ID (OPTIONAL)</span><input value={componentId} onChange={event => setComponentId(event.target.value)} maxLength={80}/></label></section><section className="control-strip" aria-label="Inspection controls">
          <label className="bearing-field"><span>BEARING TYPE</span><input value={bearingType} onChange={(event) => setBearingType(event.target.value)} maxLength={50}/></label>
          <label className="upload-button"><input type="file" accept="image/jpeg,image/png,image/webp" onChange={chooseFile}/><span>Choose image</span></label>
          <label className="camera-device-field"><span>CAMERA SOURCE</span><select value={selectedCameraId} onChange={(event) => { stopCamera(); setSelectedCameraId(event.target.value); }}><option value="">Default camera</option>{cameraDevices.map((device,index) => <option value={device.deviceId} key={device.deviceId}>{device.label || `Camera ${index + 1}`}</option>)}</select></label>
          <label className="camera-zoom-field"><span>CAPTURE ZOOM</span><input type="range" min="1" max="3" step="0.1" value={cameraZoom} onChange={(event) => setCameraZoom(Number(event.target.value))}/><b>{cameraZoom.toFixed(1)}×</b></label>
          {!cameraActive ? <button className="secondary-button" type="button" onClick={startCamera}>Start selected camera</button> : <><button className="secondary-button phone-capture-button" type="button" onClick={captureFrame}>Capture phone frame</button><button className="text-button" type="button" onClick={stopCamera}>Stop</button></>}
          <button className="inspect-button" type="button" onClick={inspectBearing} disabled={busy}>{busy ? "Processing…" : "Run inspection"}<i/></button>
        </section>
        <p className="capture-policy"><strong>CONNECTED PHONE CAMERA:</strong> enable it in Windows, select it above, then start and capture entirely from this laptop. Live captures start in review; your Accept or Reject decision updates the final status.</p>
        {capture?.source === "camera" && <div className="camera-safety-banner" role="status"><strong>LIVE CAMERA - EXPERIMENTAL</strong><span>The model has not been validated on this camera setup. Its class is evidence only; usable live captures start in HUMAN REVIEW. Your saved decision sets the final status.</span></div>}
        {error && <div className="error-banner" role="alert"><strong>Action needed</strong><span>{error}</span></div>}
        <section className="module-grid" aria-label="Inspection modules">
          <article className="module-card camera-card"><header><span className="module-number">01</span><div><p>VISION CELL</p><h2>Camera Feed</h2><small>OpenCV preprocessing + classification overlay</small></div><span className="live-chip">{cameraActive ? "LIVE" : capture ? "FRAME READY" : "STANDBY"}</span></header><div className="vision-stage"><video ref={videoRef} autoPlay muted playsInline className={cameraActive ? "" : "is-hidden"}/>{!cameraActive && overlayUrl && <img src={overlayUrl} alt="Bearing inspection overlay"/>}{!cameraActive && !overlayUrl && capture && <img src={capture.url} alt="Selected bearing"/>}{!cameraActive && !capture && <div className="empty-vision"><i/><strong>No bearing frame</strong><span>Start the camera or choose an image</span></div>}<div className="reticle" aria-hidden="true"/></div><footer><span>{capture?.name ?? "No capture selected"}</span><strong>{result?.vision_result.classification ? `${conditionLabel(result.vision_result.classification.label)} · ${percentage(result.vision_result.classification.confidence)}` : result ? `${result.vision_result.detections.length} region(s)` : "-- result"}</strong></footer></article>
          <article className="module-card analysis-card"><header><span className="module-number">02</span><div><p>QUALITY INTELLIGENCE</p><h2>Processing Analysis</h2><small>Measured evidence and routing</small></div></header><div className="quality-score"><div><span>IMAGE QUALITY</span><strong>{percentage(result?.image_quality.score)}</strong></div><i style={{ "--score": result?.image_quality.score ?? 0 } as CSSProperties}/></div><dl className="metrics"><div><dt>Sharpness</dt><dd>{percentage(result?.image_quality.blur_score)}</dd></div><div><dt>Exposure</dt><dd>{percentage(result?.image_quality.exposure_score)}</dd></div><div><dt>Contrast</dt><dd>{percentage(result?.image_quality.contrast_score)}</dd></div><div><dt>Resolution</dt><dd>{result ? `${result.image_quality.width} × ${result.image_quality.height}` : "--"}</dd></div></dl>{result?.vision_result.classification && <div className="probability-panel"><span>CLASS EVIDENCE - NOT THE FINAL DECISION</span>{Object.entries(result.vision_result.classification.probabilities).sort((a,b) => b[1] - a[1]).map(([label,value]) => <div key={label}><strong>{conditionLabel(label)}</strong><i style={{ "--score": value } as CSSProperties}/><b>{percentage(value)}</b></div>)}</div>}<div className="model-state"><span className={result?.vision_result.model_ready ? "ready" : "fallback"}/><div><strong>{result ? result.vision_result.model_ready ? "YOLO MODEL ACTIVE" : "OPENCV FALLBACK" : "VISION MODEL"}</strong><p>{result?.vision_result.note ?? "Awaiting an inspection frame."}</p></div></div><ul className="reason-list">{(result?.decision.reasons ?? ["Decision evidence will appear here."]).map((reason) => <li key={reason}>{reason}</li>)}</ul></article>
          <article className="module-card recommendation-card"><header><span className="module-number">03</span><div><p>ACTION LAYER</p><h2>VLM Recommendation</h2><small>Grounded explanation for the inspector</small></div><span className="mode-chip">{result?.vlm_result.mode.replaceAll("_", " ") ?? "WAITING"}</span></header><div className="vlm-copy"><span>ANALYSIS</span><p>{result?.vlm_result.analysis ?? "Run an inspection to generate a grounded analysis."}</p><span>RECOMMENDATION</span><strong>{result?.vlm_result.recommendation ?? "No action recommended yet."}</strong></div>{result && <div className="review-panel"><span>HUMAN-IN-THE-LOOP CONFIRMATION</span><div><button type="button" disabled={reviewBusy} onClick={() => submitReview("ACCEPT")}>Accept bearing</button><button type="button" disabled={reviewBusy} onClick={() => submitReview("REJECT")}>Reject bearing</button></div>{reviewMessage && <p>{reviewMessage}</p>}</div>}<footer>{result?.vlm_result.disclaimer ?? "The VLM layer is invoked only when deterministic evidence is uncertain."}</footer></article>
        </section>
        <section className="analytics-section" aria-label="Inspection analytics">
          <header><div><p>PRODUCTION INTELLIGENCE</p><h2>Inspection Analytics</h2></div><span>{summary?.total ?? 0} RECORDS STORED LOCALLY</span></header>
          <div className="analytics-grid">
            <article><span>TOTAL INSPECTED</span><strong>{summary?.total ?? 0}</strong><small>Captured evidence records</small></article>
            <article><span>ACCEPTED</span><strong>{summary?.status_counts.ACCEPT ?? 0}</strong><small>Inspector decision when reviewed</small></article>
            <article><span>REJECTED</span><strong>{summary?.status_counts.REJECT ?? 0}</strong><small>Inspector decision when reviewed</small></article>
            <article><span>HUMAN REVIEWED</span><strong>{summary?.reviewed ?? 0}</strong><small>{summary?.pending_review ?? 0} pending confirmation</small></article>
            <article><span>AVG PROCESSING</span><strong>{Math.round(summary?.average_processing_time_ms ?? 0)}<i> ms</i></strong><small>Capture-to-decision time</small></article>
          </div>
          <div className="analysis-charts" aria-label="Inspection analysis graphs">
            <article className="outcome-chart"><header><span>DECISION ROUTING</span><small>Current dispositions after human review</small></header><div className="outcome-bars">{statusOrder.map((status) => { const count = summary?.status_counts[status] ?? 0; const share = summary?.total ? count / summary.total : 0; return <div key={status}><b>{count}</b><i style={{ "--share": share } as CSSProperties}/><span>{status.replace("SYSTEM_HOLD", "HOLD")}</span></div>; })}</div></article>
            <article className="trend-chart"><header><span>RECENT MODEL EVIDENCE</span><small>Confidence and processing time are separate signals</small></header>{recentTrend.length ? <div className="trend-plot">{recentTrend.map((item, index) => { const confidence = item.yolo_result?.classification?.confidence ?? 0; return <div className="trend-column" key={item.id} title={`${conditionLabel(item.yolo_result?.classification?.label)}: ${percentage(confidence)}, ${Math.round(item.processing_time_ms)} ms`}><div className="trend-bars"><i className="trend-confidence" style={{ "--value": confidence } as CSSProperties}/><i className="trend-latency" style={{ "--value": item.processing_time_ms / maxProcessingTime } as CSSProperties}/></div><span>{index + 1}</span></div>; })}</div> : <p className="chart-empty">Run inspections to build the evidence trend.</p>}<footer><span><i className="legend-confidence"/>YOLO confidence</span><span><i className="legend-latency"/>Processing time</span></footer></article>
          </div>
          <div className="history-panel">
            <div className="defect-summary"><span>CONDITION DISTRIBUTION</span><div>{Object.entries(summary?.class_counts ?? {}).map(([label, count]) => <p key={label}><strong>{conditionLabel(label)}</strong><i style={{ "--share": summary?.total ? count / summary.total : 0 } as CSSProperties}/><b>{count}</b></p>)}{!Object.keys(summary?.class_counts ?? {}).length && <small>No classified inspections stored yet.</small>}</div></div>
            <div className="recent-history"><span>RECENT INSPECTIONS</span><div className="history-table"><div className="history-head"><b>TIME</b><b>BEARING</b><b>CONDITION</b><b>STATUS</b></div>{history.map((item) => <div className="history-row" key={item.id}><time>{new Date(item.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time><b>{item.bearing_type}</b><span>{conditionLabel(item.yolo_result?.classification?.label)}</span><strong data-status={item.status}>{item.status}</strong></div>)}{!history.length && <small>No inspection history yet. Run the first bearing inspection.</small>}</div></div>
          </div>
        </section>
        {result && <p className="capture-policy" role="status">Exasol save: {result.exasol_status?.replaceAll("_", " ") ?? "not confirmed"} · Original model disposition: {result.decision.disposition}</p>}<ExasolAnalytics apiBase={API_BASE} revision={analyticsRevision}/><footer className="dashboard-footer"><p><span>EXTENDQUALITY / EQ-INSPECT</span> · Local prototype interface</p><div><i/> Images stored locally <i/> Inspector decision recorded</div></footer>
      </div>
    </section>
  </main>;
}
