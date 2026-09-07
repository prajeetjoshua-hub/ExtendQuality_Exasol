# Product direction — 7 September 2026

This clarification supersedes bearing predictive-maintenance positioning in earlier planning documents. It records user-reported industry feedback, not a completed product migration.

The original bearing prototype demonstrates an image-inspection workflow. Industry experts pointed out that a bearing may look acceptable yet fail to rotate properly: visual appearance alone cannot establish functional bearing quality. The intended next application is a product whose selected quality characteristics can be inspected statically.

In the project conversation Refine Inspection Strategy, the team reported feedback from 3–4 industry experts and discussed injection-moulded parts, plastic caps/closures, rubber seals/gaskets and stamped components. No final product family has been selected. Manufacturer outreach and an industrial visit were proposed to establish actual defects, drawings, tolerances and inspection requirements.

The intended direction includes controlled imaging, product-specific visual checks, calibrated dimensional checks against approved specifications, and eventual automatic acceptance/rejection with a physical mechanism. Routine automation is a goal; an 80/20 automation split is not a measured result. Neither dimensional metrology nor physical rejection is implemented in the current software.

The reusable foundation is capture, image-quality checks, inference orchestration, decision recording, dashboard and Exasol analytics. Bearing model weights and labels do not transfer to another product without new data, rules and validation. The current human-review behavior remains unchanged until a validated replacement is implemented.

Exasol currently supports inspection traceability, inspector decisions, batch summaries and descriptive quality trends. It does not establish rotational health, remaining useful life or a validated failure prediction. Present the bearing demonstration as historical proof of the workflow, and the static-product application as the planned direction.

Keep the Exasol project separate from the existing ExtendQuality repository. The user reports that extending the existing prototype is permitted for the idea submission; this is user-provided clarification rather than independent written organizer verification.
