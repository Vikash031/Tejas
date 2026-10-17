"""
Procedural Texture Generator for HAL Tejas Mk1 (GeoFS)
Generates high-fidelity IAF Air Superiority Grey camouflage,
national roundels, fin flashes, warning stencils, and cockpit panels.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "textures", "export")
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIDTH, HEIGHT = 2048, 2048

def create_tejas_textures():
    print("Generating HAL Tejas Mk1 texture atlas (2048x2048)...")
    
    # 1. Base Diffuse Map
    base_img = Image.new("RGBA", (WIDTH, HEIGHT), (145, 155, 165, 255))
    draw = ImageDraw.Draw(base_img)
    
    # Generate subtle Perlin-like noise / camouflage cloud pattern
    np.random.seed(42)
    noise_grid = np.random.normal(0, 15, (HEIGHT // 4, WIDTH // 4))
    noise_img = Image.fromarray(np.uint8(np.clip(noise_grid + 128, 0, 255)), mode='L')
    noise_img = noise_img.resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC)
    
    # Camouflage shapes (IAF Two-Tone Grey: Light Grey #96a2ad, Darker Blue-Grey #66727d)
    camo_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    camo_draw = ImageDraw.Draw(camo_overlay)
    
    # Draw curved camouflage patches across the fuselage and wing areas
    camo_color = (102, 114, 125, 240)
    # Wing camo patches
    camo_draw.polygon([(100, 300), (350, 250), (450, 600), (200, 750), (80, 500)], fill=camo_color)
    camo_draw.polygon([(700, 350), (950, 300), (1050, 700), (850, 850), (650, 600)], fill=camo_color)
    camo_draw.polygon([(1150, 250), (1450, 220), (1500, 550), (1300, 700), (1100, 450)], fill=camo_color)
    camo_draw.polygon([(1600, 400), (1950, 350), (1980, 800), (1750, 900), (1550, 650)], fill=camo_color)
    # Fuselage spine camo
    camo_draw.polygon([(850, 1100), (1200, 1050), (1250, 1600), (800, 1650)], fill=camo_color)
    
    # Soften camouflage edges
    camo_overlay = camo_overlay.filter(ImageFilter.GaussianBlur(radius=8))
    base_img.alpha_composite(camo_overlay)
    
    # 2. Add Panel Lines & Structural Details (Dark subtle seams)
    panel_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(panel_overlay)
    panel_color = (60, 65, 70, 120)
    
    # Wing panel lines (horizontal & diagonal chord lines)
    for y in range(200, 950, 60):
        p_draw.line([(50, y), (980, y)], fill=panel_color, width=2)
        p_draw.line([(1060, y), (1990, y)], fill=panel_color, width=2)
    for x in range(150, 950, 100):
        p_draw.line([(x, 150), (x + 40, 950)], fill=panel_color, width=1)
        p_draw.line([(2048 - x, 150), (2048 - x - 40, 950)], fill=panel_color, width=1)
        
    # Fuselage frame lines
    for y in range(1000, 2000, 80):
        p_draw.line([(600, y), (1450, y)], fill=panel_color, width=2)
    p_draw.line([(1024, 980), (1024, 2020)], fill=(45, 50, 55, 180), width=3) # Dorsal centerline
    
    # Radome section (fuselage nose region) - Dark radar-absorbent dielectric grey
    p_draw.rectangle([(880, 1850), (1168, 2040)], fill=(55, 58, 62, 255))
    p_draw.line([(880, 1850), (1168, 1850)], fill=(30, 32, 35, 255), width=4) # Radome separation ring
    
    # Anti-glare matte black panel in front of windshield
    p_draw.polygon([(940, 1600), (1108, 1600), (1080, 1820), (968, 1820)], fill=(35, 38, 40, 245))
    
    # Exhaust reheat nozzle metallic ceramic bands
    p_draw.rectangle([(860, 980), (1188, 1080)], fill=(70, 65, 60, 255))
    for x in range(860, 1188, 12):
        p_draw.line([(x, 980), (x, 1080)], fill=(40, 38, 35, 200), width=2) # Exhaust petals
        
    base_img.alpha_composite(panel_overlay)
    
    # 3. IAF National Markings (Authentic Roundels & Fin Flash)
    def draw_iaf_roundel(img, cx, cy, radius):
        """Draws concentric Saffron, White, Green roundel with Navy Blue Ashoka chakra dot"""
        r_draw = ImageDraw.Draw(img)
        # Saffron outer ring
        r_draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 153, 51, 255))
        # White middle ring
        w_rad = int(radius * 0.66)
        r_draw.ellipse([cx - w_rad, cy - w_rad, cx + w_rad, cy + w_rad], fill=(255, 255, 255, 255))
        # Green inner circle
        g_rad = int(radius * 0.33)
        r_draw.ellipse([cx - g_rad, cy - g_rad, cx + g_rad, cy + g_rad], fill=(19, 136, 8, 255))
        # Center Navy Blue dot
        c_rad = max(2, int(radius * 0.08))
        r_draw.ellipse([cx - c_rad, cy - c_rad, cx + c_rad, cy + c_rad], fill=(0, 0, 128, 255))

    def draw_fin_flash(img, x, y, w, h):
        """Draws Indian national fin flash (Saffron, White, Green vertical bands)"""
        f_draw = ImageDraw.Draw(img)
        band_w = w // 3
        # Left: Saffron (Forward facing)
        f_draw.rectangle([x, y, x + band_w, y + h], fill=(255, 153, 51, 255))
        # Middle: White
        f_draw.rectangle([x + band_w, y, x + 2 * band_w, y + h], fill=(255, 255, 255, 255))
        # Right: Green
        f_draw.rectangle([x + 2 * band_w, y, x + w, y + h], fill=(19, 136, 8, 255))
        # Border
        f_draw.rectangle([x, y, x + w, y + h], outline=(40, 45, 50, 180), width=1)

    # Place wing roundels (Left Upper Wing & Right Lower Wing as per IAF standard)
    draw_iaf_roundel(base_img, 450, 550, radius=90)
    draw_iaf_roundel(base_img, 1598, 550, radius=90)
    
    # Place fuselage roundels (Port and Starboard forward fuselage)
    draw_iaf_roundel(base_img, 720, 1500, radius=55)
    draw_iaf_roundel(base_img, 1328, 1500, radius=55)
    
    # Place vertical fin flashes (Port & Starboard)
    draw_fin_flash(base_img, 320, 1200, 90, 60)
    draw_fin_flash(base_img, 1638, 1200, 90, 60)
    
    # 4. Stencils, Serials & Warning Labels
    lbl_draw = ImageDraw.Draw(base_img)
    
    # Ejection Seat Warning Triangles (Red inverted triangle with DANGER)
    def draw_ejection_warning(img, x, y, size):
        e_draw = ImageDraw.Draw(img)
        pts = [(x, y), (x + size, y), (x + size // 2, y + int(size * 0.866))]
        e_draw.polygon(pts, fill=(220, 30, 30, 255), outline=(255, 255, 255, 255))
        
    draw_ejection_warning(base_img, 770, 1630, 32)
    draw_ejection_warning(base_img, 1246, 1630, 32)
    
    # Air Intake Warning Triangles (Red chevrons near intake lips)
    draw_ejection_warning(base_img, 680, 1380, 26)
    draw_ejection_warning(base_img, 1342, 1380, 26)
    
    # Aircraft Serial Numbers & Squadrons: "LA-5001" (No. 45 Sqn "Flying Daggers")
    # Draw high-contrast clean stencil lettering using simple vector strokes
    def draw_stencil_text(img, text, x, y, color=(35, 40, 45, 240)):
        # Default PIL bitmap font works reliably everywhere without external ttf dependencies
        t_draw = ImageDraw.Draw(img)
        t_draw.text((x, y), text, fill=color)

    # Serial on tail base & nose gear door
    draw_stencil_text(base_img, "LA-5001", 335, 1270)
    draw_stencil_text(base_img, "LA-5001", 1653, 1270)
    draw_stencil_text(base_img, "TEJAS Mk1", 975, 1520)
    draw_stencil_text(base_img, "INDIAN AIR FORCE", 940, 1540)
    draw_stencil_text(base_img, "NO STEP", 410, 660, color=(180, 40, 40, 200))
    draw_stencil_text(base_img, "NO STEP", 1560, 660, color=(180, 40, 40, 200))
    
    # 5. Cockpit Instrument Texture Region (Lower left quadrant: 0-512, 1536-2048)
    cockpit_box = (50, 1600, 500, 2000)
    lbl_draw.rectangle(cockpit_box, fill=(25, 28, 32, 255)) # Dark matte cockpit panel
    # 3 Multi-Function Displays (MFDs) - Tejas glass cockpit layout
    # Center MFD (Nav / Tactical)
    lbl_draw.rectangle([(220, 1720), (330, 1830)], fill=(10, 35, 20, 255), outline=(0, 200, 100, 255), width=2)
    # Left MFD (PFD - Primary Flight Display)
    lbl_draw.rectangle([(80, 1720), (190, 1830)], fill=(15, 25, 45, 255), outline=(0, 180, 255, 255), width=2)
    # Right MFD (Engine / Systems)
    lbl_draw.rectangle([(360, 1720), (470, 1830)], fill=(30, 25, 15, 255), outline=(255, 180, 0, 255), width=2)
    # Standby instruments and switches
    lbl_draw.ellipse([(245, 1860), (305, 1920)], fill=(20, 20, 20, 255), outline=(200, 200, 200, 255), width=2)
    lbl_draw.text((255, 1880), "ATT", fill=(255, 255, 255, 255))
    lbl_draw.text((230, 1680), "HUD / UFC", fill=(180, 180, 180, 255))
    
    # Save diffuse texture
    diffuse_path = os.path.join(OUTPUT_DIR, "tejas_diffuse.png")
    base_img.save(diffuse_path, "PNG", optimize=True)
    print(f"  [x] Saved diffuse texture: {diffuse_path}")
    
    # 6. Metallic-Roughness Map (glTF PBR: Blue = Metallic, Green = Roughness)
    # Non-metallic paint: Low metallic (B~10), Medium-high roughness (G~160-190 for matte camo)
    # Metal exhaust & pitot: High metallic (B~220), Low roughness (G~60)
    # Glass canopy: Zero metallic (B=0), Very smooth (G~20)
    pbr_data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    pbr_data[:, :, 0] = 0        # Red channel: Unused in standard glTF (or AO)
    pbr_data[:, :, 1] = 175      # Green channel: Roughness (175 = matte military paint)
    pbr_data[:, :, 2] = 20       # Blue channel: Metallic (20 = dielectric composite/paint)
    
    # Radome: non-metallic dielectric, medium roughness
    pbr_data[1850:2040, 880:1168, 1] = 160
    pbr_data[1850:2040, 880:1168, 2] = 5
    
    # Exhaust nozzle: High metallic, lower roughness
    pbr_data[980:1080, 860:1188, 1] = 70
    pbr_data[980:1080, 860:1188, 2] = 230
    
    # Cockpit glass canopy patch region (1500-1800, 0-500)
    pbr_data[1500:1600, 50:500, 1] = 25  # Glass is very smooth
    pbr_data[1500:1600, 50:500, 2] = 10  # Dielectric glass
    
    pbr_img = Image.fromarray(pbr_data, mode="RGB")
    pbr_path = os.path.join(OUTPUT_DIR, "tejas_metallic_roughness.png")
    pbr_img.save(pbr_path, "PNG", optimize=True)
    print(f"  [x] Saved metallic-roughness texture: {pbr_path}")
    
    return diffuse_path, pbr_path

if __name__ == "__main__":
    create_tejas_textures()
