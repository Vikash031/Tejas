"""
Generates a 100% self-contained GeoFS in-game loader script.
Uses the official community GeoFS aircraft loading pattern:
1. Inlines 3D models as in-memory binary Blob URLs
2. Replaces part models with Blob URLs
3. Uses geofs.aircraft.instance.parseRecord()
4. Calls geofs.aircraft.instance.unloadAircraft()
5. Calls geofs.aircraft.instance.init(parsedDefinition, geofs.aircraft.instance.getCurrentCoordinates())
"""

import os
import json
import base64

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, "export")
DEF_PATH = os.path.join(BASE_DIR, "aircraft.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "geofs_test_loader.js")

def generate_loader():
    print("Reading aircraft definition and binary models...")
    with open(DEF_PATH, "r") as f:
        definition = json.load(f)

    # Read all required .glb parts and convert to base64
    model_b64 = {}
    parts = [
        "body.glb", "canopy.glb", "frontWheel.glb", "leftGear.glb",
        "rightGear.glb", "leftAileron.glb", "rightAileron.glb", "rudder.glb"
    ]
    for p in parts:
        p_path = os.path.join(EXPORT_DIR, p)
        if os.path.exists(p_path):
            with open(p_path, "rb") as bf:
                b64 = base64.b64encode(bf.read()).decode("ascii")
                model_b64[p] = b64
                print(f"  [x] Encoded {p} ({len(b64)/1024:.1f} KB base64)")
        else:
            print(f"  [!] Missing: {p}")

    def_json_str = json.dumps(definition)
    models_json_str = json.dumps(model_b64)

    script_content = f"""/**
 * HAL TEJAS Mk1 — 100% STANDALONE GEOFS FLIGHT TEST LOADER
 * 
 * ZERO SERVER REQUIRED. ZERO MIXED CONTENT RESTRICTIONS.
 * USES OFFICIAL GEOFS PARSERECORD + UNLOADAIRCRAFT + INIT PIPELINE.
 * 
 * INSTRUCTIONS:
 * 1. Open GeoFS in your browser: https://www.geo-fs.com/geofs.php
 * 2. Press F12 -> click 'Console' tab
 * 3. Copy and paste this ENTIRE file into the Console and press Enter!
 */

(function loadTejasInGeoFS() {{
    console.log("%c=======================================================", "color: #ff9933;");
    console.log("%c[HAL TEJAS Mk1] INJECTING SELF-CONTAINED AIRCRAFT...", "color: #ff9933; font-weight: bold; font-size: 14px;");
    console.log("%c=======================================================", "color: #ff9933;");

    if (!window.geofs || !geofs.aircraft || !geofs.aircraft.instance) {{
        alert("[HAL TEJAS Mk1] GeoFS simulator not detected! Make sure you are on https://www.geo-fs.com/geofs.php");
        return;
    }}

    try {{
        // Convert Base64 string to a local in-memory Blob URL
        function b64ToBlobUrl(b64) {{
            const bin = atob(b64);
            const len = bin.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {{
                bytes[i] = bin.charCodeAt(i);
            }}
            const blob = new Blob([bytes], {{ type: "model/gltf-binary" }});
            return URL.createObjectURL(blob);
        }}

        // 1. Embedded Base64 3D Models
        const modelData = {models_json_str};

        // 2. Generate in-memory Blob URLs for all 3D parts
        console.log("[HAL TEJAS Mk1] Creating in-memory 3D model buffers...");
        const blobUrls = {{}};
        for (const [filename, b64] of Object.entries(modelData)) {{
            blobUrls[filename] = b64ToBlobUrl(b64);
        }}

        // 3. Load aircraft definition and replace filenames with direct Blob URLs
        const definition = {def_json_str};
        const tejasDef = definition[0];

        tejasDef.parts.forEach(part => {{
            if (part.model && blobUrls[part.model]) {{
                part.model = blobUrls[part.model];
            }}
        }});

        // 4. Construct GeoFS Aircraft Record with Base64 encoded definition
        const customRecord = {{
            id: "custom_" + Date.now(),
            name: "HAL Tejas Mk1 (Indian Air Force)",
            fullPath: "", // Empty string so Blob URLs resolve directly
            isPremium: false,
            isCommunity: false,
            definition: btoa(JSON.stringify([tejasDef])),
            multiplayerFiles: []
        }};

        // 5. Parse definition using GeoFS internal parser
        console.log("[HAL TEJAS Mk1] Parsing definition through GeoFS engine...");
        const recordStr = JSON.stringify(customRecord);
        const parsedDefinition = geofs.aircraft.instance.parseRecord(recordStr);

        if (!parsedDefinition) {{
            throw new Error("geofs.aircraft.instance.parseRecord() failed to parse definition.");
        }}

        // 6. Unload current aircraft and initialize Tejas at current coordinates
        console.log("%c[HAL TEJAS Mk1] Spawning aircraft into simulator...", "color: #388bfd; font-weight: bold;");
        const currentCoords = geofs.aircraft.instance.getCurrentCoordinates();

        // Properly unload previous aircraft instance
        if (typeof geofs.aircraft.instance.unloadAircraft === "function") {{
            geofs.aircraft.instance.unloadAircraft();
        }}

        geofs.aircraft.instance.fullPath = customRecord.fullPath;
        geofs.aircraft.instance.aircraftRecord = customRecord;
        geofs.aircraft.instance.init(parsedDefinition, currentCoords);

        // Confirmation notification on HUD
        if (geofs.flyToNotification) {{
            geofs.flyToNotification("HAL Tejas Mk1 Loaded Successfully! Press '0'-'9' for Reheat, 'G' for Gear, 'C' for Cockpit.");
        }}

        console.log("%c=======================================================", "color: #138808;");
        console.log("%c[HAL TEJAS Mk1] READY FOR TAKEOFF! ENJOY FLYING!", "color: #138808; font-weight: bold; font-size: 15px;");
        console.log("%c=======================================================", "color: #138808;");

    }} catch (err) {{
        console.error("[HAL TEJAS Mk1] Injection error:", err);
        alert("[HAL TEJAS Mk1] Injection error: " + err.message);
    }}
}})();
"""

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out_f:
        out_f.write(script_content)

    print(f"Generated standalone loader: {OUTPUT_PATH} ({os.path.getsize(OUTPUT_PATH)/1024:.1f} KB)")

if __name__ == "__main__":
    generate_loader()
