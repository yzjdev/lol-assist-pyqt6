from PyQt6.QtCore import pyqtSignal
from qfluentwidgets import MessageBoxBase, TitleLabel, PrimaryPushButton, PushButton

from app.components.champ_select_widget import ChampSelectWidget


class ChampSelectMessageBox(MessageBoxBase):
    completed = pyqtSignal(list)

    def __init__(self, champs, selected, parent=None):
        super().__init__(parent)

        self.title_label = TitleLabel(text='选择英雄')
        self.champ_select_widget = ChampSelectWidget(champs, selected)
        self.yes_btn = PrimaryPushButton('确定', self.buttonGroup)
        self.cancel_btn = PushButton('取消', self.buttonGroup)
        self.__init_widget()
        self.__init_layout()
        self.__connect_signal_to_slot()

    def __init_widget(self):
        self.hideYesButton()
        self.hideCancelButton()

    def __init_layout(self):
        self.buttonLayout.addWidget(self.yes_btn)
        self.buttonLayout.addWidget(self.cancel_btn)
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.champ_select_widget)

    def __connect_signal_to_slot(self):
        self.yes_btn.clicked.connect(self.__onYesButtonClicked)
        self.cancel_btn.clicked.connect(self.__onCancelButtonClicked)

    def __onCancelButtonClicked(self):
        self.reject()

    def __onYesButtonClicked(self):
        self.completed.emit(self.champ_select_widget.get_selected_champ_ids())
        if self.validate():
            self.accept()
