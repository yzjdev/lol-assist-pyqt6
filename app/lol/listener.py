from PyQt6.QtCore import QThread

from app.common.signals import signal_bus
from app.common.utils import get_lcu_pids, is_lcu_process_exist


class LcuProcessListener(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.running_pid = 0
        self.daemon = True

    def run(self):
        while True:
            pids = get_lcu_pids()

            match len(pids):
                case 0:
                    if self.running_pid and not is_lcu_process_exist():
                        self.running_pid = 0
                        signal_bus.lcu_stopped.emit()
                case 1 | 2:
                    """
                    一个客户端
                    1. running_pid等于0 则客户端首次启动
                    2. running_pid不等于0 且 与pid不相等 则客户端发生改变
                    
                    两个客户端(wegame双开时 旧客户端未关闭 此时存在两个客户端 pids[1]为正常运行的lcu的pid)
                    1. 助手未打开时双开客户端 此时running_pid等于0  回调started
                    2. 助手打开时双开客户端 此时running_pid不等于0 回调changed
                    """
                    pid = pids[0] if len(pids) == 1 else pids[1]
                    if self.running_pid == 0:
                        self.running_pid = pid
                        signal_bus.lcu_started.emit(pid)
                    elif self.running_pid != pid:
                        self.running_pid = pid
                        signal_bus.lcu_changed.emit(pid)

            self.msleep(1500)
