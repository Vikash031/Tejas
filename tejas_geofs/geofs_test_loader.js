/**
 * HAL TEJAS LCA NAVY (Mk1) — GEOFS DIRECT INJECTOR
 * Supports:
 * 1. Automatic File Selector (100% bypasses Chrome Private Network / CORS blocks)
 * 2. Drag & Drop tejas_navy_geofs.glb directly onto the GeoFS window
 */
(function setupTejasNavyInjector() {
    console.log("%c[HAL TEJAS LCA NAVY] STARTING GEOFS INJECTOR...", "color: #ff9933; font-weight: bold; font-size: 14px;");

    if (!window.geofs || !geofs.aircraft || !geofs.aircraft.instance) {
        alert("GeoFS simulator not detected! Make sure you are on https://www.geo-fs.com/geofs.php");
        return;
    }

    function injectModel(modelBlobUrl) {
        try {
            console.log("[HAL TEJAS LCA NAVY] Injecting model:", modelBlobUrl);

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
                "autopilot": false,
                "Vspeeds": {
                    "VS0": 115,
                    "VS": 125,
                    "VFE": 250,
                    "VNO": 550,
                    "VNE": 750
                },
                "contactProperties": {
                    "wheel": { "frictionCoef": 2.0, "dynamicFriction": 0.01, "rollingFriction": 0.0001, "damping": 1 },
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
                    "Left Wing": { "position": [-4.5, -2.5, 1.5], "orientation": [135, -5, 0] }
                },
                "parts": [
                    {
                        "name": "body",
                        "model": modelBlobUrl,
                        "collisionPoints": [
                            [0, 6.2, 1.2], [0, -6.6, 1.4], [-4.2, -2.5, 1.2], [4.2, -2.5, 1.2],
                            [0, 3.2, 0.0], [-1.4, -1.2, 0.0], [1.4, -1.2, 0.0]
                        ]
                    },
                    { "name": "mainWingLeft", "parent": "body", "type": "airfoil", "position": [-1.8, -1.2, 1.2], "area": 19.2, "aspectRatio": 1.75, "stalls": true, "stallIncidence": 26, "forceDirection": "Z", "points": { "forceSourcePoint": [0, 0, 0] } },
                    { "name": "mainWingRight", "parent": "body", "type": "airfoil", "position": [1.8, -1.2, 1.2], "area": 19.2, "aspectRatio": 1.75, "stalls": true, "stallIncidence": 26, "forceDirection": "Z", "points": { "forceSourcePoint": [0, 0, 0] } },
                    { "name": "verticalFin", "parent": "body", "type": "airfoil", "position": [0, -3.8, 2.8], "area": 5.8, "aspectRatio": 1.45, "stalls": true, "forceDirection": "X", "points": { "forceSourcePoint": [0, 0, 0] } },
                    { "name": "engine", "type": "engine", "thrust": 84000, "forceDirection": "Y", "points": { "forceSourcePoint": [0, -6.6, 1.35] } },
                    { "name": "frontWheel", "parent": "body", "type": "wheel", "position": [0, 3.2, 0.6], "collisionPoints": [[0, 0, -0.6]], "suspension": { "stiffness": 32, "damping": 7 } },
                    { "name": "leftGear", "parent": "body", "type": "wheel", "position": [-1.4, -1.2, 0.7], "collisionPoints": [[0, 0, -0.7]], "suspension": { "stiffness": 42, "damping": 8 } },
                    { "name": "rightGear", "parent": "body", "type": "wheel", "position": [1.4, -1.2, 0.7], "collisionPoints": [[0, 0, -0.7]], "suspension": { "stiffness": 42, "damping": 8 } }
                ]
            };

            const currentCoords = geofs.aircraft.instance.getCurrentCoordinates();
            if (typeof geofs.aircraft.instance.unloadAircraft === "function") {
                geofs.aircraft.instance.unloadAircraft();
            }

            geofs.aircraft.instance.fullPath = "";
            geofs.aircraft.instance.aircraftRecord = { id: 9999, name: "HAL Tejas LCA Navy", fullPath: "" };
            geofs.aircraft.instance.init(definition, currentCoords);

            // 1. Unpause simulator & resume game loop
            geofs.doPause(0);

            // 2. Disengage autopilot so player has full manual throttle and control
            if (geofs.autopilot) {
                geofs.autopilot.turnOff();
            }

            // 3. Release brakes and clear stall state
            geofs.animation.values.brakes = 0;
            geofs.animation.values.parkingBrake = 0;

            // 4. Reset & activate camera (Mode 0 = Follow camera)
            if (geofs.camera) {
                geofs.camera.reset();
                geofs.camera.set(0);
            }

            // 5. Start GE F404 turbofan engine
            if (typeof geofs.aircraft.instance.startEngine === "function") {
                geofs.aircraft.instance.startEngine();
            }

            if (geofs.flyToNotification) {
                geofs.flyToNotification("HAL Tejas LCA Navy Active! Press '9' for Full Throttle, 'G' for Gear, 'C' for Cockpit.");
            }
            console.log("%c[HAL TEJAS LCA NAVY] AIRCRAFT READY FOR TAKEOFF! ENJOY YOUR FLIGHT!", "color: #138808; font-weight: bold; font-size: 16px;");
        } catch (err) {
            console.error("[HAL TEJAS LCA NAVY] Error:", err);
            alert("[HAL TEJAS LCA NAVY] Error: " + err.message);
        }
    }

    // Create file input to pick tejas_navy_geofs.glb locally
    let input = document.getElementById("tejas-file-picker");
    if (!input) {
        input = document.createElement("input");
        input.id = "tejas-file-picker";
        input.type = "file";
        input.accept = ".glb";
        input.style.display = "none";
        document.body.appendChild(input);
    }

    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            console.log("[HAL TEJAS LCA NAVY] Loading file:", file.name, `(${(file.size/1048576).toFixed(1)} MB)`);
            const blobUrl = URL.createObjectURL(file);
            injectModel(blobUrl);
        }
    };

    // Auto-trigger file dialog
    input.click();
    console.log("%c[HAL TEJAS LCA NAVY] Please select 'tejas_navy_geofs.glb' from your file dialog!", "color: #ff9933; font-weight: bold; font-size: 13px;");
})();
