#!/usr/bin/env python3
"""
Test basic cylinder to verify trimesh is working correctly
"""

import numpy as np
import trimesh

def test_basic_cylinder():
    """Test basic cylinder volume calculation"""
    print("=== TESTING BASIC CYLINDER ===")
    
    # Create a simple cylinder using trimesh
    radius = 110.0  # mm
    height = 20.0   # mm
    
    # Manual calculation first
    manual_volume_mm3 = np.pi * radius**2 * height
    manual_volume_cm3 = manual_volume_mm3 / 1000000
    manual_weight = manual_volume_cm3 * 1.28
    
    print(f"Manual calculation:")
    print(f"  - π × {radius}² × {height} = {manual_volume_mm3:.0f} mm³")
    print(f"  - {manual_volume_mm3:.0f} ÷ 1,000,000 = {manual_volume_cm3:.1f} cm³")
    print(f"  - {manual_volume_cm3:.1f} × 1.28 = {manual_weight:.0f}g")
    
    # Create cylinder with trimesh
    cylinder = trimesh.creation.cylinder(radius=radius, height=height)
    
    # Get volume
    trimesh_volume_mm3 = cylinder.volume
    trimesh_volume_cm3 = trimesh_volume_mm3 / 1000000
    trimesh_weight = trimesh_volume_cm3 * 1.28
    
    print(f"\nTrimesh cylinder:")
    print(f"  - Volume: {trimesh_volume_mm3:.0f} mm³")
    print(f"  - Volume: {trimesh_volume_mm3:.0f} ÷ 1,000,000 = {trimesh_volume_cm3:.1f} cm³")
    print(f"  - Weight: {trimesh_volume_cm3:.1f} × 1.28 = {trimesh_weight:.0f}g")
    
    # Compare
    error = abs(trimesh_weight - manual_weight) / manual_weight * 100
    print(f"\nComparison:")
    print(f"  - Manual: {manual_weight:.0f}g")
    print(f"  - Trimesh: {trimesh_weight:.0f}g")
    print(f"  - Error: {error:.1f}%")
    
    if error < 5:
        print("✅ Trimesh is working correctly!")
        return True, trimesh_weight
    else:
        print("❌ Trimesh has issues")
        return False, 0

def test_manual_cylinder():
    """Create cylinder manually to debug mesh generation"""
    print("\n=== TESTING MANUAL CYLINDER ===")
    
    radius = 110.0  # mm
    height = 20.0   # mm
    n_theta = 16
    
    # Create vertices
    vertices = []
    
    # Bottom circle
    for i in range(n_theta):
        angle = 2 * np.pi * i / n_theta
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = 0
        vertices.append([x, y, z])
    
    # Top circle
    for i in range(n_theta):
        angle = 2 * np.pi * i / n_theta
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = height
        vertices.append([x, y, z])
    
    # Center points
    vertices.append([0, 0, 0])      # Bottom center
    vertices.append([0, 0, height]) # Top center
    
    vertices = np.array(vertices)
    
    # Create faces
    faces = []
    
    # Side faces
    for i in range(n_theta):
        i_next = (i + 1) % n_theta
        
        # Bottom ring indices: 0 to n_theta-1
        # Top ring indices: n_theta to 2*n_theta-1
        v1 = i                   # Bottom current
        v2 = i_next              # Bottom next
        v3 = n_theta + i         # Top current
        v4 = n_theta + i_next    # Top next
        
        # Two triangles per side
        faces.append([v1, v3, v2])
        faces.append([v2, v3, v4])
    
    # Bottom cap
    bottom_center = len(vertices) - 2
    for i in range(n_theta):
        i_next = (i + 1) % n_theta
        faces.append([bottom_center, i_next, i])  # Counter-clockwise from bottom
    
    # Top cap
    top_center = len(vertices) - 1
    for i in range(n_theta):
        i_next = (i + 1) % n_theta
        faces.append([top_center, n_theta + i, n_theta + i_next])  # Counter-clockwise from top
    
    # Create mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    print(f"Manual cylinder:")
    print(f"  - Vertices: {len(vertices)}")
    print(f"  - Faces: {len(faces)}")
    print(f"  - Watertight: {mesh.is_watertight}")
    print(f"  - Volume: {mesh.volume:.0f} mm³")
    
    if mesh.volume < 0:
        print("  - Flipping negative volume")
        mesh.invert()
    
    volume_mm3 = abs(mesh.volume)
    volume_cm3 = volume_mm3 / 1000000
    weight = volume_cm3 * 1.28
    
    print(f"  - Final volume: {volume_cm3:.0f} cm³")
    print(f"  - Weight: {weight:.0f}g")
    
    return mesh, weight

if __name__ == "__main__":
    # Test 1: Built-in cylinder
    success1, weight1 = test_basic_cylinder()
    
    # Test 2: Manual cylinder
    mesh2, weight2 = test_manual_cylinder()
    
    print(f"\n" + "="*50)
    print("SUMMARY:")
    if success1:
        print(f"Built-in cylinder: {weight1:.0f}g")
    print(f"Manual cylinder: {weight2:.0f}g")
    
    if weight2 > 500:
        print("✅ Manual mesh generation works!")
        print("The issue is in the disc profile geometry, not trimesh.")
    else:
        print("❌ Still debugging needed")