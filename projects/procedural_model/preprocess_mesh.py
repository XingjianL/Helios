import trimesh
import numpy as np
import copy
import os
import io
import sys
import argparse
def preprocess_model(input_path, preprocessed_path):
    with open(input_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    material_global_counter = {}  # counts per original material
    materials_used = set()
    mtl_file_name = None
    object_name = None
    for line in lines:
        stripped = line.strip()
        
        # Keep track of the MTL file
        if stripped.startswith("mtllib "):
            mtl_file_name = stripped.split(" ", 1)[1]
            new_lines.append(line)
            continue

        # Object line
        if stripped.startswith('o '):
            object_name = stripped.split(' ', 1)[1]
            new_lines.append(line)
        elif stripped.startswith('usemtl '):
            orig_mat = stripped.split(' ', 1)[1]
            if orig_mat not in material_global_counter:
                material_global_counter[orig_mat] = 0
            else:
                material_global_counter[orig_mat] += 1

            # New unique material name
            new_mat = f"{orig_mat}_{material_global_counter[orig_mat]}"
            new_mat = object_name
            new_lines.append(f"usemtl {new_mat}\n")
            materials_used.add((orig_mat, new_mat))  # store mapping
        else:
            new_lines.append(line)

    # Save preprocessed OBJ
    with open(preprocessed_path, 'w') as f:
        f.writelines(new_lines)

    if mtl_file_name:
        mtl_path = os.path.join(os.path.dirname(input_path), mtl_file_name)
        new_mtl_path = os.path.join(os.path.dirname(preprocessed_path), mtl_file_name)

        with open(mtl_path, 'r') as f:
            mtl_lines = f.readlines()

        new_mtl_lines = []

        # Map original material name to its lines in the MTL
        mat_blocks = {}
        current_mat = None
        materials_used = list(materials_used)
        current_block = []

        for line in mtl_lines:
            stripped = line.strip()
            if stripped.startswith("newmtl "):
                if current_mat:
                    mat_blocks[current_mat] = current_block
                current_mat = stripped.split(" ", 1)[1]
                current_block = [line]  # include the newmtl line
            else:
                current_block.append(line)
        if current_mat:
            mat_blocks[current_mat] = current_block

        # Now, for each duplicated material, write a separate block
        for orig_mat, new_mat in materials_used:
            if orig_mat in mat_blocks:
                # copy original block and change newmtl line
                block = list(mat_blocks[orig_mat])
                block[0] = f"newmtl {new_mat}\n"
                new_mtl_lines.extend(block)
            else:
                print(f"⚠️ Original material {orig_mat} not found in MTL")

        # Save updated MTL
        converted_mtl = new_mtl_lines
        with open(new_mtl_path, 'w') as f:
            f.writelines(new_mtl_lines)

    return new_lines, converted_mtl

def simplify_mesh(new_lines, output_path):
    scene_or_mesh = trimesh.load_scene(io.StringIO(''.join(new_lines)), file_type="obj")
    scene = trimesh.Scene()

    # Ensure Scene wrapper
    if isinstance(scene_or_mesh, trimesh.Trimesh):
        scene_or_mesh = trimesh.Scene(scene_or_mesh)

    merged_geometries = {}

    for name, mesh in scene_or_mesh.geometry.items():
        #print(f"Processing mesh: {name} with {len(mesh.vertices)} vertices")
        merged_mesh = mesh.copy()
        merged_mesh.merge_vertices(digits_vertex = 5)  # deduplicates safely
       #print(mesh.visual.material.name)
        merged_mesh.visual.material = copy.deepcopy(merged_mesh.visual.material)
        merged_mesh.visual.material.name = f"{name}"
        merged_mesh.visual.material.glossiness = hash(name)
        merged_geometries[name] = merged_mesh
        #print(merged_mesh.visual.material.name)
        #print(f"  → Reduced to {len(merged_mesh.vertices)} vertices after merge")
        scene.add_geometry(merged_mesh, geom_name=name)

    # === Rebuild Scene with merged meshes ===
    #merged_scene = trimesh.Scene(merged_geometries)
    # for m in list(merged_geometries.values()):
    #     print(m.visual.material.name)
    # for name, mesh in scene.geometry.items():
    #     print(name)
    #converted_obj = scene.export(file_type="obj")
    converted_obj = scene.export(output_path, file_type="obj", header="")
    #print(converted_obj)
    return converted_obj

def main():
    parser = argparse.ArgumentParser(description="Process OBJ and MTL files.")

    parser.add_argument(
        "--input_obj", type=str, required=True, help="Path to the input OBJ file"
    )
    parser.add_argument(
        "--output_obj", type=str, required=True, help="Path to save the output OBJ file"
    )

    args = parser.parse_args()

    print("Input OBJ:", args.input_obj)
    print("Output OBJ:", args.output_obj)
    new_lines, converted_mtl = preprocess_model(args.input_obj, "temp.obj")
    simplify_mesh(new_lines, args.output_obj)
    # Example: You can add processing here
    # process_obj_mtl(args.input_obj, args.input_mtl, args.output_obj, args.output_mtl)

if __name__ == "__main__":
    main()
# === Settings ===
# input_path = "/home/lxianglabxing/pythonscripts/temp/helios_model_reduce/test2.obj"
# preprocessed_path = "/home/lxianglabxing/pythonscripts/temp/helios_model_reduce/preprocess/temp.obj"
# output_path = "/home/lxianglabxing/pythonscripts/temp/helios_model_reduce/output_merged2.obj"
# converted_mtl = ""
# converted_obj = ""
# === Step 1: Pre-process OBJ to rename duplicate materials per object ===
# --- Step 1: Read OBJ ---


#print(f"✅ Preprocessed OBJ saved as {preprocessed_path}")



    #print(f"✅ Updated MTL saved as {new_mtl_path}")

# === Step 2: Load preprocessed OBJ and merge duplicate vertices per mesh ===
