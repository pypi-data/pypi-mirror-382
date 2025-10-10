# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import atexit
import socket
import docker
import json
import urllib.request
import tempfile
from pathlib import Path
from typing import Dict, Optional, Set
import tarfile
from io import BytesIO
from functools import lru_cache, partial
from http import HTTPStatus
import base64

from docker.models.containers import Container
from docker.models.images import Image
from jupyter_server.serverapp import ServerApp

from .utils import maybe_await


class WebRTCManager:
    http_port = 8080
    report_path_to_container = {}
    image_name = 'nvidia/devtools/nsight-streamer-{}'
    timeout = 10     # seconds
    inside_docker = Path('/.dockerenv').exists()
    report_dir_path = Path('/mnt/host')

    # Default paths for SSL certificate and key files in selkies-gstreamer, used by Nsight Streamer.
    ssl_keyfile_path = Path('/etc/ssl/private/ssl-cert-snakeoil.key')
    ssl_certfile_path = Path('/etc/ssl/certs/ssl-cert-snakeoil.pem')
    # In https mode, we wrap the Nsight Streamer entrypoint script
    # to set the SELKIES_ENABLE_HTTPS environment variable.
    https_entrypoint_script_path = Path('/setup/entrypoint-https.sh')

    atexit.register(
        lambda: [container.stop() for container in WebRTCManager.report_path_to_container.values()])

    @classmethod
    def get_docker_client(cls):
        try:
            return docker.DockerClient()
        except docker.errors.DockerException as e:
            if cls.inside_docker:
                message = 'Failed to start docker client. Is the docker socket mounted? ' \
                    '(try adding "-v /var/run/docker.sock:/var/run/docker.sock" ' \
                    'to the docker run command).'
            else:
                message = 'Failed to start docker client. Is the docker service running? ' \
                    '(start it with "systemctl start docker").'

            message += ' Also make sure you have sufficient permissions, see: ' \
                'https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user'
            raise RuntimeError(message) from e

    @classmethod
    def get_docker_image(cls, docker_client: docker.DockerClient, tool_type: str):
        version = cls.get_latest_image_version(tool_type)
        image = f'nvcr.io/{cls.image_name.format(tool_type)}'
        return docker_client.images.get(f'{image}:{version}')

    @classmethod
    async def create_container(cls, tool_type: str, report_path: Path, host: str,
                               max_resolution: Optional[str], allowed_http_ports: Set[int],
                               allowed_media_ports: Set[int], turn_host: str, turn_port: int,
                               turn_username: str, turn_password: str):
        client = cls.get_docker_client()
        image = cls.get_docker_image(client, tool_type)

        http_port, media_port = cls._get_free_ports(
            client, image, allowed_http_ports, allowed_media_ports, turn_port)

        devtool_cmd = cls.get_image_env_var(image, 'DEVTOOL_CMD')
        ports = {cls.http_port: http_port, media_port: media_port}
        environment = {
            'DEVTOOL_CMD': f'{devtool_cmd} {cls.report_dir_path / report_path.name}',
            'HOST_IP': host,
            'TURN_PORT': str(turn_port or media_port),
            'WEB_USERNAME': '',
        }
        if max_resolution:
            environment['MAX_RESOLUTION'] = max_resolution
        if turn_host:
            environment['SELKIES_TURN_HOST'] = turn_host
        if turn_username:
            environment['TURN_USERNAME'] = turn_username
        if turn_password:
            environment['TURN_PASSWORD'] = turn_password

        server_app = ServerApp.instance()
        https_enabled = bool(server_app.certfile and server_app.keyfile)
        entrypoint = ['/bin/bash', str(cls.https_entrypoint_script_path)] if https_enabled else None

        container = client.containers.create(
            image=image,
            ports=ports,
            environment=environment,
            detach=True,
            auto_remove=True,
            entrypoint=entrypoint,
            # Note: Never use volumes= because it won't work when running inside a docker container.
        )

        await cls._copy_report_to_container(container, report_path, str(cls.report_dir_path))

        if https_enabled:
            cls._copy_to_container(container, Path(server_app.certfile),
                                   cls.ssl_certfile_path.parent, cls.ssl_certfile_path.name)
            cls._copy_to_container(container, Path(server_app.keyfile),
                                   cls.ssl_keyfile_path.parent, cls.ssl_keyfile_path.name)
            with tempfile.NamedTemporaryFile(mode='w') as tf:
                tf.write(f"""
    sudo su - "$USER" -c 'echo "export SELKIES_ENABLE_HTTPS=true" >> ~/.bashrc'
    chmod 755 {cls.ssl_keyfile_path.parent}
    chmod 755 {cls.ssl_keyfile_path}
    chmod 755 {cls.ssl_certfile_path}
    source /setup/entrypoint.sh "$@"
    """)
                tf.flush()
                cls._copy_to_container(container, Path(tf.name), cls.https_entrypoint_script_path.parent,
                                       cls.https_entrypoint_script_path.name)

        container.start()
        cls.report_path_to_container[report_path] = container

    @classmethod
    async def run(cls, tool_type: str, report_path: Path, host: str, max_resolution: Optional[str],
                  allowed_http_ports: Set[int], allowed_media_ports: Set[int], turn_host: str,
                  turn_port: int, turn_username: str, turn_password: str):
        if report_path not in cls.report_path_to_container:
            await cls.create_container(tool_type, report_path, host, max_resolution,
                                       allowed_http_ports, allowed_media_ports, turn_host, turn_port,
                                       turn_username, turn_password)
        container = cls.report_path_to_container[report_path]
        return cls.get_docker_client().api.port(container.id, cls.http_port)[0]["HostPort"]

    @classmethod
    def stop(cls, report_path: Path):
        cls.report_path_to_container[report_path].stop()
        del cls.report_path_to_container[report_path]

    @staticmethod
    def _get_free_port(include: Set[int], exclude: Set[int]):
        """
        Get a free port from the include list if not empty.
        Otherwise get a random free port respecting the exclude list.
        Uses `socket` module (i.e., using the system operating system to find a free port).
        """
        if include:
            for port in include:
                with socket.socket() as s:
                    try:
                        s.bind(('', port))
                        return port
                    except OSError:
                        continue
            raise RuntimeError('All allowed ports are in use')

        sockets = []
        try:
            # Bind all excluded ports, so they won't picked up by the OS.
            for port in exclude:
                s = socket.socket()
                try:
                    s.bind(('', port))
                    sockets.append(s)
                except OSError:
                    s.close()

            # Return a random free port.
            with socket.socket() as s:
                s.bind(('', 0))
                return s.getsockname()[1]
        finally:
            for s in sockets:
                s.close()

    @staticmethod
    def _get_free_port_for_container(client: docker.DockerClient, image: Image,
                                     include: Set[int], exclude: Set[int]):
        """
        Get a free port from the include list if not empty.
        Otherwise get a random free port respecting the exclude list.
        Uses `docker` module (i.e., using the docker daemon to find a free port).
        This method is used rather than `_get_free_port` when JupyterLab is running inside a docker
        container, because we need free ports on the docker host.
        """

        def create_dummy_container(ports: Dict[int, int]) -> Container:
            return client.containers.run(image=image, command='sleep infinity', detach=True,
                                         remove=True, stop_signal='SIGKILL', ports=ports)

        if include:
            for port in include:
                try:
                    container = create_dummy_container({port: port})
                    container.stop()
                    return port
                except docker.errors.APIError as e:
                    if e.status_code == HTTPStatus.INTERNAL_SERVER_ERROR.value:
                        continue
                    raise RuntimeError('Failed to get free ports for container') from e
            raise RuntimeError('All allowed ports are in use')

        # Get all free ports from the exclude list.
        excluded_free_ports = []
        for port in exclude:
            try:
                container = create_dummy_container({port: port})
                container.stop()
                excluded_free_ports.append(port)
            except docker.errors.APIError as e:
                if e.status_code == HTTPStatus.INTERNAL_SERVER_ERROR.value:
                    continue
                raise RuntimeError('Failed to get free ports for container') from e

        # Used as a placeholder for finding a free port using docker.
        non_excluded_port = next((p for p in range(1024, 65535) if p not in exclude))

        # Use docker to get a random free port.
        # The excluded free ports are mapped, so they won't be picked up.
        container = create_dummy_container(
            {non_excluded_port: None} | {p: p for p in excluded_free_ports})
        port = client.api.port(container.id, non_excluded_port)[0]["HostPort"]
        container.stop()
        return port

    @classmethod
    def _get_free_ports(cls, docker_client: docker.DockerClient, docker_image: Image,
                        allowed_http_ports: Set[int], allowed_media_ports: Set[int],
                        turn_port: int):
        additional_excluded_ports = {turn_port} if turn_port else set()
        if cls.inside_docker:
            get_free_port = partial(
                cls._get_free_port_for_container, docker_client, docker_image)
        else:
            get_free_port = cls._get_free_port

        http_port = get_free_port(
            allowed_http_ports, allowed_media_ports | additional_excluded_ports)
        media_port = get_free_port(
            allowed_media_ports, allowed_http_ports | additional_excluded_ports)
        return http_port, media_port

    @staticmethod
    async def _copy_report_to_container(container: Container, report_path: Path, to: str):
        if report_path.is_absolute():
            # `normalize_path` returns absolute path only when the output directory setting
            # is set to an absolute path, that is not relative to the server root.
            # In this case, ContentsManager can't and should not be used.
            WebRTCManager._copy_to_container(container, report_path, to)
            return

        # For relative paths, ContentsManager MUST be used. Because the file system
        # is not guaranteed to be mounted locally.
        contents_manager = ServerApp.instance().contents_manager
        report_path_str = str(report_path)
        model = await maybe_await(contents_manager.get(report_path_str))
        content = base64.b64decode(model['content'])
        stream = BytesIO()
        with tarfile.open(fileobj=stream, mode='w|') as tar:
            file_info = tarfile.TarInfo(name=report_path.name)
            file_info.size = len(content)
            tar.addfile(file_info, BytesIO(content))

        container.put_archive(to, stream.getvalue())

    @staticmethod
    def _copy_to_container(container: Container, src: Path, to: str, arcname: Optional[str] = None):
        stream = BytesIO()
        with tarfile.open(fileobj=stream, mode='w|') as tar:
            tar.add(src, arcname=arcname or src.name)

        container.put_archive(to, stream.getvalue())

    @staticmethod
    def get_image_env_var(image: Image, env_var: str) -> str:
        return next(filter(lambda x: x.startswith(f'{env_var}='), image.attrs['Config']['Env'])
               ).split('=')[1]

    @classmethod
    @lru_cache(maxsize=None)
    def get_latest_image_version(cls, tool_type: str):
        with urllib.request.urlopen(
            f'https://api.ngc.nvidia.com/v2/repos/{cls.image_name.format(tool_type)}'
        ) as response:
            return json.loads(response.read().decode())['latestTag']

    @classmethod
    def pull_image(cls, tool_type: str):
        cls.get_docker_client().images.pull(
            f'nvcr.io/{cls.image_name.format(tool_type)}:'
            + cls.get_latest_image_version(tool_type))
