# Security

This is a local single-operator prototype, not an authenticated production service. Keep the API and database on loopback. For remote deployment, add authentication, authorization, a least-privilege database user and verified TLS before exposing endpoints.

Store secrets only in ignored environment files or a suitable secret store. `NEXT_PUBLIC_` values are bundled into frontend code and must never contain secrets. The explicit insecure TLS option is limited to loopback development hosts.

For security findings, contact the repository owner privately through an available GitHub contact channel. Do not post credentials, private images or sensitive logs in public issues. If a secret is exposed, revoke/rotate it; removing a file alone does not remove it from history.

## Dependency audit — 7 September 2026

The submission packaging updated compatible React, Next.js, Vite and Cloudflare packages and refreshed transitive dependencies. `npm audit` reports 6 remaining findings (2 high, 4 moderate), not zero:

- `image-size`, through inherited `vinext`, has malformed-image denial-of-service advisories [ICNS](https://github.com/advisories/GHSA-w3rx-r6r6-pgpr) and [JXL/HEIF](https://github.com/advisories/GHSA-5p2g-fcmc-qvqq). The suggested dependency replacement requires a vinext beta migration, not a routine patch of the current framework.
- `drizzle-kit` and its legacy loader chain retain an [esbuild development-server advisory](https://github.com/advisories/GHSA-67mh-4wv8-2f99). D1 schema-generation tooling is inherited scaffolding, separate from the Exasol application path.

Keep this prototype local. These findings need a tested framework/tooling migration before a production deployment; local build success does not resolve them. The repository is public source, not a publicly hosted inspection service.
