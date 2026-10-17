"""
Master Rebuild Script for HAL Tejas Mk1
Fixes:
1. Aircraft sinking: Centers all landing gear and control surface parts at (0,0,0) pivots.
   Configures correct gear collision points and positions so the aircraft stands cleanly on the runway.
2. Dull quality:
   - Sets metallicFactor = 0.05 (realistic non-metallic military paint)
   - Sets roughnessFactor = 0.42 (semi-matte satin finish that catches sunlight and reflections)
   - Generates exact planar-aligned 2048x2048 IAF camouflage texture with vibrant roundels,
     fin flash, radome, anti-glare shield, and panel lines.
3. Compiles self-contained geofs_test_loader.js.
"""

import os
import math
import json
import base64
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFilter
import pygltflib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, "export")
TEXTURES_DIR = os.path.join(BASE_DIR, "textures", "export")
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(TEXTURES_DIR, exist_ok=True)

WIDTH, HEIGHT = 2048, 2048

# -------------------------------------------------------------
# 1. GENERATE PLANAR-ALIGNED IAF TEXTURE ATLAS
# -------------------------------------------------------------
def generate_aligned_texture():
    print("Generating planar-aligned IAF 2048x2048 texture atlas...")
    # Base IAF Ghost Grey (Crisp, vibrant Light Air-Superiority Grey)
    base_color = (185, 198, 210, 255) # Hex #B9C6D2 - vibrant daylight air-superiority grey
    img = Image.new("RGBA", (WIDTH, HEIGHT), base_color)
    draw = ImageDraw.Draw(img)
    
    # Coordinate mapping:
    # X from -4.2m to +4.2m -> px from 0 to 2048 (Center X = 1024)
    # Y from -6.6m to +6.6m -> py from 0 to 2048 (Nose at py = 2048, Tail at py = 0)
    def to_px(x_m, y_m):
        px = int(np.clip((x_m + 4.2) / 8.4 * WIDTH, 0, WIDTH - 1))
        py = int(np.clip((y_m + 6.6) / 13.2 * HEIGHT, 0, HEIGHT - 1))
        return px, py

    # Darker Blue-Grey Camouflage Pattern (Hex #7A8E9F)
    camo_color = (122, 142, 159, 255)
    
    # Draw curved camouflage patches on wings and spine
    camo_patches = [
        # Left wing camo
        [(-3.8, -2.5), (-1.8, -0.5), (-1.2, -3.5), (-3.5, -4.5)],
        [(-2.2, -4.0), (-0.8, -2.0), (-0.5, -5.0), (-2.0, -5.5)],
        # Right wing camo
        [(1.5, -0.8), (3.6, -2.8), (3.2, -4.8), (1.2, -3.2)],
        [(0.6, -2.5), (2.2, -4.2), (1.8, -5.8), (0.4, -4.8)],
        # Fuselage forward & canopy surround
        [(-0.6, 2.0), (0.6, 2.5), (0.5, 4.2), (-0.5, 3.8)],
        # Dorsal spine
        [(-0.4, -0.5), (0.4, -0.2), (0.3, -3.8), (-0.3, -3.5)],
    ]
    
    camo_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(camo_layer)
    for patch in camo_patches:
        pts = [to_px(xm, ym) for xm, ym in patch]
        c_draw.polygon(pts, fill=camo_color)
        
    # Soften camouflage edges slightly for authentic spray transition
    camo_layer = camo_layer.filter(ImageFilter.GaussianBlur(radius=5))
    img.alpha_composite(camo_layer)
    
    # Structural Panel Lines (Subtle dark seams)
    panel_color = (55, 62, 70, 140)
    p_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(p_layer)
    
    # Wing chord lines and elevon hinge lines
    for ym in np.linspace(-5.5, 0.5, 12):
        p0 = to_px(-3.9, ym)
        p1 = to_px(3.9, ym)
        p_draw.line([p0, p1], fill=panel_color, width=2)
    # Fuselage frame rings
    for ym in np.linspace(-6.0, 5.5, 18):
        p0 = to_px(-0.9, ym)
        p1 = to_px(0.9, ym)
        p_draw.line([p0, p1], fill=panel_color, width=2)
    # Centerline spine
    p_draw.line([to_px(0, -6.6), to_px(0, 6.0)], fill=(40, 45, 52, 180), width=3)
    
    # Elevon demarcation lines (trailing edge control surfaces)
    p_draw.line([to_px(-3.9, -4.4), to_px(-1.2, -4.4)], fill=(30, 35, 40, 220), width=3)
    p_draw.line([to_px(1.2, -4.4), to_px(3.9, -4.4)], fill=(30, 35, 40, 220), width=3)
    
    # Radome (Nose Cone) - Dark radar composite grey
    r_pts = [to_px(0, 6.6), to_px(0.55, 4.4), to_px(-0.55, 4.4)]
    p_draw.polygon(r_pts, fill=(45, 48, 52, 255))
    p_draw.line([to_px(-0.55, 4.4), to_px(0.55, 4.4)], fill=(20, 22, 25, 255), width=4) # Radome ring
    
    # Anti-glare Matte Shield in front of cockpit
    ag_pts = [to_px(-0.35, 3.8), to_px(0.35, 3.8), to_px(0.28, 4.38), to_px(-0.28, 4.38)]
    p_draw.polygon(ag_pts, fill=(28, 30, 32, 255))
    
    # Engine Exhaust Nozzle Petals
    noz_box = [to_px(-0.55, -6.6)[0], to_px(0, -6.6)[1], to_px(0.55, -6.0)[0], to_px(0, -6.0)[1]]
    p_draw.rectangle(noz_box, fill=(65, 60, 55, 255))
    for xm in np.linspace(-0.52, 0.52, 16):
        p_draw.line([to_px(xm, -6.6), to_px(xm, -6.0)], fill=(30, 28, 25, 220), width=2)
        
    img.alpha_composite(p_layer)
    
    # National Markings
    def draw_roundel(cx_m, cy_m, r_m):
        cx, cy = to_px(cx_m, cy_m)
        r = int(r_m / 8.4 * WIDTH)
        r_draw = ImageDraw.Draw(img)
        # Saffron outer ring
        r_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 140, 25, 255))
        # White middle ring
        rw = int(r * 0.66)
        r_draw.ellipse([cx - rw, cy - rw, cx + rw, cy + rw], fill=(255, 255, 255, 255))
        # Green inner circle
        rg = int(r * 0.33)
        r_draw.ellipse([cx - rg, cy - rg, cx + rg, cy + rg], fill=(15, 145, 10, 255))
        # Navy blue Ashoka chakra center dot
        rc = max(2, int(r * 0.08))
        r_draw.ellipse([cx - rc, cy - rc, cx + rc, cy + rc], fill=(0, 0, 130, 255))

    # IAF Wings Roundels: Port wing upper, Starboard wing lower
    draw_roundel(-2.5, -3.2, 0.55)
    draw_roundel(2.5, -3.2, 0.55)
    
    # Fin Flash (Indian Tricolour: Saffron, White, Green vertical stripes on fin)
    fx0, fy0 = to_px(-0.02, -4.5)
    fw, fh = 40, 60
    f_draw = ImageDraw.Draw(img)
    f_draw.rectangle([fx0 - fw, fy0, fx0 - fw + 13, fy0 + fh], fill=(255, 140, 25, 255))
    f_draw.rectangle([fx0 - fw + 13, fy0, fx0 - fw + 27, fy0 + fh], fill=(255, 255, 255, 255))
    f_draw.rectangle([fx0 - fw + 27, fy0, fx0, fy0 + fh], fill=(15, 145, 10, 255))
    f_draw.rectangle([fx0, fy0, fx0 + 13, fy0 + fh], fill=(255, 140, 25, 255))
    f_draw.rectangle([fx0 + 13, fy0, fx0 + 27, fy0 + fh], fill=(255, 255, 255, 255))
    f_draw.rectangle([fx0 + 27, fy0, fx0 + fw, fy0 + fh], fill=(15, 145, 10, 255))

    # Red Ejection Seat Warning Triangles near cockpit
    def draw_triangle(xm, ym, size):
        px, py = to_px(xm, ym)
        t_draw = ImageDraw.Draw(img)
        pts = [(px, py), (px + size, py), (px + size // 2, py - int(size * 0.86))]
        t_draw.polygon(pts, fill=(230, 25, 25, 255), outline=(255, 255, 255, 255))
    draw_triangle(-0.65, 3.2, 24)
    draw_triangle(0.65, 3.2, 24)
    
    diff_path = os.path.join(TEXTURES_DIR, "tejas_diffuse.png")
    img.save(diff_path, "PNG", optimize=True)
    print(f"  [x] Saved aligned diffuse texture: {diff_path}")
    return diff_path

# -------------------------------------------------------------
# 2. BUILD 3D GEOMETRY WITH CENTERED MOVING PART PIVOTS
# -------------------------------------------------------------
def build_all_models():
    print("Building 3D geometry with centered part pivots...")
    
    # A. Fuselage & Airframe
    sections = [
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
    verts, faces = [], []
    for ring_idx, (y, z_c, hw, hh) in enumerate(sections):
        for s in range(n_ring):
            ang = 2 * math.pi * s / n_ring
            x = hw * math.cos(ang)
            z = z_c + hh * math.sin(ang)
            if z < z_c and abs(x) > 0.3 * hw:
                z = z_c + hh * 0.85 * math.sin(ang)
            verts.append([x, y, z])
    for r in range(len(sections) - 1):
        for s in range(n_ring):
            sn = (s + 1) % n_ring
            v0, v1 = r * n_ring + s, r * n_ring + sn
            v2, v3 = (r + 1) * n_ring + sn, (r + 1) * n_ring + s
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])
    tip_v = len(verts)
    verts.append([0.0, 6.62, 0.0])
    for s in range(n_ring):
        sn = (s + 1) % n_ring
        faces.append([tip_v, s, sn])
    tail_start = (len(sections) - 1) * n_ring
    tail_c = len(verts)
    verts.append([0.0, -6.60, 0.12])
    for s in range(n_ring):
        sn = (s + 1) % n_ring
        faces.append([tail_start + sn, tail_start + s, tail_c])
    fuselage_mesh = trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces))

    # B. Compound Delta Wings
    w_verts, w_faces = [], []
    stations = [
        (0.85,  1.40, 5.80, 0.32),
        (1.80,  0.20, 4.40, 0.24),
        (2.70, -1.00, 3.10, 0.18),
        (3.60, -2.20, 2.00, 0.12),
        (4.10, -2.85, 1.35, 0.08),
    ]
    for side in [-1, 1]:
        start_v = len(w_verts)
        for st_idx, (x_pos, y_le, chord, thick) in enumerate(stations):
            x = side * x_pos
            for pt in range(10):
                if pt < 5:
                    sub_f = pt / 4.0
                    y = y_le - sub_f * chord
                    z = 0.10 + thick * 2.0 * math.sqrt(max(0.0001, sub_f)) * (1.0 - sub_f)
                else:
                    sub_f = 1.0 - (pt - 5) / 4.0
                    y = y_le - sub_f * chord
                    z = 0.10 - thick * 2.0 * math.sqrt(max(0.0001, sub_f)) * (1.0 - sub_f)
                w_verts.append([x, y, z])
        for s in range(len(stations) - 1):
            for p in range(9):
                p0, p1 = start_v + s * 10 + p, start_v + s * 10 + p + 1
                p2, p3 = start_v + (s + 1) * 10 + p + 1, start_v + (s + 1) * 10 + p
                if side == 1:
                    w_faces.append([p0, p1, p2])
                    w_faces.append([p0, p2, p3])
                else:
                    w_faces.append([p0, p2, p1])
                    w_faces.append([p0, p3, p2])
    # Wingtip rails
    for side in [-1, 1]:
        rail = trimesh.creation.box(extents=[0.12, 1.60, 0.15])
        rail.apply_translation([side * 4.15, -3.20, 0.10])
        w_verts.extend(rail.vertices.tolist())
        start_idx = len(w_faces)
        base_v = len(w_verts) - len(rail.vertices)
        for f in rail.faces:
            w_faces.append((f + base_v).tolist())
    wings_mesh = trimesh.Trimesh(vertices=np.array(w_verts), faces=np.array(w_faces))

    # C. Vertical Tail
    fin_stations = [
        (0.60, -1.80, 4.40, 0.30),
        (1.20, -2.50, 3.40, 0.22),
        (1.80, -3.20, 2.40, 0.16),
        (2.40, -3.90, 1.50, 0.10),
        (2.90, -4.20, 0.90, 0.06),
    ]
    t_verts, t_faces = [], []
    for z_pos, y_le, chord, thick in fin_stations:
        for pt in range(8):
            if pt < 4:
                frac = pt / 3.0
                y = y_le - frac * chord
                x = thick * math.sin(frac * math.pi) * 0.5
            else:
                frac = 1.0 - (pt - 4) / 3.0
                y = y_le - frac * chord
                x = -thick * math.sin(frac * math.pi) * 0.5
            t_verts.append([x, y, z_pos])
    for s in range(len(fin_stations) - 1):
        for p in range(7):
            p0, p1 = s * 8 + p, s * 8 + p + 1
            p2, p3 = (s + 1) * 8 + p + 1, (s + 1) * 8 + p
            t_faces.append([p0, p1, p2])
            t_faces.append([p0, p2, p3])
    tip_start = (len(fin_stations) - 1) * 8
    tip_c = len(t_verts)
    t_verts.append([0.0, -4.50, 2.92])
    for p in range(7):
        t_faces.append([tip_start + p, tip_start + p + 1, tip_c])
    tail_mesh = trimesh.Trimesh(vertices=np.array(t_verts), faces=np.array(t_faces))

    # D. Air Intakes & Cockpit Tub
    intakes = []
    for side in [-1, 1]:
        cowl = trimesh.creation.cylinder(radius=0.38, height=2.2, sections=12)
        cowl.apply_scale([1.1, 1.0, 0.75])
        rot = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
        cowl.apply_transform(rot)
        cowl.apply_translation([side * 0.95, 1.80, 0.05])
        intakes.append(cowl)
    intakes_mesh = trimesh.util.concatenate(intakes)
    
    # Ejection Seat silhouette
    seat = trimesh.creation.box(extents=[0.42, 0.40, 0.90])
    seat.apply_translation([0.0, 3.05, 0.65])

    # Combine static airframe into body_mesh
    body_mesh = trimesh.util.concatenate([fuselage_mesh, wings_mesh, tail_mesh, intakes_mesh, seat])

    # E. Bubble Canopy Glass (Centered on fuselage)
    can_verts, can_faces = [], []
    n_r, n_s = 10, 12
    for r in range(n_r):
        frac = r / (n_r - 1)
        y = 4.60 - frac * 2.50
        arch_h = 0.58 * math.sin(frac * math.pi)
        arch_w = 0.42 * math.sin(frac * math.pi)
        z_base = 0.60 + 0.10 * frac
        for s in range(n_s):
            ang = math.pi * s / (n_s - 1)
            x = -arch_w * math.cos(ang)
            z = z_base + arch_h * math.sin(ang)
            can_verts.append([x, y, z])
    for r in range(n_r - 1):
        for s in range(n_s - 1):
            p0, p1 = r * n_s + s, r * n_s + s + 1
            p2, p3 = (r + 1) * n_s + s + 1, (r + 1) * n_s + s
            can_faces.append([p0, p1, p2])
            can_faces.append([p0, p2, p3])
    canopy_mesh = trimesh.Trimesh(vertices=np.array(can_verts), faces=np.array(can_faces))

    # F. MOVING PARTS: CENTERED AT (0,0,0) PIVOT POINTS!
    # 1. Nose Wheel Assembly (frontWheel)
    # Pivot is at [0, 3.8, -0.3] in body frame.
    # Relative to pivot: strut extends down from Z=0 to Z=-1.05, wheels at Z=-1.05.
    nw_strut = trimesh.creation.cylinder(radius=0.045, height=1.05, sections=12)
    nw_strut.apply_translation([0, 0, -0.525])
    nw_axle = trimesh.creation.cylinder(radius=0.025, height=0.32, sections=8)
    rot_x = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])
    nw_axle.apply_transform(rot_x)
    nw_axle.apply_translation([0, 0, -1.05])
    nw_wheels = []
    for side in [-1, 1]:
        w = trimesh.creation.cylinder(radius=0.20, height=0.08, sections=16)
        w.apply_transform(rot_x)
        w.apply_translation([side * 0.12, 0, -1.05])
        nw_wheels.append(w)
    front_wheel_mesh = trimesh.util.concatenate([nw_strut, nw_axle] + nw_wheels)

    # 2. Main Landing Gear Assemblies (leftGear, rightGear)
    # Pivots at [±1.2, -1.1, -0.2].
    # Relative to pivot: strut extends down to Z=-1.05, large wheel at Z=-1.05.
    def make_main_gear(side):
        mg_strut = trimesh.creation.cylinder(radius=0.06, height=1.05, sections=12)
        mg_strut.apply_translation([0, 0, -0.525])
        mg_wheel = trimesh.creation.cylinder(radius=0.32, height=0.18, sections=16)
        mg_wheel.apply_transform(rot_x)
        mg_wheel.apply_translation([side * 0.08, 0, -1.05])
        return trimesh.util.concatenate([mg_strut, mg_wheel])
    left_gear_mesh = make_main_gear(-1)
    right_gear_mesh = make_main_gear(1)

    # 3. Elevons (leftAileron, rightAileron)
    # Pivots at [±2.85, -4.6, 0.05].
    # Trailing edge control surface box extends backward (negative Y).
    def make_elevon():
        el = trimesh.creation.box(extents=[1.25, 0.70, 0.06])
        el.apply_translation([0.0, -0.35, 0.0]) # Centered at hinge line Y=0
        return el
    left_aileron_mesh = make_elevon()
    right_aileron_mesh = make_elevon()

    # 4. Rudder
    # Pivot at [0, -4.8, 1.70].
    # Extends backward (negative Y).
    rudder_mesh = trimesh.creation.box(extents=[0.06, 0.65, 1.75])
    rudder_mesh.apply_translation([0.0, -0.325, 0.0])

    # 5. Master Assembled Model (tejas_mk1.glb)
    fw_w = front_wheel_mesh.copy().apply_translation([0, 3.8, -0.3])
    lg_w = left_gear_mesh.copy().apply_translation([-1.2, -1.1, -0.2])
    rg_w = right_gear_mesh.copy().apply_translation([1.2, -1.1, -0.2])
    la_w = left_aileron_mesh.copy().apply_translation([-2.85, -4.6, 0.05])
    ra_w = right_aileron_mesh.copy().apply_translation([2.85, -4.6, 0.05])
    rud_w = rudder_mesh.copy().apply_translation([0, -4.8, 1.70])
    master_mesh = trimesh.util.concatenate([body_mesh, canopy_mesh, fw_w, lg_w, rg_w, la_w, ra_w, rud_w])

    # ---------------------------------------------------------------
    # ORIENTATION FIX: Cesium loads glTF with Y-up convention.
    # Our geometry was built with Y=forward, Z=up (GeoFS aircraft space).
    # Rotate all meshes -90° around X so:
    #   Old +Y (fuselage forward) → New -Z (glTF "forward into screen")
    #   Old +Z (up)               → New +Y (glTF "up")
    # After Cesium's Y-up→Z-up transform the aircraft lies horizontal.
    # ---------------------------------------------------------------
    rot_fix = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])
    all_meshes = {
        "body.glb": body_mesh,
        "canopy.glb": canopy_mesh,
        "frontWheel.glb": front_wheel_mesh,
        "leftGear.glb": left_gear_mesh,
        "rightGear.glb": right_gear_mesh,
        "leftAileron.glb": left_aileron_mesh,
        "rightAileron.glb": right_aileron_mesh,
        "rudder.glb": rudder_mesh,
        "tejas_mk1.glb": master_mesh,
    }
    for m in all_meshes.values():
        m.apply_transform(rot_fix)
    return all_meshes

