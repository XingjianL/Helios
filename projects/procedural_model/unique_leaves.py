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
        merged_mesh = mesh.copy()
        merged_mesh.merge_vertices(digits_vertex = 4)
        print(f"name: {name}, faces: {merged_mesh.faces.shape[0]}")
        components = merged_mesh.split(only_watertight = False)
        for i, comp in enumerate(components):
            print(f"name: {name}, Component {i}: {comp.faces.shape[0]} faces")
        merged_mesh.visual.material = copy.deepcopy(merged_mesh.visual.material)
        merged_mesh.visual.material.name = f"{name}"
        merged_mesh.visual.material.glossiness = hash(name) # using glossiness to define a unique material ID (otherwise mat will be combined)
        merged_geometries[name] = merged_mesh
        scene.add_geometry(merged_mesh, geom_name=name)

    converted_obj = scene.export(output_path, file_type="obj", header="")
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
