# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from abc import ABC, abstractmethod
import base64
import shutil
from pathlib import Path
import tempfile
import shlex
import socket
from typing import List, Optional, Set
from jupyter_server.serverapp import ServerApp
import platform

from .utils import maybe_await


class NsightTool(ABC):
    class VersionError(Exception):
        pass

    class ArgumentError(Exception):
        pass

    def __init__(self, kernel_id: str, installation_path: str, args: str):
        self.kernel_id = kernel_id
        self.installation_path = installation_path
        self.args = shlex.split(args)
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_report_path = Path(self.tmp_dir.name) / f'tmp_report.{self.target_exe_name()}-rep'
        self.target_exe = shutil.which(self.target_exe_name(), path=self.target_exe_dir())

    @abstractmethod
    def target_exe_name(self) -> str:
        """
        Returns the name of the tool executable
        """

    @abstractmethod
    def target_exe_dir(self) -> Optional[Path]:
        """
        Returns the path to the directory of the tool executable.
        """

    @abstractmethod
    def launch_kernel_cmd(self) -> List[str]:
        """
        Returns the tool command to inject to the kernel launch command.
        """

    @abstractmethod
    def set_version(self, version: str) -> Optional[str]:
        """
        Set and validate the version of the tool.
        The version argument is the output of the tool executable when called with --version.
        The optional returned string is a warning that should be displayed to the user.
        Raises NsightTool.VersionError if the version is not supported.
        """

    @abstractmethod
    def get_start_code(self, **kwargs) -> str:
        """
        Returns the Python code to start the tool (to be executed by the kernel).
        """

    @abstractmethod
    def get_stop_code(self, **kwargs) -> str:
        """
        Returns the Python code to stop the tool (to be executed by the kernel).
        """

    @abstractmethod
    def get_not_allowed_options(self):
        """
        Returns a set of options that are not allowed to be used with the tool.
        """

    @staticmethod
    def normalize_path(path: str):
        path = Path(path).expanduser()
        if path.is_absolute():
            path = path.resolve()
            server_root_dir = ServerApp.instance().root_dir
            if path.is_relative_to(server_root_dir):
                path = path.relative_to(server_root_dir)
        return path

    def _check_supported_args(self, args: Set[str]):
        not_allowed = args & self.get_not_allowed_options()
        if not_allowed:
            return 'The following options are not supported by Nsight extension: ' \
                f'{list(not_allowed)}. '
        return ''

    def cleanup(self):
        self.tmp_dir.cleanup()
    
    async def save_report(self, path: str):
        """
        Save `self.tmp_report_path` (which was just created by the tool) to `path`.
        And remove `self.tmp_report_path`.
        """
        if not self.tmp_report_path.exists():
            return False

        normalized_path = NsightTool.normalize_path(path)
        if normalized_path.is_absolute():
            # `normalize_path` returns absolute path only when the output directory setting
            # is set to an absolute path, that is not relative to the server root.
            # In this case, ContentsManager can't and should not be used.
            shutil.copy(self.tmp_report_path, normalized_path)
            self.tmp_report_path.unlink()
            return True

        # For relative paths, ContentsManager MUST be used. Because the file system
        # is not guaranteed to be mounted locally.
        contents_manager = ServerApp.instance().contents_manager
        model = {
            "type": "file",
            "format": "base64",
            "content": base64.b64encode(self.tmp_report_path.read_bytes()).decode('ascii')
        }
        self.tmp_report_path.unlink()
        path_str = str(normalized_path)
        await maybe_await(contents_manager.save(model, path_str))
        return True


