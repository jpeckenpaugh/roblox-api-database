# Roblox API Database

A git-tracked database of official Roblox Client and Studio API dumps. Designed for offline engine schema lookup, static analysis, and programmatic validation in CI/CD pipelines.

## Repository Contents

* `roblox_api_dump.json`: The complete official Roblox API JSON schema dump.
* `fetch_api_dump.sh`: Bash script to query Roblox CDN endpoints and download the latest dump.
* `.gitignore`: System and temporary files ignored.

## Usage

### 1. Updating the API Dump
To download and overwrite the current dump with the latest API schema from the Roblox CDN:
```bash
./fetch_api_dump.sh
```

### 2. Programmatic Queries
Use standard JSON parsing tools like `jq` to search classes or enums without loading the entire 4MB file into memory.

**Example: Check if a material name is a valid Enum value:**
```bash
jq '.Enums[] | select(.Name=="Material") | .Items[].Name' roblox_api_dump.json | grep -i "Slate"
```
