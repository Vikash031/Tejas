// ==UserScript==
// @name         GeoFS - HAL Tejas LCA Navy Mk1
// @namespace    https://github.com/Vikash031/Tejas
// @version      1.0
// @description  One-click fly the Indian Navy HAL Tejas LCA fighter jet in GeoFS with authentic camouflage, transparent canopy, and tuned flight physics.
// @author       Vikash031
// @match        https://www.geo-fs.com/geofs.php*
// @match        https://geo-fs.com/geofs.php*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// @connect      127.0.0.1
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    console.log("%c[HAL TEJAS LCA NAVY] Tampermonkey Userscript Loaded", "color: #ff9933; font-weight: bold; font-size: 14px;");

    function getTejasDefinition(modelBlobUrl) {
        return {
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
                        [0, 6.2, 1.2],       // Nose tip
                        [0, -6.6, 1.4],      // Tail cone / exhaust
                        [-4.2, -2.5, 1.2],   // Left wingtip
                        [4.2, -2.5, 1.2],    // Right wingtip
                        [0, -3.8, 4.8]       // Vertical stabilizer fin tip
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
    }

    function injectTejas(modelBlobUrl) {
        if (!window.geofs || !geofs.aircraft || !geofs.aircraft.instance) {
            alert("GeoFS is still initializing. Please wait 5 seconds and click again.");
            return;
        }

        console.log("%c[HAL TEJAS LCA NAVY] Spawning aircraft with model:", "color: #138808; font-weight: bold;", modelBlobUrl);

        const definition = getTejasDefinition(modelBlobUrl);
        const currentCoords = geofs.aircraft.instance.getCurrentCoordinates();

        if (typeof geofs.aircraft.instance.unloadAircraft === "function") {
            geofs.aircraft.instance.unloadAircraft();
        }

        geofs.aircraft.instance.fullPath = "";
        geofs.aircraft.instance.aircraftRecord = { id: 9999, name: "HAL Tejas LCA Navy", fullPath: "" };
        geofs.aircraft.instance.init(definition, currentCoords);

        // Safe unpause & control release loop (executes at 200ms, 800ms, and 2000ms after model load)
        [200, 800, 2000].forEach(delay => {
            setTimeout(() => {
                try {
                    if (typeof controls !== "undefined" && controls.reset) controls.reset();
                    if (typeof geofs.aircraft.instance.reset === "function") geofs.aircraft.instance.reset();
                    if (typeof instruments !== "undefined" && instruments.reset) instruments.reset();

                    geofs.doPause(0);

                    if (geofs.autopilot) geofs.autopilot.turnOff();

                    geofs.animation.values.brakes = 0;
                    geofs.animation.values.parkingBrake = 0;

                    if (geofs.camera) geofs.camera.reset();

                    if (typeof geofs.aircraft.instance.startEngine === "function") {
                        geofs.aircraft.instance.startEngine();
                    }
                } catch (e) {
                    console.warn("[HAL TEJAS LCA NAVY] Lifecycle sync:", e);
                }
            }, delay);
        });

        if (geofs.flyToNotification) {
            geofs.flyToNotification("HAL Tejas LCA Navy Ready! Press 9 for Full Throttle, G for Gear, C for Cockpit.");
        }
    }

    function triggerFilePicker() {
        let input = document.getElementById("tejas-tm-picker");
        if (!input) {
            input = document.createElement("input");
            input.id = "tejas-tm-picker";
            input.type = "file";
            input.accept = ".glb";
            input.style.display = "none";
            document.body.appendChild(input);
            input.onchange = function(e) {
                const file = e.target.files[0];
                if (file) {
                    const blobUrl = URL.createObjectURL(file);
                    injectTejas(blobUrl);
                }
            };
        }
        input.click();
    }

    function loadFromLocalServerOrPicker() {
        // Try GM_xmlhttpRequest first (bypasses Chrome Private Network Access)
        if (typeof GM_xmlhttpRequest !== "undefined") {
            console.log("[HAL TEJAS LCA NAVY] Attempting direct fetch from http://localhost:8080/export/tejas_navy_geofs.glb...");
            GM_xmlhttpRequest({
                method: "GET",
                url: "http://localhost:8080/export/tejas_navy_geofs.glb",
                responseType: "blob",
                timeout: 3000,
                onload: function(res) {
                    if (res.status === 200 && res.response) {
                        console.log("%c[HAL TEJAS LCA NAVY] Local server model fetched successfully!", "color: #138808; font-weight: bold;");
                        const blobUrl = URL.createObjectURL(res.response);
                        injectTejas(blobUrl);
                    } else {
                        console.warn("[HAL TEJAS LCA NAVY] Local server returned status:", res.status, "- opening file picker.");
                        triggerFilePicker();
                    }
                },
                ontimeout: function() {
                    console.warn("[HAL TEJAS LCA NAVY] Local server timed out - opening file picker.");
                    triggerFilePicker();
                },
                onerror: function() {
                    console.warn("[HAL TEJAS LCA NAVY] Local server unreachable - opening file picker.");
                    triggerFilePicker();
                }
            });
        } else {
            triggerFilePicker();
        }
    }

    // Add On-Screen Button to GeoFS UI
    function createFlyButton() {
        if (document.getElementById("btn-fly-tejas")) return;

        const btn = document.createElement("button");
        btn.id = "btn-fly-tejas";
        btn.innerHTML = `<span style="font-size:16px;">✈</span> <b>FLY HAL TEJAS</b>`;
        btn.title = "Inject HAL Tejas LCA Navy Mk1 into GeoFS";
        btn.style.cssText = `
            position: fixed;
            top: 12px;
            right: 180px;
            z-index: 999999;
            background: linear-gradient(135deg, #0a192f 0%, #1e3a5f 100%);
            color: #ffffff;
            border: 2px solid #ff9933;
            border-radius: 8px;
            padding: 8px 16px;
            font-family: 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
            letter-spacing: 0.5px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5), 0 0 10px rgba(255,153,51,0.4);
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        `;

        btn.onmouseover = () => {
            btn.style.transform = "scale(1.05)";
            btn.style.boxShadow = "0 6px 20px rgba(255,153,51,0.7)";
            btn.style.borderColor = "#138808";
        };
        btn.onmouseout = () => {
            btn.style.transform = "scale(1)";
            btn.style.boxShadow = "0 4px 15px rgba(0,0,0,0.5), 0 0 10px rgba(255,153,51,0.4)";
            btn.style.borderColor = "#ff9933";
        };

        btn.onclick = loadFromLocalServerOrPicker;
        document.body.appendChild(btn);
    }

    // Enable Drag and Drop on the entire GeoFS screen
    function enableDragAndDrop() {
        window.addEventListener("dragover", (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
        window.addEventListener("drop", (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                const file = e.dataTransfer.files[0];
                if (file.name.toLowerCase().endsWith(".glb")) {
                    console.log("[HAL TEJAS LCA NAVY] Model dropped onto window:", file.name);
                    const blobUrl = URL.createObjectURL(file);
                    injectTejas(blobUrl);
                }
            }
        });
    }

    // Wait for GeoFS UI to mount, then attach button
    const checkInterval = setInterval(() => {
        if (window.geofs && geofs.aircraft && geofs.aircraft.instance) {
            createFlyButton();
            enableDragAndDrop();
            clearInterval(checkInterval);
        }
    }, 1000);

    // Global shortcut
    window.loadTejas = loadFromLocalServerOrPicker;
})();
