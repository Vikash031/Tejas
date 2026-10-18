/**
 * HAL TEJAS LCA NAVY (Mk1) — GEOFS INJECTOR
 * Authentic Indian Navy Livery, PBR Textures, Transparent Canopy Glass
 * 
 * HOW TO RUN IN GEOFS:
 * 1. Ensure local server is running: python tejas_geofs/viewer/server.py
 * 2. Open https://www.geo-fs.com/geofs.php in your browser (Chrome / Edge / Firefox)
 * 3. Press F12 (or Right-Click -> Inspect) to open Developer Tools -> Console tab
 * 4. Paste this command and hit Enter:
 *    fetch("http://localhost:8080/geofs_test_loader.js").then(r=>r.text()).then(eval);
 */
(function loadTejasNavyInGeoFS() {
    console.log("%c[HAL TEJAS LCA NAVY] INJECTING INDIAN NAVY FIGHTER JET...", "color: #ff9933; font-weight: bold; font-size: 14px;");

    if (!window.geofs || !geofs.aircraft || !geofs.aircraft.instance) {
        alert("[HAL TEJAS NAVY] GeoFS simulator not detected! Make sure you are on https://www.geo-fs.com/geofs.php");
        return;
    }

    try {
        const MODEL_URL = "http://localhost:8080/export/tejas_navy_geofs.glb";

        const definition = {
            "name": "HAL Tejas LCA Navy",
            "description": "HAL Tejas LCA Navy Mk1 carrier-capable multi-role lightweight fighter — Indian Navy",
            "scale": 1,
            "mass": 6560,
            "tensorFactor": 0.02,
            "dragFactor": 1.15,
            "com": [0, -0.4, 1.2],
            "gearTravelTime": 4.5,
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
            "startAltitude": 1.6,
            "startTilt": 0,
            "minimumSpeed": 115,
            "cockpitScaleFix": 1,
            "autopilot": true,
            "contactProperties": {
                "wheel": { "frictionCoef": 2.0, "dynamicFriction": 0.01, "rollingFriction": 0.0001, "lockSpeed": 0.01, "damping": 1 },
                "frame": { "frictionCoef": 1.4, "dynamicFriction": 0.01, "damping": 1 },
                "airfoil": { "frictionCoef": 1.4, "dynamicFriction": 0.01, "damping": 1 }
            },
            "instruments": {
                "airspeedJet": "", "altitude": "", "attitudeJet": "", "varioJet": "",
                "compass": "", "rpmJet": "", "brakes": "", "gear": ""
            },
            "cameras": {
                "cockpit": { "position": [0, 1.8, 1.9], "orientation": [0, -3, 0] },
                "follow": { "distance": 22 },
                "Right Wing": { "position": [4.5, -2.5, 1.5], "orientation": [-135, -5, 0] },
                "Left Wing": { "position": [-4.5, -2.5, 1.5], "orientation": [135, -5, 0] },
                "Gear View": { "position": [0, 3.5, 0.4], "orientation": [-180, -10, 0] }
            },
            "parts": [
                {
                    "name": "body",
                    "model": MODEL_URL,
                    "collisionPoints": [
                        [0, 6.2, 1.2],       // Nose tip
                        [0, -6.6, 1.4],      // Tail cone / exhaust
                        [-4.2, -2.5, 1.2],   // Left wingtip
                        [4.2, -2.5, 1.2],    // Right wingtip
                        [0, 3.2, 0.0],       // Nose gear contact
                        [-1.4, -1.2, 0.0],   // Left main gear contact
                        [1.4, -1.2, 0.0]     // Right main gear contact
                    ]
                },
                {
                    "name": "mainWingLeft",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [-1.8, -1.2, 1.2],
                    "area": 19.2,
                    "aspectRatio": 1.75,
                    "stalls": true,
                    "stallIncidence": 26,
                    "forceDirection": "Z",
                    "points": { "forceSourcePoint": [0, 0, 0] }
                },
                {
                    "name": "mainWingRight",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [1.8, -1.2, 1.2],
                    "area": 19.2,
                    "aspectRatio": 1.75,
                    "stalls": true,
                    "stallIncidence": 26,
                    "forceDirection": "Z",
                    "points": { "forceSourcePoint": [0, 0, 0] }
                },
                {
                    "name": "verticalFin",
                    "parent": "body",
                    "type": "airfoil",
                    "position": [0, -3.8, 2.8],
                    "area": 5.8,
                    "aspectRatio": 1.45,
                    "stalls": true,
                    "forceDirection": "X",
                    "points": { "forceSourcePoint": [0, 0, 0] }
                },
                {
                    "name": "engine",
                    "type": "engine",
                    "thrust": 84000,
                    "forceDirection": "Y",
                    "points": { "forceSourcePoint": [0, -6.6, 1.35] }
                },
                {
                    "name": "frontWheel",
                    "parent": "body",
                    "type": "wheel",
                    "position": [0, 3.2, 0.6],
                    "collisionPoints": [[0, 0, -0.6]],
                    "suspension": { "stiffness": 32, "damping": 7 }
                },
                {
                    "name": "leftGear",
                    "parent": "body",
                    "type": "wheel",
                    "position": [-1.4, -1.2, 0.7],
                    "collisionPoints": [[0, 0, -0.7]],
                    "suspension": { "stiffness": 42, "damping": 8 }
                },
                {
                    "name": "rightGear",
                    "parent": "body",
                    "type": "wheel",
                    "position": [1.4, -1.2, 0.7],
                    "collisionPoints": [[0, 0, -0.7]],
                    "suspension": { "stiffness": 42, "damping": 8 }
                }
            ]
        };

        const customRecord = {
            id: 9999,
            name: "HAL Tejas LCA Navy",
            fullPath: "http://localhost:8080/",
            definition: JSON.stringify([definition])
        };

        const parsedDefinition = geofs.aircraft.instance.parseRecord(customRecord);
        const currentCoords = geofs.aircraft.instance.getCurrentCoordinates();
        if (typeof geofs.aircraft.instance.unloadAircraft === "function") {
            geofs.aircraft.instance.unloadAircraft();
        }

        geofs.aircraft.instance.fullPath = customRecord.fullPath;
        geofs.aircraft.instance.aircraftRecord = customRecord;
        geofs.aircraft.instance.init(parsedDefinition, currentCoords);

        if (geofs.flyToNotification) {
            geofs.flyToNotification("HAL Tejas LCA Navy Active! Press '0'-'9' for Throttle, 'G' for Gear, 'C' for Cockpit.");
        }
        console.log("%c[HAL TEJAS LCA NAVY] AIRCRAFT READY FOR FLIGHT! ENJOY!", "color: #138808; font-weight: bold; font-size: 15px;");
    } catch (err) {
        console.error("[HAL TEJAS LCA NAVY] Error:", err);
        alert("[HAL TEJAS LCA NAVY] " + err.message);
    }
})();
