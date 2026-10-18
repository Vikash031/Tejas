## ✈️ Pull Request: HAL Tejas Mk1 / LCA Navy Package

### 📌 Summary of Changes
<!-- Provide a brief description of what this PR introduces or fixes -->
- 

### 🗂️ Change Type
- [ ] 🎨 **3D Model & Livery** (Mesh update, camouflage texture, cockpit canopy transparency)
- [ ] ⚡ **Flight Dynamics** (Engine thrust, V-speeds, delta wing aerodynamics, center of mass)
- [ ] ⚓ **Naval Operations** (Carrier arrestor hook, ski-jump takeoff physics, landing gear damping)
- [ ] 🛠️ **Simulator Integration** (GeoFS loader, Tampermonkey userscript, bookmarklet)
- [ ] 🧪 **Testing & CI** (Automated validation suite, workflow actions)
- [ ] 📚 **Documentation** (Specifications, README, flight instructions)

### 🛫 Flight Sim Verification Checklist
- [ ] Simulator unpauses cleanly (`geofs.doPause(0)`) without controls locking
- [ ] Tricycle landing gear rolls smoothly on tarmac without ground clipping
- [ ] HUD & Cockpit camera (`geofs.camera.modes[0]`) aligns with HUD glass
- [ ] Delta wing stalls realistically at high alpha (>26° AoA)
- [ ] Full reheat afterburner engages smoothly with key `9`
- [ ] All automated tests pass (`python -m unittest discover tests`)

### 📸 Screenshots / Previews
<!-- Attach in-game screenshots, 3D viewer renders, or test flight clips if applicable -->

---
*Authored under `Vikash031` for the Indian Navy HAL Tejas LCA flight simulator project.*
