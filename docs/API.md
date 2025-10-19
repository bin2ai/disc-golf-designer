# API Documentation

## DiscProfile Class

The core class that handles disc design and calculations.

### Constructor

```python
disc_profile = DiscProfile()
```

Creates a new disc profile with default 7-point control system.

### Methods

#### `calculate_dimensions(material="PETG (Recommended)")`

Calculates disc dimensions and properties with material-specific density.

**Parameters:**
- `material` (str): Material type for density calculation
  - "PLA (Lighter)" - 1.24 g/cm³
  - "PETG (Recommended)" - 1.28 g/cm³  
  - "ABS (Stronger)" - 1.05 g/cm³
  - "Commercial Plastic (Reference)" - 1.60 g/cm³

**Returns:**
- `dict`: Dictionary containing:
  - `radius` (float): Disc radius in mm
  - `diameter` (float): Disc diameter in mm
  - `flight_plate_thickness` (float): Flight plate thickness in mm
  - `disc_thickness` (float): Total disc thickness in mm
  - `rim_depth` (float): Rim depth in mm
  - `rim_width` (float): Rim width in mm
  - `estimated_weight` (float): Estimated weight in grams

#### `get_full_profile()`

Generates the complete disc profile using spline interpolation.

**Returns:**
- `tuple`: (x_coords, y_coords) numpy arrays representing the profile

#### `validate_constraints()`

Validates all geometric constraints and PDGA compliance.

**Returns:**
- `dict`: Dictionary containing validation results with status and messages

### Properties

#### `points`

Dictionary containing the 7 control points:

```python
{
    1: {'x': 0, 'y': 0, 'name': 'Center Top', 'fixed_x': True},
    2: {'x': -90, 'y': -1, 'name': 'Shoulder'},
    3: {'x': -110, 'y': -2, 'name': 'Nose'},
    4: {'x': -100, 'y': -8, 'name': 'Rim Top'},
    5: {'x': -85, 'y': -15, 'name': 'Rim Bottom'},
    6: {'x': -85, 'y': -12, 'name': 'Rim End'},
    7: {'x': 0, 'y': -2, 'name': 'Center Bottom', 'fixed_x': True}
}
```

#### `curves`

Dictionary containing curve parameters between control points.

## Utility Functions

### `create_plotly_visualization(disc_profile)`

Creates interactive 2D cross-section and 3D revolved model visualization.

**Parameters:**
- `disc_profile` (DiscProfile): The disc profile to visualize

**Returns:**
- `plotly.graph_objects.Figure`: Interactive plotly figure

### `generate_stl_file(disc_profile, filename="disc.stl")`

Generates STL file for 3D printing.

**Parameters:**
- `disc_profile` (DiscProfile): The disc profile to export
- `filename` (str): Output filename

**Returns:**
- `str`: Success message or error description

## Constants

### PDGA Standards

```python
PDGA_STANDARDS = {
    'min_diameter': 210,     # mm
    'max_diameter': 230,     # mm
    'min_height': 10,        # mm
    'max_height': 30,        # mm
    'min_weight': 150,       # g
    'max_weight': 180,       # g
    'min_rim_depth': 5,      # mm
    'max_rim_depth': 25,     # mm
    'min_rim_width': 10,     # mm
    'max_rim_width': 25,     # mm
    'min_flight_plate': 1,   # mm
    'max_flight_plate': 4    # mm
}
```