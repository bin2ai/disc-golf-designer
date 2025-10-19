#!/usr/bin/env python3
"""
Test the actual DiscProfile class with corrected weight calculation
"""

import sys
import os
import numpy as np

# Import required modules first
try:
    import trimesh
except ImportError:
    print("Installing trimesh...")
    os.system("pip install trimesh")
    import trimesh

# Add the current directory to path
sys.path.append(os.path.dirname(__file__))

# Import the class from the main file without running the Streamlit app
def extract_disc_profile_class():
    """Extract just the DiscProfile class without running Streamlit"""
    
    # Read the main file and extract the class
    with open('disc_designer.py', 'r') as f:
        content = f.read()
    
    # Find the class definition
    class_start = content.find('class DiscProfile:')
    if class_start == -1:
        print("Could not find DiscProfile class")
        return None
    
    # Find the end of the class (next class or function at root level)
    lines = content[class_start:].split('\n')
    class_lines = []
    indent_level = None
    
    for line in lines:
        if line.strip() == '':
            class_lines.append(line)
            continue
            
        if line.startswith('class ') or line.startswith('def ') and not line.startswith('    '):
            if class_lines:  # We've found the end of the class
                break
        
        if indent_level is None and line.strip():
            indent_level = len(line) - len(line.lstrip())
        
        class_lines.append(line)
    
    # Execute the class definition
    class_code = '\n'.join(class_lines)
    
    # Create a local namespace with required imports
    namespace = {
        'np': np,
        'trimesh': trimesh,
        'create_simplified_profile': lambda x, y, target_points: (x[::len(x)//target_points], y[::len(y)//target_points])
    }
    
    try:
        exec(class_code, namespace)
        return namespace['DiscProfile']
    except Exception as e:
        print(f"Error executing class: {e}")
        return None

def test_disc_profile():
    """Test the DiscProfile class"""
    print("=== TESTING DISCPROFILE CLASS ===")
    
    DiscProfile = extract_disc_profile_class()
    if not DiscProfile:
        print("Failed to extract DiscProfile class")
        return False
    
    # Create instance
    disc = DiscProfile()
    
    # Test dimensions calculation
    dimensions = disc.calculate_dimensions("PETG (Recommended)")
    
    print(f"Disc dimensions:")
    print(f"  - Diameter: {dimensions['diameter']:.0f}mm")
    print(f"  - Height: {dimensions['disc_thickness']:.0f}mm")
    print(f"  - Weight: {dimensions['estimated_weight']:.0f}g")
    
    # Check if weight is realistic
    weight = dimensions['estimated_weight']
    if 120 <= weight <= 200:
        print("✅ SUCCESS: Weight calculation is now realistic!")
        return True
    else:
        print(f"❌ FAILED: Weight {weight:.0f}g is still not realistic")
        return False

if __name__ == "__main__":
    success = test_disc_profile()
    if success:
        print("\n🎉 DISC GOLF DESIGNER WEIGHT CALCULATION FIXED!")
        print("The application now shows realistic disc weights.")
    else:
        print("\n❌ Still needs debugging")