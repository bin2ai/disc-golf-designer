#!/usr/bin/env python3
"""
Debug volume calculation step by step
"""

import numpy as np
import trimesh

def debug_simple_disc():
    """Create a very simple disc and verify each step"""
    print("=== DEBUGGING SIMPLE DISC STEP BY STEP ===")
    
    # Super simple disc profile - just a flat disc
    # Radius = 110mm, height = 15mm (should give ~570 cm³ volume)
    radius = 110.0  # mm
    height = 15.0   # mm
    
    print(f"Target: Simple flat disc")
    print(f"- Radius: {radius}mm")
    print(f"- Height: {height}mm")
    print(f"- Expected volume: π × r² × h = {np.pi * radius**2 * height / 1000000:.1f} cm³")
    print(f"- Expected weight (PETG): {np.pi * radius**2 * height / 1000000 * 1.28:.0f}g")
    
    # Create simple profile - just top and bottom circles
    profile_points = [
        (radius, 0),      # top edge
        (radius, -height) # bottom edge
    ]
    
    x_coords = np.array([p[0] for p in profile_points])
    y_coords = np.array([p[1] for p in profile_points])
    
    print(f"\nProfile points:")
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        print(f"  Point {i}: x={x}mm, y={y}mm")
    
    # Create revolution
    n_theta = 8  # Simple for debugging
    theta = np.linspace(0, 2*np.pi, n_theta, endpoint=False)
    
    vertices = []
    
    # Generate vertices
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        r = abs(x)
        for j, angle in enumerate(theta):
            vertex_x = r * np.cos(angle)
            vertex_y = r * np.sin(angle)
            vertex_z = y
            vertices.append([vertex_x, vertex_y, vertex_z])
            print(f"  Vertex {len(vertices)-1}: ({vertex_x:.1f}, {vertex_y:.1f}, {vertex_z:.1f})")
    
    # Add center points
    top_center = [0, 0, 0]
    bottom_center = [0, 0, -height]
    vertices.extend([top_center, bottom_center])
    
    vertices = np.array(vertices)
    n_profile = len(x_coords)
    
    print(f"\nGenerated {len(vertices)} vertices")
    print(f"Profile points: {n_profile}")
    print(f"Angular divisions: {n_theta}")
    
    faces = []
    
    # Side faces (connecting top and bottom circles)
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        
        # Top circle vertex indices: 0 to n_theta-1
        # Bottom circle vertex indices: n_theta to 2*n_theta-1
        v1 = j                    # top current
        v2 = j_next               # top next
        v3 = n_theta + j          # bottom current
        v4 = n_theta + j_next     # bottom next
        
        # Two triangles
        faces.append([v1, v3, v2])
        faces.append([v2, v3, v4])
    
    # Top cap (connect to center)
    top_center_idx = len(vertices) - 2
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        faces.append([top_center_idx, j_next, j])
    
    # Bottom cap (connect to center)
    bottom_center_idx = len(vertices) - 1
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        faces.append([bottom_center_idx, n_theta + j, n_theta + j_next])
    
    print(f"Generated {len(faces)} faces")
    
    # Create mesh
    try:
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        print(f"\nMesh properties:")
        print(f"- Is watertight: {mesh.is_watertight}")
        print(f"- Volume: {mesh.volume:.0f} mm³")
        
        if mesh.volume < 0:
            print("- Flipping negative volume...")
            mesh.invert()
        
        volume_mm3 = abs(mesh.volume)
        volume_cm3 = volume_mm3 / 1000000
        weight = volume_cm3 * 1.28
        
        print(f"- Final volume: {volume_cm3:.1f} cm³")
        print(f"- Weight (PETG): {weight:.0f}g")
        
        # Check if reasonable
        expected_volume = np.pi * radius**2 * height / 1000000
        error_percent = abs(volume_cm3 - expected_volume) / expected_volume * 100
        
        print(f"\nValidation:")
        print(f"- Expected: {expected_volume:.1f} cm³")
        print(f"- Actual: {volume_cm3:.1f} cm³")
        print(f"- Error: {error_percent:.1f}%")
        
        if error_percent < 20 and 50 <= weight <= 250:
            print("✅ SUCCESS: Volume calculation is working!")
        else:
            print("❌ FAILED: Volume calculation still wrong")
            
        return mesh, volume_cm3
        
    except Exception as e:
        print(f"Error: {e}")
        return None, 0