# -------------------------------------------------------------
# 3. EXPORT glTF 2.0 WITH CORRECT PBR SHADING
# -------------------------------------------------------------
def export_and_apply_pbr(models_dict):
    print("Exporting glTF 2.0 binary models with proper PBR materials...")
    
    with open(os.path.join(TEXTURES_DIR, "tejas_diffuse.png"), "rb") as f:
        diffuse_bytes = f.read()

    for filename, mesh in models_dict.items():
        out_path = os.path.join(EXPORT_DIR, filename)
        mesh.export(out_path)
        
        gltf = pygltflib.GLTF2().load(out_path)
        blob = bytearray(gltf.binary_blob())
        
        pos_acc = gltf.accessors[gltf.meshes[0].primitives[0].attributes.POSITION]
        pos_bv = gltf.bufferViews[pos_acc.bufferView]
        pos_bytes = blob[pos_bv.byteOffset : pos_bv.byteOffset + pos_bv.byteLength]
        num_verts = pos_acc.count
        positions = np.frombuffer(pos_bytes, dtype=np.float32).reshape((num_verts, 3))
        
        # Use genuine smooth 3D vertex normals from trimesh for realistic curved specular highlights
        normals = mesh.vertex_normals.astype(np.float32)
        normals_bytes = normals.tobytes()
        
        idx_acc = gltf.accessors[gltf.meshes[0].primitives[0].indices]
        idx_bv = gltf.bufferViews[idx_acc.bufferView]
        idx_bytes = blob[idx_bv.byteOffset : idx_bv.byteOffset + idx_bv.byteLength]
        
        new_blob = bytearray()
        def append_data(data, align=4):
            pad = (align - (len(new_blob) % align)) % align
            new_blob.extend(b"\x00" * pad)
            offset = len(new_blob)
            new_blob.extend(data)
            return offset, len(data)

        offset_idx, len_idx = append_data(idx_bytes)
        offset_pos, len_pos = append_data(pos_bytes)
        offset_norm, len_norm = append_data(normals_bytes)

        if filename in ["body.glb", "tejas_mk1.glb"]:
            # Planar UV mapping matching our 2048x2048 texture atlas
            # Note: After rot_fix (-90° X), original fuselage forward (+Y) corresponds to glTF -Z (-p[2])
            uvs = np.zeros((num_verts, 2), dtype=np.float32)
            for i, p in enumerate(positions):
                u = float(np.clip((p[0] + 4.2) / 8.4, 0.0, 1.0))
                orig_y = -p[2]
                v = float(np.clip((orig_y + 6.6) / 13.2, 0.0, 1.0))
                uvs[i] = [u, v]
            uv_bytes = uvs.tobytes()
            offset_uv, len_uv = append_data(uv_bytes)
            offset_diff, len_diff = append_data(diffuse_bytes)
            
            gltf.bufferViews = [
                pygltflib.BufferView(buffer=0, byteOffset=offset_idx, byteLength=len_idx),
                pygltflib.BufferView(buffer=0, byteOffset=offset_pos, byteLength=len_pos),
                pygltflib.BufferView(buffer=0, byteOffset=offset_norm, byteLength=len_norm),
                pygltflib.BufferView(buffer=0, byteOffset=offset_uv, byteLength=len_uv),
                pygltflib.BufferView(buffer=0, byteOffset=offset_diff, byteLength=len_diff),
            ]
            gltf.accessors = [
                pygltflib.Accessor(bufferView=0, byteOffset=0, componentType=idx_acc.componentType, count=idx_acc.count, type="SCALAR", max=idx_acc.max, min=idx_acc.min),
                pygltflib.Accessor(bufferView=1, byteOffset=0, componentType=pygltflib.FLOAT, count=num_verts, type="VEC3", max=pos_acc.max, min=pos_acc.min),
                pygltflib.Accessor(bufferView=2, byteOffset=0, componentType=pygltflib.FLOAT, count=num_verts, type="VEC3", max=[1.0, 1.0, 1.0], min=[-1.0, -1.0, -1.0]),
                pygltflib.Accessor(bufferView=3, byteOffset=0, componentType=pygltflib.FLOAT, count=num_verts, type="VEC2", max=[1.0, 1.0], min=[0.0, 0.0]),
            ]
            gltf.images = [pygltflib.Image(mimeType="image/png", bufferView=4)]
            gltf.samplers = [pygltflib.Sampler(magFilter=pygltflib.LINEAR, minFilter=pygltflib.LINEAR_MIPMAP_LINEAR, wrapS=pygltflib.REPEAT, wrapT=pygltflib.REPEAT)]
            gltf.textures = [pygltflib.Texture(sampler=0, source=0)]
            
            # Non-metallic dielectric military paint (metallic=0.05, roughness=0.35 for realistic sheen)
            gltf.materials = [
                pygltflib.Material(
                    name="HAL_Tejas_Airframe",
                    pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                        baseColorTexture=pygltflib.TextureInfo(index=0, texCoord=0),
                        baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                        roughnessFactor=0.35,
                        metallicFactor=0.05
                    ),
                    doubleSided=True
                )
            ]
            gltf.meshes[0].primitives[0].attributes.NORMAL = 2
            gltf.meshes[0].primitives[0].attributes.TEXCOORD_0 = 3
            gltf.meshes[0].primitives[0].material = 0
        else:
            # Clean solid PBR materials for moving parts & canopy
            gltf.bufferViews = [
                pygltflib.BufferView(buffer=0, byteOffset=offset_idx, byteLength=len_idx),
                pygltflib.BufferView(buffer=0, byteOffset=offset_pos, byteLength=len_pos),
                pygltflib.BufferView(buffer=0, byteOffset=offset_norm, byteLength=len_norm),
            ]
            gltf.accessors = [
                pygltflib.Accessor(bufferView=0, byteOffset=0, componentType=idx_acc.componentType, count=idx_acc.count, type="SCALAR", max=idx_acc.max, min=idx_acc.min),
                pygltflib.Accessor(bufferView=1, byteOffset=0, componentType=pygltflib.FLOAT, count=num_verts, type="VEC3", max=pos_acc.max, min=pos_acc.min),
                pygltflib.Accessor(bufferView=2, byteOffset=0, componentType=pygltflib.FLOAT, count=num_verts, type="VEC3", max=[1.0, 1.0, 1.0], min=[-1.0, -1.0, -1.0]),
            ]
            gltf.images = []
            gltf.textures = []
            
            if filename == "canopy.glb":
                color = [0.20, 0.28, 0.38, 0.65] # Transparent tinted sky-blue canopy glass
                roughness = 0.05
                metallic = 0.1
                alpha_mode = "BLEND"
            elif "Gear" in filename or "Wheel" in filename:
                color = [0.25, 0.27, 0.30, 1.0] # Dark titanium strut & rubber tire
                roughness = 0.50
                metallic = 0.4
                alpha_mode = "OPAQUE"
            else: # Elevons and rudder
                color = [0.65, 0.70, 0.75, 1.0] # IAF Ghost Grey
                roughness = 0.42
                metallic = 0.05
                alpha_mode = "OPAQUE"
                
            gltf.materials = [
                pygltflib.Material(
                    name=filename.replace(".glb", "_Mat"),
                    pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                        baseColorFactor=color,
                        roughnessFactor=roughness,
                        metallicFactor=metallic
                    ),
                    alphaMode=alpha_mode,
                    doubleSided=True
                )
            ]
            gltf.meshes[0].primitives[0].attributes.NORMAL = 2
            gltf.meshes[0].primitives[0].attributes.TEXCOORD_0 = None
            gltf.meshes[0].primitives[0].material = 0

        gltf.set_binary_blob(bytes(new_blob))
        gltf.buffers[0].byteLength = len(new_blob)
        gltf.save(out_path)
        print(f"  [x] Saved {filename:<16} ({len(new_blob)/1024:6.1f} KB)")

