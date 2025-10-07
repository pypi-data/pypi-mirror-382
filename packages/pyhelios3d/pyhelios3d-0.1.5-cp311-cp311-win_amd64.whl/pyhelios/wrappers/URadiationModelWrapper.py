"""
Ctypes wrapper for RadiationModel C++ bindings.

This module provides low-level ctypes bindings to interface with 
the native Helios RadiationModel plugin via the C++ wrapper layer.
"""

import ctypes
from typing import List

from ..plugins import helios_lib
from ..exceptions import check_helios_error

# Define the URadiationModel struct
class URadiationModel(ctypes.Structure):
    pass

# Import UContext from main wrapper to avoid type conflicts
from .UContextWrapper import UContext

# Error checking callback
def _check_error(result, func, args):
    """
    Errcheck callback that automatically checks for Helios errors after each RadiationModel function call.
    This ensures that C++ exceptions are properly converted to Python exceptions.
    """
    check_helios_error(helios_lib.getLastErrorCode, helios_lib.getLastErrorMessage)
    return result

# Try to set up RadiationModel function prototypes
try:
    # RadiationModel creation and destruction
    helios_lib.createRadiationModel.argtypes = [ctypes.POINTER(UContext)]
    helios_lib.createRadiationModel.restype = ctypes.POINTER(URadiationModel)

    helios_lib.destroyRadiationModel.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.destroyRadiationModel.restype = None

    # Message control
    helios_lib.disableRadiationMessages.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.disableRadiationMessages.restype = None

    helios_lib.enableRadiationMessages.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.enableRadiationMessages.restype = None

    # Band management
    helios_lib.addRadiationBand.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p]
    helios_lib.addRadiationBand.restype = None

    helios_lib.addRadiationBandWithWavelengths.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_float, ctypes.c_float]
    helios_lib.addRadiationBandWithWavelengths.restype = None

    helios_lib.copyRadiationBand.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_char_p]
    helios_lib.copyRadiationBand.restype = None

    # Source management  
    helios_lib.addCollimatedRadiationSourceDefault.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.addCollimatedRadiationSourceDefault.restype = ctypes.c_uint

    helios_lib.addCollimatedRadiationSourceVec3.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.addCollimatedRadiationSourceVec3.restype = ctypes.c_uint

    helios_lib.addCollimatedRadiationSourceSpherical.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.addCollimatedRadiationSourceSpherical.restype = ctypes.c_uint

    helios_lib.addSphereRadiationSource.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.addSphereRadiationSource.restype = ctypes.c_uint

    helios_lib.addSunSphereRadiationSource.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float]
    helios_lib.addSunSphereRadiationSource.restype = ctypes.c_uint

    # Ray count configuration
    helios_lib.setDirectRayCount.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_size_t]
    helios_lib.setDirectRayCount.restype = None

    helios_lib.setDiffuseRayCount.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_size_t]
    helios_lib.setDiffuseRayCount.restype = None

    # Flux configuration
    helios_lib.setDiffuseRadiationFlux.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_float]
    helios_lib.setDiffuseRadiationFlux.restype = None

    helios_lib.setSourceFlux.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_uint, ctypes.c_char_p, ctypes.c_float]
    helios_lib.setSourceFlux.restype = None

    helios_lib.setSourceFluxMultiple.argtypes = [ctypes.POINTER(URadiationModel), ctypes.POINTER(ctypes.c_uint), ctypes.c_size_t, ctypes.c_char_p, ctypes.c_float]
    helios_lib.setSourceFluxMultiple.restype = None

    helios_lib.getSourceFlux.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_uint, ctypes.c_char_p]
    helios_lib.getSourceFlux.restype = ctypes.c_float

    # Scattering configuration
    helios_lib.setScatteringDepth.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_uint]
    helios_lib.setScatteringDepth.restype = None

    helios_lib.setMinScatterEnergy.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_float]
    helios_lib.setMinScatterEnergy.restype = None

    # Emission control
    helios_lib.disableEmission.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p]
    helios_lib.disableEmission.restype = None

    helios_lib.enableEmission.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p]
    helios_lib.enableEmission.restype = None

    # Geometry and simulation
    helios_lib.updateRadiationGeometry.argtypes = [ctypes.POINTER(URadiationModel)]
    helios_lib.updateRadiationGeometry.restype = None

    helios_lib.updateRadiationGeometryUUIDs.argtypes = [ctypes.POINTER(URadiationModel), ctypes.POINTER(ctypes.c_uint), ctypes.c_size_t]
    helios_lib.updateRadiationGeometryUUIDs.restype = None

    helios_lib.runRadiationBand.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p]
    helios_lib.runRadiationBand.restype = None

    helios_lib.runRadiationBandMultiple.argtypes = [ctypes.POINTER(URadiationModel), ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t]
    helios_lib.runRadiationBandMultiple.restype = None

    # Results and information
    helios_lib.getTotalAbsorbedFlux.argtypes = [ctypes.POINTER(URadiationModel), ctypes.POINTER(ctypes.c_size_t)]
    helios_lib.getTotalAbsorbedFlux.restype = ctypes.POINTER(ctypes.c_float)

    # Camera and Image Functions (v1.3.47)
    helios_lib.writeCameraImage.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, 
                                           ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                           ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_float]
    helios_lib.writeCameraImage.restype = ctypes.c_char_p

    helios_lib.writeNormCameraImage.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, 
                                               ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                               ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    helios_lib.writeNormCameraImage.restype = ctypes.c_char_p

    helios_lib.writeCameraImageData.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p, ctypes.c_char_p,
                                               ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    helios_lib.writeCameraImageData.restype = None

    # Bounding box functions
    helios_lib.writeImageBoundingBoxes.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                  ctypes.c_char_p, ctypes.c_uint, ctypes.c_char_p,
                                                  ctypes.c_char_p, ctypes.c_char_p]
    helios_lib.writeImageBoundingBoxes.restype = None

    helios_lib.writeImageBoundingBoxesVector.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                        ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                                        ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,
                                                        ctypes.c_char_p, ctypes.c_char_p]
    helios_lib.writeImageBoundingBoxesVector.restype = None

    helios_lib.writeImageBoundingBoxes_ObjectData.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                             ctypes.c_char_p, ctypes.c_uint, ctypes.c_char_p,
                                                             ctypes.c_char_p, ctypes.c_char_p]
    helios_lib.writeImageBoundingBoxes_ObjectData.restype = None

    helios_lib.writeImageBoundingBoxes_ObjectDataVector.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                                   ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                                                   ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,
                                                                   ctypes.c_char_p, ctypes.c_char_p]
    helios_lib.writeImageBoundingBoxes_ObjectDataVector.restype = None

    # Segmentation mask functions
    helios_lib.writeImageSegmentationMasks.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                       ctypes.c_char_p, ctypes.c_uint, ctypes.c_char_p,
                                                       ctypes.c_char_p, ctypes.c_int]
    helios_lib.writeImageSegmentationMasks.restype = None

    helios_lib.writeImageSegmentationMasksVector.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                            ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                                            ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,
                                                            ctypes.c_char_p, ctypes.c_int]
    helios_lib.writeImageSegmentationMasksVector.restype = None

    helios_lib.writeImageSegmentationMasks_ObjectData.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                                 ctypes.c_char_p, ctypes.c_uint, ctypes.c_char_p,
                                                                 ctypes.c_char_p, ctypes.c_int]
    helios_lib.writeImageSegmentationMasks_ObjectData.restype = None

    helios_lib.writeImageSegmentationMasks_ObjectDataVector.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                                                       ctypes.POINTER(ctypes.c_uint), ctypes.c_char_p,
                                                                       ctypes.c_char_p, ctypes.c_int]
    helios_lib.writeImageSegmentationMasks_ObjectDataVector.restype = None

    # Auto-calibration function
    helios_lib.autoCalibrateCameraImage.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
                                                    ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
    helios_lib.autoCalibrateCameraImage.restype = ctypes.c_char_p

    # Camera creation functions
    helios_lib.addRadiationCameraVec3.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                  ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                                  ctypes.c_float, ctypes.c_float, ctypes.c_float,
                                                  ctypes.c_float, ctypes.c_float, ctypes.c_float,
                                                  ctypes.POINTER(ctypes.c_float), ctypes.c_uint]
    helios_lib.addRadiationCameraVec3.restype = None

    helios_lib.addRadiationCameraSpherical.argtypes = [ctypes.POINTER(URadiationModel), ctypes.c_char_p,
                                                       ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t,
                                                       ctypes.c_float, ctypes.c_float, ctypes.c_float,
                                                       ctypes.c_float, ctypes.c_float, ctypes.c_float,
                                                       ctypes.POINTER(ctypes.c_float), ctypes.c_uint]
    helios_lib.addRadiationCameraSpherical.restype = None

    # Add automatic error checking to all RadiationModel functions
    helios_lib.createRadiationModel.errcheck = _check_error
    # Note: destroyRadiationModel doesn't need errcheck as it doesn't fail

    # Message control
    helios_lib.disableRadiationMessages.errcheck = _check_error
    helios_lib.enableRadiationMessages.errcheck = _check_error

    # Band management
    helios_lib.addRadiationBand.errcheck = _check_error
    helios_lib.addRadiationBandWithWavelengths.errcheck = _check_error
    helios_lib.copyRadiationBand.errcheck = _check_error

    # Source management
    helios_lib.addCollimatedRadiationSourceDefault.errcheck = _check_error
    helios_lib.addCollimatedRadiationSourceVec3.errcheck = _check_error
    helios_lib.addCollimatedRadiationSourceSpherical.errcheck = _check_error
    helios_lib.addSphereRadiationSource.errcheck = _check_error
    helios_lib.addSunSphereRadiationSource.errcheck = _check_error

    # Ray count configuration
    helios_lib.setDirectRayCount.errcheck = _check_error
    helios_lib.setDiffuseRayCount.errcheck = _check_error

    # Flux configuration
    helios_lib.setDiffuseRadiationFlux.errcheck = _check_error
    helios_lib.setSourceFlux.errcheck = _check_error
    helios_lib.setSourceFluxMultiple.errcheck = _check_error
    helios_lib.getSourceFlux.errcheck = _check_error

    # Scattering configuration
    helios_lib.setScatteringDepth.errcheck = _check_error
    helios_lib.setMinScatterEnergy.errcheck = _check_error

    # Emission control
    helios_lib.disableEmission.errcheck = _check_error
    helios_lib.enableEmission.errcheck = _check_error

    # Geometry and simulation
    helios_lib.updateRadiationGeometry.errcheck = _check_error
    helios_lib.updateRadiationGeometryUUIDs.errcheck = _check_error
    helios_lib.runRadiationBand.errcheck = _check_error
    helios_lib.runRadiationBandMultiple.errcheck = _check_error

    # Results and information
    helios_lib.getTotalAbsorbedFlux.errcheck = _check_error

    # Camera and Image Functions
    helios_lib.writeCameraImage.errcheck = _check_error
    helios_lib.writeNormCameraImage.errcheck = _check_error
    helios_lib.writeCameraImageData.errcheck = _check_error

    # Bounding box functions
    helios_lib.writeImageBoundingBoxes.errcheck = _check_error
    helios_lib.writeImageBoundingBoxesVector.errcheck = _check_error
    helios_lib.writeImageBoundingBoxes_ObjectData.errcheck = _check_error
    helios_lib.writeImageBoundingBoxes_ObjectDataVector.errcheck = _check_error

    # Segmentation mask functions
    helios_lib.writeImageSegmentationMasks.errcheck = _check_error
    helios_lib.writeImageSegmentationMasksVector.errcheck = _check_error
    helios_lib.writeImageSegmentationMasks_ObjectData.errcheck = _check_error
    helios_lib.writeImageSegmentationMasks_ObjectDataVector.errcheck = _check_error

    # Auto-calibration function
    helios_lib.autoCalibrateCameraImage.errcheck = _check_error

    # Camera creation functions
    helios_lib.addRadiationCameraVec3.errcheck = _check_error
    helios_lib.addRadiationCameraSpherical.errcheck = _check_error

    # Mark that RadiationModel functions are available
    _RADIATION_MODEL_FUNCTIONS_AVAILABLE = True

