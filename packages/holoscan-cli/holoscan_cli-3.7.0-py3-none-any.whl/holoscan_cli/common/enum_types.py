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
from enum import Enum


class ApplicationType(Enum):
    PythonModule = "Python Module"
    PythonFile = "Python File"
    CppCMake = "C++"
    Binary = "Binary"


class SdkType(Enum):
    """
    Note the values assigned are used as entry_points in setup.py for detecting the SDK to use.
    """

    Holoscan = "holoscan"
    MonaiDeploy = "monai-deploy"


class Arch(Enum):
    amd64 = "linux/amd64"
    arm64 = "linux/arm64"


class Platform(Enum):
    # User values - when a new value is added, please also update SDK.PLATFORMS
    Jetson = "jetson"
    IGX_iGPU = "igx-igpu"
    IGX_dGPU = "igx-dgpu"
    SBSA = "sbsa"
    x86_64 = "x86_64"

    # Internal use only - for mapping actual platform with platform configuration
    #  as defined in SDK.INTERNAL_PLATFORM_MAPPINGS.
    IGXOrinDevIt = "igx-orin-devkit"
    JetsonAgxOrinDevKit = "jetson-agx-orin-devkit"
    X64Workstation = "x64-workstation"


class PlatformConfiguration(Enum):
    iGPU = "igpu"  # noqa: N815
    dGPU = "dgpu"  # noqa: N815
    CPU = "cpu"
