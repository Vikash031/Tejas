"""
Re-export Tejas Navy GLB with correct Indian Navy colour scheme.
Real INS Tejas Navy colour: dark blue-grey  ~#3B5068 / #304455
MTL Kd values are correct but too dark for Three.js rendering.
We multiply them up to correct perceptual navy blue-grey.
"""
import trimesh, numpy as np
from pathlib import Path
from PIL import Image

OBJ = Path("tejas_geofs/3dmodel/files/Tejas_Navy.obj")
MTL = Path("tejas_geofs/3dmodel/files/Tejas_Navy_fixed.mtl")
TEX = Path("tejas_geofs/3dmodel/files/Textures")
OUT = Path("tejas_geofs/export/tejas_navy_final.glb")

# ── Parse MTL ──────────────────────────────────────────────
mat_info = {}   # name -> {color, diffuse_tex}
current = None
with open(MTL, encoding='utf-8', errors='replace') as f:
    for line in f:
        line = line.strip()
        if line.startswith('newmtl '):
            current = line[7:].strip()
            mat_info[current] = {'color': [0.5,0.5,0.5,1.0], 'tex': None}
        elif current:
            if line.startswith('Kd '):
                p = line.split()
                if len(p) >= 4:
                    mat_info[current]['color'] = [float(p[1]), float(p[2]), float(p[3]), 1.0]
            elif line.startswith('map_Kd '):
                mat_info[current]['tex'] = line[7:].strip()

# ── Indian Navy colour corrections ─────────────────────────
# Real Tejas Navy: dark blue-grey #304455 ≈ (0.19, 0.27, 0.33)
# MTL has Kd ≈ 0.056, 0.102, 0.138 — correct hue, too dark.
# We multiply fuselage colours by ~3.4x to reach perceptual navy grey-blue.
NAVY_BOOST = {
    'Body_Fuselage':       [0.192, 0.267, 0.333, 1.0],   # #314455 naval blue-grey
    'Body_Fuselage_dark':  [0.157, 0.220, 0.278, 1.0],   # slightly darker panels
    'Body_Fuselage_light': [0.420, 0.430, 0.415, 1.0],   # lighter belly grey
    'Nose':                [0.200, 0.220, 0.240, 1.0],   # dark radar nose
    'Metalic_Grey':        [0.340, 0.348, 0.355, 1.0],   # polished metal grey
    'Steel_Pipe':          [0.55,  0.55,  0.55,  1.0],   # steel struts
    'Engine_plates':       [0.28,  0.28,  0.28,  1.0],   # engine housing
    'Missile_Red':         [0.70,  0.05,  0.03,  1.0],   # red missile tip
    'Missile_white':       [0.85,  0.85,  0.85,  1.0],   # white missile body
    'Tire':                [0.10,  0.10,  0.10,  1.0],   # black tyres
    'Cockpit_cabin':       [0.08,  0.08,  0.09,  1.0],   # dark cockpit interior
    'Seat_Hard_black':     [0.10,  0.10,  0.10,  1.0],   # ejection seat
    'Seat_Belt':           [0.05,  0.22,  0.06,  1.0],   # green harness
    'Cable':               [0.12,  0.12,  0.12,  1.0],   # dark cables
    'Mirror':              [0.85,  0.85,  0.90,  1.0],   # mirror sheen
    'Glass_2':             [0.30,  0.50,  0.65,  0.25],  # canopy glass
    'Windshield_glass':    [0.30,  0.50,  0.65,  0.25],  # windshield glass
    'Emisson_Red':         [1.0,   0.1,   0.05,  1.0],   # red nav light
    'Emisson_Yellow':      [1.0,   0.8,   0.0,   1.0],   # yellow light
    'Emisson_white':       [1.0,   1.0,   1.0,   1.0],   # white light
    'Tricolor':            [1.0,   1.0,   1.0,   1.0],   # tricolor decal (white base)
    'Navy_Emblem':         [1.0,   1.0,   1.0,   1.0],   # emblem (white base)
    'Tejas_written':       [1.0,   1.0,   1.0,   1.0],   # Tejas text (white)
    'None':                [0.192, 0.267, 0.333, 1.0],   # fallback = navy grey
}

for name, info in mat_info.items():
    if name in NAVY_BOOST:
        info['color'] = NAVY_BOOST[name]

print("Loading OBJ...")
scene = trimesh.load(str(OBJ), force='scene', process=False)
print(f"  {len(scene.geometry)} meshes")

print("\nApplying navy colours and textures...")
for geo_name, mesh in scene.geometry.items():
    info = mat_info.get(geo_name, {'color':[0.5,0.5,0.5,1.0],'tex':None})
    c    = info['color']
    tex  = info['tex']

    if tex:
        tex_path = Path(tex)
        if tex_path.exists():
            try:
                img = Image.open(tex_path).convert('RGBA')
                mat = trimesh.visual.material.SimpleMaterial(image=img, diffuse=[255,255,255,255])
                uv  = mesh.visual.uv if hasattr(mesh.visual,'uv') and mesh.visual.uv is not None else np.zeros((len(mesh.vertices),2))
                mesh.visual = trimesh.visual.TextureVisuals(uv=uv, material=mat)
                print(f"  + tex  {geo_name} -> {tex_path.name}")
                continue
            except Exception as e:
                print(f"  ! tex err {geo_name}: {e}")

    # Apply colour (convert linear to uint8)
    r,g,b,a = [min(255, int(v*255)) for v in c]
    vc = np.tile([r,g,b,a], (len(mesh.vertices),1)).astype(np.uint8)
    mesh.visual = trimesh.visual.ColorVisuals(vertex_colors=vc)
    if c != [0.5,0.5,0.5,1.0]:
        print(f"  + col  {geo_name} -> #{r:02x}{g:02x}{b:02x}")

print("\nExporting GLB...")
OUT.parent.mkdir(exist_ok=True)
glb = scene.export(file_type='glb')
with open(OUT,'wb') as f: f.write(glb)
print(f"  Saved {len(glb)/1024/1024:.1f} MB -> {OUT}")
print("Done!")
