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
import pprint
import shutil
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ..common.constants import Constants, DefaultValues
from ..common.dockerutils import (
    build_docker_image,
    create_and_get_builder,
    docker_export_tarball,
)
from ..common.exceptions import (
    IncompatiblePlatformConfigurationError,
    WrongApplicationPathError,
)
from .parameters import PackageBuildParameters, PlatformBuildResults, PlatformParameters


class BuilderBase:
    """
    Docker container image builder base class.
    Prepares files for building the docker image and calls Docker API to build the container image.
    """

    def __init__(
        self,
        build_parameters: PackageBuildParameters,
        temp_dir: str,
    ) -> None:
        """
        Copy the application, model files, and user documentations here in __init__ since they
        won't change when building different platforms.

        Args:
            build_parameters (PackageBuildParameters): general build parameters
            temp_dir (str): temporary directory to store files required for build

        """
        self._logger = logging.getLogger("packager.builder")
        self._build_parameters = build_parameters
        self._temp_dir = temp_dir
        self._copy_application()
        self._copy_model_files()
        self._copy_docs()
        self._copy_libs()
        self._copy_input_data()

        _ = self._write_dockerignore()
        _ = self._copy_script()

    def build(self, platform_parameters: PlatformParameters) -> PlatformBuildResults:
        """Build a new container image for a specific platform.
        Copy supporting files, such as redistributables and generate Dockerfile for the build.

        Args:
            platform_parameters (PlatformParameters): platform parameters

        Returns:
            PlatformBuildResults: build results
        """
        self._copy_supporting_files(platform_parameters)
        docker_file_path = self._write_dockerfile(platform_parameters)

        return self._build_internal(docker_file_path, platform_parameters)

    def _build_internal(
        self, dockerfile: str, platform_parameters: PlatformParameters
    ) -> PlatformBuildResults:
        """Prepare parameters for Docker buildx build

        Args:
            dockerfile (str): Path to Dockerfile to be built
            platform_parameters (PlatformParameters): platform parameters

        Returns:
            PlatformBuildResults: build results
        """
        builder = create_and_get_builder(Constants.LOCAL_BUILDX_BUILDER_NAME)

        build_result = PlatformBuildResults(platform_parameters)

        cache_to = {"type": "local", "dest": self._build_parameters.build_cache}
        cache_from = [{"type": "local", "src": self._build_parameters.build_cache}]
        if platform_parameters.base_image is not None:
            cache_from.append(
                {"type": "registry", "ref": platform_parameters.base_image}
            )
        if platform_parameters.build_image is not None:
            cache_from.append(
                {"type": "registry", "ref": platform_parameters.build_image}
            )

        builds = {
            "builder": builder,
            "cache": not self._build_parameters.no_cache,
            "cache_from": None if self._build_parameters.no_cache else cache_from,
            "cache_to": None if self._build_parameters.no_cache else cache_to,
            "context_path": self._temp_dir,
            "file": dockerfile,
            "platforms": [platform_parameters.docker_arch],
            "progress": "plain" if self._logger.root.level == logging.DEBUG else "auto",
            "pull": True,
            "tags": [platform_parameters.tag],
        }

        if self._build_parameters.add_hosts:
            builds["add_hosts"] = {}
            for host in self._build_parameters.add_hosts:
                host_name, host_ip = host.split(":")
                builds["add_hosts"][host_name] = host_ip

        export_to_tar_ball = False
        if self._build_parameters.tarball_output is not None:
            build_result.tarball_filename = str(
                self._build_parameters.tarball_output
                / f"{platform_parameters.tag}{Constants.TARBALL_FILE_EXTENSION}"
            ).replace(":", "-")

        # Make result image available on 'docker image' only if arch matches
        if platform_parameters.same_arch_as_system:
            builds["load"] = True
            build_result.docker_tag = platform_parameters.tag
            export_to_tar_ball = self._build_parameters.tarball_output is not None
        else:
            if self._build_parameters.tarball_output is not None:
                builds["output"] = {
                    # type=oci cannot be loaded by docker: https://github.com/docker/buildx/issues/59
                    "type": "docker",
                    "dest": build_result.tarball_filename,
                }
            else:
                build_result.succeeded = False
                build_result.error = (
                    "Skipped due to incompatible system architecture. "
                    "Use '--output' to write image to disk."
                )
                return build_result

        builds["build_args"] = {
            "UID": self._build_parameters.uid,
            "GID": self._build_parameters.gid,
            "UNAME": self._build_parameters.username,
            "GPU_TYPE": platform_parameters.platform_config.value,
        }

        self._logger.debug(
            f"Building Holoscan Application Package: tag={platform_parameters.tag}"
        )

        self.print_build_info(platform_parameters)

        try:
            build_docker_image(**builds)
            build_result.succeeded = True
            if export_to_tar_ball:
                try:
                    self._logger.info(
                        f"Saving {platform_parameters.tag} to {build_result.tarball_filename}..."
                    )
                    docker_export_tarball(
                        build_result.tarball_filename, platform_parameters.tag
                    )
                except Exception as ex:
                    build_result.error = f"Error saving tarball: {ex}"
                    build_result.succeeded = False
        except Exception as e:
            print(e)
            build_result.succeeded = False
            build_result.error = (
                "Error building image: see Docker output for additional details."
            )

        return build_result

    def _copy_input_data(self):
        """Copy input data to temporary location"""
        if self._build_parameters.input_data is not None:
            shutil.copytree(
                self._build_parameters.input_data, os.path.join(self._temp_dir, "input")
            )

    def print_build_info(self, platform_parameters):
        """Print build information for the platform."""
        self._logger.info(
            f"""
===============================================================================
Building image for:                 {platform_parameters.platform.value}
    Architecture:                   {platform_parameters.platform_arch.value}
    Base Image:                     {platform_parameters.base_image}
    Build Image:                    {platform_parameters.build_image if platform_parameters.build_image is not None else "N/A"}
    CUDA Version:                   {platform_parameters.cuda_version}
    Cache:                          {'Disabled' if self._build_parameters.no_cache else 'Enabled'}
    Configuration:                  {platform_parameters.platform_config.value}
    Holoscan SDK Package:           {platform_parameters.holoscan_sdk_file if platform_parameters.holoscan_sdk_file is not None else "N/A"}
    MONAI Deploy App SDK Package:   {platform_parameters.monai_deploy_sdk_file if platform_parameters.monai_deploy_sdk_file is not None else "N/A"}
    gRPC Health Probe:              {platform_parameters.health_probe if platform_parameters.health_probe is not None else "N/A"}
    SDK Version:                    {self._build_parameters.holoscan_sdk_version}
    SDK:                            {self._build_parameters.sdk.value}
    Tag:                            {platform_parameters.tag}
    Included features/dependencies: {", ".join(self._build_parameters.includes) if self._build_parameters.includes else "N/A"}
    """  # noqa: E501
        )

    def _write_dockerignore(self):
        """Copy .dockerignore file to temporary location."""
        # Write out .dockerignore file
        dockerignore_source_file_path = (
            Path(__file__).parent / "templates" / "dockerignore"
        )
        dockerignore_dest_file_path = os.path.join(self._temp_dir, ".dockerignore")
        shutil.copyfile(dockerignore_source_file_path, dockerignore_dest_file_path)
        return dockerignore_dest_file_path

    def _copy_script(self):
        """Copy HAP/MAP tools.sh script to temporary directory"""
        # Copy the tools script
        tools_script_file_path = Path(__file__).parent / "templates" / "tools.sh"
        tools_script_dest_file_path = os.path.join(self._temp_dir, "tools")
        shutil.copyfile(tools_script_file_path, tools_script_dest_file_path)
        return tools_script_dest_file_path

    def _write_dockerfile(self, platform_parameters: PlatformParameters):
        """Write Dockerfile temporary location"""
        docker_template_string = self._get_template(platform_parameters)
        self._logger.debug(
            f"""
========== Begin Dockerfile ==========
{docker_template_string}
=========== End Dockerfile ===========
"""
        )

        docker_file_path = os.path.join(self._temp_dir, DefaultValues.DOCKER_FILE_NAME)
        with open(docker_file_path, "w") as docker_file:
            docker_file.write(docker_template_string)

        return os.path.abspath(docker_file_path)

    def _copy_application(self):
        """Copy application to temporary location"""
        # Copy application files to temp directory (under 'app' folder)
        target_application_path = Path(os.path.join(self._temp_dir, "app"))
        if os.path.exists(target_application_path):
            shutil.rmtree(target_application_path)

        if not os.path.exists(self._build_parameters.application):
            raise WrongApplicationPathError(
                f'Directory "{self._build_parameters.application}" not found.'
            )

        if os.path.isfile(self._build_parameters.application):
            shutil.copytree(
                self._build_parameters.application.parent, target_application_path
            )
        else:
            shutil.copytree(self._build_parameters.application, target_application_path)

        target_config_file_path = Path(os.path.join(self._temp_dir, "app.config"))
        shutil.copyfile(
            self._build_parameters.app_config_file_path, target_config_file_path
        )

    def _copy_libs(self):
        """
        - Copy additional libraries to the temporary application directory.
        - Stores all subdirectories from the copied libraries to the 'additional_lib_paths'
          parameter that will be used to set the LD_LIBRARY_PATH or PYTHONPATH environment variable
          in the Dockerfile.
        """
        if self._build_parameters.additional_libs is None:
            return
        target_libs_path = Path(os.path.join(self._temp_dir, "lib"))
        if os.path.exists(target_libs_path):
            shutil.rmtree(target_libs_path)

        for lib_path in self._build_parameters.additional_libs:
            self._logger.debug(
                f"Copying additional libraries from {lib_path} to {target_libs_path}"
            )
            shutil.copytree(lib_path, target_libs_path, dirs_exist_ok=True)

        subdirectories = [
            os.path.join(
                DefaultValues.HOLOSCAN_LIB_DIR,
                os.path.join(root, subdir)
                .replace(str(target_libs_path), "")
                .lstrip("/"),
            )
            for root, dirs, _ in os.walk(target_libs_path)
            for subdir in dirs
        ]
        self._build_parameters.additional_lib_paths = ":".join(subdirectories)

    def _copy_model_files(self):
        """Copy models to temporary location"""
        if self._build_parameters.models:
            target_models_root_path = os.path.join(self._temp_dir, "models")
            os.makedirs(target_models_root_path, exist_ok=True)

            for model in self._build_parameters.models:
                target_model_path = os.path.join(target_models_root_path, model)
                if self._build_parameters.models[model].is_dir():
                    shutil.copytree(
                        self._build_parameters.models[model], target_model_path
                    )
                elif self._build_parameters.models[model].is_file():
                    os.makedirs(target_model_path, exist_ok=True)
                    target_model_path = os.path.join(
                        target_model_path, self._build_parameters.models[model].name
                    )
                    shutil.copy(self._build_parameters.models[model], target_model_path)

    def _copy_docs(self):
        """Copy user documentations to temporary location"""
        if self._build_parameters.docs is not None:
            target_path = os.path.join(self._temp_dir, "docs")
            shutil.copytree(self._build_parameters.docs, target_path)

    def _get_template(self, platform_parameters: PlatformParameters):
        """Generate Dockerfile using Jinja2 engine"""
        jinja_env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )
        self._logger.debug(
            f"""
========== Begin Build Parameters ==========
{pprint.pformat(self._build_parameters.to_jinja)}
=========== End Build Parameters ===========
"""
        )
        self._logger.debug(
            f"""
========== Begin Platform Parameters ==========
{pprint.pformat(platform_parameters.to_jinja)}
=========== End Platform Parameters ===========
"""
        )

        if platform_parameters.cuda_version == 12:
            jinja_template = jinja_env.get_template("Dockerfile-cu12.jinja2")
        elif platform_parameters.cuda_version == 13:
            jinja_template = jinja_env.get_template("Dockerfile.jinja2")
        else:
            raise IncompatiblePlatformConfigurationError(
                f"Invalid CUDA version: {platform_parameters.cuda_version}"
            )

        return jinja_template.render(
            {
                **self._build_parameters.to_jinja,
                **platform_parameters.to_jinja,
            }
        )

    def _copy_supporting_files(self, platform_parameters: PlatformParameters):
        """Abstract base function to copy supporting files"""
        return NotImplemented

    def __init_subclass__(cls):
        if cls._copy_supporting_files is BuilderBase._copy_supporting_files:
            raise NotImplementedError(
                "{cls} has not overwritten method {_copy_supporting_files}!"
            )


