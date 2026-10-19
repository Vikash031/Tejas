# 🇮🇳 HAL Tejas LCA Navy Mk1 — GeoFS Community Aircraft Package

<div align="center">

[![GeoFS Package CI](https://github.com/Vikash031/Tejas/actions/workflows/ci.yml/badge.svg)](https://github.com/Vikash031/Tejas/actions/workflows/ci.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/Vikash031/Tejas/pulls)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Vikash031/Tejas?style=flat-square&color=blue)](https://github.com/Vikash031/Tejas/pulls)
[![GitHub issues](https://img.shields.io/github/issues/Vikash031/Tejas?style=flat-square&color=orange)](https://github.com/Vikash031/Tejas/issues)
[![Version](https://img.shields.io/badge/version-v1.2.0--navy-blue.svg?style=flat-square)](https://github.com/Vikash031/Tejas/releases)
[![Simulator](https://img.shields.io/badge/Simulator-GeoFS%20v3.9+-1e3a5f.svg?style=flat-square)](https://www.geo-fs.com)
[![Aircraft](https://img.shields.io/badge/Aircraft-HAL%20Tejas%20LCA%20Navy-0a192f.svg?style=flat-square)](https://en.wikipedia.org/wiki/HAL_Tejas)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

**High-fidelity Indian Navy carrier-capable multi-role lightweight fighter jet package for [GeoFS](https://www.geo-fs.com).**  
Featuring authentic naval air superiority grey camouflage, transparent cockpit canopy, GE F404 reheat physics, and one-click flight integration.

[✈️ Quick Flight Guide](#️-quick-flight-guide) • [🎮 Flight Controls](#-flight-controls-in-geofs) • [⚓ Carrier Ops](docs/CARRIER_OPS.md) • [🛠️ Contributing](#️-contributing--pull-requests) • [📜 Changelog](PROJECT_PROGRESS.txt)

---

</div>

## 🌟 Highlights

* **Authentic Naval Livery:** Dual-tone Air Superiority Ghost Grey (`#788A9B` upper, `#AEC0D0` belly, `#384048` radome) with 18 authentic decals (Tricolor fin flash, Navy Emblem, serial `3002`, Navy markings, tire treads).
* **Transparent Canopy:** PBR semi-transparent glass (`alphaMode: BLEND`, 20% opacity) showing cockpit interior, HUD alpha, and ejection seat.
* **Calibrated Cesium Aerodynamics:** Tailored to Cesium axes (+X forward, +Y up) with zero left-drift, authentic compound delta wing stalling (>26° AoA), and 84 kN reheat thrust.
* **1-Click GeoFS Integration:** Dedicated Tampermonkey userscript with on-screen `[✈ FLY HAL TEJAS]` button completely bypassing Chrome Private Network Access restrictions.
* **Carrier Operations:** Full STOBAR ski-jump takeoff and wire-trap recovery for INS Vikrant / INS Vikramaditya. See [Carrier Ops Manual](docs/CARRIER_OPS.md).

---

## ✈️ Quick Flight Guide

### Method A: One-Click Userscript (Recommended — Zero Copy-Pasting)
1. Install [Tampermonkey for Chrome](https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo).
2. Create a new script and paste [`tejas_geofs/tejas_navy.user.js`](tejas_geofs/tejas_navy.user.js). Save with **Ctrl+S**.
3. Open [GeoFS (geo-fs.com/geofs.php)](https://www.geo-fs.com/geofs.php).
4. Click the on-screen **`[✈ FLY HAL TEJAS]`** button to spawn and fly!

### Method B: Browser Bookmarklet
1. Copy the contents of [`tejas_geofs/bookmarklet.txt`](tejas_geofs/bookmarklet.txt).
2. Right-click your Chrome Bookmarks Bar (Ctrl+Shift+B) → **Add page...** → Name: `Fly Tejas`, URL: `<paste>`.
3. Click the bookmark while on GeoFS to pick `tejas_navy_geofs.glb` and fly.

---

## 🎮 Flight Controls in GeoFS

| Key | Action | Flight Effect |
|---|---|---|
| `9` | Full Reheat (Afterburner) | Max thrust 84,000 N; Mach 1.6 sprint |
| `0` | Idle Throttle | Flight idle (1,000 RPM) |
| `G` | Toggle Landing Gear | Retract/extend tricycle gear (4.5s cycle) |
| `B` | Airbrakes / Wheel Brakes | Deploys dorsal speedbrake & wheel brakes |
| `C` | Cycle Camera | Cockpit POV / Chase Camera / Wing POV / Carrier Approach |
| `Arrows` / Stick | Pitch & Roll | Compound delta elevon response |

---

## 📁 Repository Structure

```
proj_tejas/
├── .github/
│   ├── workflows/ci.yml             # Automated CI validation pipeline
│   ├── pull_request_template.md     # Standardised flight-test PR template
│   └── ISSUE_TEMPLATE/bug_report.yml
├── docs/
│   ├── CARRIER_OPS.md               # INS Vikrant / Vikramaditya ops manual
│   ├── GEOFS_REQUIREMENTS.md        # GeoFS technical specification reference
│   └── SUBMISSION_PACKAGE.md        # Official submission manifest & email draft
├── scripts/
│   └── export_navy_colours.py       # GLB colour export utility
├── tejas_geofs/
│   ├── export/
│   │   └── tejas_navy_geofs.glb     # Calibrated 38 MB master 3D model
│   ├── viewer/                      # WebGL interactive 3D viewer (Three.js)
│   ├── tejas_navy.user.js           # 1-Click Tampermonkey userscript
│   ├── geofs_test_loader.js         # Direct in-browser injector
│   ├── bookmarklet.txt              # Standalone Chrome bookmarklet
│   ├── aircraft.json                # GeoFS aircraft definition
│   └── definition.json              # Detailed physics specification
├── tests/
│   └── test_geofs_package.py        # Automated test suite (CI validation)
├── requirements.txt                 # Python dependencies
└── PROJECT_PROGRESS.txt             # Chronological engineering audit log
```

---

## 🛠️ Contributing & Pull Requests

Contributions, livery variants, and flight tuning PRs are warmly welcomed!

1. **Fork & Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Run Validation Tests:**
   ```bash
   pip install -r requirements.txt
   python -m unittest discover tests -v
   ```
3. **Submit a Pull Request:** Open your PR against `main`. All CI checks run automatically to verify the model and physics schemas.

---

## 📄 License & Credits

* **Model & Package:** Indian Navy HAL Tejas LCA Mk1 Community Edition by [Vikash031](https://github.com/Vikash031).
* **Simulator:** Designed for [GeoFS](https://www.geo-fs.com) by Xavier Tassin.
* **License:** MIT License. See [LICENSE](LICENSE) for details.
