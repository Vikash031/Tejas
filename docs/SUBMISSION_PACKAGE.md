# HAL Tejas LCA Navy Mk1 — GeoFS Community Submission Package

**Aircraft:** HAL Tejas LCA Navy Mk1 (Light Combat Aircraft — Naval Variant)  
**Operator / Livery:** Indian Navy Naval Air Arm (Serial: NP-1 / NP-2, Tail Code: `3002`)  
**Author:** [Vikash031](https://github.com/Vikash031)  
**Status:** Ready for Submission Review  
**Date:** 2026-10-18  

---

## 1. Aircraft Description

The **HAL Tejas LCA Navy Mk1** is the carrier-capable naval variant of India's indigenous Light Combat Aircraft programme, designed by ADA/HAL for operations from INS Vikrant (R11) and INS Vikramaditya (R33).

Key characteristics:
- **Engine:** General Electric F404-GE-IN20 — 84 kN wet reheat / 54 kN dry
- **Wing:** Tailless compound (cranked-arrow) delta with LERX
- **Carrier Config:** STOBAR (Ski-jump take-off, arrested recovery) with rear arrestor hook
- **Livery:** Indian Naval Air Arm — Ghost Grey `#788A9B` upper / Light Compass Grey `#AEC0D0` belly / dark radome `#384048`

---

## 2. Package Manifest & File Sizes

| File | Description | Size | Status |
|---|---|---|---|
| `tejas_geofs/aircraft.json` | Master GeoFS aircraft definition & aerodynamics | ~9 KB | ✅ Verified |
| `tejas_geofs/definition.json` | Mirror definition for backend editor compatibility | ~9 KB | ✅ Verified |
| `tejas_geofs/export/tejas_navy_geofs.glb` | Unified calibrated 3D model (Cesium-aligned) | ~38 MB | ✅ Verified |
| `tejas_geofs/tejas_navy.user.js` | Tampermonkey 1-click flight integration userscript | ~14 KB | ✅ Verified |
| `tejas_geofs/bookmarklet.txt` | Standalone drag-drop bookmarklet | ~6 KB | ✅ Verified |
| `tejas_geofs/geofs_test_loader.js` | In-browser direct injection loader | ~370 KB | ✅ Verified |

---

## 3. Completed Tests & Automated Verification

- [x] **glTF 2.0 Binary Header:** Magic `glTF`, version 2, length verified
- [x] **Dimensional Accuracy:** 13.20m length · 8.44m wingspan · wheels at Z=0.0m tarmac
- [x] **Cesium Axis Alignment:** forwardAxis=X, upAxis=Y — no sky-pointing on load
- [x] **Flight Dynamics Model:**
  - Empty Weight: 6,560 kg
  - Wing Area: 38.4 m² · Aspect Ratio: 1.75
  - Engine Thrust: 84 kN wet / 54 kN dry
  - Elevon mixed Roll/Pitch control
  - Retractable tricycle gear + arrestor hook
- [x] **Simulator Integration:** Verified unpause, brake release, engine start, camera reset
- [x] **Tampermonkey Userscript:** GM_xmlhttpRequest PNA bypass tested in Chrome
- [x] **CI Pipeline:** 9/9 workflow runs passing on GitHub Actions

---

## 4. Carrier Operations Support

Full STOBAR carrier operations for INS Vikrant / INS Vikramaditya:
- Ski-jump takeoff (14° ramp) — see [`docs/CARRIER_OPS.md`](../docs/CARRIER_OPS.md)
- Wire-trap arrested recovery (Wire #2 / #3)
- Dedicated **Carrier Approach** camera mode (`C` to cycle)
- Arrestor hook with speedbrake deployment linkage

---

## 5. Credits & Licensing

- **Aircraft Design:** Hindustan Aeronautics Limited (HAL) & Aeronautical Development Agency (ADA)
- **GeoFS Integration & 3D:** Community Developed by [Vikash031](https://github.com/Vikash031)
- **Livery & Markings:** Indian Naval Air Arm (public domain military markings)
- **License:** MIT — Open community add-on for GeoFS. Free for personal flight simulation.

---

## 6. Draft Email for Requesting GeoFS Developer Editor Permissions

```text
To: contact@geo-fs.com
Subject: GeoFS Community Aircraft Submission: HAL Tejas LCA Navy Mk1

Dear Xavier,

I have completed development and flight testing of a new community aircraft for GeoFS:
the HAL Tejas LCA Navy Mk1 (Indian Naval Air Arm carrier-capable fighter).

Project Summary:
- Aircraft: HAL Tejas LCA Navy Mk1 (STOBAR carrier operations)
- 3D Model: Authentic Indian Navy livery, unified glTF 2.0 GLB (~38 MB)
- Textures: 18 embedded decals — Tricolor fin flash, Navy Emblem, serial 3002, PBR glass
- Flight Model: 6,560 kg, 84 kN reheat (GE F404-IN20), compound delta, retractable gear + arrestor hook
- Carrier Support: STOBAR ski-jump takeoff + wire-trap recovery for INS Vikrant/Vikramaditya
- Testing: Validated via CI pipeline + Tampermonkey one-click integration tested in Chrome

GitHub Repository: https://github.com/Vikash031/Tejas
My GeoFS User ID: [INSERT YOUR GEOFS USER ID HERE]

Could you please grant my account aircraft editor permissions on https://www.geo-fs.com/backend/aircraft?

Thank you for creating GeoFS!

Best regards,
Vikash031
```
