#!/usr/bin/env python3
"""
Test the corrected weight calculation with proper conversion
"""

import numpy as np
import trimesh

def test_corrected_conversion():
    """Test with the corrected mm³ to cm³ conversion"""
    print("=== TESTING CORRECTED VOLUME CONVERSION ===")
    
    # Create a simple cylinder
    radius = 110.0  # mm
    height = 20.0   # mm
    
    cylinder = trimesh.creation.cylinder(radius=radius, height=height)
    
    # Get volume in mm³
    volume_mm3 = abs(cylinder.volume)
    
    # CORRECTED conversion: 1000 mm³ = 1 cm³
    volume_cm3 = volume_mm3 / 1000
    weight_petg = volume_cm3 * 1.28
    
    print(f"Solid cylinder test:")
    print(f"  - Radius: {radius}mm")
    print(f"  - Height: {height}mm")
    print(f"  - Volume: {volume_mm3:.0f} mm³")
    print(f"  - Volume: {volume_mm3:.0f} ÷ 1000 = {volume_cm3:.0f} cm³")
    print(f"  - Weight (PETG): {volume_cm3:.0f} × 1.28 = {weight_petg:.0f}g")
    
    print(f"\nRealistic disc weights:")
    print(f"  - 15% fill: {weight_petg * 0.15:.0f}g")
    print(f"  - 18% fill: {weight_petg * 0.18:.0f}g") 
    print(f"  - 22% fill: {weight_petg * 0.22:.0f}g")
    
    if 140 <= weight_petg * 0.18 <= 180:
        print("✅ SUCCESS: 18% fill gives realistic disc weight!")
        return True
    else:
        print("❌ Still not right")
        return False

def test_simple_disc_profile():
    """Test a very simple disc profile"""
    print("\n=== TESTING SIMPLE DISC PROFILE ===")
    
    # Simple disc profile - just a basic shape
    # Top surface at z=0, bottom at z=-18
    radius_outer = 110.0  # mm
    radius_inner = 20.0   # mm  
    height = 18.0         # mm
    
    # Create a simple disc profile
    points = [
        (0, 0),              # Center top
        (radius_inner, 0),   # Inner top
        (radius_outer, 0),   # Outer top
        (radius_outer, -height),  # Outer bottom
        (radius_inner, -height),  # Inner bottom
        (0, -height),        # Center bottom
    ]
    
    # Create revolution
    n_theta = 16
    theta = np.linspace(0, 2*np.pi, n_theta, endpoint=False)
    
    vertices = []
    for x, y in points:
        r = abs(x)
        for angle in theta:
            vertices.append([r * np.cos(angle), r * np.sin(angle), y])
    
    vertices = np.array(vertices)
    n_profile = len(points)
    
    # Create faces
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
    
    # Close the profile
    for j in range(n_theta):
        j_next = (j + 1) % n_theta
        
        v1 = (n_profile - 1) * n_theta + j
        v2 = (n_profile - 1) * n_theta + j_next
        v3 = j
        v4 = j_next
        
        faces.append([v1, v3, v2])
        faces.append([v2, v3, v4])
    
    # Create mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    if mesh.volume < 0:
        mesh.invert()
    
    volume_mm3 = abs(mesh.volume)
    volume_cm3 = volume_mm3 / 1000  # CORRECTED conversion
    weight_petg = volume_cm3 * 1.28
    
    print(f"Simple disc profile:")
    print(f"  - Volume: {volume_mm3:.0f} mm³ = {volume_cm3:.0f} cm³")
    print(f"  - Weight: {weight_petg:.0f}g")
    
    if 120 <= weight_petg <= 200:
        print("✅ SUCCESS: Simple disc profile gives realistic weight!")
        return True
    else:
        print("❌ Still needs work")
        return False

if __name__ == "__main__":
    success1 = test_corrected_conversion()
    success2 = test_simple_disc_profile()
    
    if success1 and success2:
        print("\n🎉 WEIGHT CALCULATION IS FINALLY FIXED!")
        print("The corrected conversion (÷1000) gives realistic weights.")
    else:
        print("\n❌ Still debugging needed")