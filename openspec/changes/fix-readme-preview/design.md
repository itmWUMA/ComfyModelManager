## Context

README files are downloaded into the data directory, but the preview UI checks for README presence using a path resolution flow that can diverge from where downloads land. The preview state currently conflates missing downloads with path mismatches, which leads to a false "README not found" status even when the file exists.

## Goals / Non-Goals

**Goals:**
- Align README preview checks with the actual downloaded data directory layout.
- Surface clear preview states: not downloaded vs downloaded but not located.
- Provide diagnostics that identify which README path was evaluated.

**Non-Goals:**
- Redesign the download workflow or storage layout.
- Introduce new persistent metadata formats for downloads.
- Change unrelated preview UI behavior outside README visibility.

## Decisions

- Use the data directory contents as the source of truth for README availability. This matches download output and avoids mismatches with inferred paths.
  - Alternatives: Derive paths from config only (rejected because config may not reflect actual download location); rely on cached metadata (rejected due to staleness).
- Add a distinct preview state for "downloaded but README not located" with the last-checked path in diagnostics. This improves troubleshooting without changing the underlying download logic.
  - Alternatives: Keep a single "not found" state (rejected because it hides actionable distinctions).
- Keep diagnostics in the UI layer only, derived from preview checks, to avoid cross-module coupling.
  - Alternatives: Introduce a shared logging module (rejected for scope creep).

## Risks / Trade-offs

- Additional filesystem checks may add minor latency in preview refreshes → Mitigation: reuse existing directory scans when possible and avoid repeated checks in the same refresh cycle.
- Users may misinterpret diagnostics as errors → Mitigation: label diagnostics as "checked path" rather than warnings.
