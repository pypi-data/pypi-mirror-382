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
import logging
import os
import platform
from pathlib import Path
from typing import Any, List, Optional

from ..common.constants import SDK, Constants, DefaultValues
from ..common.dockerutils import parse_docker_image_name_and_tag
from ..common.enum_types import (
    ApplicationType,
    Arch,
    Platform,
    PlatformConfiguration,
    SdkType,
)
from ..common.exceptions import InvalidTagValueError, UnknownApplicationTypeError


class PlatformParameters:
    def __init__(
        self,
        platform: Platform,
        tag: str,
        version: str,
        cuda_version: int = 13,
    ) -> None:
        self._logger = logging.getLogger("platform.parameters")
        self._platform = SDK.INTERNAL_PLATFORM_MAPPINGS[platform][0]
        self._platform_config: PlatformConfiguration = SDK.INTERNAL_PLATFORM_MAPPINGS[
            platform
        ][1]
        self._arch: Arch = SDK.PLATFORM_ARCH_MAPPINGS[platform]
        self._tag_prefix: Optional[str]
        self._version: Optional[str]

        (self._tag_prefix, self._version) = parse_docker_image_name_and_tag(tag)

        if self._tag_prefix is None:
            raise InvalidTagValueError(
                f"'{tag}' is not a valid Docker tag. Format: name[:tag]"
            )

        if self._version is None:
            self._version = version

        self._data: dict[str, Any] = {}
        self._data["tag"] = tag
        self._data["base_image"] = None
        self._data["build_image"] = None
        self._data["holoscan_sdk_file"] = None
        self._data["holoscan_sdk_filename"] = None
        self._data["monai_deploy_sdk_file"] = None
        self._data["monai_deploy_sdk_filename"] = None
        self._data["custom_base_image"] = False
        self._data["custom_holoscan_sdk"] = False
        self._data["custom_monai_deploy_sdk"] = False
        self._data["cuda_version"] = cuda_version
        self._data["target_arch"] = "aarch64" if self._arch == Arch.arm64 else "x86_64"
        self._data["cuda_deb_arch"] = "sbsa" if self._arch == Arch.arm64 else "x86_64"
        self._data["holoscan_deb_arch"] = (
            "arm64" if self._arch == Arch.arm64 else "amd64"
        )
        self._data["gpu_type"] = self.platform_config.value

    @property
    def tag(self) -> str:
        return (
            f"{self._tag_prefix}-"
            f"{self.platform.value}-"
            f"{self.platform_config.value}-"
            f"{self.platform_arch.value}:"
            f"{self.version}"
        ).replace("/", "-")

    @property
    def tag_prefix(self) -> str:
        return self._tag_prefix

    @property
    def custom_base_image(self) -> Optional[str]:
        return self._data["custom_base_image"]

    @custom_base_image.setter
    def custom_base_image(self, value: str):
        self._data["custom_base_image"] = value

    @property
    def custom_holoscan_sdk(self) -> Optional[str]:
        return self._data["custom_holoscan_sdk"]

    @custom_holoscan_sdk.setter
    def custom_holoscan_sdk(self, value: str):
        self._data["custom_holoscan_sdk"] = value

    @property
    def custom_monai_deploy_sdk(self) -> Optional[str]:
        return self._data["custom_monai_deploy_sdk"]

    @custom_monai_deploy_sdk.setter
    def custom_monai_deploy_sdk(self, value: str):
        self._data["custom_monai_deploy_sdk"] = value

    @property
    def base_image(self) -> Optional[str]:
        return self._data["base_image"]

    @base_image.setter
    def base_image(self, value: str):
        self._data["base_image"] = value

    @property
    def build_image(self) -> Optional[str]:
        return self._data["build_image"]

    @build_image.setter
    def build_image(self, value: str):
        self._data["build_image"] = value

    @property
    def cuda_version(self) -> int:
        return self._data["cuda_version"]

    @property
    def holoscan_sdk_file(self) -> Optional[Path]:
        return self._data["holoscan_sdk_file"]

    @holoscan_sdk_file.setter
    def holoscan_sdk_file(self, value: Path):
        self._data["holoscan_sdk_file"] = value
        if value is not None and hasattr(value, "name"):
            self._data["holoscan_sdk_filename"] = value.name
        elif value is not None:
            self._data["holoscan_sdk_filename"] = value

    @property
    def monai_deploy_sdk_file(self) -> Optional[Path]:
        return self._data["monai_deploy_sdk_file"]

    @monai_deploy_sdk_file.setter
    def monai_deploy_sdk_file(self, value: Path):
        self._data["monai_deploy_sdk_file"] = value
        if value is not None and hasattr(value, "name"):
            self._data["monai_deploy_sdk_filename"] = value.name

    @property
    def version(self) -> str:
        return self._version

    @property
    def health_probe(self) -> Optional[Path]:
        return self._data.get("health_probe", None)

    @health_probe.setter
    def health_probe(self, value: Optional[Path]):
        self._data["health_probe"] = value

    @property
    def platform_arch(self) -> Arch:
        return self._arch

    @property
    def docker_arch(self) -> str:
        return self._arch.value

    @property
    def platform(self) -> Platform:
        return self._platform

    @property
    def platform_config(self) -> PlatformConfiguration:
        return self._platform_config

    @property
    def to_jinja(self) -> dict[str, Any]:
        return self._data

    @property
    def same_arch_as_system(self) -> bool:
        return (platform.machine() == "aarch64" and self._arch == Arch.arm64) or (
            platform.machine() == "x86_64" and self._arch == Arch.amd64
        )

    @property
    def cuda_deb_arch(self) -> str:
        return self._data["cuda_deb_arch"]

    @property
    def holoscan_deb_arch(self) -> str:
        return self._data["holoscan_deb_arch"]

    @property
    def target_arch(self) -> str:
        return self._data["target_arch"]


