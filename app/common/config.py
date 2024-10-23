import sys

from qfluentwidgets import ConfigItem, QConfig, qconfig, BoolValidator


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    enableAutoAccept = ConfigItem('ChampSelectCard', 'EnableAutoAccept', True, BoolValidator())
    enableAutoSelect = ConfigItem('ChampSelectCard', 'EnableAutoSelect', False, BoolValidator())
    wantSelectChamps = ConfigItem('ChampSelectCard', 'WantSelectChamps', [157])
    wantBanChamps = ConfigItem('ChampSelectCard', 'WantBanChamps', [])

    enableAutoReconnect = ConfigItem('GameCard', 'EnableAutoReconnect', False, BoolValidator())
    enableAutoSearch = ConfigItem('GameCard', 'EnableAutoSearch', False, BoolValidator())


cfg = Config()
qconfig.load("app/resource/config/config.json", cfg)
