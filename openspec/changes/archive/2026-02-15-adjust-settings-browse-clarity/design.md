## Context

The settings UI exposes two browse buttons for path selection, but the current labels and flow do not make the expected path type clear. Users are unsure which paths to provide, leading to misconfiguration during setup.

## Goals / Non-Goals

**Goals:**
- Make each browse action's intent and required path type explicit at the point of interaction.
- Provide immediate, actionable guidance (labels, helper text, validation) to reduce user confusion.
- Ensure the selected path is clearly associated with the correct setting field.

**Non-Goals:**
- Redesign the entire settings page layout or theming.
- Change underlying storage formats or path persistence behavior.
- Introduce new settings unrelated to path selection clarity.

## Decisions

- Add explicit field labels and concise helper text adjacent to each browse control. This keeps guidance visible without requiring extra clicks, and reduces reliance on external documentation.
- Tie each browse button to a distinct field with clear placeholder examples (e.g., folder vs. file path) so the user can confirm correctness before saving.
- Surface validation feedback immediately after selection to confirm the chosen path matches the expected type (directory vs. file), preventing silent misconfiguration.

## Risks / Trade-offs

- More UI text can add visual noise → Keep helper text short and use subtle styling.
- Validation may block advanced use cases (e.g., atypical paths) → Provide a clear error message and allow correction without losing input.
