"""
Embeds authentic IAF camouflage textures into exported glTF/GLB models.
Binds diffuse/baseColor and metallicRoughness textures.
"""

import os
import pygltflib

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "export")
TEXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "textures", "export")

DIFFUSE_FILE = os.path.join(TEXTURES_DIR, "tejas_diffuse.png")
PBR_FILE = os.path.join(TEXTURES_DIR, "tejas_metallic_roughness.png")

def embed_textures_in_glb(glb_filename):
    glb_path = os.path.join(EXPORT_DIR, glb_filename)
    if not os.path.exists(glb_path):
        return
    
    print(f"Embedding PBR textures into {glb_filename}...")
    gltf = pygltflib.GLTF2().load(glb_path)
    
    # Read diffuse bytes
    with open(DIFFUSE_FILE, "rb") as f:
        diffuse_bytes = f.read()
        
    with open(PBR_FILE, "rb") as f:
        pbr_bytes = f.read()
        
    # Create or update images
    gltf.images = [
        pygltflib.Image(uri=None, mimeType="image/png"),
        pygltflib.Image(uri=None, mimeType="image/png")
    ]
    
    # Store images in binary buffer
    # Calculate byte offsets
    buffer_bytes = gltf.binary_blob() if gltf.binary_blob() else b""
    # Pad to 4 bytes
    pad = (4 - (len(buffer_bytes) % 4)) % 4
    buffer_bytes += b"\x00" * pad
    
    offset_diffuse = len(buffer_bytes)
    len_diffuse = len(diffuse_bytes)
    buffer_bytes += diffuse_bytes
    
    pad2 = (4 - (len(buffer_bytes) % 4)) % 4
    buffer_bytes += b"\x00" * pad2
    offset_pbr = len(buffer_bytes)
    len_pbr = len(pbr_bytes)
    buffer_bytes += pbr_bytes
    
    # Buffer views
    bv_diffuse_idx = len(gltf.bufferViews)
    gltf.bufferViews.append(pygltflib.BufferView(
        buffer=0, byteOffset=offset_diffuse, byteLength=len_diffuse
    ))
    gltf.images[0].bufferView = bv_diffuse_idx
    
    bv_pbr_idx = len(gltf.bufferViews)
    gltf.bufferViews.append(pygltflib.BufferView(
        buffer=0, byteOffset=offset_pbr, byteLength=len_pbr
    ))
    gltf.images[1].bufferView = bv_pbr_idx
    
    # Update buffer 0
    gltf.set_binary_blob(buffer_bytes)
    gltf.buffers[0].byteLength = len(buffer_bytes)
    
    # Sampler
    sampler_idx = 0
    if not gltf.samplers:
        gltf.samplers.append(pygltflib.Sampler(
            magFilter=pygltflib.LINEAR,
            minFilter=pygltflib.LINEAR_MIPMAP_LINEAR,
            wrapS=pygltflib.REPEAT,
            wrapT=pygltflib.REPEAT
        ))
        
    # Textures
    gltf.textures = [
        pygltflib.Texture(sampler=0, source=0),
        pygltflib.Texture(sampler=0, source=1)
    ]
    
    # Material
    gltf.materials = [
        pygltflib.Material(
            name="HAL_Tejas_IAF_Material",
            pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                baseColorTexture=pygltflib.TextureInfo(index=0),
                metallicRoughnessTexture=pygltflib.TextureInfo(index=1),
                roughnessFactor=1.0,
                metallicFactor=1.0
            ),
            doubleSided=True
        )
    ]
    
    # Apply material to all primitives
    for mesh in gltf.meshes:
        for prim in mesh.primitives:
            prim.material = 0
            
    gltf.save(glb_path)
    new_size = os.path.getsize(glb_path) / 1024
    print(f"  [x] Successfully saved {glb_filename} with IAF PBR textures ({new_size:6.1f} KB)")

if __name__ == "__main__":
    for name in ["body.glb", "tejas_mk1.glb"]:
        embed_textures_in_glb(name)