except AttributeError:
    # RadiationModel functions not available in current native library
    _RADIATION_MODEL_FUNCTIONS_AVAILABLE = False

# Python wrapper functions

def createRadiationModel(context):
    """Create a new RadiationModel instance"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        return None  # Return None for mock mode
    return helios_lib.createRadiationModel(context)

def destroyRadiationModel(radiation_model):
    """Destroy RadiationModel instance"""
    if radiation_model is None:
        return  # Destroying None is acceptable - no-op
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    helios_lib.destroyRadiationModel(radiation_model)

def disableMessages(radiation_model):
    """Disable RadiationModel status messages"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot disable messages.")
    helios_lib.disableRadiationMessages(radiation_model)

def enableMessages(radiation_model):
    """Enable RadiationModel status messages"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot enable messages.")
    helios_lib.enableRadiationMessages(radiation_model)

def addRadiationBand(radiation_model, label: str):
    """Add radiation band with label"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot add radiation band.")
    label_encoded = label.encode('utf-8')
    helios_lib.addRadiationBand(radiation_model, label_encoded)

def addRadiationBandWithWavelengths(radiation_model, label: str, wavelength_min: float, wavelength_max: float):
    """Add radiation band with wavelength bounds"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot add radiation band.")
    label_encoded = label.encode('utf-8')
    helios_lib.addRadiationBandWithWavelengths(radiation_model, label_encoded, wavelength_min, wavelength_max)

def copyRadiationBand(radiation_model, old_label: str, new_label: str):
    """Copy existing radiation band to new label"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot copy radiation band.")
    old_encoded = old_label.encode('utf-8')
    new_encoded = new_label.encode('utf-8')
    helios_lib.copyRadiationBand(radiation_model, old_encoded, new_encoded)

