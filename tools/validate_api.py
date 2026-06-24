#!/usr/bin/env python3
import sys
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_DB_PATH = os.path.join(SCRIPT_DIR, "..", "current", "roblox_api_dump.json")

def load_db(path):
    if not os.path.exists(path):
        print(f"Error: API Dump file not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)

def get_class_map(db):
    return {c["Name"].lower(): c for c in db.get("Classes", [])}

def get_enum_map(db):
    return {e["Name"].lower(): {item["Name"].lower(): item["Name"] for item in e.get("Items", [])} for e in db.get("Enums", [])}

def get_class_inheritance(classes, class_name):
    inheritance = []
    curr = classes.get(class_name.lower())
    while curr:
        inheritance.append(curr["Name"])
        superclass = curr.get("Superclass")
        curr = classes.get(superclass.lower()) if superclass else None
    return inheritance

def get_class_properties(classes, class_name):
    inheritance = get_class_inheritance(classes, class_name)
    properties = {}
    for cls_name in inheritance:
        cls_data = classes[cls_name.lower()]
        for member in cls_data.get("Members", []):
            if member["MemberType"] == "Property":
                properties[member["Name"].lower()] = member
    return properties

def validate_properties(classes, enums, class_name, props_dict):
    target = class_name.lower()
    if target not in classes:
        return False, f"Class '{class_name}' is invalid."
    
    valid_props = get_class_properties(classes, class_name)
    
    for k, v in props_dict.items():
        k_lower = k.lower()
        if k_lower not in valid_props:
            return False, f"Property '{k}' is not valid for Class '{classes[target]['Name']}'."
        
        prop_data = valid_props[k_lower]
        val_type_info = prop_data.get("ValueType", {})
        val_category = val_type_info.get("Category")
        val_type = val_type_info.get("Name")
        
        # Validate Enums if category is Enum
        if val_category == "Enum" and val_type:
            enum_group = val_type.replace("Enum.", "").lower()
            if enum_group in enums:
                v_str = str(v).lower()
                if v_str not in enums[enum_group]:
                    valid_keys = ", ".join(enums[enum_group].values())
                    return False, f"Invalid value '{v}' for property '{k}' (Enum: {val_type}). Valid keys: {valid_keys}"
            else:
                return False, f"Internal Error: Enum group '{enum_group}' not found in database."
                
    return True, "All properties are valid."

def validate_class_constraints(classes, enums, class_name, props_dict):
    success, msg = validate_properties(classes, enums, class_name, props_dict)
    if not success:
        return False, msg
        
    # Apply standard Roblox sizing constraints (e.g. Size limits 2048 studs)
    size = None
    for k in props_dict:
        if k.lower() == "size":
            size = props_dict[k]
            break
            
    if size:
        if isinstance(size, list) and len(size) == 3:
            for dim in size:
                if not isinstance(dim, (int, float)) or dim <= 0 or dim > 2048:
                    return False, f"Invalid Size dimension '{dim}'. Roblox size dimensions must be > 0 and <= 2048 studs."
                    
    return True, f"Class {class_name} conforms to all engine limits."

# Known valid Roblox enums and classes that may be missing from CDN JSON dumps
CLASS_ALLOWLIST = {"unreliableremoteevent"}
ENUM_ALLOWLIST = set()

def scan_lua_directory(classes, enums, directory_path):
    print(f"Scanning directory '{directory_path}' for Roblox API violations...")
    violations = 0
    
    # Pre-compile regex patterns
    enum_pattern = re.compile(r"Enum\.([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)")
    inst_pattern = re.compile(r"Instance\.new\s*\(\s*[\"']([a-zA-Z0-9_]+)[\"']\s*\)")
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            if not file.endswith(".lua"):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        # 1. Scan for Instance.new("ClassName")
                        for inst_match in inst_pattern.finditer(line):
                            class_name = inst_match.group(1)
                            if class_name.lower() not in classes and class_name.lower() not in CLASS_ALLOWLIST:
                                print(f"  [ERROR] {file_path}:{line_num} -> Invalid Instance.new(\"{class_name}\")")
                                violations += 1
                                
                        # 2. Scan for Enum.GroupName.KeyName
                        for enum_match in enum_pattern.finditer(line):
                            group = enum_match.group(1).lower()
                            key = enum_match.group(2).lower()
                            
                            # Ignore common false positives/custom wrappers if not in actual Roblox enums
                            if group in enums:
                                if key not in enums[group]:
                                    print(f"  [ERROR] {file_path}:{line_num} -> Invalid Enum value 'Enum.{enum_match.group(1)}.{enum_match.group(2)}'")
                                    violations += 1
            except Exception as e:
                print(f"Warning: Failed to read {file_path}: {e}", file=sys.stderr)
                
    return violations == 0, f"Scan complete. Violations found: {violations}"

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 validate_api.py [properties|class|scan_src] [args]", file=sys.stderr)
        print("Example: python3 validate_api.py properties Part '{\"Material\": \"Obsidian\"}'", file=sys.stderr)
        print("Example: python3 validate_api.py class Part '{\"Size\": [4, 10, 4]}'", file=sys.stderr)
        print("Example: python3 validate_api.py scan_src /path/to/src", file=sys.stderr)
        sys.exit(1)
        
    action = sys.argv[1]
    db_path = DEFAULT_DB_PATH
    db = load_db(db_path)
    
    classes = get_class_map(db)
    enums = get_enum_map(db)
    
    if action == "properties":
        class_name = sys.argv[2]
        props = json.loads(sys.argv[3])
        success, msg = validate_properties(classes, enums, class_name, props)
        print(msg)
        sys.exit(0 if success else 1)
        
    elif action == "class":
        class_name = sys.argv[2]
        props = json.loads(sys.argv[3])
        success, msg = validate_class_constraints(classes, enums, class_name, props)
        print(msg)
        sys.exit(0 if success else 1)
        
    elif action == "scan_src":
        target_dir = sys.argv[2]
        success, msg = scan_lua_directory(classes, enums, target_dir)
        print(msg)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
