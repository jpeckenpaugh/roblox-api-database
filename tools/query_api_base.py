#!/usr/bin/env python3
import sys
import json
import os

# Default database location relative to the script directory
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_DB_PATH = os.path.join(SCRIPT_DIR, "..", "current", "roblox_api_dump.json")

def load_db(path):
    if not os.path.exists(path):
        print(f"Error: API Dump file not found at {path}", file=sys.stderr)
        print("Run ./fetch_api_dump.sh to generate the database.", file=sys.stderr)
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)

def query_enum(db, enum_name):
    for entry in db.get("Enums", []):
        if entry.get("Name").lower() == enum_name.lower():
            print(f"Enum: {entry['Name']}")
            print("-" * (len(entry['Name']) + 6))
            for item in sorted(entry.get("Items", []), key=lambda x: x.get("Value")):
                print(f"  - {item['Name']} (Value: {item['Value']})")
            return
    print(f"Error: Enum '{enum_name}' not found.", file=sys.stderr)
    sys.exit(1)

def query_class(db, class_name):
    # Find target class
    classes = {c["Name"].lower(): c for c in db.get("Classes", [])}
    target = class_name.lower()
    
    if target not in classes:
        print(f"Error: Class '{class_name}' not found.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Class: {classes[target]['Name']}")
    
    # Resolve inheritance tree
    inheritance = []
    curr = classes[target]
    while curr:
        inheritance.append(curr["Name"])
        superclass = curr.get("Superclass")
        curr = classes.get(superclass.lower()) if superclass else None
    
    print(f"Inheritance: {' -> '.join(inheritance)}")
    print("-" * 40)
    
    # Collate members from self and superclasses
    members = []
    for cls_name in inheritance:
        cls_data = classes[cls_name.lower()]
        for member in cls_data.get("Members", []):
            members.append((cls_name, member))
            
    # Print sorted members
    for cls_origin, member in sorted(members, key=lambda x: (x[1]["MemberType"], x[1]["Name"])):
        m_type = member["MemberType"]
        m_name = member["Name"]
        
        if m_type == "Property":
            val_type = member.get("ValueType", {}).get("Name", "unknown")
            sec = member.get("Security", {}).get("Read", "None")
            print(f"  [Property] {m_name}: {val_type}  (Origin: {cls_origin}, Read Security: {sec})")
        elif m_type == "Function":
            params = ", ".join([f"{p['Name']}: {p['Type']['Name']}" for p in member.get("Parameters", [])])
            ret = member.get("ReturnType", {}).get("Name", "void")
            print(f"  [Function] {m_name}({params}) -> {ret}  (Origin: {cls_origin})")
        elif m_type == "Event":
            params = ", ".join([f"{p['Name']}: {p['Type']['Name']}" for p in member.get("Parameters", [])])
            print(f"  [Event] {m_name}({params})  (Origin: {cls_origin})")

def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("enum", "class"):
        print("Usage: python3 query_api.py [enum|class] [name] [optional_path_to_db]", file=sys.stderr)
        print("Example: python3 query_api.py enum Material", file=sys.stderr)
        print("Example: python3 query_api.py class Part", file=sys.stderr)
        sys.exit(1)
        
    action = sys.argv[1]
    name = sys.argv[2]
    db_path = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_DB_PATH
    
    db = load_db(db_path)
    if action == "enum":
        query_enum(db, name)
    elif action == "class":
        query_class(db, name)

if __name__ == "__main__":
    main()
