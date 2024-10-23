from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal, QSize, QEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy, QFrame
from qasync import asyncSlot
from qfluentwidgets import SettingCardGroup, SmoothScrollArea, SwitchSettingCard, ExpandGroupSettingCard, FluentIcon, \
    PushButton, SwitchButton, IndicatorPosition, PushSettingCard, LineEdit, TransparentToolButton

from app.common.config import cfg
from app.common.signals import signal_bus
from app.components.message_box import ChampSelectMessageBox
from app.components.round_widget import RoundIcon
from app.lol.lcu import lcu


class SettingInterface(SmoothScrollArea):

    def __init__(self):
        super().__init__()

        self.setting_widget = QWidget()
        self.setting_box = QVBoxLayout(self.setting_widget)

        self.champ_select_group = SettingCardGroup('英雄选择')
        self.auto_accept_card = AutoAcceptCard()
        self.auto_select_card = AutoSelectCard()
        self.auto_ban_card = AutoBanCard()

        self.game_group = SettingCardGroup('游戏')
        self.back_hall_card = BackHallCard()
        self.auto_search_card = AutoSearchCard()
        self.auto_reconnect_card = AutoReconnectCard()
        self.practice_card = PracticeCard()
        self.play_again_card = PlayAgainCard()

        self.client_group = SettingCardGroup('客户端')

        self.restart_client_card = RestartClientCard()

        """add layout"""

        self.client_group.addSettingCard(self.restart_client_card)

        self.game_group.addSettingCard(self.back_hall_card)
        self.game_group.addSettingCard(self.auto_search_card)
        self.game_group.addSettingCard(self.auto_reconnect_card)
        self.game_group.addSettingCard(self.practice_card)
        self.game_group.addSettingCard(self.play_again_card)

        self.champ_select_group.addSettingCard(self.auto_accept_card)
        self.champ_select_group.addSettingCard(self.auto_select_card)
        self.champ_select_group.addSettingCard(self.auto_ban_card)

        self.setting_box.setContentsMargins(0, 0, 0, 0)
        self.setting_box.addWidget(self.champ_select_group)
        self.setting_box.addWidget(self.game_group)
        self.setting_box.addWidget(self.client_group)
        self.setting_box.addStretch(1)

        self.setWidget(self.setting_widget)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()


class AutoAcceptCard(SwitchSettingCard):
    def __init__(self):
        super().__init__(
            icon=FluentIcon.TRANSPARENT,
            title="自动接受对局",
            content="排队时寻找到对局自动接受，无需值守",
            configItem=cfg.enableAutoAccept
        )
        init_switch_button_text(self.switchButton)
        self.checkedChanged.connect(self.__on_checked_changed)

    @asyncSlot(bool)
    async def __on_checked_changed(self, is_checked: bool):
        if is_checked:
            self.switchButton.setOnText('开')
            signal_bus.game_status_changed.emit(await lcu.get_game_status())
        else:
            self.switchButton.setOffText('关')


