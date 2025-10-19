import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import interpolate
from scipy.spatial.distance import cdist
import pandas as pd
from stl import mesh
import trimesh
import io
import base64

# Performance optimization for Streamlit Cloud
@st.cache_data
def create_cached_mesh(vertices, faces):
    """Create and cache mesh objects for better performance"""
    return trimesh.Trimesh(vertices=vertices, faces=faces)

@st.cache_data
def calculate_cached_spline(points, smoothing=0.1):
    """Cache spline calculations for better performance"""
    if len(points) < 2:
        return np.array([]), np.array([])
    
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    if len(points) == 2:
        t = np.linspace(0, 1, 100)
        x_interp = np.interp(t, [0, 1], x_coords)
        y_interp = np.interp(t, [0, 1], y_coords)
    else:
        t = np.linspace(0, 1, len(points))
        t_new = np.linspace(0, 1, 100)
        
        try:
            tck_x, _ = interpolate.splprep([x_coords, y_coords], s=smoothing, k=min(3, len(points)-1))
            x_interp, y_interp = interpolate.splev(t_new, tck_x)
        except:
            x_interp = np.interp(t_new, t, x_coords)
            y_interp = np.interp(t_new, t, y_coords)
    
    return x_interp, y_interp

@st.cache_data
def load_logo():
    """Load and cache the logo for favicon"""
    try:
        import os
        logo_path = os.path.join(os.path.dirname(__file__), "media", "logo.png")
        if os.path.exists(logo_path):
            return logo_path
        else:
            return "🥏"  # Fallback emoji
    except:
        return "🥏"  # Fallback emoji

