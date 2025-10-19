#!/usr/bin/env python3
"""
Debug the unit conversion issue
"""

import numpy as np
import trimesh

def debug_unit_conversion():
    """Debug exactly what's happening with unit conversion"""
    print("=== DEBUGGING UNIT CONVERSION ===")
    
    # Create simple solid cylinder
    radius = 110.0  # mm
    height = 18.0   # mm
    
    # Manual calculation
    volume_mm3_manual = np.pi * radius**2 * height
    volume_cm3_manual = volume_mm3_manual / 1000000
    
    print(f"Manual calculation:")
    print(f"- π × {radius}² × {height} = {volume_mm3_manual:.0f} mm³")
    print(f"- {volume_mm3_manual:.0f} ÷ 1,000,000 = {volume_cm3_manual:.3f} cm³")
    print(f"- {volume_cm3_manual:.3f} cm³ × 1.28 g/cm³ = {volume_cm3_manual * 1.28:.1f}g")
    
    # Now test trimesh
    profile_points = [(radius, 0), (radius, -height)]
    x_coords = np.array([p[0] for p in profile_points])
    y_coords = np.array([p[1] for p in profile_points])
    
    n_theta = 16
    theta = np.linspace(0, 2*np.pi, n_theta, endpoint=False)
    
    vertices = []
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        r = abs(x)
        for j, angle in enumerate(theta):
            vertex_x = r * np.cos(angle)
            vertex_y = r * np.sin(angle)
            vertex_z = y
            vertices.append([vertex_x, vertex_y, vertex_z])
    
    # Add centers
    top_center = [0, 0, 0]
    bottom_center = [0, 0, -height]
    vertices.extend([top_center, bottom_center])
    vertices = np.array(vertices)
    
    # Create faces
    faces = []
    n_profile = len(x_coords)
    
    # Side faces
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        v1, v2 = j, j_next
        v3, v4 = n_theta + j, n_theta + j_next
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
    
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    print(f"\nTrimesh results:")
    print(f"- Raw volume: {mesh.volume}")
    print(f"- Absolute volume: {abs(mesh.volume)}")
    print(f"- Is negative: {mesh.volume < 0}")
    
    volume_mm3 = abs(mesh.volume)
    print(f"- Volume in mm³: {volume_mm3}")
    print(f"- Volume in mm³ (formatted): {volume_mm3:.0f}")
    print(f"- Volume in mm³ (exact): {volume_mm3:.6f}")
    
    # Step by step conversion
    print(f"\nStep by step conversion:")
    print(f"- {volume_mm3:.6f} mm³")
    conversion_factor = 1000000
    print(f"- ÷ {conversion_factor} = {volume_mm3 / conversion_factor:.6f}")
    
    volume_cm3 = volume_mm3 / conversion_factor
    print(f"- Volume in cm³: {volume_cm3:.6f}")
    print(f"- Volume in cm³ (rounded): {volume_cm3:.3f}")
    print(f"- Volume in cm³ (int): {int(volume_cm3)}")
    
    weight = volume_cm3 * 1.28
    print(f"- Weight: {volume_cm3:.6f} × 1.28 = {weight:.3f}g")
    
    # Compare to expected
    error = abs(volume_cm3 - volume_cm3_manual) / volume_cm3_manual * 100
    print(f"\nComparison:")
    print(f"- Expected: {volume_cm3_manual:.3f} cm³")
    print(f"- Actual: {volume_cm3:.3f} cm³") 
    print(f"- Error: {error:.1f}%")
    
    if error < 20:
        print("✅ Unit conversion is working correctly!")
        print(f"   Weight: {weight:.0f}g (solid cylinder)")
        print(f"   Real disc ~70%: {weight * 0.7:.0f}g")
        
        if 80 <= weight * 0.7 <= 200:
            print("✅ This is in the correct weight range!")
            return True
    else:
        print("❌ Still has conversion issues")
        return False

if __name__ == "__main__":
    success = debug_unit_conversion()
    if success:
        print("\n🎉 VOLUME CALCULATION IS FIXED!")
        print("   Ready to update the main application.")
    else:
        print("\n❌ Still needs debugging")