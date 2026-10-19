# GeoFS Aircraft Development Requirements & Technical Specification

**Project:** HAL Tejas Mk1 for GeoFS  
**Status:** Phase 1 Complete (Researched & Verified)  
**Last Updated:** 2026-10-17  

---

## 1. Official Documentation & Source Links

1. **GeoFS Aircraft Editor Portal:**  
   [https://www.geo-fs.com/backend/aircraft](https://www.geo-fs.com/backend/aircraft)  
   *The official backend portal used by approved community developers and Xavier (GeoFS Creator) to configure, manage, and submit aircraft.*

2. **GeoFS Aircraft Editor Announcement & Guidelines:**  
   [https://blog.geo-fs.com/2017/06/geofs-aircraft-editor.html](https://blog.geo-fs.com/2017/06/geofs-aircraft-editor.html)  
   *Confirms the modern architecture: no need to manually separate all animated parts; models and animation nodes are loaded into Cesium / WebGL.*

3. **GeoFS Runtime Architecture (`geofs.aircraft`):**  
   - Core runtime object: `geofs.aircraft.instance`  
   - Parser: `geofs.aircraft.instance.parseRecord(record)`  
   - Definition format: Base64-encoded JSON or direct definition object passed to `init()`  
   - Reference Repository: [geofs-plugins/aircraft-warehouse](https://github.com/geofs-plugins/aircraft-warehouse) & [geofs-plugins/aircraft-loader](https://github.com/geofs-plugins/aircraft-loader)

4. **HAL Tejas Official Reference:**  
   [https://hal-india.co.in/product/lca](https://hal-india.co.in/product/lca) & [https://lcatejas.com](https://lcatejas.com)

---

## 2. Verified Requirements

### A. Coordinate Conventions & Units
* **Units:** Metric (metres for dimensions/offsets, kilograms for mass, Newtons for thrust).
* **Aircraft Coordinate System in GeoFS:**
  * **+Y axis:** Forward (Nose direction)
  * **-Y axis:** Aft (Tail / Exhaust direction)
  * **+X axis:** Right wingtip
  * **-X axis:** Left wingtip
  * **+Z axis:** Upwards (Ceiling / Canopy / Vertical Fin)
  * **-Z axis:** Downwards (Ground / Landing Gear extension)
* **Rotations:** Angles are typically specified in degrees.
  * Pitch: Rotation around X axis
  * Roll: Rotation around Y axis
  * Yaw: Rotation around Z axis

### B. 3D Model Formats & Structure
* **Format:** Binary glTF 2.0 (`.glb`) or standard `.gltf` with textures.
* **Separation vs. Hierarchy:**
  * Supported: Separate `.glb` meshes for distinct moving parts (`body.glb`, `leftAileron.glb`, `rudder.glb`, `leftGear.glb`, etc.) or named node hierarchy inside a single master `.glb`.
  * For highest compatibility across both the backend editor and community loaders, a modular multi-part `.glb` setup or single rigged hierarchy with standard node names is used.
* **Scale:** Real-world 1:1 scale (1 unit = 1 metre).
* **Materials & Textures:**
  * PBR Metallic-Roughness workflow (`baseColorTexture`, `metallicRoughnessTexture`, `normalTexture`).
  * Texture resolutions: 2048x2048 for fuselage/wings; 1024x1024 for cockpit and gear. Texture atlasing strongly recommended to minimize HTTP draw calls.
  * Power-of-two (POT) textures: Required for WebGL mipmapping (1024x1024, 2048x2048).

### C. Aircraft Definition (`definition.json` / `aircraft.json`)
The definition JSON is wrapped inside an array `[ { ... } ]` with the following top-level keys:

```json
{
  "scale": 1,
  "mass": 6560,
  "tensorFactor": 0.02,
  "dragFactor": 1.2,
  "com": [0, 0, 0],
  "gearTravelTime": 5,
  "flapsTravelTime": 0,
  "flapsSteps": 0,
  "airbrakesTravelTime": 1.2,
  "brakeDamping": 8,
  "zeroThrustAltitude": 55000,
  "reverse": false,
  "minRPM": 1000,
  "maxRPM": 10000,
  "driveRatio": 0.3,
  "engineInertia": 0.8,
  "startupTime": 8,
  "startAltitude": 2.2,
  "startTilt": 0,
  "minimumSpeed": 120,
  "cockpitScaleFix": 1,
  "autopilot": true,
  "contactProperties": {
    "wheel": { "frictionCoef": 4.5, "dynamicFriction": 0.01, "rollingFriction": 0.0002, "lockSpeed": 0.01, "damping": 1 },
    "frame": { "frictionCoef": 1.4, "dynamicFriction": 0.01, "damping": 1 },
    "airfoil": { "frictionCoef": 1.4, "dynamicFriction": 0.01, "damping": 1 }
  },
  "instruments": {
    "airspeedJet": "",
    "altitude": "",
    "attitudeJet": "",
    "varioJet": "",
    "compass": "",
    "rpmJet": "",
    "brakes": "",
    "gear": ""
  },
  "cameras": {
    "cockpit": { "position": [0, 1.8, 0.75], "orientation": [0, -4, 0] },
    "follow": { "distance": 28 }
  },
  "parts": [ ... ]
}
```

### D. Parts & Animations Specification
1. **Fuselage (`body`):** Parent part containing collision points for belly/nose/wingtip contacts.
2. **Airfoils (Wings & Control Surfaces):**
   * `type: "airfoil"`
   * `area`: Wing surface area (m²)
   * `aspectRatio`: Span / Mean Chord
   * `forceDirection`: `"Z"` (for lift) or `"X"` (for vertical fin sideforce)
   * `stalls`: true
   * `points`: `{ "forceSourcePoint": [x, y, z] }`
   * Animations:
     * Elevons/Ailerons: `type: "rotate"`, `axis: "X"`, `value: "roll"` (or mixed `"pitch"` and `"roll"`)
     * Rudder: `type: "rotate"`, `axis: "Z"`, `value: "yaw"`
3. **Engine (`engine`):**
   * `type: "engine"`
   * `thrust`: 84000 N (with reheat) / 54000 N (dry)
   * `forceDirection`: `"Y"`
   * `points`: `{ "forceSourcePoint": [0, -6.0, 0] }`
4. **Landing Gear (`wheel`):**
   * Tricycle gear: 1 nose gear, 2 main gears.
   * `type: "wheel"`
   * `collisionPoints`: Contact coordinates `[x, y, z]` relative to gear part pivot.
   * `suspension`: `{ "stiffness": 30, "damping": 6 }`
   * Animations:
     * Retraction: `type: "rotate"`, `value: "gearPosition"`, `ratio: 90`
     * Hide when stowed: `type: "hide"`, `value: "gearPosition"`, `threshold: 0.99`
     * Nosewheel steering: `type: "rotate"`, `axis: "Z"`, `value: "yaw"`, `ratio: 40`

---

## 3. Publication Process & Developer Permissions

* **Access Requirements:** Access to the official backend editor (`/backend/aircraft`) is restricted to authorized contributors.
* **How to Request:** Email Xavier Tassin at `contact@geo-fs.com` (or `xtassin@gmail.com`) stating:
  1. Your GeoFS User ID (not callsign).
  2. The aircraft project name: **HAL Tejas Mk1**.
  3. Screenshots / renders and project description.
* **Testing without prior approval:**
  * Fully supported! The GeoFS community tests custom aircraft by injecting the definition and model URLs directly into the live simulator via the browser console or a lightweight Tampermonkey userscript (`geofs.aircraft.instance.init(...)`).
  * This allows 100% flight testing, tuning, and bug fixing before submitting to the developer.

---

## 4. File Size Limits & Optimization Guidelines

* Total aircraft package: Should ideally remain **under 15 MB** (uncompressed) to ensure fast loading for multiplayer.
* 3D Geometry: Under 30,000 triangles total for browser WebGL rendering efficiency.
* Textures: Combined texture footprint under 8 MB (using compressed JPEG or optimized PNG/WebP).

---

## 5. Uncertainties & Verification Status

| Item | Status | Verification Detail |
|---|---|---|
| Single GLB vs Multi-file GLB | **Verified** | Both are supported; separate GLB parts (`body.glb`, `rudder.glb`) are the standard community format for legacy/backend editor, while single GLBs with internal node hierarchies are supported in newer Cesium builds. We will support both! |
| Coordinate System (+Y forward, +Z up) | **Verified** | Verified against official `B738/aircraft.json` and `Ecological314/Blender-GeoFS-Utilities`. |
| Audio/Sound Assets | **Verified** | Jetliner/fighter sounds (`jetliner/rpm1.mp3`, `tyres/rolling1.mp3`) are built-in GeoFS sound assets available to all aircraft. |
| Elevon Mixing Support | **Unverified / Simulator-Specific** | In GeoFS, elevons are typically modeled either as separate roll/pitch surfaces or using multi-animation blocks on the same part (`rotate` roll + `rotate` pitch). We will configure dual animation entries. |

---

## 6. Implementation Plan

1. **Phase 2 & 3:** Model procedural geometry of HAL Tejas Mk1 (slender nose, compound delta wing, vertical fin, single engine intake/nozzle, landing gear) with IAF low-visibility camouflage and roundels.
2. **Phase 4:** Write reproducible Blender Python scripts (`build_tejas.py`, `validate_model.py`, `render_previews.py`) and pure Python glTF generator as a standalone fallback.
3. **Phase 5 & 6:** Generate complete GeoFS aircraft definition (`aircraft.json` / `definition.json`) tuned to HAL Tejas Mk1 specs.
4. **Phase 7 & 8:** Package all assets, optimize textures and polygon counts.
5. **Phase 9 & 10:** Automated validation, local 3D viewer, and browser console injection script for live flight testing in GeoFS.
6. **Phase 11 & 12:** Submission package, publication draft email, and beginner-friendly user guide.
