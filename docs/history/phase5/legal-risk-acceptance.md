# Phase 5 legal risk acceptance

Recorded: 2026-09-01 · Authority: Matthieu Carré, event owner

## Decision

The event owner accepts the exact frozen Phase 5 SBOM inventory for this event release without
package-level licence conclusions. The reference packages and libraries are globally acceptable
for the event. Scanner `NOASSERTION` values and corresponding-source uncertainty remain recorded
and are accepted release risks because the event date is close.

This decision does not assert that every dependency received individual legal analysis or that
every redistribution obligation was independently proved complete.

## Exact scope

| Record | Value |
|---|---:|
| Packages | 2,135 |
| Risk-accepted unresolved records | 2,135 |
| Scanner `NOASSERTION` records | 1,098 |
| Archived licence artifacts | 8 |
| Archived source artifacts | 4 |
| Review SHA-256 | `e8d7ecd92dd405b72e281fcb3722fd4f2d8d60dde8d11eef1ed6688eac94cb5e` |
| Notices SHA-256 | `adc2b9654dd4dcdeff3a68de04e74533659fd97b158f2dc467edc170071a5c15` |
| Approval SHA-256 | `07068b0924c89558b4e90b4faade5241ca8b54bfebbe7c618b9788e4b1af5468` |

The approval identity is `human-event-owner-phase5-legal-risk-2026-09-01`. The approval document
binds the exact review, notices, eight licence artifacts, and four source archives. The original
package-level pending review and notice draft were preserved outside git for traceability.

## Consequence

The package-by-package legal gate is replaced for this release by explicit global risk acceptance.
The release tooling must preserve the nonzero unresolved count and must describe the decision as
`risk-accepted`, never as package-level approval. The remaining #48 work is the declaration, two
byte-identical real builds, and the fresh offline audit.
