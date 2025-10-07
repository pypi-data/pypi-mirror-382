"""
Ctypes wrapper for Visualizer C++ bindings.

This module provides low-level ctypes bindings to interface with 
the native Helios Visualizer plugin via the C++ wrapper layer.
"""

import ctypes
from typing import List, Optional

from ..plugins import helios_lib
from ..exceptions import check_helios_error

# Define the UVisualizer struct
class UVisualizer(ctypes.Structure):
    pass

# Import UContext from main wrapper to avoid type conflicts
from .UContextWrapper import UContext

# Try to set up Visualizer function prototypes
try:
    # Visualizer creation and destruction
    helios_lib.createVisualizer.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_bool]
    helios_lib.createVisualizer.restype = ctypes.POINTER(UVisualizer)
    
    # Add errcheck to automatically handle errors and nulls
    def _check_visualizer_creation(result, func, args):
        if _ERROR_MANAGEMENT_AVAILABLE:
            check_helios_error(helios_lib.getLastErrorCode, helios_lib.getLastErrorMessage)
        if not result:
            raise RuntimeError(
                "Failed to create Visualizer. This may indicate:\n"
                "1. OpenGL/graphics initialization problems in headless environments\n"
                "2. Missing graphics drivers or display support\n" 
                "3. Insufficient system resources for graphics context creation\n"
                "4. XQuartz or display server configuration issues on macOS/Linux"
            )
        return result
    
    helios_lib.createVisualizer.errcheck = _check_visualizer_creation

    helios_lib.createVisualizerWithAntialiasing.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_bool]
    helios_lib.createVisualizerWithAntialiasing.restype = ctypes.POINTER(UVisualizer)
    helios_lib.createVisualizerWithAntialiasing.errcheck = _check_visualizer_creation

    helios_lib.destroyVisualizer.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.destroyVisualizer.restype = None

    # Context geometry building
    helios_lib.buildContextGeometry.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(UContext)]
    helios_lib.buildContextGeometry.restype = None

    helios_lib.buildContextGeometryUUIDs.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(UContext), ctypes.POINTER(ctypes.c_uint32), ctypes.c_size_t]
    helios_lib.buildContextGeometryUUIDs.restype = None

    # Visualization functions
    helios_lib.plotInteractive.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.plotInteractive.restype = None

    helios_lib.plotUpdate.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.plotUpdate.restype = None

    helios_lib.printWindow.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_char_p]
    helios_lib.printWindow.restype = None

    helios_lib.closeWindow.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.closeWindow.restype = None

    # Camera control
    helios_lib.setCameraPosition.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setCameraPosition.restype = None

    helios_lib.setCameraPositionSpherical.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setCameraPositionSpherical.restype = None

    # Scene configuration
    helios_lib.setBackgroundColor.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setBackgroundColor.restype = None

    helios_lib.setLightDirection.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setLightDirection.restype = None

    helios_lib.setLightingModel.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_uint32]
    helios_lib.setLightingModel.restype = None

    # Primitive coloring functions
    helios_lib.colorContextPrimitivesByData.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_char_p]
    helios_lib.colorContextPrimitivesByData.restype = None
    
    helios_lib.colorContextPrimitivesByDataUUIDs.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
    helios_lib.colorContextPrimitivesByDataUUIDs.restype = None

    # Camera Control Functions
    helios_lib.setCameraFieldOfView.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_float]
    helios_lib.setCameraFieldOfView.restype = None

    helios_lib.getCameraPosition.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
    helios_lib.getCameraPosition.restype = None

    helios_lib.getBackgroundColor.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float)]
    helios_lib.getBackgroundColor.restype = None

    # Lighting Control Functions
    helios_lib.setLightIntensityFactor.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_float]
    helios_lib.setLightIntensityFactor.restype = None

    # Window and Display Functions
    helios_lib.getWindowSize.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
    helios_lib.getWindowSize.restype = None

    helios_lib.getFramebufferSize.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
    helios_lib.getFramebufferSize.restype = None

    helios_lib.printWindowDefault.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.printWindowDefault.restype = None

    helios_lib.displayImageFromPixels.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint, ctypes.c_uint]
    helios_lib.displayImageFromPixels.restype = None

    helios_lib.displayImageFromFile.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_char_p]
    helios_lib.displayImageFromFile.restype = None

    # Window Data Access Functions
    helios_lib.getWindowPixelsRGB.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_uint)]
    helios_lib.getWindowPixelsRGB.restype = None

    helios_lib.getDepthMap.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.POINTER(ctypes.c_float)), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
    helios_lib.getDepthMap.restype = None

    helios_lib.plotDepthMap.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.plotDepthMap.restype = None

    # Geometry Management Functions
    helios_lib.clearGeometry.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.clearGeometry.restype = None

    helios_lib.clearContextGeometry.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.clearContextGeometry.restype = None

    helios_lib.deleteGeometry.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_uint]
    helios_lib.deleteGeometry.restype = None

    helios_lib.updateContextPrimitiveColors.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.updateContextPrimitiveColors.restype = None

    # Coordinate Axes and Grid Functions
    helios_lib.addCoordinateAxes.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.addCoordinateAxes.restype = None

    helios_lib.addCoordinateAxesCustom.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_char_p]
    helios_lib.addCoordinateAxesCustom.restype = None

    helios_lib.disableCoordinateAxes.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.disableCoordinateAxes.restype = None

    helios_lib.addGridWireFrame.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int)]
    helios_lib.addGridWireFrame.restype = None

    # Colorbar Control Functions
    helios_lib.enableColorbar.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.enableColorbar.restype = None

    helios_lib.disableColorbar.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.disableColorbar.restype = None

    helios_lib.setColorbarPosition.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setColorbarPosition.restype = None

    helios_lib.setColorbarSize.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setColorbarSize.restype = None

    helios_lib.setColorbarRange.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_float, ctypes.c_float]
    helios_lib.setColorbarRange.restype = None

    helios_lib.setColorbarTicks.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float), ctypes.c_uint]
    helios_lib.setColorbarTicks.restype = None

    helios_lib.setColorbarTitle.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_char_p]
    helios_lib.setColorbarTitle.restype = None

    helios_lib.setColorbarFontColor.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float)]
    helios_lib.setColorbarFontColor.restype = None

    helios_lib.setColorbarFontSize.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_uint]
    helios_lib.setColorbarFontSize.restype = None

    # Colormap Functions
    helios_lib.setColormap.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_uint]
    helios_lib.setColormap.restype = None

    helios_lib.setCustomColormap.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.c_uint]
    helios_lib.setCustomColormap.restype = None

    # Object/Primitive Coloring Functions
    helios_lib.colorContextPrimitivesByObjectData.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_char_p]
    helios_lib.colorContextPrimitivesByObjectData.restype = None

    helios_lib.colorContextPrimitivesByObjectDataIDs.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint), ctypes.c_uint]
    helios_lib.colorContextPrimitivesByObjectDataIDs.restype = None

    helios_lib.colorContextPrimitivesRandomly.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_uint), ctypes.c_uint]
    helios_lib.colorContextPrimitivesRandomly.restype = None

    helios_lib.colorContextObjectsRandomly.argtypes = [ctypes.POINTER(UVisualizer), ctypes.POINTER(ctypes.c_uint), ctypes.c_uint]
    helios_lib.colorContextObjectsRandomly.restype = None

    helios_lib.clearColor.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.clearColor.restype = None

    # Watermark Control Functions
    helios_lib.hideWatermark.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.hideWatermark.restype = None

    helios_lib.showWatermark.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.showWatermark.restype = None

    helios_lib.updateWatermark.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.updateWatermark.restype = None

    # Performance and Utility Functions
    helios_lib.enableMessages.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.enableMessages.restype = None

    helios_lib.disableMessages.argtypes = [ctypes.POINTER(UVisualizer)]
    helios_lib.disableMessages.restype = None

    helios_lib.plotOnce.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_bool]
    helios_lib.plotOnce.restype = None

    helios_lib.plotUpdateWithVisibility.argtypes = [ctypes.POINTER(UVisualizer), ctypes.c_bool]
    helios_lib.plotUpdateWithVisibility.restype = None

    # Error management functions availability check
    try:
        helios_lib.getLastErrorCode.restype = ctypes.c_int
        helios_lib.getLastErrorMessage.restype = ctypes.c_char_p
        helios_lib.clearLastError.restype = None
        _ERROR_MANAGEMENT_AVAILABLE = True
    except AttributeError:
        _ERROR_MANAGEMENT_AVAILABLE = False

    _VISUALIZER_FUNCTIONS_AVAILABLE = True
