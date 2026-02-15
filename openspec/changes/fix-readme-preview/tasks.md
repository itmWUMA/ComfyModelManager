## 1. Investigate README preview resolution

- [x] 1.1 Trace README preview lookup flow and confirm which data directory path is used
- [x] 1.2 Capture current preview states and where "README not found" is emitted
- [x] 1.3 Document which README filename(s) and locations are considered

## 2. Align preview checks with downloaded data

- [x] 2.1 Update README availability check to use downloaded data directory contents
- [x] 2.2 Add "downloaded but README not located" preview state
- [x] 2.3 Surface diagnostics showing last-checked README path

## 3. Validate behavior

- [ ] 3.1 Verify README renders when present in downloaded data (pending re-test)
- [ ] 3.2 Verify missing README shows the new state with diagnostics (pending re-test)
- [ ] 3.3 Confirm unchanged behavior for non-README preview states (pending re-test)
