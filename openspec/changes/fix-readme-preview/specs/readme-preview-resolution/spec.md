## ADDED Requirements

### Requirement: Preview resolves README from downloaded data
The preview UI MUST determine README availability by checking the downloaded data directory contents for the selected model asset.

#### Scenario: README exists in downloaded data
- **WHEN** the selected model has been downloaded and a README file exists in its data directory
- **THEN** the preview MUST show the README as available and render its contents

#### Scenario: README missing from downloaded data
- **WHEN** the selected model has been downloaded but no README file exists in its data directory
- **THEN** the preview MUST show a "downloaded but README not located" state

### Requirement: Preview exposes README check diagnostics
The preview UI MUST expose diagnostics that indicate which README path(s) were checked during preview resolution.

#### Scenario: README diagnostics available
- **WHEN** the preview checks for README availability
- **THEN** the UI MUST surface the last-checked README path in diagnostics
