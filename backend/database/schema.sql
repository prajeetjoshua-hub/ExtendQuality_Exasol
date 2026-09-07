CREATE SCHEMA IF NOT EXISTS {schema!q};
CREATE TABLE IF NOT EXISTS {schema!q}.INSPECTIONS (
    inspection_id VARCHAR(64) NOT NULL,
    component_id VARCHAR(80) NOT NULL,
    component_type VARCHAR(50) NOT NULL,
    batch_id VARCHAR(80) NOT NULL,
    machine_id VARCHAR(80) NOT NULL,
    observed_at TIMESTAMP NOT NULL,
    data_source VARCHAR(30) NOT NULL,
    disposition VARCHAR(20) NOT NULL,
    model_label VARCHAR(100) NOT NULL,
    model_confidence DOUBLE,
    image_quality_score DOUBLE NOT NULL,
    model_version VARCHAR(200) NOT NULL,
    vlm_mode VARCHAR(40) NOT NULL,
    vlm_summary VARCHAR(4000) NOT NULL,
    processing_time_ms DOUBLE NOT NULL,
    PRIMARY KEY (inspection_id)
);
CREATE TABLE IF NOT EXISTS {schema!q}.HUMAN_REVIEWS (
    inspection_id VARCHAR(64) NOT NULL PRIMARY KEY,
    decision VARCHAR(20) NOT NULL,
    reviewed_at TIMESTAMP NOT NULL
);
CREATE OR REPLACE VIEW {schema!q}.EFFECTIVE_INSPECTIONS AS
SELECT i.inspection_id, i.component_id, i.component_type, i.batch_id, i.machine_id,
       i.observed_at, i.data_source, COALESCE(r.decision,i.disposition) AS disposition,
       i.disposition AS original_disposition, r.decision AS human_decision,
       i.model_label, i.model_confidence, i.image_quality_score,
       i.model_version, i.vlm_mode, i.vlm_summary, i.processing_time_ms
FROM {schema!q}.INSPECTIONS i LEFT JOIN {schema!q}.HUMAN_REVIEWS r ON i.inspection_id=r.inspection_id;
CREATE OR REPLACE VIEW {schema!q}.DAILY_QUALITY AS
SELECT data_source, batch_id, machine_id, CAST(observed_at AS DATE) AS "day",
       COUNT(*) AS total,
       SUM(CASE WHEN disposition IN ('ACCEPT','REJECT') THEN 1 ELSE 0 END) AS eligible,
       SUM(CASE WHEN disposition='REJECT' THEN 1 ELSE 0 END) AS rejected
FROM {schema!q}.EFFECTIVE_INSPECTIONS
GROUP BY data_source, batch_id, machine_id, CAST(observed_at AS DATE);
