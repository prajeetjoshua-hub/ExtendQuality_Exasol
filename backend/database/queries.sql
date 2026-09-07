-- name: overview
SELECT COUNT(*) AS total,
SUM(CASE WHEN disposition='ACCEPT' THEN 1 ELSE 0 END) AS accepted,
SUM(CASE WHEN disposition='REJECT' THEN 1 ELSE 0 END) AS rejected,
SUM(CASE WHEN disposition NOT IN ('ACCEPT','REJECT') THEN 1 ELSE 0 END) AS unresolved,
AVG(image_quality_score) AS average_image_quality,
AVG(processing_time_ms) AS average_processing_time_ms
FROM {schema!q}.EFFECTIVE_INSPECTIONS
WHERE data_source={source} AND ({batch} IS NULL OR batch_id={batch});
-- name: batches
SELECT batch_id, machine_id, COUNT(*) AS total,
SUM(CASE WHEN disposition IN ('ACCEPT','REJECT') THEN 1 ELSE 0 END) AS eligible,
SUM(CASE WHEN disposition='REJECT' THEN 1 ELSE 0 END) AS rejected,
100.0*SUM(CASE WHEN disposition='REJECT' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN disposition IN ('ACCEPT','REJECT') THEN 1 ELSE 0 END),0) AS reject_percent
FROM {schema!q}.EFFECTIVE_INSPECTIONS
WHERE data_source={source} AND ({batch} IS NULL OR batch_id={batch})
GROUP BY batch_id, machine_id ORDER BY reject_percent DESC NULLS LAST, batch_id, machine_id;
-- name: daily
SELECT batch_id, machine_id, "day", total, eligible, rejected,
100.0*rejected/NULLIF(eligible,0) AS reject_percent
FROM {schema!q}.DAILY_QUALITY
WHERE data_source={source} AND ({batch} IS NULL OR batch_id={batch})
ORDER BY "day", batch_id, machine_id;
-- name: categories
SELECT model_label, disposition, COUNT(*) AS total FROM {schema!q}.EFFECTIVE_INSPECTIONS
WHERE data_source={source} AND ({batch} IS NULL OR batch_id={batch})
GROUP BY model_label, disposition ORDER BY total DESC;
-- name: history
SELECT inspection_id, component_id, batch_id, machine_id, observed_at, disposition,
model_label, model_confidence, image_quality_score, vlm_mode
FROM {schema!q}.EFFECTIVE_INSPECTIONS
WHERE data_source={source} AND ({batch} IS NULL OR batch_id={batch})
ORDER BY observed_at DESC, inspection_id LIMIT 100;