def addCollimatedRadiationSourceDefault(radiation_model):
    """Add default collimated radiation source"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addCollimatedRadiationSourceDefault(radiation_model)

def addCollimatedRadiationSourceVec3(radiation_model, x: float, y: float, z: float):
    """Add collimated radiation source with vec3 direction"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addCollimatedRadiationSourceVec3(radiation_model, x, y, z)

def addCollimatedRadiationSourceSpherical(radiation_model, radius: float, zenith: float, azimuth: float):
    """Add collimated radiation source with spherical direction"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addCollimatedRadiationSourceSpherical(radiation_model, radius, zenith, azimuth)

def addSphereRadiationSource(radiation_model, x: float, y: float, z: float, radius: float):
    """Add spherical radiation source"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addSphereRadiationSource(radiation_model, x, y, z, radius)

def addSunSphereRadiationSource(radiation_model, radius: float, zenith: float, azimuth: float, 
                               position_scaling: float, angular_width: float, flux_scaling: float):
    """Add sun sphere radiation source"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot create radiation source.")
    return helios_lib.addSunSphereRadiationSource(radiation_model, radius, zenith, azimuth, 
                                                 position_scaling, angular_width, flux_scaling)

def setDirectRayCount(radiation_model, label: str, count: int):
    """Set direct ray count for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set ray count.")
    label_encoded = label.encode('utf-8')
    helios_lib.setDirectRayCount(radiation_model, label_encoded, count)

