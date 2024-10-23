import asyncio
import random

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from qasync import asyncClose, asyncSlot
from qfluentwidgets import SubtitleLabel, BodyLabel, CardWidget, StrongBodyLabel, IndeterminateProgressRing

from app.common.config import cfg
from app.common.signals import signal_bus
from app.components.splash import SplashScreen
from app.lol.lcu import lcu
from app.lol.listener import LcuProcessListener
from app.view.setting_interface import SettingInterface
from app.view.summoner_interface import SummonerInterface


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # splash
        self.splash_screen = SplashScreen(self)
        self.splash_screen.setFixedSize(800, 600)
        self.show()

        self.main_box = QVBoxLayout(self)

        self.progressRing = IndeterminateProgressRing()

        self.game_status_widget = CardWidget()
        self.game_status_box = QHBoxLayout(self.game_status_widget)
        self.label = SubtitleLabel(text='游戏状态')
        self.label2 = StrongBodyLabel(text='None')

        self.summoner_card_widget = SummonerInterface()

        self.lcu_widget = QWidget()
        self.lcu_box = QHBoxLayout(self.lcu_widget)
        self.pid_label = BodyLabel(text='pid = ')
        self.port_label = BodyLabel(text='port = ')
        self.token_label = BodyLabel(text='token = ')

        self.setting_widget = SettingInterface()

        self.__init_widget()
        self.__init_layout()
        self.__connect_signal_to_slot()

        self.lcu_process_listener = LcuProcessListener(self)
        self.lcu_process_listener.start()

    def __init_widget(self):
        pass

    def __init_layout(self):
        self.lcu_box.addStretch(1)
        self.lcu_box.addWidget(self.pid_label)
        self.lcu_box.addWidget(self.port_label)
        self.lcu_box.addWidget(self.token_label)
        self.lcu_box.addStretch(1)

        self.game_status_box.addWidget(self.label)
        self.game_status_box.addWidget(self.label2)

        self.main_box.addWidget(self.game_status_widget)
        self.main_box.addWidget(self.summoner_card_widget)
        self.main_box.addWidget(self.lcu_widget)
        self.main_box.addWidget(self.setting_widget)

    def showLoadingPage(self, enable=True):
        self.game_status_widget.setVisible(not enable)
        self.summoner_card_widget.setVisible(not enable)
        self.lcu_widget.setVisible(not enable)
        self.setting_widget.setVisible(not enable)
        self.progressRing.setVisible(enable)

    def __connect_signal_to_slot(self):
        signal_bus.lcu_started.connect(self.__on_lcu_started)
        signal_bus.lcu_stopped.connect(self.__on_lcu_stopped)
        signal_bus.lcu_changed.connect(self.__on_lcu_changed)

        signal_bus.game_status_changed.connect(self.__on_game_status_changed)
        signal_bus.champ_select_changed.connect(self.__on_champ_select_changed)

        signal_bus.summoner_profile_changed.connect(self.__on_summoner_profile_changed)
        signal_bus.summoner_rp_changed.connect(self.__on_summoner_rp_changed)
        signal_bus.summoner_blue_changed.connect(self.__on_summoner_blue_changed)
        signal_bus.summoner_orange_changed.connect(self.__on_summoner_orange_changed)

    @asyncSlot(str)
    async def __on_game_status_changed(self, status: str):
        self.label2.setText(status)
        match status:
            case 'None':
                print('大厅')
            case 'Lobby':
                if cfg.enableAutoSearch.value:
                    await lcu.matchmaking_search()
            case 'Matchmaking':
                print('寻找对局')
            case 'ReadyCheck':
                if cfg.enableAutoAccept.value:
                    await lcu.matchmaking_accept()
            case 'ChampSelect':
                await self.__on_champ_select_begin()  # 第一次进入英雄选择阶段
            case 'GameStart':
                print('游戏开始')
            case 'InProgress':
                print('游戏中')
            case 'WaitingForStats':
                print('结算')
            case 'PreEndOfGame':
                print('点赞')
            case 'EndOfGame':
                print('游戏结束')
            case 'Reconnect':
                if cfg.enableAutoReconnect.value:
                    await lcu.reconnect()

    @asyncSlot(dict)
    async def __on_champ_select_changed(self, data):
        pass

        # selected_champ_id = await lcu.get_curr_select_champ()
        # if selected_champ_id > 0:
        #     return
        # actions = data['actions'][0]

        # action = [action for action in actions if action['actorCellId'] == data['localPlayerCellId']][0]
        # action_id = action['id']
        #
        # action_type = action['type']
        #
        # action_champ_id = action['championId']
        #
        # a = data['bans']['myTeamBans']
        # b = data['bans']['theirTeamBans']
        # bans = []
        # [bans.append(i) for i in a + b if i not in bans]
        #
        # match action_type:
        #     case 'pick':
        #         if action_champ_id > 0:
        #             return
        #         want_select_champs = cfg.autoSelectChamp.value
        #         if len(want_select_champs) == 0:
        #             return
        #         for champ_id in want_select_champs:
        #             if champ_id not in bans:
        #                 await lcu.select_champ(action_id, champ_id, cfg.enableAutoSelect.value)
        #                 break

    async def __on_champ_select_begin(self):
        """只做匹配pick"""
        champ_select_session = await lcu.get_champ_select_session()
        actions = champ_select_session['actions'][0]
        local_id = champ_select_session['localPlayerCellId']

        action = [action for action in actions if action['actorCellId'] == local_id][0]
        if action['type'] == 'pick':
            want_select_champs = cfg.wantSelectChamps.value
            if len(want_select_champs) == 0:
                return
            champ_id = random.choice(want_select_champs)
            await lcu.select_champ(action['id'], champ_id, cfg.enableAutoSelect.value)

    @asyncSlot(dict)
    async def __on_summoner_profile_changed(self, info):
        self.summoner_card_widget.update_info(info)

        self.pid_label.setText(f'pid = {lcu.pid}')
        self.port_label.setText(f'port = {lcu.port}')
        self.token_label.setText(f'token = {lcu.token}')

    @asyncSlot(int)
    async def __on_summoner_rp_changed(self, data):
        self.summoner_card_widget.update_rp(data)

    @asyncSlot(int)
    async def __on_summoner_blue_changed(self, data):
        self.summoner_card_widget.update_blue_essence(data)

    @asyncSlot(int)
    async def __on_summoner_orange_changed(self, data):
        self.summoner_card_widget.update_orange_essence(data)

    @asyncSlot(int)
    async def __on_lcu_started(self, pid):
        await lcu.start(pid, True)
        await self.__on_game_status_changed(await lcu.get_game_status())
        await self.__on_summoner_profile_changed(await lcu.get_curr_summoner())
        await self.__on_summoner_rp_changed(await lcu.get_summoner_rp())
        await self.__on_summoner_blue_changed(await lcu.get_summoner_blue_essence())
        await self.__on_summoner_orange_changed(await lcu.get_summoner_orange_essence())
        asyncio.create_task(self.setting_widget.auto_select_card.init_champs())

        self.splash_screen.hide()

    @asyncSlot()
    async def __on_lcu_stopped(self):
        self.splash_screen.show()
        try:
            await lcu.close()
        except:
            pass

    @asyncSlot(int)
    async def __on_lcu_changed(self, pid):
        await self.__on_lcu_stopped()
        self.lcu_process_listener.running_pid = pid
        await self.__on_lcu_started(pid)

    @asyncClose
    async def closeEvent(self, event):
        await self.__on_lcu_stopped()
        self.lcu_process_listener.terminate()
        return super().closeEvent(event)
