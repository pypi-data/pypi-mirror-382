from datasette import hookimpl, Response
import platform
import os
import sys
import json


def gather_os_info():
    """Gather comprehensive OS information."""
    info = {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        },
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
    }

    # Detect if running in a container
    container_info = {}

    # Check for Docker
    if os.path.exists("/.dockerenv"):
        container_info["is_docker"] = True

    # Check /proc/1/cgroup for container indicators
    if os.path.exists("/proc/1/cgroup"):
        try:
            with open("/proc/1/cgroup", "r") as f:
                cgroup_content = f.read()
                if "docker" in cgroup_content:
                    container_info["is_docker"] = True
                    container_info["cgroup_docker"] = True
                if "lxc" in cgroup_content:
                    container_info["is_lxc"] = True
                if "kubepods" in cgroup_content:
                    container_info["is_kubernetes"] = True
        except:
            pass

    # Check for container environment variables
    container_env_vars = {}
    container_indicators = [
        "KUBERNETES_SERVICE_HOST",
        "DOCKER_CONTAINER",
        "container",
        "PODMAN_VERSION",
    ]
    for var in container_indicators:
        if var in os.environ:
            container_env_vars[var] = os.environ[var]

    if container_env_vars:
        container_info["environment_variables"] = container_env_vars

    if container_info:
        info["container"] = container_info

    # Linux distribution information
    if platform.system() == "Linux":
        linux_info = {}

        # Read /etc/os-release
        if os.path.exists("/etc/os-release"):
            try:
                os_release = {}
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            # Remove quotes
                            value = value.strip('"').strip("'")
                            os_release[key] = value
                linux_info["os_release"] = os_release
            except:
                pass

        # Try to read Docker base image info
        docker_image_info = {}

        # Check for common Docker image indicator files
        image_files = [
            "/etc/docker-image",
            "/etc/docker-base-image",
            "/.docker-base-image",
        ]
        for file_path in image_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        docker_image_info["base_image_file"] = {
                            "path": file_path,
                            "content": f.read().strip(),
                        }
                except:
                    pass

        # Read various system files that might indicate the base system
        if os.path.exists("/etc/debian_version"):
            try:
                with open("/etc/debian_version", "r") as f:
                    linux_info["debian_version"] = f.read().strip()
            except:
                pass

        if os.path.exists("/etc/alpine-release"):
            try:
                with open("/etc/alpine-release", "r") as f:
                    linux_info["alpine_release"] = f.read().strip()
            except:
                pass

        if os.path.exists("/etc/redhat-release"):
            try:
                with open("/etc/redhat-release", "r") as f:
                    linux_info["redhat_release"] = f.read().strip()
            except:
                pass

        # Kernel information
        if hasattr(os, "uname"):
            uname = os.uname()
            linux_info["kernel"] = {
                "sysname": uname.sysname,
                "nodename": uname.nodename,
                "release": uname.release,
                "version": uname.version,
                "machine": uname.machine,
            }

        # CPU info from /proc/cpuinfo
        if os.path.exists("/proc/cpuinfo"):
            try:
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo_content = f.read()
                    # Extract model name
                    for line in cpuinfo_content.split("\n"):
                        if line.startswith("model name"):
                            linux_info["cpu_model"] = line.split(":", 1)[1].strip()
                            break
            except:
                pass

        # Memory info from /proc/meminfo
        if os.path.exists("/proc/meminfo"):
            try:
                meminfo = {}
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            meminfo[key.strip()] = value.strip()
                linux_info["memory"] = {
                    "MemTotal": meminfo.get("MemTotal"),
                    "MemFree": meminfo.get("MemFree"),
                    "MemAvailable": meminfo.get("MemAvailable"),
                    "SwapTotal": meminfo.get("SwapTotal"),
                    "SwapFree": meminfo.get("SwapFree"),
                }
            except:
                pass

        if docker_image_info:
            linux_info["docker_image_info"] = docker_image_info

        if linux_info:
            info["linux"] = linux_info

    # macOS specific information
    if platform.system() == "Darwin":
        macos_info = {}
        try:
            macos_info["mac_ver"] = platform.mac_ver()
        except:
            pass
        if macos_info:
            info["macos"] = macos_info

    # Windows specific information
    if platform.system() == "Windows":
        windows_info = {}
        try:
            windows_info["win32_ver"] = platform.win32_ver()
            windows_info["win32_edition"] = platform.win32_edition()
        except:
            pass
        if windows_info:
            info["windows"] = windows_info

    # Environment variables that might be useful
    interesting_env_vars = [
        "SHELL",
        "TERM",
        "USER",
        "HOME",
        "PATH",
        "LANG",
        "TZ",
        "VIRTUAL_ENV",
        "CONDA_DEFAULT_ENV",
    ]

    env_vars = {}
    for var in interesting_env_vars:
        if var in os.environ:
            env_vars[var] = os.environ[var]

    if env_vars:
        info["environment"] = env_vars

    # Python executable path
    info["python_executable"] = sys.executable

    return info


@hookimpl
def register_routes():
    """Register the /-/os route."""

    async def os_info_view(request):
        data = gather_os_info()
        # Convert any non-serializable objects to strings
        json_data = json.dumps(data, indent=2, default=str)
        return Response(
            json_data, headers={"content-type": "application/json; charset=utf-8"}
        )

    return [
        (r"^/-/os$", os_info_view),
    ]
