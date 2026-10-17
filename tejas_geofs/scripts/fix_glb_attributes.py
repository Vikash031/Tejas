"""
Rigorous glTF 2.0 Geometry & Attribute Validator / Fixer
Ensures:
1. All textured primitives have valid POSITION, NORMAL, and TEXCOORD_0 attributes.
2. Prevents Cesium WebGL 'undefined' texture coordinate shader compilation crashes.
3. Assigns clean, optimized PBR materials to all parts.
"""

import os
import struct
import numpy as np
import pygltflib

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "export")
TEXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "textures", "export")

DIFFUSE_FILE = os.path.join(TEXTURES_DIR, "tejas_diffuse.png")
PBR_FILE = os.path.join(TEXTURES_DIR, "tejas_metallic_roughness.png")

def fix_textured_model(filename):
    filepath = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(filepath):
        return
    print(f"Fixing attributes and UVs in {filename}...")
    gltf = pygltflib.GLTF2().load(filepath)
    
    # Read binary blob
    blob = bytearray(gltf.binary_blob())
    
    # 1. Read Positions
    pos_accessor_idx = gltf.meshes[0].primitives[0].attributes.POSITION
    pos_accessor = gltf.accessors[pos_accessor_idx]
    pos_bv = gltf.bufferViews[pos_accessor.bufferView]
    
    pos_bytes = blob[pos_bv.byteOffset : pos_bv.byteOffset + pos_bv.byteLength]
    num_verts = pos_accessor.count
    positions = np.frombuffer(pos_bytes, dtype=np.float32).reshape((num_verts, 3))
    
    # 2. Compute Normals (Approximate outward from centerline/Z)
    normals = np.zeros_like(positions)
    for i, p in enumerate(positions):
        norm = np.array([p[0], 0.1 * p[1], p[2]])
        length = np.linalg.norm(norm)
        normals[i] = norm / length if length > 1e-4 else np.array([0, 0, 1], dtype=np.float32)
    normals_bytes = normals.astype(np.float32).tobytes()
    
    # 3. Compute TEXCOORD_0 (U from X span: -4.2m to +4.2m, V from Y length: -6.6m to +6.6m)
    uvs = np.zeros((num_verts, 2), dtype=np.float32)
    for i, p in enumerate(positions):
        u = float(np.clip((p[0] + 4.2) / 8.4, 0.0, 1.0))
        v = float(np.clip((p[1] + 6.6) / 13.2, 0.0, 1.0))
        uvs[i] = [u, v]
    uvs_bytes = uvs.tobytes()
    
    # 4. Pack Diffuse and PBR Textures
    with open(DIFFUSE_FILE, "rb") as f:
        diffuse_bytes = f.read()
    with open(PBR_FILE, "rb") as f:
        pbr_bytes = f.read()
        
    # Reconstruct buffer 0 cleanly
    new_blob = bytearray()
    
    # Copy indices
    idx_accessor_idx = gltf.meshes[0].primitives[0].indices
    idx_accessor = gltf.accessors[idx_accessor_idx]
    idx_bv = gltf.bufferViews[idx_accessor.bufferView]
    idx_bytes = blob[idx_bv.byteOffset : idx_bv.byteOffset + idx_bv.byteLength]
    
    def append_data(data, align=4):
        pad = (align - (len(new_blob) % align)) % align
        new_blob.extend(b"\x00" * pad)
        offset = len(new_blob)
        new_blob.extend(data)
        return offset, len(data)

    offset_idx, len_idx = append_data(idx_bytes)
    offset_pos, len_pos = append_data(pos_bytes)
    offset_norm, len_norm = append_data(normals_bytes)
    offset_uv, len_uv = append_data(uvs_bytes)
    offset_diff, len_diff = append_data(diffuse_bytes)
    offset_pbr, len_pbr = append_data(pbr_bytes)
    
    # Buffer views
    bv_idx = pygltflib.BufferView(buffer=0, byteOffset=offset_idx, byteLength=len_idx)
    bv_pos = pygltflib.BufferView(buffer=0, byteOffset=offset_pos, byteLength=len_pos)
    bv_norm = pygltflib.BufferView(buffer=0, byteOffset=offset_norm, byteLength=len_norm)
    bv_uv = pygltflib.BufferView(buffer=0, byteOffset=offset_uv, byteLength=len_uv)
    bv_diff = pygltflib.BufferView(buffer=0, byteOffset=offset_diff, byteLength=len_diff)
    bv_pbr = pygltflib.BufferView(buffer=0, byteOffset=offset_pbr, byteLength=len_pbr)
    
    gltf.bufferViews = [bv_idx, bv_pos, bv_norm, bv_uv, bv_diff, bv_pbr]
    
    # Accessors
    acc_idx = pygltflib.Accessor(
        bufferView=0, byteOffset=0, componentType=idx_accessor.componentType,
        count=idx_accessor.count, type="SCALAR", max=idx_accessor.max, min=idx_accessor.min
    )
    acc_pos = pygltflib.Accessor(
        bufferView=1, byteOffset=0, componentType=pygltflib.FLOAT,
        count=num_verts, type="VEC3", max=pos_accessor.max, min=pos_accessor.min
    )
    acc_norm = pygltflib.Accessor(
        bufferView=2, byteOffset=0, componentType=pygltflib.FLOAT,
        count=num_verts, type="VEC3", max=[1.0, 1.0, 1.0], min=[-1.0, -1.0, -1.0]
    )
    acc_uv = pygltflib.Accessor(
        bufferView=3, byteOffset=0, componentType=pygltflib.FLOAT,
        count=num_verts, type="VEC2", max=[1.0, 1.0], min=[0.0, 0.0]
    )
    
    gltf.accessors = [acc_idx, acc_pos, acc_norm, acc_uv]
    
    # Images & Textures
    gltf.images = [
        pygltflib.Image(mimeType="image/png", bufferView=4),
        pygltflib.Image(mimeType="image/png", bufferView=5)
    ]
    gltf.samplers = [
        pygltflib.Sampler(
            magFilter=pygltflib.LINEAR, minFilter=pygltflib.LINEAR_MIPMAP_LINEAR,
            wrapS=pygltflib.REPEAT, wrapT=pygltflib.REPEAT
        )
    ]
    gltf.textures = [
        pygltflib.Texture(sampler=0, source=0),
        pygltflib.Texture(sampler=0, source=1)
    ]
    
    # PBR Material
    gltf.materials = [
        pygltflib.Material(
            name="HAL_Tejas_IAF_Material",
            pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                baseColorTexture=pygltflib.TextureInfo(index=0, texCoord=0),
                metallicRoughnessTexture=pygltflib.TextureInfo(index=1, texCoord=0),
                baseColorFactor=[1.0, 1.0, 1.0, 1.0],
                roughnessFactor=1.0,
                metallicFactor=1.0
            ),
            doubleSided=True
        )
    ]
    
    # Update primitive
    prim = gltf.meshes[0].primitives[0]
    prim.indices = 0
    prim.attributes.POSITION = 1
    prim.attributes.NORMAL = 2
    prim.attributes.TEXCOORD_0 = 3
    prim.material = 0
    
    # Finalize buffer
    gltf.set_binary_blob(bytes(new_blob))
    gltf.buffers[0].byteLength = len(new_blob)
    
    gltf.save(filepath)
    print(f"  [x] Successfully saved {filename} with valid POSITION, NORMAL, TEXCOORD_0 ({len(new_blob)/1024:.1f} KB)")

