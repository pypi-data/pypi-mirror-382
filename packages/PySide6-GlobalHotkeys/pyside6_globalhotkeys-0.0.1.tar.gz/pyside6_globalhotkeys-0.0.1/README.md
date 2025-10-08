# Global Hotkeys for PySide6 Applications

Triggers the system's user interface for setting up global hotkeys for an application.

TODO: implement custom user interfaces for the systems that don't support that.

Provides Qt signals for the hotkey presses and releases.

Your application has to set the `QCoreApplication.applicationName` to an application that exists in the system (has a `*.desktop` file in `~/.local/share/applications`).

See an example application https://github.com/develOseven/demo-PySide6-GlobalHotkeys