def setDiffuseRayCount(radiation_model, label: str, count: int):
    """Set diffuse ray count for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set ray count.")
    label_encoded = label.encode('utf-8')
    helios_lib.setDiffuseRayCount(radiation_model, label_encoded, count)

def setDiffuseRadiationFlux(radiation_model, label: str, flux: float):
    """Set diffuse radiation flux for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set radiation flux.")
    label_encoded = label.encode('utf-8')
    helios_lib.setDiffuseRadiationFlux(radiation_model, label_encoded, flux)

def setSourceFlux(radiation_model, source_id: int, label: str, flux: float):
    """Set source flux for single source"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set source flux.")
    label_encoded = label.encode('utf-8')
    helios_lib.setSourceFlux(radiation_model, source_id, label_encoded, flux)

def setSourceFluxMultiple(radiation_model, source_ids: List[int], label: str, flux: float):
    """Set source flux for multiple sources"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set source flux.")
    label_encoded = label.encode('utf-8')
    source_array = (ctypes.c_uint * len(source_ids))(*source_ids)
    helios_lib.setSourceFluxMultiple(radiation_model, source_array, len(source_ids), label_encoded, flux)

def getSourceFlux(radiation_model, source_id: int, label: str) -> float:
    """Get source flux for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot get source flux.")
    label_encoded = label.encode('utf-8')
    return helios_lib.getSourceFlux(radiation_model, source_id, label_encoded)

def setScatteringDepth(radiation_model, label: str, depth: int):
    """Set scattering depth for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set scattering depth.")
    label_encoded = label.encode('utf-8')
    helios_lib.setScatteringDepth(radiation_model, label_encoded, depth)

