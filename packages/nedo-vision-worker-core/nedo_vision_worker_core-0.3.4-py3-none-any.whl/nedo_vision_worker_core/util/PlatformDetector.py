import os
import platform
import sys
import torch


class PlatformDetector:
    """
    Detects platform and multimedia stack capabilities.
    """

    @staticmethod
    def is_linux() -> bool:
        return sys.platform.startswith("linux")

    @staticmethod
    def is_windows() -> bool:
        return sys.platform.startswith("win")

    @staticmethod
    def is_macos() -> bool:
        return sys.platform == "darwin"

    @staticmethod
    def is_jetson() -> bool:
        """
        Determines if the platform is an NVIDIA Jetson device.
        """
        try:
            # Device-tree model (most reliable)
            if os.path.exists("/proc/device-tree/model"):
                with open("/proc/device-tree/model", "r") as f:
                    model = f.read().strip()
                    if "NVIDIA Jetson" in model:
                        return True

            # Jetson-specific libs/paths
            jetson_libraries = ["/usr/lib/aarch64-linux-gnu/tegra", "/etc/nv_tegra_release", "/etc/tegra-release"]
            if any(os.path.exists(p) for p in jetson_libraries):
                return True

            # Arch alone is not definitive, but is a signal
            if platform.machine() == "aarch64" and os.path.exists("/dev/nvhost-ctrl"):
                return True

        except Exception:
            pass

        return False

    @staticmethod
    def get_platform_type() -> str:
        """
        Returns a coarse platform type: 'jetson' | 'mac' | 'windows' | 'linux'
        """
        if PlatformDetector.is_jetson():
            return "jetson"
        if PlatformDetector.is_macos():
            return "mac"
        if PlatformDetector.is_windows():
            return "windows"
        return "linux"

    @staticmethod
    def has_gstreamer() -> bool:
        """
        Check if OpenCV was built with GStreamer support.
        """
        try:
            import cv2
            info = cv2.getBuildInformation()
            return ("GStreamer:                   YES" in info) or ("GStreamer: YES" in info)
        except Exception:
            return False

    @staticmethod
    def has_nvidia_gpu() -> bool:
        """
        Heuristic for NVIDIA dGPU presence (desktop/server).
        """
        if PlatformDetector.is_windows():
            return bool(os.environ.get("NVIDIA_VISIBLE_DEVICES", ""))  # WSL/Docker hint
        if PlatformDetector.is_linux():
            if os.path.exists("/proc/driver/nvidia/version"):
                return True
            if os.environ.get("NVIDIA_VISIBLE_DEVICES", "") not in ("", "none"):
                return True
        return False
    
    @staticmethod
    def get_device() -> str:
        """
        Check for GPU availability and return the appropriate device.
        """
        if torch.cuda.is_available():
            return "cuda"
        # Add checks for other devices like MPS if needed
        # elif torch.backends.mps.is_available():
        #     return "mps"
        return "cpu"
