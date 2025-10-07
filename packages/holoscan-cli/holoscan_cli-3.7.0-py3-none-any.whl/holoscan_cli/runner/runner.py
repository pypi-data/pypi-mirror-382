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
import json
import logging
import os
import re
import shutil
import sys
import tempfile
from argparse import Namespace
from glob import glob
from pathlib import Path
from typing import Optional

from ..common.dockerutils import create_or_use_network, docker_run, image_exists
from ..common.exceptions import ManifestReadError, UnmatchedDeviceError
from ..common.utils import (
    compare_versions,
    get_requested_gpus,
    print_manifest_json,
    run_cmd,
    run_cmd_output,
)
from .resources import get_shared_memory_size

logger = logging.getLogger("runner")


def _fetch_map_manifest(map_name: str) -> tuple[dict, dict]:
    """
    Execute HAP/MAP and fetch the manifest files.

    Args:
        map_name: HAP/MAP image name.

    Returns:
        app_info: application manifest as a python dict
        pkg_info: package manifest as a python dict
    """

    def _ensure_valid_exit_code(returncode: int) -> None:
        if returncode != 0:
            raise ManifestReadError("Error reading manifest file from the package.")

    logger.info("Reading HAP/MAP manifest...")

    with tempfile.TemporaryDirectory() as info_dir:
        docker_id = run_cmd_output(["docker", "create", map_name]).strip()
        returncode = run_cmd(
            [
                "docker",
                "cp",
                f"{docker_id}:/etc/holoscan/app.json",
                f"{info_dir}/app.json",
            ]
        )
        _ensure_valid_exit_code(returncode)
        returncode = run_cmd(
            [
                "docker",
                "cp",
                f"{docker_id}:/etc/holoscan/pkg.json",
                f"{info_dir}/pkg.json",
            ]
        )
        _ensure_valid_exit_code(returncode)
        returncode = run_cmd(["docker", "rm", "-v", docker_id])
        _ensure_valid_exit_code(returncode)

        app_json = Path(f"{info_dir}/app.json")
        pkg_json = Path(f"{info_dir}/pkg.json")

        app_info = json.loads(app_json.read_text())
        pkg_info = json.loads(pkg_json.read_text())

        print_manifest_json(app_info, "app.json")
        print_manifest_json(pkg_info, "pkg.json")

        return app_info, pkg_info


def _run_app(args: Namespace, app_info: dict, pkg_info: dict):
    """
    Executes the Holoscan Application Package.

    Args:
        args: user arguments
        app_info: application manifest dictionary
        pkg_info: package manifest dictionary

    Returns:
        returncode: command returncode
    """

    map_name: str = args.map
    input_path: Path = args.input
    output_path: Path = args.output
    quiet: bool = args.quiet
    driver: bool = args.driver
    worker: bool = args.worker
    health_check: bool = args.health_check
    fragments: Optional[str] = args.fragments
    network: str = create_or_use_network(args.network, map_name)
    nic: Optional[str] = args.nic if args.nic else None
    use_all_nics: bool = args.use_all_nics
    gpus: Optional[str] = args.gpus if args.gpus else None
    config: Optional[Path] = args.config if args.config else None
    address: Optional[str] = args.address if args.address else None
    worker_address: Optional[str] = args.worker_address if args.worker_address else None
    render: bool = args.render
    user: str = f"{args.uid}:{args.gid}"
    remove: bool = args.rm
    hostname: Optional[str] = "driver" if driver else None
    terminal: bool = args.terminal
    platform_config: str = pkg_info.get("platformConfig")
    shared_memory_size: Optional[str] = (
        get_shared_memory_size(pkg_info, worker, driver, fragments, args.shm_size)
        if args.shm_size
        else None
    )

    commands = []
    devices = _lookup_devices(args.device) if args.device is not None else []

    if driver:
        commands.append("--driver")
        logger.info("Application running in Driver mode")
    if worker:
        commands.append("--worker")
        logger.info("Application running in Worker mode")
    if fragments:
        commands.append("--fragments")
        commands.append(fragments)
        logger.info(f"Configured fragments: {fragments}")
    if address:
        commands.append("--address")
        commands.append(address)
        logger.info(f"App Driver address and port: {address}")
    if worker_address:
        commands.append("--worker_address")
        commands.append(worker_address)
        logger.info(f"App Worker address and port: {worker_address}")

    docker_run(
        hostname,
        map_name,
        input_path,
        output_path,
        app_info,
        pkg_info,
        quiet,
        commands,
        health_check,
        network,
        nic,
        use_all_nics,
        gpus,
        config,
        render,
        user,
        terminal,
        devices,
        platform_config,
        shared_memory_size,
        args.uid == 0,
        remove,
    )


