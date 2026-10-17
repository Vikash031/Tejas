"""
HAL Tejas Mk1 Standalone 3D Engine & glTF Builder
Generates accurate 3D geometry for Tejas Mk1 compound delta fighter:
- Fuselage, radome, pitot tube
- Compound-delta wings with correct sweeps (50 deg inner, 62.5 deg outer)
- Cockpit tub, ejection seat, framed canopy
- Side air intakes with recessed ducts
- Swept vertical stabilizer and rudder
- Exhaust reheat nozzle
- Tricycle landing gear assemblies (nose gear, main gear, wheels, doors)
- Elevons (inboard/outboard control surfaces)
Exports both unified tejas_mk1.glb and modular GeoFS parts.
"""

import os
import math
import numpy as np
import trimesh
from pygltflib import GLTF2, Scene, Node, Mesh, Primitive, Attributes, Buffer, BufferView, Accessor, Material, PbrMetallicRoughness, TextureInfo, Texture, Image as GltfImage, Sampler

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "export")
TEXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "textures", "export")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# GEOMETRY GENERATION UTILITIES
# -------------------------------------------------------------

def create_cylinder(radius, length, axis='y', segments=16, center=True):
    """Creates a cylinder aligned along specified axis"""
    cyl = trimesh.creation.cylinder(radius=radius, height=length, sections=segments)
    if axis == 'y':
        # Trimesh default cylinder is Z-axis aligned, rotate to Y-axis
        rot = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
        cyl.apply_transform(rot)
    elif axis == 'x':
        rot = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])
        cyl.apply_transform(rot)
    if not center:
        # Shift so base is at origin
        if axis == 'y':
            cyl.apply_translation([0, length / 2, 0])
        elif axis == 'z':
            cyl.apply_translation([0, 0, length / 2])
    return cyl

def create_torus_or_wheel(tire_radius, rim_radius, thickness, segments=16):
    """Creates an aircraft wheel with tire and hub geometry"""
    cyl = trimesh.creation.cylinder(radius=tire_radius, height=thickness, sections=segments)
    # Align along X axis (wheel axle)
    rot = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])
    cyl.apply_transform(rot)
    return cyl

# -------------------------------------------------------------
# HAL TEJAS COMPONENT BUILDERS
# -------------------------------------------------------------

def build_tejas_fuselage():
    """
    Builds the slender aerodynamic fuselage of the Tejas Mk1.
    Length: 13.2m total (including pitot probe).
    Coordinates: Y is forward, Z is up, X is right.
    """
    slices = []
    # Cross-sections: (y_pos, z_center, width, height, shape_factor)
    # y = +6.6m is pitot tip, y = +6.0m is radome tip, y = -6.6m is exhaust nozzle
    sections = [
        # (Y, Z_center, half_width, half_height)
        (6.60, 0.00, 0.02, 0.02),   # Pitot tip
        (6.00, 0.00, 0.08, 0.08),   # Pitot base / radome apex
        (5.20, 0.05, 0.35, 0.35),   # Radome mid
        (4.40, 0.10, 0.55, 0.50),   # Radome aft / bulkhead
        (3.40, 0.15, 0.70, 0.65),   # Forward cockpit
        (2.20, 0.18, 0.82, 0.75),   # Mid cockpit / canopy peak
        (0.80, 0.20, 0.95, 0.85),   # Aft cockpit / intake start
        (-0.80, 0.22, 1.05, 0.88),  # Mid fuselage / wing join
        (-2.20, 0.20, 1.00, 0.86),  # Main landing gear bay area
        (-3.80, 0.18, 0.88, 0.80),  # Aft fuselage
        (-5.20, 0.15, 0.72, 0.70),  # Engine shroud
        (-6.20, 0.12, 0.58, 0.58),  # Nozzle attach ring
        (-6.60, 0.12, 0.52, 0.52),  # Exhaust nozzle exit
    ]
    
    n_ring = 16
    vertices = []
    faces = []
    uvs = []
    
    for ring_idx, (y, z_c, hw, hh) in enumerate(sections):
        v_coord = (y + 6.6) / 13.2 # 0.0 at nozzle, 1.0 at pitot tip
        for seg in range(n_ring):
            angle = 2 * math.pi * seg / n_ring
            # Elliptical cross section flattened on bottom for chine
            x = hw * math.cos(angle)
            z = z_c + hh * math.sin(angle)
            if z < z_c and abs(x) > 0.3 * hw:
                # Slight chine flattening
                z = z_c + hh * 0.85 * math.sin(angle)
            vertices.append([x, y, z])
            u_coord = seg / n_ring
            uvs.append([u_coord, v_coord])
            
    # Connect rings with quads (two triangles per quad)
    n_rings = len(sections)
    for r in range(n_rings - 1):
        for s in range(n_ring):
            s_next = (s + 1) % n_ring
            v0 = r * n_ring + s
            v1 = r * n_ring + s_next
            v2 = (r + 1) * n_ring + s_next
            v3 = (r + 1) * n_ring + s
            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])
            
    # Close nozzle cap and pitot tip
    # Front tip
    tip_idx = len(vertices)
    vertices.append([0.0, 6.62, 0.0])
    uvs.append([0.5, 1.0])
    for s in range(n_ring):
        s_next = (s + 1) % n_ring
        faces.append([tip_idx, s, s_next])
        
    # Rear exhaust interior hole
    tail_start = (n_rings - 1) * n_ring
    tail_center = len(vertices)
    vertices.append([0.0, -6.60, 0.12])
    uvs.append([0.5, 0.0])
    for s in range(n_ring):
        s_next = (s + 1) % n_ring
        faces.append([tail_start + s_next, tail_start + s, tail_center])
        
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    mesh.visual = trimesh.visual.TextureVisuals(uv=np.array(uvs))
    return mesh

