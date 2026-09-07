# Contributing

Use an isolated branch and explain the behavior being changed. Preserve original inspection evidence, explicit synthetic labels and source separation. New product support requires its own defect definitions, data, acceptance criteria and validation; changing UI labels is not model adaptation.

Run backend tests, the frontend build/rendered tests and TypeScript checks as documented in the README. SQL integration tests require a local Exasol instance and dedicated test schema. Do not use a factory or shared production schema for tests.

Never commit `.env.local`, API keys, database credentials, runtime data or unapproved images/model files. Review staged changes and verify your Git identity before committing. Preserve genuine authorship and third-party notices.

Repository access is managed by the owner. Listing a historical contributor does not grant collaborator access.
