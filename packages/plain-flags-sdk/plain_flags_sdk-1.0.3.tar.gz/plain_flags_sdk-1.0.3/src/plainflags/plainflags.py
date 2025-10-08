import aiohttp
import asyncio
from .flagstate import FlagState
from .constrainer import is_turned_on_in_context


class PlainFlagsConfig():
    def __init__(self, service_url: str, api_key: str,
                 timeout_ms: int, poll_interval_ms: int = 0):
        """
        Params:
        service_url: str - the URL of your PlainFlags flag states service.
        api_key: str - the shared API key between your software and your PlainFlags states service.
        timeout_ms: int - the timeout for requests in milliseconds.
        poll_interval_ms: int - the interval for polling the service in milliseconds. Set to 0 to disable polling.
        """
        self.service_url = service_url
        self.api_key = api_key
        self.timeout_ms = timeout_ms
        self.poll_interval_ms = poll_interval_ms


class PlainFlags():
    def __init__(self, config: PlainFlagsConfig, infoFunc=print, errorFunc=print):
        """
        Params:
        config: PlainFlagsConfig - a configuration object for the PlainFlags service.
        infoFunc: callable - a function to log informational messages. Pass None to mute.
        errorFunc: callable - a function to log error messages. Pass None to mute.

        Example usage:
        ```python
        config = PlainFlagsConfig(
            service_url="https://plainflags.mysite.com",
            api_key="your_api_key",
            timeout_ms=5000,
            poll_interval_ms=10000
        )
        flags = PlainFlags(config, infoFunc=logging.info, errorFunc=logging.error)
        ```
        """
        self.__config = config
        self.__infoFunc = infoFunc
        self.__errorFunc = errorFunc

        self.__flag_states = {}
        self.__ispolling = False
        self.__polling_task = None

    async def init(self):
        """
        Initializes the PlainFlags instance by fetching the initial state of flags.
        Call this method before using the `is_on` method to ensure flags are loaded.
        If polling is enabled, it starts polling the states service for feature state.
        """
        if self.__config.poll_interval_ms <= 0:
            await self.update_state()
            return

        # Start polling in a background task and store the reference
        self.__polling_task = asyncio.create_task(self.__start_polling())

        # Ensure the task doesn't get garbage collected by adding a done callback
        self.__polling_task.add_done_callback(
            lambda t: t.exception() if t.done() and not t.cancelled() else None)

    async def __start_polling(self):
        """
        Private method that starts a polling loop to periodically update flag states.
        This method is called by init() when polling is enabled.
        """
        if self.__ispolling:
            return

        self.__ispolling = True
        self.__info(
            f"Starting polling with interval {self.__config.poll_interval_ms}ms")

        try:
            while self.__ispolling:
                try:
                    await self.update_state()
                except Exception as e:
                    self.__error(f"Error updating state during polling: {e}")
                    # Continue polling even if an update fails

                await asyncio.sleep(self.__config.poll_interval_ms / 1000.0)
        except asyncio.CancelledError:
            # Handle task cancellation gracefully
            self.__info("Polling cancelled")
            raise
        except Exception as e:
            self.__error(f"Fatal error in polling loop: {e}")
        finally:
            self.__ispolling = False
            self.__info("Polling stopped")

    async def stop_updates(self):
        """
        Stops the polling of the PlainFlags state service for feature states.
        This method should be called when you no longer need to poll for updates,
        such as when shutting down your application.
        """
        self.__ispolling = False
        if self.__polling_task and not self.__polling_task.done():
            self.__polling_task.cancel()
            try:
                await self.__polling_task
            except asyncio.CancelledError:
                pass
        self.__polling_task = None

    async def update_state(self):
        """
        Fetches the latest feature flag states from the PlainFlags service.
        This method is called automatically if polling is enabled, or can be called manually
        to refresh the flag states.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.__config.service_url}/api/sdk",
                    headers={"x-api-key": self.__config.api_key},
                    timeout=aiohttp.ClientTimeout(
                        self.__config.timeout_ms / 1000.0)
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        self.__flag_states = dict((key, FlagState(value))
                                                  for key, value in data.items())
                        self.__info("Feature flags updated")
                    else:
                        raise Exception(
                            f"Failed to fetch flags: {response.status}")
        except Exception as e:
            self.__error(f"Error fetching flags: {e}")

    def is_on(self, flag_name: str, default: bool = False,
              context: dict[str, str] | None = None) -> bool:
        """
        Checks if a feature flag is turned on in the given context.
        Params:
        flag_name: str - the name of the feature flag to check.
        default: bool - the default value to return if the flag is not found.
        context: dict[str, str] | None - the context in which to check the flag state,
            such as user identity or other constraints. When you pass a context,
            a flag is only on if it is activated in the dashboard, and the context matches the constraints.
            If None, the state is the same as you set in the PlainFlags dashboard for all contexts.

        Returns:
        bool - True if the flag is turned on in the given context, False otherwise.

        Example usage:
        ```python
        is_feature_enabled = flags.is_on("new_feature", default=False, context={"user_id": get_user(), "region_id": get_region()})
        ```
        """
        if not flag_name in self.__flag_states:
            return default

        return is_turned_on_in_context(self.__flag_states[flag_name], context)

    def set_info_function(self, infoFunc):
        """
        Sets the function to be used for logging informational messages.
        Pass None to mute informational messages.

        Params:
        infoFunc: callable - a function that takes a string message as its first argument.
        """
        self.__infoFunc = infoFunc

    def set_error_function(self, errorFunc):
        """
        Sets the function to be used for logging error messages.
        Pass None to mute error messages.

        Params:
        errorFunc: callable - a function that takes a string message as its first argument.
        """
        self.__errorFunc = errorFunc

    def current_states(self) -> dict[str, FlagState]:
        """
        Returns the current states of all feature flags as a dictionary.
        The keys are the flag names and the values are FlagState objects.

        Returns:
        dict[str, FlagState] - a dictionary of current feature flag states.
        """
        return self.__flag_states

    def set_states(self, states: dict[str, FlagState]):
        """
        Sets the current states of all feature flags.
        This method can be used for testing or to manually set flag states.

        Params:
        states: dict[str, FlagState] - a dictionary of feature flag states to set.
        """
        self.__flag_states = states

    def __info(self, message: str, *args, **kwargs):
        if self.__infoFunc:
            self.__infoFunc(message, *args, **kwargs)

    def __error(self, message: str, *args, **kwargs):
        if self.__errorFunc:
            self.__errorFunc(message, *args, **kwargs)
