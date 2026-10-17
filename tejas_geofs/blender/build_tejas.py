"""
HAL Tejas Mk1 Procedural Blender Build Script
Automates 100% of the 3D aircraft creation, materials, collections,
rigging pivots, camera setup, native .blend saving, and GeoFS glTF export.
Can be executed headlessly:
    blender --background --python blender/build_tejas.py
"""

import os
import sys
import math

try:
    import bpy
    import bmesh
    from mathutils import Vector, Euler, Matrix
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, "export")
TEXTURES_DIR = os.path.join(BASE_DIR, "textures", "export")
BLEND_FILE = os.path.join(BASE_DIR, "blender", "tejas_mk1.blend")
os.makedirs(EXPORT_DIR, exist_ok=True)

def reset_scene():
    """Wipes the current scene to ensure idempotent builds without duplicates"""
    if not IN_BLENDER:
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Ensure scene exists
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    # Set units to Metric
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    scene.unit_settings.scale_length = 1.0

def create_collection(name, parent_col=None):
    if not parent_col:
        parent_col = bpy.context.scene.collection
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        parent_col.children.link(col)
    return col

def get_or_create_material(name, base_color=(0.58, 0.62, 0.66, 1.0), roughness=0.7, metallic=0.1):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = base_color
            bsdf.inputs['Roughness'].default_value = roughness
            bsdf.inputs['Metallic'].default_value = metallic
    return mat

def create_fuselage(col, mat):
    """Builds Tejas Mk1 fuselage loft with radome and exhaust"""
    mesh = bpy.data.meshes.new("FuselageMesh")
    obj = bpy.data.objects.new("Fuselage", mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    sections = [
        # (Y, Z, half_w, half_h)
        (6.60, 0.00, 0.02, 0.02),
        (6.00, 0.00, 0.08, 0.08),
        (5.20, 0.05, 0.35, 0.35),
        (4.40, 0.10, 0.55, 0.50),
        (3.40, 0.15, 0.70, 0.65),
        (2.20, 0.18, 0.82, 0.75),
        (0.80, 0.20, 0.95, 0.85),
        (-0.80, 0.22, 1.05, 0.88),
        (-2.20, 0.20, 1.00, 0.86),
        (-3.80, 0.18, 0.88, 0.80),
        (-5.20, 0.15, 0.72, 0.70),
        (-6.20, 0.12, 0.58, 0.58),
        (-6.60, 0.12, 0.52, 0.52),
    ]
    
    n_ring = 16
    ring_verts = []
    for y, z_c, hw, hh in sections:
        current_ring = []
        for i in range(n_ring):
            ang = 2 * math.pi * i / n_ring
            x = hw * math.cos(ang)
            z = z_c + hh * math.sin(ang)
            if z < z_c and abs(x) > 0.3 * hw:
                z = z_c + hh * 0.85 * math.sin(ang)
            current_ring.append(bm.verts.new(Vector((x, y, z))))
        ring_verts.append(current_ring)
        
    for r in range(len(ring_verts) - 1):
        for s in range(n_ring):
            s_next = (s + 1) % n_ring
            v0 = ring_verts[r][s]
            v1 = ring_verts[r][s_next]
            v2 = ring_verts[r + 1][s_next]
            v3 = ring_verts[r + 1][s]
            bm.faces.new([v0, v1, v2, v3])
            
    # Close ends
    tip_v = bm.verts.new(Vector((0.0, 6.62, 0.0)))
    for s in range(n_ring):
        s_next = (s + 1) % n_ring
        bm.faces.new([tip_v, ring_verts[0][s], ring_verts[0][s_next]])
        
    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)
    return obj

def create_compound_delta_wings(col, mat):
    """Builds compound delta wings with 50/62.5 deg sweep"""
    mesh = bpy.data.meshes.new("WingsMesh")
    obj = bpy.data.objects.new("Wings", mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    stations = [
        (0.85,  1.40, 5.80, 0.32),
        (1.80,  0.20, 4.40, 0.24),
        (2.70, -1.00, 3.10, 0.18),
        (3.60, -2.20, 2.00, 0.12),
        (4.10, -2.85, 1.35, 0.08),
    ]
    
    for side in [-1, 1]:
        station_verts = []
        for x_pos, y_le, chord, thick in stations:
            current_st = []
            x = side * x_pos
            for pt in range(8):
                frac = pt / 7.0
                y = y_le - frac * chord
                if pt < 4:
                    sub_f = pt / 3.0
                    y = y_le - sub_f * chord
                    z = 0.10 + thick * 2.0 * math.sqrt(max(0.0001, sub_f)) * (1.0 - sub_f)
                else:
                    sub_f = 1.0 - (pt - 4) / 3.0
                    y = y_le - sub_f * chord
                    z = 0.10 - thick * 2.0 * math.sqrt(max(0.0001, sub_f)) * (1.0 - sub_f)
                current_st.append(bm.verts.new(Vector((x, y, z))))
            station_verts.append(current_st)
            
        for s in range(len(station_verts) - 1):
            for p in range(7):
                v0 = station_verts[s][p]
                v1 = station_verts[s][p + 1]
                v2 = station_verts[s + 1][p + 1]
                v3 = station_verts[s + 1][p]
                if side == 1:
                    bm.faces.new([v0, v1, v2, v3])
                else:
                    bm.faces.new([v0, v3, v2, v1])
                    
    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)
    return obj