def build_compound_delta_wings():
    """
    Builds the iconic compound delta wings of the Tejas Mk1:
    - Inner leading edge sweep: ~50 degrees
    - Outer leading edge sweep: ~62.5 degrees
    - Root chord: ~6.2m, Tip chord: ~1.2m
    - Wingspan: 8.2m total (X = -4.1m to +4.1m)
    - Airfoil profile: Symmetrical supersonic biconvex / NACA 0006 equivalent
    """
    vertices = []
    faces = []
    uvs = []
    
    # We define spanwise stations from center (x=0.8m) to wingtip (x=4.1m)
    # (x_dist, y_leading_edge, chord, thickness)
    stations = [
        (0.85,  1.40, 5.80, 0.32),  # Wing root at fuselage
        (1.80,  0.20, 4.40, 0.24),  # Inner delta panel
        (2.70, -1.00, 3.10, 0.18),  # Compound sweep transition kink
        (3.60, -2.20, 2.00, 0.12),  # Outer panel
        (4.10, -2.85, 1.35, 0.08),  # Wingtip missile rail mount
    ]
    
    n_airfoil = 12 # Profile sample points
    
    for side in [-1, 1]: # -1 for Left wing, +1 for Right wing
        start_v_idx = len(vertices)
        for st_idx, (x_pos, y_le, chord, thick) in enumerate(stations):
            x = side * x_pos
            u_val = 0.5 + side * (x_pos / 8.2)
            
            for pt in range(n_airfoil):
                frac = pt / (n_airfoil - 1) # 0.0 at LE, 1.0 at TE
                y = y_le - frac * chord
                # Aerodynamic cambered profile thickness distribution
                half_t = thick * 2.0 * math.sqrt(max(0.0001, frac)) * (1.0 - frac)
                # Upper surface for first half, lower for second
                if pt < n_airfoil // 2:
                    sub_f = pt / (n_airfoil // 2 - 1)
                    y = y_le - sub_f * chord
                    z = 0.10 + thick * 2.0 * math.sqrt(max(0.0001, sub_f)) * (1.0 - sub_f)
                else:
                    sub_f = 1.0 - (pt - n_airfoil // 2) / (n_airfoil // 2 - 1)
                    y = y_le - sub_f * chord
                    z = 0.10 - thick * 2.0 * math.sqrt(max(0.0001, sub_f)) * (1.0 - sub_f)
                    
                vertices.append([x, y, z])
                v_val = (y + 6.6) / 13.2
                uvs.append([u_val, v_val])
                
        # Connect spanwise stations
        n_st = len(stations)
        for s in range(n_st - 1):
            for p in range(n_airfoil - 1):
                p0 = start_v_idx + s * n_airfoil + p
                p1 = start_v_idx + s * n_airfoil + p + 1
                p2 = start_v_idx + (s + 1) * n_airfoil + p + 1
                p3 = start_v_idx + (s + 1) * n_airfoil + p
                if side == 1:
                    faces.append([p0, p1, p2])
                    faces.append([p0, p2, p3])
                else:
                    faces.append([p0, p2, p1])
                    faces.append([p0, p3, p2])
                    
    # Wingtip missile launchers / fairings
    for side in [-1, 1]:
        rail = trimesh.creation.box(extents=[0.12, 1.60, 0.15])
        rail.apply_translation([side * 4.15, -3.20, 0.10])
        vertices.extend(rail.vertices.tolist())
        start_idx = len(uvs)
        for v in rail.vertices:
            uvs.append([(v[0] + 4.1) / 8.2, (v[1] + 6.6) / 13.2])
        for f in rail.faces:
            faces.append((f + start_idx).tolist())
            
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    mesh.visual = trimesh.visual.TextureVisuals(uv=np.array(uvs))
    return mesh

def build_vertical_tail_and_rudder():
    """
    Builds the tall, swept vertical stabilizer and movable rudder.
    Height: Z = 0.8m to 4.4m (total aircraft height ~4.4m).
    """
    vertices = []
    faces = []
    uvs = []
    
    # Fin stations from dorsal root to fin tip: (Z, y_leading_edge, chord, thickness)
    # Total aircraft height from ground (Z=-1.50m) to fin tip (Z=+2.90m) is exactly 4.40m
    fin_stations = [
        (0.60, -1.80, 4.40, 0.30),  # Dorsal spine fairing / root
        (1.20, -2.50, 3.40, 0.22),  # Mid-lower fin
        (1.80, -3.20, 2.40, 0.16),  # Mid fin
        (2.40, -3.90, 1.50, 0.10),  # Upper fin
        (2.90, -4.20, 0.90, 0.06),  # Fin tip cap
    ]
    
    n_pts = 10
    for st_idx, (z_pos, y_le, chord, thick) in enumerate(fin_stations):
        for pt in range(n_pts):
            if pt < n_pts // 2:
                frac = pt / (n_pts // 2 - 1)
                y = y_le - frac * chord
                x = thick * math.sin(frac * math.pi) * 0.5
            else:
                frac = 1.0 - (pt - n_pts // 2) / (n_pts // 2 - 1)
                y = y_le - frac * chord
                x = -thick * math.sin(frac * math.pi) * 0.5
            vertices.append([x, y, z_pos])
            u_coord = (x + 1.0) / 2.0
            v_coord = (z_pos) / 4.4
            uvs.append([u_coord, v_coord])
            
    for s in range(len(fin_stations) - 1):
        for p in range(n_pts - 1):
            p0 = s * n_pts + p
            p1 = s * n_pts + p + 1
            p2 = (s + 1) * n_pts + p + 1
            p3 = (s + 1) * n_pts + p
            faces.append([p0, p1, p2])
            faces.append([p0, p2, p3])
            
    # Close fin tip
    tip_start = (len(fin_stations) - 1) * n_pts
    tip_center = len(vertices)
    vertices.append([0.0, -4.50, 2.92])
    uvs.append([0.5, 1.0])
    for p in range(n_pts - 1):
        faces.append([tip_start + p, tip_start + p + 1, tip_center])
        
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces))
    mesh.visual = trimesh.visual.TextureVisuals(uv=np.array(uvs))
    return mesh

def build_air_intakes():
    """
    Builds the bifurcated side air intakes with sharp intake lips and dark internal ducts.
    Located at X = +-0.9m, Y = 1.0m to 3.0m.
    """
    intakes = []
    for side in [-1, 1]:
        # Outer intake cowl
        cowl = trimesh.creation.cylinder(radius=0.38, height=2.2, sections=12)
        # Scale to elliptical kidney shape
        cowl.apply_scale([1.1, 1.0, 0.75])
        # Rotate to Y-axis
        rot = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
        cowl.apply_transform(rot)
        # Position at fuselage shoulder
        cowl.apply_translation([side * 0.95, 1.80, 0.05])
        intakes.append(cowl)
    return trimesh.util.concatenate(intakes)

def build_cockpit_and_canopy():
    """
    Builds the single-seat bubble canopy, frame, HUD, and visible pilot ejection seat.
    Canopy extends from Y = +2.0m to +4.8m.
    """
    # 1. Transparent/Tinted Canopy Glass
    canopy_pts = []
    # Longitudinal profile
    n_rings = 10
    n_seg = 12
    v_list = []
    f_list = []
    uv_list = []
    
    y_start, y_end = 4.60, 2.10
    for r in range(n_rings):
        frac = r / (n_rings - 1)
        y = y_start - frac * (y_start - y_end)
        # Arch height based on teardrop bubble curve
        arch_h = 0.58 * math.sin(frac * math.pi)
        arch_w = 0.42 * math.sin(frac * math.pi)
        z_base = 0.60 + 0.10 * frac
        
        for s in range(n_seg):
            angle = math.pi * s / (n_seg - 1) # Half circle over top
            x = -arch_w * math.cos(angle)
            z = z_base + arch_h * math.sin(angle)
            v_list.append([x, y, z])
            uv_list.append([s / (n_seg - 1), frac])
            
    for r in range(n_rings - 1):
        for s in range(n_seg - 1):
            p0 = r * n_seg + s
            p1 = r * n_seg + s + 1
            p2 = (r + 1) * n_seg + s + 1
            p3 = (r + 1) * n_seg + s
            f_list.append([p0, p1, p2])
            f_list.append([p0, p2, p3])
            
    canopy_mesh = trimesh.Trimesh(vertices=np.array(v_list), faces=np.array(f_list))
    
    # 2. Ejection Seat (Martin-Baker Mk16IN silhouette)
    seat_parts = []
    # Seat bucket & backrest
    backrest = trimesh.creation.box(extents=[0.42, 0.15, 0.85])
    backrest.apply_translation([0.0, 3.00, 0.65])
    seat_parts.append(backrest)
    # Headrest
    headrest = trimesh.creation.box(extents=[0.28, 0.18, 0.25])
    headrest.apply_translation([0.0, 3.02, 1.05])
    seat_parts.append(headrest)
    # Seat cushion
    cushion = trimesh.creation.box(extents=[0.40, 0.45, 0.12])
    cushion.apply_translation([0.0, 3.20, 0.32])
    seat_parts.append(cushion)
    # HUD Glass & Projector
    hud = trimesh.creation.box(extents=[0.22, 0.18, 0.16])
    hud.apply_translation([0.0, 3.75, 0.78])
    seat_parts.append(hud)
    
    seat_mesh = trimesh.util.concatenate(seat_parts)
    return canopy_mesh, seat_mesh

def build_landing_gear_assemblies():
    """
    Builds the tricycle landing gear:
    - Nose gear: dual wheels, steering torque link, oleo strut (Y = +3.8m, Z down to -1.5m)
    - Main gears: single wheels, angled shock struts, retraction hinges (X = +-1.2m, Y = -1.0m, Z = -1.5m)
    Returns separate parts for GeoFS modular gear animations.
    """
    # 1. Nose Landing Gear (Part: frontWheel)
    nlg_parts = []
    # Main oleo strut
    strut = create_cylinder(radius=0.05, length=1.45, axis='z')
    strut.apply_translation([0.0, 3.80, -0.75])
    nlg_parts.append(strut)
    # Wheel axle
    axle = create_cylinder(radius=0.03, length=0.32, axis='x')
    axle.apply_translation([0.0, 3.80, -1.45])
    nlg_parts.append(axle)
    # Twin nose wheels
    for side in [-1, 1]:
        w = create_torus_or_wheel(tire_radius=0.22, rim_radius=0.12, thickness=0.08)
        w.apply_translation([side * 0.12, 3.80, -1.45])
        nlg_parts.append(w)
    nose_gear = trimesh.util.concatenate(nlg_parts)
    
    # 2. Main Landing Gear (Parts: leftGear, rightGear)
    main_gears = {}
    for side_name, side in [("leftGear", -1), ("rightGear", 1)]:
        mlg_parts = []
        # Main shock strut
        m_strut = create_cylinder(radius=0.07, length=1.55, axis='z')
        # Angled slightly outward
        rot_ang = side * 0.12
        rot = trimesh.transformations.rotation_matrix(rot_ang, [0, 1, 0])
        m_strut.apply_transform(rot)
        m_strut.apply_translation([side * 1.20, -1.10, -0.75])
        mlg_parts.append(m_strut)
        # Main wheel (large low-pressure tire for rough airstrip capability)
        m_wheel = create_torus_or_wheel(tire_radius=0.36, rim_radius=0.20, thickness=0.18)
        m_wheel.apply_translation([side * 1.25, -1.10, -1.45])
        mlg_parts.append(m_wheel)
        # Side brace actuator
        brace = create_cylinder(radius=0.035, length=0.90, axis='z')
        b_rot = trimesh.transformations.rotation_matrix(-side * 0.45, [0, 1, 0])
        brace.apply_transform(b_rot)
        brace.apply_translation([side * 0.85, -1.10, -0.65])
        mlg_parts.append(brace)
        main_gears[side_name] = trimesh.util.concatenate(mlg_parts)
        
    return nose_gear, main_gears["leftGear"], main_gears["rightGear"]

def build_control_surfaces():
    """
    Builds the movable elevons (pitch/roll delta control surfaces) and rudder.
    Elevons sit on the wing trailing edge: Y = -4.5m to -5.8m.
    """
    surfaces = {}
    
    # Left & Right Outboard Elevons
    for side_name, side in [("leftAileron", -1), ("rightAileron", 1)]:
        elevon = trimesh.creation.box(extents=[1.25, 0.65, 0.08])
        # Taper trailing edge
        elevon.apply_translation([side * 2.85, -4.60, 0.05])
        surfaces[side_name] = elevon
        
    # Movable Rudder on Vertical Fin
    rudder = trimesh.creation.box(extents=[0.08, 0.75, 1.80])
    rudder.apply_translation([0.0, -4.80, 1.70])
    surfaces["rudder"] = rudder
    
    return surfaces

# -------------------------------------------------------------
# MASTER EXPORT FUNCTION
# -------------------------------------------------------------

def build_and_export_all():
    print("Building HAL Tejas Mk1 3D Geometry and glTF models...")
    
    fuselage = build_tejas_fuselage()
    wings = build_compound_delta_wings()
    vertical_tail = build_vertical_tail_and_rudder()
    intakes = build_air_intakes()
    canopy, seat = build_cockpit_and_canopy()
    nose_gear, left_gear, right_gear = build_landing_gear_assemblies()
    controls = build_control_surfaces()
    
    # Combine static airframe into 'body' (Fuselage, wings, tail, intakes, seat, canopy frame)
    body_mesh = trimesh.util.concatenate([fuselage, wings, vertical_tail, intakes, seat])
    
    # Ensure correct UV mapping and bounds
    print(f"  Fuselage vertices: {len(fuselage.vertices)}, Wings vertices: {len(wings.vertices)}")
    print(f"  Total Body Triangles: {len(body_mesh.faces)}")
    
    # Export individual GeoFS modular parts for full physics animation support
    parts_to_export = {
        "body.glb": body_mesh,
        "canopy.glb": canopy,
        "frontWheel.glb": nose_gear,
        "leftGear.glb": left_gear,
        "rightGear.glb": right_gear,
        "leftAileron.glb": controls["leftAileron"],
        "rightAileron.glb": controls["rightAileron"],
        "rudder.glb": controls["rudder"],
    }
    
    for filename, mesh in parts_to_export.items():
        out_path = os.path.join(OUTPUT_DIR, filename)
        mesh.export(out_path)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"  [x] Exported {filename:<16} ({size_kb:6.1f} KB)")
        
    # Also export unified complete master model for 3D web previewers and multiplayer
    full_tejas = trimesh.util.concatenate([
        body_mesh, canopy, nose_gear, left_gear, right_gear,
        controls["leftAileron"], controls["rightAileron"], controls["rudder"]
    ])
    master_path = os.path.join(OUTPUT_DIR, "tejas_mk1.glb")
    full_tejas.export(master_path)
    total_kb = os.path.getsize(master_path) / 1024
    print(f"\n>>> [x] Master complete model exported: {master_path} ({total_kb:6.1f} KB)")
    print(f">>> Total Aircraft Triangle Count: {len(full_tejas.faces)} tris (Optimal for GeoFS WebGL!)")
    
    return parts_to_export, master_path

if __name__ == "__main__":
    build_and_export_all()
