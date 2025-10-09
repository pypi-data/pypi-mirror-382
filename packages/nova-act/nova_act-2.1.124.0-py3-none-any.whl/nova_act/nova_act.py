# Copyright 2025 Amazon Inc

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import os
import shutil
import tempfile
import uuid
from typing import Literal, Mapping, Type, cast

from boto3.session import Session
from playwright.sync_api import Page, Playwright

from nova_act.impl.backend import Backend, get_urls_for_backend
from nova_act.impl.common import rsync_to_temp_dir
from nova_act.impl.controller import NovaStateController
from nova_act.impl.dispatcher import ActDispatcher
from nova_act.impl.extension import ExtensionActuator
from nova_act.impl.inputs import (
    validate_base_parameters,
    validate_length,
    validate_prompt,
    validate_step_limit,
    validate_timeout,
    validate_url,
)
from nova_act.impl.run_info_compiler import RunInfoCompiler
from nova_act.impl.telemetry import send_act_telemetry, send_environment_telemetry
from nova_act.tools.browser.default.default_nova_local_browser_actuator import (
    DefaultNovaLocalBrowserActuator,
)
from nova_act.tools.browser.default.playwright_instance_options import PlaywrightInstanceOptions
from nova_act.tools.browser.interface.browser import BrowserActuatorBase
from nova_act.tools.browser.interface.playwright_pages import PlaywrightPageManagerBase


from nova_act.impl.routes.factory import for_backend
from nova_act.types.act_errors import ActError
from nova_act.types.act_result import ActResult
from nova_act.types.errors import (
    AuthError,
    ClientNotStarted,
    IAMAuthError,
    NovaActError,
    StartFailed,
    StopFailed,
    ValidationFailed,
)
from nova_act.types.events import EventType, LogType
from nova_act.types.features import PreviewFeatures
from nova_act.types.hooks import StopHook
from nova_act.types.json_type import JSONType
from nova_act.types.state.act import Act
from nova_act.util.event_handler import EventHandler
from nova_act.util.jsonschema import (
    add_schema_to_prompt,
    populate_json_schema_response,
    validate_jsonschema_schema,
)
from nova_act.util.logging import (
    get_session_id_prefix,
    make_trace_logger,
    set_logging_session,
    setup_logging,
)

DEFAULT_SCREEN_WIDTH = 1600
DEFAULT_SCREEN_HEIGHT = 900

_LOGGER = setup_logging(__name__)
_TRACE_LOGGER = make_trace_logger()


ManagedActuatorType = Type[DefaultNovaLocalBrowserActuator | ExtensionActuator]



