import os
import json
import struct
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GEOFS_DIR = os.path.join(REPO_ROOT, "tejas_geofs")


class TestGeoFSAircraftPackage(unittest.TestCase):
    """Automated CI validation test suite for HAL Tejas Mk1 / LCA Navy GeoFS package."""

    def test_aircraft_definition_json_validity(self):
        """Ensure definition.json is valid JSON and contains all required GeoFS fields."""
        def_path = os.path.join(GEOFS_DIR, "definition.json")
        self.assertTrue(os.path.exists(def_path), f"Missing {def_path}")

        with open(def_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data = data[0] if isinstance(data, list) else data
        required_keys = ["name", "mass", "com", "parts", "contactProperties"]
        for key in required_keys:
            self.assertIn(key, data, f"definition.json missing required key: {key}")

        # Mass sanity (HAL Tejas LCA Navy is ~6560 kg empty)
        self.assertGreater(data["mass"], 4000)
        self.assertLess(data["mass"], 15000)

        # Parts sanity
        part_names = [p["name"] for p in data["parts"]]
        self.assertIn("body", part_names, "Missing 'body' part in parts array")

    def test_aircraft_json_validity(self):
        """Ensure aircraft.json exists and contains correct metadata."""
        ac_path = os.path.join(GEOFS_DIR, "aircraft.json")
        self.assertTrue(os.path.exists(ac_path), f"Missing {ac_path}")

        with open(ac_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        record = data[0] if isinstance(data, list) else data
        self.assertIn("name", record)
        self.assertIn("parts", record)
        self.assertTrue("Tejas" in record["name"])

    def test_glb_model_binary_header(self):
        """Ensure tejas_navy_geofs.glb exists and has valid glTF 2.0 binary header."""
        glb_path = os.path.join(GEOFS_DIR, "export", "tejas_navy_geofs.glb")
        self.assertTrue(os.path.exists(glb_path), f"Missing GLB file at {glb_path}")

        file_size = os.path.getsize(glb_path)
        self.assertGreater(file_size, 1_000_000, f"GLB file too small ({file_size} bytes)")
        self.assertLess(file_size, 100_000_000, f"GLB file exceeds 100 MB GitHub limit ({file_size} bytes)")

        # Verify magic header 'glTF' and version 2
        with open(glb_path, "rb") as f:
            magic, version, length = struct.unpack("<4sII", f.read(12))
            self.assertEqual(magic, b"glTF", "File magic header is not glTF")
            self.assertEqual(version, 2, "glTF version is not 2")
            self.assertEqual(length, file_size, "Header length does not match file size")

    def test_tampermonkey_userscript_metadata(self):
        """Ensure Tampermonkey script exists and has required metadata headers."""
        tm_path = os.path.join(GEOFS_DIR, "tejas_navy.user.js")
        self.assertTrue(os.path.exists(tm_path), f"Missing {tm_path}")

        with open(tm_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("// ==UserScript==", content)
        self.assertIn("@match", content)
        self.assertIn("geo-fs.com", content)
        self.assertIn("GM_xmlhttpRequest", content)
        self.assertIn("// ==/UserScript==", content)

    def test_bookmarklet_syntax(self):
        """Ensure bookmarklet starts with javascript: and is within length limits."""
        bm_path = os.path.join(GEOFS_DIR, "bookmarklet.txt")
        self.assertTrue(os.path.exists(bm_path), f"Missing {bm_path}")

        with open(bm_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        self.assertTrue(content.startswith("javascript:"), "Bookmarklet must start with 'javascript:'")
        self.assertLess(len(content), 32767, "Bookmarklet exceeds maximum browser URL length (32KB)")


if __name__ == "__main__":
    unittest.main()