def debug_disc_profile_from_app():
    """Test with the exact same profile structure as the app"""
    print("\n=== DEBUGGING WITH APP PROFILE STRUCTURE ===")
    
    # Use the same default points as in the DiscProfile class
    # These are the actual points from the application
    points = {
        1: {'x': 0, 'y': 0, 'name': 'Center Top'},      # Flight plate center
        2: {'x': -90, 'y': -1, 'name': 'Shoulder'},      # Shoulder
        3: {'x': -110, 'y': -2, 'name': 'Nose'},         # Rim start
        4: {'x': -100, 'y': -8, 'name': 'Rim Top'},      # Rim top
        5: {'x': -85, 'y': -15, 'name': 'Rim Bottom'},   # Rim bottom
        6: {'x': -85, 'y': -12, 'name': 'Rim End'},      # Rim end
        7: {'x': 0, 'y': -2, 'name': 'Center Bottom'}    # Flight plate bottom
    }
    
    print("Using actual app profile points:")
    for point_id, point in points.items():
        print(f"  P{point_id}: ({point['x']}, {point['y']}) - {point['name']}")
    
    # Extract coordinates in order for profile
    profile_order = [1, 2, 3, 4, 5, 6, 7]  # Top to bottom
    x_coords = []
    y_coords = []
    
    for point_id in profile_order:
        x_coords.append(abs(points[point_id]['x']))  # Take absolute value for radius
        y_coords.append(points[point_id]['y'])
    
    x_coords = np.array(x_coords)
    y_coords = np.array(y_coords)
    
    print(f"\nExtracted profile:")
    print(f"X (radii): {x_coords}")
    print(f"Y (heights): {y_coords}")
    
    # Calculate expected volume roughly
    avg_radius = np.mean(x_coords)
    height = abs(min(y_coords) - max(y_coords))
    rough_volume = np.pi * avg_radius**2 * height * 0.7  # 70% fill factor
    expected_cm3 = rough_volume / 1000000
    expected_weight = expected_cm3 * 1.28
    
    print(f"\nRough estimates:")
    print(f"- Average radius: {avg_radius:.0f}mm")
    print(f"- Height: {height:.0f}mm")
    print(f"- Rough volume: {expected_cm3:.0f} cm³")
    print(f"- Expected weight: {expected_weight:.0f}g")
    
    # Now create the mesh using the same method as the app
    n_theta = 24
    theta = np.linspace(0, 2*np.pi, n_theta, endpoint=False)
    
    vertices = []
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        r = abs(x)
        for j, angle in enumerate(theta):
            vertex_x = r * np.cos(angle)
            vertex_y = r * np.sin(angle)
            vertex_z = y
            vertices.append([vertex_x, vertex_y, vertex_z])
    
    vertices = np.array(vertices)
    n_profile = len(x_coords)
    
    # Generate faces
    faces = []
    for i in range(n_profile - 1):
        for j in range(n_theta):
            j_next = (j + 1) % n_theta
            
            v1 = i * n_theta + j
            v2 = i * n_theta + j_next
            v3 = (i + 1) * n_theta + j
            v4 = (i + 1) * n_theta + j_next
            
            faces.append([v1, v3, v2])
            faces.append([v2, v3, v4])
    
    # Add caps
    top_center = [0, 0, max(y_coords)]
    bottom_center = [0, 0, min(y_coords)]
    vertices = np.vstack([vertices, [top_center, bottom_center]])
    
    top_center_idx = len(vertices) - 2
    bottom_center_idx = len(vertices) - 1
    
    # Top cap
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        faces.append([top_center_idx, j_next, j])
    
    # Bottom cap
    bottom_start = (n_profile - 1) * n_theta
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        faces.append([bottom_center_idx, bottom_start + j, bottom_start + j_next])
    
    try:
        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        if mesh.volume < 0:
            mesh.invert()
        
        volume_mm3 = abs(mesh.volume)
        volume_cm3 = volume_mm3 / 1000000
        weight = volume_cm3 * 1.28
        
        print(f"\nActual app mesh results:")
        print(f"- Volume: {volume_cm3:.1f} cm³")
        print(f"- Weight: {weight:.0f}g")
        
        if 50 <= weight <= 250:
            print("✅ SUCCESS: App profile gives reasonable weight!")
        else:
            print("❌ FAILED: App profile still wrong")
            
        return mesh, volume_cm3
        
    except Exception as e:
        print(f"Error: {e}")
        return None, 0

if __name__ == "__main__":
    # Test 1: Simple flat disc
    simple_mesh, simple_vol = debug_simple_disc()
    
    # Test 2: Actual app profile
    app_mesh, app_vol = debug_disc_profile_from_app()
    
    print(f"\n" + "="*60)
    print("SUMMARY:")
    if simple_vol > 0:
        print(f"Simple disc: {simple_vol:.1f} cm³ = {simple_vol * 1.28:.0f}g PETG")
    if app_vol > 0:
        print(f"App profile: {app_vol:.1f} cm³ = {app_vol * 1.28:.0f}g PETG")
        
    if app_vol * 1.28 >= 50:
        print("✅ READY FOR APP INTEGRATION")
    else:
        print("❌ NEEDS MORE DEBUGGING")