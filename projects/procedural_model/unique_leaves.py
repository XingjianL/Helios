import trimesh
import numpy as np
import copy
import os
import io
import sys
import argparse
import re
def parse_mtl(text):
    # Split by newmtl while keeping names
    print(text)
    blocks = re.split(r'(?=newmtl\s+)', text)

    materials = []

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()
        name = lines[0].split()[1]

        materials.append({
            "name": name,
            "content": block
        })

    return materials
def build_mtl(materials):
    return "\n\n".join(mat["content"] for mat in materials)
def duplicate_material(materials_dict, original_name, new_name):
    if original_name not in materials_dict:
        return None

    content = materials_dict[original_name]

    # Replace ONLY the first line (newmtl ...)
    lines = content.splitlines()
    lines[0] = f"newmtl {new_name}"

    return {
        "name": new_name,
        "content": "\n".join(lines)
    }
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

def simplify_mesh(new_lines, output_path, converted_mtl):
    scene_or_mesh = trimesh.load_scene(io.StringIO(''.join(new_lines)), file_type="obj")
    scene = trimesh.Scene()
    # Ensure Scene wrapper
    if isinstance(scene_or_mesh, trimesh.Trimesh):
        scene_or_mesh = trimesh.Scene(scene_or_mesh)
    materials = parse_mtl(''.join(converted_mtl))
    materials_dict = {m["name"]: m["content"] for m in materials}
    output_materials = []#list(materials)
    for name, mesh in scene_or_mesh.geometry.items():
        merged_mesh = mesh.copy()
        merged_mesh.merge_vertices(digits_vertex = 4)
        merged_mesh.visual.material = copy.deepcopy(merged_mesh.visual.material)
        merged_mesh.visual.material.name = f"{name}"
        merged_mesh.visual.material.glossiness = hash(name)
        #if "leaf" not in name:
        merged_mesh.remove_degenerate_faces()
        merged_mesh.remove_duplicate_faces()
        merged_mesh.remove_unreferenced_vertices()
        components : list[trimesh.Trimesh] = merged_mesh.split(only_watertight = False)
        print(f"name: {name}, faces: {merged_mesh.faces.shape[0]}, components: {len(components)}")
        
        new_components = []
        expected_faces = np.argmax(np.bincount([comp.faces.shape[0] for comp in components]))
        
        uv_leaves_ind = 0

        #mesh_center = merged_mesh.centroid
        for i, comp in enumerate(components):
            print(f"name: {name}, Component {i}: {comp.faces.shape[0]} faces")
            if comp.visual.uv is None:
                new_components.append(comp)
                continue
            if any(s in name for s in ["sepal", "petal", "petiolule"]): # elements that do not need further sections for instances
                new_components.append(comp)
                continue
            uv_leaves_count_side = 16
            max_per_mesh = uv_leaves_count_side**2
            if any(s in name for s in ["petiole", "fruit", "shoot"]): # elements that get further instance at different frequencies to leaves
                uv_leaves_count_side = 8
                max_per_mesh = uv_leaves_count_side**2
            #if "leaf" not in name:
            # if comp.faces.shape[0] < 2:
            #     new_components.append(comp)
            #     continue
            # UV coordinates are stored as a (N, 2) NumPy array (U, V)
            # Multiply the entire array by 0.25 (or / 4.0) in place
            comp.visual.uv *= 1.0 / uv_leaves_count_side
            if comp.faces.shape[0] == expected_faces:
                u_ind = int((uv_leaves_ind % uv_leaves_count_side**2) / uv_leaves_count_side)
                v_ind = int((uv_leaves_ind % uv_leaves_count_side**2) % uv_leaves_count_side)
                print(f"u_ind: {u_ind}, v_ind: {v_ind}")
                comp.visual.uv[:, 0] += u_ind / uv_leaves_count_side
                comp.visual.uv[:, 1] += v_ind / uv_leaves_count_side
                
                uv_leaves_ind += 1
            new_components.append(comp)
        
        for chunk_idx, i in enumerate(range(0, len(new_components), max_per_mesh)):
            chunk = new_components[i:i+max_per_mesh]
            merged_chunk = trimesh.util.concatenate(chunk)
            chunk_name = f"{name}_{chunk_idx}"
            output_materials.append(duplicate_material(materials_dict, name, chunk_name))
            merged_chunk.visual.material = copy.deepcopy(merged_mesh.visual.material)
            merged_chunk.visual.material.name = chunk_name
            merged_chunk.visual.material.glossiness = hash(chunk_name)
            scene.add_geometry(merged_chunk, geom_name=f"{name}_{chunk_idx}")
    with open("test.mtl", "w") as f:
        f.write(build_mtl(output_materials))
        #merged_mesh.visual.material = copy.deepcopy(merged_mesh.visual.material)
        #merged_mesh = trimesh.util.concatenate(new_components)
        
        # using glossiness to define a unique material ID (otherwise mat will be combined)
        #scene.add_geometry(merged_mesh, geom_name=name)

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
    simplify_mesh(new_lines, args.output_obj, converted_mtl)
    # Example: You can add processing here
    # process_obj_mtl(args.input_obj, args.input_mtl, args.output_obj, args.output_mtl)

if __name__ == "__main__":
    main()