# -------------------------------------------------------------
# 4. UPDATE GEOFS AIRCRAFT DEFINITION (POSITIONING & FLIGHT DYNAMICS)
# -------------------------------------------------------------
def update_definition():
    print("Updating GeoFS aircraft definition with correct gear elevations...")
    definition = [
        {
            "name": "HAL Tejas Mk1",
            "description": "HAL Tejas Mk1 single-engine tailless compound-delta fighter of the Indian Air Force",
            "scale": 1,
            "mass": 6560,
            "tensorFactor": 0.02,
            "dragFactor": 1.25,
            "com": [0, -0.5, 0],
            "gearTravelTime": 5,
            "flapsTravelTime": 0,
            "flapsSteps": 0,
            "airbrakesTravelTime": 1.2,
            "brakeDamping": 8,
            "zeroThrustAltitude": 55000,
            "reverse": False,
            "minRPM": 1000,
            "maxRPM": 10000,
            "driveRatio": 0.3,
            "engineInertia": 0.8,
            "startupTime": 8,
            "startAltitude": 1.6, # Height of fuselage above runway when resting on gear
            "startTilt": 0,
            "minimumSpeed": 115,
            "cockpitScaleFix": 1,
            "autopilot": True,
            "contactProperties": {
                "wheel": { "frictionCoef": 2.0, "dynamicFriction": 0.01, "rollingFriction": 0.0001, "lockSpeed": 0.01, "damping": 1 },
                "frame": { "frictionCoef": 1.4, "dynamicFriction": 0.01, "damping": 1 },
                "airfoil": { "frictionCoef": 1.4, "dynamicFriction": 0.01, "damping": 1 }
            },
            "instruments": {
                "airspeedJet": "", "altitude": "", "attitudeJet": "", "varioJet": "",
                "compass": "", "rpmJet": "", "brakes": "", "gear": ""
            },
            "cameras": {
                "cockpit": { "position": [0, 2.8, 0.95], "orientation": [0, -4, 0] },
                "follow": { "distance": 28 },
                "Right Wing": { "position": [4.2, -3.2, 0.4], "orientation": [-135, -5, 0] },
                "Left Wing": { "position": [-4.2, -3.2, 0.4], "orientation": [135, -5, 0] },
                "Nose Gear": { "position": [0, 5.0, -0.6], "orientation": [-180, -10, 0] }
            },
            "parts": [
                {
                    "name": "body",
                    "model": "body.glb",
                    "collisionPoints": [
                        [0, 6.0, 0.0],
                        [0, -6.6, 0.12],
                        [-4.1, -3.2, 0.1],
                        [4.1, -3.2, 0.1],
                        [0, -1.5, -0.45] # Belly contact point (well above ground when gear is down!)
                    ]
                },
                {
                    "name": "canopy",
                    "parent": "body",
                    "model": "canopy.glb"
                },
                {
                    "name": "mainWingLeft",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [-1.8, -1.5, 0.1],
                    "area": 17.0,
                    "aspectRatio": 1.75,
                    "stalls": True,
                    "stallIncidence": 24,
                    "forceDirection": "Z",
                    "points": { "forceSourcePoint": [0, 0, 0] }
                },
                {
                    "name": "mainWingRight",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [1.8, -1.5, 0.1],
                    "area": 17.0,
                    "aspectRatio": 1.75,
                    "stalls": True,
                    "stallIncidence": 24,
                    "forceDirection": "Z",
                    "points": { "forceSourcePoint": [0, 0, 0] }
                },
                {
                    "name": "verticalFin",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [0, -3.4, 1.75],
                    "area": 5.2,
                    "aspectRatio": 1.4,
                    "stalls": True,
                    "forceDirection": "X",
                    "points": { "forceSourcePoint": [0, 0, 0] }
                },
                {
                    "name": "leftAileron",
                    "parent": "body",
                    "type": "airfoil",
                    "model": "leftAileron.glb",
                    "position": [-2.85, -4.6, 0.05],
                    "area": 2.2,
                    "forceDirection": "Z",
                    "points": { "forceSourcePoint": [0, 0, 0] },
                    "animations": [
                        { "type": "rotate", "axis": "X", "value": "roll", "ratio": -25 },
                        { "type": "rotate", "axis": "X", "value": "pitch", "ratio": 20 }
                    ]
                },
                {
                    "name": "rightAileron",
                    "parent": "body",
                    "type": "airfoil",
                    "model": "rightAileron.glb",
                    "position": [2.85, -4.6, 0.05],
                    "area": 2.2,
                    "forceDirection": "Z",
                    "points": { "forceSourcePoint": [0, 0, 0] },
                    "animations": [
                        { "type": "rotate", "axis": "X", "value": "roll", "ratio": 25 },
                        { "type": "rotate", "axis": "X", "value": "pitch", "ratio": 20 }
                    ]
                },
                {
                    "name": "rudder",
                    "parent": "body",
                    "type": "airfoil",
                    "model": "rudder.glb",
                    "position": [0, -4.8, 1.70],
                    "area": 1.8,
                    "forceDirection": "X",
                    "points": { "forceSourcePoint": [0, 0, 0] },
                    "animations": [
                        { "type": "rotate", "axis": "Z", "value": "yaw", "ratio": -25 }
                    ]
                },
                {
                    "name": "engine",
                    "type": "engine",
                    "thrust": 84000,
                    "forceDirection": "Y",
                    "points": { "forceSourcePoint": [0, -6.6, 0.0] }
                },
                # Landing Gear: Pivots attach to underside of fuselage, collision points define tire ground contact
                {
                    "name": "frontWheel",
                    "parent": "body",
                    "type": "wheel",
                    "model": "frontWheel.glb",
                    "position": [0, 3.8, -0.3], # Attached under nose
                    "collisionPoints": [
                        [0, 0, -1.25] # Tire contacts runway 1.25m below pivot (Ground Z = -1.55m in body frame)
                    ],
                    "suspension": { "stiffness": 28, "damping": 6 },
                    "animations": [
                        { "type": "rotate", "axis": "Z", "value": "yaw", "ratio": 16 },
                        { "type": "rotate", "axis": "X", "value": "gearPosition", "ratio": -95 },
                        { "type": "hide", "value": "gearPosition", "threshold": 0.98 }
                    ]
                },
                {
                    "name": "leftGear",
                    "parent": "body",
                    "type": "wheel",
                    "model": "leftGear.glb",
                    "position": [-1.2, -1.1, -0.2], # Attached under port wing root
                    "collisionPoints": [
                        [0, 0, -1.35] # Tire contacts runway 1.35m below pivot (Ground Z = -1.55m in body frame)
                    ],
                    "suspension": { "stiffness": 38, "damping": 7 },
                    "animations": [
                        { "type": "rotate", "axis": "Y", "value": "gearPosition", "ratio": 85 },
                        { "type": "hide", "value": "gearPosition", "threshold": 0.98 }
                    ]
                },
                {
                    "name": "rightGear",
                    "parent": "body",
                    "type": "wheel",
                    "model": "rightGear.glb",
                    "position": [1.2, -1.1, -0.2], # Attached under starboard wing root
                    "collisionPoints": [
                        [0, 0, -1.35] # Tire contacts runway 1.35m below pivot (Ground Z = -1.55m in body frame)
                    ],
                    "suspension": { "stiffness": 38, "damping": 7 },
                    "animations": [
                        { "type": "rotate", "axis": "Y", "value": "gearPosition", "ratio": -85 },
                        { "type": "hide", "value": "gearPosition", "threshold": 0.98 }
                    ]
                }
            ]
        }
    ]
    
    with open(os.path.join(BASE_DIR, "aircraft.json"), "w", encoding="utf-8") as f:
        json.dump(definition, f, indent=2)
    with open(os.path.join(BASE_DIR, "definition.json"), "w", encoding="utf-8") as f:
        json.dump(definition, f, indent=2)
    print("  [x] Saved updated aircraft.json & definition.json")
    return definition

