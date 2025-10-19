#!/usr/bin/env python3
"""
Fix the display formatting issue and recalculate properly
"""

import numpy as np

def calculate_real_volumes():
    """Calculate actual expected volumes without formatting issues"""
    print("=== REAL VOLUME CALCULATIONS ===")
    
    diameter_mm = 220
    radius_mm = diameter_mm / 2
    heights = [18, 19, 20, 22]  # mm
    
    print(f"Standard disc: {diameter_mm}mm diameter ({radius_mm}mm radius)")
    print("")
    
    for height in heights:
        # Volume in mm³
        volume_mm3 = np.pi * radius_mm**2 * height
        
        # Convert to cm³ properly
        volume_cm3 = volume_mm3 / 1000000
        
        print(f"Height {height}mm:")
        print(f"  - Volume: π × {radius_mm}² × {height} = {volume_mm3:.0f} mm³")
        print(f"  - Volume: {volume_mm3:.0f} mm³ ÷ 1,000,000 = {volume_cm3:.1f} cm³")
        print(f"  - PETG weight: {volume_cm3:.1f} × 1.28 = {volume_cm3 * 1.28:.0f}g")
        print(f"  - At 20% hollow: {volume_cm3 * 0.2 * 1.28:.0f}g")
        print("")
    
    # What we're actually getting
    our_volume = 0.667  # cm³
    our_weight = our_volume * 1.28
    print(f"Our current result: {our_volume:.1f} cm³ = {our_weight:.0f}g")
    print("")
    
    # The issue
    expected_solid = np.pi * 110**2 * 20 / 1000000  # 20mm height
    ratio = expected_solid / our_volume
    
    print(f"Expected solid volume: {expected_solid:.0f} cm³")
    print(f"Our volume: {our_volume:.1f} cm³") 
    print(f"We're off by factor of: {ratio:.0f}x")
    
    return expected_solid

def debug_simple_cylinder():
    """Create the simplest possible cylinder to debug"""
    print("\n=== DEBUGGING SIMPLE CYLINDER ===")
    
    import trimesh
    
    # Create cylinder using trimesh built-in
    radius = 110.0  # mm
    height = 20.0   # mm
    
    cylinder = trimesh.creation.cylinder(radius=radius, height=height)
    
    volume_mm3 = cylinder.volume
    volume_cm3 = volume_mm3 / 1000000
    weight = volume_cm3 * 1.28
    
    print(f"Trimesh built-in cylinder:")
    print(f"  - Radius: {radius}mm")
    print(f"  - Height: {height}mm") 
    print(f"  - Volume: {volume_mm3:.0f} mm³")
    print(f"  - Volume: {volume_cm3:.0f} cm³")
    print(f"  - Weight: {weight:.0f}g")
    
    # Manual calculation
    manual_volume_mm3 = np.pi * radius**2 * height
    manual_volume_cm3 = manual_volume_mm3 / 1000000
    manual_weight = manual_volume_cm3 * 1.28
    
    print(f"\nManual calculation:")
    print(f"  - Volume: {manual_volume_mm3:.0f} mm³")
    print(f"  - Volume: {manual_volume_cm3:.0f} cm³")
    print(f"  - Weight: {manual_weight:.0f}g")
    
    if abs(volume_cm3 - manual_volume_cm3) < 1:
        print("✅ Trimesh cylinder matches manual calculation!")
        return True, volume_cm3
    else:
        print("❌ Trimesh cylinder doesn't match manual")
        return False, 0

if __name__ == "__main__":
    expected = calculate_real_volumes()
    success, actual = debug_simple_cylinder()
    
    if success:
        print(f"\n🎉 FOUND THE ISSUE!")
        print(f"Trimesh works correctly: {actual:.0f} cm³")
        print(f"The problem is in our custom mesh generation!")
        print(f"We need to fix the disc profile mesh creation.")
    else:
        print(f"\n❌ Still debugging needed")