class AutoSelectCard(ExpandGroupSettingCard):
    def __init__(self):
        super().__init__(
            icon=FluentIcon.TRANSPARENT,
            title="自动选择英雄",
            content="随机亮起所选英雄，开启锁定则自动pick"
        )

        self.status_label = QLabel(text='已启用' if cfg.enableAutoSelect.value else '未启用')
        self.select_widget = QWidget()
        self.select_layout = QHBoxLayout(self.select_widget)
        self.title_label = QLabel(text='默认选择英雄：')
        self.champ_line_edit = ChampionsCard()
        self.select_btn = PushButton(text='选择')
        self.lock_widget = QWidget()
        self.lock_layout = QHBoxLayout(self.lock_widget)
        self.lock_label = QLabel(text='自动锁定英雄')
        self.lock_switch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)
        self.__init_widget()
        self.__init_layout()

    def __init_widget(self):
        init_switch_button_text(self.lock_switch)

        self.lock_switch.setChecked(cfg.enableAutoSelect.value)

        is_not_want_select = len(cfg.wantSelectChamps.value) == 0
        self.status_label.setText('未启用' if is_not_want_select else '已启用')
        self.lock_switch.setEnabled(False if is_not_want_select else True)

        self.select_btn.clicked.connect(self.on_select_btn_clicked)
        self.lock_switch.checkedChanged.connect(self.__on_checked_changed)

    def __init_layout(self):
        self.lock_layout.addWidget(self.lock_label)
        self.lock_layout.addWidget(self.lock_switch)

        self.select_layout.addWidget(self.title_label, Qt.AlignmentFlag.AlignLeft)
        self.select_layout.addWidget(self.champ_line_edit, 0, Qt.AlignmentFlag.AlignRight)
        self.select_layout.addWidget(self.select_btn, 0, Qt.AlignmentFlag.AlignRight)

        self.addWidget(self.status_label)
        self.addGroupWidget(self.select_widget)
        self.addGroupWidget(self.lock_widget)

    @pyqtSlot(bool)
    def __on_checked_changed(self, is_checked: bool):
        # self.status_label.setText('已启用' if is_checked else '未启用')
        cfg.set(cfg.enableAutoSelect, is_checked)

    async def init_champs(self, champs: dict = None):
        if champs:
            self.champs = champs
        else:
            self.champs = await lcu.get_champions()
        self.champ_line_edit.clearRequested.connect(lambda: self.on_champ_selected_changed([]))
        selected = cfg.wantSelectChamps.value
        icons = [[champ for champ in self.champs if champ['id'] == id][0]['icon'] for id in selected]
        self.champ_line_edit.updateChampions(icons)

    @asyncSlot()
    async def on_select_btn_clicked(self):
        selected = cfg.wantSelectChamps.value
        box = ChampSelectMessageBox(self.champs, selected, self.window())
        box.completed.connect(self.on_champ_selected_changed)
        box.exec()

    @pyqtSlot(list)
    def on_champ_selected_changed(self, selected):
        cfg.set(cfg.wantSelectChamps, selected)
        icons = [[champ for champ in self.champs if champ['id'] == id][0]['icon'] for id in selected]
        self.champ_line_edit.updateChampions(icons)
        self.lock_switch.setEnabled(False if len(selected) == 0 else True)
        self.status_label.setText('未启用' if len(selected) == 0 else '已启用')


class AutoBanCard(ExpandGroupSettingCard):
    def __init__(self):
        super().__init__(
            icon=FluentIcon.TRANSPARENT,
            title="自动禁用英雄",
            content="随机亮起所选英雄，开启锁定则自动ban",

        )
        self.setEnabled(False)

        self.status_label = QLabel()
        self.status_label.setText('未启用')

        self.select_widget = QWidget()
        self.select_layout = QHBoxLayout(self.select_widget)
        self.title_label = QLabel(text='默认禁用英雄：')
        self.champ_line_edit = LineEdit()
        self.champ_line_edit.setClearButtonEnabled(True)
        self.champ_line_edit.setMinimumWidth(250)
        self.select_btn = PushButton(text='选择')

        self.lock_widget = QWidget()
        self.lock_layout = QHBoxLayout(self.lock_widget)
        self.lock_label = QLabel(text='自动禁用英雄')
        self.lock_switch = SwitchButton(indicatorPos=IndicatorPosition.RIGHT)

        self.lock_layout.addWidget(self.lock_label)
        self.lock_layout.addWidget(self.lock_switch)

        self.select_layout.addWidget(self.title_label, Qt.AlignmentFlag.AlignLeft)
        self.select_layout.addWidget(self.champ_line_edit, 0, Qt.AlignmentFlag.AlignRight)
        self.select_layout.addWidget(self.select_btn, 0, Qt.AlignmentFlag.AlignRight)

        self.addWidget(self.status_label)
        self.addGroupWidget(self.select_widget)
        self.addGroupWidget(self.lock_widget)


class BackHallCard(PushSettingCard):
    def __init__(self):
        super().__init__(text='返回',
                         icon=FluentIcon.TRANSPARENT,
                         title="返回大厅",
                         content="点击返回大厅")
        self.clicked.connect(self.__btn_clicked)

    @asyncSlot()
    async def __btn_clicked(self):
        await lcu.delete_lobby()


