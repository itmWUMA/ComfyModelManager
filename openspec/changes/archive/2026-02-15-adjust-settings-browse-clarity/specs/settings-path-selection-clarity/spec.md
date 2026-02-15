## ADDED Requirements

### Requirement: Path fields are clearly labeled
The settings UI SHALL present distinct labels for each path field so users can identify the intended path type before interacting with browse controls.

#### Scenario: Labels visible on load
- **WHEN** the settings screen is opened
- **THEN** each path field displays a unique label that states the expected path type

### Requirement: Browse actions communicate expected path type
Each browse button SHALL indicate the expected selection type (file or directory) through nearby helper text or inline description.

#### Scenario: Helper text clarifies selection
- **WHEN** the user views a browse button
- **THEN** the UI shows helper text that states whether a file or directory should be selected

### Requirement: Selected path is bound to the correct field
The system SHALL associate each browse action with its corresponding field and display the selected path in that field immediately after selection.

#### Scenario: Selection populates the correct field
- **WHEN** the user selects a path via a browse button
- **THEN** the selected path appears in the corresponding field and not in any other field

### Requirement: Path validation provides immediate feedback
After a selection, the system SHALL validate that the chosen path matches the expected type and display a clear error if it does not.

#### Scenario: Invalid path type is rejected
- **WHEN** the user selects a file for a directory-only field (or vice versa)
- **THEN** the UI displays a validation error indicating the required path type and keeps the field editable for correction
