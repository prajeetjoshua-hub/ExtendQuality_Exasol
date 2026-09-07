"use client";
import { useCallback, useEffect, useState } from "react";

type Risk = { score: number | null; level: string; trend: string; reason: string; recommended_action: string };
type Analytics = {
  data_source: string;
  overview: Array<{ total: number; accepted: number | null; rejected: number | null; unresolved: number | null }>;
  batches: Array<{ batch_id: string; machine_id: string; total: number; eligible: number; rejected: number; reject_percent: number | null; risk: Risk }>;
  daily: Array<{ batch_id: string; machine_id: string; day: string; total: number; eligible: number; rejected: number; reject_percent: number | null }>;
};
type Health = { status: string; pending: number; message?: string };

export default function ExasolAnalytics({ apiBase, revision }: { apiBase: string; revision: number }) {
  const [source, setSource] = useState("prototype_inspection");
  const [data, setData] = useState<Analytics | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const refresh = useCallback(async (signal?: AbortSignal) => {
    setLoading(true); setError(""); setData(null);
    try {
      const [healthResponse, response] = await Promise.all([
        fetch(`${apiBase}/api/analytics/health`, { signal }),
        fetch(`${apiBase}/api/analytics?source=${source}`, { signal }),
      ]);
      if (signal?.aborted) return;
      if (healthResponse.ok) setHealth(await healthResponse.json());
      if (!response.ok) throw new Error("Exasol analytics unavailable. Check configuration and retry pending records.");
      const payload = await response.json() as Analytics;
      if (!signal?.aborted) setData(payload);
    } catch {
      if (!signal?.aborted) { setData(null); setError("Exasol analytics unavailable. No substitute data is shown."); }
    } finally { if (!signal?.aborted) setLoading(false); }
  }, [apiBase, source]);
  useEffect(() => { const controller = new AbortController(); void refresh(controller.signal); return () => controller.abort(); }, [refresh, revision]);
  async function retry() {
    setLoading(true);
    try {
      const response = await fetch(`${apiBase}/api/analytics/retry`, { method: "POST" });
      if (!response.ok) throw new Error();
      await refresh();
    } catch { setError("Sync failed. Pending records remain in the local queue."); setLoading(false); }
  }
  const overview = data?.overview[0];
  return <section className="analytics-section exasol-section" aria-label="Exasol quality analytics">
    <header><div><p>EXASOL PERSONAL · SQL ANALYTICS</p><h2>Batch Quality Risk</h2></div><span>{loading ? "CHECKING…" : health?.status?.toUpperCase() ?? "UNAVAILABLE"} · {health?.pending ?? "—"} PENDING</span></header>
    <div className="exasol-controls"><label>Data source <select value={source} disabled={loading} onChange={event => setSource(event.target.value)}><option value="prototype_inspection">Real prototype inspections</option><option value="synthetic_demo">Synthetic demonstration data</option></select></label><button className="secondary-button" disabled={loading} onClick={() => void refresh()}>Refresh SQL</button><button className="secondary-button" disabled={loading} onClick={() => void retry()}>Retry pending records</button></div>
    <p className="capture-policy">{source === "synthetic_demo" ? "SYNTHETIC DEMONSTRATION DATA — no factory measurements or model inference." : "PROTOTYPE INSPECTIONS — inspector decisions take precedence after review; original model evidence is retained."}</p>
    {error && <p role="alert" className="error-banner">{error}</p>}
    {overview && <div className="analytics-grid"><article><span>EXASOL RECORDS</span><strong>{overview.total}</strong></article><article><span>ACCEPTED</span><strong>{overview.accepted ?? 0}</strong></article><article><span>REJECTED</span><strong>{overview.rejected ?? 0}</strong></article><article><span>UNRESOLVED</span><strong>{overview.unresolved ?? 0}</strong><small>Excluded from reject-rate denominator</small></article></div>}
    {data && !data.batches.length && <p>No records in this data source. Run an inspection or explicitly seed the synthetic demo.</p>}
    <div className="exasol-batches">{data?.batches.map(batch => <article key={`${batch.batch_id}:${batch.machine_id}`} className="module-card"><h3>{batch.batch_id} · {batch.machine_id}</h3><p><strong>{batch.risk.level.replaceAll("_", " ")}</strong> · {batch.risk.score === null ? "No score" : `${batch.risk.score}/100 rule-based score`}</p><p>{batch.rejected}/{batch.eligible} terminal decisions rejected · trend: {batch.risk.trend.replaceAll("_", " ")}</p><p>{batch.risk.reason}</p><p><strong>Next action:</strong> {batch.risk.recommended_action}</p></article>)}</div>
    {!!data?.daily.length && <details><summary>Inspect daily SQL evidence</summary><div className="exasol-table"><table><thead><tr><th>UTC date</th><th>Batch</th><th>Machine</th><th>Eligible</th><th>Rejected</th></tr></thead><tbody>{data.daily.map(row => <tr key={`${row.day}:${row.batch_id}:${row.machine_id}`}><td>{String(row.day).slice(0,10)}</td><td>{row.batch_id}</td><td>{row.machine_id}</td><td>{row.eligible}</td><td>{row.rejected}</td></tr>)}</tbody></table></div></details>}
    <p className="capture-policy">Descriptive triage only. No remaining-life estimate, calibrated failure probability, or verified factory defect rate. Repeated views of one component are not independent samples.</p>
  </section>;
}