class AutoSearchCard(SwitchSettingCard):
    def __init__(self):
        super().__init__(
            icon=FluentIcon.TRANSPARENT,
            title="自动寻找对局",
            content="开启则自动寻找对局，关闭则取消寻找",
            configItem=cfg.enableAutoSearch
        )
        init_switch_button_text(self.switchButton)
        self.checkedChanged.connect(self.__checked_changed)

    @asyncSlot(bool)
    async def __checked_changed(self, is_checked: bool):
        if is_checked:
            self.switchButton.setOnText('开')
            signal_bus.game_status_changed.emit(await lcu.get_game_status())
        else:

            self.switchButton.setOffText('关')
            await lcu.matchmaking_search_cancel()


class AutoReconnectCard(SwitchSettingCard):
    def __init__(self):
        super().__init__(
            icon=FluentIcon.TRANSPARENT,
            title="自动重连",
            content="开启则中途退出游戏自动重连",
            configItem=cfg.enableAutoReconnect
        )
        init_switch_button_text(self.switchButton)
        self.checkedChanged.connect(self.__checked_changed)

    @asyncSlot(bool)
    async def __checked_changed(self, is_checked: bool):
        if is_checked:
            self.switchButton.setOnText('开')
            signal_bus.game_status_changed.emit(await lcu.get_game_status())
        else:
            self.switchButton.setOffText('关')


class PracticeCard(PushSettingCard):
    def __init__(self):
        super().__init__(
            text='创建',
            icon=FluentIcon.TRANSPARENT,
            title="创建 5v5 训练模式",
            content="自动添加随机机器人",
        )
        self.clicked.connect(self.__btn_clicked)

    @asyncSlot()
    async def __btn_clicked(self):
        await lcu.create_custom_lobby()
        await lcu.add_blue_bots()
        await lcu.add_red_bots()


class PlayAgainCard(PushSettingCard):
    def __init__(self):
        super().__init__(
            text='确定',
            icon=FluentIcon.TRANSPARENT,
            title="再玩一局",
            content="跳过结算时无限加载",
        )

        self.clicked.connect(self.__play_again)

    @asyncSlot()
    async def __play_again(self):
        await lcu.play_again()


class RestartClientCard(PushSettingCard):
    def __init__(self):
        super().__init__(
            text='重启',
            icon=FluentIcon.TRANSPARENT,
            title="重启客户端",
            content="重启客户端而不需要排队")

        self.clicked.connect(self.__restart)

    @asyncSlot()
    async def __restart(self):
        await lcu.restart_client()


class ChampionsCard(QFrame):
    clearRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(2, 0, 4, 0)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.iconLayout = QHBoxLayout()
        self.iconLayout.setContentsMargins(6, 6, 0, 6)
        self.clearButton = TransparentToolButton(FluentIcon.CLOSE)
        self.clearButton.setFixedSize(28, 28)
        self.clearButton.setIconSize(QSize(15, 15))
        self.clearButton.setVisible(False)
        self.clearButton.clicked.connect(self.clearRequested)

        self.hBoxLayout.addLayout(self.iconLayout)
        self.hBoxLayout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self.hBoxLayout.addWidget(self.clearButton, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.setFixedWidth(250)
        self.setFixedHeight(42)
        self.setStyleSheet("""
                ChampionsCard {
                    border: 1px solid rgba(0, 0, 0, 0.095);
                    border-radius: 6px;
                    background-color: rgba(245, 245, 245, 0.667);
                }""")

    def updateChampions(self, champions):
        self.clear()

        for icon in champions:
            icon = RoundIcon(icon, 28, 2, 2)
            self.iconLayout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignVCenter)

    def clear(self):
        for i in reversed(range(self.iconLayout.count())):
            item = self.iconLayout.itemAt(i)
            self.iconLayout.removeItem(item)

            if item.widget():
                item.widget().deleteLater()

    def enterEvent(self, a0: QEvent) -> None:
        self.clearButton.setVisible(True)
        return super().enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        self.clearButton.setVisible(False)
        return super().leaveEvent(a0)


def init_switch_button_text(switch: SwitchButton):
    switch.setOnText('开')
    switch.setOffText('关')