def setMinScatterEnergy(radiation_model, label: str, energy: float):
    """Set minimum scatter energy for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot set scatter energy.")
    label_encoded = label.encode('utf-8')
    helios_lib.setMinScatterEnergy(radiation_model, label_encoded, energy)

def disableEmission(radiation_model, label: str):
    """Disable emission for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot disable emission.")
    label_encoded = label.encode('utf-8')
    helios_lib.disableEmission(radiation_model, label_encoded)

def enableEmission(radiation_model, label: str):
    """Enable emission for band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot enable emission.")
    label_encoded = label.encode('utf-8')
    helios_lib.enableEmission(radiation_model, label_encoded)

def updateGeometry(radiation_model):
    """Update all geometry in radiation model"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot update geometry.")
    helios_lib.updateRadiationGeometry(radiation_model)

def updateGeometryUUIDs(radiation_model, uuids: List[int]):
    """Update specific geometry UUIDs in radiation model"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot update geometry.")
    uuid_array = (ctypes.c_uint * len(uuids))(*uuids)
    helios_lib.updateRadiationGeometryUUIDs(radiation_model, uuid_array, len(uuids))

def runBand(radiation_model, label: str):
    """Run simulation for single band"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot run simulation.")
    label_encoded = label.encode('utf-8')
    helios_lib.runRadiationBand(radiation_model, label_encoded)

def runBandMultiple(radiation_model, labels: List[str]):
    """Run simulation for multiple bands"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot run simulation.")
    # Convert list of strings to array of c_char_p
    encoded_labels = [label.encode('utf-8') for label in labels]
    label_array = (ctypes.c_char_p * len(encoded_labels))(*encoded_labels)
    helios_lib.runRadiationBandMultiple(radiation_model, label_array, len(encoded_labels))

def getTotalAbsorbedFlux(radiation_model) -> List[float]:
    """Get total absorbed flux for all primitives"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot get absorbed flux.")
    size = ctypes.c_size_t()
    flux_ptr = helios_lib.getTotalAbsorbedFlux(radiation_model, ctypes.byref(size))
    return list(flux_ptr[:size.value])

#=============================================================================
# Camera and Image Functions (v1.3.47)
#=============================================================================

def writeCameraImage(radiation_model, camera: str, bands: List[str], imagefile_base: str, 
                     image_path: str = "./", frame: int = -1, flux_to_pixel_conversion: float = 1.0) -> str:
    """Write camera image to file and return output filename"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write camera image.")
    
    camera_encoded = camera.encode('utf-8')
    imagefile_base_encoded = imagefile_base.encode('utf-8')
    image_path_encoded = image_path.encode('utf-8')
    
    # Convert band list to ctypes array
    band_array = (ctypes.c_char_p * len(bands))()
    for i, band in enumerate(bands):
        band_array[i] = band.encode('utf-8')
    
    result = helios_lib.writeCameraImage(radiation_model, camera_encoded, band_array, len(bands),
                                        imagefile_base_encoded, image_path_encoded, frame, flux_to_pixel_conversion)
    return result.decode('utf-8') if result else ""

def writeNormCameraImage(radiation_model, camera: str, bands: List[str], imagefile_base: str, 
                         image_path: str = "./", frame: int = -1) -> str:
    """Write normalized camera image to file and return output filename"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write normalized camera image.")
    
    camera_encoded = camera.encode('utf-8')
    imagefile_base_encoded = imagefile_base.encode('utf-8')
    image_path_encoded = image_path.encode('utf-8')
    
    # Convert band list to ctypes array
    band_array = (ctypes.c_char_p * len(bands))()
    for i, band in enumerate(bands):
        band_array[i] = band.encode('utf-8')
    
    result = helios_lib.writeNormCameraImage(radiation_model, camera_encoded, band_array, len(bands),
                                            imagefile_base_encoded, image_path_encoded, frame)
    return result.decode('utf-8') if result else ""

