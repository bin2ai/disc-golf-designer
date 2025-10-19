# User Guide

## Getting Started

### Installation

1. **Download or Clone**
   ```bash
   git clone https://github.com/yourusername/disc-golf-designer.git
   cd disc-golf-designer
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**
   ```bash
   streamlit run app.py
   ```

### First Steps

1. **Open your browser** to `http://localhost:8501`
2. **Explore the default disc design** - starts with a basic midrange disc
3. **Try adjusting the sidebar controls** to see real-time changes
4. **Watch the validation messages** for PDGA compliance feedback

## Interface Overview

### Main View
- **2D Cross-Section**: Shows the disc profile with control points
- **3D Model**: Interactive 3D visualization of the revolved disc
- **Metrics**: Real-time calculations for diameter, weight, etc.

### Sidebar Controls
- **Key Parameters**: Quick adjustments for common disc properties
- **Fine-Tune Points**: Precise control over individual points
- **Shape Curves**: Adjust curve strength and angles
- **Material Selection**: Choose plastic type for weight calculation

## Design Process

### 1. Start with Key Parameters

Use the main parameter sliders to quickly establish the basic disc shape:

- **Disc Type**: Choose from Distance Driver, Fairway Driver, Midrange, or Putter presets
- **Diameter**: Overall disc size (210-230mm)
- **Total Height**: Disc thickness (10-30mm)
- **Rim Depth**: How deep the rim cavity is
- **Rim Width**: How wide the rim is

### 2. Fine-Tune Control Points

For precise control, expand the "Fine-Tune Points" section:

- **Point 2 (Shoulder)**: Controls the flight plate edge transition
- **Point 3 (Nose)**: The leftmost rim edge point
- **Point 4 (Rim Top)**: Upper rim profile shape
- **Point 5 (Rim Bottom)**: Deepest point of the rim
- **Point 6 (Rim End)**: Inner rim wall position
- **Point 7 (Center Bottom)**: Flight plate bottom thickness

### 3. Adjust Curves

Use the "Shape Curves" section to create smooth transitions:

- **Curve Strength**: -2.0 to 2.0 (negative = inward curve, positive = outward curve)
- **Tangent Angle**: -180° to 180° (controls curve direction)

### 4. Validate Design

Watch the real-time validation:

- ✅ **Green**: PDGA compliant
- ⚠️ **Yellow**: Warning (still usable)
- ❌ **Red**: Error (needs fixing)

### 5. Export

When satisfied with your design:

- **STL Export**: Generate 3D printable file
- **Save Settings**: Note the parameters for future reference

## Control Point System

### Understanding the 7 Points

1. **Center Top (P1)**: Fixed at origin (0,0) - flight plate center
2. **Shoulder (P2)**: Transition from flight plate to rim
3. **Nose (P3)**: Leftmost point - determines disc diameter
4. **Rim Top (P4)**: Upper rim profile curve
5. **Rim Bottom (P5)**: Bottommost point - determines disc height
6. **Rim End (P6)**: Inner rim wall - affects rim width
7. **Center Bottom (P7)**: Flight plate bottom - determines plate thickness

### Geometric Constraints

The system enforces realistic constraints:

- Points cannot cross each other
- Rim must be to the left of center
- Bottom points must be below top points
- Rim width and depth must be reasonable

## Material Guide

### Plastic Types

**PLA (Lighter)**
- Density: 1.24 g/cm³
- Best for: Lightweight discs, beginners
- Print temp: 190-220°C

**PETG (Recommended)**
- Density: 1.28 g/cm³  
- Best for: Durability and flight consistency
- Print temp: 220-250°C

**ABS (Stronger)**
- Density: 1.05 g/cm³
- Best for: High-impact resistance
- Print temp: 220-250°C

**Commercial Plastic (Reference)**
- Density: 1.60 g/cm³
- For comparison to manufactured discs

## Weight Calculation

The application uses advanced 3D mesh analysis:

1. **Profile Creation**: Generates smooth spline curves
2. **3D Mesh**: Revolves profile to create solid model
3. **Volume Analysis**: Calculates precise volume using trimesh
4. **Weight Estimation**: Multiplies volume by material density

**Typical Results:**
- Distance Driver: 150-170g
- Fairway Driver: 160-175g
- Midrange: 165-180g
- Putter: 170-180g

## Troubleshooting

### Common Issues

**App won't start**
- Check Python version (3.8+)
- Install requirements: `pip install -r requirements.txt`
- Try: `python -m streamlit run app.py`

**Weight shows 0g**
- Check that all control points are properly positioned
- Ensure the disc profile forms a closed shape
- Try adjusting rim width if too narrow

**PDGA validation errors**
- Red messages indicate violations of PDGA rules
- Adjust dimensions to meet 210-230mm diameter range
- Keep height between 10-30mm
- Ensure reasonable rim proportions

**Curves look wrong**
- Reset curve parameters to 0
- Adjust curve strength gradually
- Use tangent angles between -90° and 90° for most natural curves

### Getting Help

1. **Check validation messages** - they provide specific guidance
2. **Use tooltips** - hover over controls for explanations
3. **Try presets** - start with a disc type preset and modify
4. **Reset if needed** - use the reset button to start over

## Tips for Good Designs

### Aerodynamics
- **Smooth curves**: Avoid sharp angles in the profile
- **Gradual transitions**: Use moderate curve strengths
- **Proper rim shape**: Follow the natural S-curve of disc rims

### Printability
- **Wall thickness**: Ensure adequate thickness for 3D printing
- **Support**: Consider overhang angles for support-free printing
- **Scale**: Most printers can handle full-size discs (220mm)

### PDGA Compliance
- **Stay in bounds**: Keep within PDGA dimensional limits
- **Weight targets**: Aim for 150-180g for approved play
- **Rim ratios**: Maintain reasonable rim depth to width ratios

Happy designing! 🥏