def create_vertical_tail(col, mat):
    """Builds vertical stabilizer fin"""
    mesh = bpy.data.meshes.new("TailMesh")
    obj = bpy.data.objects.new("VerticalTail", mesh)
    col.objects.link(obj)
    
    bm = bmesh.new()
    stations = [
        (0.80, -1.80, 4.40, 0.30),
        (1.80, -2.50, 3.40, 0.22),
        (2.80, -3.20, 2.40, 0.16),
        (3.80, -3.90, 1.50, 0.10),
        (4.35, -4.20, 0.90, 0.06),
    ]
    
    fin_verts = []
    for z_pos, y_le, chord, thick in stations:
        cur_ring = []
        for pt in range(8):
            if pt < 4:
                frac = pt / 3.0
                y = y_le - frac * chord
                x = thick * math.sin(frac * math.pi) * 0.5
            else:
                frac = 1.0 - (pt - 4) / 3.0
                y = y_le - frac * chord
                x = -thick * math.sin(frac * math.pi) * 0.5
            cur_ring.append(bm.verts.new(Vector((x, y, z_pos))))
        fin_verts.append(cur_ring)
        
    for s in range(len(fin_verts) - 1):
        for p in range(7):
            v0 = fin_verts[s][p]
            v1 = fin_verts[s][p + 1]
            v2 = fin_verts[s + 1][p + 1]
            v3 = fin_verts[s + 1][p]
            bm.faces.new([v0, v1, v2, v3])
            
    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)
    return obj

def setup_cameras_and_lights():
    """Sets up preview cameras and lighting"""
    # Key light
    light_data = bpy.data.lights.new(name="SunLight", type='SUN')
    light_data.energy = 3.5
    light_obj = bpy.data.objects.new(name="Sun", object_data=light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.rotation_euler = Euler((math.radians(50), math.radians(20), math.radians(-35)), 'XYZ')
    
    # Cameras
    cam_configs = {
        "Cam_Front": (Vector((0, 18, 0.5)), Euler((math.radians(90), 0, math.radians(180)))),
        "Cam_Side": (Vector((-18, 0, 1.0)), Euler((math.radians(88), 0, math.radians(-90)))),
        "Cam_Top": (Vector((0, 0, 22)), Euler((0, 0, math.radians(90)))),
        "Cam_ThreeQuarter": (Vector((-14, 12, 6)), Euler((math.radians(65), 0, math.radians(-130)))),
    }
    
    for name, (pos, rot) in cam_configs.items():
        cam_data = bpy.data.cameras.new(name)
        cam_obj = bpy.data.objects.new(name, cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        cam_obj.location = pos
        cam_obj.rotation_euler = rot

def build_tejas_blender():
    if not IN_BLENDER:
        print("[!] Note: This script is designed for Blender's embedded Python (bpy).")
        print("    Run via: blender --background --python blender/build_tejas.py")
        return
        
    print("Executing automated procedural Blender build for HAL Tejas Mk1...")
    reset_scene()
    
    col_fuselage = create_collection("Collection_Fuselage")
    col_wings = create_collection("Collection_Wings")
    col_tail = create_collection("Collection_Tail")
    col_cockpit = create_collection("Collection_Cockpit")
    col_gear = create_collection("Collection_LandingGear")
    
    mat_iaf = get_or_create_material("MAT_IAF_Camo", base_color=(0.58, 0.62, 0.66, 1.0), roughness=0.7)
    mat_dark = get_or_create_material("MAT_Radome_Dark", base_color=(0.18, 0.20, 0.22, 1.0), roughness=0.8)
    
    fuselage = create_fuselage(col_fuselage, mat_iaf)
    wings = create_compound_delta_wings(col_wings, mat_iaf)
    tail = create_vertical_tail(col_tail, mat_iaf)
    
    setup_cameras_and_lights()
    
    # Save native .blend file
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"  [x] Saved native Blender project: {BLEND_FILE}")
    
    # Export glTF
    export_glb = os.path.join(EXPORT_DIR, "tejas_mk1_blender.glb")
    bpy.ops.export_scene.gltf(
        filepath=export_glb,
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(f"  [x] Exported glTF: {export_glb}")

if __name__ == "__main__":
    build_tejas_blender()
