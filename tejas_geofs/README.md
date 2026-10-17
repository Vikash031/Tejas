# HAL Tejas Mk1 — GeoFS Community Aircraft Package

Welcome to the **HAL Tejas Mk1** aircraft project for the [GeoFS](https://www.geo-fs.com) web flight simulator!

Everything has been automated for you. You **do not need Blender** or 3D modeling skills to view, test-fly, or submit this aircraft.

---

## 📁 Project Directory Map

* **3D Aircraft Models (`.glb`):** `tejas_geofs/export/`
  * `body.glb` — Fuselage, delta wings, vertical fin, air intakes, cockpit tub
  * `canopy.glb` — Bubble canopy glass
  * `frontWheel.glb` — Steerable nose gear with twin wheels
  * `leftGear.glb` & `rightGear.glb` — Retractable main landing gear assemblies
  * `leftAileron.glb` & `rightAileron.glb` — Movable elevon control surfaces
  * `rudder.glb` — Movable vertical stabilizer rudder
  * `tejas_mk1.glb` — Unified master model (for 3D viewer & multiplayer)
* **Textures & Livery:** `tejas_geofs/textures/export/`
  * `tejas_diffuse.png` — Indian Air Force dual-tone camo, roundels, stencils
  * `tejas_metallic_roughness.png` — PBR metallic-roughness map
* **GeoFS Aircraft Definitions:**
  * `tejas_geofs/aircraft.json`
  * `tejas_geofs/definition.json`
* **Automated Scripts:**
  * `tejas_geofs/scripts/build_standalone_glb.py` — Generates 3D models without Blender
  * `tejas_geofs/scripts/generate_textures.py` — Procedural texture generator
  * `tejas_geofs/scripts/render_previews.py` — Renders 8 preview screenshots
  * `tejas_geofs/blender/build_tejas.py` — Native Blender procedural builder
  * `tejas_geofs/blender/validate_model.py` — 22-point automated test suite
* **Testing & Viewing Tools:**
  * `tejas_geofs/viewer/index.html` — Interactive 3D Web Viewer
  * `tejas_geofs/viewer/server.py` — Local HTTP server
  * `tejas_geofs/geofs_test_loader.js` — Live GeoFS in-game loader script
* **Screenshots & Documentation:**
  * `tejas_geofs/screenshots/` — 8 multi-angle preview renders
  * `tejas_geofs/GEOFS_REQUIREMENTS.md` — Complete technical requirements
  * `tejas_geofs/SUBMISSION_PACKAGE.md` — Submission manifest & developer email draft
  * `PROJECT_PROGRESS.txt` — Project audit log

---

## 🚀 How to View the Aircraft (Interactive 3D Web Viewer)

You can view and inspect the aircraft in 3D right now in your web browser:

1. Open your terminal in this project folder and run:
   ```powershell
   python tejas_geofs/viewer/server.py
   ```
2. Open your web browser (Chrome, Edge, Firefox) and go to:
   ```
   http://localhost:8080/viewer/index.html
   ```
3. You can:
   * **Rotate 360° & Zoom:** Left-click and drag to rotate, scroll wheel to zoom.
   * **Move Control Surfaces:** Use the sliders for Elevon Pitch, Roll, and Rudder Yaw.
   * **Toggle Landing Gear:** Click the gear button to see deployed / retracted states.
   * **Inspect Views:** Click Top Planform, Side Profile, Front Nose, or Cockpit POV.

---

## ✈️ How to Test Fly the Aircraft Live in GeoFS

GeoFS runs directly in your browser, meaning you can test-fly your Tejas in the actual game right now:

1. Keep the local server running:
   ```powershell
   python tejas_geofs/viewer/server.py
   ```
2. Open the GeoFS flight simulator in your browser:
   [https://www.geo-fs.com/geofs.php](https://www.geo-fs.com/geofs.php)
3. Open your browser's Developer Tools Console:
   * Press `F12` on your keyboard (or right-click anywhere and click **Inspect**).
   * Click on the **Console** tab at the top.
4. Open the file `tejas_geofs/geofs_test_loader.js`, copy all its code, paste it into the console, and press `Enter`.
5. **Takeoff!** The simulator will instantly load your HAL Tejas Mk1.
   * Press `0` to `9` for throttle (full reheat).
   * Use your arrow keys / joystick to pull back and climb.
   * Press `G` to retract/extend landing gear.
   * Press `C` to switch between Cockpit, Chase, and Wing camera views.

---

## 🎨 How to Install Blender (If You Ever Want It)

Blender is **not currently installed** on your computer. You do not need it to use this project, but if you ever want the native 3D software:

### Option A: Via Windows Package Manager (Fastest & Automatic)
Open PowerShell and run:
```powershell
winget install BlenderFoundation.Blender
```
Press `Y` if prompted. Windows will download and install Blender automatically.

### Option B: Via Official Website
1. Go to [https://www.blender.org/download/](https://www.blender.org/download/)
2. Click **Download Blender** (Windows Installer `.msi`).
3. Run the downloaded installer and click **Next** through the setup wizard.

Once installed, you can generate the native `.blend` file anytime by running:
```powershell
blender --background --python tejas_geofs/blender/build_tejas.py
```

---

## 📬 How to Submit to GeoFS Community

1. Test-fly the aircraft in GeoFS using the instructions above to ensure you like how it handles.
2. Find your **GeoFS User ID** in your GeoFS account settings.
3. Open `tejas_geofs/SUBMISSION_PACKAGE.md`, copy the pre-written email in Section 5, fill in your User ID, and send it to **`contact@geo-fs.com`**.
4. Once Xavier enables editor permissions for your account, upload the files from `tejas_geofs/export/` and paste `tejas_geofs/aircraft.json` into the editor at [https://www.geo-fs.com/backend/aircraft](https://www.geo-fs.com/backend/aircraft).
