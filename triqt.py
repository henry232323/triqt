"""
A simple way to use trio with your Python Qt application.

To begin running the app
```py
>>> app = App()
>>> trio.run(task, instruments=[triqt.Instrument(app)])
```
To invoke an async function from Qt using a Signal
```py
>>> triqt.async_signal(func, args)
```
"""

import os
import logging
import trio
from collections import deque

__all__ = ["initialize"]

import importlib

logger = logging.getLogger('triqt')

########### BEGIN IMPLEMENTATION DETECTION & IMPORT ###########
try:
    QtModuleName = os.environ['QUAMASH_QTIMPL']
except KeyError:
    QtModule = None
else:
    logger.info('Forcing use of {} as Qt Implementation'.format(QtModuleName))
    QtModule = importlib.import_module(QtModuleName)

if not QtModule:
    for QtModuleName in ('PyQt5', 'PyQt4', 'PySide'):
        try:
            QtModule = importlib.import_module(QtModuleName)
        except ImportError:
            continue
        else:
            break
    else:
        raise ImportError('No Qt implementations found')

logger.info('Using Qt Implementation: {}'.format(QtModuleName))

QtCore = importlib.import_module(QtModuleName + '.QtCore', package=QtModuleName)
QtGui = importlib.import_module(QtModuleName + '.QtGui', package=QtModuleName)
if QtModuleName == 'PyQt5':
    from PyQt5 import QtWidgets

    QApplication = QtWidgets.QApplication
else:
    QApplication = QtGui.QApplication

########### END IMPLEMENTATION DETECTION & IMPORT ###########
    

def _make_signaller(qtimpl_qtcore, *args):
    """Implementation independent Signal object"""
    class Signaller(qtimpl_qtcore.QObject):
        try:
            signal = qtimpl_qtcore.Signal(*args)
        except AttributeError:
            signal = qtimpl_qtcore.pyqtSignal(*args)

    return Signaller()


async_signaller = _make_signaller(QtCore, object, tuple)
async_signal = async_signaller.signal


class Instrument(trio.abc.Instrument):
    def __init__(self, app=None):
        self._app = app or QApplication.instance()
        if self._app is None:
            raise RuntimeError('No QApplication has been instantiated')

        self._tasks = deque()

        async_signal.connect(lambda callback, args: self._tasks.append((callback, *args)))

    def before_run(self):
        trio.hazmat.spawn_system_task(self._run_ui)

    async def _run_ui(self):
        try:
            async with trio.open_nursery() as nursery:
                while True:
                    if self._tasks:
                        nursery.start_soon(*self._tasks.popleft())
                    await trio.sleep(0)
                    self._app.processEvents()
        finally:
            self._app.exit()