def writeCameraImageData(radiation_model, camera: str, band: str, imagefile_base: str, 
                         image_path: str = "./", frame: int = -1):
    """Write camera image data to file (ASCII format)"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write camera image data.")
    
    camera_encoded = camera.encode('utf-8')
    band_encoded = band.encode('utf-8')
    imagefile_base_encoded = imagefile_base.encode('utf-8')
    image_path_encoded = image_path.encode('utf-8')
    
    helios_lib.writeCameraImageData(radiation_model, camera_encoded, band_encoded,
                                   imagefile_base_encoded, image_path_encoded, frame)

# Bounding box functions
def writeImageBoundingBoxes(radiation_model, camera_label: str, primitive_data_label: str, 
                           object_class_id: int, image_file: str, classes_txt_file: str = "classes.txt", 
                           image_path: str = "./"):
    """Write image bounding boxes (single primitive data label)"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write bounding boxes.")
    
    camera_encoded = camera_label.encode('utf-8')
    primitive_encoded = primitive_data_label.encode('utf-8')
    image_file_encoded = image_file.encode('utf-8')
    classes_encoded = classes_txt_file.encode('utf-8')
    image_path_encoded = image_path.encode('utf-8')
    
    helios_lib.writeImageBoundingBoxes(radiation_model, camera_encoded, primitive_encoded, object_class_id,
                                      image_file_encoded, classes_encoded, image_path_encoded)

def writeImageBoundingBoxesVector(radiation_model, camera_label: str, primitive_data_labels: List[str], 
                                  object_class_ids: List[int], image_file: str, 
                                  classes_txt_file: str = "classes.txt", image_path: str = "./"):
    """Write image bounding boxes (vector primitive data labels)"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write vector bounding boxes.")
    
    if len(primitive_data_labels) != len(object_class_ids):
        raise ValueError("primitive_data_labels and object_class_ids must have the same length")
    
    camera_encoded = camera_label.encode('utf-8')
    image_file_encoded = image_file.encode('utf-8')
    classes_encoded = classes_txt_file.encode('utf-8')
    image_path_encoded = image_path.encode('utf-8')
    
    # Convert lists to ctypes arrays
    label_array = (ctypes.c_char_p * len(primitive_data_labels))()
    for i, label in enumerate(primitive_data_labels):
        label_array[i] = label.encode('utf-8')
    
    id_array = (ctypes.c_uint * len(object_class_ids))(*object_class_ids)
    
    helios_lib.writeImageBoundingBoxesVector(radiation_model, camera_encoded, label_array, len(primitive_data_labels),
                                            id_array, image_file_encoded, classes_encoded, image_path_encoded)

def writeImageBoundingBoxes_ObjectData(radiation_model, camera_label: str, object_data_label: str, 
                                       object_class_id: int, image_file: str, 
                                       classes_txt_file: str = "classes.txt", image_path: str = "./"):
    """Write image bounding boxes with object data (single label)"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write object bounding boxes.")
    
    camera_encoded = camera_label.encode('utf-8')
    object_encoded = object_data_label.encode('utf-8')
    image_file_encoded = image_file.encode('utf-8')
    classes_encoded = classes_txt_file.encode('utf-8')
    image_path_encoded = image_path.encode('utf-8')
    
    helios_lib.writeImageBoundingBoxes_ObjectData(radiation_model, camera_encoded, object_encoded, object_class_id,
                                                 image_file_encoded, classes_encoded, image_path_encoded)

