# Roblox API Database

A git-tracked database of official Roblox Client and Studio API dumps. Designed for offline engine schema lookup, static analysis, and programmatic validation in CI/CD pipelines.

---

> [!IMPORTANT]
> **AI Agent Directive:** Do NOT attempt to read `current/roblox_api_dump.json` directly. The file is over 4MB and contains hundreds of thousands of lines of schema, which will instantly overload your token context window. Always use the CLI tools under `tools/` as documented in [docs/AGENTS.md](docs/AGENTS.md).

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
│   ├── validate_api.py           # Executable CLI validation and linting script
│   └── test_tools.py             # Python unit test suite
├── tests/
│   ├── valid_code_samples/       # Subfolder containing valid Lua code examples
│   └── invalid_code_samples/     # Subfolder containing invalid Lua code examples
├── docs/
│   ├── DEVELOPER.md              # Documentation for testing and internal architecture
│   └── AGENTS.md                 # Context instructions and workflows for AI agents
├── README.md                     # This file
└── .gitignore
```

---

## 2. Setup & Installation

The tools are lightweight and self-contained. They require only **Python 3.x** and standard library modules (`sys`, `json`, `os`, `urllib.request`, `datetime`, `re`, `unittest`). No external `pip` packages or virtual environments are required.

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

---

### B. Querying the Database
Use the bundled Python tool to check class structures, inheritance, and enum values:

**Example: Check all values for a specific Enum:**
```bash
./tools/query_api.py enum Material
```

**Example: Check all properties, methods, and inherited members for a Class:**
```bash
./tools/query_api.py class SurfaceGui
```

For more detailed workflows, refer to the [Agent Guide](docs/AGENTS.md).

---

### C. Running Unit Tests
To run the standard Python unittest suite:
```bash
python3 -m unittest tools/test_tools.py
```

For more details on validator usage and constraints checking, see the [Developer Guide](docs/DEVELOPER.md).