except AttributeError:
    _VISUALIZER_FUNCTIONS_AVAILABLE = False
    _ERROR_MANAGEMENT_AVAILABLE = False

def _check_for_helios_error():
    """Check for and raise Helios errors if error management is available."""
    if _ERROR_MANAGEMENT_AVAILABLE:
        check_helios_error(helios_lib.getLastErrorCode, helios_lib.getLastErrorMessage)

# Wrapper functions

def create_visualizer(width: int, height: int, headless: bool = False) -> Optional[ctypes.POINTER(UVisualizer)]:
    """
    Create a new Visualizer instance.
    
    Args:
        width: Window width in pixels
        height: Window height in pixels
        headless: Enable headless mode (no window display)
        
    Returns:
        Pointer to UVisualizer or None if not available
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If visualizer creation fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    try:
        # The errcheck callback will handle error checking and null pointer validation
        visualizer = helios_lib.createVisualizer(
            ctypes.c_uint32(width),
            ctypes.c_uint32(height), 
            ctypes.c_bool(headless)
        )
        return visualizer
    except OSError as e:
        # Handle low-level system errors (e.g., graphics context failures)
        raise RuntimeError(
            f"Visualizer plugin failed to initialize due to system error: {e}. "
            "This may indicate missing graphics drivers, OpenGL issues, or "
            "incompatible system configuration. Try building with different options "
            "or check system requirements."
        )

def create_visualizer_with_antialiasing(width: int, height: int, antialiasing_samples: int, headless: bool = False) -> Optional[ctypes.POINTER(UVisualizer)]:
    """
    Create a new Visualizer instance with antialiasing.
    
    Args:
        width: Window width in pixels
        height: Window height in pixels
        antialiasing_samples: Number of antialiasing samples
        headless: Enable headless mode (no window display)
        
    Returns:
        Pointer to UVisualizer or None if not available
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If visualizer creation fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    try:
        # The errcheck callback will handle error checking and null pointer validation
        visualizer = helios_lib.createVisualizerWithAntialiasing(
            ctypes.c_uint32(width),
            ctypes.c_uint32(height),
            ctypes.c_uint32(antialiasing_samples),
            ctypes.c_bool(headless)
        )
        return visualizer
    except OSError as e:
        # Handle low-level system errors (e.g., graphics context failures)
        raise RuntimeError(
            f"Visualizer plugin failed to initialize due to system error: {e}. "
            "This may indicate missing graphics drivers, OpenGL issues, or "
            "incompatible system configuration. Try building with different options "
            "or check system requirements."
        )

