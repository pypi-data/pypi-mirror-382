# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

from __future__ import annotations

import os
import re
import sys
import time
import logging
import threading
import jsonschema
from typing import Callable, Optional

from deadline.unreal_cmd_utils import merge_cmd_args_with_priority
from deadline.client.api import get_deadline_cloud_library_telemetry_client, TelemetryClient
from openjd.adaptor_runtime._version import version as openjd_adaptor_version
from openjd.adaptor_runtime_client import Action
from openjd.adaptor_runtime.process import LoggingSubprocess
from openjd.adaptor_runtime.adaptors import Adaptor, SemanticVersion
from openjd.adaptor_runtime.app_handlers import RegexCallback, RegexHandler
from openjd.adaptor_runtime.application_ipc import ActionsQueue, AdaptorServer
from openjd.adaptor_runtime.adaptors.configuration import AdaptorConfiguration


from .._version import version as adaptor_version
from .common import DataValidation, add_module_to_pythonpath

logger = logging.getLogger(__name__)


class UnrealNotRunningError(Exception):
    """Error that is raised when attempting to use Unreal while it is not running"""

    pass


class UnrealSubprocessWithLogs(LoggingSubprocess): ...


class UnrealAdaptor(Adaptor[AdaptorConfiguration]):
    """
    Adaptor that creates a session in Unreal to Render interactively.
    """

    _SERVER_START_TIMEOUT_SECONDS = 30
    _SERVER_END_TIMEOUT_SECONDS = 30
    _UNREAL_START_TIMEOUT_SECONDS = 86400
    _UNREAL_END_TIMEOUT_SECONDS = 30

    _server: AdaptorServer | None = None

    _server_thread: threading.Thread | None = None

    _unreal_client: UnrealSubprocessWithLogs | None = None

    _action_queue = ActionsQueue()

    _is_rendering: bool = False

    _exc_info: Exception | None = None

    _performing_cleanup = False

    _telemetry_client: TelemetryClient | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_validation = DataValidation()

    @property
    def integration_data_interface_version(self) -> SemanticVersion:
        return SemanticVersion(major=0, minor=1)  # pragma: no cover

    @property
    def telemetry_client(self) -> TelemetryClient:
        """
        Wrapper around the Deadline Client Library telemetry client, in order to set package-specific information
        """

        if not self._telemetry_client:
            self._telemetry_client = get_deadline_cloud_library_telemetry_client()
            self._telemetry_client.update_common_details(
                {
                    "deadline-cloud-for-unreal-engine-adaptor-version": adaptor_version,
                    "open-jd-adaptor-runtime-version": openjd_adaptor_version,
                }
            )
        return self._telemetry_client

    @staticmethod
    def get_timer(timeout: int | float) -> Callable[[], bool]:
        """Given a timeout length, returns a lambda which returns True until the timeout occurs"""
        timeout_time = time.time() + timeout
        return lambda: time.time() < timeout_time

    @property
    def _has_exception(self) -> bool:
        """Property which checks the private _exc_info property for an exception

        :raises self._exc_info: An exception if there is one

        :return: False there is no exception waiting to be raised
        :rtype: bool
        """
        if self._exc_info and not self._performing_cleanup:
            raise self._exc_info
        return False

    @property
    def _unreal_is_running(self) -> bool:
        """Property which indicates that the unreal client is running

        :return: True if the unreal client is running, false otherwise
        :rtype: bool
        """
        return self._unreal_client is not None and self._unreal_client.is_running

    @property
    def _unreal_is_rendering(self) -> bool:
        """Property which indicates if unreal is rendering

        :return: True if unreal is rendering, false otherwise
        :rtype: bool
        """
        return self._unreal_is_running and self._is_rendering

    @_unreal_is_rendering.setter
    def _unreal_is_rendering(self, value: bool) -> None:
        """Property setter which updates the private _is_rendering boolean.

        :param bool value: A boolean indicated if unreal is rendering.
        """
        self._is_rendering = value

    @property
    def unreal_client_path(self) -> str:
        """
        Obtains the unreal_client.py path by searching directories in sys.path

        :raises FileNotFoundError: If the unreal_client.py file could not be found.

        :return: The path to the unreal_client.py file.
        :rtype: str
        """
        for p in sys.path:
            path = os.path.join(p, "deadline", "unreal_adaptor", "UnrealClient", "unreal_client.py")
            if os.path.isfile(path):
                return path
        raise FileNotFoundError(
            "Could not find unreal_client.py. Check that the UnrealClient package is in one of the "
            f"following directories: {sys.path[1:]}"
        )

    def _wait_for_adaptor_server_socket(self) -> str:
        """
        Performs a busy wait for the socket path that the adaptor server is running on, then
        returns it.

        :raises RuntimeError: If the server does not finish initializing

        :return: The socket path the adaptor server is running on.
        :rtype: str
        """
        is_not_timed_out = self.get_timer(self._SERVER_START_TIMEOUT_SECONDS)

        while (self._server is None or self._server.server_path is None) and is_not_timed_out():
            time.sleep(0.01)

        if self._server is not None and self._server.server_path is not None:
            return self._server.server_path

        raise RuntimeError(
            "Could not find a socket path because the server did not finish initializing"
        )

    def _wait_for_unreal_started(self):
        """
        Performs a busy wait for the starting of the Unreal Engine with the UnrealClient script

        :raises RuntimeError: Raised when the UnrealClient encountered an error during initialization
        :raises TimeoutError: Raised when the UnrealClient doesn't complete the initial actions before timeout reached
        """
        is_not_timed_out = self.get_timer(self._UNREAL_START_TIMEOUT_SECONDS)
        while (
            self._unreal_is_running
            and not self._has_exception
            and len(self._action_queue)
            > 0  # for now the initializing actions in the action queue, defined by
            # _populate_client_loaded_action() method.
            # So we wait for them to be done or for time is out.
            and is_not_timed_out()
        ):
            time.sleep(0.1)

        self.telemetry_client.record_event(
            event_type="com.amazon.rum.deadline.adaptor.runtime.start", event_details={}
        )

        if len(self._action_queue) > 0:  # if for some reason, all the actions are not complete
            if is_not_timed_out():  # and timeout is not reached
                raise RuntimeError(  # <- we catch some exception - self._has_exception is True
                    "Unreal encountered an error and was not able to complete initialization actions."
                )
            else:
                raise TimeoutError(  # All the actions are note complete and timeout reached
                    "Unreal did not complete initialization actions in "
                    f"{self._UNREAL_START_TIMEOUT_SECONDS} seconds and failed to start."
                )

    def _start_unreal_server(self) -> None:
        """
        Starts a server with the given ActionsQueue, attaches the server to the adaptor and serves
        forever in a blocking call.
        """
        self._server = AdaptorServer(self._action_queue, self)
        self._server.serve_forever()

    def _start_unreal_server_thread(self) -> None:
        """
        Starts the unreal adaptor server in a thread.
        Sets the environment variable "UNREAL_ADAPTOR_SOCKET_PATH" to the socket the server is running
        on after the server has finished starting.
        """

        self._server_thread = threading.Thread(
            target=self._start_unreal_server, name="UnrealAdaptorServerThread"
        )
        self._server_thread.start()
        os.environ["UNREAL_ADAPTOR_SOCKET_PATH"] = self._wait_for_adaptor_server_socket()

    def _get_regex_callbacks(self) -> list[RegexCallback]:
        """
        Returns a list of RegexCallbacks built from UnrealClient handler regex patterns
        :return: List of Regex Callbacks to add
        :rtype: list[RegexCallback]
        """

        # We should get UE version to write the telemetry in the most proper way
        callbacks: list[RegexCallback] = [
            RegexCallback(
                [re.compile(".*Engine Version: (.*)"), re.compile('.*engineversion="([^"]*)"')],
                self._handle_unreal_engine_version,
            )
        ]

        from deadline.unreal_adaptor.UnrealClient.step_handlers import get_step_handler_class

        for handler_name in ["render", "custom"]:
            handler_class = get_step_handler_class(handler_name)

            logger.info(f"Getting regex patterns from step handler: {handler_class}...")

            callbacks.append(
                RegexCallback(handler_class.regex_pattern_progress(), self._handle_progress)
            )

            callbacks.append(
                RegexCallback(handler_class.regex_pattern_complete(), self._handle_complete)
            )

            callbacks.append(RegexCallback(handler_class.regex_pattern_error(), self._handle_error))

        return callbacks

    def _handle_complete(self, match: re.Match) -> None:
        """
        Callback for stdout that indicate completeness of a render. Updates progress to 100

        :param match: re.Match object from the regex pattern that was matched the message
        :type match: re.Match
        """
        self._unreal_is_rendering = False
        self.update_status(progress=100)

    def _handle_progress(self, match: re.Match) -> None:
        """
        Callback for stdout that indicate progress of a render.

        :param match: re.Match object from the regex pattern that was matched the message
        :type match: re.Match
        """
        progress = int(float(match.groups()[0]))
        self.update_status(progress=progress)

    def _handle_error(self, match: re.Match) -> None:
        """
        Callback for stdout that indicates an error or warning.

        :param match: re.Match object from the regex pattern that was matched the message
        :type match: re.Match

        :raises RuntimeError: Always raises a runtime error to halt the adaptor.
        """
        self._exc_info = RuntimeError(f"Unreal Encountered an Error: {match.group(0)}")

    def _handle_unreal_engine_version(self, match: re.Match) -> None:
        """
        Callback for stdout that indicates Unreal Engine version running

        :param match: re.Match object from the regex pattern that was matched the message
        :type match: re.Match
        """

        if match and len(match.groups()) > 0:
            self.telemetry_client.update_common_details(
                {"unreal-engine-version": match.groups()[0]}
            )

    def _start_unreal_client(self) -> None:
        """
        Starts the Unreal client by launching UnrealEditor-Cmd with the unreal_client.py file.

        UnrealEditor-Cmd must be on the system PATH, for example due to a Rez environment being active.

        :raises FileNotFoundError: If the unreal_client.py file could not be found.
        """

        unreal_project_path = self.init_data.get("project_path", "")
        unreal_project_path = os.path.expandvars(unreal_project_path)

        unreal_exe = self.init_data.get("executable", "UnrealEditor-Cmd")
        unreal_exe = os.path.expandvars(unreal_exe)

        # Read args from file since it can be too long to pass
        # them to Job parameter (1024 chars limit)
        extra_cmd_str = self.init_data.get("extra_cmd_args", "") or ""
        extra_cmd_args_file = self.init_data.get("extra_cmd_args_file", "")
        if os.path.exists(extra_cmd_args_file):
            with open(extra_cmd_args_file, "r") as f:
                extra_cmd_file_str = f.read()
                extra_cmd_str = merge_cmd_args_with_priority(extra_cmd_str, extra_cmd_file_str)

        # Everything between -execcmds=" and " is the value we want to keep
        match = re.search(r'-execcmds=["\']([^"\']*)["\']', extra_cmd_str)
        if match:
            execcmds_value = match.group(1)
        else:
            execcmds_value = None

        logger.info(f"execcmds: {execcmds_value}")

        # Remove the -execcmds argument from the extra_cmd_args
        extra_cmd_str = re.sub(r'(-execcmds=["\'][^"\']*["\'])', "", extra_cmd_str)

        client_path = self.unreal_client_path.replace("\\", "/")
        log_args = ["-log", "-unattended", "-stdout", "-allowstdoutlogverbosity", "-nozen"]

        remote_execution = os.getenv("REMOTE_EXECUTION", "True")
        if remote_execution == "True":
            log_args += ["-NoLoadingScreen", "-NoScreenMessages", "-RenderOffscreen", "-nozen"]

        extra_cmd_args = extra_cmd_str.split(" ")

        args = [unreal_exe, unreal_project_path]
        args.extend(log_args)
        args.extend(extra_cmd_args)
        args = [arg for arg in args if arg]  # Remove empty strings
        args = list(dict.fromkeys(args))  # Remove duplicates

        # Add the execcmds argument back to the args
        if execcmds_value is not None:
            execcmds_value = f"-execcmds={execcmds_value},py {client_path}"
        else:
            execcmds_value = f"-execcmds=r.HLOD 0,py {client_path}"

        args.append(execcmds_value)

        # Add Mrq Job Dependencies Descriptor argument if exists
        if "job_dependencies_descriptor" in self.init_data:
            args.append(
                "-MrqJobDependenciesDescriptor={}".format(
                    self.init_data["job_dependencies_descriptor"]
                )
            )

        logger.info(f"Starting Unreal Engine with args: {args}")

        regexhandler = RegexHandler(self._get_regex_callbacks())
        self._unreal_client = UnrealSubprocessWithLogs(
            args=args,
            stdout_handler=regexhandler,
            stderr_handler=regexhandler,
        )

    def _populate_client_loaded_action(self) -> None:
        """
        Populates the adaptor server's action queue with the specific action to check if UE initialized or not yet
        """

        self._action_queue.enqueue_action(Action(name="client_loaded"))

    def _record_error_and_raise(
        self, exc: Exception, exception_scope: str, exit_code: Optional[int] = None
    ) -> None:
        """
        Record telemetry error event and raise given exception
        """
        self.telemetry_client.record_error(
            event_details={"exit_code": exit_code, "exception_scope": exception_scope},
            exception_type=str(type(exc)),
            from_gui=False,
        )
        raise exc

    def on_start(self) -> None:
        """
        For job stickiness. Will start everything required for the Task.

        :raises jsonschema.ValidationError:
            When init_data fails validation against the adaptor schema.
        :raises jsonschema.SchemaError: When the adaptor schema itself is invalid.
        :raises RuntimeError: If Unreal did not complete initialization actions due to an exception
        :raises TimeoutError: If Unreal did not complete initialization actions due to timing out.
        :raises FileNotFoundError: If the unreal_client.py file could not be found.
        """

        try:
            self.data_validation.validate_init_data(self.init_data)
        except (jsonschema.exceptions.ValidationError, jsonschema.exceptions.SchemaError) as e:
            self._record_error_and_raise(exc=e, exception_scope="on_start")

        # Notify worker agent about starting Unreal
        self.update_status(progress=0, status_message="Initializing Unreal Engine")

        # Starts the unreal adaptor server
        try:
            self._start_unreal_server_thread()
        except Exception as e:
            self._record_error_and_raise(exc=e, exception_scope="on_start")

        self._populate_client_loaded_action()

        # Add the openjd and adaptor namespace directory to PYTHONPATH, so that adaptor_runtime_client
        # will be available directly to the adaptor client.

        import openjd.adaptor_runtime_client

        add_module_to_pythonpath(
            os.path.dirname(os.path.dirname(openjd.adaptor_runtime_client.__file__))
        )
        add_module_to_pythonpath(
            os.path.dirname(
                os.path.dirname(os.path.dirname(openjd.adaptor_runtime_client.__file__))
            )
        )

        import deadline.unreal_adaptor

        add_module_to_pythonpath(os.path.dirname(os.path.dirname(deadline.unreal_adaptor.__file__)))

        try:
            self._start_unreal_client()
            self._wait_for_unreal_started()
        except Exception as e:
            self._record_error_and_raise(exc=e, exception_scope="on_start")

    def on_run(self, run_data: dict) -> None:
        """
        This starts a render in Unreal for the given frame and performs a busy wait until the render completes.

        :param run_data: Dictionary containing Run Data
        :type run_data: dict

        :raises jsonschema.ValidationError:
            When init_data fails validation against the adaptor schema.
        :raises jsonschema.SchemaError: When the adaptor schema itself is invalid.
        :raises RuntimeError: When Unreal exited early and did not render successfully
        """
        if not self._unreal_is_running:
            self._record_error_and_raise(
                exc=UnrealNotRunningError("Cannot render because Unreal is not running"),
                exception_scope="on_run",
            )

        try:
            self.data_validation.validate_run_data(run_data)
        except (jsonschema.exceptions.ValidationError, jsonschema.exceptions.SchemaError) as e:
            self._record_error_and_raise(exc=e, exception_scope="on_run")

        # Set up the step handler
        self._action_queue.enqueue_action(
            Action("set_handler", {"handler": run_data.get("handler", "base")})
        )

        self._unreal_is_rendering = True
        self._action_queue.enqueue_action(Action("run_script", run_data))

        while self._unreal_is_rendering and not self._has_exception:
            time.sleep(1)
            # Wait for:
            #   1. set_handler to be executed
            #   2. run_script to be executed (launch render process in separate thread by UE API)
            # by UnrealClient and don't spam before
            if len(self._action_queue) == 0:
                logger.info("Enqueue wait result")
                self._action_queue.enqueue_action(Action("wait_result", {}))

        # The Unreal subprocess always exists at this point but can be terminated by a user script
        # or other means. For example unreal.SystemLibrary.quit_editor().
        # Before treating it as an error, we should check the return code.
        if not self._unreal_is_running and self._unreal_client:
            exit_code = self._unreal_client.returncode
            if exit_code != 0:
                self._record_error_and_raise(
                    exc=RuntimeError(
                        "Unreal exited early and did not render successfully, please check render logs. "
                        f"Exit code {exit_code}"
                    ),
                    exception_scope="on_run",
                    exit_code=exit_code,
                )

    def on_stop(self) -> None:
        """
        Execute stop action
        """
        pass

    def on_cleanup(self):
        """
        Cleans up the adaptor by closing the unreal client and adaptor server.
        """

        self._performing_cleanup = True

        # Send "close" action to the UnrealClient
        self._action_queue.enqueue_action(Action("close"), front=True)

        # Wait for UnrealClient to be terminated
        is_not_timed_out = self.get_timer(self._UNREAL_END_TIMEOUT_SECONDS)
        while self._unreal_is_running and is_not_timed_out():
            time.sleep(0.1)

        if self._unreal_is_running and self._unreal_client:
            logger.error(
                "Unreal did not complete cleanup actions and failed to gracefully shutdown. "
                "Terminating."
            )
            self._unreal_client.terminate(0)

        # Terminate AdaptorServer instance
        if self._server:
            self._server.shutdown()

        # Terminate AdaptorServer thread launched in background
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=self._SERVER_END_TIMEOUT_SECONDS)
            if self._server_thread.is_alive():
                logger.error("Failed to shutdown the Unreal Adaptor server.")

        self._performing_cleanup = False

    def on_cancel(self):
        """
        Cancels the current render if Unreal is rendering.
        """
        logger.info("CANCEL REQUESTED")
        if not self._unreal_client or not self._unreal_is_running:
            logger.info("Nothing to cancel because Unreal is not running")
            return

        # Terminate immediately since the Unreal client does not have a graceful shutdown
        self._unreal_client.terminate(grace_time_s=0)
