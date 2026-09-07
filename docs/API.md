# API reference

Base URL in the default local setup: `http://127.0.0.1:8000`. Interactive OpenAPI documentation: `/docs`.

| Method | Path | Behavior |
|---|---|---|
| GET | `/api/analytics/health` | Exasol connectivity and local queue counts |
| GET | `/api/analytics?source=synthetic_demo` | SQL overview, batches, dates, categories and history for synthetic records |
| GET | `/api/analytics?source=prototype_inspection` | SQL analytics for captured inspections |
| GET | `/api/analytics?source=prototype_inspection&batch=YOUR-BATCH` | Optional batch filter |
| POST | `/api/analytics/retry` | Retry at most 100 pending inspections and 100 review events |
| POST | `/api/inspections` | Multipart image upload; supports batch, machine and optional component identity |
| GET | `/api/inspections/{id}` | Local evidence, original disposition and current disposition |
| POST | `/api/inspections/{id}/review` | JSON decision ACCEPT or REJECT, with a reason |

Example review body:

```json
{"decision": "ACCEPT", "reason": "Inspector checked the visible condition"}
```

Use the generated OpenAPI schema for the complete upload fields and response types. `exasol_status` reports whether delivery succeeded or remains pending; an inspection stored locally is not automatically confirmed as saved in Exasol.

## Failure semantics

An unavailable Exasol query returns HTTP 503; the connection-health endpoint reports an unavailable state. Unsupported sources return validation errors. The service never replaces failed SQL results with synthetic rows. The browser clears stale analytical results on failure.

This is a local single-operator application without production authentication. Keep API bindings on loopback. Do not expose it publicly as a production service.
