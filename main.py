import asyncio
import sys

from PyQt6.QtGui import QIcon
from qasync import QApplication, QEventLoop

from app.view.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('LOL助手')

    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_future = event_loop.create_future()

    def resolve_app_close_future():
        if not app_close_future.done():
            app_close_future.set_result(None)

    app.lastWindowClosed.connect(resolve_app_close_future)
    app.aboutToQuit.connect(resolve_app_close_future)

    w = MainWindow()

    w.setWindowIcon(QIcon('logo.ico'))
    w.setWindowTitle('LOL助手')
    w.setFixedSize(800, 600)
    w.show()
    with event_loop:
        event_loop.run_until_complete(app_close_future)
