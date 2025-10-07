import platform
import os

def get_os_type():
    os_type = platform.system()
    if os_type == "Linux":
        # Check for Docker first
        if os.path.exists("/.dockerenv"):
            return "Linux"  # Running inside Docker container
        try:
            with open("/proc/1/cgroup", "rt") as f:
                cgroup_info = f.read().lower()
            if "docker" in cgroup_info or "containerd" in cgroup_info:
                return "Linux"  # Running inside Docker container
        except Exception:
            pass

        # Check for WSL2
        try:
            with open("/proc/version", "r") as f:
                version_info = f.read().lower()
            if "microsoft" in version_info:
                return "WSL"
        except Exception:
            pass

        # Check for WSL2 environment variable
        if "WSL_DISTRO_NAME" in os.environ:
            return "WSL"

        return "Linux"  # Native Linux
    elif os_type == "Windows":
        return "Windows"
    elif os_type == "Darwin":
        return "Mac"
    else:
        return "Unknown"