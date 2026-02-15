## Why

README downloads are succeeding, but the preview UI still reports the README as missing. This breaks the user flow for verifying downloads and makes the preview unreliable.

## What Changes

- Add a capability that ensures the preview UI resolves README availability based on the downloaded data artifacts.
- Update the preview status logic to distinguish "not downloaded" from "downloaded but not located" states.
- Add diagnostics to surface which README file is being checked.

## Capabilities

### New Capabilities
- `readme-preview-resolution`: Resolve README preview state using downloaded data contents and surface precise availability.

### Modified Capabilities
- `settings-path-selection-clarity`: Clarify how preview resolves data paths and README presence for downloaded assets.

## Impact

- Preview UI status messaging and data path resolution logic.
- README download verification path in the data directory.
- Documentation for preview diagnostics.