def writeImageBoundingBoxes_ObjectDataVector(radiation_model, camera_label: str, object_data_labels: List[str], 
                                             object_class_ids: List[int], image_file: str, 
                                             classes_txt_file: str = "classes.txt", image_path: str = "./"):
    """Write image bounding boxes with object data (vector labels)"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write vector object bounding boxes.")
    
    if len(object_data_labels) != len(object_class_ids):
        raise ValueError("object_data_labels and object_class_ids must have the same length")
    
    camera_encoded = camera_label.encode('utf-8')
    image_file_encoded = image_file.encode('utf-8')
    classes_encoded = classes_txt_file.encode('utf-8')
    image_path_encoded = image_path.encode('utf-8')
    
    # Convert lists to ctypes arrays
    label_array = (ctypes.c_char_p * len(object_data_labels))()
    for i, label in enumerate(object_data_labels):
        label_array[i] = label.encode('utf-8')
    
    id_array = (ctypes.c_uint * len(object_class_ids))(*object_class_ids)
    
    helios_lib.writeImageBoundingBoxes_ObjectDataVector(radiation_model, camera_encoded, label_array, len(object_data_labels),
                                                       id_array, image_file_encoded, classes_encoded, image_path_encoded)

# Segmentation mask functions
def writeImageSegmentationMasks(radiation_model, camera_label: str, primitive_data_label: str, 
                               object_class_id: int, json_filename: str, image_file: str, append_file: bool = False):
    """Write image segmentation masks (single primitive data label)"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write segmentation masks.")
    
    camera_encoded = camera_label.encode('utf-8')
    primitive_encoded = primitive_data_label.encode('utf-8')
    json_encoded = json_filename.encode('utf-8')
    image_file_encoded = image_file.encode('utf-8')
    
    helios_lib.writeImageSegmentationMasks(radiation_model, camera_encoded, primitive_encoded, object_class_id,
                                          json_encoded, image_file_encoded, int(append_file))

def writeImageSegmentationMasksVector(radiation_model, camera_label: str, primitive_data_labels: List[str], 
                                      object_class_ids: List[int], json_filename: str, image_file: str, 
                                      append_file: bool = False):
    """Write image segmentation masks (vector primitive data labels)"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write vector segmentation masks.")
    
    if len(primitive_data_labels) != len(object_class_ids):
        raise ValueError("primitive_data_labels and object_class_ids must have the same length")
    
    camera_encoded = camera_label.encode('utf-8')
    json_encoded = json_filename.encode('utf-8')
    image_file_encoded = image_file.encode('utf-8')
    
    # Convert lists to ctypes arrays
    label_array = (ctypes.c_char_p * len(primitive_data_labels))()
    for i, label in enumerate(primitive_data_labels):
        label_array[i] = label.encode('utf-8')
    
    id_array = (ctypes.c_uint * len(object_class_ids))(*object_class_ids)
    
    helios_lib.writeImageSegmentationMasksVector(radiation_model, camera_encoded, label_array, len(primitive_data_labels),
                                                id_array, json_encoded, image_file_encoded, int(append_file))

def writeImageSegmentationMasks_ObjectData(radiation_model, camera_label: str, object_data_label: str, 
                                           object_class_id: int, json_filename: str, image_file: str, 
                                           append_file: bool = False):
    """Write image segmentation masks with object data (single label)"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write object segmentation masks.")
    
    camera_encoded = camera_label.encode('utf-8')
    object_encoded = object_data_label.encode('utf-8')
    json_encoded = json_filename.encode('utf-8')
    image_file_encoded = image_file.encode('utf-8')
    
    helios_lib.writeImageSegmentationMasks_ObjectData(radiation_model, camera_encoded, object_encoded, object_class_id,
                                                     json_encoded, image_file_encoded, int(append_file))

def writeImageSegmentationMasks_ObjectDataVector(radiation_model, camera_label: str, object_data_labels: List[str], 
                                                 object_class_ids: List[int], json_filename: str, image_file: str, 
                                                 append_file: bool = False):
    """Write image segmentation masks with object data (vector labels)"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot write vector object segmentation masks.")
    
    if len(object_data_labels) != len(object_class_ids):
        raise ValueError("object_data_labels and object_class_ids must have the same length")
    
    camera_encoded = camera_label.encode('utf-8')
    json_encoded = json_filename.encode('utf-8')
    image_file_encoded = image_file.encode('utf-8')
    
    # Convert lists to ctypes arrays
    label_array = (ctypes.c_char_p * len(object_data_labels))()
    for i, label in enumerate(object_data_labels):
        label_array[i] = label.encode('utf-8')
    
    id_array = (ctypes.c_uint * len(object_class_ids))(*object_class_ids)
    
    helios_lib.writeImageSegmentationMasks_ObjectDataVector(radiation_model, camera_encoded, label_array, len(object_data_labels),
                                                           id_array, json_encoded, image_file_encoded, int(append_file))

# Auto-calibration function
def autoCalibrateCameraImage(radiation_model, camera_label: str, red_band_label: str, green_band_label: str, 
                            blue_band_label: str, output_file_path: str, print_quality_report: bool = False, 
                            algorithm: int = 1, ccm_export_file_path: str = "") -> str:
    """Auto-calibrate camera image with color correction and return output filename"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot auto-calibrate camera image.")
    
    camera_encoded = camera_label.encode('utf-8')
    red_encoded = red_band_label.encode('utf-8')
    green_encoded = green_band_label.encode('utf-8')
    blue_encoded = blue_band_label.encode('utf-8')
    output_encoded = output_file_path.encode('utf-8')
    ccm_encoded = ccm_export_file_path.encode('utf-8') if ccm_export_file_path else None
    
    result = helios_lib.autoCalibrateCameraImage(radiation_model, camera_encoded, red_encoded, green_encoded,
                                               blue_encoded, output_encoded, int(print_quality_report),
                                               algorithm, ccm_encoded)
    return result.decode('utf-8') if result else ""

