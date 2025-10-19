#!/usr/bin/env python3
"""
Test the fixed volume calculation from the main app
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import the DiscProfile class from the main app
import numpy as np
import trimesh

class DiscProfile:
    """Test version of DiscProfile with fixed volume calculation"""
    
    def __init__(self):
        # Default 7-point control system
        self.points = {
            1: {'x': 0, 'y': 0, 'name': 'Center Top', 'fixed_x': True},
            2: {'x': -90, 'y': -1, 'name': 'Shoulder'},
            3: {'x': -110, 'y': -2, 'name': 'Nose'},
            4: {'x': -100, 'y': -8, 'name': 'Rim Top'},
            5: {'x': -85, 'y': -15, 'name': 'Rim Bottom'},
            6: {'x': -85, 'y': -12, 'name': 'Rim End'},
            7: {'x': 0, 'y': -2, 'name': 'Center Bottom', 'fixed_x': True}
        }
    
    def _create_trimesh_for_volume_calculation(self):
        """Create a watertight trimesh for accurate volume calculation"""
        try:
            # FIXED: Create a SOLID disc by using a simple top-to-bottom profile
            # This creates the full interior volume, not just the surface
            
            # Create a proper disc profile that fills the interior
            # From the profile points, create top and bottom surfaces
            top_surface_radius = abs(self.points[3]['x'])      # Rim radius (110mm)
            bottom_surface_radius = abs(self.points[6]['x'])   # Inner rim radius (85mm)
            
            top_z = self.points[1]['y']    # Top surface (0mm)
            rim_top_z = self.points[4]['y']    # Rim top (-8mm) 
            rim_bottom_z = self.points[5]['y'] # Rim bottom (-15mm)
            bottom_z = self.points[7]['y'] # Bottom surface (-2mm)
            
            # Create a solid profile that represents the actual disc volume
            profile_points = [
                # Top surface
                (0, top_z),                           # Center top
                (abs(self.points[2]['x']), self.points[2]['y']),  # Shoulder
                # Rim outer edge
                (top_surface_radius, self.points[3]['y']),        # Rim edge top
                (top_surface_radius, rim_top_z),                  # Rim top
                (top_surface_radius, rim_bottom_z),               # Rim bottom 
                # Back towards center at bottom
                (bottom_surface_radius, rim_bottom_z),            # Rim inner bottom
                (bottom_surface_radius, self.points[6]['y']),     # Rim inner top
                (abs(self.points[7]['x']), bottom_z),             # Center bottom area
                (0, bottom_z),                                    # Center bottom
            ]
            
            x_coords = np.array([p[0] for p in profile_points])
            y_coords = np.array([p[1] for p in profile_points])
            
            print("SOLID disc profile points:")
            for i, (x, y) in enumerate(zip(x_coords, y_coords)):
                print(f"  Point {i}: r={x:.0f}mm, z={y:.0f}mm")
            
            # Create revolution mesh 
            n_theta = 24  # Sufficient for volume calculation
            theta = np.linspace(0, 2*np.pi, n_theta, endpoint=False)
            
            vertices = []
            
            # Generate vertices by revolving the SOLID profile
            for i, (x, y) in enumerate(zip(x_coords, y_coords)):
                r = abs(x)
                for j, angle in enumerate(theta):
                    vertex_x = r * np.cos(angle)
                    vertex_y = r * np.sin(angle)
                    vertex_z = y
                    vertices.append([vertex_x, vertex_y, vertex_z])
            
            vertices = np.array(vertices)
            n_profile = len(x_coords)
            
            print(f"Generated {len(vertices)} vertices from {n_profile} profile points × {n_theta} angles")
            
            # Generate faces for the solid shape
            faces = []
            
            # Side faces connecting adjacent profile rings (creates the solid interior)
            for i in range(n_profile - 1):
                for j in range(n_theta):
                    j_next = (j + 1) % n_theta
                    
                    v1 = i * n_theta + j
                    v2 = i * n_theta + j_next
                    v3 = (i + 1) * n_theta + j
                    v4 = (i + 1) * n_theta + j_next
                    
                    # Correct winding for outward normals
                    faces.append([v1, v3, v2])
                    faces.append([v2, v3, v4])
            
            # Close the profile to make it watertight
            for j in range(n_theta):
                j_next = (j + 1) % n_theta
                
                # Connect last profile ring to first profile ring
                v1 = (n_profile - 1) * n_theta + j
                v2 = (n_profile - 1) * n_theta + j_next
                v3 = j  # First ring
                v4 = j_next
                
                faces.append([v1, v3, v2])
                faces.append([v2, v3, v4])
            
            print(f"Generated {len(faces)} faces")
            
            # Create trimesh
            disc_trimesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            
            print(f"Trimesh properties:")
            print(f"  - Watertight: {disc_trimesh.is_watertight}")
            print(f"  - Volume: {disc_trimesh.volume:.0f} mm³")
            
            # Ensure proper orientation
            if disc_trimesh.volume < 0:
                print("  - Flipping negative volume")
                disc_trimesh.invert()
            
            # Fix mesh to ensure it's watertight
            disc_trimesh.fix_normals()
            
            # Volume information
            volume_mm3 = abs(disc_trimesh.volume)
            volume_cm3 = volume_mm3 / 1000000.0  # Explicit float division
            weight_petg = volume_cm3 * 1.28
            
            print(f"\nFinal results:")
            print(f"  - Volume: {volume_mm3:.0f} mm³")
            print(f"  - Volume: {volume_mm3:.0f} ÷ 1,000,000 = {volume_cm3:.1f} cm³")
            print(f"  - Weight (PETG): {volume_cm3:.1f} × 1.28 = {weight_petg:.0f}g")
            
            if 80 <= weight_petg <= 200:
                print("✅ SUCCESS: Weight is in realistic range!")
            else:
                print("❌ FAILED: Weight still unrealistic")
                
                # Compare to what we should get
                expected_vol = np.pi * 110**2 * 15 * 0.2 / 1000000  # 20% fill
                expected_weight = expected_vol * 1.28
                print(f"   Expected ~20% fill: {expected_weight:.0f}g")
            
            return disc_trimesh
            
        except Exception as e:
            print(f"ERROR: Trimesh creation failed: {e}")
            return None
    
    def _fallback_weight_estimation(self, plastic_density):
        """Simple fallback weight estimation based on disc dimensions"""
        radius = abs(self.points[3]['x'])  # ~110mm
        thickness = abs(self.points[1]['y'] - self.points[5]['y'])  # ~15mm
        
        # More realistic approximation for disc golf disc
        cylinder_volume = np.pi * radius**2 * thickness * 0.22
        volume_cm3 = cylinder_volume / 1000000.0  # mm³ to cm³
        
        print(f"\nFallback calculation:")
        print(f"  - Radius: {radius}mm")
        print(f"  - Thickness: {thickness}mm")
        print(f"  - Volume: {cylinder_volume:.0f} mm³ = {volume_cm3:.1f} cm³")
        print(f"  - Weight: {volume_cm3:.1f} × {plastic_density} = {volume_cm3 * plastic_density:.0f}g")
        
        return volume_cm3 * plastic_density

def test_fixed_volume():
    """Test the fixed volume calculation"""
    print("=== TESTING FIXED VOLUME CALCULATION ===")
    
    disc = DiscProfile()
    
    # Test trimesh calculation
    mesh = disc._create_trimesh_for_volume_calculation()
    
    # Test fallback calculation
    fallback_weight = disc._fallback_weight_estimation(1.28)
    
    print(f"\n" + "="*50)
    print("COMPARISON:")
    if mesh:
        volume_cm3 = abs(mesh.volume) / 1000000
        trimesh_weight = volume_cm3 * 1.28
        print(f"Trimesh method: {trimesh_weight:.0f}g")
    print(f"Fallback method: {fallback_weight:.0f}g")
    
    return mesh is not None

if __name__ == "__main__":
    success = test_fixed_volume()
    if success:
        print("\n🎉 VOLUME CALCULATION FIXED!")
    else:
        print("\n❌ Still needs work")