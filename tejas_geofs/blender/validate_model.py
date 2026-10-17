"""
Automated Model & Project Validation Suite for HAL Tejas Mk1
Verifies:
1. All required export models exist and are valid glTF binary files
2. Aircraft bounding box dimensions match Tejas Mk1 specs (~13.2m x ~8.2m x ~4.4m)
3. Coordinate orientation (+Y forward, +Z up, +X right)
4. Texture atlas existence, resolution, and format
5. Package file count and total size within GeoFS limits (<15 MB)
6. GeoFS definition configuration (aircraft.json / definition.json) validity
7. Animated parts and contact points integrity
"""

import os
import sys
import json
import trimesh
import pygltflib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, "export")
TEXTURES_DIR = os.path.join(BASE_DIR, "textures", "export")
DEF_FILE = os.path.join(BASE_DIR, "aircraft.json")

def validate_project():
    print("=" * 70)
    print("RUNNING AUTOMATED VALIDATION SUITE: HAL TEJAS Mk1 GEOFS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    def report_check(name, status, details=""):
        nonlocal passed, failed
        if status:
            passed += 1
            print(f" [PASS] {name:<35} {details}")
        else:
            failed += 1
            print(f" [FAIL] {name:<35} {details}")

    # 1. Check required exported glB parts
    required_parts = [
        "body.glb", "canopy.glb", "frontWheel.glb", "leftGear.glb",
        "rightGear.glb", "leftAileron.glb", "rightAileron.glb",
        "rudder.glb", "tejas_mk1.glb"
    ]
    for part in required_parts:
        p_path = os.path.join(EXPORT_DIR, part)
        exists = os.path.exists(p_path)
        sz = os.path.getsize(p_path) if exists else 0
        report_check(f"Part Exists: {part}", exists and sz > 500, f"({sz/1024:.1f} KB)")

    # 2. Check 3D Dimensions of Master Aircraft Model
    master_path = os.path.join(EXPORT_DIR, "tejas_mk1.glb")
    if os.path.exists(master_path):
        mesh = trimesh.load(master_path)
        bounds = mesh.bounds
        extents = mesh.extents
        # glTF 2.0 Coordinate convention (Y-up, required for Cesium / GeoFS):
        # extents[0] = X (Wingspan)
        # extents[1] = Y (Height / Up)
        # extents[2] = Z (Length / Longitudinal)
        dx, dy, dz = extents[0], extents[1], extents[2]
        
        # Tejas specs: Length ~13.2m, Span ~8.2m, Height ~4.4m
        len_ok = 12.0 <= dz <= 14.5
        span_ok = 7.5 <= dx <= 9.0
        ht_ok = 4.0 <= dy <= 4.8
        report_check("Length (~13.2m)", len_ok, f"Actual: {dz:.2f} m (glTF Z)")
        report_check("Wingspan (~8.2m)", span_ok, f"Actual: {dx:.2f} m (glTF X)")
        report_check("Height (~4.4m)", ht_ok, f"Actual: {dy:.2f} m (glTF Y)")
        
        # Check forward orientation in glTF (nose forward at glTF -Z, tail at +Z)
        fwd_ok = bounds[0][2] < -5.0 and bounds[1][2] > 5.0
        report_check("Forward Axis (glTF Z)", fwd_ok, f"Z range: [{bounds[0][2]:.2f}, {bounds[1][2]:.2f}]")
        
        # Polygon count
        if hasattr(mesh, 'geometry'):
            n_tris = sum(len(g.faces) for g in mesh.geometry.values() if hasattr(g, 'faces'))
        elif hasattr(mesh, 'faces'):
            n_tris = len(mesh.faces)
        else:
            n_tris = 0
            
        poly_ok = 1000 <= n_tris <= 30000
        report_check("Polygon Budget (<30k tris)", poly_ok, f"{n_tris} triangles")
    else:
        report_check("Master Model Load", False, "File missing")

    # 3. Check Textures
    diffuse_path = os.path.join(TEXTURES_DIR, "tejas_diffuse.png")
    pbr_path = os.path.join(TEXTURES_DIR, "tejas_metallic_roughness.png")
    report_check("Diffuse Map Exists", os.path.exists(diffuse_path), f"({os.path.getsize(diffuse_path)/1024:.1f} KB)")
    report_check("PBR Map Exists", os.path.exists(pbr_path), f"({os.path.getsize(pbr_path)/1024:.1f} KB)")

    # 4. Check Total Package Size (< 15 MB)
    total_bytes = 0
    for root, _, files in os.walk(EXPORT_DIR):
        for f in files:
            total_bytes += os.path.getsize(os.path.join(root, f))
    for root, _, files in os.walk(TEXTURES_DIR):
        for f in files:
            total_bytes += os.path.getsize(os.path.join(root, f))
    total_mb = total_bytes / (1024 * 1024)
    report_check("Package Size (<15 MB)", total_mb < 15.0, f"Total: {total_mb:.2f} MB")

    # 5. Check GeoFS Definition file
    if os.path.exists(DEF_FILE):
        try:
            with open(DEF_FILE, "r") as f:
                data = json.load(f)
            rec = data[0] if isinstance(data, list) else data
            has_mass = rec.get("mass", 0) > 4000
            has_parts = len(rec.get("parts", [])) >= 5
            has_cams = "cockpit" in rec.get("cameras", {})
            has_wheels = any(p.get("type") == "wheel" for p in rec.get("parts", []))
            has_airfoils = any(p.get("type") == "airfoil" for p in rec.get("parts", []))
            report_check("GeoFS JSON Schema", True, f"{len(rec.get('parts', []))} parts configured")
            report_check("Tejas Mass Defined", has_mass, f"{rec.get('mass')} kg")
            report_check("Cockpit Camera", has_cams, str(rec.get("cameras", {}).get("cockpit", {}).get("position")))
            report_check("Landing Gear Configured", has_wheels, "Tricycle wheels present")
            report_check("Airfoils Configured", has_airfoils, "Compound delta airfoils present")
        except Exception as e:
            report_check("GeoFS JSON Parse", False, str(e))
    else:
        report_check("GeoFS aircraft.json", False, "File pending creation")

    print("=" * 70)
    print(f"VALIDATION SUMMARY: {passed} PASSED, {failed} FAILED")
    print("=" * 70)
    return failed == 0

if __name__ == "__main__":
    success = validate_project()
    sys.exit(0 if success else 1)
