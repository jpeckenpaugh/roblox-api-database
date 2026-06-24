#!/usr/bin/env python3
import sys
import json
import urllib.request
import os
import datetime

VERSION_URL = "https://setup.rbxcdn.com/versionQTStudio"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
VERSIONS_DIR = os.path.join(ROOT_DIR, "versions")
CURRENT_FILE = os.path.join(ROOT_DIR, "current", "roblox_api_dump.json")

def get_latest_hash():
    try:
        with urllib.request.urlopen(VERSION_URL) as response:
            return response.read().decode('utf-8').strip()
    except Exception as e:
        print(f"Error fetching version hash: {e}", file=sys.stderr)
        sys.exit(1)

def download_api_dump(version_hash):
    url = f"https://setup.rbxcdn.com/{version_hash}-API-Dump.json"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error downloading API dump: {e}", file=sys.stderr)
        sys.exit(1)

def normalize_dump(dump):
    """Normalize the API dump structure to make semantic comparison order-independent."""
    normalized = {}
    
    # Sort Enums by Name, and their items by Name
    enums = []
    for enum in dump.get("Enums", []):
        norm_enum = {
            "Name": enum["Name"],
            "Items": sorted(enum.get("Items", []), key=lambda x: x.get("Name", ""))
        }
        enums.append(norm_enum)
    normalized["Enums"] = sorted(enums, key=lambda x: x["Name"])
    
    # Sort Classes by Name, and their members by MemberType + Name
    classes = []
    for cls in dump.get("Classes", []):
        norm_cls = {
            "Name": cls["Name"],
            "Superclass": cls.get("Superclass", ""),
            "Members": sorted(cls.get("Members", []), key=lambda x: (x.get("MemberType", ""), x.get("Name", "")))
        }
        classes.append(norm_cls)
    normalized["Classes"] = sorted(classes, key=lambda x: x["Name"])
    
    return normalized

def semantic_equals(dump_a, dump_b):
    return normalize_dump(dump_a) == normalize_dump(dump_b)

def main():
    print("Checking latest Roblox Studio version hash...")
    version_hash = get_latest_hash()
    print(f"Latest Version Hash: {version_hash}")
    
    print("Downloading API dump from CDN...")
    new_dump = download_api_dump(version_hash)
    
    # Check if we have an existing dump
    if os.path.exists(CURRENT_FILE):
        try:
            with open(CURRENT_FILE, "r") as f:
                old_dump = json.load(f)
            
            if semantic_equals(old_dump, new_dump):
                print("No semantic changes detected. Skipping update.")
                sys.exit(0)
        except Exception as e:
            print(f"Warning: Failed to parse existing dump: {e}. Re-writing.", file=sys.stderr)
            
    # Generate timestamped filename
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    version_filename = f"{timestamp}.json"
    version_path = os.path.join(VERSIONS_DIR, version_filename)
    
    # Ensure versions dir exists
    os.makedirs(VERSIONS_DIR, exist_ok=True)
    
    # Write the new dump file
    with open(version_path, "w") as f:
        json.dump(new_dump, f, indent=4)
    print(f"Saved new version: versions/{version_filename}")
    
    # Update current symlink
    current_dir = os.path.dirname(CURRENT_FILE)
    os.makedirs(current_dir, exist_ok=True)
    if os.path.exists(CURRENT_FILE):
        os.remove(CURRENT_FILE)
        
    # Relative symlink from current/ to versions/
    os.symlink(f"../versions/{version_filename}", CURRENT_FILE)
    print("Updated symlink current/roblox_api_dump.json")

if __name__ == "__main__":
    main()
