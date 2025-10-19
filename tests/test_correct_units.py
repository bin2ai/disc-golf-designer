#!/usr/bin/env python3
"""
Test with CORRECT unit expectations for disc golf disc
"""

import numpy as np
import trimesh

def test_realistic_disc():
    """Test with proper disc golf disc dimensions and expectations"""
    print("=== TESTING REALISTIC DISC GOLF DISC ===")
    
    # Standard disc golf disc dimensions
    radius = 110.0  # mm (edge to edge diameter ~220mm)
    height = 18.0   # mm (typical disc height)
    
    print(f"Disc specifications:")
    print(f"- Radius: {radius}mm = {radius/10:.1f}cm")
    print(f"- Height: {height}mm = {height/10:.1f}cm")
    
    # Calculate CORRECT expected volume
    radius_cm = radius / 10
    height_cm = height / 10
    volume_cm3 = np.pi * radius_cm**2 * height_cm
    
    print(f"- CORRECT expected volume: π × {radius_cm}² × {height_cm} = {volume_cm3:.0f} cm³")
    print(f"- CORRECT expected weight (PETG): {volume_cm3 * 1.28:.0f}g")
    print(f"- But disc is hollow/curved, so expect ~70% = {volume_cm3 * 0.7 * 1.28:.0f}g")
    
    # Create mesh
    profile_points = [
        (radius, 0),      # top edge
        (radius, -height) # bottom edge
    ]
    
    x_coords = np.array([p[0] for p in profile_points])
    y_coords = np.array([p[1] for p in profile_points])
    
    # Create revolution
    n_theta = 16
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
    
    # Add center points
    top_center = [0, 0, 0]
    bottom_center = [0, 0, -height]
    vertices.extend([top_center, bottom_center])
    
    vertices = np.array(vertices)
    n_profile = len(x_coords)
    
    faces = []
    
    # Side faces
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        
        v1 = j                    # top current
        v2 = j_next               # top next
        v3 = n_theta + j          # bottom current
        v4 = n_theta + j_next     # bottom next
        
        faces.append([v1, v3, v2])
        faces.append([v2, v3, v4])
    
    # Top cap
    top_center_idx = len(vertices) - 2
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        faces.append([top_center_idx, j_next, j])
    
    # Bottom cap
    bottom_center_idx = len(vertices) - 1
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        faces.append([bottom_center_idx, n_theta + j, n_theta + j_next])
    
    # Create mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    if mesh.volume < 0:
        mesh.invert()
    
    volume_mm3 = abs(mesh.volume)
    volume_cm3 = volume_mm3 / 1000000  # Convert mm³ to cm³
    weight = volume_cm3 * 1.28
    
    print(f"\nMesh results:")
    print(f"- Volume: {volume_mm3:.0f} mm³ = {volume_cm3:.0f} cm³")
    print(f"- Weight (PETG): {weight:.0f}g")
    
    # Check if this is reasonable
    if 400 <= weight <= 800:  # Full cylinder would be ~680g
        print("✅ SUCCESS: This is the correct range for a solid cylinder!")
        print("   (Real discs are hollow/curved so expect ~100-200g)")
    else:
        print("❌ FAILED: Still not in expected range")
    
    return volume_cm3, weight

def test_hollow_disc():
    """Test with a more realistic hollow disc profile"""
    print("\n=== TESTING HOLLOW DISC PROFILE ===")
    
    # Create a realistic disc profile that's curved/hollow
    # Points for a typical disc cross-section
    points = [
        (0, 0),        # Center top
        (60, -0.5),    # Inner flight plate
        (90, -1),      # Shoulder
        (110, -2),     # Rim start  
        (105, -8),     # Rim curve
        (90, -16),     # Rim bottom
        (80, -18),     # Rim inner
        (20, -18),     # Inner bottom
        (0, -4)        # Center bottom
    ]
    
    x_coords = np.array([abs(p[0]) for p in points])
    y_coords = np.array([p[1] for p in points])
    
    print("Hollow disc profile:")
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        print(f"  Point {i}: r={x}mm, z={y}mm")
    
    # Create revolution
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
    
    # Generate faces connecting profile points
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
    
    # Close the profile (connect last to first)
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        
        v1 = (n_profile - 1) * n_theta + j
        v2 = (n_profile - 1) * n_theta + j_next
        v3 = j  # First ring
        v4 = j_next
        
        faces.append([v1, v3, v2])
        faces.append([v2, v3, v4])
    
    # Create mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    print(f"Mesh properties:")
    print(f"- Is watertight: {mesh.is_watertight}")
    print(f"- Volume: {mesh.volume:.0f} mm³")
    
    if mesh.volume < 0:
        print("- Flipping negative volume...")
        mesh.invert()
    
    volume_mm3 = abs(mesh.volume)
    volume_cm3 = volume_mm3 / 1000000
    weight = volume_cm3 * 1.28
    
    print(f"- Final volume: {volume_cm3:.0f} cm³")
    print(f"- Weight (PETG): {weight:.0f}g")
    
    if 80 <= weight <= 200:
        print("✅ SUCCESS: This looks like a realistic disc weight!")
    else:
        print("❌ Still not quite right")
    
    return volume_cm3, weight

if __name__ == "__main__":
    # Test 1: Solid cylinder (should be ~680g)
    solid_vol, solid_weight = test_realistic_disc()
    
    # Test 2: Hollow disc (should be ~100-150g)
    hollow_vol, hollow_weight = test_hollow_disc()
    
    print(f"\n" + "="*50)
    print("FINAL RESULTS:")
    print(f"Solid cylinder: {solid_vol:.0f} cm³ = {solid_weight:.0f}g")
    print(f"Hollow disc: {hollow_vol:.0f} cm³ = {hollow_weight:.0f}g")
    
    if 80 <= hollow_weight <= 200:
        print("✅ VOLUME CALCULATION IS WORKING CORRECTLY!")
        print("   The issue was wrong expectations, not the code.")
    else:
        print("❌ Still need to debug further")