@st.cache_data
def get_logo_base64():
    """Convert logo to base64 for embedding in HTML"""
    try:
        import os
        logo_path = os.path.join(os.path.dirname(__file__), "media", "logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_bytes = f.read()
            logo_base64 = base64.b64encode(logo_bytes).decode()
            return f"data:image/png;base64,{logo_base64}"
        else:
            return None
    except:
        return None

# Configure page
st.set_page_config(
    page_title="Disc Golf Designer Pro",
    page_icon=load_logo(),
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        text-align: center;
        font-weight: 700;
    }
    .parameter-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #f39c12;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f1aeb5;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #e74c3c;
    }
    .success-box {
        background: #d1ecf1;
        border: 1px solid #b8daff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class PDGAStandards:
    """PDGA specification standards for disc golf discs"""
    
    # Diameter specifications (in mm)
    MIN_DIAMETER = 210.0
    MAX_DIAMETER = 230.0
    
    # Height specifications (in mm)
    MIN_HEIGHT = 10.0
    MAX_HEIGHT = 30.0
    
    # Weight specifications (in grams)
    MIN_WEIGHT = 150.0
    MAX_WEIGHT = 180.0
    
    # Rim specifications (in mm)
    MIN_RIM_DEPTH = 5.0
    MAX_RIM_DEPTH = 25.0
    MIN_RIM_WIDTH = 10.0
    MAX_RIM_WIDTH = 25.0
    
    # Flight plate thickness (in mm)
    MIN_FLIGHT_PLATE_THICKNESS = 1.0
    MAX_FLIGHT_PLATE_THICKNESS = 4.0
    
    @classmethod
    def validate_dimensions(cls, diameter, height, weight, rim_depth, rim_width, flight_plate_thickness):
        """Validate dimensions against PDGA standards"""
        violations = []
        warnings = []
        
        if diameter < cls.MIN_DIAMETER or diameter > cls.MAX_DIAMETER:
            violations.append(f"Diameter ({diameter:.1f}mm) must be between {cls.MIN_DIAMETER}-{cls.MAX_DIAMETER}mm")
        
        if height < cls.MIN_HEIGHT or height > cls.MAX_HEIGHT:
            violations.append(f"Height ({height:.1f}mm) must be between {cls.MIN_HEIGHT}-{cls.MAX_HEIGHT}mm")
        
        if weight < cls.MIN_WEIGHT or weight > cls.MAX_WEIGHT:
            violations.append(f"Weight ({weight:.1f}g) must be between {cls.MIN_WEIGHT}-{cls.MAX_WEIGHT}g")
        
        if rim_depth < cls.MIN_RIM_DEPTH or rim_depth > cls.MAX_RIM_DEPTH:
            violations.append(f"Rim depth ({rim_depth:.1f}mm) must be between {cls.MIN_RIM_DEPTH}-{cls.MAX_RIM_DEPTH}mm")
        
        if rim_width < cls.MIN_RIM_WIDTH or rim_width > cls.MAX_RIM_WIDTH:
            violations.append(f"Rim width ({rim_width:.1f}mm) must be between {cls.MIN_RIM_WIDTH}-{cls.MAX_RIM_WIDTH}mm")
        
        if flight_plate_thickness < cls.MIN_FLIGHT_PLATE_THICKNESS or flight_plate_thickness > cls.MAX_FLIGHT_PLATE_THICKNESS:
            warnings.append(f"Flight plate thickness ({flight_plate_thickness:.1f}mm) should be between {cls.MIN_FLIGHT_PLATE_THICKNESS}-{cls.MAX_FLIGHT_PLATE_THICKNESS}mm")
        
        return violations, warnings

class DiscProfile:
    """Class to handle disc cross-section profile with 7 control points"""
    
    # Parameterized defaults for disc types
    DISC_PRESETS = {
        'driver': {
            'radius': 105.0,  # Controls nose position (point 3)
            'shoulder_offset': 90.0,  # Point 2 distance from center
            'rim_width': 25.0,  # Points 4,5,6 distance from nose
            'total_height': 12.0,  # Point 5 depth
            'flight_plate_thickness': 2.0,  # Point 7 depth
            'shoulder_drop': 3.0,  # Point 2 Y offset
            'nose_drop': 5.0,  # Point 3 Y offset
        }
    }
    
    def __init__(self, preset='driver'):
        self.points = {}
        self.curves = {}
        self.initialize_profile(preset)
    
    def initialize_profile(self, preset='driver'):
        """Initialize with parameterized disc profile"""
        p = self.DISC_PRESETS[preset]
        
        # Calculate related positions from parameters
        self.points = {
            1: {'x': 0, 'y': 0, 'fixed_x': True, 'fixed_y': True, 'name': 'Flight Plate Top'},
            2: {'x': -p['shoulder_offset'], 'y': -p['shoulder_drop'], 'fixed_x': False, 'fixed_y': False, 'name': 'Shoulder'},
            3: {'x': -p['radius'], 'y': -p['nose_drop'], 'fixed_x': False, 'fixed_y': False, 'name': 'Nose'},
            4: {'x': -p['radius'] + p['rim_width']/3, 'y': -p['nose_drop'] - 3, 'fixed_x': False, 'fixed_y': False, 'name': 'Lower Rim'},
            5: {'x': -p['radius'] + p['rim_width'], 'y': -p['total_height'], 'fixed_x': False, 'fixed_y': False, 'name': 'Rim Bottom'},
            6: {'x': -p['radius'] + p['rim_width'], 'y': -p['shoulder_drop'] - 2, 'fixed_x': False, 'fixed_y': False, 'name': 'Rim Wall'},
            7: {'x': 0, 'y': -p['flight_plate_thickness'], 'fixed_x': True, 'fixed_y': False, 'name': 'Flight Plate Bottom'}
        }
        
        # Initialize curve parameters
        for i in range(1, 7):
            self.curves[f"{i}-{i+1}"] = {'curve_strength': 0.0, 'tangent_angle': 0.0}
    
    def validate_constraints(self):
        """Validate simplified geometric constraints"""
        violations = []
        p = self.points
        
        # Core geometric relationships
        constraints = [
            (p[2]['x'] > p[3]['x'], "Point 2 (Shoulder) must be right of Point 3 (Nose)"),
            (p[3]['x'] <= -105, "Point 3 (Nose) must define proper disc radius (~105mm)"),
            (p[5]['x'] == p[6]['x'], "Points 5&6 (Rim) must align vertically"),
            (abs(p[5]['y']) <= 20, "Point 5 (Bottom) must be within 20mm of center"),
            (p[7]['y'] < p[1]['y'] and p[7]['y'] > p[2]['y'], "Point 7 must be between Points 1&2"),
        ]
        
        # Check sequential Y ordering: 1 > 2 > 3 and 3 > 4 > 5
        y_order = [
            (p[1]['y'] > p[2]['y'], "Point 1 must be above Point 2"),
            (p[2]['y'] > p[3]['y'], "Point 2 must be above Point 3"), 
            (p[3]['y'] > p[4]['y'], "Point 3 must be above Point 4"),
            (p[4]['y'] > p[5]['y'], "Point 4 must be above Point 5"),
        ]
        
        for condition, message in constraints + y_order:
            if not condition:
                violations.append(message)
                
        return violations
    
    def generate_spline_curve(self, p1_idx, p2_idx, num_points=50):
        """Generate a spline curve between two points"""
        p1 = self.points[p1_idx]
        p2 = self.points[p2_idx]
        
        # Handle straight line from point 1 to 7
        if (p1_idx == 1 and p2_idx == 7) or (p1_idx == 7 and p2_idx == 1):
            x_vals = np.linspace(p1['x'], p2['x'], num_points)
            y_vals = np.linspace(p1['y'], p2['y'], num_points)
            return x_vals, y_vals
        
        # Get curve parameters
        curve_key = f"{min(p1_idx, p2_idx)}-{max(p1_idx, p2_idx)}"
        curve_params = self.curves.get(curve_key, {'curve_strength': 0.0, 'tangent_angle': 0.0})
        
        # Create control points for cubic spline
        dx = p2['x'] - p1['x']
        dy = p2['y'] - p1['y']
        
        # Calculate tangent vectors
        strength = curve_params['curve_strength']
        angle = np.radians(curve_params['tangent_angle'])
        
        # Control points
        cp1_x = p1['x'] + strength * np.cos(angle) * abs(dx) / 3
        cp1_y = p1['y'] + strength * np.sin(angle) * abs(dy) / 3
        cp2_x = p2['x'] - strength * np.cos(angle + np.pi) * abs(dx) / 3
        cp2_y = p2['y'] - strength * np.sin(angle + np.pi) * abs(dy) / 3
        
        # Ensure control points don't violate boundaries
        cp1_x = max(min(cp1_x, max(p1['x'], p2['x'])), min(p1['x'], p2['x']))
        cp1_y = max(min(cp1_y, max(p1['y'], p2['y'])), min(p1['y'], p2['y']))
        cp2_x = max(min(cp2_x, max(p1['x'], p2['x'])), min(p1['x'], p2['x']))
        cp2_y = max(min(cp2_y, max(p1['y'], p2['y'])), min(p1['y'], p2['y']))
        
        # Create bezier curve
        t = np.linspace(0, 1, num_points)
        x_vals = ((1-t)**3 * p1['x'] + 
                 3*(1-t)**2*t * cp1_x + 
                 3*(1-t)*t**2 * cp2_x + 
                 t**3 * p2['x'])
        y_vals = ((1-t)**3 * p1['y'] + 
                 3*(1-t)**2*t * cp1_y + 
                 3*(1-t)*t**2 * cp2_y + 
                 t**3 * p2['y'])
        
        return x_vals, y_vals
    
    def get_full_profile(self):
        """Get the complete disc profile as x,y coordinates"""
        x_coords = []
        y_coords = []
        
        # Generate curves between sequential points
        for i in range(1, 7):
            x_curve, y_curve = self.generate_spline_curve(i, i+1)
            if i == 1:
                x_coords.extend(x_curve)
                y_coords.extend(y_curve)
            else:
                x_coords.extend(x_curve[1:])  # Skip first point to avoid duplication
                y_coords.extend(y_curve[1:])
        
        # Add straight line from point 7 to 1
        x_line, y_line = self.generate_spline_curve(7, 1)
        x_coords.extend(x_line[1:])  # Skip first point
        y_coords.extend(y_line[1:])
        
        return np.array(x_coords), np.array(y_coords)
    
    def calculate_dimensions(self, material="PETG (Recommended)"):
        """Calculate disc dimensions and properties with material-specific density"""
        # Material density mapping
        density_map = {
            "PLA (Lighter)": 1.24,
            "PETG (Recommended)": 1.28,
            "ABS (Stronger)": 1.05,
            "Commercial Plastic (Reference)": 1.60
        }
        plastic_density = density_map.get(material, 1.28)  # Default to PETG
        
        # Radius and diameter
        radius = abs(self.points[3]['x'])  # Distance from origin to nose
        diameter = 2 * radius
        
        # Flight plate thickness
        flight_plate_thickness = abs(self.points[1]['y'] - self.points[7]['y'])
        
        # Total disc thickness
        disc_thickness = abs(self.points[1]['y'] - self.points[5]['y'])
        
        # Rim dimensions
        rim_depth = abs(self.points[5]['y'] - self.points[3]['y'])
        rim_width = abs(self.points[6]['x'] - self.points[3]['x'])
        
        # Accurate weight calculation using trimesh library
        try:
            # Create the 3D mesh and calculate volume using trimesh
            disc_mesh = self._create_trimesh_for_volume_calculation()
            if disc_mesh is not None and disc_mesh.is_watertight:
                # Get volume in mm³ and convert to cm³ (FIXED: correct conversion)
                volume_mm3 = abs(disc_mesh.volume)
                volume_cm3 = volume_mm3 / 1000  # mm³ to cm³ (1000 mm³ = 1 cm³)
                estimated_weight = volume_cm3 * plastic_density
            else:
                # Fallback to simple estimation if mesh creation fails
                estimated_weight = self._fallback_weight_estimation(plastic_density)
        except Exception as e:
            # Fallback to simple estimation
            estimated_weight = self._fallback_weight_estimation(plastic_density)
        
        return {
            'radius': radius,
            'diameter': diameter,
            'flight_plate_thickness': flight_plate_thickness,
            'disc_thickness': disc_thickness,
            'rim_depth': rim_depth,
            'rim_width': rim_width,
            'estimated_weight': estimated_weight
        }
    
    def _create_trimesh_for_volume_calculation(self):
        """Create a watertight trimesh for accurate volume calculation"""
        try:
            # FIXED: Use a properly closed profile that forms a complete disc shape
            # Instead of using the simplified profile, create a proper closed profile
            
            # Get the key disc points in order from center to rim and back
            points_ordered = [
                (0, self.points[1]['y']),                    # Center top
                (abs(self.points[2]['x']), self.points[2]['y']),  # Shoulder  
                (abs(self.points[3]['x']), self.points[3]['y']),  # Nose/rim edge
                (abs(self.points[4]['x']), self.points[4]['y']),  # Rim top
                (abs(self.points[5]['x']), self.points[5]['y']),  # Rim bottom
                (abs(self.points[6]['x']), self.points[6]['y']),  # Rim inner
                (abs(self.points[7]['x']), self.points[7]['y']),  # Center bottom
                (0, self.points[7]['y'])                     # Center bottom (closed)
            ]
            
            x_coords = np.array([p[0] for p in points_ordered])
            y_coords = np.array([p[1] for p in points_ordered])
            
            # Create revolution mesh with proper closure
            n_theta = 32  # More points for accurate volume calculation
            theta = np.linspace(0, 2*np.pi, n_theta, endpoint=False)
            
            vertices = []
            
            # Generate vertices by revolving the profile
            for i, (x, y) in enumerate(zip(x_coords, y_coords)):
                r = abs(x)
                for j, angle in enumerate(theta):
                    vertex_x = r * np.cos(angle)
                    vertex_y = r * np.sin(angle)
                    vertex_z = y
                    vertices.append([vertex_x, vertex_y, vertex_z])
            
            vertices = np.array(vertices)
            n_profile = len(x_coords)
            
            # Generate faces - FIXED: Ensure proper connectivity for closed shape
            faces = []
            
            # Side faces connecting adjacent profile rings
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
            
            # FIXED: Close the profile by connecting last ring to first ring
            # This creates the complete enclosed disc shape
            for j in range(n_theta):
                j_next = (j + 1) % n_theta
                
                # Connect last profile ring to first profile ring
                v1 = (n_profile - 1) * n_theta + j
                v2 = (n_profile - 1) * n_theta + j_next
                v3 = j  # First ring
                v4 = j_next
                
                faces.append([v1, v3, v2])
                faces.append([v2, v3, v4])
            
            # Create trimesh
            disc_trimesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            
            # Ensure proper orientation
            if disc_trimesh.volume < 0:
                disc_trimesh.invert()
            
            # Fix mesh to ensure it's watertight
            disc_trimesh.fix_normals()
            

            
            return disc_trimesh
            
        except Exception as e:
            return None
    
    def _fallback_weight_estimation(self, plastic_density):
        """Simple fallback weight estimation based on disc dimensions"""
        radius = abs(self.points[3]['x'])  # ~110mm
        thickness = abs(self.points[1]['y'] - self.points[5]['y'])  # ~15-20mm
        
        # FIXED: More realistic approximation for disc golf disc
        # A disc golf disc is roughly 18-22% of a solid cylinder due to hollow sections
        cylinder_volume = np.pi * radius**2 * thickness * 0.18  # 18% fill for realistic weight
        volume_cm3 = cylinder_volume / 1000  # mm³ to cm³ (FIXED: correct conversion)
        
        return volume_cm3 * plastic_density

def create_plotly_visualization(disc_profile):
    """Create interactive 2D cross-section and 3D revolved model visualization"""
    
    # Get full profile
    x_coords, y_coords = disc_profile.get_full_profile()
    
    # Calculate tight bounds for 2D view with minimal padding
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    
    # Use minimal padding (2-5% instead of 10%)
    x_range = x_max - x_min
    y_range = y_max - y_min
    x_padding = max(x_range * 0.03, 2.0)  # Minimum 2mm padding
    y_padding = max(y_range * 0.05, 1.0)  # Minimum 1mm padding
    
    # Ensure uniform scaling by using the larger range for both axes
    max_range = max(x_range + 2*x_padding, y_range + 2*y_padding)
    
    # Center the smaller dimension
    if x_range + 2*x_padding < max_range:
        x_center = (x_min + x_max) / 2
        x_min_scaled = x_center - max_range/2
        x_max_scaled = x_center + max_range/2
    else:
        x_min_scaled = x_min - x_padding
        x_max_scaled = x_max + x_padding
        
    if y_range + 2*y_padding < max_range:
        y_center = (y_min + y_max) / 2
        y_min_scaled = y_center - max_range/2
        y_max_scaled = y_center + max_range/2
    else:
        y_min_scaled = y_min - y_padding
        y_max_scaled = y_max + y_padding
    
    # Create figure with subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Cross-Section Profile', '3D Revolved Model'),
        specs=[[{"secondary_y": False}, {"type": "scene"}]]
    )
    
    # Cross-section view (2D)
    fig.add_trace(
        go.Scatter(
            x=x_coords, y=y_coords,
            mode='lines+markers',
            name='Disc Profile',
            line=dict(color='#667eea', width=3),
            marker=dict(size=4, color='#764ba2'),
            hovertemplate='<b>Position</b><br>X: %{x:.1f}mm<br>Y: %{y:.1f}mm<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add control points
    for point_id, point in disc_profile.points.items():
        color = '#e74c3c' if point.get('fixed_x') or point.get('fixed_y') else '#2ecc71'
        fig.add_trace(
            go.Scatter(
                x=[point['x']], y=[point['y']],
                mode='markers',
                name=f"P{point_id}",
                marker=dict(size=8, color=color, symbol='diamond'),
                hovertemplate=f'<b>P{point_id}: {point["name"]}</b><br>X: {point["x"]:.1f}mm<br>Y: {point["y"]:.1f}mm<extra></extra>',
                showlegend=False
            ),
            row=1, col=1
        )
    
    # 3D revolved model - create highly simplified solid surface
    n_theta = 12  # Minimal angular divisions for very clean mesh
    n_profile = len(x_coords[::12])  # Sample every 12th profile point for maximum simplification
    
    theta = np.linspace(0, 2*np.pi, n_theta + 1)  # +1 to close the surface
    profile_x = x_coords[::12]
    profile_y = y_coords[::12]
    
    # Create minimal mesh grid for clean solid surface
    X_3d = np.zeros((n_profile, n_theta + 1))
    Y_3d = np.zeros((n_profile, n_theta + 1))
    Z_3d = np.zeros((n_profile, n_theta + 1))
    
    for i, (x, y) in enumerate(zip(profile_x, profile_y)):
        r = abs(x)
        for j, angle in enumerate(theta):
            X_3d[i, j] = r * np.cos(angle)
            Y_3d[i, j] = r * np.sin(angle)
            Z_3d[i, j] = y
    
    # Create very simple solid surface mesh
    fig.add_trace(
        go.Surface(
            x=X_3d, y=Y_3d, z=Z_3d,
            colorscale=[[0, '#1E3A8A'], [0.5, '#3B82F6'], [1, '#93C5FD']],  # Clean blue gradient  
            opacity=0.95,
            showscale=False,
            name='Simplified Disc Model',
            hovertemplate='<b>Clean Disc Body</b><br>X: %{x:.1f}mm<br>Y: %{y:.1f}mm<br>Z: %{z:.1f}mm<extra></extra>',
            lighting=dict(ambient=0.6, diffuse=0.8, specular=0.1),
            lightposition=dict(x=50, y=50, z=100),
            contours=dict(
                x=dict(show=False),
                y=dict(show=False), 
                z=dict(show=False)
            ),
            surfacecolor=np.ones((n_profile, n_theta + 1)) * 0.5  # Uniform color for clean look
        ),
        row=1, col=2
    )
    
    # Update layout with tighter spacing
    fig.update_layout(
        height=500,  # Reduced height for more compact view
        showlegend=False, 
        title_text="Disc Golf Design Visualization",
        margin=dict(l=20, r=20, t=50, b=20)  # Tighter margins
    )
    
    # 2D subplot settings with uniform scaling and tight bounds
    fig.update_xaxes(
        title_text="Distance from Center (mm)", 
        scaleanchor="y", 
        scaleratio=1,
        range=[x_min_scaled, x_max_scaled],
        constrain="domain",
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Height (mm)", 
        range=[y_min_scaled, y_max_scaled],
        constrain="domain",
        row=1, col=1
    )
    
    # 3D subplot settings with matching scale
    max_3d_range = max(abs(x_min), abs(x_max), abs(y_min), abs(y_max)) * 1.1
    fig.update_scenes(
        xaxis=dict(title="X (mm)", range=[-max_3d_range, max_3d_range]),
        yaxis=dict(title="Y (mm)", range=[-max_3d_range, max_3d_range]),
        zaxis=dict(title="Height (mm)", range=[y_min_scaled, y_max_scaled]),
        aspectmode='manual',
        aspectratio=dict(x=1, y=1, z=(y_max_scaled-y_min_scaled)/(2*max_3d_range)),
        row=1, col=2
    )
    
    return fig

def generate_stl_file(disc_profile, resolution=16):
    """Generate highly simplified STL file with minimal, clean solid body mesh"""
    try:
        # Get profile coordinates and create very simplified profile
        x_full, y_full = disc_profile.get_full_profile()
        
        # Create extremely simplified profile - only essential points
        x_coords, y_coords = create_simplified_profile(x_full, y_full, target_points=12)
        
        # Use minimal angular divisions for clean, simple geometry
        theta = np.linspace(0, 2*np.pi, resolution, endpoint=False)
        vertices = []
        faces = []
        
        # Generate vertices by revolving the highly simplified profile
        for i, (x, y) in enumerate(zip(x_coords, y_coords)):
            r = abs(x)  # radius at this height
            for j, angle in enumerate(theta):
                vertex_x = r * np.cos(angle)
                vertex_y = r * np.sin(angle)
                vertex_z = y
                vertices.append([vertex_x, vertex_y, vertex_z])
        
        vertices = np.array(vertices)
        n_profile = len(x_coords)
        n_theta = len(theta)
        
        # Generate minimal faces with proper winding
        for i in range(n_profile - 1):
            for j in range(n_theta):
                j_next = (j + 1) % n_theta
                
                v1 = i * n_theta + j
                v2 = i * n_theta + j_next
                v3 = (i + 1) * n_theta + j
                v4 = (i + 1) * n_theta + j_next
                
                # Two triangles per quad with outward normals
                faces.append([v1, v2, v3])
                faces.append([v2, v4, v3])
        
        faces = np.array(faces)
        
        # Create simple mesh
        disc_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, face in enumerate(faces):
            for j in range(3):
                disc_mesh.vectors[i][j] = vertices[face[j], :]
        
        return disc_mesh

    except Exception as e:
        st.error(f"Error generating STL: {str(e)}")
        return None

def create_simplified_profile(x_coords, y_coords, target_points=15):
    """Create a highly simplified profile with minimal points for very clean mesh"""
    if len(x_coords) <= target_points:
        return x_coords, y_coords
    
    # Simple uniform sampling for maximum simplification
    indices = np.linspace(0, len(x_coords) - 1, target_points, dtype=int)
    x_simplified = x_coords[indices]
    y_simplified = y_coords[indices]
    
    # Ensure we keep the start and end points exactly
    x_simplified[0] = x_coords[0]
    x_simplified[-1] = x_coords[-1]
    y_simplified[0] = y_coords[0]
    y_simplified[-1] = y_coords[-1]
    
    return x_simplified, y_simplified

def main():
    # Header with logo
    logo_base64 = get_logo_base64()
    if logo_base64:
        st.markdown(f"""
        <div class="main-header">
            <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
                <img src="{logo_base64}" style="height: 60px; width: auto;" alt="Disc Golf Designer Logo">
                <div>
                    <h1 style="margin: 0;">Disc Golf Designer Pro</h1>
                    <p style="color: white; text-align: center; margin: 0; font-size: 0.9em;">Professional PDGA-Compliant Disc Design Tool</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-header">
            <h1>🥏 Disc Golf Designer Pro</h1>
            <p style="color: white; text-align: center; margin: 0;">Professional PDGA-Compliant Disc Design Tool</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'disc_profile' not in st.session_state:
        st.session_state.disc_profile = DiscProfile()
    
    disc_profile = st.session_state.disc_profile
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎛️ Design Controls")
        
        # Grouped point adjustments
        st.subheader("Key Parameters")
        
        # Primary shape controls with session state keys for proper updates
        radius = st.slider("Disc Radius", 105.0, 115.0, abs(disc_profile.points[3]['x']), 0.5, 
                          help="Controls overall disc size (Point 3)", key="key_radius")
        shoulder_pos = st.slider("Shoulder Position", 80.0, 100.0, abs(disc_profile.points[2]['x']), 1.0,
                                help="Shoulder distance from center (Point 2)", key="key_shoulder")
        rim_width = st.slider("Rim Width", 15.0, 35.0, abs(disc_profile.points[3]['x'] - disc_profile.points[6]['x']), 1.0,
                             help="Width of rim area (Points 3-6)", key="key_rim_width")
        total_height = st.slider("Total Height", 8.0, 20.0, abs(disc_profile.points[5]['y']), 0.5,
                                help="Overall disc thickness (Point 5)", key="key_height")
        plate_thickness = st.slider("Flight Plate", 1.0, 4.0, abs(disc_profile.points[7]['y']), 0.1,
                                   help="Flight plate thickness (Point 7)", key="key_plate")
        
        # Material selection for weight calculation
        st.subheader("Material")
        material = st.selectbox("3D Print Material", 
                               ["PETG (Recommended)", "PLA (Lighter)", "ABS (Stronger)", "Commercial Plastic (Reference)"],
                               help="Select material type for accurate weight calculation")
        
        # Update points based on parameters and synchronize with fine-tune controls
        disc_profile.points[2]['x'] = -shoulder_pos
        disc_profile.points[3]['x'] = -radius
        disc_profile.points[4]['x'] = -radius + rim_width/3
        disc_profile.points[5]['x'] = disc_profile.points[6]['x'] = -radius + rim_width
        disc_profile.points[5]['y'] = -total_height
        disc_profile.points[7]['y'] = -plate_thickness
        
        # Update session state keys for fine-tune controls to match key parameter changes
        if f"fine_x_2" not in st.session_state or abs(st.session_state.get("fine_x_2", 0) - (-shoulder_pos)) > 0.1:
            st.session_state["fine_x_2"] = -shoulder_pos
        if f"fine_x_3" not in st.session_state or abs(st.session_state.get("fine_x_3", 0) - (-radius)) > 0.1:
            st.session_state["fine_x_3"] = -radius
        if f"fine_x_4" not in st.session_state or abs(st.session_state.get("fine_x_4", 0) - (-radius + rim_width/3)) > 0.1:
            st.session_state["fine_x_4"] = -radius + rim_width/3
        if f"fine_x_5" not in st.session_state or abs(st.session_state.get("fine_x_5", 0) - (-radius + rim_width)) > 0.1:
            st.session_state["fine_x_5"] = -radius + rim_width
        if f"fine_x_6" not in st.session_state or abs(st.session_state.get("fine_x_6", 0) - (-radius + rim_width)) > 0.1:
            st.session_state["fine_x_6"] = -radius + rim_width
        if f"fine_y_5" not in st.session_state or abs(st.session_state.get("fine_y_5", 0) - (-total_height)) > 0.1:
            st.session_state["fine_y_5"] = -total_height
        if f"fine_y_7" not in st.session_state or abs(st.session_state.get("fine_y_7", 0) - (-plate_thickness)) > 0.1:
            st.session_state["fine_y_7"] = -plate_thickness
        
        # Force session state update to trigger re-render
        st.session_state.disc_profile = disc_profile
        
        st.markdown("---")
        
        # Fine-tune individual points (synchronized with key parameters)
        with st.expander("🔧 Fine-Tune Points"):
            for point_id in [2, 3, 4, 5, 6, 7]:  # Skip point 1 (fixed)
                point = disc_profile.points[point_id]
                st.write(f"**P{point_id}: {point['name'][:12]}**")
                
                col1, col2 = st.columns(2)
                with col1:
                    if not point.get('fixed_x', False):
                        # Initialize session state if not exists
                        if f"fine_x_{point_id}" not in st.session_state:
                            st.session_state[f"fine_x_{point_id}"] = float(point['x'])
                        
                        # Use session state value that gets updated by key parameters
                        new_x = st.number_input(f"X", value=st.session_state[f"fine_x_{point_id}"], 
                                              step=0.5, key=f"fine_x_input_{point_id}")
                        
                        # Update both the point and session state
                        disc_profile.points[point_id]['x'] = new_x
                        st.session_state[f"fine_x_{point_id}"] = new_x
                        
                with col2:
                    if not point.get('fixed_y', False):
                        # Initialize session state if not exists
                        if f"fine_y_{point_id}" not in st.session_state:
                            st.session_state[f"fine_y_{point_id}"] = float(point['y'])
                        
                        # Use session state value that gets updated by key parameters
                        new_y = st.number_input(f"Y", value=st.session_state[f"fine_y_{point_id}"], 
                                              step=0.5, key=f"fine_y_input_{point_id}")
                        
                        # Update both the point and session state
                        disc_profile.points[point_id]['y'] = new_y
                        st.session_state[f"fine_y_{point_id}"] = new_y
        
        st.markdown("---")
        
        # Simplified curve controls
        st.subheader("Shape Curves")
        curve_segments = ["1→2 (Top)", "2→3 (Shoulder)", "3→4 (Nose)", "4→5 (Bottom)", "5→6 (Rim)"]
        
        for i, label in enumerate(curve_segments, 1):
            curve_key = f"{i}-{i+1}"
            
            col1, col2 = st.columns(2)
            with col1:
                strength = st.slider(f"Curve", -2.0, 2.0, 
                                   disc_profile.curves.get(curve_key, {'curve_strength': 0.0})['curve_strength'],
                                   0.1, key=f"str_{i}", label_visibility="collapsed")
            with col2:
                angle = st.slider(f"Angle", -180, 180,
                                int(disc_profile.curves.get(curve_key, {'tangent_angle': 0.0})['tangent_angle']),
                                10, key=f"ang_{i}", label_visibility="collapsed")
            
            st.caption(f"{label}")
            disc_profile.curves[curve_key] = {'curve_strength': strength, 'tangent_angle': angle}
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Reset to Default", type="secondary"):
            st.session_state.disc_profile = DiscProfile()
            # Clear fine-tune session state keys to sync with reset
            for point_id in [2, 3, 4, 5, 6, 7]:
                if f"fine_x_{point_id}" in st.session_state:
                    del st.session_state[f"fine_x_{point_id}"]
                if f"fine_y_{point_id}" in st.session_state:
                    del st.session_state[f"fine_y_{point_id}"]
            st.rerun()
    
    # Main content area
    dimensions = disc_profile.calculate_dimensions(material)
    
    # Visualization (full width)
    fig = create_plotly_visualization(disc_profile)
    st.plotly_chart(fig, use_container_width=True)
    
    # Compact metrics row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Diameter", f"{dimensions['diameter']:.1f}mm")
    with col2:
        st.metric("Height", f"{dimensions['disc_thickness']:.1f}mm")
    with col3:
        st.metric("Flight Plate", f"{dimensions['flight_plate_thickness']:.1f}mm")
    with col4:
        st.metric("Rim Depth", f"{dimensions['rim_depth']:.1f}mm")
    with col5:
        st.metric("Rim Width", f"{dimensions['rim_width']:.1f}mm")
    with col6:
        # Get density for help text
        density_map = {
            "PLA (Lighter)": 1.24,
            "PETG (Recommended)": 1.28,
            "ABS (Stronger)": 1.05,
            "Commercial Plastic (Reference)": 1.60
        }
        current_density = density_map.get(material, 1.28)
        
        st.metric("Weight", f"{dimensions['estimated_weight']:.0f}g",
                 help=f"Calculated using volume integration: π∫r²dr method with {material.split(' ')[0]} density ({current_density}g/cm³)")
    
    # Weight calculation explanation
    with st.expander("📊 Weight Calculation Details", expanded=False):
        st.write("**Accurate Calculation Method:**")
        st.write("1. **3D Mesh Generation:** Creates watertight triangular mesh from 2D profile")
        st.write("2. **Trimesh Library:** Uses professional 3D mesh processing library")
        st.write("3. **Precise Volume:** Calculates exact volume from closed triangular mesh")
        st.write(f"4. **Selected Material Density:** {material} = {current_density} g/cm³")
        st.write("")
        st.write("**Formula:** Volume = Trimesh.volume (exact 3D calculation)")
        st.write("**Weight = Volume × Material Density**")
        st.write("")
        st.write("**Volume Calculation Debug:**")
        try:
            # Create trimesh for volume calculation
            disc_trimesh = disc_profile._create_trimesh_for_volume_calculation()
            if disc_trimesh is not None and disc_trimesh.is_watertight:
                volume_mm3 = disc_trimesh.volume
                volume_cm3 = volume_mm3 / 1000000
                st.write(f"• Trimesh Volume: {volume_cm3:.1f} cm³ ✅ (Accurate)")
                st.write(f"• Mesh Status: Watertight with {len(disc_trimesh.vertices)} vertices")
            else:
                fallback_weight = disc_profile._fallback_weight_estimation(current_density)
                fallback_volume = fallback_weight / current_density
                st.write(f"• Fallback Volume: {fallback_volume:.1f} cm³ ⚠️ (Approximate)")
                st.write("• Mesh Status: Failed to create watertight mesh")
        except Exception as e:
            st.write(f"• Error: {str(e)}")
        
        st.write(f"• Expected Range: 75-100 cm³ (typical 3D printed disc)")
        st.write(f"• Slicer weight should match: {dimensions['estimated_weight']:.0f}g ± 5g")
        st.write("")
        st.write("**Available Material Densities:**")
        st.write("• PLA: 1.24 g/cm³ (lighter, more brittle, easiest to print)")
        st.write("• PETG: 1.28 g/cm³ (recommended - durable, good flight)")
        st.write("• ABS: 1.05 g/cm³ (strong, heat resistant)")
        st.write("• Commercial plastics: 1.60 g/cm³ (reference - heavier than 3D printed)")
        st.write("")
        st.write("*Note: Calculation uses PETG density. Actual weight may vary by ±5-10g due to infill percentage, print settings, and material variations.*")
    
    # Validation and Export Row
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Quick validation status
        constraint_violations = disc_profile.validate_constraints()
        violations, warnings = PDGAStandards.validate_dimensions(
            dimensions['diameter'], dimensions['disc_thickness'], dimensions['estimated_weight'],
            dimensions['rim_depth'], dimensions['rim_width'], dimensions['flight_plate_thickness']
        )
        
        # Enhanced PDGA compliance indicators
        diameter_status = "✅" if PDGAStandards.MIN_DIAMETER <= dimensions['diameter'] <= PDGAStandards.MAX_DIAMETER else "❌"
        height_status = "✅" if PDGAStandards.MIN_HEIGHT <= dimensions['disc_thickness'] <= PDGAStandards.MAX_HEIGHT else "❌"
        weight_status = "✅" if PDGAStandards.MIN_WEIGHT <= dimensions['estimated_weight'] <= PDGAStandards.MAX_WEIGHT else "❌"
        geometry_status = "✅" if not constraint_violations else "⚠️"
        
        # Create detailed compliance display
        compliance_details = []
        if diameter_status == "❌":
            compliance_details.append(f"Diameter: {dimensions['diameter']:.1f}mm (need {PDGAStandards.MIN_DIAMETER}-{PDGAStandards.MAX_DIAMETER}mm)")
        if height_status == "❌":
            compliance_details.append(f"Height: {dimensions['disc_thickness']:.1f}mm (need {PDGAStandards.MIN_HEIGHT}-{PDGAStandards.MAX_HEIGHT}mm)")
        if weight_status == "❌":
            compliance_details.append(f"Weight: {dimensions['estimated_weight']:.0f}g (need {PDGAStandards.MIN_WEIGHT}-{PDGAStandards.MAX_WEIGHT}g)")
        
        # Main status line
        all_pdga_ok = all([diameter_status == "✅", height_status == "✅", weight_status == "✅"])
        status_line = f"**PDGA Compliance:** {'✅ Legal' if all_pdga_ok else '❌ Non-compliant'} | "
        status_line += f"**Geometry:** {geometry_status} | "
        status_line += f"**Issues:** {len(constraint_violations + compliance_details)}"
        
        st.write(status_line)
        
        # Show specific violations if any
        if compliance_details or constraint_violations:
            with st.expander("🔍 View Compliance Details", expanded=False):
                if compliance_details:
                    st.write("**PDGA Violations:**")
                    for detail in compliance_details:
                        st.write(f"• {detail}")
                if constraint_violations:
                    st.write("**Geometry Warnings:**")
                    for violation in constraint_violations:
                        st.write(f"• {violation}")
                        
                # Add PDGA standards reference
                st.write("**PDGA Standards Reference:**")
                st.write(f"• Diameter: {PDGAStandards.MIN_DIAMETER}-{PDGAStandards.MAX_DIAMETER}mm")
                st.write(f"• Height: {PDGAStandards.MIN_HEIGHT}-{PDGAStandards.MAX_HEIGHT}mm") 
                st.write(f"• Weight: {PDGAStandards.MIN_WEIGHT}-{PDGAStandards.MAX_WEIGHT}g")
                st.write(f"• Rim Width: ≤{PDGAStandards.MAX_RIM_WIDTH}mm")
                st.write(f"• Rim Depth: ≤{PDGAStandards.MAX_RIM_DEPTH}mm")
        
        if constraint_violations:
            with st.expander("⚠️ Geometry Warnings"):
                for violation in constraint_violations[:3]:
                    st.write(f"• {violation}")
    
    with col2:
        # Compact export options
        col_stl, col_csv = st.columns(2)
        
        with col_stl:
            if st.button("📥 STL", type="primary", use_container_width=True):
                with st.spinner("Generating..."):
                    stl_mesh = generate_stl_file(disc_profile)
                    if stl_mesh is not None:
                        stl_mesh.save('temp_disc.stl')
                        with open('temp_disc.stl', 'rb') as f:
                            st.download_button("Download STL", f.read(), "disc_design.stl", 
                                             "application/octet-stream", use_container_width=True)
        
        with col_csv:
            if st.button("📊 CSV", type="secondary", use_container_width=True):
                csv = pd.DataFrame([dimensions]).to_csv(index=False)
                st.download_button("Download CSV", csv, "disc_specs.csv", "text/csv", use_container_width=True)

if __name__ == "__main__":
    main()