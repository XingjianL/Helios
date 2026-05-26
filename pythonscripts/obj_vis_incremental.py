import open3d as o3d
import numpy as np
import time
import random

vertices = []
vertex_colors = []

# Map to store material names and their assigned RGB colors
material_palette = {}

def get_color_for_material(mtl_name):
    """Assigns a random consistent color to a material name."""
    if mtl_name not in material_palette:
        # Generate a random RGB color (0.0 to 1.0)
        material_palette[mtl_name] = [random.random(), random.random(), random.random()]
    return material_palette[mtl_name]

# Create an Open3D visualizer
vis = o3d.visualization.Visualizer()
vis.create_window(window_name="Material-Based Point Cloud", width=1280, height=720)

pcd = o3d.geometry.PointCloud()
vis.add_geometry(pcd)

current_color = [0.5, 0.5, 0.5]  # Default gray

with open("test_merge.obj", "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # if "leaf" in line:
        #     break
        parts = line.split()
        
        # Track material changes
        if line.startswith("usemtl"):
            mtl_name = parts[1]
            current_color = get_color_for_material(mtl_name)
            
        # Parse vertices
        elif line.startswith("v "):
            vertices.append(list(map(float, parts[1:4])))
            vertex_colors.append(current_color)

            # Update visualization every 100 vertices
            if len(vertices) % 100 == 0:
                pcd.points = o3d.utility.Vector3dVector(np.array(vertices))
                pcd.colors = o3d.utility.Vector3dVector(np.array(vertex_colors))
                
                vis.update_geometry(pcd)
                if len(vertices) == 100:
                    vis.reset_view_point(True)
                
                vis.poll_events()
                vis.update_renderer()
                time.sleep(0.001)

# Final update
pcd.points = o3d.utility.Vector3dVector(np.array(vertices))
pcd.colors = o3d.utility.Vector3dVector(np.array(vertex_colors))
vis.update_geometry(pcd)
vis.reset_view_point(True)

print(f"Finished loading {len(vertices)} points with {len(material_palette)} unique materials.")
vis.run()
vis.destroy_window()