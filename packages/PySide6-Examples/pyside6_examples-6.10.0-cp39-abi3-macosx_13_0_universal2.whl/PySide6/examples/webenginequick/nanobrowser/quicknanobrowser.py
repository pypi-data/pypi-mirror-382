# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 WebEngine QtQuick 2 Example"""

import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from PySide6.QtCore import (QCoreApplication, QFileInfo, QMetaObject, QObject,
                            QUrl, Slot, Q_ARG)
from PySide6.QtQml import QQmlApplicationEngine, QmlElement, QmlSingleton
from PySide6.QtGui import QGuiApplication
from PySide6.QtWebEngineQuick import QtWebEngineQuick

import rc_resources  # noqa: F401


# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "BrowserUtils"
QML_IMPORT_MAJOR_VERSION = 1


def url_from_user_input(user_input):
    file_info = QFileInfo(user_input)
    if file_info.exists():
        return QUrl.fromLocalFile(file_info.absoluteFilePath())
    return QUrl.fromUserInput(user_input)


@QmlElement
@QmlSingleton
class Utils(QObject):

    @Slot(str, result=QUrl)
    def fromUserInput(self, user_input):
        return url_from_user_input(user_input)


if __name__ == '__main__':
    QCoreApplication.setApplicationName("Quick Nano Browser")
    QCoreApplication.setOrganizationName("QtProject")

    QtWebEngineQuick.initialize()

    argument_parser = ArgumentParser(description="Quick Nano Browser",
                                     formatter_class=RawTextHelpFormatter)
    argument_parser.add_argument("--single-process", "-s", action="store_true",
                                 help="Run in single process mode (trouble shooting)")
    argument_parser.add_argument("url", help="The URL to open",
                                 nargs='?', type=str)
    options = argument_parser.parse_args()

    url = url_from_user_input(options.url) if options.url else QUrl("chrome://qt")

    app_args = sys.argv
    if options.single_process:
        app_args.extend(["--webEngineArgs", "--single-process"])
    app = QGuiApplication(app_args)
    engine = QQmlApplicationEngine()
    qml_file = os.fspath(Path(__file__).resolve().parent / 'ApplicationRoot.qml')
    engine.load(QUrl.fromLocalFile(qml_file))
    if not engine.rootObjects():
        sys.exit(-1)

    QMetaObject.invokeMethod(engine.rootObjects()[0], "load", Q_ARG("QVariant", url))

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)
