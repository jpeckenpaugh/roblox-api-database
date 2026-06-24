# Roblox API Database

A git-tracked database of official Roblox Client and Studio API dumps. Designed for offline engine schema lookup, static analysis, and programmatic validation in CI/CD pipelines.

---

> [!IMPORTANT]
> **AI Agent Directive:** Do NOT attempt to read `current/roblox_api_dump.json` directly. The file is over 4MB and contains hundreds of thousands of lines of schema, which will instantly overload your token context window. Always use `./tools/query_api.py` or `./tools/validate_api.py` to query or validate the specific class or enum you need.

---

## 1. Directory Structure

```
roblox-api-database/
├── versions/
│   ├── YYYY-MM-DD-HH-mm-ss.json  # Semantic, timestamped API dump files
│   └── ...
├── current/
│   └── roblox_api_dump.json      # Relative symlink pointing to the latest version JSON
├── tools/
│   ├── fetch_api_dump.sh         # Executable CLI to fetch/update dump
│   ├── fetch_api_dump.py         # Python fetch and normalization logic
│   ├── query_api.py              # Executable CLI query lookup script
│   └── validate_api.py           # Executable CLI validation and linting script
├── README.md                     # This file
└── .gitignore
```

---

## 2. Setup & Installation

The tools are lightweight and self-contained. They require only **Python 3.x** and standard library modules (`sys`, `json`, `os`, `urllib.request`, `datetime`, `re`). No external `pip` packages or virtual environments are required.

To add this database as a submodule to your project:
```bash
git submodule add git@github.com:jpeckenpaugh/roblox-api-database.git docs/api-database
```

---

## 3. Usage

### A. Updating the Database (CI/CD / Manual)
To fetch the latest API dump from the official Roblox CDN endpoints:
```bash
./tools/fetch_api_dump.sh
```

**Semantic Comparison Logic:**
To prevent repository bloat, the download script normalizes the downloaded JSON (sorting enums, classes, and members alphabetically) and compares it against the active version. If no actual semantic engine API changes have occurred, the update is skipped and no file is committed.

---

### B. Querying the Database

#### Class Queries (Properties, Methods, Events)
To inspect the member properties, functions, and events of any Roblox class (including members inherited from parent classes):
```bash
./tools/query_api.py class <ClassName>
```

**Example:** Check all available properties of the `SurfaceGui` class:
```bash
./tools/query_api.py class SurfaceGui
```

#### Enum Queries
To list all available key-value pairs belonging to a Roblox Enum group:
```bash
./tools/query_api.py enum <EnumName>
```

**Example:** Check all valid keys and values for the `Material` Enum:
```bash
./tools/query_api.py enum Material
```

---

### C. Validating API Structures (Static Analysis & Linting)

Use `validate_api.py` to programmatically lint Lua codebases or configuration files against the active Roblox API dump.

#### 1. Property Set Validation
Validate whether a specific set of properties and value types are valid for a Roblox Class:
```bash
./tools/validate_api.py properties <ClassName> '<json_properties>'
```

**Example:** Validate whether `Obsidian` is a valid Material for a `Part`:
```bash
./tools/validate_api.py properties Part '{"Material": "Obsidian"}'
# Error: Invalid value 'Obsidian' for property 'Material' (Enum: Material).
```

#### 2. Size and Constraint Checking
Check if an instantiated class object conforms to sizing and geometry limitations:
```bash
./tools/validate_api.py class Part '{"Size": [4, 2500, 4]}'
# Error: Invalid Size dimension '2500'. Roblox size dimensions must be <= 2048 studs.
```

#### 3. Codebase Directory Scanning (Pre-commit / CI Linting)
Scan a directory of `.lua` source code files to verify that all `Enum` values and `Instance.new("Class")` strings are valid Roblox API structures:
```bash
./tools/validate_api.py scan_src <path_to_directory>
```

**Example:**
```bash
./tools/validate_api.py scan_src ./src
```
