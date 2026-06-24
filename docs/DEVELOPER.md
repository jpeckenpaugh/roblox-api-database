# Roblox API Database — Developer Guide

This document is intended for developers and maintainers of the `roblox-api-database` utility suite. It details how the testing suite is structured, how to run tests, and how to extend the validation engine.

---

## 1. Running Unit Tests

The test suite is built using Python's standard `unittest` module, requiring zero external dependencies or virtual environments.

To execute the test suite from the repository root:
```bash
python3 -m unittest tools/test_tools.py
```

### Expected Output:
```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.003s

OK
```

---

## 2. Test Architecture & Mocks

To ensure the tests are fast, stable, and independent of external CDN updates, `tools/test_tools.py` uses a lightweight, self-contained mock database definition:

```python
self.mock_db = {
    "Classes": [
        {
            "Name": "Part",
            "Superclass": "BasePart",
            "Members": [ ... ]
        }
    ],
    "Enums": [
        {
            "Name": "Material",
            "Items": [ ... ]
        }
    ]
}
```

This mock structure is passed directly into the validation functions (`validate_properties`, `validate_class_constraints`, and `scan_lua_directory`) during setup.

---

## 3. Extending the Validation Engine (`tools/validate_api.py`)

When modifying the validation scripts:
1. **Case Insensitivity:** Ensure all lookups are case-insensitive. Dictionary keys should be matched in `.lower()` format to prevent casing discrepancies from causing false failures in Lua scripts.
2. **Roblox Sizing & Physics Constraints:** Standard constraints (like part dimensions or coordinate limits) can be appended directly within the `validate_class_constraints` function.
3. **Allowlist Management:** If a valid Roblox class is missing from the CDN JSON dump (such as `UnreliableRemoteEvent`), append its lowercase class name to `CLASS_ALLOWLIST` in `tools/validate_api.py`.