class PlatformBuildResults:
    def __init__(self, parameters: PlatformParameters):
        self._parameters = parameters
        self._docker_tag: Optional[str] = None
        self._tarball_filename: Optional[str] = None
        self._succeeded = False
        self._error: Optional[str] = None

    @property
    def parameters(self) -> PlatformParameters:
        return self._parameters

    @property
    def error(self) -> Optional[str]:
        return self._error

    @error.setter
    def error(self, value: Optional[str]):
        self._error = value

    @property
    def docker_tag(self) -> Optional[str]:
        return self._docker_tag

    @docker_tag.setter
    def docker_tag(self, value: Optional[str]):
        self._docker_tag = value

    @property
    def tarball_filename(self) -> Optional[str]:
        return self._tarball_filename

    @tarball_filename.setter
    def tarball_filename(self, value: Optional[str]):
        self._tarball_filename = value

    @property
    def succeeded(self) -> bool:
        return self._succeeded

    @succeeded.setter
    def succeeded(self, value: bool):
        self._succeeded = value


class PackageBuildParameters:
    """
    Parameters required for building the Docker image with Jinja template.
    """

    def __init__(self):
        self._logger = logging.getLogger("packager.parameters")
        self._data = {}
        self._data["app_dir"] = DefaultValues.HOLOSCAN_APP_DIR
        self._data["lib_dir"] = DefaultValues.HOLOSCAN_LIB_DIR
        self._data["config_file_path"] = DefaultValues.HOLOSCAN_CONFIG_PATH
        self._data["docs_dir"] = DefaultValues.HOLOSCAN_DOCS_DIR
        self._data["logs_dir"] = DefaultValues.HOLOSCAN_LOGS_DIR
        self._data["full_input_path"] = DefaultValues.WORK_DIR / DefaultValues.INPUT_DIR
        self._data["full_output_path"] = (
            DefaultValues.WORK_DIR / DefaultValues.OUTPUT_DIR
        )
        self._data["input_dir"] = DefaultValues.INPUT_DIR
        self._data["models_dir"] = DefaultValues.MODELS_DIR
        self._data["output_dir"] = DefaultValues.OUTPUT_DIR
        self._data["timeout"] = DefaultValues.TIMEOUT
        self._data["working_dir"] = DefaultValues.WORK_DIR
        self._data["app_json"] = DefaultValues.APP_MANIFEST_PATH
        self._data["pkg_json"] = DefaultValues.PKG_MANIFEST_PATH
        self._data["username"] = DefaultValues.USERNAME
        self._data["build_cache"] = DefaultValues.BUILD_CACHE_DIR
        self._data["uid"] = os.getuid()
        self._data["gid"] = os.getgid()
        self._data["tarball_output"] = None
        self._data["cmake_args"] = ""
        self._data["includes"] = []
        self._data["input_data"] = None
        self._data["additional_lib_paths"] = ""
        self._data["add_hosts"] = []
        self._data["application_directory"] = None
        self._data["application_type"] = None
        self._data["application"] = None
        self._data["app_config_file_path"] = None
        self._data["command"] = None
        self._data["no_cache"] = False
        self._data["pip_packages"] = None
        self._data["requirements_file_path"] = None
        self._data["holoscan_sdk_version"] = None
        self._data["monai_deploy_app_sdk_version"] = None
        self._data["title"] = None
        self._data["version"] = None

        self._additional_libs = []

    @property
    def build_cache(self) -> int:
        return self._data["build_cache"]

    @build_cache.setter
    def build_cache(self, value: int):
        self._data["build_cache"] = value

    @property
    def full_input_path(self) -> str:
        return self._data["full_input_path"]

    @property
    def full_output_path(self) -> str:
        return self._data["full_output_path"]

    @property
    def docs_dir(self) -> str:
        return self._data["docs_dir"]

    @property
    def logs_dir(self) -> str:
        return self._data["logs_dir"]

    @property
    def tarball_output(self) -> int:
        return self._data["tarball_output"]

    @tarball_output.setter
    def tarball_output(self, value: int):
        self._data["tarball_output"] = value

    @property
    def cmake_args(self) -> str:
        return self._data["cmake_args"]

    @cmake_args.setter
    def cmake_args(self, value: str):
        self._data["cmake_args"] = value.strip('"') if value is not None else ""

    @property
    def gid(self) -> int:
        return self._data["gid"]

    @gid.setter
    def gid(self, value: int):
        self._data["gid"] = value

    @property
    def uid(self) -> int:
        return self._data["uid"]

    @uid.setter
    def uid(self, value: int):
        self._data["uid"] = value

    @property
    def username(self) -> str:
        return self._data["username"]

    @username.setter
    def username(self, value: str):
        self._data["username"] = value

    @property
    def app_manifest_path(self):
        return self._data["app_json"]

    @property
    def package_manifest_path(self):
        return self._data["pkg_json"]

    @property
    def title(self):
        return self._data["title"]

    @title.setter
    def title(self, value):
        self._data["title"] = value

    @property
    def docs(self) -> Path:
        return self._data.get("docs", None)

    @docs.setter
    def docs(self, value: Path):
        if value is not None:
            self._data["docs"] = value

    @property
    def models(self) -> dict[str, Path]:
        return self._data.get("models", None)

    @models.setter
    def models(self, value: dict[str, Path]):
        if value is not None:
            self._data["models"] = value

    @property
    def pip_packages(self):
        return self._data["pip_packages"]

    @pip_packages.setter
    def pip_packages(self, value):
        self._data["pip_packages"] = value

    @property
    def no_cache(self):
        return self._data["no_cache"]

    @no_cache.setter
    def no_cache(self, value):
        self._data["no_cache"] = value

    @property
    def config_file_path(self):
        return self._data["config_file_path"]

    @property
    def app_config_file_path(self):
        return self._data["app_config_file_path"]

    @app_config_file_path.setter
    def app_config_file_path(self, value):
        self._data["app_config_file_path"] = value

    @property
    def app_dir(self):
        return self._data["app_dir"]

    @property
    def application(self) -> Path:
        return self._data["application"]

    @application.setter
    def application(self, value: Path):
        self._data["application"] = value
        self._logger.info(f"Application: {self.application}")
        self._application_type = self._detect_application_type()
        self._data["application_type"] = self._application_type.name
        self._logger.info(f"Detected application type: {self.application_type.value}")
        self._data["application_directory"] = (
            self.application
            if os.path.isdir(self.application)
            else Path(os.path.dirname(self.application))
        )
        requirements_file_path = self.application_directory / "requirements.txt"
        if os.path.exists(requirements_file_path):
            self._data["requirements_file_path"] = requirements_file_path
        else:
            self._data["requirements_file_path"] = None
        self._data["command"] = self._set_app_command()
        self._data["command_filename"] = os.path.basename(self.application)

    @property
    def command_filename(self) -> str:
        return self._data["command_filename"]

    @property
    def command(self) -> str:
        return self._data["command"]

    @property
    def application_directory(self) -> Path:
        return self._data["application_directory"]

    @property
    def requirements_file_path(self) -> Path:
        return self._data["requirements_file_path"]

    @property
    def version(self) -> str:
        return self._data["version"]

    @version.setter
    def version(self, value: str):
        self._data["version"] = value

    @property
    def timeout(self) -> int:
        return self._data["timeout"]

    @timeout.setter
    def timeout(self, value: int):
        self._data["timeout"] = value

    @property
    def working_dir(self) -> Path:
        return self._data["working_dir"]

    @property
    def models_dir(self) -> Path:
        return self._data["models_dir"]

    @models_dir.setter
    def models_dir(self, value: Path):
        self._data["models_dir"] = value

    @property
    def input_dir(self) -> str:
        return self._data["input_dir"]

    @property
    def output_dir(self) -> str:
        return self._data["output_dir"]

    @property
    def application_type(self) -> ApplicationType:
        return self._application_type

    @property
    def sdk(self) -> SdkType:
        return self._data["sdk"]

    @sdk.setter
    def sdk(self, value: SdkType):
        self._data["sdk"] = value
        self._data["sdk_type"] = value.value

    @property
    def holoscan_sdk_version(self) -> str:
        return self._data["holoscan_sdk_version"]

    @holoscan_sdk_version.setter
    def holoscan_sdk_version(self, value: str):
        self._data["holoscan_sdk_version"] = value

    @property
    def monai_deploy_app_sdk_version(self) -> str:
        return self._data["monai_deploy_app_sdk_version"]

    @monai_deploy_app_sdk_version.setter
    def monai_deploy_app_sdk_version(self, value: str):
        self._data["monai_deploy_app_sdk_version"] = value

    @property
    def add_hosts(self) -> List[str]:
        return self._data["add_hosts"]

    @add_hosts.setter
    def add_hosts(self, value: List[str]):
        self._data["add_hosts"] = value

    @property
    def includes(self) -> str:
        return self._data["includes"]

    @includes.setter
    def includes(self, value: str):
        self._data["includes"] = value

    @property
    def input_data(self) -> Path:
        return self._data["input_data"]

    @input_data.setter
    def input_data(self, value: Path):
        self._data["input_data"] = value

    @property
    def additional_lib_paths(self) -> str:
        """
        Additional libraries that user wants to include in the package.
        Stores the post-processed values to be injected into LD_LIBRARY_PATH and PYTHONPATH in the
        Jinja2 template.
        """
        return self._data["additional_lib_paths"]

    @additional_lib_paths.setter
    def additional_lib_paths(self, value: str):
        self._data["additional_lib_paths"] = value

    @property
    def additional_libs(self) -> list[str]:
        """
        Additional libraries that user wants to include in the package.
        Stores paths entered from the command line before processing.
        """
        return self._additional_libs

    @additional_libs.setter
    def additional_libs(self, value: list[str]):
        self._additional_libs = value

    @property
    def to_jinja(self) -> dict[str, Any]:
        return self._data

    def _detect_application_type(self) -> ApplicationType:
        if os.path.isdir(self.application):
            if os.path.exists(self.application / Constants.PYTHON_MAIN_FILE):
                return ApplicationType.PythonModule
            elif os.path.exists(self.application / Constants.CPP_CMAKELIST_FILE):
                return ApplicationType.CppCMake
        elif os.path.isfile(self.application):
            if Path(self.application).suffix == ".py":
                return ApplicationType.PythonFile
            elif os.access(self.application, os.X_OK):
                return ApplicationType.Binary

        raise UnknownApplicationTypeError(
            f"""\n\nUnable to determine application type. Please ensure the application path
            contains one of the following:
    \t- Python directory/module with '{Constants.PYTHON_MAIN_FILE}'
    \t- Python file
    \t- C++ source directory with '{Constants.CPP_CMAKELIST_FILE}'
    \t- Binary file"""
        )

    def _set_app_command(self) -> str:
        if self.application_type == ApplicationType.PythonFile:
            return (
                f'["{Constants.PYTHON_EXECUTABLE}", '
                + f'"{os.path.join(self._data["app_dir"], os.path.basename(self.application))}"]'
            )
        elif self.application_type == ApplicationType.PythonModule:
            return f'["{Constants.PYTHON_EXECUTABLE}", "{self._data["app_dir"]}"]'
        elif self.application_type in [
            ApplicationType.CppCMake,
            ApplicationType.Binary,
        ]:
            return f'["{os.path.join(self._data["app_dir"], os.path.basename(self.application))}"]'

        raise UnknownApplicationTypeError("Unsupported application type.")
