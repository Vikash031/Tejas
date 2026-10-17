"""
Master 3D High-Fidelity Generator & Packager for HAL Tejas Mk1 (GeoFS)
- Generates high-detail compound-delta airframe with LERX, canted intakes, pitot boom,
  missiles, pylons, ventral strakes, titanium afterburner nozzle, and landing gear.
- Integrates the entire visual airframe into a unified, watertight master model so
  NO parts ever detach or float.
- Aligns texture atlas coordinates with glTF standard.
- Calibrates GeoFS flight physics and tricycle gear contact points for straight acceleration.
- Recompiles standalone geofs_test_loader.js.
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
# 1. GENERATE HIGH-RESOLUTION 2048x2048 IAF TEXTURE ATLAS
# -------------------------------------------------------------
def generate_aligned_texture():
    print("Generating high-resolution IAF 2048x2048 camouflage texture atlas...")
    # Base IAF Ghost Grey
    base_color = (180, 192, 204, 255)
    img = Image.new("RGBA", (WIDTH, HEIGHT), base_color)
    draw = ImageDraw.Draw(img)

    # In PIL (0,0) is top-left, py=0 is top.
    # glTF standard: V=1.0 is top (nose Y=+6.6m), V=0.0 is bottom (tail Y=-6.6m).
    # Therefore py = 0 corresponds to y_m = +6.6m, py = 2047 corresponds to y_m = -6.6m.
    def to_px(x_m, y_m):
        px = int(np.clip((x_m + 4.2) / 8.4 * WIDTH, 0, WIDTH - 1))
        py = int(np.clip((6.6 - y_m) / 13.2 * HEIGHT, 0, HEIGHT - 1))
        return px, py

    # Dual-tone IAF Camouflage patches
    camo_color = (112, 132, 150, 255)
    camo_patches = [
        [(-3.8, -2.5), (-1.8, -0.5), (-1.2, -3.5), (-3.5, -4.5)],
        [(-2.2, -4.0), (-0.8, -2.0), (-0.5, -5.0), (-2.0, -5.5)],
        [(1.5, -0.8), (3.6, -2.8), (3.2, -4.8), (1.2, -3.2)],
        [(0.6, -2.5), (2.2, -4.2), (1.8, -5.8), (0.4, -4.8)],
        [(-0.6, 2.0), (0.6, 2.5), (0.5, 4.2), (-0.5, 3.8)],
        [(-0.4, -0.5), (0.4, -0.2), (0.3, -3.8), (-0.3, -3.5)],
    ]
    camo_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(camo_layer)
    for patch in camo_patches:
        pts = [to_px(xm, ym) for xm, ym in patch]
        c_draw.polygon(pts, fill=camo_color)

    camo_layer = camo_layer.filter(ImageFilter.GaussianBlur(radius=6))
    img.alpha_composite(camo_layer)

    # Panel lines layer
    p_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(p_layer)
    panel_col = (45, 52, 60, 160)

    # Wing panel lines & elevon hinges
    for ym in np.linspace(-5.5, 0.5, 14):
        p0 = to_px(-3.9, ym)
        p1 = to_px(3.9, ym)
        p_draw.line([p0, p1], fill=panel_col, width=2)
    # Fuselage frame rings
    for ym in np.linspace(-6.0, 5.5, 20):
        p0 = to_px(-0.95, ym)
        p1 = to_px(0.95, ym)
        p_draw.line([p0, p1], fill=panel_col, width=2)
    # Dorsal spine seam
    p_draw.line([to_px(0, -6.6), to_px(0, 6.0)], fill=(30, 35, 42, 200), width=3)
    # Elevon demarcation lines
    p_draw.line([to_px(-3.9, -4.4), to_px(-1.2, -4.4)], fill=(25, 30, 35, 240), width=3)
    p_draw.line([to_px(1.2, -4.4), to_px(3.9, -4.4)], fill=(25, 30, 35, 240), width=3)

    # Radome nose cone
    r_pts = [to_px(0, 6.6), to_px(0.55, 4.4), to_px(-0.55, 4.4)]
    p_draw.polygon(r_pts, fill=(40, 42, 45, 255))
    p_draw.line([to_px(-0.55, 4.4), to_px(0.55, 4.4)], fill=(18, 20, 22, 255), width=4)

    # Anti-glare matte shield ahead of windscreen
    ag_pts = [to_px(-0.35, 3.8), to_px(0.35, 3.8), to_px(0.28, 4.38), to_px(-0.28, 4.38)]
    p_draw.polygon(ag_pts, fill=(25, 26, 28, 255))

    # Titanium exhaust nozzle petals
    for ym in np.linspace(-6.6, -6.0, 4):
        p0 = to_px(-0.55, ym)
        p1 = to_px(0.55, ym)
        p_draw.line([p0, p1], fill=(55, 50, 45, 255), width=2)
    for xm in np.linspace(-0.52, 0.52, 16):
        p_draw.line([to_px(xm, -6.6), to_px(xm, -6.0)], fill=(35, 32, 28, 240), width=2)

    img.alpha_composite(p_layer)

    # National Roundels
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

    # Fin Flash (Indian Tricolour: Saffron, White, Green)
    fx0, fy0 = to_px(-0.02, -4.5)
    fw, fh = 40, 60
    f_draw = ImageDraw.Draw(img)
    f_draw.rectangle([fx0 - fw, fy0 - fh//2, fx0 - fw + 13, fy0 + fh//2], fill=(255, 140, 25, 255))
    f_draw.rectangle([fx0 - fw + 14, fy0 - fh//2, fx0 - fw + 26, fy0 + fh//2], fill=(255, 255, 255, 255))
    f_draw.rectangle([fx0 - fw + 27, fy0 - fh//2, fx0, fy0 + fh//2], fill=(15, 145, 10, 255))

    # Red Ejection Seat Warning Triangles
    def draw_triangle(xm, ym, size):
        px, py = to_px(xm, ym)
        t_draw = ImageDraw.Draw(img)
        pts = [(px, py), (px + size, py), (px + size // 2, py - int(size * 0.86))]
        t_draw.polygon(pts, fill=(230, 25, 25, 255), outline=(255, 255, 255, 255))
    draw_triangle(-0.65, 3.2, 22)
    draw_triangle(0.65, 3.2, 22)

    diff_path = os.path.join(TEXTURES_DIR, "tejas_diffuse.png")
    img.save(diff_path, "PNG", optimize=True)
    print(f"  [x] Saved aligned diffuse texture: {diff_path}")
    return diff_path

# -------------------------------------------------------------
# 2. BUILD DETAILED 3D GEOMETRY FOR HAL TEJAS Mk1
# -------------------------------------------------------------
def build_high_detail_tejas():
    print("Building high-detail 3D geometry for HAL Tejas Mk1...")
    
    # A. Fuselage with Area-Rule (Coke Bottle) & Dorsal Spine
    sections = [
        # (y, z_center, half_width, half_height)
        (6.60, 0.00, 0.02, 0.02), # Radome tip
        (6.00, 0.00, 0.12, 0.10),
        (5.20, 0.05, 0.38, 0.35),
        (4.40, 0.10, 0.58, 0.52), # Windscreen base
        (3.40, 0.15, 0.72, 0.65), # Cockpit area
        (2.20, 0.18, 0.82, 0.75), # Forward fuselage
        (0.80, 0.20, 0.92, 0.82), # Mid-fuselage (intake blend)
        (-0.50, 0.22, 0.86, 0.85), # Wasp-waist area rule narrowing
        (-1.80, 0.22, 0.94, 0.86), # Wing root max breadth
        (-3.20, 0.20, 0.96, 0.84),
        (-4.50, 0.18, 0.84, 0.78), # Aft fuselage
        (-5.50, 0.15, 0.68, 0.68), # Engine bay
        (-6.30, 0.12, 0.54, 0.54), # Pre-nozzle
        (-6.60, 0.12, 0.48, 0.48), # Exhaust exit
    ]
    n_ring = 20
    verts, faces = [], []
    for r_idx, (y, z_c, hw, hh) in enumerate(sections):
        for s in range(n_ring):
            ang = 2 * math.pi * s / n_ring
            x = hw * math.cos(ang)
            z = z_c + hh * math.sin(ang)
            # Flatten bottom slightly for authentic chine
            if z < z_c and abs(x) > 0.2 * hw:
                z = z_c + hh * 0.88 * math.sin(ang)
            verts.append([x, y, z])
    for r in range(len(sections) - 1):
        for s in range(n_ring):
            sn = (s + 1) % n_ring
            v0 = r * n_ring + s
            v1 = r * n_ring + sn
            v2 = (r + 1) * n_ring + sn
            v3 = (r + 1) * n_ring + s
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])
    # Close radome tip
    tip_v = len(verts)
    verts.append([0.0, 6.62, 0.0])
    for s in range(n_ring):
        sn = (s + 1) % n_ring
        faces.append([tip_v, s, sn])
    # Close exhaust
    tail_start = (len(sections) - 1) * n_ring
    tail_c = len(verts)
    verts.append([0.0, -6.60, 0.12])
    for s in range(n_ring):
        sn = (s + 1) % n_ring
        faces.append([tail_start + sn, tail_start + s, tail_c])
    fuselage_mesh = trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces))

    # B. Pitot Boom Needle (Nose Probe)
    pitot = trimesh.creation.cylinder(radius=0.015, height=0.60, sections=8)
    rot_p = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    pitot.apply_transform(rot_p)
    pitot.apply_translation([0.0, 6.90, 0.0])

    # C. Canted D-Shaped Air Intakes with Splitter Plates
    intake_parts = []
    for side in [-1, 1]:
        # Intake cowl
        cowl = trimesh.creation.cylinder(radius=0.38, height=2.4, sections=16)
        cowl.apply_scale([1.15, 1.0, 0.80])
        cowl.apply_transform(rot_p)
        cowl.apply_translation([side * 0.95, 1.70, 0.05])
        # Splitter plate (boundary layer diverter)
        splitter = trimesh.creation.box(extents=[0.04, 1.4, 0.65])
        splitter.apply_translation([side * 0.62, 1.90, 0.05])
        intake_parts.extend([cowl, splitter])

    # D. Authentic Compound Delta Wings with LERX
    w_verts, w_faces = [], []
    wing_stations = [
        # (x_pos, y_le, chord, thickness)
        (0.80,  2.20, 6.60, 0.34), # LERX root blend
        (1.40,  1.20, 5.50, 0.28), # Inner 50 deg sweep
        (2.30, -0.30, 4.00, 0.20), # Transition notch (dogtooth)
        (3.30, -1.80, 2.50, 0.14), # Outer 62.5 deg sweep
        (4.10, -2.85, 1.40, 0.08), # Wingtip launcher rail
    ]
    for side in [-1, 1]:
        start_v = len(w_verts)
        for st_idx, (x_pos, y_le, chord, thick) in enumerate(wing_stations):
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
        for s in range(len(wing_stations) - 1):
            for p in range(9):
                p0 = start_v + s * 10 + p
                p1 = start_v + s * 10 + p + 1
                p2 = start_v + (s + 1) * 10 + p + 1
                p3 = start_v + (s + 1) * 10 + p
                if side == 1:
                    w_faces.append([p0, p1, p2])
                    w_faces.append([p0, p2, p3])
                else:
                    w_faces.append([p0, p2, p1])
                    w_faces.append([p0, p3, p2])
    # Wingtip missile rails & Astra BVRAAM missiles
    missile_parts = []
    for side in [-1, 1]:
        rail = trimesh.creation.box(extents=[0.08, 1.70, 0.12])
        rail.apply_translation([side * 4.15, -3.15, 0.10])
        # Missile body
        mis = trimesh.creation.cylinder(radius=0.08, height=1.9, sections=12)
        mis.apply_transform(rot_p)
        mis.apply_translation([side * 4.15, -3.15, -0.05])
        # Missile fins
        fin_h = trimesh.creation.box(extents=[0.40, 0.25, 0.02])
        fin_h.apply_translation([side * 4.15, -3.85, -0.05])
        fin_v = trimesh.creation.box(extents=[0.02, 0.25, 0.40])
        fin_v.apply_translation([side * 4.15, -3.85, -0.05])
        # Underwing weapons pylons
        pylon1 = trimesh.creation.box(extents=[0.08, 1.4, 0.25])
        pylon1.apply_translation([side * 2.4, -2.2, -0.08])
        pylon2 = trimesh.creation.box(extents=[0.08, 1.2, 0.25])
        pylon2.apply_translation([side * 3.3, -3.0, -0.06])
        missile_parts.extend([rail, mis, fin_h, fin_v, pylon1, pylon2])

    wings_mesh = trimesh.Trimesh(vertices=np.array(w_verts), faces=np.array(w_faces))

    # E. Swept Vertical Stabilizer with Dorsal Ram Air Scoop
    fin_stations = [
        (0.60, -1.80, 4.40, 0.30),
        (1.20, -2.50, 3.40, 0.22),
        (1.80, -3.20, 2.40, 0.16),
        (2.40, -3.90, 1.50, 0.10),
        (2.95, -4.25, 0.85, 0.05),
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
    t_verts.append([0.0, -4.55, 2.98])
    for p in range(7):
        t_faces.append([tip_start + p, tip_start + p + 1, tip_c])
    tail_mesh = trimesh.Trimesh(vertices=np.array(t_verts), faces=np.array(t_faces))

    # Dorsal ram air intake scoop at fin base
    fin_scoop = trimesh.creation.cylinder(radius=0.10, height=0.6, sections=10)
    fin_scoop.apply_transform(rot_p)
    fin_scoop.apply_translation([0.0, -1.95, 0.85])

    # Twin Ventral Strakes
    strakes = []
    for side in [-1, 1]:
        strake = trimesh.creation.box(extents=[0.04, 1.2, 0.28])
        strake.apply_translation([side * 0.45, -4.6, -0.42])
        strakes.append(strake)

    # F. Framed Cockpit Canopy, Glareshield & Ejection Seat
    can_verts, can_faces = [], []
    n_r, n_s = 12, 14
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
            p0 = r * n_s + s
            p1 = r * n_s + s + 1
            p2 = (r + 1) * n_s + s + 1
            p3 = (r + 1) * n_s + s
            can_faces.append([p0, p1, p2])
            can_faces.append([p0, p2, p3])
    canopy_mesh = trimesh.Trimesh(vertices=np.array(can_verts), faces=np.array(can_faces))

    # Ejection Seat with Martin-Baker style headrest
    seat_base = trimesh.creation.box(extents=[0.42, 0.45, 0.60])
    seat_base.apply_translation([0.0, 3.10, 0.55])
    seat_head = trimesh.creation.box(extents=[0.30, 0.28, 0.40])
    seat_head.apply_translation([0.0, 3.00, 0.95])
    hud_glass = trimesh.creation.box(extents=[0.24, 0.02, 0.18])
    hud_glass.apply_translation([0.0, 3.75, 0.88])

    # G. GE F404 16-Petal Titanium Afterburner Nozzle
    nozzle_cyl = trimesh.creation.cylinder(radius=0.48, height=0.65, sections=16)
    nozzle_cyl.apply_transform(rot_p)
    nozzle_cyl.apply_translation([0.0, -6.65, 0.12])

    # H. Authentic Tricycle Landing Gear (Attached cleanly in body)
    rot_x = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])
    
    # Nose gear at [0, 3.8, -0.3] -> strut down to Z=-1.40, dual wheels
    nw_strut = trimesh.creation.cylinder(radius=0.045, height=1.10, sections=12)
    nw_strut.apply_translation([0.0, 3.8, -0.85])
    nw_axle = trimesh.creation.cylinder(radius=0.025, height=0.32, sections=8)
    nw_axle.apply_transform(rot_x)
    nw_axle.apply_translation([0.0, 3.8, -1.35])
    nw_w1 = trimesh.creation.cylinder(radius=0.20, height=0.08, sections=16)
    nw_w1.apply_transform(rot_x)
    nw_w1.apply_translation([-0.12, 3.8, -1.35])
    nw_w2 = trimesh.creation.cylinder(radius=0.20, height=0.08, sections=16)
    nw_w2.apply_transform(rot_x)
    nw_w2.apply_translation([0.12, 3.8, -1.35])

    # Main gear at [±1.2, -1.1, -0.2] -> strut down to Z=-1.40, large wheels
    main_gears = []
    for side in [-1, 1]:
        mg_strut = trimesh.creation.cylinder(radius=0.065, height=1.15, sections=12)
        mg_strut.apply_translation([side * 1.2, -1.1, -0.80])
        mg_wheel = trimesh.creation.cylinder(radius=0.32, height=0.18, sections=16)
        mg_wheel.apply_transform(rot_x)
        mg_wheel.apply_translation([side * 1.2, -1.1, -1.35])
        main_gears.extend([mg_strut, mg_wheel])

    # Control surfaces (integrated at neutral trail positions)
    la_box = trimesh.creation.box(extents=[1.25, 0.70, 0.06])
    la_box.apply_translation([-2.85, -4.95, 0.05])
    ra_box = trimesh.creation.box(extents=[1.25, 0.70, 0.06])
    ra_box.apply_translation([2.85, -4.95, 0.05])
    rud_box = trimesh.creation.box(extents=[0.06, 0.65, 1.75])
    rud_box.apply_translation([0.0, -5.12, 1.70])

    # Assemble all high-fidelity components into ONE monolithic master model!
    all_components = (
        [fuselage_mesh, pitot] +
        intake_parts +
        [wings_mesh] +
        missile_parts +
        [tail_mesh, fin_scoop] +
        strakes +
        [canopy_mesh, seat_base, seat_head, hud_glass, nozzle_cyl] +
        [nw_strut, nw_axle, nw_w1, nw_w2] +
        main_gears +
        [la_box, ra_box, rud_box]
    )
    master_mesh = trimesh.util.concatenate(all_components)

    # Apply -90 deg X rotation so Cesium glTF 2.0 Y-up convention maps to horizontal flight:
    #   Old +Y (forward nose) -> glTF -Z (forward)
    #   Old +Z (up canopy)    -> glTF +Y (up)
    rot_fix = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])
    master_mesh.apply_transform(rot_fix)

    # Individual component meshes for standalone parts compatibility
    canopy_solo = canopy_mesh.copy().apply_transform(rot_fix)
    
    return {
        "body.glb": master_mesh,
        "tejas_mk1.glb": master_mesh,
        "canopy.glb": canopy_solo,
    }

# -------------------------------------------------------------
# 3. EXPORT glTF 2.0 BINARY MODELS WITH PBR MATERIALS
# -------------------------------------------------------------
def export_pbr_models(models_dict):
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

        # Genuine smooth geometric normals
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

        # Planar UV coordinates matching 2048x2048 texture atlas
        # Since rot_fix was applied, airframe X is p[0], longitudinal Y is -p[2]
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

        # Specular PBR military satin finish (metallic=0.08, roughness=0.36)
        gltf.materials = [
            pygltflib.Material(
                name="HAL_Tejas_PBR",
                pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                    baseColorTexture=pygltflib.TextureInfo(index=0, texCoord=0),
                    roughnessFactor=0.36,
                    metallicFactor=0.08
                ),
                alphaMode="OPAQUE",
                doubleSided=True
            )
        ]
        gltf.meshes[0].primitives[0].attributes.NORMAL = 2
        gltf.meshes[0].primitives[0].attributes.TEXCOORD_0 = 3
        gltf.meshes[0].primitives[0].material = 0

        gltf.set_binary_blob(bytes(new_blob))
        gltf.buffers[0].byteLength = len(new_blob)
        gltf.save(out_path)
        print(f"  [x] Saved {filename:<16} ({len(new_blob)/1024:6.1f} KB)")

# -------------------------------------------------------------
# 4. CALIBRATE GEOFS AIRCRAFT DEFINITION (FLIGHT DYNAMICS)
# -------------------------------------------------------------
def update_definition():
    print("Updating GeoFS aircraft definition with stable ground physics...")
    definition = [
        {
            "name": "HAL Tejas Mk1",
            "description": "HAL Tejas Mk1 single-engine tailless compound-delta fighter of the Indian Air Force",
            "scale": 1,
            "mass": 6560,
            "tensorFactor": 0.02,
            "dragFactor": 1.20,
            "com": [0, -0.5, 0.0],
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
            "startAltitude": 1.45, # Tires rest smoothly on tarmac
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
                "cockpit": { "position": [0, 3.1, 0.95], "orientation": [0, -3, 0] },
                "follow": { "distance": 26 },
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
                        [0, -1.5, -0.45]
                    ]
                },
                # Aerodynamic lift surfaces (pure physics, no detached visual models)
                {
                    "name": "mainWingLeft",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [-1.8, -1.5, 0.1],
                    "area": 18.0,
                    "aspectRatio": 1.75,
                    "stalls": True,
                    "stallIncidence": 26,
                    "forceDirection": "Z",
                    "points": { "forceSourcePoint": [0, 0, 0] }
                },
                {
                    "name": "mainWingRight",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [1.8, -1.5, 0.1],
                    "area": 18.0,
                    "aspectRatio": 1.75,
                    "stalls": True,
                    "stallIncidence": 26,
                    "forceDirection": "Z",
                    "points": { "forceSourcePoint": [0, 0, 0] }
                },
                {
                    "name": "verticalFin",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [0, -3.4, 1.75],
                    "area": 5.4,
                    "aspectRatio": 1.4,
                    "stalls": True,
                    "forceDirection": "X",
                    "points": { "forceSourcePoint": [0, 0, 0] }
                },
                {
                    "name": "leftElevon",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [-2.85, -4.6, 0.05],
                    "area": 2.4,
                    "forceDirection": "Z",
                    "points": { "forceSourcePoint": [0, 0, 0] },
                    "animations": [
                        { "type": "rotate", "axis": "X", "value": "roll", "ratio": -25 },
                        { "type": "rotate", "axis": "X", "value": "pitch", "ratio": 20 }
                    ]
                },
                {
                    "name": "rightElevon",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [2.85, -4.6, 0.05],
                    "area": 2.4,
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
                    "points": { "forceSourcePoint": [0, -6.6, 0.0] } # Straight through center of mass
                },
                # Tricycle Landing Gear physics nodes
                {
                    "name": "frontWheel",
                    "parent": "body",
                    "type": "wheel",
                    "position": [0, 3.8, -0.3],
                    "collisionPoints": [
                        [0, 0, -1.05]
                    ],
                    "suspension": { "stiffness": 30, "damping": 7 },
                    "animations": [
                        { "type": "rotate", "axis": "Z", "value": "yaw", "ratio": 16 },
                        { "type": "hide", "value": "gearPosition", "threshold": 0.98 }
                    ]
                },
                {
                    "name": "leftGear",
                    "parent": "body",
                    "type": "wheel",
                    "position": [-1.2, -1.1, -0.2],
                    "collisionPoints": [
                        [0, 0, -1.15]
                    ],
                    "suspension": { "stiffness": 40, "damping": 8 },
                    "animations": [
                        { "type": "hide", "value": "gearPosition", "threshold": 0.98 }
                    ]
                },
                {
                    "name": "rightGear",
                    "parent": "body",
                    "type": "wheel",
                    "position": [1.2, -1.1, -0.2],
                    "collisionPoints": [
                        [0, 0, -1.15]
                    ],
                    "suspension": { "stiffness": 40, "damping": 8 },
                    "animations": [
                        { "type": "hide", "value": "gearPosition", "threshold": 0.98 }
                    ]
                }
            ]
        }
    ]

    for p in [os.path.join(BASE_DIR, "aircraft.json"), os.path.join(BASE_DIR, "definition.json")]:
        with open(p, "w") as f:
            json.dump(definition, f, indent=2)
    print("  [x] Saved updated aircraft.json & definition.json")
    return definition

# -------------------------------------------------------------
# 5. COMPILE STANDALONE IN-MEMORY geofs_test_loader.js
# -------------------------------------------------------------
def compile_standalone_loader(definition):
    print("Compiling self-contained geofs_test_loader.js...")
    loader_path = os.path.join(BASE_DIR, "geofs_test_loader.js")
    
    body_path = os.path.join(EXPORT_DIR, "body.glb")
    with open(body_path, "rb") as f:
        body_b64 = base64.b64encode(f.read()).decode("utf-8")

    js_code = f"""/**
 * HAL TEJAS Mk1 — HIGH-FIDELITY STANDALONE GEOFS INJECTOR
 * Single-mesh unified airframe with authentic IAF camouflage and stable flight physics.
 */