class NsysProfiler(NsightTool):
    min_supported_version = '2024.1.1'

    def __init__(self, *args, **kwargs):
        self._set_target_dir_name()
        super().__init__(*args, **kwargs)
        self.stats_requested = False
        error_message = self._check_supported_args(set(self.args))
        if error_message:
            raise NsightTool.ArgumentError(error_message)

    def _set_target_dir_name(self):
        platform_system = platform.system()
        if platform_system == 'Linux':
            if platform.machine() == 'x86_64':
                self.nsys_target_dir_name = 'target-linux-x64'
            elif platform.machine() == 'aarch64':
                # Logic is taken from QuadD/Host/Analysis/SshDevice.cpp
                device_tree_path = Path('/proc/device-tree')
                is_tegra_based = device_tree_path.exists() and device_tree_path.is_dir() and \
                    any(f.name.startswith('tegra') for f in device_tree_path.iterdir()
                        if f.is_file())
                is_desktop_gpu_driver = False
                is_mobile_gpu_driver = False
                for line in Path('/proc/modules').read_text().splitlines():
                    if line.startswith('nvgpu'):
                        is_mobile_gpu_driver = True
                    elif line.startswith('nvidia'):
                        is_desktop_gpu_driver = True
                if is_tegra_based and is_mobile_gpu_driver:
                    self.nsys_target_dir_name = 'target-linux-tegra-armv8'
                elif is_desktop_gpu_driver:
                    self.nsys_target_dir_name = 'target-linux-sbsa-armv8'
                else:
                    raise NotImplementedError(
                        f'Unsupported Linux aarch64 platform: is_tegra_based={is_tegra_based} '
                        f'is_desktop_gpu_driver={is_desktop_gpu_driver} '
                        f'is_mobile_gpu_driver={is_mobile_gpu_driver}')
            else:
                raise NotImplementedError(f'Nsys is not supported on {platform.machine()}')
        elif platform_system == 'Windows':
            self.nsys_target_dir_name = 'target-windows-x64'
        else:
            raise NotImplementedError(f'Nsys is not supported on {platform_system}')

    def target_exe_name(self) -> str:
        return 'nsys'

    def target_exe_dir(self) -> Optional[Path]:
        if self.installation_path:
            return Path(self.installation_path) / self.nsys_target_dir_name

    def launch_kernel_cmd(self) -> List[str]:
        return [self.target_exe, 'launch', f'--session={self.kernel_id}'] + self.args

    def set_version(self, version: str):
        version = version.split()[-1]
        if version != socket.gethostname():
            version = version.split('-')[0]
            if tuple(map(int, version.split('.'))) < tuple(map(int, self.min_supported_version.split('.'))):
                raise self.VersionError(f'jupyterlab-nvidia-nsight requires nsys >= "{self.min_supported_version}".'
                                        f' Found: "{version}"')

    def get_start_code(self, args: str) -> str:
        error_message = self._check_supported_args(set(shlex.split(args)))
        if error_message:
            raise self.ArgumentError(error_message)

        args = shlex.split(args)
        if '--stats=true' in args or \
           ('--stats' in args and len(args) > args.index('--stats') + 1 and args[args.index('--stats') + 1] == 'true'):
            self.stats_requested = True

        return f"""
subprocess.check_call(
    ['{self.target_exe}', 'start', '--session={self.kernel_id}', '--output={self.tmp_report_path}', '-f', 'true'] + {args})
"""

    def get_stop_code(self) -> str:
        code = f"""subprocess.check_call(
            ['{self.target_exe}', 'stop', '--session={self.kernel_id}'], stderr=subprocess.PIPE)
"""
        if self.stats_requested:
            code += f"""
if pathlib.Path('{self.tmp_report_path}').exists():
    subprocess.check_call(
        ['{self.target_exe}', 'stats', '{self.tmp_report_path}', '--force-export=true'])
"""
        self.stats_requested = False
        return code

    def get_not_allowed_options(self):
        return {
            '--help', '-h',
            '--hotkey-capture',
            '--output', '-o',
            '--session-new',
            '--session',
            '--stop-on-exit', '-x',
        }