# -------------------------------------------------------------
# 5. COMPILE SELF-CONTAINED geofs_test_loader.js
# -------------------------------------------------------------
def compile_loader(definition):
    print("Compiling self-contained geofs_test_loader.js...")
    parts = ["body.glb", "canopy.glb", "frontWheel.glb", "leftGear.glb", "rightGear.glb", "leftAileron.glb", "rightAileron.glb", "rudder.glb"]
    model_b64 = {}
    for p in parts:
        with open(os.path.join(EXPORT_DIR, p), "rb") as f:
            model_b64[p] = base64.b64encode(f.read()).decode("ascii")

    def_json_str = json.dumps(definition)
    models_json_str = json.dumps(model_b64)

    loader_code = f"""/**
 * HAL TEJAS Mk1 — STANDALONE GEOFS FLIGHT TEST LOADER
 * Updated: Ground elevation calibrated & PBR sunlight shading enhanced.
 */
(function loadTejasInGeoFS() {{
    console.log("%c[HAL TEJAS Mk1] INJECTING CALIBRATED AIRCRAFT...", "color: #ff9933; font-weight: bold; font-size: 14px;");

    if (!window.geofs || !geofs.aircraft || !geofs.aircraft.instance) {{
        alert("[HAL TEJAS Mk1] GeoFS simulator not detected! Make sure you are on https://www.geo-fs.com/geofs.php");
        return;
    }}

    try {{
        function b64ToBlobUrl(b64) {{
            const bin = atob(b64);
            const len = bin.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
            return URL.createObjectURL(new Blob([bytes], {{ type: "model/gltf-binary" }}));
        }}

        const modelData = {models_json_str};
        const blobUrls = {{}};
        for (const [filename, b64] of Object.entries(modelData)) {{
            blobUrls[filename] = b64ToBlobUrl(b64);
        }}

        const definition = {def_json_str};
        const tejasDef = definition[0];
        tejasDef.parts.forEach(part => {{
            if (part.model && blobUrls[part.model]) {{
                part.model = blobUrls[part.model];
            }}
        }});

        const customRecord = {{
            id: "custom_" + Date.now(),
            name: "HAL Tejas Mk1 (Indian Air Force)",
            fullPath: "",
            isPremium: false,
            isCommunity: false,
            definition: btoa(JSON.stringify([tejasDef])),
            multiplayerFiles: []
        }};

        const parsedDefinition = geofs.aircraft.instance.parseRecord(JSON.stringify(customRecord));
        if (!parsedDefinition) throw new Error("Failed to parse definition.");

        const currentCoords = geofs.aircraft.instance.getCurrentCoordinates();
        if (typeof geofs.aircraft.instance.unloadAircraft === "function") {{
            geofs.aircraft.instance.unloadAircraft();
        }}

        geofs.aircraft.instance.fullPath = customRecord.fullPath;
        geofs.aircraft.instance.aircraftRecord = customRecord;
        geofs.aircraft.instance.init(parsedDefinition, currentCoords);

        if (geofs.flyToNotification) {{
            geofs.flyToNotification("HAL Tejas Mk1 Active! Press '0'-'9' for Reheat, 'G' for Gear, 'C' for Cockpit.");
        }}
        console.log("%c[HAL TEJAS Mk1] READY FOR FLIGHT! ENJOY!", "color: #138808; font-weight: bold; font-size: 15px;");
    }} catch (err) {{
        console.error("[HAL TEJAS Mk1] Error:", err);
        alert("[HAL TEJAS Mk1] " + err.message);
    }}
}})();
"""
    out_loader = os.path.join(BASE_DIR, "geofs_test_loader.js")
    with open(out_loader, "w", encoding="utf-8") as f:
        f.write(loader_code)
    print(f"  [x] Saved updated loader: {out_loader} ({os.path.getsize(out_loader)/1024:.1f} KB)")

if __name__ == "__main__":
    generate_aligned_texture()
    models = build_all_models()
    export_and_apply_pbr(models)
    definition = update_definition()
    compile_loader(definition)
    print("\n>>> ALL REFINEMENTS COMPLETE! Ready for testing.")