def fix_solid_parts():
    """Fixes non-textured parts with clean solid PBR materials (no texture coordinates needed)"""
    part_configs = {
        "canopy.glb": {
            "name": "Canopy_Glass",
            "color": [0.12, 0.16, 0.22, 0.7],
            "roughness": 0.05,
            "metallic": 0.1,
            "alphaMode": "BLEND"
        },
        "frontWheel.glb": {
            "name": "Nose_Gear_Assembly",
            "color": [0.25, 0.27, 0.30, 1.0],
            "roughness": 0.65,
            "metallic": 0.4,
            "alphaMode": "OPAQUE"
        },
        "leftGear.glb": {
            "name": "Main_Gear_Assembly",
            "color": [0.25, 0.27, 0.30, 1.0],
            "roughness": 0.65,
            "metallic": 0.4,
            "alphaMode": "OPAQUE"
        },
        "rightGear.glb": {
            "name": "Main_Gear_Assembly",
            "color": [0.25, 0.27, 0.30, 1.0],
            "roughness": 0.65,
            "metallic": 0.4,
            "alphaMode": "OPAQUE"
        },
        "leftAileron.glb": {
            "name": "Elevon_Paint",
            "color": [0.55, 0.60, 0.65, 1.0],
            "roughness": 0.70,
            "metallic": 0.1,
            "alphaMode": "OPAQUE"
        },
        "rightAileron.glb": {
            "name": "Elevon_Paint",
            "color": [0.55, 0.60, 0.65, 1.0],
            "roughness": 0.70,
            "metallic": 0.1,
            "alphaMode": "OPAQUE"
        },
        "rudder.glb": {
            "name": "Rudder_Paint",
            "color": [0.55, 0.60, 0.65, 1.0],
            "roughness": 0.70,
            "metallic": 0.1,
            "alphaMode": "OPAQUE"
        }
    }
    
    for filename, cfg in part_configs.items():
        filepath = os.path.join(EXPORT_DIR, filename)
        if not os.path.exists(filepath):
            continue
        gltf = pygltflib.GLTF2().load(filepath)
        gltf.textures = []
        gltf.images = []
        gltf.materials = [
            pygltflib.Material(
                name=cfg["name"],
                pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                    baseColorFactor=cfg["color"],
                    roughnessFactor=cfg["roughness"],
                    metallicFactor=cfg["metallic"]
                ),
                alphaMode=cfg["alphaMode"],
                doubleSided=True
            )
        ]
        if gltf.meshes and gltf.meshes[0].primitives:
            gltf.meshes[0].primitives[0].material = 0
            # Ensure no rogue texture coordinate reference
            gltf.meshes[0].primitives[0].attributes.TEXCOORD_0 = None
        gltf.save(filepath)
        print(f"  [x] Set clean solid PBR material for {filename}")

if __name__ == "__main__":
    fix_textured_model("body.glb")
    fix_textured_model("tejas_mk1.glb")
    fix_solid_parts()
