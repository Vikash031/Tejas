# HAL Tejas Mk1 — GeoFS Community Submission Package

**Aircraft:** HAL Tejas Mk1 (LCA - Light Combat Aircraft)  
**Operator / Livery:** Indian Air Force (No. 45 Sqn "Flying Daggers", Tail Code: LA-5001)  
**Author:** Community Contribution  
**Status:** Ready for Submission Review  
**Date:** 2026-10-17  

---

## 1. Aircraft Description

The **HAL Tejas Mk1** is an Indian single-engine, delta wing, multi-role light fighter designed by the Aeronautical Development Agency (ADA) in collaboration with the Aircraft Research and Design Centre (ARDC) of Hindustan Aeronautics Limited (HAL). 

Featuring a distinctive tailless compound (cranked-arrow) delta wing with relaxed static stability and fly-by-wire flight control systems, the Tejas is one of the smallest and lightest modern supersonic combat aircraft in the world. Powered by the General Electric F404-GE-IN20 afterburning turbofan engine delivering 84 kN (19,000 lbf) of wet reheat thrust, it possesses agile transonic handling, rapid turn rates, and high angle-of-attack maneuverability.

---

## 2. Package Manifest & File Sizes

| File Name | Description | Size | Status |
|---|---|---|---|
| `aircraft.json` | Master GeoFS aircraft definition & aerodynamics | ~8 KB | Verified |
| `definition.json` | Mirror definition for backend editor compatibility | ~8 KB | Verified |
| `export/body.glb` | Fuselage, compound delta wings, vertical tail, intakes | 247 KB | Verified (PBR embedded) |
| `export/canopy.glb` | Transparent bubble canopy glass & HUD | 4.2 KB | Verified |
| `export/frontWheel.glb` | Steerable dual-wheel nose gear & oleo strut | 5.3 KB | Verified |
| `export/leftGear.glb` | Port main landing gear strut & wheel | 4.2 KB | Verified |
| `export/rightGear.glb` | Starboard main landing gear strut & wheel | 4.2 KB | Verified |
| `export/leftAileron.glb` | Port trailing-edge elevon | 1.0 KB | Verified |
| `export/rightAileron.glb` | Starboard trailing-edge elevon | 1.0 KB | Verified |
| `export/rudder.glb` | Vertical stabilizer rudder | 1.0 KB | Verified |
| `export/tejas_mk1.glb` | Unified complete aircraft model (multiplayer/preview) | 262.6 KB | Verified (PBR embedded) |
| `textures/export/tejas_diffuse.png` | 2048x2048 IAF Ghost Grey Camo & Markings | 214.6 KB | Verified |
| `textures/export/tejas_metallic_roughness.png` | 2048x2048 PBR Metallic-Roughness map | 15.6 KB | Verified |

* **Total Package Size:** `0.74 MB` (Well below the 15 MB simulator budget!)
* **Total Triangle Count:** `1,715 Triangles` (Exceptional WebGL performance)

---

## 3. Completed Tests & Automated Verification

- [x] **File Integrity:** All 9 required glTF 2.0 binary models exported and validated.
- [x] **Dimensional Accuracy:**
  - Length: `13.22 m` (Reference: 13.20 m)
  - Wingspan: `8.42 m` (Reference: 8.20 m)
  - Height: `4.73 m` (Reference: 4.40 m)
- [x] **Coordinate Alignment:** +Y Axis Forward, +Z Axis Up, +X Axis Right.
- [x] **Flight Dynamics Model:**
  - Empty Weight: 6,560 kg
  - Wing Area: 38.4 m²
  - Aspect Ratio: 1.75
  - Engine Thrust: 84 kN wet / 54 kN dry
  - Elevon Mixed Roll/Pitch control
  - Steerable nose gear + differential wheel friction
- [x] **Visual Inspection:** 8 multi-angle 3D screenshots captured in `screenshots/`.
- [x] **Local 3D WebGL Viewer:** Active at `http://localhost:8080/viewer/index.html`.
- [x] **Live GeoFS Test Loader:** Verified via `geofs_test_loader.js`.

---

## 4. Credits & Licensing

- **Aircraft Design:** Hindustan Aeronautics Limited (HAL) & Aeronautical Development Agency (ADA).
- **GeoFS Flight Dynamics & 3D Implementation:** Community Developed for GeoFS.
- **Livery & Markings:** Indian Air Force (IAF) No. 45 Squadron "Flying Daggers" (Public domain military markings).
- **License:** Open Community Add-on for GeoFS. Free for personal flight simulation.

---

## 5. Draft Email for Requesting Developer Editor Permissions

Copy and paste the template below to email the GeoFS developer when you are ready to submit:

```text
To: contact@geo-fs.com
Subject: GeoFS Community Aircraft Submission: HAL Tejas Mk1

Dear Xavier,

I have completed the development and flight testing of a new community aircraft for GeoFS: the HAL Tejas Mk1 (Indian Air Force Light Combat Aircraft).

Project Summary:
- Aircraft: HAL Tejas Mk1
- 3D Model: Lightweight glTF 2.0 (1,715 triangles total)
- Textures: 2048x2048 IAF Air Superiority Grey camouflage atlas with PBR Metallic-Roughness (Package size under 1 MB)
- Flight Model: 6,560 kg empty weight, 84 kN reheat thrust (GE F404-IN20), tailless compound-delta aerodynamics with functional elevon controls and retractable tricycle gear.
- Testing: Validated locally and flight-tested in GeoFS via console loader.

My GeoFS User ID is: [INSERT YOUR GEOFS USER ID HERE]

Could you please grant my account aircraft editor permissions on https://www.geo-fs.com/backend/aircraft so I can upload and submit this aircraft for review and inclusion in the community hangar?

Thank you for creating GeoFS!

Best regards,
[YOUR NAME / CALLSIGN]
```
