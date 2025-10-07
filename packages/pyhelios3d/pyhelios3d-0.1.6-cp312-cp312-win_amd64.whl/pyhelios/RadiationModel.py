"""
High-level RadiationModel interface for PyHelios.

This module provides a user-friendly interface to the radiation modeling
capabilities with graceful plugin handling and informative error messages.
"""

import logging
from typing import List, Optional
from contextlib import contextmanager
from pathlib import Path
import os

from .plugins.registry import get_plugin_registry, require_plugin, graceful_plugin_fallback
from .wrappers import URadiationModelWrapper as radiation_wrapper
from .validation.plugins import (
    validate_wavelength_range, validate_flux_value, validate_ray_count,
    validate_direction_vector, validate_band_label, validate_source_id, validate_source_id_list
)
from .validation.plugin_decorators import (
    validate_radiation_band_params, validate_collimated_source_params, validate_sphere_source_params,
    validate_sun_sphere_params, validate_get_source_flux_params,
    validate_update_geometry_params, validate_run_band_params, validate_scattering_depth_params,
    validate_min_scatter_energy_params
)
from .Context import Context
from .assets import get_asset_manager

logger = logging.getLogger(__name__)


@contextmanager
def _radiation_working_directory():
    """
    Context manager that temporarily changes working directory to where RadiationModel assets are located.
    
    RadiationModel C++ code uses hardcoded relative paths like "plugins/radiation/cuda_compile_ptx_generated_rayGeneration.cu.ptx"
    expecting assets relative to working directory. This manager temporarily changes to the build directory
    where assets are actually located.
    
    Raises:
        RuntimeError: If build directory or RadiationModel assets are not found, indicating a build system error.
    """
    # Find the build directory containing RadiationModel assets
    # Try asset manager first (works for both development and wheel installations)
    asset_manager = get_asset_manager()
    working_dir = asset_manager._get_helios_build_path()
    
    if working_dir and working_dir.exists():
        radiation_assets = working_dir / 'plugins' / 'radiation'
    else:
        # For wheel installations, check packaged assets  
        current_dir = Path(__file__).parent
        packaged_build = current_dir / 'assets' / 'build'
        
        if packaged_build.exists():
            working_dir = packaged_build
            radiation_assets = working_dir / 'plugins' / 'radiation'
        else:
            # Fallback to development paths
            repo_root = current_dir.parent
            build_lib_dir = repo_root / 'pyhelios_build' / 'build' / 'lib'
            working_dir = build_lib_dir.parent
            radiation_assets = working_dir / 'plugins' / 'radiation'
            
            if not build_lib_dir.exists():
                raise RuntimeError(
                    f"PyHelios build directory not found at {build_lib_dir}. "
                    f"Run: python build_scripts/build_helios.py --plugins radiation"
                )
    
    if not radiation_assets.exists():
        raise RuntimeError(
            f"RadiationModel assets not found at {radiation_assets}. "
            f"This indicates a build system error. The build script should copy PTX files to this location."
        )
    
    # Change to the build directory temporarily
    original_dir = os.getcwd()
    try:
        os.chdir(working_dir)
        logger.debug(f"Changed working directory to {working_dir} for RadiationModel asset access")
        yield working_dir
    finally:
        os.chdir(original_dir)
        logger.debug(f"Restored working directory to {original_dir}")


class RadiationModelError(Exception):
    """Raised when RadiationModel operations fail."""
    pass


class CameraProperties:
    """
    Camera properties for radiation model cameras.

    This class encapsulates the properties needed to configure a radiation camera,
    providing sensible defaults and validation for camera parameters.
    """

    def __init__(self, camera_resolution=None, focal_plane_distance=1.0, lens_diameter=0.05,
                 HFOV=20.0, FOV_aspect_ratio=1.0):
        """
        Initialize camera properties with defaults matching C++ CameraProperties.

        Args:
            camera_resolution: Camera resolution as (width, height) tuple or list. Default: (512, 512)
            focal_plane_distance: Distance from viewing plane to focal plane. Default: 1.0
            lens_diameter: Diameter of camera lens (0 = pinhole camera). Default: 0.05
            HFOV: Horizontal field of view in degrees. Default: 20.0
            FOV_aspect_ratio: Ratio of horizontal to vertical field of view. Default: 1.0
        """
        # Set camera resolution with validation
        if camera_resolution is None:
            self.camera_resolution = (512, 512)
        else:
            if isinstance(camera_resolution, (list, tuple)) and len(camera_resolution) == 2:
                self.camera_resolution = (int(camera_resolution[0]), int(camera_resolution[1]))
            else:
                raise ValueError("camera_resolution must be a tuple or list of 2 integers")

        # Validate and set other properties
        if focal_plane_distance <= 0:
            raise ValueError("focal_plane_distance must be greater than 0")
        if lens_diameter < 0:
            raise ValueError("lens_diameter must be non-negative")
        if HFOV <= 0 or HFOV > 180:
            raise ValueError("HFOV must be between 0 and 180 degrees")
        if FOV_aspect_ratio <= 0:
            raise ValueError("FOV_aspect_ratio must be greater than 0")

        self.focal_plane_distance = float(focal_plane_distance)
        self.lens_diameter = float(lens_diameter)
        self.HFOV = float(HFOV)
        self.FOV_aspect_ratio = float(FOV_aspect_ratio)

    def to_array(self):
        """
        Convert to array format expected by C++ interface.

        Returns:
            List of 6 float values: [resolution_x, resolution_y, focal_distance, lens_diameter, HFOV, FOV_aspect_ratio]
        """
        return [
            float(self.camera_resolution[0]),  # resolution_x
            float(self.camera_resolution[1]),  # resolution_y
            self.focal_plane_distance,
            self.lens_diameter,
            self.HFOV,
            self.FOV_aspect_ratio
        ]

    def __repr__(self):
        return (f"CameraProperties(camera_resolution={self.camera_resolution}, "
                f"focal_plane_distance={self.focal_plane_distance}, "
                f"lens_diameter={self.lens_diameter}, "
                f"HFOV={self.HFOV}, "
                f"FOV_aspect_ratio={self.FOV_aspect_ratio})")


