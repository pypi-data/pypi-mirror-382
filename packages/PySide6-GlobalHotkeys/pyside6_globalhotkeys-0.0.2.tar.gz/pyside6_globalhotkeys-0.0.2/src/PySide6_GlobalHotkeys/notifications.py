from PySide6 import QtCore
from PySide6.QtCore import QObject, Slot
from PySide6.QtDBus import (
    QDBusConnection,
    QDBusInterface,
    QDBusMessage,
    QDBusObjectPath,
)

from .appid import getAppId
from .dbuspaths import (
    BUS_NAME,
    HANDLE_TOKEN,
    OBJECT_PATH,
    REGISTRY_IFACE,
    SESSION_HANDLE_TOKEN,
    SHORTCUT_IFACE,
)


class Listener(QObject):
    hotkeyPressed = QtCore.Signal(str)
    hotkeyReleased = QtCore.Signal(str)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self.session: QDBusObjectPath | None = None

        self.bus = QDBusConnection.sessionBus()

        # Make it have the correct name in the UI.
        self.registry = QDBusInterface(BUS_NAME, OBJECT_PATH, REGISTRY_IFACE, self.bus)
        msg = self.registry.call("Register", getAppId(), {})
        if msg.type() == QDBusMessage.ErrorMessage:
            raise RuntimeError(msg.errorMessage())

        # Connect the hotkey signals.
        self.portal = QDBusInterface(BUS_NAME, OBJECT_PATH, SHORTCUT_IFACE, self.bus)
        options = {
            "handle_token": HANDLE_TOKEN,
            "session_handle_token": SESSION_HANDLE_TOKEN,
        }
        msg = self.portal.call("CreateSession", options)
        if msg.type() == QDBusMessage.ErrorMessage:
            raise RuntimeError(msg.errorMessage())

        self.portal.connect(
            QtCore.SIGNAL("Activated(QDBusObjectPath,QString,qulonglong,QVariantMap)"),
            self.onKeyActivated,
        )
        self.portal.connect(
            QtCore.SIGNAL(
                "Deactivated(QDBusObjectPath,QString,qulonglong,QVariantMap)"
            ),
            self.onKeyDeactivated,
        )

    @Slot("o", "s", "t", "a{sv}")
    def onKeyActivated(
        self,
        session_handle: QDBusObjectPath,
        shortcutId: str,
        timestamp: int,
        options: dict,
    ):
        self.hotkeyPressed.emit(shortcutId)

    @Slot("o", "s", "u", "a{sv}")
    def onKeyDeactivated(
        self,
        session_handle: QDBusObjectPath,
        shortcutId: str,
        timestamp: int,
        options: dict,
    ):
        self.hotkeyReleased.emit(shortcutId)