def destroy_visualizer(visualizer: ctypes.POINTER(UVisualizer)) -> None:
    """
    Destroy a Visualizer instance.
    
    Args:
        visualizer: Pointer to UVisualizer to destroy
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        return  # Silent no-op for cleanup
    
    if visualizer:
        helios_lib.destroyVisualizer(visualizer)
        _check_for_helios_error()

def build_context_geometry(visualizer: ctypes.POINTER(UVisualizer), context: ctypes.POINTER(UContext)) -> None:
    """
    Build Context geometry in the visualizer.
    
    Args:
        visualizer: Pointer to UVisualizer
        context: Pointer to UContext
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If geometry building fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if not context:
        raise ValueError("Context pointer is null")
    
    helios_lib.buildContextGeometry(visualizer, context)
    _check_for_helios_error()

def build_context_geometry_uuids(visualizer: ctypes.POINTER(UVisualizer), context: ctypes.POINTER(UContext), uuids: List[int]) -> None:
    """
    Build specific Context geometry UUIDs in the visualizer.
    
    Args:
        visualizer: Pointer to UVisualizer
        context: Pointer to UContext
        uuids: List of primitive UUIDs to visualize
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If geometry building fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if not context:
        raise ValueError("Context pointer is null")
    if not uuids:
        raise ValueError("UUIDs list cannot be empty")
    
    # Convert Python list to ctypes array
    uuid_array = (ctypes.c_uint32 * len(uuids))(*uuids)
    
    helios_lib.buildContextGeometryUUIDs(visualizer, context, uuid_array, ctypes.c_size_t(len(uuids)))
    _check_for_helios_error()

def plot_interactive(visualizer: ctypes.POINTER(UVisualizer)) -> None:
    """
    Open interactive visualization window.
    
    Args:
        visualizer: Pointer to UVisualizer
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If visualization fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    helios_lib.plotInteractive(visualizer)
    _check_for_helios_error()

