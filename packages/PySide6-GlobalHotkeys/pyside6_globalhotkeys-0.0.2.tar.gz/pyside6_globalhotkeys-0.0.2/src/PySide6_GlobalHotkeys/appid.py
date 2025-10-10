import hashlib
import os
import pathlib

from PySide6.QtCore import QCoreApplication


def getAppId() -> str:
    """Get the appId that is the name of the *.desktop file of the application."""

    applicationName = QCoreApplication.applicationName()

    appImage = os.environ.get("APPIMAGE")
    if appImage is not None:
        # Running as an AppImage. See libappimage for the details.
        hash = hashlib.md5(pathlib.Path(appImage).as_uri().encode()).hexdigest()
        return f"appimagekit_{hash}-{applicationName}"

    return applicationName
