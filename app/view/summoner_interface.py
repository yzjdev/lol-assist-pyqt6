import pyperclip
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import ElevatedCardWidget, SubtitleLabel, BodyLabel, ToolButton, FluentIcon

from app.components.avatar_widget import AvatarWidget


class SummonerInterface(ElevatedCardWidget):
    def __init__(self):
        super().__init__()
        self.summoner_box = QHBoxLayout(self)

        self.icon_widget = AvatarWidget()

        self.name_wallet_box = QVBoxLayout()
        self.name_box = QHBoxLayout()
        self.name_label = SubtitleLabel(text='')
        self.tag_label = BodyLabel(text='')
        self.name_copy_btn = ToolButton(FluentIcon.COPY)

        self.wallet_box = QHBoxLayout()

        self.rp_label = SubtitleLabel(text='')
        self.blue_label = SubtitleLabel(text='')
        self.orange_label = SubtitleLabel(text='')

        self.wallet_box.addWidget(SubtitleLabel(text='点券: '))
        self.wallet_box.addWidget(self.rp_label)
        self.wallet_box.addSpacing(20)
        self.wallet_box.addWidget(SubtitleLabel(text='蓝色精粹: '))
        self.wallet_box.addWidget(self.blue_label)
        self.wallet_box.addSpacing(20)
        self.wallet_box.addWidget(SubtitleLabel(text='橙色精粹: '))
        self.wallet_box.addWidget(self.orange_label)
        self.wallet_box.addStretch(1)
        self.wallet_box.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.name_box.addWidget(self.name_label)
        self.name_box.addWidget(self.tag_label)
        self.name_box.addWidget(self.name_copy_btn)
        self.name_box.addStretch(1)
        self.name_box.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.name_wallet_box.addLayout(self.name_box)
        self.name_wallet_box.addLayout(self.wallet_box)

        self.summoner_box.addStretch(1)
        self.summoner_box.addWidget(self.icon_widget)
        self.summoner_box.addSpacing(20)
        self.summoner_box.addLayout(self.name_wallet_box)
        self.summoner_box.addStretch(1)

        self.name_copy_btn.clicked.connect(lambda: pyperclip.copy(f'{self.name_label.text()}{self.tag_label.text()}'))

    def update_info(self, info):
        self.icon_widget.update_icon(info['icon'], info['xp'], info['level'])
        self.name_label.setText(info['name'])
        self.tag_label.setText(f'#{info['tag']}')

    def update_rp(self, rp):
        self.rp_label.setText(str(rp))

    def update_blue_essence(self, blue_essence):
        self.blue_label.setText(str(blue_essence))

    def update_orange_essence(self, orange_essence):
        self.orange_label.setText(str(orange_essence))
