from __future__ import annotations

import importlib
import lzma
import os
import pprint
import random
import re
import shutil
import sys
import time
from dataclasses import dataclass
from functools import wraps
from types import TracebackType
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

from xproject.xcommand import execute_cmd_code_by_subprocess_popen, execute_cmd_code_by_subprocess_run
from xproject.xlogger import get_logger, Logger
from xproject.xurl import url_to_file_path, get_furl_obj

if TYPE_CHECKING:
    import frida as f
    import _frida as _f

    Device = _f.Device
    Session = _f.Session
    Script = _f.Script
    Application = _f.Application
    Process = _f.Process
else:
    Device = object
    Session = object
    Script = object
    Application = object
    Process = object


@dataclass(frozen=True)
class FridaData:
    frida_server_xz_url: str
    frida_server_version: str
    pc_frida_server_xz_file_path: str
    pc_frida_server_file_path: str
    mobile_frida_server_file_path: str
    mobile_frida_server_process_name: str


P = ParamSpec("P")
R = TypeVar("R")


def frida_log(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        self: Frida = args[0]
        logger = getattr(self, "logger")
        if logger is not None:
            logger.debug(f"Calling {func.__qualname__}...")
        result = func(*args, **kwargs)
        if logger is not None:
            logger.debug(f"Called {func.__qualname__}.")
        return result

    return wrapper


class Frida:
    def __init__(
            self,
            frida_server_xz_url: str | None = None,
            device_id: str | None = None,
            logger: Logger | None = None,
            timeout: int = 5,
            encoding: str | None = None,
            with_use_open_log: bool = True,
            with_use_init: bool = True
    ) -> None:
        """
        https://github.com/frida/frida/releases
        """
        if not frida_server_xz_url:
            frida_server_xz_url = "https://github.com/frida/frida/releases/download/16.0.0/frida-server-16.0.0-android-arm64.xz"
        self.frida_server_xz_url = frida_server_xz_url

        self.device_id = device_id

        self.logger: Logger | None = None
        if logger is None:
            logger = get_logger()
        else:
            self.logger = logger
        self._logger = logger

        self.timeout = timeout

        self.encoding = encoding

        self.with_use_open_log = with_use_open_log
        self.with_use_init = with_use_init

        self.frida_data = self._create_frida_data()
        assert self.frida_data is not None

        self.device: Device | None = None
        self.session: Session | None = None
        self.script: Script | None = None

    def open_log(self) -> None:
        if self.logger is None:
            self.logger = self._logger

    def close_log(self) -> None:
        if self.logger is not None:
            self.logger = None

    @frida_log
    def _create_frida_data(self) -> FridaData | None:
        try:
            segments = get_furl_obj(self.frida_server_xz_url).path.segments
            assert len(segments) == 6
            assert segments[0] == "frida"
            assert segments[1] == "frida"
            assert segments[2] == "releases"
            assert segments[3] == "download"
            frida_server_version = segments[4]

            from xproject import get_file_assets_dir_path
            assets_dir_path = get_file_assets_dir_path(__file__)
            mobile_dir_path = "/data/local/tmp/"

            frida_server_xz_file_name = os.path.basename(self.frida_server_xz_url)
            pc_frida_server_xz_file_path = os.path.join(assets_dir_path, frida_server_xz_file_name)

            frida_server_file_name = re.sub(r"\.xz$", "", frida_server_xz_file_name, re.DOTALL)
            pc_frida_server_file_path = os.path.join(assets_dir_path, frida_server_file_name)

            mobile_frida_server_file_path = (
                mobile_dir_path + frida_server_file_name
                if mobile_dir_path.endswith("/") else
                mobile_dir_path + "/" + frida_server_file_name
            )
            mobile_frida_server_process_name = frida_server_file_name

            return FridaData(
                self.frida_server_xz_url,
                frida_server_version,
                pc_frida_server_xz_file_path,
                pc_frida_server_file_path,
                mobile_frida_server_file_path,
                mobile_frida_server_process_name
            )
        except:  # noqa
            return None

    @frida_log
    def _download_frida_server_xz(self) -> bool:
        return url_to_file_path(
            self.frida_data.frida_server_xz_url,
            file_path=self.frida_data.pc_frida_server_xz_file_path
        ) == self.frida_data.pc_frida_server_xz_file_path

    @frida_log
    def _decompress_frida_server_xz(self) -> bool:
        with (
            lzma.open(self.frida_data.pc_frida_server_xz_file_path, "rb") as f_in,
            open(self.frida_data.pc_frida_server_file_path, "wb") as f_out
        ):
            shutil.copyfileobj(f_in, f_out)  # type: ignore
            return True

    @frida_log
    def _push_and_chmod_frida_server(self) -> bool:
        text = execute_cmd_code_by_subprocess_run(
            f"adb shell test -e {self.frida_data.mobile_frida_server_file_path} && echo 1 || echo 0",
            encoding=self.encoding,
            logger=self.logger
        ).text
        if text == "0":
            return execute_cmd_code_by_subprocess_run(
                f"adb push {self.frida_data.pc_frida_server_file_path} "
                f"{self.frida_data.mobile_frida_server_file_path}",
                encoding=self.encoding,
                logger=self.logger
            ).result.returncode == 0

        text = execute_cmd_code_by_subprocess_run(
            f"adb shell test -x {self.frida_data.mobile_frida_server_file_path} && echo 1 || echo 0"
        ).text
        if text == "0":
            return execute_cmd_code_by_subprocess_run(
                f"adb shell chmod 755 {self.frida_data.mobile_frida_server_file_path}",
                encoding=self.encoding,
                logger=self.logger
            ).result.returncode == 0

        return True

    @frida_log
    def _pip_install_frida(self) -> bool:
        text = execute_cmd_code_by_subprocess_popen(
            "pip show frida",
            encoding=self.encoding,
            logger=self.logger
        ).text

        if text == "WARNING: Package(s) not found: frida":
            return execute_cmd_code_by_subprocess_popen(
                f"pip install frida=={self.frida_data.frida_server_version}",
                encoding=self.encoding,
                logger=self.logger
            ).returncode == 0

        else:
            if f"Version: {self.frida_data.frida_server_version}" not in text:
                return execute_cmd_code_by_subprocess_popen(
                    f"pip install --upgrade --force-reinstall frida=={self.frida_data.frida_server_version}",
                    encoding=self.encoding,
                    logger=self.logger
                ).returncode == 0

        return True

    @frida_log
    def _pip_install_frida_tools(self) -> bool:
        text = execute_cmd_code_by_subprocess_popen(
            "pip show frida-tools",
            encoding=self.encoding,
            logger=self.logger
        ).text
        if text == "WARNING: Package(s) not found: frida-tools":
            return execute_cmd_code_by_subprocess_popen(
                "pip install frida-tools",
                encoding=self.encoding,
                logger=self.logger
            ).returncode == 0
        return True

    @frida_log
    def _pip_install_frida_and_frida_tools(self) -> bool:
        if not self._pip_install_frida():
            return False

        if not self._pip_install_frida_tools():
            return False

        return True

    @frida_log
    def _import_frida(self) -> bool:
        if not self._pip_install_frida():
            return False
        globals()["f"] = importlib.import_module("frida")

        if not self._pip_install_frida_tools():
            return False
        globals()["_f"] = importlib.import_module("_frida")
        return True

    @frida_log
    def init(self):
        assert self._download_frida_server_xz() is True

        assert self._decompress_frida_server_xz() is True

        assert self._push_and_chmod_frida_server() is True

    @frida_log
    def frida_server_is_running(self) -> bool:
        return execute_cmd_code_by_subprocess_popen(
            f"adb shell pidof {self.frida_data.mobile_frida_server_process_name}",
            encoding=self.encoding,
            logger=self.logger
        ).text != ""

    @frida_log
    def start_frida_server(self) -> bool:
        if not self.frida_server_is_running():
            return execute_cmd_code_by_subprocess_run(
                f'''adb shell su -c "{self.frida_data.mobile_frida_server_file_path} >/dev/null 2>&1 &"''',
                encoding=self.encoding,
                logger=self.logger
            ).text == ""

        return True

    @frida_log
    def stop_frida_server(self) -> bool:
        if self.frida_server_is_running():
            return execute_cmd_code_by_subprocess_popen(
                f'''adb shell su -c "kill -9 $(pidof {self.frida_data.mobile_frida_server_process_name})"''',
                encoding=self.encoding,
                logger=self.logger
            ).returncode == 0

        return True

    @frida_log
    def init_device(self) -> None:
        if not self.frida_server_is_running():
            return

        self._import_frida()

        self.device = f.get_device(self.device_id) if self.device_id else f.get_usb_device(self.timeout)

    @frida_log
    def detach_session(self) -> None:
        if self.session is not None:
            self.session.detach()
            self.session = None

    @frida_log
    def spawn(self, package_names: list[str] | str) -> None:
        self.detach_session()

        if isinstance(package_names, str):
            package_names = [package_names]

        if not package_names:
            return

        pid = self.device.spawn(package_names)  # noqa
        self.session = self.device.attach(pid)
        self.device.resume(pid)
        if self.logger is not None:
            self.logger.info(f"Spawned package_names, package_names: {package_names}")

        seconds = random.uniform(1, 3)
        if self.logger is not None:
            self.logger.info(f"Random sleep for {seconds:.2f} seconds")

        time.sleep(seconds)

    @frida_log
    def get_frontmost_application(self) -> Application | None:
        return self.device.get_frontmost_application()

    @frida_log
    def attach(self, pid_or_process_name: int | str | None = None) -> None:
        self.detach_session()

        if pid_or_process_name is None:
            application = self.get_frontmost_application()
            pid = application.pid
            pid_or_process_name = pid

        if not pid_or_process_name:
            return

        self.session = self.device.attach(pid_or_process_name)
        if self.logger is not None:
            self.logger.info(f"Attached pid_or_process_name, pid_or_process_name: {pid_or_process_name}")

    @frida_log
    def unload_script(self) -> None:
        if self.script is not None:
            self.script.unload()
            self.script = None

    @frida_log
    def load_script(self, js_file_path_or_js_code: str, on_message=None) -> None:
        self.unload_script()

        if not js_file_path_or_js_code:
            return

        if os.path.isfile(js_file_path_or_js_code) and os.path.exists(js_file_path_or_js_code):
            with open(js_file_path_or_js_code, "r", encoding="utf-8") as file:
                js_code = file.read()
        else:
            js_code = js_file_path_or_js_code

        self.script = self.session.create_script(js_code)

        def default_message(message, data):
            if message["type"] == "send":
                text = f"[*] {message['payload']}"
                if self.logger is not None:
                    self.logger.success(text)
                else:
                    print(text)
            else:
                text = f"[*] {pprint.pformat(message)}"
                if self.logger is not None:
                    self.logger.success(text)
                else:
                    print(text)

        self.script.on("message", on_message or default_message)
        self.script.load()
        if self.logger is not None:
            self.logger.info(f"Script loaded, js_file_path_or_js_code: {js_file_path_or_js_code}")

    @frida_log
    def listen(
            self,
            use_unload_script: bool = True,
            use_detach_session: bool = True
    ) -> None:
        try:
            for line in sys.stdin:
                if line.strip().lower() in ("exit", "quit"):
                    break
        except KeyboardInterrupt:
            if self.logger is not None:
                self.logger.warning(f"Interrupted by user, cleaning up")
        finally:
            if use_unload_script:
                self.unload_script()
            if use_detach_session:
                self.detach_session()

    def __enter__(self) -> Frida:
        if self.with_use_open_log:
            self.open_log()
        if self.with_use_init:
            self.init()
        self.start_frida_server()
        self.init_device()
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None
    ) -> None:
        self.stop_frida_server()

    def get_processes(self) -> list[Process]:
        return self.device.enumerate_processes()


if __name__ == '__main__':
    def main1():
        frida = Frida()
        frida.open_log()
        frida.init()
        frida.start_frida_server()
        frida.init_device()

        frida.spawn("com.example.networkapplication")
        # frida.attach()

        # language=JavaScript
        js_code = """
                  Java.perform(function () {
                    let MainActivity = Java.use("com.example.networkapplication.MainActivity");
                    MainActivity["s"].implementation = function (message) {
                      console.log(`MainActivity.s is called: message=${message}`);
                      this["s"](message);
                    };
                  });
                  """

        frida.load_script(js_code)
        frida.listen()

        frida.stop_frida_server()


    def main2():
        with Frida(with_use_init=False) as frida:
            # frida.spawn("com.example.networkapplication")
            frida.attach()

            # language=JavaScript
            js_code = """
                      Java.perform(function () {
                        let MainActivity = Java.use("com.example.networkapplication.MainActivity");
                        MainActivity["s"].implementation = function (message) {
                          console.log(`MainActivity.s is called: message=${message}`);
                          this["s"](message);
                        };
                      });
                      """

            frida.load_script(js_code)
            frida.listen()


    main1()
    main2()
