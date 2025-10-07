# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from pathlib import Path

from .enum_types import Arch, Platform, PlatformConfiguration, SdkType


class DefaultValues:
    """
    This class contains default values for various parameters.
    """

    API_VERSION = "1.0.0"  # MAP/HAP version number
    DOCKER_FILE_NAME = "Dockerfile"  # Filename of the generated Dockerfile
    TIMEOUT = 0  # Default application timeout
    USERNAME = "holoscan"  # Default user to be created in the container
    BUILD_CACHE_DIR = Path(
        "~/.holoscan_build_cache"
    )  # A local directory used for storing Docker build cache

    HOLOSCAN_APP_DIR = Path("/opt/holoscan/app")  # Path to user's application
    HOLOSCAN_LIB_DIR = Path("/opt/holoscan/lib")  # Path to user's application
    HOLOSCAN_CONFIG_PATH = Path(
        "/var/holoscan/app.yaml"
    )  # Path to the application config file
    HOLOSCAN_DOCS_DIR = Path("/opt/holoscan/docs")  # Path to documentation
    HOLOSCAN_LOGS_DIR = Path("/var/holoscan/logs")  # Path to application logs
    INPUT_DIR = "input/"  # Relative path to application input data
    MODELS_DIR = Path("/opt/holoscan/models/")  # Path to user provided model(s)
    OUTPUT_DIR = "output/"  # Relative path to application generated results
    WORK_DIR = Path("/var/holoscan/")  # Default working directory
    APP_MANIFEST_PATH = "/etc/holoscan/app.json"  # Path to app.json manifest file
    PKG_MANIFEST_PATH = "/etc/holoscan/pkg.json"  # Path to pkg.json manifest file

    DEFAULT_SHM_SIZE = 1073741824


class Constants:
    CPP_CMAKELIST_FILE = "CMakeLists.txt"
    PYTHON_EXECUTABLE = "python3"
    PYTHON_MAIN_FILE = "__main__.py"

    TARBALL_FILE_EXTENSION = ".tar"

    DEBIAN_FILE_EXTENSION = ".deb"
    PYPI_WHEEL_FILE_EXTENSION = ".whl"
    PYPI_TARGZ_FILE_EXTENSION = ".gz"
    PYTHON_FILE_EXTENSION = ".py"

    PYPI_FILE_EXTENSIONS = [PYPI_WHEEL_FILE_EXTENSION, PYPI_TARGZ_FILE_EXTENSION]

    LOCAL_BUILDX_BUILDER_NAME = "holoscan_app_builder"
    LOCAL_DOCKER_REGISTRY_NAME = "holoscan_build_registry"
    LOCAL_REGISTRY_IMAGE_NAME = "registry:2"
    LOCAL_REGISTRY_HOST = "localhost"
    LOCAL_REGISTRY_INTERNAL_PORT = "5000/tcp"

    RESOURCE_SHARED_MEMORY_KEY = "sharedMemory"

    # Include "holoscan" for backward compatibility; remove post 3.7.0 release
    PYPI_PACKAGE_NAMES = ["holoscan-cu12", "holoscan-cu13", "holoscan"]


class SDK:
    """
    This class contains lookup tables for various platform and SDK settings.

    """

    # Platform to architecture mappings
    PLATFORM_ARCH_MAPPINGS = {
        Platform.Jetson: Arch.arm64,
        Platform.IGX_iGPU: Arch.arm64,
        Platform.IGX_dGPU: Arch.arm64,
        Platform.SBSA: Arch.arm64,
        Platform.x86_64: Arch.amd64,
    }

    # Values of all platforms supported by the Packager
    PLATFORMS = [
        Platform.Jetson.value,
        Platform.IGX_iGPU.value,
        Platform.IGX_dGPU.value,
        Platform.SBSA.value,
        Platform.x86_64.value,
    ]

    # Values of all platform configurations supported by the Packager
    PLATFORM_CONFIGS = [
        PlatformConfiguration.iGPU.value,
        PlatformConfiguration.dGPU.value,
    ]

    INTERNAL_PLATFORM_MAPPINGS = {
        Platform.Jetson: (Platform.JetsonAgxOrinDevKit, PlatformConfiguration.iGPU),
        Platform.IGX_iGPU: (Platform.IGXOrinDevIt, PlatformConfiguration.iGPU),
        Platform.IGX_dGPU: (Platform.IGXOrinDevIt, PlatformConfiguration.dGPU),
        Platform.SBSA: (Platform.SBSA, PlatformConfiguration.dGPU),
        Platform.x86_64: (Platform.X64Workstation, PlatformConfiguration.dGPU),
    }

    # Values of SDKs supported by the Packager
    SDKS = [SdkType.Holoscan.value, SdkType.MonaiDeploy.value]


class EnvironmentVariables:
    """
    This class includes all environment variables set in
    the container and in the app.json manifest file."""

    HOLOSCAN_APPLICATION = "HOLOSCAN_APPLICATION"
    HOLOSCAN_INPUT_PATH = "HOLOSCAN_INPUT_PATH"
    HOLOSCAN_OUTPUT_PATH = "HOLOSCAN_OUTPUT_PATH"
    HOLOSCAN_WORKDIR = "HOLOSCAN_WORKDIR"
    HOLOSCAN_MODEL_PATH = "HOLOSCAN_MODEL_PATH"
    HOLOSCAN_CONFIG_PATH = "HOLOSCAN_CONFIG_PATH"
    HOLOSCAN_APP_MANIFEST_PATH = "HOLOSCAN_APP_MANIFEST_PATH"
    HOLOSCAN_PKG_MANIFEST_PATH = "HOLOSCAN_PKG_MANIFEST_PATH"
    HOLOSCAN_DOCS_PATH = "HOLOSCAN_DOCS_PATH"
    HOLOSCAN_LOGS_PATH = "HOLOSCAN_LOGS_PATH"