class RadiationModel:
    """
    High-level interface for radiation modeling and ray tracing.
    
    This class provides a user-friendly wrapper around the native Helios
    radiation plugin with automatic plugin availability checking and
    graceful error handling.
    """
    
    def __init__(self, context: Context):
        """
        Initialize RadiationModel with graceful plugin handling.
        
        Args:
            context: Helios Context instance
            
        Raises:
            TypeError: If context is not a Context instance
            RadiationModelError: If radiation plugin is not available
        """
        # Validate context type
        if not isinstance(context, Context):
            raise TypeError(f"RadiationModel requires a Context instance, got {type(context).__name__}")
        
        self.context = context
        self.radiation_model = None
        
        # Check plugin availability using registry
        registry = get_plugin_registry()
        
        if not registry.is_plugin_available('radiation'):
            # Get helpful information about the missing plugin
            plugin_info = registry.get_plugin_capabilities()
            available_plugins = registry.get_available_plugins()
            
            error_msg = (
                "RadiationModel requires the 'radiation' plugin which is not available.\n\n"
                "The radiation plugin provides GPU-accelerated ray tracing using OptiX.\n"
                "System requirements:\n"
                "- NVIDIA GPU with CUDA support\n"
                "- CUDA Toolkit installed\n"
                "- OptiX runtime (bundled with PyHelios)\n\n"
                "To enable radiation modeling:\n"
                "1. Build PyHelios with radiation plugin:\n"
                "   build_scripts/build_helios --plugins radiation\n"
                "2. Or build with multiple plugins:\n"
                "   build_scripts/build_helios --plugins radiation,visualizer,weberpenntree\n"
                f"\nCurrently available plugins: {available_plugins}"
            )
            
            # Suggest alternatives if available
            alternatives = registry.suggest_alternatives('radiation')
            if alternatives:
                error_msg += f"\n\nAlternative plugins available: {alternatives}"
                error_msg += "\nConsider using energybalance or leafoptics for thermal modeling."
            
            raise RadiationModelError(error_msg)
        
        # Plugin is available - create radiation model using working directory context manager
        try:
            with _radiation_working_directory():
                self.radiation_model = radiation_wrapper.createRadiationModel(context.getNativePtr())
                if self.radiation_model is None:
                    raise RadiationModelError(
                        "Failed to create RadiationModel instance. "
                        "This may indicate a problem with the native library or GPU initialization."
                    )
            logger.info("RadiationModel created successfully")
            
        except Exception as e:
            raise RadiationModelError(f"Failed to initialize RadiationModel: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit with proper cleanup."""
        if self.radiation_model is not None:
            try:
                radiation_wrapper.destroyRadiationModel(self.radiation_model)
                logger.debug("RadiationModel destroyed successfully")
            except Exception as e:
                logger.warning(f"Error destroying RadiationModel: {e}")
    
    def get_native_ptr(self):
        """Get native pointer for advanced operations."""
        return self.radiation_model
    
    def getNativePtr(self):
        """Get native pointer for advanced operations. (Legacy naming for compatibility)"""
        return self.get_native_ptr()
    
    @require_plugin('radiation', 'disable status messages')
    def disableMessages(self):
        """Disable RadiationModel status messages."""
        radiation_wrapper.disableMessages(self.radiation_model)
    
    @require_plugin('radiation', 'enable status messages')
    def enableMessages(self):
        """Enable RadiationModel status messages."""
        radiation_wrapper.enableMessages(self.radiation_model)
    
    @require_plugin('radiation', 'add radiation band')
    def addRadiationBand(self, band_label: str, wavelength_min: float = None, wavelength_max: float = None):
        """
        Add radiation band with optional wavelength bounds.
        
        Args:
            band_label: Name/label for the radiation band
            wavelength_min: Optional minimum wavelength (μm)
            wavelength_max: Optional maximum wavelength (μm)
        """
        # Validate inputs
        validate_band_label(band_label, "band_label", "addRadiationBand")
        if wavelength_min is not None and wavelength_max is not None:
            validate_wavelength_range(wavelength_min, wavelength_max, "wavelength_min", "wavelength_max", "addRadiationBand")
            radiation_wrapper.addRadiationBandWithWavelengths(self.radiation_model, band_label, wavelength_min, wavelength_max)
            logger.debug(f"Added radiation band {band_label}: {wavelength_min}-{wavelength_max} μm")
        else:
            radiation_wrapper.addRadiationBand(self.radiation_model, band_label)
            logger.debug(f"Added radiation band: {band_label}")
    
    @require_plugin('radiation', 'copy radiation band')
    @validate_radiation_band_params
    def copyRadiationBand(self, old_label: str, new_label: str):
        """
        Copy existing radiation band to new label.
        
        Args:
            old_label: Existing band label to copy
            new_label: New label for the copied band
        """
        radiation_wrapper.copyRadiationBand(self.radiation_model, old_label, new_label)
        logger.debug(f"Copied radiation band {old_label} to {new_label}")
    
    @require_plugin('radiation', 'add radiation source')
    @validate_collimated_source_params
    def addCollimatedRadiationSource(self, direction=None) -> int:
        """
        Add collimated radiation source.
        
        Args:
            direction: Optional direction vector. Can be tuple (x, y, z), vec3, or None for default direction.
            
        Returns:
            Source ID
        """
        if direction is None:
            source_id = radiation_wrapper.addCollimatedRadiationSourceDefault(self.radiation_model)
        else:
            # Handle vec3, SphericalCoord, and tuple types
            if hasattr(direction, 'x') and hasattr(direction, 'y') and hasattr(direction, 'z'):
                # vec3-like object
                x, y, z = direction.x, direction.y, direction.z
            elif hasattr(direction, 'radius') and hasattr(direction, 'elevation') and hasattr(direction, 'azimuth'):
                # SphericalCoord object - convert to Cartesian
                import math
                r = direction.radius
                elevation = direction.elevation
                azimuth = direction.azimuth
                x = r * math.cos(elevation) * math.cos(azimuth)
                y = r * math.cos(elevation) * math.sin(azimuth)
                z = r * math.sin(elevation)
            else:
                # Assume tuple-like object - validate it first
                try:
                    if len(direction) != 3:
                        raise TypeError(f"Direction must be a 3-element tuple, vec3, or SphericalCoord, got {type(direction).__name__} with {len(direction)} elements")
                    x, y, z = direction
                except (TypeError, AttributeError):
                    # Not a valid sequence type
                    raise TypeError(f"Direction must be a tuple, vec3, or SphericalCoord, got {type(direction).__name__}")
            source_id = radiation_wrapper.addCollimatedRadiationSourceVec3(self.radiation_model, x, y, z)
        
        logger.debug(f"Added collimated radiation source: ID {source_id}")
        return source_id
    
    @require_plugin('radiation', 'add spherical radiation source')
    @validate_sphere_source_params
    def addSphereRadiationSource(self, position, radius: float) -> int:
        """
        Add spherical radiation source.
        
        Args:
            position: Position of the source. Can be tuple (x, y, z) or vec3.
            radius: Radius of the spherical source
            
        Returns:
            Source ID
        """
        # Handle both tuple and vec3 types
        if hasattr(position, 'x') and hasattr(position, 'y') and hasattr(position, 'z'):
            # vec3-like object
            x, y, z = position.x, position.y, position.z
        else:
            # Assume tuple-like object
            x, y, z = position
        source_id = radiation_wrapper.addSphereRadiationSource(self.radiation_model, x, y, z, radius)
        logger.debug(f"Added sphere radiation source: ID {source_id} at ({x}, {y}, {z}) with radius {radius}")
        return source_id
    
    @require_plugin('radiation', 'add sun radiation source')
    @validate_sun_sphere_params
    def addSunSphereRadiationSource(self, radius: float, zenith: float, azimuth: float,
                                    position_scaling: float = 1.0, angular_width: float = 0.53,
                                    flux_scaling: float = 1.0) -> int:
        """
        Add sun sphere radiation source.
        
        Args:
            radius: Radius of the sun sphere
            zenith: Zenith angle (degrees)
            azimuth: Azimuth angle (degrees)
            position_scaling: Position scaling factor
            angular_width: Angular width of the sun (degrees)
            flux_scaling: Flux scaling factor
            
        Returns:
            Source ID
        """
        source_id = radiation_wrapper.addSunSphereRadiationSource(
            self.radiation_model, radius, zenith, azimuth, position_scaling, angular_width, flux_scaling
        )
        logger.debug(f"Added sun radiation source: ID {source_id}")
        return source_id
    
    @require_plugin('radiation', 'set ray count')
    def setDirectRayCount(self, band_label: str, ray_count: int):
        """Set direct ray count for radiation band."""
        validate_band_label(band_label, "band_label", "setDirectRayCount")
        validate_ray_count(ray_count, "ray_count", "setDirectRayCount")
        radiation_wrapper.setDirectRayCount(self.radiation_model, band_label, ray_count)
    
    @require_plugin('radiation', 'set ray count')
    def setDiffuseRayCount(self, band_label: str, ray_count: int):
        """Set diffuse ray count for radiation band."""
        validate_band_label(band_label, "band_label", "setDiffuseRayCount")
        validate_ray_count(ray_count, "ray_count", "setDiffuseRayCount")
        radiation_wrapper.setDiffuseRayCount(self.radiation_model, band_label, ray_count)
    
    @require_plugin('radiation', 'set radiation flux')
    def setDiffuseRadiationFlux(self, label: str, flux: float):
        """Set diffuse radiation flux for band."""
        validate_band_label(label, "label", "setDiffuseRadiationFlux")
        validate_flux_value(flux, "flux", "setDiffuseRadiationFlux")
        radiation_wrapper.setDiffuseRadiationFlux(self.radiation_model, label, flux)
    
    @require_plugin('radiation', 'set source flux')
    def setSourceFlux(self, source_id, label: str, flux: float):
        """Set source flux for single source or multiple sources."""
        validate_band_label(label, "label", "setSourceFlux")
        validate_flux_value(flux, "flux", "setSourceFlux")
        
        if isinstance(source_id, (list, tuple)):
            # Multiple sources
            validate_source_id_list(list(source_id), "source_id", "setSourceFlux")
            radiation_wrapper.setSourceFluxMultiple(self.radiation_model, source_id, label, flux)
        else:
            # Single source
            validate_source_id(source_id, "source_id", "setSourceFlux")
            radiation_wrapper.setSourceFlux(self.radiation_model, source_id, label, flux)
    
    
    @require_plugin('radiation', 'get source flux')
    @validate_get_source_flux_params
    def getSourceFlux(self, source_id: int, label: str) -> float:
        """Get source flux for band."""
        return radiation_wrapper.getSourceFlux(self.radiation_model, source_id, label)
    
    @require_plugin('radiation', 'update geometry')
    @validate_update_geometry_params
    def updateGeometry(self, uuids: Optional[List[int]] = None):
        """
        Update geometry in radiation model.
        
        Args:
            uuids: Optional list of specific UUIDs to update. If None, updates all geometry.
        """
        if uuids is None:
            radiation_wrapper.updateGeometry(self.radiation_model)
            logger.debug("Updated all geometry in radiation model")
        else:
            radiation_wrapper.updateGeometryUUIDs(self.radiation_model, uuids)
            logger.debug(f"Updated {len(uuids)} geometry UUIDs in radiation model")
    
    @require_plugin('radiation', 'run radiation simulation')
    @validate_run_band_params
    def runBand(self, band_label):
        """
        Run radiation simulation for single band or multiple bands.
        
        PERFORMANCE NOTE: When simulating multiple radiation bands, it is HIGHLY RECOMMENDED
        to run all bands in a single call (e.g., runBand(["PAR", "NIR", "SW"])) rather than
        sequential single-band calls. This provides significant computational efficiency gains
        because:
        
        - GPU ray tracing setup is done once for all bands
        - Scene geometry acceleration structures are reused
        - OptiX kernel launches are batched together
        - Memory transfers between CPU/GPU are minimized
        
        Example:
            # EFFICIENT - Single call for multiple bands
            radiation.runBand(["PAR", "NIR", "SW"])
            
            # INEFFICIENT - Sequential single-band calls  
            radiation.runBand("PAR")
            radiation.runBand("NIR") 
            radiation.runBand("SW")
        
        Args:
            band_label: Single band name (str) or list of band names for multi-band simulation
        """
        if isinstance(band_label, (list, tuple)):
            # Multiple bands - validate each label
            for lbl in band_label:
                if not isinstance(lbl, str):
                    raise TypeError(f"Band labels must be strings, got {type(lbl).__name__}")
            radiation_wrapper.runBandMultiple(self.radiation_model, band_label)
            logger.info(f"Completed radiation simulation for bands: {band_label}")
        else:
            # Single band - validate label type
            if not isinstance(band_label, str):
                raise TypeError(f"Band label must be a string, got {type(band_label).__name__}")
            radiation_wrapper.runBand(self.radiation_model, band_label)
            logger.info(f"Completed radiation simulation for band: {band_label}")
    
    
    @require_plugin('radiation', 'get simulation results')
    def getTotalAbsorbedFlux(self) -> List[float]:
        """Get total absorbed flux for all primitives."""
        results = radiation_wrapper.getTotalAbsorbedFlux(self.radiation_model)
        logger.debug(f"Retrieved absorbed flux data for {len(results)} primitives")
        return results
    
    # Configuration methods
    @require_plugin('radiation', 'configure radiation simulation')
    @validate_scattering_depth_params
    def setScatteringDepth(self, label: str, depth: int):
        """Set scattering depth for radiation band."""
        radiation_wrapper.setScatteringDepth(self.radiation_model, label, depth)
    
    @require_plugin('radiation', 'configure radiation simulation')
    @validate_min_scatter_energy_params
    def setMinScatterEnergy(self, label: str, energy: float):
        """Set minimum scatter energy for radiation band."""
        radiation_wrapper.setMinScatterEnergy(self.radiation_model, label, energy)
    
    @require_plugin('radiation', 'configure radiation emission')
    def disableEmission(self, label: str):
        """Disable emission for radiation band."""
        validate_band_label(label, "label", "disableEmission")
        radiation_wrapper.disableEmission(self.radiation_model, label)
    
    @require_plugin('radiation', 'configure radiation emission')
    def enableEmission(self, label: str):
        """Enable emission for radiation band."""
        validate_band_label(label, "label", "enableEmission")
        radiation_wrapper.enableEmission(self.radiation_model, label)
    
    #=============================================================================
    # Camera and Image Functions (v1.3.47)
    #=============================================================================

    @require_plugin('radiation', 'add radiation camera')
    def addRadiationCamera(self, camera_label: str, band_labels: List[str], position, lookat_or_direction,
                          camera_properties=None, antialiasing_samples: int = 100):
        """
        Add a radiation camera to the simulation.

        Args:
            camera_label: Unique label string for the camera
            band_labels: List of radiation band labels for the camera
            position: Camera position as vec3 object
            lookat_or_direction: Either:
                - Lookat point as vec3 object
                - SphericalCoord for viewing direction
            camera_properties: CameraProperties instance or None for defaults
            antialiasing_samples: Number of antialiasing samples (default: 100)

        Raises:
            ValidationError: If parameters are invalid or have wrong types
            RadiationModelError: If camera creation fails

        Example:
            >>> from pyhelios import vec3, CameraProperties
            >>> # Create camera looking at origin from above
            >>> camera_props = CameraProperties(camera_resolution=(1024, 1024))
            >>> radiation_model.addRadiationCamera("main_camera", ["red", "green", "blue"],
            ...                                   position=vec3(0, 0, 5), lookat_or_direction=vec3(0, 0, 0),
            ...                                   camera_properties=camera_props)
        """
        # Import here to avoid circular imports
        from .wrappers import URadiationModelWrapper as radiation_wrapper
        from .wrappers.DataTypes import SphericalCoord, vec3, make_vec3
        from .validation.plugins import validate_camera_label, validate_band_labels_list, validate_antialiasing_samples

        # Validate basic parameters
        validated_label = validate_camera_label(camera_label, "camera_label", "addRadiationCamera")
        validated_bands = validate_band_labels_list(band_labels, "band_labels", "addRadiationCamera")
        validated_samples = validate_antialiasing_samples(antialiasing_samples, "antialiasing_samples", "addRadiationCamera")

        # Validate position (must be vec3)
        if not (hasattr(position, 'x') and hasattr(position, 'y') and hasattr(position, 'z')):
            raise TypeError("position must be a vec3 object. Use vec3(x, y, z) to create one.")
        validated_position = position

        # Validate lookat_or_direction (must be vec3 or SphericalCoord)
        if hasattr(lookat_or_direction, 'radius') and hasattr(lookat_or_direction, 'elevation'):
            validated_direction = lookat_or_direction  # SphericalCoord
        elif hasattr(lookat_or_direction, 'x') and hasattr(lookat_or_direction, 'y') and hasattr(lookat_or_direction, 'z'):
            validated_direction = lookat_or_direction  # vec3
        else:
            raise TypeError("lookat_or_direction must be a vec3 or SphericalCoord object. Use vec3(x, y, z) or SphericalCoord to create one.")

        # Set up camera properties
        if camera_properties is None:
            camera_properties = CameraProperties()

        # Call appropriate wrapper function based on direction type
        try:
            if hasattr(validated_direction, 'radius') and hasattr(validated_direction, 'elevation'):
                # SphericalCoord case
                direction_coords = validated_direction.to_list()
                if len(direction_coords) >= 3:
                    # Use only radius, elevation, azimuth (first 3 elements)
                    radius, elevation, azimuth = direction_coords[0], direction_coords[1], direction_coords[2]
                else:
                    raise ValueError("SphericalCoord must have at least radius, elevation, and azimuth")

                radiation_wrapper.addRadiationCameraSpherical(
                    self.radiation_model,
                    validated_label,
                    validated_bands,
                    validated_position.x, validated_position.y, validated_position.z,
                    radius, elevation, azimuth,
                    camera_properties.to_array(),
                    validated_samples
                )
            else:
                # vec3 case
                radiation_wrapper.addRadiationCameraVec3(
                    self.radiation_model,
                    validated_label,
                    validated_bands,
                    validated_position.x, validated_position.y, validated_position.z,
                    validated_direction.x, validated_direction.y, validated_direction.z,
                    camera_properties.to_array(),
                    validated_samples
                )

        except Exception as e:
            raise RadiationModelError(f"Failed to add radiation camera '{validated_label}': {e}")

    @require_plugin('radiation', 'write camera images')
    def writeCameraImage(self, camera: str, bands: List[str], imagefile_base: str,
                          image_path: str = "./", frame: int = -1,
                          flux_to_pixel_conversion: float = 1.0) -> str:
        """
        Write camera image to file and return output filename.
        
        Args:
            camera: Camera label
            bands: List of band labels to include in the image
            imagefile_base: Base filename for output
            image_path: Output directory path (default: current directory)
            frame: Frame number to write (-1 for all frames)
            flux_to_pixel_conversion: Conversion factor from flux to pixel values
            
        Returns:
            Output filename string
            
        Raises:
            RadiationModelError: If camera image writing fails
            TypeError: If parameters have incorrect types
        """
        # Validate inputs
        if not isinstance(camera, str) or not camera.strip():
            raise TypeError("Camera label must be a non-empty string")
        if not isinstance(bands, list) or not bands:
            raise TypeError("Bands must be a non-empty list of strings")
        if not all(isinstance(band, str) and band.strip() for band in bands):
            raise TypeError("All band labels must be non-empty strings")
        if not isinstance(imagefile_base, str) or not imagefile_base.strip():
            raise TypeError("Image file base must be a non-empty string")
        if not isinstance(image_path, str):
            raise TypeError("Image path must be a string")
        if not isinstance(frame, int):
            raise TypeError("Frame must be an integer")
        if not isinstance(flux_to_pixel_conversion, (int, float)) or flux_to_pixel_conversion <= 0:
            raise TypeError("Flux to pixel conversion must be a positive number")
        
        filename = radiation_wrapper.writeCameraImage(
            self.radiation_model, camera, bands, imagefile_base, 
            image_path, frame, flux_to_pixel_conversion)
        
        logger.info(f"Camera image written to: {filename}")
        return filename
    
    @require_plugin('radiation', 'write normalized camera images')
    def writeNormCameraImage(self, camera: str, bands: List[str], imagefile_base: str,
                               image_path: str = "./", frame: int = -1) -> str:
        """
        Write normalized camera image to file and return output filename.
        
        Args:
            camera: Camera label
            bands: List of band labels to include in the image
            imagefile_base: Base filename for output
            image_path: Output directory path (default: current directory)
            frame: Frame number to write (-1 for all frames)
            
        Returns:
            Output filename string
            
        Raises:
            RadiationModelError: If normalized camera image writing fails
            TypeError: If parameters have incorrect types
        """
        # Validate inputs
        if not isinstance(camera, str) or not camera.strip():
            raise TypeError("Camera label must be a non-empty string")
        if not isinstance(bands, list) or not bands:
            raise TypeError("Bands must be a non-empty list of strings")
        if not all(isinstance(band, str) and band.strip() for band in bands):
            raise TypeError("All band labels must be non-empty strings")
        if not isinstance(imagefile_base, str) or not imagefile_base.strip():
            raise TypeError("Image file base must be a non-empty string")
        if not isinstance(image_path, str):
            raise TypeError("Image path must be a string")
        if not isinstance(frame, int):
            raise TypeError("Frame must be an integer")
        
        filename = radiation_wrapper.writeNormCameraImage(
            self.radiation_model, camera, bands, imagefile_base, image_path, frame)
        
        logger.info(f"Normalized camera image written to: {filename}")
        return filename
    
    @require_plugin('radiation', 'write camera image data')
    def writeCameraImageData(self, camera: str, band: str, imagefile_base: str,
                               image_path: str = "./", frame: int = -1):
        """
        Write camera image data to file (ASCII format).
        
        Args:
            camera: Camera label
            band: Band label
            imagefile_base: Base filename for output
            image_path: Output directory path (default: current directory)
            frame: Frame number to write (-1 for all frames)
            
        Raises:
            RadiationModelError: If camera image data writing fails
            TypeError: If parameters have incorrect types
        """
        # Validate inputs
        if not isinstance(camera, str) or not camera.strip():
            raise TypeError("Camera label must be a non-empty string")
        if not isinstance(band, str) or not band.strip():
            raise TypeError("Band label must be a non-empty string")
        if not isinstance(imagefile_base, str) or not imagefile_base.strip():
            raise TypeError("Image file base must be a non-empty string")
        if not isinstance(image_path, str):
            raise TypeError("Image path must be a string")
        if not isinstance(frame, int):
            raise TypeError("Frame must be an integer")
        
        radiation_wrapper.writeCameraImageData(
            self.radiation_model, camera, band, imagefile_base, image_path, frame)
        
        logger.info(f"Camera image data written for camera {camera}, band {band}")
    
    @require_plugin('radiation', 'write image bounding boxes')
    def writeImageBoundingBoxes(self, camera_label: str,
                                  primitive_data_labels=None, object_data_labels=None,
                                  object_class_ids=None, image_file: str = "",
                                  classes_txt_file: str = "classes.txt",
                                  image_path: str = "./"):
        """
        Write image bounding boxes for object detection training.
        
        Supports both single and multiple data labels. Either provide primitive_data_labels
        or object_data_labels, not both.
        
        Args:
            camera_label: Camera label
            primitive_data_labels: Single primitive data label (str) or list of primitive data labels
            object_data_labels: Single object data label (str) or list of object data labels  
            object_class_ids: Single class ID (int) or list of class IDs (must match data labels)
            image_file: Image filename
            classes_txt_file: Classes definition file (default: "classes.txt")
            image_path: Image output path (default: current directory)
            
        Raises:
            RadiationModelError: If bounding box writing fails
            TypeError: If parameters have incorrect types
            ValueError: If both primitive and object data labels are provided, or neither
        """
        # Validate exclusive parameter usage
        if primitive_data_labels is not None and object_data_labels is not None:
            raise ValueError("Cannot specify both primitive_data_labels and object_data_labels")
        if primitive_data_labels is None and object_data_labels is None:
            raise ValueError("Must specify either primitive_data_labels or object_data_labels")
        
        # Validate common parameters
        if not isinstance(camera_label, str) or not camera_label.strip():
            raise TypeError("Camera label must be a non-empty string")
        if not isinstance(image_file, str) or not image_file.strip():
            raise TypeError("Image file must be a non-empty string")
        if not isinstance(classes_txt_file, str):
            raise TypeError("Classes txt file must be a string")
        if not isinstance(image_path, str):
            raise TypeError("Image path must be a string")
        
        # Handle primitive data labels
        if primitive_data_labels is not None:
            if isinstance(primitive_data_labels, str):
                # Single label
                if not isinstance(object_class_ids, int):
                    raise TypeError("For single primitive data label, object_class_ids must be an integer")
                radiation_wrapper.writeImageBoundingBoxes(
                    self.radiation_model, camera_label, primitive_data_labels, 
                    object_class_ids, image_file, classes_txt_file, image_path)
                logger.info(f"Image bounding boxes written for primitive data: {primitive_data_labels}")
            
            elif isinstance(primitive_data_labels, list):
                # Multiple labels
                if not isinstance(object_class_ids, list):
                    raise TypeError("For multiple primitive data labels, object_class_ids must be a list")
                if len(primitive_data_labels) != len(object_class_ids):
                    raise ValueError("primitive_data_labels and object_class_ids must have the same length")
                if not all(isinstance(lbl, str) and lbl.strip() for lbl in primitive_data_labels):
                    raise TypeError("All primitive data labels must be non-empty strings")
                if not all(isinstance(cid, int) for cid in object_class_ids):
                    raise TypeError("All object class IDs must be integers")
                
                radiation_wrapper.writeImageBoundingBoxesVector(
                    self.radiation_model, camera_label, primitive_data_labels, 
                    object_class_ids, image_file, classes_txt_file, image_path)
                logger.info(f"Image bounding boxes written for {len(primitive_data_labels)} primitive data labels")
            else:
                raise TypeError("primitive_data_labels must be a string or list of strings")
        
        # Handle object data labels  
        elif object_data_labels is not None:
            if isinstance(object_data_labels, str):
                # Single label
                if not isinstance(object_class_ids, int):
                    raise TypeError("For single object data label, object_class_ids must be an integer")
                radiation_wrapper.writeImageBoundingBoxes_ObjectData(
                    self.radiation_model, camera_label, object_data_labels, 
                    object_class_ids, image_file, classes_txt_file, image_path)
                logger.info(f"Image bounding boxes written for object data: {object_data_labels}")
            
            elif isinstance(object_data_labels, list):
                # Multiple labels
                if not isinstance(object_class_ids, list):
                    raise TypeError("For multiple object data labels, object_class_ids must be a list")
                if len(object_data_labels) != len(object_class_ids):
                    raise ValueError("object_data_labels and object_class_ids must have the same length")
                if not all(isinstance(lbl, str) and lbl.strip() for lbl in object_data_labels):
                    raise TypeError("All object data labels must be non-empty strings")
                if not all(isinstance(cid, int) for cid in object_class_ids):
                    raise TypeError("All object class IDs must be integers")
                
                radiation_wrapper.writeImageBoundingBoxes_ObjectDataVector(
                    self.radiation_model, camera_label, object_data_labels, 
                    object_class_ids, image_file, classes_txt_file, image_path)
                logger.info(f"Image bounding boxes written for {len(object_data_labels)} object data labels")
            else:
                raise TypeError("object_data_labels must be a string or list of strings")
    
    @require_plugin('radiation', 'write image segmentation masks')
    def writeImageSegmentationMasks(self, camera_label: str,
                                      primitive_data_labels=None, object_data_labels=None,
                                      object_class_ids=None, json_filename: str = "",
                                      image_file: str = "", append_file: bool = False):
        """
        Write image segmentation masks in COCO JSON format.
        
        Supports both single and multiple data labels. Either provide primitive_data_labels
        or object_data_labels, not both.
        
        Args:
            camera_label: Camera label
            primitive_data_labels: Single primitive data label (str) or list of primitive data labels
            object_data_labels: Single object data label (str) or list of object data labels
            object_class_ids: Single class ID (int) or list of class IDs (must match data labels)
            json_filename: JSON output filename
            image_file: Image filename
            append_file: Whether to append to existing JSON file
            
        Raises:
            RadiationModelError: If segmentation mask writing fails
            TypeError: If parameters have incorrect types
            ValueError: If both primitive and object data labels are provided, or neither
        """
        # Validate exclusive parameter usage
        if primitive_data_labels is not None and object_data_labels is not None:
            raise ValueError("Cannot specify both primitive_data_labels and object_data_labels")
        if primitive_data_labels is None and object_data_labels is None:
            raise ValueError("Must specify either primitive_data_labels or object_data_labels")
        
        # Validate common parameters
        if not isinstance(camera_label, str) or not camera_label.strip():
            raise TypeError("Camera label must be a non-empty string")
        if not isinstance(json_filename, str) or not json_filename.strip():
            raise TypeError("JSON filename must be a non-empty string")
        if not isinstance(image_file, str) or not image_file.strip():
            raise TypeError("Image file must be a non-empty string")
        if not isinstance(append_file, bool):
            raise TypeError("append_file must be a boolean")
        
        # Handle primitive data labels
        if primitive_data_labels is not None:
            if isinstance(primitive_data_labels, str):
                # Single label
                if not isinstance(object_class_ids, int):
                    raise TypeError("For single primitive data label, object_class_ids must be an integer")
                radiation_wrapper.writeImageSegmentationMasks(
                    self.radiation_model, camera_label, primitive_data_labels, 
                    object_class_ids, json_filename, image_file, append_file)
                logger.info(f"Image segmentation masks written for primitive data: {primitive_data_labels}")
            
            elif isinstance(primitive_data_labels, list):
                # Multiple labels
                if not isinstance(object_class_ids, list):
                    raise TypeError("For multiple primitive data labels, object_class_ids must be a list")
                if len(primitive_data_labels) != len(object_class_ids):
                    raise ValueError("primitive_data_labels and object_class_ids must have the same length")
                if not all(isinstance(lbl, str) and lbl.strip() for lbl in primitive_data_labels):
                    raise TypeError("All primitive data labels must be non-empty strings")
                if not all(isinstance(cid, int) for cid in object_class_ids):
                    raise TypeError("All object class IDs must be integers")
                
                radiation_wrapper.writeImageSegmentationMasksVector(
                    self.radiation_model, camera_label, primitive_data_labels, 
                    object_class_ids, json_filename, image_file, append_file)
                logger.info(f"Image segmentation masks written for {len(primitive_data_labels)} primitive data labels")
            else:
                raise TypeError("primitive_data_labels must be a string or list of strings")
        
        # Handle object data labels
        elif object_data_labels is not None:
            if isinstance(object_data_labels, str):
                # Single label
                if not isinstance(object_class_ids, int):
                    raise TypeError("For single object data label, object_class_ids must be an integer")
                radiation_wrapper.writeImageSegmentationMasks_ObjectData(
                    self.radiation_model, camera_label, object_data_labels, 
                    object_class_ids, json_filename, image_file, append_file)
                logger.info(f"Image segmentation masks written for object data: {object_data_labels}")
            
            elif isinstance(object_data_labels, list):
                # Multiple labels
                if not isinstance(object_class_ids, list):
                    raise TypeError("For multiple object data labels, object_class_ids must be a list")
                if len(object_data_labels) != len(object_class_ids):
                    raise ValueError("object_data_labels and object_class_ids must have the same length")
                if not all(isinstance(lbl, str) and lbl.strip() for lbl in object_data_labels):
                    raise TypeError("All object data labels must be non-empty strings")
                if not all(isinstance(cid, int) for cid in object_class_ids):
                    raise TypeError("All object class IDs must be integers")
                
                radiation_wrapper.writeImageSegmentationMasks_ObjectDataVector(
                    self.radiation_model, camera_label, object_data_labels, 
                    object_class_ids, json_filename, image_file, append_file)
                logger.info(f"Image segmentation masks written for {len(object_data_labels)} object data labels")
            else:
                raise TypeError("object_data_labels must be a string or list of strings")
    
    @require_plugin('radiation', 'auto-calibrate camera image')
    def autoCalibrateCameraImage(self, camera_label: str, red_band_label: str,
                                   green_band_label: str, blue_band_label: str,
                                   output_file_path: str, print_quality_report: bool = False,
                                   algorithm: str = "MATRIX_3X3_AUTO",
                                   ccm_export_file_path: str = "") -> str:
        """
        Auto-calibrate camera image with color correction and return output filename.
        
        Args:
            camera_label: Camera label
            red_band_label: Red band label
            green_band_label: Green band label  
            blue_band_label: Blue band label
            output_file_path: Output file path
            print_quality_report: Whether to print quality report
            algorithm: Color correction algorithm ("DIAGONAL_ONLY", "MATRIX_3X3_AUTO", "MATRIX_3X3_FORCE")
            ccm_export_file_path: Path to export color correction matrix (optional)
            
        Returns:
            Output filename string
            
        Raises:
            RadiationModelError: If auto-calibration fails
            TypeError: If parameters have incorrect types
            ValueError: If algorithm is not valid
        """
        # Validate inputs
        if not isinstance(camera_label, str) or not camera_label.strip():
            raise TypeError("Camera label must be a non-empty string")
        if not isinstance(red_band_label, str) or not red_band_label.strip():
            raise TypeError("Red band label must be a non-empty string")
        if not isinstance(green_band_label, str) or not green_band_label.strip():
            raise TypeError("Green band label must be a non-empty string")
        if not isinstance(blue_band_label, str) or not blue_band_label.strip():
            raise TypeError("Blue band label must be a non-empty string")
        if not isinstance(output_file_path, str) or not output_file_path.strip():
            raise TypeError("Output file path must be a non-empty string")
        if not isinstance(print_quality_report, bool):
            raise TypeError("print_quality_report must be a boolean")
        if not isinstance(ccm_export_file_path, str):
            raise TypeError("ccm_export_file_path must be a string")
        
        # Map algorithm string to integer (using MATRIX_3X3_AUTO = 1 as default)
        algorithm_map = {
            "DIAGONAL_ONLY": 0,
            "MATRIX_3X3_AUTO": 1,
            "MATRIX_3X3_FORCE": 2
        }
        
        if algorithm not in algorithm_map:
            raise ValueError(f"Invalid algorithm: {algorithm}. Must be one of: {list(algorithm_map.keys())}")
        
        algorithm_int = algorithm_map[algorithm]
        
        filename = radiation_wrapper.autoCalibrateCameraImage(
            self.radiation_model, camera_label, red_band_label, green_band_label,
            blue_band_label, output_file_path, print_quality_report, 
            algorithm_int, ccm_export_file_path)
        
        logger.info(f"Auto-calibrated camera image written to: {filename}")
        return filename
    
    def getPluginInfo(self) -> dict:
        """Get information about the radiation plugin."""
        registry = get_plugin_registry()
        return registry.get_plugin_capabilities('radiation')