class PythonAppBuilder(BuilderBase):
    """A subclass of BuilderBase for Python-based applications.
    Copioes PyPI package and requirement.txt file
    """

    def __init__(
        self,
        build_parameters: PackageBuildParameters,
        temp_dir: str,
    ) -> None:
        BuilderBase.__init__(self, build_parameters, temp_dir)

    def _copy_supporting_files(self, platform_parameters: PlatformParameters):
        self._copy_sdk_file(platform_parameters.holoscan_sdk_file)
        self._copy_sdk_file(platform_parameters.monai_deploy_sdk_file)
        self._copy_pip_requirements()

    def _copy_pip_requirements(self):
        pip_folder = os.path.join(self._temp_dir, "pip")
        os.makedirs(pip_folder, exist_ok=True)
        pip_requirements_path = os.path.join(pip_folder, "requirements.txt")

        # Build requirements content first
        requirements_content = []
        if self._build_parameters.requirements_file_path is not None:
            with open(self._build_parameters.requirements_file_path) as lr:
                requirements_content.extend(lr)
            requirements_content.append("")

        if self._build_parameters.pip_packages:
            requirements_content.extend(self._build_parameters.pip_packages)

        # Write all content at once
        with open(pip_requirements_path, "w") as requirements_file:
            requirements_file.writelines(requirements_content)
            self._logger.debug(
                "================ Begin requirements.txt ================"
            )
            for req in requirements_content:
                self._logger.debug(f"  {req.strip()}")
            self._logger.debug(
                "================ End requirements.txt =================="
            )

    def _copy_sdk_file(self, sdk_file: Optional[Path]):
        if sdk_file is not None and os.path.isfile(sdk_file):
            dest = os.path.join(self._temp_dir, sdk_file.name)
            if os.path.exists(dest):
                os.remove(dest)
            shutil.copyfile(sdk_file, dest)


class CppAppBuilder(BuilderBase):
    """A subclass of BuilderBase for C++ applications.
    Copies Debian.
    """

    def __init__(
        self,
        build_parameters: PackageBuildParameters,
        temp_dir: str,
    ) -> None:
        BuilderBase.__init__(self, build_parameters, temp_dir)

    def _copy_supporting_files(self, platform_parameters: PlatformParameters):
        """Copies the SDK file to the temporary directory"""
        if platform_parameters.holoscan_sdk_file is not None and os.path.isfile(
            platform_parameters.holoscan_sdk_file
        ):
            dest = os.path.join(
                self._temp_dir, platform_parameters.holoscan_sdk_file.name
            )
            if os.path.exists(dest):
                os.remove(dest)
            shutil.copyfile(
                platform_parameters.holoscan_sdk_file,
                dest,
            )
