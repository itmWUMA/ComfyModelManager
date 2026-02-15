## MODIFIED Requirements

### Requirement: Selected path is bound to the correct field
The system SHALL associate each browse action with its corresponding field and display the selected path in that field immediately after selection.

#### Scenario: Selection populates the correct field
- **WHEN** the user selects a path via a browse button
- **THEN** the selected path appears in the corresponding field and not in any other field

#### Scenario: Preview resolves README from selected data path
- **WHEN** the user selects a data directory path and opens the README preview
- **THEN** the preview MUST check for README presence under the selected data path and show a diagnostic with the checked path