def _lookup_devices(devices: list[str]) -> list[str]:
    """
    Looks up matching devices in /dev and returns a list
    of fully qualified device paths.

    Raises exception if any devices cannot be found.
    """
    matched_devices = []
    unmatched_devices = []

    for dev in devices:
        pattern = dev
        if not pattern.startswith("/"):
            pattern = "/dev/" + pattern
        found_devices = glob(pattern)
        if len(found_devices) == 0:
            unmatched_devices.append(dev)
        else:
            matched_devices.extend(found_devices)

    if len(unmatched_devices) > 0:
        raise UnmatchedDeviceError(unmatched_devices)

    return matched_devices


def _dependency_verification(map_name: str) -> bool:
    """Check if all the dependencies are installed or not.

    Args:
        map_name: HAP/MAP name

    Returns:
        True if all dependencies are satisfied, otherwise False.
    """
    logger.info("Checking dependencies...")

    # check for docker
    prog = "docker"
    logger.info(f'--> Verifying if "{prog}" is installed...\n')
    if not shutil.which(prog):
        logger.error(
            '"%s" not installed, please install it from https://docs.docker.com/engine/install/.',
            prog,
        )
        return False

    buildx_paths = [
        os.path.expandvars("$HOME/.docker/cli-plugins"),
        "/usr/local/lib/docker/cli-plugins",
        "/usr/local/libexec/docker/cli-plugins",
        "/usr/lib/docker/cli-plugins",
        "/usr/libexec/docker/cli-plugins",
    ]
    prog = "docker-buildx"
    logger.info('--> Verifying if "%s" is installed...\n', prog)
    buildx_found = False
    for path in buildx_paths:
        if shutil.which(os.path.join(path, prog)):
            buildx_found = True

    if not buildx_found:
        logger.error(
            '"%s" not installed, please install it from https://docs.docker.com/engine/install/.',
            prog,
        )
        return False

    # check for map image
    logger.info('--> Verifying if "%s" is available...\n', map_name)
    if not image_exists(map_name):
        logger.error("Unable to fetch required image.")
        return False

    return True


def _pkg_specific_dependency_verification(pkg_info: dict) -> bool:
    """Checks for any package specific dependencies.

    Currently it verifies the following dependencies:
    * If gpu has been requested by the application, verify that nvidia-ctk is installed.
    Note: when running inside a Docker container, always assume nvidia-ctk is installed.
    Args:
        pkg_info: package manifest as a python dict

    Returns:
        True if all dependencies are satisfied, otherwise False.
    """
    if os.path.exists("/.dockerenv"):
        logger.info("--> Skipping nvidia-ctk check inside Docker...\n")
        return True

    requested_gpus = get_requested_gpus(pkg_info)
    if requested_gpus > 0:
        # check for NVIDIA Container TOolkit
        prog = "nvidia-ctk"
        logger.info('--> Verifying if "%s" is installed...\n', prog)
        if not shutil.which(prog):
            logger.error(
                '"%s" not installed, please install NVIDIA Container Toolkit.', prog
            )
            return False

        logger.info('--> Verifying "%s" version...\n', prog)
        output = run_cmd_output(["nvidia-ctk", "--version"], "version")
        match = re.search(r"([0-9]+\.[0-9]+\.[0-9]+)", output)
        min_ctk_version = "1.12.0"
        recommended_ctk_version = "1.14.1"

        if match is None:
            logger.error(
                f"Error detecting NVIDIA Container Toolkit version. "
                f"Version {min_ctk_version}+ is required ({recommended_ctk_version}+ recommended)."
            )
            return False
        elif compare_versions(min_ctk_version, match.group()) > 0:
            logger.error(
                f"Found '{prog}' Version {match.group()}. "
                f"Version {min_ctk_version}+ is required ({recommended_ctk_version}+ recommended)."
            )
            return False

    return True


def execute_run_command(args: Namespace):
    """
    Entrypoint for the Holoscan Run command.

    Args:
        args: Namespace object containing user arguments.

    Returns:
        None
    """
    if not _dependency_verification(args.map):
        logger.error("Execution Aborted")
        sys.exit(2)
    try:
        # Fetch application manifest from MAP
        app_info, pkg_info = _fetch_map_manifest(args.map)
    except Exception as e:
        logger.error(f"Failed to fetch MAP manifest: {e}")
        sys.exit(2)

    if not _pkg_specific_dependency_verification(pkg_info):
        logger.error("Execution Aborted")
        sys.exit(2)
    try:
        # Run Holoscan Application
        _run_app(args, app_info, pkg_info)
    except Exception as ex:
        logger.debug(ex, exc_info=True)
        logger.error(f"Error executing {args.map}: {ex}")
        sys.exit(2)
