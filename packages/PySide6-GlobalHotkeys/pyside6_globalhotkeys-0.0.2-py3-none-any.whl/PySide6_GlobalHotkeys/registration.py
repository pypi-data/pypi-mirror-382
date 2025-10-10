import asyncio
import random
import string
from typing import Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
    dbus_property_async,
    dbus_signal_async,
)

from .appid import getAppId
from .dbuspaths import (
    BUS_NAME,
    HANDLE_TOKEN,
    OBJECT_PATH,
    REGISTRY_IFACE,
    REQUEST_IFACE,
    SESSION_HANDLE_TOKEN,
    SHORTCUT_IFACE,
)

# Can't use different loops for the successve calls.
# Unable to call a dbus method twice with asyncio.run
# https://github.com/python-sdbus/python-sdbus/issues/69
loop: asyncio.AbstractEventLoop | None = None

# Can't register the app ID twice as per XDG docs.
# Registering can only done at most once; any subsequent call will result in an error.
appIdRegistered = False


class Registry(
    DbusInterfaceCommonAsync,
    interface_name=REGISTRY_IFACE,
):
    # --- Methods ---

    @dbus_method_async("sa{sv}", "")
    async def Register(self, app_id: str, options: dict):
        pass

    # --- Properties ---

    @dbus_property_async("u")
    def version(self) -> int:
        return 0


class GlobalShortcuts(
    DbusInterfaceCommonAsync,
    interface_name=SHORTCUT_IFACE,
):

    # --- Methods ---

    @dbus_method_async("a{sv}", "o")
    async def CreateSession(self, options: dict):
        """
        CreateSession(a{sv} options) → o handle
        """
        pass

    @dbus_method_async("oa(sa{sv})sa{sv}", "o")
    async def BindShortcuts(
        self, session_handle: str, shortcuts: list, parent_window: str, options: dict
    ):
        """
        BindShortcuts(o session_handle, a(sa{sv}) shortcuts, s parent_window, a{sv} options) → o request_handle
        """
        pass

    @dbus_method_async("oa{sv}", "o")
    async def ListShortcuts(self, session_handle: str, options: dict):
        """
        ListShortcuts(o session_handle, a{sv} options) → o request_handle
        """
        pass

    # --- Signals ---

    @dbus_signal_async("osta{sv}")
    def Activated(
        self, session_handle: str, shortcut_id: str, timestamp: int, options: dict
    ):
        """
        Activated(o session_handle, s shortcut_id, t timestamp, a{sv} options)
        """
        pass

    @dbus_signal_async("osta{sv}")
    def Deactivated(
        self, session_handle: str, shortcut_id: str, timestamp: int, options: dict
    ):
        """
        Deactivated(o session_handle, s shortcut_id, t timestamp, a{sv} options)
        """
        pass

    @dbus_signal_async("oa(sa{sv})")
    def ShortcutsChanged(self, session_handle: str, shortcuts: list):
        """
        ShortcutsChanged(o session_handle, a(sa{sv}) shortcuts)
        """
        pass

    # --- Properties ---

    @dbus_property_async(property_signature="u", property_name="version")
    def version(self) -> int:
        return 0


class Request(
    DbusInterfaceCommonAsync,
    interface_name=REQUEST_IFACE,
):
    # --- Methods ---

    @dbus_method_async("", "")
    async def Close(self):
        pass

    # --- Signals ---

    @dbus_signal_async("ua{sv}")
    def Response(self, response: int, results: dict):
        pass


def hotkeysToSdBusHotkeys(
    hotkeys: list[Tuple[str, dict[str, str]]],
) -> list[Tuple[str, dict[str, Tuple[str, str]]]]:
    """Convert some string values to the protocol-compatible Variant type."""
    sdBusHotkeys = []
    for binding, options in hotkeys:
        convertedOptions = {key: ("s", value) for key, value in options.items()}
        sdBusHotkeys.append((binding, convertedOptions))
    return sdBusHotkeys


async def bindHotkeysCoro(hotkeys: list[Tuple[str, dict[str, str]]]) -> None:
    global appIdRegistered
    if not appIdRegistered:
        # Make it have the correct name in the UI.
        registry = Registry.new_proxy(BUS_NAME, OBJECT_PATH)
        await registry.Register(getAppId(), {})
        appIdRegistered = True

    # Interact with the global shortcuts configurator UI of the system.
    globalShortcuts = GlobalShortcuts.new_proxy(BUS_NAME, OBJECT_PATH)
    randomSuffix = "_" + "".join(random.choices(string.ascii_letters, k=8))
    options = {
        "handle_token": ("s", HANDLE_TOKEN),
        "session_handle_token": ("s", SESSION_HANDLE_TOKEN + randomSuffix),
    }
    request = Request.new_proxy(BUS_NAME, await globalShortcuts.CreateSession(options))

    async def onSessionCreated():
        async for response in request.Response:
            sessionHandle = response[1]["session_handle"][1]
            break

        # Open the global shortcuts configurator UI of the system.
        await globalShortcuts.BindShortcuts(
            sessionHandle,
            hotkeysToSdBusHotkeys(hotkeys),
            "",
            {},
        )

    await asyncio.get_event_loop().create_task(onSessionCreated())


def bindHotkeys(hotkeys: list[Tuple[str, dict[str, str]]]):
    global loop
    if loop is None:
        loop = asyncio.new_event_loop()
    loop.run_until_complete(loop.create_task(bindHotkeysCoro(hotkeys)))
