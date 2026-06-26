# Roblox API Database — Agent Instructions

This document is the authoritative instruction file for all AI coding agents working on repositories that consume this database submodule.

---

> [!CRITICAL]
> **Token Context Mandate:** You MUST NOT read `current/roblox_api_dump.json` directly. The file is over 4MB and contains hundreds of thousands of lines of schema. Reading it directly will waste your token context window, degrade your reasoning capacity, and inflate execution costs. 
> 
> You MUST use the CLI tools (`./tools/query_api.py` and `./tools/validate_api.py`) to query or validate schemas.

---

## 1. Schema Query Workflow

Before defining interface contracts or writing structural parameters:

### A. Verify Class Structures
Query class properties, methods, events, and inheritance to make sure you use correct names and casing.
```bash
./tools/query_api.py class <ClassName>
```
* **Use Case:** Verify if a property is inherited (e.g. checking if `Part` has `Size` which originates in `BasePart`).

### B. Verify Enums
Query enum groups to get valid key names and values.
```bash
./tools/query_api.py enum <EnumGroupName>
```
* **Use Case:** Check valid keys for `Material`, `NormalId`, or `PartType` to avoid using invalid values (like using `Obsidian` instead of `Slate`).

---

## 2. Validation Workflow (Pre-Flight)

Before staging code changes, run verification tasks to ensure your proposed parameters and script structures match Roblox specifications:

### A. Lint Code Directory
Scan your source directory to catch invalid class creation strings or enum paths:
```bash
./tools/validate_api.py scan_src <path_to_src>
```

### B. Validate Part Instantiation
Verify if a dictionary of proposed properties conforms to Roblox constraints:
```bash
./tools/validate_api.py class <ClassName> '<json_properties>'
```
* **Example:**
  `./tools/validate_api.py class Part '{"Size": [4, 10, 4]}'`
