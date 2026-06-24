#!/usr/bin/env python3
import unittest
import os
import tempfile
import shutil
import sys

# Add tools/ parent directory to path to allow importing validate_api
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(SCRIPT_DIR)

import validate_api

class TestRobloxApiValidator(unittest.TestCase):
    def setUp(self):
        # Create a mini mock Roblox API Database structure for isolated testing
        self.mock_db = {
            "Classes": [
                {
                    "Name": "Instance",
                    "Superclass": "",
                    "Members": [
                        {
                            "MemberType": "Function",
                            "Name": "Destroy",
                            "ReturnType": {"Name": "null"},
                            "Parameters": []
                        }
                    ]
                },
                {
                    "Name": "BasePart",
                    "Superclass": "Instance",
                    "Members": [
                        {
                            "MemberType": "Property",
                            "Name": "Size",
                            "ValueType": {"Category": "Primitive", "Name": "Vector3"}
                        },
                        {
                            "MemberType": "Property",
                            "Name": "Material",
                            "ValueType": {"Category": "Enum", "Name": "Material"}
                        }
                    ]
                },
                {
                    "Name": "Part",
                    "Superclass": "BasePart",
                    "Members": [
                        {
                            "MemberType": "Property",
                            "Name": "Shape",
                            "ValueType": {"Category": "Enum", "Name": "PartType"}
                        }
                    ]
                },
                {
                    "Name": "SurfaceGuiBase",
                    "Superclass": "Instance",
                    "Members": [
                        {
                            "MemberType": "Property",
                            "Name": "Face",
                            "ValueType": {"Category": "Enum", "Name": "NormalId"}
                        }
                    ]
                },
                {
                    "Name": "SurfaceGui",
                    "Superclass": "SurfaceGuiBase",
                    "Members": [
                        {
                            "MemberType": "Property",
                            "Name": "LightInfluence",
                            "ValueType": {"Category": "Primitive", "Name": "float"}
                        }
                    ]
                }
            ],
            "Enums": [
                {
                    "Name": "Material",
                    "Items": [
                        {"Name": "Plastic", "Value": 256},
                        {"Name": "Slate", "Value": 800}
                    ]
                },
                {
                    "Name": "PartType",
                    "Items": [
                        {"Name": "Ball", "Value": 0},
                        {"Name": "Block", "Value": 1}
                    ]
                },
                {
                    "Name": "NormalId",
                    "Items": [
                        {"Name": "Front", "Value": 0},
                        {"Name": "Back", "Value": 1}
                    ]
                }
            ]
        }
        self.classes = validate_api.get_class_map(self.mock_db)
        self.enums = validate_api.get_enum_map(self.mock_db)

    def test_class_property_inheritance(self):
        # Part should inherit 'Size' and 'Material' from BasePart
        props = validate_api.get_class_properties(self.classes, "Part")
        self.assertIn("size", props)
        self.assertIn("material", props)
        self.assertIn("shape", props)
        
        # 'Destroy' is a Function, not a Property
        self.assertNotIn("destroy", props)

    def test_property_validation_positive(self):
        # Slate is a valid Material for a Part
        success, msg = validate_api.validate_properties(
            self.classes, self.enums, "Part", {"Material": "Slate"}
        )
        self.assertTrue(success)

    def test_property_validation_negative(self):
        # Obsidian is invalid in our Material enum
        success, msg = validate_api.validate_properties(
            self.classes, self.enums, "Part", {"Material": "Obsidian"}
        )
        self.assertFalse(success)
        self.assertIn("Invalid value 'Obsidian'", msg)

        # Invalid property name
        success, msg = validate_api.validate_properties(
            self.classes, self.enums, "Part", {"FakeProperty": "Slate"}
        )
        self.assertFalse(success)
        self.assertIn("is not valid for Class", msg)

    def test_class_constraints_sizing(self):
        # Valid Size
        success, msg = validate_api.validate_class_constraints(
            self.classes, self.enums, "Part", {"Size": [4, 10, 4]}
        )
        self.assertTrue(success)

        # Invalid Size (dimension <= 0)
        success, msg = validate_api.validate_class_constraints(
            self.classes, self.enums, "Part", {"Size": [4, 0, 4]}
        )
        self.assertFalse(success)
        self.assertIn("Invalid Size dimension", msg)

        # Invalid Size (dimension > 2048)
        success, msg = validate_api.validate_class_constraints(
            self.classes, self.enums, "Part", {"Size": [4, 2500, 4]}
        )
        self.assertFalse(success)
        self.assertIn("Roblox size dimensions must be", msg)

    def test_scan_directory_violations(self):
        # Resolve physical test directories relative to script
        test_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        valid_dir = os.path.join(test_dir, "tests", "valid_code_samples")
        invalid_dir = os.path.join(test_dir, "tests", "invalid_code_samples")

        # 1. Scanning valid samples should report 0 violations
        success, msg = validate_api.scan_lua_directory(self.classes, self.enums, valid_dir)
        self.assertTrue(success)
        self.assertIn("Violations found: 0", msg)

        # 2. Scanning invalid samples should report 3 violations (1 class error, 2 enum errors)
        success, msg = validate_api.scan_lua_directory(self.classes, self.enums, invalid_dir)
        self.assertFalse(success)
        self.assertIn("Violations found: 3", msg)

if __name__ == "__main__":
    unittest.main()
