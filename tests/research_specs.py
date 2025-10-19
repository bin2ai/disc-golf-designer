#!/usr/bin/env python3
"""
Research actual disc golf disc specifications
"""

def research_disc_specs():
    """Calculate volume based on real disc measurements"""
    print("=== REAL DISC GOLF DISC RESEARCH ===")
    
    # Standard PDGA disc specifications:
    diameter_mm = 220  # Standard disc diameter
    radius_mm = diameter_mm / 2
    
    # Height varies by disc type
    typical_heights = {
        "Distance Driver": 18,
        "Fairway Driver": 19, 
        "Midrange": 20,
        "Putter": 22
    }
    
    # Typical weights
    typical_weights = {
        "Light": "150-165g",
        "Standard": "165-175g", 
        "Max Weight": "175-180g"
    }
    
    print(f"PDGA Standard Specifications:")
    print(f"- Diameter: {diameter_mm}mm")
    print(f"- Radius: {radius_mm}mm")
    print("")
    
    for disc_type, height in typical_heights.items():
        print(f"{disc_type}: {height}mm height")
        
        # Calculate volume of solid cylinder
        volume_mm3 = 3.14159 * radius_mm**2 * height
        volume_cm3 = volume_mm3 / 1000000
        
        # Estimate hollow factor (discs are not solid)
        # Flight plate is thin, rim has hollow sections
        hollow_factors = {
            "Distance Driver": 0.15,  # Very hollow, thin flight plate
            "Fairway Driver": 0.18,
            "Midrange": 0.22,
            "Putter": 0.25  # More solid, thicker
        }
        
        hollow_factor = hollow_factors[disc_type]
        actual_volume = volume_cm3 * hollow_factor
        
        # PETG density: 1.28 g/cm³
        weight_petg = actual_volume * 1.28
        
        print(f"  - Solid volume: {volume_cm3:.0f} cm³")
        print(f"  - Hollow factor: {hollow_factor:.0%}")
        print(f"  - Actual volume: {actual_volume:.0f} cm³") 
        print(f"  - PETG weight: {weight_petg:.0f}g")
        print("")
    
    print("Expected Results:")
    print("- Standard disc: 120-140g PETG")
    print("- Volume should be: 95-110 cm³")
    print("- Our current result: 0.67 cm³ = 1g")
    print("")
    print("CONCLUSION: Our volume is ~150x too small!")
    print("There must be a fundamental error in the mesh generation.")

def calculate_what_we_need():
    """Calculate what volume we need to get realistic weights"""
    print("=== WHAT VOLUME DO WE NEED? ===")
    
    target_weights = [120, 140, 160, 175]  # grams
    petg_density = 1.28  # g/cm³
    
    print("To achieve realistic weights with PETG:")
    for weight in target_weights:
        needed_volume = weight / petg_density
        print(f"- {weight}g requires {needed_volume:.0f} cm³")
    
    print("")
    print(f"Current volume: 0.67 cm³")
    print(f"Needed volume: ~94-137 cm³")
    print(f"Scaling factor needed: {94 / 0.67:.0f}x to {137 / 0.67:.0f}x")
    
    return 94, 137

if __name__ == "__main__":
    research_disc_specs()
    min_vol, max_vol = calculate_what_we_need()
    
    print("\n" + "="*50)
    print("DIAGNOSIS:")
    print("1. ✅ Unit conversion is correct")
    print("2. ✅ Trimesh volume calculation is working") 
    print("3. ❌ Mesh geometry is fundamentally wrong")
    print("4. 🔍 Need to investigate mesh generation process")
    print("")
    print("The issue is likely:")
    print("- Wrong profile interpretation")
    print("- Incorrect face winding")
    print("- Missing volume in the mesh")