"""
Multi-Angle 3D Preview Renderer for HAL Tejas Mk1
Renders 8 inspection angles:
1. Direct Front (Nose, Radome, Pitot, Intakes)
2. Direct Rear (Exhaust Nozzle, Vertical Fin, Wing Trailing Edge)
3. Direct Top (Compound Delta Planform, Camouflage, National Roundels)
4. Direct Side (Aerodynamic Silhouette, Cockpit Bubble, Fin)
5. Front Three-Quarter (Signature Perspective View)
6. Rear Three-Quarter (Delta Wing & Dorsal Spine)
7. Cockpit Close-up (Canopy, Ejection Seat, HUD, Console)
8. Landing Gear Close-up (Tricycle Struts, Wheels, Bays)
Saves images to tejas_geofs/screenshots/
"""

import os
import math
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "export", "tejas_mk1.glb")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def render_all_previews():
    print("Loading 3D model for multi-angle preview rendering...")
    scene = trimesh.load(MODEL_PATH)
    
    # Extract all triangles and vertices across scene geometries
    all_verts = []
    all_faces = []
    offset = 0
    
    geoms = scene.geometry.values() if hasattr(scene, 'geometry') else [scene]
    for g in geoms:
        if hasattr(g, 'vertices') and hasattr(g, 'faces'):
            all_verts.append(g.vertices)
            all_faces.append(g.faces + offset)
            offset += len(g.vertices)
            
    vertices = np.vstack(all_verts)
    faces = np.vstack(all_faces)
    
    # Aircraft coordinate system: X is right, Y is forward, Z is up
    # In Matplotlib 3D: X is right, Y is depth (forward), Z is up
    triangles = vertices[faces]
    
    # 8 Required Camera Views: (elev, azim, title, filename, zoom_center, zoom_radius)
    views = [
        # Front view: looking directly at nose
        (4, 90, "HAL Tejas Mk1 - Direct Front View", "01_direct_front.png", [0, 0, 0], 7.5),
        # Rear view: looking directly at exhaust
        (4, -90, "HAL Tejas Mk1 - Direct Rear View", "02_direct_rear.png", [0, 0, 0], 7.5),
        # Top view: directly overhead looking down
        (89, 90, "HAL Tejas Mk1 - Direct Top Planform", "03_direct_top.png", [0, 0, 0], 7.5),
        # Side view: looking at side profile
        (0, 0, "HAL Tejas Mk1 - Direct Side Profile", "04_direct_side.png", [0, 0, 0], 7.5),
        # Front three-quarter: signature perspective view
        (18, 55, "HAL Tejas Mk1 - Front Three-Quarter View", "05_front_three_quarter.png", [0, 0, 0], 7.8),
        # Rear three-quarter: delta trailing edge & fin
        (18, -125, "HAL Tejas Mk1 - Rear Three-Quarter View", "06_rear_three_quarter.png", [0, 0, 0], 7.8),
        # Cockpit close-up
        (22, 65, "HAL Tejas Mk1 - Cockpit Detail", "07_cockpit_closeup.png", [0, 3.0, 0.6], 2.4),
        # Landing gear close-up
        (-5, 60, "HAL Tejas Mk1 - Landing Gear Detail", "08_landing_gear_closeup.png", [0, 1.2, -1.0], 2.8),
    ]
    
    print(f"Rendering {len(views)} preview images ({len(faces)} triangles)...")
    
    # Palette colors
    c_camo = (0.55, 0.60, 0.65, 0.95)
    c_edge = (0.35, 0.38, 0.42, 0.25)
    
    for idx, (elev, azim, title, filename, center, radius) in enumerate(views):
        fig = plt.figure(figsize=(10, 7), dpi=120)
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('#1a1e24') # Premium dark hangar background
        fig.patch.set_facecolor('#14171c')
        
        # Build 3D mesh collection
        # Subsample faces slightly for rapid crisp rendering if large
        mesh_col = Poly3DCollection(
            triangles,
            facecolors=c_camo,
            edgecolors=c_edge,
            linewidths=0.3,
            shade=True
        )
        ax.add_collection3d(mesh_col)
        
        # Set camera bounds
        cx, cy, cz = center
        r = radius
        ax.set_xlim([cx - r, cx + r])
        ax.set_ylim([cy - r, cy + r])
        ax.set_zlim([cz - r, cz + r])
        
        # Camera angle
        ax.view_init(elev=elev, azim=azim)
        
        # Turn off grid/axis box for a sleek clean render
        ax.set_axis_off()
        
        # Title and specs overlay
        plt.title(title, color='#e0e6ed', fontsize=14, fontweight='bold', pad=12)
        fig.text(0.5, 0.04, "HAL TEJAS Mk1 - GEOFS AIRCRAFT SPECIFICATION | INDIAN AIR FORCE",
                 ha='center', color='#8892a0', fontsize=9, fontfamily='monospace')
        
        out_file = os.path.join(SCREENSHOTS_DIR, filename)
        plt.tight_layout()
        plt.savefig(out_file, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        plt.close(fig)
        print(f"  [{idx+1}/8] Rendered: {filename}")
        
    print("\n>>> All 8 preview renders generated successfully in tejas_geofs/screenshots/!")

if __name__ == "__main__":
    render_all_previews()