def plot_update(visualizer: ctypes.POINTER(UVisualizer)) -> None:
    """
    Update visualization (non-interactive).
    
    Args:
        visualizer: Pointer to UVisualizer
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If visualization update fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    helios_lib.plotUpdate(visualizer)
    _check_for_helios_error()

def print_window(visualizer: ctypes.POINTER(UVisualizer), filename: str) -> None:
    """
    Save current visualization to image file.
    
    Args:
        visualizer: Pointer to UVisualizer
        filename: Output filename for image
        
    Raises:
        NotImplementedError: If visualizer functions not available
        RuntimeError: If image saving fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    filename_encoded = filename.encode('utf-8')
    helios_lib.printWindow(visualizer, filename_encoded)
    _check_for_helios_error()

def close_window(visualizer: ctypes.POINTER(UVisualizer)) -> None:
    """
    Close visualization window.
    
    Args:
        visualizer: Pointer to UVisualizer
        
    Raises:
        NotImplementedError: If visualizer functions not available
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    helios_lib.closeWindow(visualizer)
    _check_for_helios_error()

def set_camera_position(visualizer: ctypes.POINTER(UVisualizer), position: List[float], look_at: List[float]) -> None:
    """
    Set camera position using Cartesian coordinates.
    
    Args:
        visualizer: Pointer to UVisualizer
        position: Camera position [x, y, z]
        look_at: Camera look-at point [x, y, z]
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If camera positioning fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    # Check if objects have the required methods instead of isinstance
    if not (hasattr(position, 'to_list') and hasattr(position, 'x') and hasattr(position, 'y') and hasattr(position, 'z')):
        raise ValueError(f"Position must be a vec3 object, got {type(position).__name__}")
    if not (hasattr(look_at, 'to_list') and hasattr(look_at, 'x') and hasattr(look_at, 'y') and hasattr(look_at, 'z')):
        raise ValueError(f"Look-at must be a vec3 object, got {type(look_at).__name__}")
    
    # Convert vec3 objects to ctypes arrays
    pos_array = (ctypes.c_float * 3)(*position.to_list())
    look_array = (ctypes.c_float * 3)(*look_at.to_list())
    
    helios_lib.setCameraPosition(visualizer, pos_array, look_array)
    _check_for_helios_error()

def set_camera_position_spherical(visualizer: ctypes.POINTER(UVisualizer), angle: List[float], look_at: List[float]) -> None:
    """
    Set camera position using spherical coordinates.
    
    Args:
        visualizer: Pointer to UVisualizer
        angle: Camera position [radius, zenith, azimuth]
        look_at: Camera look-at point [x, y, z]
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If camera positioning fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    # Check if objects have the required methods instead of isinstance
    if not (hasattr(angle, 'to_list') and hasattr(angle, 'radius') and hasattr(angle, 'elevation') and hasattr(angle, 'azimuth')):
        raise ValueError(f"Angle must be a SphericalCoord object, got {type(angle).__name__}")
    if not (hasattr(look_at, 'to_list') and hasattr(look_at, 'x') and hasattr(look_at, 'y') and hasattr(look_at, 'z')):
        raise ValueError(f"Look-at must be a vec3 object, got {type(look_at).__name__}")
    
    # Convert SphericalCoord and vec3 objects to ctypes arrays
    # SphericalCoord.to_list() returns [radius, elevation, zenith, azimuth] but we need [radius, elevation, azimuth]
    angle_list = [angle.radius, angle.elevation, angle.azimuth]
    angle_array = (ctypes.c_float * 3)(*angle_list)
    look_array = (ctypes.c_float * 3)(*look_at.to_list())
    
    helios_lib.setCameraPositionSpherical(visualizer, angle_array, look_array)
    _check_for_helios_error()

def set_background_color(visualizer: ctypes.POINTER(UVisualizer), color: List[float]) -> None:
    """
    Set background color.
    
    Args:
        visualizer: Pointer to UVisualizer
        color: Background color [r, g, b]
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If color setting fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    # Check if object has the required methods instead of isinstance
    if not (hasattr(color, 'to_list') and hasattr(color, 'r') and hasattr(color, 'g') and hasattr(color, 'b')):
        raise ValueError(f"Color must be an RGBcolor object, got {type(color).__name__}")
    
    # Convert RGBcolor object to ctypes array
    color_array = (ctypes.c_float * 3)(*color.to_list())
    
    helios_lib.setBackgroundColor(visualizer, color_array)
    _check_for_helios_error()