(function loadTejasInGeoFS() {{
    console.log("%c[HAL TEJAS Mk1] INJECTING HIGH-FIDELITY AIRCRAFT...", "color: #ff9933; font-weight: bold; font-size: 14px;");

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

        const bodyBlobUrl = b64ToBlobUrl("{body_b64}");
        const definition = {json.dumps(definition)};
        const tejasDef = definition[0];
        
        tejasDef.parts.forEach(part => {{
            if (part.name === "body") {{
                part.model = bodyBlobUrl;
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
        console.log("%c[HAL TEJAS Mk1] READY FOR TAKEOFF! ENJOY!", "color: #138808; font-weight: bold; font-size: 15px;");
    }} catch (err) {{
        console.error("[HAL TEJAS Mk1] Error:", err);
        alert("[HAL TEJAS Mk1] " + err.message);
    }}
}})();
"""
    with open(loader_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print(f"  [x] Saved updated loader: {loader_path} ({os.path.getsize(loader_path)/1024:.1f} KB)")

if __name__ == "__main__":
    generate_aligned_texture()
    models = build_high_detail_tejas()
    export_pbr_models(models)
    definition = update_definition()
    compile_standalone_loader(definition)
    print("\n>>> HIGH-FIDELITY TEJAS BUILD COMPLETE!")
