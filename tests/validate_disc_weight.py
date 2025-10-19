#!/usr/bin/env python3
"""
Comprehensive test with realistic disc golf disc dimensions
"""

import numpy as np
import trimesh

def test_realistic_disc_dimensions():
    """Test with actual disc golf disc dimensions"""
    print("=== Testing Realistic Disc Golf Disc ===")
    
    # Typical disc golf disc specifications:
    # - Diameter: 210-220mm (PDGA regulation)
    # - Radius: 105-110mm
    # - Height: 12-20mm
    # - Rim width: 15-25mm
    # - Flight plate thickness: 1-3mm
    
    # Create realistic disc profile (simplified but accurate)
    profile_points = [
        (0, 0),        # center top (flight plate)
        (80, -1),      # shoulder start
        (105, -2),     # shoulder end
        (110, -4),     # rim start
        (110, -15),    # rim bottom
        (90, -18),     # rim taper
        (0, -18)       # center bottom
    ]
    
    x_coords = np.array([p[0] for p in profile_points])
    y_coords = np.array([p[1] for p in profile_points])
    
    print(f"Disc dimensions:")
    print(f"- Diameter: {max(x_coords) * 2:.0f}mm")
    print(f"- Height: {abs(min(y_coords)):.0f}mm")
    print(f"- Flight plate thickness: {abs(y_coords[1]):.0f}mm")
    
    # Expected volume calculation (rough estimate):
    # Approximate as truncated cone/cylinder hybrid
    avg_radius = 85  # mm (between center and rim)
    height = 18      # mm
    fill_factor = 0.6  # Disc shape factor
    expected_volume_mm3 = np.pi * avg_radius**2 * height * fill_factor
    expected_volume_cm3 = expected_volume_mm3 / 1000000
    expected_weight_petg = expected_volume_cm3 * 1.28
    
    print(f"\nExpected estimates:")
    print(f"- Volume: ~{expected_volume_cm3:.0f} cm³")
    print(f"- Weight (PETG): ~{expected_weight_petg:.0f}g")
    
    # Create revolution mesh
    n_theta = 24  # Good resolution
    theta = np.linspace(0, 2*np.pi, n_theta, endpoint=False)
    
    vertices = []
    faces = []
    
    # Generate vertices by revolving profile
    for i, (x, y) in enumerate(zip(x_coords, y_coords)):
        r = abs(x)
        for j, angle in enumerate(theta):
            vertex_x = r * np.cos(angle)
            vertex_y = r * np.sin(angle)
            vertex_z = y
            vertices.append([vertex_x, vertex_y, vertex_z])
    
    vertices = np.array(vertices)
    n_profile = len(x_coords)
    
    print(f"\nMesh generation:")
    print(f"- Profile points: {n_profile}")
    print(f"- Angular divisions: {n_theta}")
    print(f"- Total vertices: {len(vertices)}")
    
    # Generate side faces with correct winding
    for i in range(n_profile - 1):
        for j in range(n_theta):
            j_next = (j + 1) % n_theta
            
            v1 = i * n_theta + j
            v2 = i * n_theta + j_next
            v3 = (i + 1) * n_theta + j
            v4 = (i + 1) * n_theta + j_next
            
            # Corrected winding for outward normals
            faces.append([v1, v3, v2])
            faces.append([v2, v3, v4])
    
    print(f"- Side faces: {len(faces)}")
    
    # Add center vertices for caps
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
    
    print(f"- Cap faces: {n_theta * 2}")
    print(f"- Total faces: {len(faces)}")
    
    try:
        # Create mesh
        disc_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
        
        print(f"\nMesh analysis:")
        print(f"- Is watertight: {disc_mesh.is_watertight}")
        print(f"- Volume (raw): {disc_mesh.volume:.0f} mm³")
        
        # Handle negative volume (flip if needed)
        if disc_mesh.volume < 0:
            print("- Volume was negative, flipping normals...")
            disc_mesh.invert()
            
        volume_mm3 = abs(disc_mesh.volume)
        volume_cm3 = volume_mm3 / 1000000
        
        print(f"- Final volume: {volume_mm3:.0f} mm³ = {volume_cm3:.1f} cm³")
        
        # Calculate weights for different materials
        materials = {
            "PLA": 1.24,
            "PETG": 1.28,
            "ABS": 1.05
        }
        
        print(f"\nWeight calculations:")
        for material, density in materials.items():
            weight = volume_cm3 * density
            print(f"- {material}: {weight:.0f}g")
        
        # Validation
        if 50 <= volume_cm3 * 1.28 <= 250:
            print(f"\n✅ SUCCESS: Weight in acceptable range (50-250g)")
            print(f"   PETG weight: {volume_cm3 * 1.28:.0f}g")
        else:
            print(f"\n❌ FAILED: Weight out of range")
            print(f"   PETG weight: {volume_cm3 * 1.28:.0f}g (should be 50-250g)")
        
        return disc_mesh, volume_cm3
        
    except Exception as e:
        print(f"\nError creating mesh: {e}")
        return None, 0

def validate_against_known_discs():
    """Validate against known commercial disc specifications"""
    print("\n" + "="*50)
    print("VALIDATION AGAINST KNOWN DISCS")
    print("="*50)
    
    known_discs = [
        {"name": "Innova Champion Destroyer", "weight": "173-175g", "diameter": "211mm"},
        {"name": "Discraft ESP Buzzz", "weight": "177-180g", "diameter": "215mm"},
        {"name": "Dynamic Discs Lucid Judge", "weight": "173-176g", "diameter": "210mm"}
    ]
    
    print("Commercial disc golf discs typically weigh:")
    for disc in known_discs:
        print(f"- {disc['name']}: {disc['weight']} (diameter: {disc['diameter']})")
    
    print(f"\n3D printed discs should be lighter due to:")
    print(f"- Lower plastic density (PETG 1.28 vs commercial ~1.6 g/cm³)")
    print(f"- Infill percentage (usually 80-100%)")
    print(f"- Expected range: 100-150g for PETG")

if __name__ == "__main__":
    print("COMPREHENSIVE DISC GOLF DISC WEIGHT VALIDATION")
    print("=" * 60)
    
    # Test with realistic dimensions
    mesh, volume = test_realistic_disc_dimensions()
    
    # Show validation against known discs
    validate_against_known_discs()
    
    print(f"\n" + "="*60)
    if volume > 0:
        petg_weight = volume * 1.28
        if 50 <= petg_weight <= 250:
            print(f"✅ FINAL RESULT: {petg_weight:.0f}g PETG - ACCEPTABLE")
        else:
            print(f"❌ FINAL RESULT: {petg_weight:.0f}g PETG - OUT OF RANGE")
    else:
        print(f"❌ FINAL RESULT: Volume calculation failed")