def set_light_direction(visualizer: ctypes.POINTER(UVisualizer), direction) -> None:
    """
    Set light direction.
    
    Args:
        visualizer: Pointer to UVisualizer
        direction: Light direction vector as vec3
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If light direction setting fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    
    # Check if object has the required methods instead of isinstance
    if not (hasattr(direction, 'to_list') and hasattr(direction, 'x') and hasattr(direction, 'y') and hasattr(direction, 'z')):
        raise ValueError(f"Direction must be a vec3 object, got {type(direction).__name__}")
    
    # Convert vec3 object to ctypes array
    dir_array = (ctypes.c_float * 3)(*direction.to_list())
    
    helios_lib.setLightDirection(visualizer, dir_array)
    _check_for_helios_error()

def set_lighting_model(visualizer: ctypes.POINTER(UVisualizer), lighting_model: int) -> None:
    """
    Set lighting model.
    
    Args:
        visualizer: Pointer to UVisualizer
        lighting_model: Lighting model (0=NONE, 1=PHONG, 2=PHONG_SHADOWED)
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If lighting model setting fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if lighting_model not in [0, 1, 2]:
        raise ValueError("Lighting model must be 0 (NONE), 1 (PHONG), or 2 (PHONG_SHADOWED)")
    
    helios_lib.setLightingModel(visualizer, ctypes.c_uint32(lighting_model))
    _check_for_helios_error()

def color_context_primitives_by_data(visualizer: ctypes.POINTER(UVisualizer), data_name: str) -> None:
    """
    Color context primitives based on primitive data values.
    
    Args:
        visualizer: Pointer to UVisualizer
        data_name: Name of primitive data to use for coloring
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If coloring fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if not data_name:
        raise ValueError("Data name cannot be empty")
    
    data_name_bytes = data_name.encode('utf-8')
    helios_lib.colorContextPrimitivesByData(visualizer, data_name_bytes)
    _check_for_helios_error()

def color_context_primitives_by_data_uuids(visualizer: ctypes.POINTER(UVisualizer), data_name: str, uuids: List[int]) -> None:
    """
    Color specific context primitives based on primitive data values.
    
    Args:
        visualizer: Pointer to UVisualizer
        data_name: Name of primitive data to use for coloring
        uuids: List of primitive UUIDs to color
        
    Raises:
        NotImplementedError: If visualizer functions not available
        ValueError: If parameters are invalid
        RuntimeError: If coloring fails
    """
    if not _VISUALIZER_FUNCTIONS_AVAILABLE:
        raise NotImplementedError(
            "Visualizer functions not available in current Helios library. "
            "Rebuild with visualizer plugin enabled."
        )
    
    if not visualizer:
        raise ValueError("Visualizer pointer is null")
    if not data_name:
        raise ValueError("Data name cannot be empty")
    if not uuids:
        raise ValueError("UUID list cannot be empty")
    
    data_name_bytes = data_name.encode('utf-8')
    uuid_array = (ctypes.c_uint32 * len(uuids))(*uuids)
    helios_lib.colorContextPrimitivesByDataUUIDs(visualizer, data_name_bytes, uuid_array, len(uuids))
    _check_for_helios_error()

# Mock implementations when visualizer is not available
if not _VISUALIZER_FUNCTIONS_AVAILABLE:
    def _mock_function(*args, **kwargs):
        raise RuntimeError(
            "Mock mode: Visualizer plugin not available. "
            "This would perform visualization with native Helios library. "
            "To enable visualizer functionality:\n"
            "1. Build PyHelios with visualizer plugin: build_scripts/build_helios --plugins visualizer\n"
            "2. Ensure OpenGL, GLFW, and graphics dependencies are available\n"
            "3. Rebuild PyHelios with graphics system support"
        )
    
    # Replace all wrapper functions with mock
    create_visualizer = _mock_function
    create_visualizer_with_antialiasing = _mock_function
    build_context_geometry = _mock_function
    build_context_geometry_uuids = _mock_function
    plot_interactive = _mock_function
    plot_update = _mock_function
    print_window = _mock_function
    close_window = _mock_function
    set_camera_position = _mock_function
    set_camera_position_spherical = _mock_function
    set_background_color = _mock_function
    set_light_direction = _mock_function
    set_lighting_model = _mock_function
    color_context_primitives_by_data = _mock_function
    color_context_primitives_by_data_uuids = _mock_function