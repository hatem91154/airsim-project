"""
AirSim settings data types represented as Python classes.
This module provides a class-based representation of AirSim settings.
"""
#%%

from typing import Dict, List, Optional, Union, Any
import json
import math
import copy


# Utility constants and functions
NaN = float('nan')


class ImageType:
    """Enum for image types, matches C++ ImageType enum."""
    
    # This indexes to array, -1 is special to indicate main camera
    Scene = 0
    DepthPlanar = 1
    DepthPerspective = 2
    DepthVis = 3
    DisparityNormalized = 4
    Segmentation = 5
    SurfaceNormals = 6
    Infrared = 7
    OpticalFlow = 8
    OpticalFlowVis = 9
    Annotation = 10
    Count = 11  # Must be last

class ImageTypeVehicle:
    """Enum for image types, matches C++ ImageType enum."""
    
    # This indexes to array, -1 is special to indicate main camera
    Scene = 0
    Count = 1  # Must be last




class JsonSerializable:
    """Base class for all settings classes that can be serialized to JSON."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary suitable for JSON serialization."""
        result = {}
        for key, value in self.__dict__.items():
            # Convert camelCase property names to match AirSim JSON format
            json_key = key[0].upper() + key[1:] if key[0].islower() else key
            
            if isinstance(value, JsonSerializable):
                result[json_key] = value.to_dict()
            elif isinstance(value, list):
                result[json_key] = [
                    item.to_dict() if isinstance(item, JsonSerializable) else item
                    for item in value
                ]
            elif isinstance(value, dict):
                result[json_key] = {
                    k: v.to_dict() if isinstance(v, JsonSerializable) else v
                    for k, v in value.items()
                }
            else:
                result[json_key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JsonSerializable':
        """Create an instance from a dictionary."""
        # Default implementation - override in subclasses
        instance = cls()
        for key, value in data.items():
            # Convert JSON keys to Python property names (first letter lowercase)
            py_key = key[0].lower() + key[1:] if key[0].isupper() else key
            setattr(instance, py_key, value)
        return instance
    
    def to_json(self, indent=2) -> str:
        """Convert the object to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

# 1. Basic Data Types
class Vector3r(JsonSerializable):
    """Represents a 3D vector (X, Y, Z)."""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.X = x
        self.Y = y
        self.Z = z
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Vector3r':
        return cls(
            x=data.get('X', 0.0),
            y=data.get('Y', 0.0),
            z=data.get('Z', 0.0)
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "X": self.X,
            "Y": self.Y,
            "Z": self.Z
        }


class Rotation(JsonSerializable):
    """Represents rotation in terms of Yaw, Pitch, Roll."""
    
    def __init__(self, yaw: float = 0.0, pitch: float = 0.0, roll: float = 0.0):
        self.Yaw = yaw
        self.Pitch = pitch
        self.Roll = roll
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Rotation':
        return cls(
            yaw=data.get('Yaw', 0.0),
            pitch=data.get('Pitch', 0.0),
            roll=data.get('Roll', 0.0)
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "Yaw": self.Yaw,
            "Pitch": self.Pitch,
            "Roll": self.Roll
        }


class Pose(JsonSerializable):
    """Represents position and rotation."""
    
    def __init__(self, position: Vector3r = None, rotation: Rotation = None):
        self.Position = position or Vector3r()
        self.Rotation = rotation or Rotation()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pose':
        position = Vector3r.from_dict(data) if 'X' in data else Vector3r()
        rotation = Rotation.from_dict(data) if 'Yaw' in data else Rotation()
        return cls(position=position, rotation=rotation)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        result.update(self.Position.to_dict())
        result.update(self.Rotation.to_dict())
        return result


class Wind(Vector3r):
    """Represents wind as a 3D vector."""
    
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        super().__init__(x, y, z)


# 2. Core Settings Structures
class SubwindowSetting(JsonSerializable):
    """Sub-window settings."""
    
    def __init__(self, window_id: int = 0, image_type: int = 0, visible: bool = False,
                 camera_name: str = "", vehicle_name: str = "", annotation: str = ""):
        self.WindowID = window_id
        self.ImageType = image_type
        self.Visible = visible
        self.CameraName = camera_name
        self.VehicleName = vehicle_name
        self.Annotation = annotation
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubwindowSetting':
        return cls(
            window_id=data.get('WindowID', 0),
            image_type=data.get('ImageType', 0),
            visible=data.get('Visible', False),
            camera_name=data.get('CameraName', ""),
            vehicle_name=data.get('VehicleName', ""),
            annotation=data.get('Annotation', "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "WindowID": self.WindowID,
            "ImageType": self.ImageType,
            "Visible": self.Visible,
            "CameraName": self.CameraName,
            "VehicleName": self.VehicleName,
            "Annotation": self.Annotation
        }


class RCSettings(JsonSerializable):
    """Remote control settings."""
    
    def __init__(self, remote_control_id: int = 0, allow_api_when_disconnected: bool = True):
        self.RemoteControlID = remote_control_id
        self.AllowAPIWhenDisconnected = allow_api_when_disconnected
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RCSettings':
        return cls(
            remote_control_id=data.get('RemoteControlID', 0),
            allow_api_when_disconnected=data.get('AllowAPIWhenDisconnected', True)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "RemoteControlID": self.RemoteControlID,
            "AllowAPIWhenDisconnected": self.AllowAPIWhenDisconnected
        }


# 3. Camera-Related Settings
class CaptureSetting(JsonSerializable):
    """Camera capture settings."""
    def __init__(self, image_type: int = 0, width: int = 256, height: int = 144,
                 fov_degrees: float = 90.0, auto_exposure_method: int = -1,
                 auto_exposure_speed: float = float('nan'), auto_exposure_bias: float = float('nan'),
                 auto_exposure_max_brightness: float = float('nan'), auto_exposure_min_brightness: float = float('nan'),
                 auto_exposure_low_percent: float = float('nan'), auto_exposure_high_percent: float = float('nan'),
                 auto_exposure_histogram_log_min: float = float('nan'), auto_exposure_histogram_log_max: float = float('nan'),
                 motion_blur_amount: float = float('nan'), motion_blur_max: float = float('nan'),
                 target_gamma: float = float('nan'), projection_mode: int = 0,
                 ortho_width: float = float('nan'), chromatic_aberration_scale: float = float('nan'),
                 ignore_marked: bool = False, lumen_gi_enable: bool = False,
                 lumen_reflection_enable: bool = False, lumen_final_quality: float = 1,
                 lumen_scene_detail: float = 1.0, lumen_scene_lightning_detail: float = 1):
        self.ImageType = image_type
        self.Width = width
        self.Height = height
        self.FOV_Degrees = fov_degrees
        self.AutoExposureMethod = auto_exposure_method
        self.AutoExposureSpeed = auto_exposure_speed
        self.AutoExposureBias = auto_exposure_bias
        self.AutoExposureMaxBrightness = auto_exposure_max_brightness
        self.AutoExposureMinBrightness = auto_exposure_min_brightness
        self.AutoExposureLowPercent = auto_exposure_low_percent
        self.AutoExposureHighPercent = auto_exposure_high_percent
        self.AutoExposureHistogramLogMin = auto_exposure_histogram_log_min
        self.AutoExposureHistogramLogMax = auto_exposure_histogram_log_max
        self.MotionBlurAmount = motion_blur_amount
        self.MotionBlurMax = motion_blur_max
        self.TargetGamma = target_gamma
        self.ProjectionMode = projection_mode
        self.OrthoWidth = ortho_width
        self.ChromaticAberrationScale = chromatic_aberration_scale
        self.IgnoreMarked = ignore_marked
        self.LumenGIEnable = lumen_gi_enable
        self.LumenReflectionEnable = lumen_reflection_enable
        self.LumenFinalQuality = lumen_final_quality
        self.LumenSceneDetail = lumen_scene_detail
        self.LumenSceneLightningDetail = lumen_scene_lightning_detail

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CaptureSetting':
        return cls(
            image_type=data.get('ImageType', 0),
            width=data.get('Width', 256),
            height=data.get('Height', 144),
            fov_degrees=data.get('FOV_Degrees', float('nan')),
            auto_exposure_method=data.get('AutoExposureMethod', -1),
            auto_exposure_speed=data.get('AutoExposureSpeed', float('nan')),
            auto_exposure_bias=data.get('AutoExposureBias', float('nan')),
            auto_exposure_max_brightness=data.get('AutoExposureMaxBrightness', float('nan')),
            auto_exposure_min_brightness=data.get('AutoExposureMinBrightness', float('nan')),
            auto_exposure_low_percent=data.get('AutoExposureLowPercent', float('nan')),
            auto_exposure_high_percent=data.get('AutoExposureHighPercent', float('nan')),
            auto_exposure_histogram_log_min=data.get('AutoExposureHistogramLogMin', float('nan')),
            auto_exposure_histogram_log_max=data.get('AutoExposureHistogramLogMax', float('nan')),
            motion_blur_amount=data.get('MotionBlurAmount', float('nan')),
            motion_blur_max=data.get('MotionBlurMax', float('nan')),
            target_gamma=data.get('TargetGamma', float('nan')),
            projection_mode=data.get('ProjectionMode', 0),
            ortho_width=data.get('OrthoWidth', float('nan')),
            chromatic_aberration_scale=data.get('ChromaticAberrationScale', float('nan')),
            ignore_marked=data.get('IgnoreMarked', False),
            lumen_gi_enable=data.get('LumenGIEnable', False),
            lumen_reflection_enable=data.get('LumenReflectionEnable', False),
            lumen_final_quality=data.get('LumenFinalQuality', 1),
            lumen_scene_detail=data.get('LumenSceneDetail', 1.0),
            lumen_scene_lightning_detail=data.get('LumenSceneLightningDetail', 1)
        )

class CaptureSettingVehicle(JsonSerializable):
    """Simplified capture settings for vehicles."""
    def __init__(self, image_type: int = 0, width: int = 256, height: int = 144, fov_degrees: float = 90.0):
        self.ImageType = image_type
        self.Width = width
        self.Height = height
        self.FOV_Degrees = fov_degrees

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CaptureSettingVehicle':
        return cls(
            image_type=data.get('ImageType', 0),
            width=data.get('Width', 256),
            height=data.get('Height', 144),
            fov_degrees=data.get('FOV_Degrees', float('nan'))
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ImageType": self.ImageType,
            "Width": self.Width,
            "Height": self.Height,
            "FOV_Degrees": self.FOV_Degrees
        }



class NoiseSetting(JsonSerializable):
    """Noise settings for camera images."""
    def __init__(self, image_type: int = 0, enabled: bool = False, rand_contrib: float = 0.2,
                 rand_speed: float = 100000.0, rand_size: float = 500.0, rand_density: float = 2.0,
                 horz_wave_contrib: float = 0.03, horz_wave_strength: float = 0.08,
                 horz_wave_vert_size: float = 1.0, horz_wave_screen_size: float = 1.0,
                 horz_noise_lines_contrib: float = 1.0, horz_noise_lines_density_y: float = 0.01,
                 horz_noise_lines_density_xy: float = 0.5, horz_distortion_contrib: float = 1.0,
                 horz_distortion_strength: float = 0.002, lens_distortion_enable: bool = False,
                 lens_distortion_area_falloff: float = 1.0, lens_distortion_area_radius: float = 1.0,
                 lens_distortion_intensity: float = 0.5, lens_distortion_invert: bool = False):
        self.ImageType = image_type
        self.Enabled = enabled
        self.RandContrib = rand_contrib
        self.RandSpeed = rand_speed
        self.RandSize = rand_size
        self.RandDensity = rand_density
        self.HorzWaveContrib = horz_wave_contrib
        self.HorzWaveStrength = horz_wave_strength
        self.HorzWaveVertSize = horz_wave_vert_size
        self.HorzWaveScreenSize = horz_wave_screen_size
        self.HorzNoiseLinesContrib = horz_noise_lines_contrib
        self.HorzNoiseLinesDensityY = horz_noise_lines_density_y
        self.HorzNoiseLinesDensityXY = horz_noise_lines_density_xy
        self.HorzDistortionContrib = horz_distortion_contrib
        self.HorzDistortionStrength = horz_distortion_strength
        self.LensDistortionEnable = lens_distortion_enable
        self.LensDistortionAreaFalloff = lens_distortion_area_falloff
        self.LensDistortionAreaRadius = lens_distortion_area_radius
        self.LensDistortionIntensity = lens_distortion_intensity
        self.LensDistortionInvert = lens_distortion_invert

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NoiseSetting':
        return cls(
            image_type=data.get('ImageType', 0),
            enabled=data.get('Enabled', False),
            rand_contrib=data.get('RandContrib', 0.2),
            rand_speed=data.get('RandSpeed', 100000.0),
            rand_size=data.get('RandSize', 500.0),
            rand_density=data.get('RandDensity', 2),
            horz_wave_contrib=data.get('HorzWaveContrib', 0.03),
            horz_wave_strength=data.get('HorzWaveStrength', 0.08),
            horz_wave_vert_size=data.get('HorzWaveVertSize', 1.0),
            horz_wave_screen_size=data.get('HorzWaveScreenSize', 1.0),
            horz_noise_lines_contrib=data.get('HorzNoiseLinesContrib', 1.0),
            horz_noise_lines_density_y=data.get('HorzNoiseLinesDensityY', 0.01),
            horz_noise_lines_density_xy=data.get('HorzNoiseLinesDensityXY', 0.5),
            horz_distortion_contrib=data.get('HorzDistortionContrib', 1.0),
            horz_distortion_strength=data.get('HorzDistortionStrength', 0.002),
            lens_distortion_enable=data.get('LensDistortionEnable', True),
            lens_distortion_area_falloff=data.get('LensDistortionAreaFalloff', 2),
            lens_distortion_area_radius=data.get('LensDistortionAreaRadius', 1),
            lens_distortion_intensity=data.get('LensDistortionIntensity', 0.5),
            lens_distortion_invert=data.get('LensDistortionInvert', False)
        )


class GimbalSetting(JsonSerializable):
    """Gimbal settings for cameras."""
    
    def __init__(self, stabilization: int = 0, rotation: Rotation = None):
        self.Stabilization = stabilization
        self.Rotation = rotation or Rotation(NaN, NaN, NaN)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"Stabilization": self.Stabilization}
        result.update(self.Rotation.to_dict())
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GimbalSetting':
        rotation = Rotation(
            pitch=data.get('Pitch', NaN),
            roll=data.get('Roll', NaN),
            yaw=data.get('Yaw', NaN)
        )
        return cls(
            stabilization=data.get('Stabilization', 0),
            rotation=rotation
        )


class PixelFormatOverrideSetting(JsonSerializable):
    """Pixel format override settings."""
    def __init__(self, pixel_format: int = 0):
        self.PixelFormat = pixel_format

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PixelFormatOverrideSetting':
        return cls(
            pixel_format=data.get('PixelFormat', 0)
        )


class UnrealEngineSetting(JsonSerializable):
    """Unreal Engine specific settings."""
    def __init__(self, pixel_format_overrides: List[PixelFormatOverrideSetting] = None):
        self.PixelFormatOverride = pixel_format_overrides or [PixelFormatOverrideSetting()]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnrealEngineSetting':
        pixel_format_overrides = [
            PixelFormatOverrideSetting.from_dict(override) 
            for override in data.get('PixelFormatOverride', [])
        ] or [PixelFormatOverrideSetting()]
        return cls(pixel_format_overrides=pixel_format_overrides)

class CameraSetting(JsonSerializable):
    def __init__(self,
                 position: Vector3r = None,
                 rotation: Rotation = None,
                 external: bool = False,
                 external_ned: bool = True,
                 draw_sensor: bool = False,
                 gimbal: GimbalSetting = None,
                 capture_settings: Dict[int, CaptureSetting] = None,
                 noise_settings: Dict[int, NoiseSetting] = None,
                 ue_setting: UnrealEngineSetting = None):
        self.Position = position or Vector3r(0, 0, 0)
        self.Rotation = rotation or Rotation(0, 0, 0)
        self.External = external
        self.ExternalNed = external_ned
        self.DrawSensor = draw_sensor
        self.Gimbal = gimbal or GimbalSetting()
        self.CaptureSettings = capture_settings or {}
        self.NoiseSettings = noise_settings or {}
        # self.UeSetting = ue_setting or UnrealEngineSetting()

        if not self.CaptureSettings:
            self._initialize_capture_settings()
        if not self.NoiseSettings:
            self._initialize_noise_settings()

    def _initialize_capture_settings(self):
        self.CaptureSettings.clear()
        for i in range(-1, ImageType.Count):
            self.CaptureSettings[i] = CaptureSetting(image_type=i)
        if 0 in self.CaptureSettings:
            self.CaptureSettings[0].TargetGamma = 1.4

    def _initialize_noise_settings(self):
        self.NoiseSettings.clear()
        for i in range(-1, ImageType.Count):
            self.NoiseSettings[i] = NoiseSetting(image_type=i)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "External": self.External,
            "ExternalNed": self.ExternalNed,
            "DrawSensor": self.DrawSensor,
            "Gimbal": self.Gimbal.to_dict(),
            "CaptureSettings": [
                {"ImageType": k, **v.to_dict()} for k, v in self.CaptureSettings.items()
            ],
            "NoiseSettings": [
                {"ImageType": k, **v.to_dict()} for k, v in self.NoiseSettings.items()
            ]
        }
        result.update({
            "X": self.Position.X, "Y": self.Position.Y, "Z": self.Position.Z,
            "Pitch": self.Rotation.Pitch, "Roll": self.Rotation.Roll, "Yaw": self.Rotation.Yaw
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraSetting':
        position = Vector3r(
            x=data.get('X', 0.0),
            y=data.get('Y', 0.0),
            z=data.get('Z', 0.0)
        )
        rotation = Rotation(
            yaw=data.get('Yaw', 0.0),
            pitch=data.get('Pitch', 0.0),
            roll=data.get('Roll', 0.0)
        )
        gimbal = GimbalSetting.from_dict(data.get("Gimbal", {}))

        capture_settings = {}
        for cs in data.get("CaptureSettings", []):
            image_type = cs.get("ImageType", 0)
            capture_settings[image_type] = CaptureSetting.from_dict(cs)

        noise_settings = {}
        for ns in data.get("NoiseSettings", []):
            image_type = ns.get("ImageType", 0)
            noise_settings[image_type] = NoiseSetting.from_dict(ns)

        # ue_setting = UnrealEngineSetting.from_dict(data.get("UnrealEngine", {}))

        return cls(
            position=position,
            rotation=rotation,
            external=data.get("External", False),
            external_ned=data.get("ExternalNed", True),
            draw_sensor=data.get("DrawSensor", False),
            gimbal=gimbal,
            capture_settings=capture_settings,
            noise_settings=noise_settings,
            # ue_setting=ue_setting
        )

class CameraSettingVechile(JsonSerializable):
    def __init__(self,
                 position: Vector3r = None,
                 rotation: Rotation = None,
                 gimbal: GimbalSetting = None,
                 capture_settings: Dict[int, CaptureSettingVehicle] = None):
        self.Position = position or Vector3r(0, 0, 0)
        self.Rotation = rotation or Rotation(0, 0, 0)
        self.Gimbal = gimbal or GimbalSetting()
        self.CaptureSettings = capture_settings or {}

        if not self.CaptureSettings:
            self._initialize_capture_settings()

    def _initialize_capture_settings(self):
        self.CaptureSettings.clear()
        for i in range(-1, ImageTypeVehicle.Count):
            self.CaptureSettings[i] = CaptureSettingVehicle(image_type=i)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "Gimbal": self.Gimbal.to_dict(),
            "CaptureSettings": [
                {"ImageType": k, **v.to_dict()} for k, v in self.CaptureSettings.items()
            ],
        }
        result.update({
            "X": self.Position.X, "Y": self.Position.Y, "Z": self.Position.Z,
            "Pitch": self.Rotation.Pitch, "Roll": self.Rotation.Roll, "Yaw": self.Rotation.Yaw
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraSettingVechile':
        position = Vector3r(
            x=data.get('X', 0.0),
            y=data.get('Y', 0.0),
            z=data.get('Z', 0.0)
        )
        rotation = Rotation(
            yaw=data.get('Yaw', 0.0),
            pitch=data.get('Pitch', 0.0),
            roll=data.get('Roll', 0.0)
        )
        gimbal = GimbalSetting.from_dict(data.get("Gimbal", {}))

        capture_settings = {}
        for cs in data.get("CaptureSettings", []):
            image_type = cs.get("ImageType", 0)
            capture_settings[image_type] = CaptureSettingVehicle.from_dict(cs)

        return cls(
            position=position,
            rotation=rotation,
            gimbal=gimbal,
            capture_settings=capture_settings,
        )


class CameraDirectorSetting(JsonSerializable):
    """Settings for the camera director in AirSim."""

    def __init__(self, follow_distance: float = -3, 
                 position: Vector3r = None, 
                 rotation: Rotation = None):
        self.FollowDistance = follow_distance
        self.Position = position or Vector3r(0, 0, 0)
        self.Rotation = rotation or Rotation(0, 0, 0)

    def to_dict(self) -> Dict[str, Any]:
        result = {"FollowDistance": self.FollowDistance}
        result.update(self.Position.to_dict())
        result.update(self.Rotation.to_dict())
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CameraDirectorSetting':
        position = Vector3r.from_dict(data)
        rotation = Rotation.from_dict(data)
        return cls(
            follow_distance=data.get('FollowDistance', -3),
            position=position,
            rotation=rotation
        )

class VehicleSetting(JsonSerializable):
    """Vehicle settings."""

    def __init__(self, vehicle_type: str = "", default_vehicle_state: str = "",
                 auto_create: bool = True, pawn_path: str = "",
                 enable_collision_passthrough: bool = False, enable_collisions: bool = True,
                 allow_api_always: bool = True, enable_trace: bool = False,
                 rc: RCSettings = None, cameras: Dict[str, CameraSettingVechile] = None,
                 pose: Pose = None):
        self.VehicleType = vehicle_type
        self.DefaultVehicleState = default_vehicle_state
        self.AutoCreate = auto_create
        self.PawnPath = pawn_path
        self.EnableCollisionPassthrough = enable_collision_passthrough
        self.EnableCollisions = enable_collisions
        self.AllowAPIAlways = allow_api_always
        self.EnableTrace = enable_trace
        self.RC = rc or RCSettings()
        self.Cameras = cameras or {}
        self.Pose = pose or Pose()

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "VehicleType": self.VehicleType,
            "DefaultVehicleState": self.DefaultVehicleState,
            "AutoCreate": self.AutoCreate,
            "PawnPath": self.PawnPath,
            "EnableCollisionPassthrough": self.EnableCollisionPassthrough,
            "EnableCollisions": self.EnableCollisions,
            "AllowAPIAlways": self.AllowAPIAlways,
            "EnableTrace": self.EnableTrace,
            "RC": self.RC.to_dict(),
            "Cameras": {
                name: camera.to_dict() for name, camera in self.Cameras.items()
            }
        }
        result.update(self.Pose.to_dict())
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VehicleSetting':
        rc = RCSettings.from_dict(data.get('RC', {})) if 'RC' in data else RCSettings()

        cameras = {}
        if 'Cameras' in data and isinstance(data['Cameras'], dict):
            for name, camera_data in data['Cameras'].items():
                cameras[name] = CameraSettingVechile.from_dict(camera_data)

        pose = Pose.from_dict(data)

        return cls(
            vehicle_type=data.get('VehicleType', ""),
            default_vehicle_state=data.get('DefaultVehicleState', ""),
            auto_create=data.get('AutoCreate', True),
            pawn_path=data.get('PawnPath', ""),
            enable_collision_passthrough=data.get('EnableCollisionPassthrough', False),
            enable_collisions=data.get('EnableCollisions', True),
            allow_api_always=data.get('AllowAPIAlways', True),
            enable_trace=data.get('EnableTrace', False),
            rc=rc,
            cameras=cameras,
            pose=pose
        )

# 6. Environment Settings
class OriginGeopoint(JsonSerializable):
    """Geographic origin point settings."""
    def __init__(self, latitude: float = 47.641468, longitude: float = -122.140165, 
                 altitude: float = 122):
        self.Latitude = latitude
        self.Longitude = longitude
        self.Altitude = altitude

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OriginGeopoint':
        return cls(
            latitude=data.get('Latitude', 47.641468),
            longitude=data.get('Longitude', -122.140165),
            altitude=data.get('Altitude', 122)
        )


class TimeOfDaySetting(JsonSerializable):
    """Time of day settings for simulation."""
    def __init__(self, enabled: bool = False, start_date_time: str = "",
                 celestial_clock_speed: float = 1, start_date_time_dst: bool = False,
                 update_interval_secs: int = 60):
        self.Enabled = enabled
        self.StartDateTime = start_date_time
        self.CelestialClockSpeed = celestial_clock_speed
        self.StartDateTimeDst = start_date_time_dst
        self.UpdateIntervalSecs = update_interval_secs

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeOfDaySetting':
        return cls(
            enabled=data.get('Enabled', False),
            start_date_time=data.get('StartDateTime', ""),
            celestial_clock_speed=data.get('CelestialClockSpeed', 1),
            start_date_time_dst=data.get('StartDateTimeDst', False),
            update_interval_secs=data.get('UpdateIntervalSecs', 60)
        )

#%%
# 7. Main Container Class
class AirSimSettings(JsonSerializable):
    """Main AirSim settings class."""

    def __init__(self, sim_mode: str = "", clock_type: str = "", clock_speed: int = 1,
                 local_host_ip: str = "127.0.0.1", api_server_port: int = 41451,
                 record_ui_visible: bool = True, move_world_origin: bool = False,
                 initial_instance_segmentation: bool = True, log_messages_visible: bool = True,
                 show_los_debug_lines: bool = False, view_mode: str = "",
                 rpc_enabled: bool = True, engine_sound: bool = True,
                 physics_engine_name: str = "", speed_unit_factor: float = 1.0,
                 speed_unit_label: str = "m/s", wind: Vector3r = None,
                 camera_director: CameraDirectorSetting = None, camera_defaults: CameraSetting = None, 
                 origin_geopoint: OriginGeopoint = None, time_of_day: TimeOfDaySetting = None, 
                 sub_windows: List[SubwindowSetting] = None, vehicles: Dict[str, VehicleSetting] = None):

        self.SimMode = sim_mode
        self.ClockType = clock_type
        self.ClockSpeed = clock_speed
        self.LocalHostIp = local_host_ip
        self.ApiServerPort = api_server_port
        self.RecordUIVisible = record_ui_visible
        self.MoveWorldOrigin = move_world_origin
        self.InitialInstanceSegmentation = initial_instance_segmentation
        self.LogMessagesVisible = log_messages_visible
        self.ShowLosDebugLines = show_los_debug_lines
        self.ViewMode = view_mode
        self.RpcEnabled = rpc_enabled
        self.EngineSound = engine_sound
        self.PhysicsEngineName = physics_engine_name
        self.SpeedUnitFactor = speed_unit_factor
        self.SpeedUnitLabel = speed_unit_label
        self.Wind = wind or Vector3r()
        self.CameraDirector = camera_director or CameraDirectorSetting()
        self.CameraDefaults = camera_defaults or CameraSetting()
        self.OriginGeopoint = origin_geopoint or OriginGeopoint()
        self.TimeOfDay = time_of_day or TimeOfDaySetting()

        if sub_windows is None:
            self.SubWindows = [
                SubwindowSetting(0, "0", 3, "", False),
                SubwindowSetting(1, "0", 5, "", False),
                SubwindowSetting(2, "0", 0, "", False)
            ]
        else:
            self.SubWindows = sub_windows

        if vehicles is None:
            self.Vehicles = {
                "SimpleFlight": VehicleSetting(
                    vehicle_type="SimpleFlight",
                    default_vehicle_state="Armed",
                    auto_create=True
                )
            }
        else:
            self.Vehicles = vehicles

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AirSimSettings':
        wind = Vector3r.from_dict(data.get('Wind', {}))
        camera_director = CameraDirectorSetting.from_dict(data.get('CameraDirector', {}))
        camera_defaults = CameraSetting.from_dict(data.get('CameraDefaults', {}))
        origin_geopoint = OriginGeopoint.from_dict(data.get('OriginGeopoint', {}))
        time_of_day = TimeOfDaySetting.from_dict(data.get('TimeOfDay', {}))

        sub_windows = []
        for window_data in data.get('SubWindows', []):
            sub_windows.append(SubwindowSetting.from_dict(window_data))

        vehicles = {}
        for name, vehicle_data in data.get('Vehicles', {}).items():
            vehicles[name] = VehicleSetting.from_dict(vehicle_data)

        return cls(
            sim_mode=data.get('SimMode', ""),
            clock_type=data.get('ClockType', ""),
            clock_speed=data.get('ClockSpeed', 1),
            local_host_ip=data.get('LocalHostIp', "127.0.0.1"),
            api_server_port=data.get('ApiServerPort', 41451),
            record_ui_visible=data.get('RecordUIVisible', True),
            move_world_origin=data.get('MoveWorldOrigin', False),
            initial_instance_segmentation=data.get('InitialInstanceSegmentation', True),
            log_messages_visible=data.get('LogMessagesVisible', True),
            show_los_debug_lines=data.get('ShowLosDebugLines', False),
            view_mode=data.get('ViewMode', ""),
            rpc_enabled=data.get('RpcEnabled', True),
            engine_sound=data.get('EngineSound', True),
            physics_engine_name=data.get('PhysicsEngineName', ""),
            speed_unit_factor=data.get('SpeedUnitFactor', 1.0),
            speed_unit_label=data.get('SpeedUnitLabel', "m/s"),
            wind=wind,
            camera_director=camera_director,
            camera_defaults=camera_defaults,
            origin_geopoint=origin_geopoint,
            time_of_day=time_of_day,
            sub_windows=sub_windows,
            vehicles=vehicles
        )

    @classmethod
    def load_from_file(cls, file_path: str) -> 'AirSimSettings':
        """Load settings from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save_to_file(self, file_path: str, indent: int = 2) -> None:
        """Save settings to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=indent)

# Utility functions for conversion between dict and class representations
def convert_dict_to_settings(settings_dict: Dict[str, Any]) -> AirSimSettings:
    """
    Convert a dictionary representation of AirSim settings to a class-based model.
    
    Args:
        settings_dict: Dictionary containing AirSim settings
        
    Returns:
        An AirSimSettings object initialized with the values from the dictionary
    """
    if not settings_dict:
        return AirSimSettings()
    
    return AirSimSettings.from_dict(settings_dict)


def convert_settings_to_dict(settings: AirSimSettings) -> Dict[str, Any]:
    """
    Convert a class-based AirSimSettings object to a dictionary representation.
    
    Args:
        settings: AirSimSettings object
        
    Returns:
        A dictionary containing the AirSim settings
    """
    if not settings:
        return {}
        
    return settings.to_dict()


def update_settings_dict_from_classes(settings_dict: Dict[str, Any], 
                                      settings_obj: AirSimSettings) -> Dict[str, Any]:
    """
    Update an existing settings dictionary with values from a class-based
    This is useful when you want to preserve any custom fields that might not be
    represented in the class model.
    
    Args:
        settings_dict: The original dictionary to update
        settings_obj: The AirSimSettings object with new values
        
    Returns:
        The updated dictionary
    """
    if not settings_obj:
        return settings_dict
    
    # Create a deep copy to avoid modifying the original
    result = copy.deepcopy(settings_dict) if settings_dict else {}
    
    # Update with values from the class model
    class_dict = settings_obj.to_dict()
    
    # Recursive helper function to update nested dictionaries
    def update_dict_recursive(target, source):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # If both are dictionaries, merge them recursively
                update_dict_recursive(target[key], value)
            else:
                # Otherwise, update or add the value
                target[key] = copy.deepcopy(value)
    
    # Update the dictionary
    update_dict_recursive(result, class_dict)
    
    return result


def create_default_settings() -> AirSimSettings:
    """
    Create a new AirSimSettings object with default values.
    
    Returns:
        A new AirSimSettings object with default values
    """
    return AirSimSettings(
        sim_mode="Multirotor",
        vehicles={
            "SimpleFlight": VehicleSetting(
                vehicle_type="SimpleFlight",
                default_vehicle_state="Armed",
                auto_create=True
            )
        }
    )





