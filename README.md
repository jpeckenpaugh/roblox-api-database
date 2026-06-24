# Roblox API Database

A git-tracked database of official Roblox Client and Studio API dumps. Designed for offline engine schema lookup, static analysis, and programmatic validation in CI/CD pipelines.

## Repository Contents

* `roblox_api_dump.json`: The complete official Roblox API JSON schema dump.
* `fetch_api_dump.sh`: Bash script to query Roblox CDN endpoints and download the latest dump.
* `query_api.py`: Python CLI query tool to check classes and enums.
* `.gitignore`: System and temporary files ignored.

## Usage

### 1. Updating the API Dump
To download and overwrite the current dump with the latest API schema from the Roblox CDN:
```bash
./fetch_api_dump.sh
```

### 2. Querying the Database
Use the bundled Python tool to check class structures, inheritance, and enum values:

**Example: Check all values for a specific Enum:**
```bash
./query_api.py enum Material
```

**Example: Check all properties, methods, and inherited members for a Class:**
```bash
./query_api.py class SurfaceGui
```