class NcuProfiler(NsightTool):
    nvtx_domain = 'JupyterLabNvidiaNsight'
    min_supported_version = '2024.3'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_enable_args()
        self.ncu_ui_support = True

        # self.report_path contains the profiling results during the whole kernel lifecycle.
        self.report_path = Path(self.tmp_dir.name) / 'report.ncu-rep'
        self.intermediate_report_path = Path(self.tmp_dir.name) / 'intermediate_report.ncu-rep'

    def target_exe_name(self) -> str:
        return 'ncu'

    def target_exe_dir(self) -> Optional[Path]:
        if self.installation_path:
            return Path(self.installation_path)

    def launch_kernel_cmd(self) -> List[str]:
        return [self.target_exe,
                '-o', str(self.report_path),
                '--nvtx-exclude', f'{self.nvtx_domain}@exclude'] + self.args

    def set_version(self, version: str):
        version = version.strip().splitlines()[-1].split()[1]
        if tuple(map(int, version.split('.'))) < tuple(map(int, self.min_supported_version.split('.'))):
            self.ncu_ui_support = False
            return f'''jupyterlab-nvidia-nsight requires ncu >= "{self.min_supported_version}" for full support.
Found: "{version}". Using console output only.'''

    def get_start_code(self, args: str) -> str:
        self.validate_start_args(set(shlex.split(args)))

    def get_stop_code(self, args: str, range_id: str) -> str:
        if not self.report_path.exists():
            return ''
        if not self.ncu_ui_support:
            # NCU < 2024.3
            return f"""
subprocess.check_call(
    '{self.target_exe} -i {self.report_path} --nvtx-include {self.nvtx_domain}@{range_id} {args}',
    shell=True)
"""

        return f"""
# First, filter from the full report the last cell(s) profiling results.
# This prevents flag conflict when the user uses "--nvtx-include".
subprocess.check_call(
    ['{self.target_exe}', '-i', '{self.report_path}',
     '--nvtx-include', '{self.nvtx_domain}@{range_id}', '-o', '{self.intermediate_report_path}', '-f'],
    stdout=subprocess.DEVNULL)

# Export the new report, using the CLI flags provided by the user.
subprocess.check_call(
    '{self.target_exe} -i {self.intermediate_report_path} -o {self.tmp_report_path} -f --log-file stderr {args}',
    shell=True)

# Generate console output of the new report, using the CLI flags provided by the user.
subprocess.check_call('{self.target_exe} -i {self.intermediate_report_path} {args}', shell=True)
"""

    def validate_enable_args(self):
        if '--nvtx' not in self.args:
            self.args.append('--nvtx')

        args = set(self.args)
        error_message = self._check_supported_args(args)

        not_allowed_on_enable = args & self.NOT_ALLOWED_OPTIONS_ON_ENABLE
        if not_allowed_on_enable:
            error_message += 'The following options can be used only when profiling cells, ' \
                f'not when enabling ncu: {list(not_allowed_on_enable)}. '

        if error_message:
            raise self.ArgumentError(error_message)

    def validate_start_args(self, args: Set[str]):
        error_message = self._check_supported_args(args)

        not_allowed_on_start = args & self.NOT_ALLOWED_OPTIONS_ON_START
        if not_allowed_on_start:
            error_message += 'The following options can be used only when enabling NCU tool ' \
                + str(list(not_allowed_on_start))

        if error_message:
            raise self.ArgumentError(error_message)

    def get_not_allowed_options(self):
        return {
            '--app-replay-buffer',
            '--app-replay-match',
            '--app-replay-mode',
            '--check-exit-code',
            '--chips',
            '--config-file-path',
            '--config-file',
            '--export', '-o',
            '--force-overwrite', '-f',
            '--help', '-h',
            '--hostname',
            '--import', '-i',
            '--kill',
            '--list-chips',
            '--list-metrics',
            '--list-rules',
            '--list-sections',
            '--list-sets',
            '--log-file',
            '--mode',
            '--null-stdin',
            '--open-in-ui',
            '--profile-from-start',
            '--query-metrics-collection',
            '--query-metrics-mode',
            '--query-metrics',
            '--quiet',
            '--range-filter',
            '--range-replay-options',
            '--rename-kernels-export',
            '--replay-mode',
            '--section-folder-restore',
            '--version', '-v',
        }

    NOT_ALLOWED_OPTIONS_ON_ENABLE = {
        '--csv',
        '--devices',
        '--disable-extra-suffixes',
        '--filter-mode',
        '--kernel-id',
        '--kernel-name-base',
        '--kernel-name', '-k',
        '--launch-count', '-c',
        '--launch-skip-before-match',
        '--launch-skip', '-s',
        '--nvtx-exclude',
        '--nvtx-include',
        '--page',
        '--print-details',
        '--print-fp',
        '--print-kernel-base',
        '--print-metric-attribution',
        '--print-metric-instances',
        '--print-metric-name',
        '--print-nvtx-rename',
        '--print-rule-details',
        '--print-source',
        '--print-summary',
        '--print-units',
        '--rename-kernels-path',
        '--rename-kernels',
        '--resolve-source-file',
    }

    NOT_ALLOWED_OPTIONS_ON_START = {
        '--apply-rules',
        '--cache-control',
        '--call-stack-type',
        '--call-stack',
        '--clock-control',
        '--disable-profiler-start-stop',
        '--graph-profiling',
        '--import-source',
        '--injection-path-32',
        '--injection-path-64',
        '--max-connections',
        '--metrics',
        '--pm-sampling-buffer-size',
        '--pm-sampling-interval',
        '--pm-sampling-max-passes',
        '--port', '-p',
        '--preload-library',
        '--rule',
        '--section-folder-recursive',
        '--section-folder',
        '--section',
        '--set',
        '--source-folders',
        '--support-32bit',
        '--target-processes-filter',
        '--target-processes',
        '--verbose',
        '--warp-sampling-buffer-size',
        '--warp-sampling-interval',
        '--warp-sampling-max-passes',
    }


tools = {
    'nsys': NsysProfiler,
    'ncu': NcuProfiler
}
