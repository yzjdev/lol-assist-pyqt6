from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    lcu_started = pyqtSignal(int)  # 客户端启动
    lcu_stopped = pyqtSignal()  # 客户端关闭
    lcu_changed = pyqtSignal(int)  # 客户端改变

    game_status_changed = pyqtSignal(str)  # 游戏状态
    summoner_profile_changed = pyqtSignal(dict)  # 玩家信息
    summoner_rp_changed = pyqtSignal(int)  # 点券
    summoner_blue_changed = pyqtSignal(int)  # 蓝色精粹
    summoner_orange_changed = pyqtSignal(int)  # 橙色精粹

    champ_select_changed = pyqtSignal(dict)


signal_bus = SignalBus()