# Camera creation functions
def addRadiationCameraVec3(radiation_model, camera_label: str, band_labels: List[str],
                          position_x: float, position_y: float, position_z: float,
                          lookat_x: float, lookat_y: float, lookat_z: float,
                          camera_properties: List[float], antialiasing_samples: int):
    """Add radiation camera with position and lookat vectors"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot add radiation camera.")

    if not band_labels:
        raise ValueError("At least one band label is required")
    if len(camera_properties) != 6:
        raise ValueError("camera_properties must contain exactly 6 values: [resolution_x, resolution_y, focal_distance, lens_diameter, HFOV, FOV_aspect_ratio]")

    # Encode camera label
    camera_encoded = camera_label.encode('utf-8')

    # Convert band labels to ctypes array
    band_array = (ctypes.c_char_p * len(band_labels))()
    for i, label in enumerate(band_labels):
        band_array[i] = label.encode('utf-8')

    # Convert camera properties to ctypes array
    props_array = (ctypes.c_float * len(camera_properties))(*camera_properties)

    helios_lib.addRadiationCameraVec3(radiation_model, camera_encoded, band_array, len(band_labels),
                                     ctypes.c_float(position_x), ctypes.c_float(position_y), ctypes.c_float(position_z),
                                     ctypes.c_float(lookat_x), ctypes.c_float(lookat_y), ctypes.c_float(lookat_z),
                                     props_array, ctypes.c_uint(antialiasing_samples))

def addRadiationCameraSpherical(radiation_model, camera_label: str, band_labels: List[str],
                               position_x: float, position_y: float, position_z: float,
                               radius: float, elevation: float, azimuth: float,
                               camera_properties: List[float], antialiasing_samples: int):
    """Add radiation camera with position and spherical viewing direction"""
    if not _RADIATION_MODEL_FUNCTIONS_AVAILABLE:
        raise RuntimeError("RadiationModel functions are not available. Native library missing or radiation plugin not enabled.")
    if radiation_model is None:
        raise ValueError("RadiationModel instance is None. Cannot add radiation camera.")

    if not band_labels:
        raise ValueError("At least one band label is required")
    if len(camera_properties) != 6:
        raise ValueError("camera_properties must contain exactly 6 values: [resolution_x, resolution_y, focal_distance, lens_diameter, HFOV, FOV_aspect_ratio]")

    # Encode camera label
    camera_encoded = camera_label.encode('utf-8')

    # Convert band labels to ctypes array
    band_array = (ctypes.c_char_p * len(band_labels))()
    for i, label in enumerate(band_labels):
        band_array[i] = label.encode('utf-8')

    # Convert camera properties to ctypes array
    props_array = (ctypes.c_float * len(camera_properties))(*camera_properties)

    helios_lib.addRadiationCameraSpherical(radiation_model, camera_encoded, band_array, len(band_labels),
                                          ctypes.c_float(position_x), ctypes.c_float(position_y), ctypes.c_float(position_z),
                                          ctypes.c_float(radius), ctypes.c_float(elevation), ctypes.c_float(azimuth),
                                          props_array, ctypes.c_uint(antialiasing_samples))