class NovaAct:
    """Client for interacting with the Nova Act Agent.

    Example:
    ```
    >>> from nova_act import NovaAct
    >>> n = NovaAct(starting_page="https://nova.amazon.com/act")
    >>> n.start()
    >>> n.act("Click learn more. Then, return the title and publication date of the blog.")
    ```

    Attributes
    ----------
    started: bool
        whether the browser has been launched
    page : playwright.Page
        The playwright Page object for actuation
    pages: list[playwright.Page]
        All playwright Pages available in Browser
    dispatcher: Dispatcher
        Component for sending act prompts to the Browser

    Methods
    -------
    start()
        Starts the client
    act(command)
        Actuates a natural language command in the web browser
    stop()
        Stops the client
    get_page(i)
        Gets a specific playwright page by its index in the browser context
    """

    def __init__(
        self,
        starting_page: str | None = None,
        *,
        boto_session: Session | None = None,
        cdp_endpoint_url: str | None = None,
        cdp_headers: dict[str, str] | None = None,
        cdp_use_existing_page: bool = False,
        chrome_channel: str | None = None,
        clone_user_data_dir: bool = True,
        actuator: ManagedActuatorType | BrowserActuatorBase = DefaultNovaLocalBrowserActuator,
        go_to_url_timeout: int | None = None,
        headless: bool = False,
        ignore_https_errors: bool = False,
        logs_directory: str | None = None,
        nova_act_api_key: str | None = None,
        playwright_instance: Playwright | None = None,
        preview: PreviewFeatures | None = None,
        profile_directory: str | None = None,
        proxy: dict[str, str] | None = None,
        record_video: bool = False,
        screen_width: int = DEFAULT_SCREEN_WIDTH,
        screen_height: int = DEFAULT_SCREEN_HEIGHT,
        stop_hooks: list[StopHook] = [],
        tty: bool = True,
        use_default_chrome_browser: bool = False,
        user_agent: str | None = None,
        user_data_dir: str | None = None,
    ):
        """Initialize a client object.

        Parameters
        ----------
        starting_page : str
            Starting web page for the browser window. Can be omitted if re-using an existing CDP page.
        user_data_dir: str, optional
            Path to Chrome data storage (cookies, cache, etc.).
            If not specified, will use a temp dir.
            Note that if multiple NovaAct instances are used in the same process (e.g., via a ThreadPool), each
            one must have its own user_data_dir. In practice, this means either not specifying user_data_dir
            (so a fresh temp dir is used for each instance) or using clone_user_data_dir=True.
        clone_user_data_dir: bool
            If True (default), will make a copy of user_data_dir into a temp dir for each instance of NovaAct.
            This ensures the original is not modified and that each instance has its own user_data_dir.
            If user_data_dir is not specified, this flag has no effect.
        actuator: ManagedActuatorType
            Type or instance of a custom actuator.
            Note that deviations from NovaAct's standard observation and I/O formats may impact model performance
        profile_directory: str
            Name of the Chrome user profile. Only needed if using an existing, non-Default Chrome profile.
            Must be relative path within user_data_dir.
        screen_width: int
            Width of the screen for the playwright instance. Within range [1536, 2304].
        screen_height: int
            Height of the screen for the playwright instance. Within range [864, 1296].
        headless: bool
            Whether to launch the Playwright browser in headless mode. Defaults to False. Can also be enabled with
            the `NOVA_ACT_HEADLESS` environment variable.
        chrome_channel: str, optional
            Browser channel to use (e.g., "chromium", "chrome-beta", "msedge" etc.). Defaults to "chrome". Can also
            be specified via `NOVA_ACT_CHROME_CHANNEL` environment variable.
        nova_act_api_key: str
            API key for interacting with NovaAct. Will override the NOVA_ACT_API_KEY environment variable
        playwright_instance: Playwright
            Add an existing Playwright instance for use
        tty: bool
            Whether output logs should be formatted for a terminal (true) or file (false)
        cdp_endpoint_url: str, optional
            A Chrome DevTools Protocol (CDP) endpoint to connect to
        cdp_headers: dict[str, str], optional
            Additional HTTP headers to be sent when connecting to a CDP endpoint
        cdp_use_existing_page: bool
             If True, Nova Act will re-use an existing page from the CDP context rather
             than opening a new one
        user_agent: str, optional
            Optionally override the user agent used by playwright.
        logs_directory: str, optional
            Output directory for video and agent run output. Will default to a temp dir.
        record_video: bool
            Whether to record video
        go_to_url_timeout : int, optional
            Max wait time on initial page load in seconds
        ignore_https_errors: bool
            Whether to ignore https errors for url to allow website with self-signed certificates
        stop_hooks: list[StopHook]
            A list of stop hooks that are called when this object is stopped.
        use_default_chrome_browser: bool
            Use the locally installed Chrome browser. Only works on MacOS.
        preview: PreviewFeatures
            Optional preview features for opt-in.
        boto_session : Session, optional
            A boto3 session containing IAM credentials for authentication.
            When provided, enables AWS IAM-based authentication instead of API key authentication.
            Cannot be used together with nova_act_api_key.
        proxy: dict[str, str], optional
            Proxy configuration for the browser. Should contain 'server', 'username', and 'password' keys.
        """

        self._boto_session = boto_session

        self._run_info_compiler: RunInfoCompiler | None = None
        self._backend = self._determine_backend()
        self._backend_info = get_urls_for_backend(self._backend)

        self._starting_page = starting_page


        if preview is not None:
            _LOGGER.warning(
                "No preview features in this release! Check back soon!\n\n"
                "• If you are looking for Playwright Actuation, it is now the default, so no parameters are needed!\n"
                "• If you are looking for Custom Actuators, they can now be passed directly in the `actuator` param."
            )
            if not actuator and (custom_actuator := preview.get("custom_actuator")):
                actuator = cast(BrowserActuatorBase, custom_actuator)

        if actuator is ExtensionActuator:
            _LOGGER.warning(
                "`ExtensionActuator` is deprecated and no longer has any effect. Falling back to default behavior."
            )
            actuator = DefaultNovaLocalBrowserActuator

        _chrome_channel = str(chrome_channel or os.environ.get("NOVA_ACT_CHROME_CHANNEL", "chrome"))
        _headless = headless or bool(os.environ.get("NOVA_ACT_HEADLESS"))

        validate_base_parameters(
            starting_page=self._starting_page,
            use_existing_page=bool(cdp_endpoint_url and cdp_use_existing_page),
            backend_uri=self._backend_info.api_uri,
            profile_directory=profile_directory,
            user_data_dir=user_data_dir,
            screen_width=screen_width,
            screen_height=screen_height,
            logs_directory=logs_directory,
            chrome_channel=_chrome_channel,
            ignore_https_errors=ignore_https_errors,
            clone_user_data_dir=clone_user_data_dir,
            use_default_chrome_browser=use_default_chrome_browser,
            proxy=proxy,
        )

        self._session_user_data_dir_is_temp: bool = False
        if user_data_dir:  # pragma: no cover
            if clone_user_data_dir:
                # We want to make a copy so the original is unmodified.
                _LOGGER.info(f"Copying {user_data_dir} to temp dir")
                self._session_user_data_dir = rsync_to_temp_dir(user_data_dir)
                _LOGGER.info(f"Copied {user_data_dir} to {self._session_user_data_dir}")
                self._session_user_data_dir_is_temp = True
            else:
                # We want to just use the original.
                self._session_user_data_dir = user_data_dir
        else:
            # We weren't given an existing user_data_dir, just make a temp directory.
            self._session_user_data_dir = tempfile.mkdtemp(suffix="_nova_act_user_data_dir")
            self._session_user_data_dir_is_temp = True

        _LOGGER.debug(f"{self._session_user_data_dir=}")

        if logs_directory is None:
            logs_directory = tempfile.mkdtemp(suffix="_nova_act_logs")

        self._logs_directory = logs_directory
        self._session_logs_directory: str = ""
        if go_to_url_timeout is not None:
            validate_timeout(go_to_url_timeout)
        self.go_to_url_timeout = go_to_url_timeout

        self._nova_act_api_key = nova_act_api_key or os.environ.get("NOVA_ACT_API_KEY") or ""

        self._validate_auth()


        if self._nova_act_api_key:
            validate_length(
                starting_page=self._starting_page,
                profile_directory=profile_directory,
                user_data_dir=self._session_user_data_dir,
                nova_act_api_key=self._nova_act_api_key,
                cdp_endpoint_url=cdp_endpoint_url,
                user_agent=user_agent,
                logs_directory=logs_directory,
                backend=self._backend,
            )

        self._tty = tty

        self.screen_width = screen_width
        self.screen_height = screen_height

        self._stop_hooks = stop_hooks
        self._log_stop_hooks_registration()
        user_browser_args = os.environ.get("NOVA_ACT_BROWSER_ARGS", "").split()

        self._session_id: str | None = None


        playwright_options = PlaywrightInstanceOptions(
            maybe_playwright=playwright_instance,
            starting_page=self._starting_page,
            chrome_channel=_chrome_channel,
            headless=_headless,
            user_data_dir=self._session_user_data_dir,
            profile_directory=profile_directory,
            cdp_endpoint_url=cdp_endpoint_url,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
            user_agent=user_agent,
            record_video=bool(record_video and self._logs_directory),
            ignore_https_errors=ignore_https_errors,
            go_to_url_timeout=self.go_to_url_timeout,
            use_default_chrome_browser=use_default_chrome_browser,
            cdp_headers=cdp_headers,
            proxy=proxy,
            cdp_use_existing_page=cdp_use_existing_page,
            user_browser_args=user_browser_args,
        )
        self._cdp_endpoint_url = cdp_endpoint_url

        self._actuator: BrowserActuatorBase
        self._dispatcher: ActDispatcher

        self._event_callback = None

        self._event_handler = EventHandler(self._event_callback)
        self._controller = NovaStateController(self._tty)

        if isinstance(actuator, type):
            if issubclass(actuator, DefaultNovaLocalBrowserActuator):
                if actuator is not DefaultNovaLocalBrowserActuator:
                    _LOGGER.warning(
                        f"Using a custom actuator: {actuator.__name__}\n"
                        "Deviations from NovaAct's standard observation"
                        " and I/O formats may impact model performance"
                    )
                _LOGGER.debug(f"Using a DefaultNovaLocalBrowserActuator: {actuator.__name__}")
                self._actuator = actuator(
                    playwright_options=playwright_options,
                )
            else:
                raise ValidationFailed(
                    "Please subclass DefaultNovaLocalBrowserActuator if passing a custom actuator by type"
                )
        else:
            _LOGGER.warning(
                f"Using a user-defined actuator instance: {type(actuator).__name__}\n"
                "Deviations from NovaAct's standard observation and I/O formats may impact model performance"
            )
            self._actuator = actuator

        self._routes = for_backend(
            backend=self._backend,
            api_key=self._nova_act_api_key,
            boto_session=self._boto_session,
        )


        self._dispatcher = ActDispatcher(
            actuator=self._actuator,
            routes=self._routes,
            event_handler=self._event_handler,
            controller=self._controller,
        )


    def _log_stop_hooks_registration(self) -> None:
        """Log registered stop hooks for debugging purposes."""
        if self._stop_hooks:
            hook_names = [type(hook).__name__ for hook in self._stop_hooks]
            _LOGGER.info(f"Registered stop hooks: {', '.join(hook_names)}")
        else:
            _LOGGER.debug("No stop hooks registered")

    def _determine_backend(self) -> Backend:
        """Determines which Nova Act backend to use."""

        if self._boto_session:
            return Backend.HELIOS

        return Backend.PROD

    def _validate_auth(self) -> None:
        """Validate that the NovaAct instance is using supported authentication methods."""
        # Case 1: Both boto_session and API key provided (invalid)
        if self._boto_session and self._nova_act_api_key:
            raise IAMAuthError("Cannot set both API key and boto session!")

        # Case 2: No authentication provided (invalid)
        if not self._boto_session and not self._nova_act_api_key:
            raise AuthError(backend_info=self._backend_info)  # at least API key must be set

        # Case 3: Only boto_session provided (valid if credentials are valid)
        if self._boto_session and not self._nova_act_api_key:
            self._validate_boto_session(self._boto_session)
            return

        # Case 4: Only API key provided (valid)
        if not self._boto_session and self._nova_act_api_key:
            return

    def _validate_boto_session(self, boto_session: Session) -> None:
        """
        Validate that the boto3 session has valid credentials associated with a real IAM identity.

        Args:
            boto_session: The boto3 session to validate

        Raises:
            IAMAuthError: If the boto3 session doesn't have valid credentials or the credentials
                        are not associated with a real IAM identity
        """
        # Check if credentials exist
        if not boto_session.get_credentials():
            raise IAMAuthError("IAM credentials not found. Please ensure your boto3 session has valid credentials.")

        # Verify credentials are associated with a real IAM identity
        try:
            sts_client = boto_session.client("sts")
            sts_client.get_caller_identity()
        except Exception as e:
            raise IAMAuthError(
                f"IAM validation failed: {str(e)}. Check your credentials with 'aws sts get-caller-identity'."
            )

    def __del__(self) -> None:
        if hasattr(self, "_session_user_data_dir_is_temp") and self._session_user_data_dir_is_temp:
            _LOGGER.debug(f"Deleting {self._session_user_data_dir}")
            shutil.rmtree(self._session_user_data_dir, ignore_errors=True)

    def __enter__(self) -> NovaAct:
        self.start()
        return self

    def __exit__(
        self, exc_type: Type[BaseException] | None, exc_value: BaseException | None, traceback: BaseException | None
    ) -> None:
        self.stop()

    @property
    def started(self) -> bool:
        return self._actuator.started and self._session_id is not None

    @property
    def page(self) -> Page:
        """Get the current playwright page, if the provided actuator is of type PlaywrightPageManagerBase.

        This is the Playwright Page on which the SDK is currently actuating

        To get a specific page, use `NovaAct.pages` to list all pages,
        then fetch the intended page with its 0-starting index in `NovaAct.get_page(i)`.
        """
        return self.get_page()

    def get_page(self, index: int = -1) -> Page:
        """Get a particular playwright page by index or the currently actuating page if index == -1.

        Note: the order of these pages might not reflect their tab order in the window if they have been moved.

        Only available if the provided actuator is of type PlaywrightPageManagerBase.
        """
        if not self.started:
            raise ClientNotStarted("Run start() to start the client before accessing the Playwright Page.")

        if not isinstance(self._actuator, PlaywrightPageManagerBase):
            raise ValidationFailed(
                "Did you implement a non-playwright actuator? If so, you must get your own page object directly.\n"
                "If you are using playwright, ensure you are implementing PlaywrightPageManagerBase to get page access"
            )

        maybe_playwright_page = self._actuator.get_page(index)
        return maybe_playwright_page

    @property
    def pages(self) -> list[Page]:
        """Get the current playwright pages.

        Note: the order of these pages might not reflect their tab order in the window if they have been moved.

        Only available if the provided actuator is of type PlaywrightPageManagerBase.
        """
        if not self.started:
            raise ClientNotStarted("Run start() to start the client before accessing Playwright Pages.")

        if not isinstance(self._actuator, PlaywrightPageManagerBase):
            raise ValidationFailed(
                "Did you implement a non-playwright actuator? If so, you must get your own page object directly.\n"
                "If you are using playwright, ensure you are implementing PlaywrightPageManagerBase to get page access"
            )

        maybe_playwright_pages = self._actuator.pages
        return maybe_playwright_pages

    def go_to_url(self, url: str) -> None:
        """Navigates to the specified URL and waits for the page to settle."""

        validate_url(url, "go_to_url")

        if not self.started or self._session_id is None:
            raise ClientNotStarted("Run start() to start the client before running go_to_url")

        self.dispatcher.go_to_url(url)

    @property
    def dispatcher(self) -> ActDispatcher:
        """Get an ActDispatcher for actuation on the current page."""
        if not self.started:
            raise ClientNotStarted("Client must be started before accessing the dispatcher.")
        assert self._dispatcher is not None
        return self._dispatcher

    def _create_session_id(self) -> str:
        return str(uuid.uuid4())

    def get_session_id(self) -> str:
        """Get the session ID for the current client.

        Raises ClientNotStarted if the client has not been started.
        """
        if not self.started:
            raise ClientNotStarted("Client must be started before accessing the session ID.")
        return str(self._session_id)

    def get_logs_directory(self) -> str:
        """Get the logs directory for the current client."""
        if not self._logs_directory:
            raise ValueError("Logs directory is not set.")

        return self._logs_directory

    def _init_session_logs_directory(self, base_dir: str, session_id: str) -> str:
        _session_logs_directory: str = os.path.join(base_dir, session_id) if base_dir else ""
        if _session_logs_directory:
            try:
                os.mkdir(_session_logs_directory)
            except Exception as e:
                _LOGGER.error(
                    f"Failed to create directory: {_session_logs_directory} with Error: {e} "
                    f"of type {type(e).__name__}"
                )
        return _session_logs_directory

    def get_session_logs_directory(self) -> str:
        """
        Get the session logs directory path where run_info_compiler.py creates files.

        Returns:
            str: Path to the session logs directory

        Raises:
            ValueError: If logs directory is not set
        """
        if not self._session_logs_directory:
            raise ValueError("Session logs directory is not set.")

        return self._session_logs_directory

    def start(self) -> None:
        """Start the client."""
        if self.started:
            _LOGGER.warning("Attention: Client is already started; to start over, run stop().")
            return


        try:
            self._session_id = self._create_session_id()
            set_logging_session(self._session_id)
            self._session_logs_directory = self._init_session_logs_directory(self._logs_directory, self._session_id)

            actuator_type: Literal["custom", "playwright"]
            actuator_type = "playwright" if isinstance(self._actuator, DefaultNovaLocalBrowserActuator) else "custom"

            send_environment_telemetry(
                endpoint=self._backend_info.api_uri,
                nova_act_api_key=self._nova_act_api_key,
                session_id=self._session_id,
                actuator_type=actuator_type,
            )

            self._actuator.start(starting_page=self._starting_page, session_logs_directory=self._session_logs_directory)

            self._dispatcher.wait_for_page_to_settle()
            self._run_info_compiler = RunInfoCompiler(self._session_logs_directory)
            session_logs_str = f" logs dir {self._session_logs_directory}" if self._session_logs_directory else ""

            loggable_url = self._starting_page or self._cdp_endpoint_url
            _TRACE_LOGGER.info(f"\nstart session {self._session_id} on {loggable_url}{session_logs_str}\n")
            self._event_handler.send_event(
                type=EventType.LOG,
                log_level=LogType.INFO,
                data=f"start session {self._session_id} on {loggable_url}{session_logs_str}",
            )

        except Exception as e:
            _LOGGER.exception(f"Failed to start the actuator: {e}")
            self._stop()
            raise StartFailed(str(e)) from e

    def register_stop_hook(self, hook: StopHook) -> None:
        """Register a stop hook that will be called during stop().

        Parameters
        ----------
        hook : StopHook
            The stop hook to register. Must implement the StopHook protocol.
        """
        if hook in self._stop_hooks:
            raise ValueError(f"Stop hook {hook} is already registered.")
        self._stop_hooks.append(hook)

    def unregister_stop_hook(self, hook: StopHook) -> None:
        """Unregister a previously registered stop hook.

        Parameters
        ----------
        hook : StopHook
            The stop hook to unregister.
        """
        if hook not in self._stop_hooks:
            raise ValueError(f"Stop hook {hook} is not registered.")
        self._stop_hooks.remove(hook)

    def _execute_stop_hooks(self) -> None:
        """Call all registered stop hooks."""
        for hook in self._stop_hooks:
            try:
                hook.on_stop(self)
            except Exception as e:
                _LOGGER.error(f"Error in stop hook {hook}: {e}", exc_info=True)

    def _stop(self) -> None:
        try:
            self._execute_stop_hooks()
            self._dispatcher.cancel_prompt()
            self._actuator.stop()
            _TRACE_LOGGER.info(f"\nend session: {self._session_id}\n")
            self._event_handler.send_event(
                type=EventType.LOG, log_level=LogType.INFO, data=f"end session: {self._session_id}"
            )

            self._session_id = None
            set_logging_session(None)
        except Exception as e:
            raise StopFailed(str(e)) from e

    def stop(self) -> None:
        """Stop the client."""
        if not self.started:
            _LOGGER.warning("Attention: Client is already stopped.")
            return
        self._stop()


    def act(
        self,
        prompt: str,
        *,
        timeout: int | None = None,
        max_steps: int | None = None,
        schema: Mapping[str, JSONType] | None = None,
        model_temperature: float | None = None,
        model_top_k: int | None = None,
        model_seed: int | None = None,
        observation_delay_ms: int | None = None,
    ) -> ActResult:
        """Actuate on the web browser using natural language.

        Parameters
        ----------
        prompt: str
            The natural language task to actuate on the web browser.
        timeout: int, optional
            The timeout (in seconds) for the task to actuate.
        max_steps: int
            Configure the maximum number of steps (browser actuations) `act()` will take before giving up on the task.
            Use this to make sure the agent doesn't get stuck forever trying different paths. Default is 30.
        schema: Dict[str, Any] | None
            An optional jsonschema, which the output should to adhere to
        observation_delay_ms: int | None
            Additional delay in milliseconds before taking an observation of the page

        Returns
        -------
        ActResult

        Raises
        ------
        ActError
        ValidationFailed
        """
        if not self.started:
            raise ClientNotStarted("Run start() to start the client before calling act().")

        validate_timeout(timeout)
        validate_prompt(prompt)
        validate_step_limit(max_steps)

        if schema:
            validate_jsonschema_schema(schema)
            prompt = add_schema_to_prompt(prompt, schema)


        act = Act(
            prompt,
            session_id=str(self._session_id),
            timeout=timeout or float("inf"),
            max_steps=max_steps,
            model_temperature=model_temperature,
            model_top_k=model_top_k,
            model_seed=model_seed,
            observation_delay_ms=observation_delay_ms,
        )
        _TRACE_LOGGER.info(f'{get_session_id_prefix()}act("{prompt}")')

        self._event_handler.set_act(act)
        self._event_handler.send_event(type=EventType.LOG, log_level=LogType.INFO, data=f'act("{prompt}")')


        error: NovaActError | None = None
        result: ActResult | None = None

        try:
            result = self.dispatcher.dispatch(act)

            if schema:
                result = populate_json_schema_response(result, schema)
        except (ActError, AuthError) as e:
            error = e
            raise e
        except Exception as e:
            error = ActError(metadata=act.metadata, message=f"{type(e).__name__}: {e}")
            raise error from e
        finally:
            send_act_telemetry(
                endpoint=self._backend_info.api_uri,
                nova_act_api_key=self._nova_act_api_key,
                act=act,
                success=result,
                error=error,
            )

            if self._run_info_compiler:
                file_path = self._run_info_compiler.compile(act, result)
                _TRACE_LOGGER.info(f"\n{get_session_id_prefix()}** View your act run here: {file_path}\n")
                self._event_handler.send_event(
                    type=EventType.LOG,
                    log_level=LogType.INFO,
                    data=f"** View your act run here: {file_path}",
                )

        return result

