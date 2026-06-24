# Roblox API Database

A git-tracked database of official Roblox Client and Studio API dumps. Designed for offline engine schema lookup, static analysis, and programmatic validation in CI/CD pipelines.

---

> [!IMPORTANT]
> **AI Agent Directive:** Do NOT attempt to read `current/roblox_api_dump.json` directly. The file is over 4MB and contains hundreds of thousands of lines of schema, which will instantly overload your token context window. Always use `./tools/query_api.py` to query only the specific class or enum you need.

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
│   └── query_api.py              # Executable CLI query lookup script
├── README.md                     # This file
└── .gitignore
```

---

## 2. Setup & Installation

The tools are lightweight and self-contained. They require only **Python 3.x** and standard library modules (`sys`, `json`, `os`, `urllib.request`, `datetime`). No external `pip` packages or virtual environments are required.

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

### B. Querying Classes (Properties, Methods, Events)
To inspect the member properties, functions, and events of any Roblox class (including members inherited from parent classes):
```bash
./tools/query_api.py class <ClassName>
```

**Example:** Check all available properties, types, and inherited events of the `SurfaceGui` class:
```bash
./tools/query_api.py class SurfaceGui
```

**Output Snippet:**
```
Class: SurfaceGui
Inheritance: SurfaceGui -> SurfaceGuiBase -> LayerCollector -> GuiBase2d -> GuiBase -> Instance
----------------------------------------
  [Property] Face: NormalId  (Origin: SurfaceGuiBase, Read Security: None)
  [Property] LightInfluence: float  (Origin: SurfaceGui, Read Security: None)
  [Event] Destroying()  (Origin: Instance)
  [Function] Destroy() -> null  (Origin: Instance)
```

---

### C. Querying Enums
To list all available key-value pairs belonging to a Roblox Enum group:
```bash
./tools/query_api.py enum <EnumName>
```

**Example:** Check all valid keys and values for the `Material` Enum:
```bash
./tools/query_api.py enum Material
```

**Output Snippet:**
```
Enum: Material
--------------
  - Plastic (Value: 256)
  - SmoothPlastic (Value: 272)
  - Neon (Value: 288)
  - Wood (Value: 512)
  - WoodPlanks (Value: 528)
  - Slate (Value: 800)
```
