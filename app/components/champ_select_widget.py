from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from qfluentwidgets import SmoothScrollArea, FlowLayout, SearchLineEdit, TransparentToolButton, FluentIcon

from app.components.draggable_widget import DraggableItem, ItemsDraggableWidget
from app.components.round_widget import RoundIcon, RoundIconButton


class ChampionTabItem(DraggableItem):
    closeRequested = pyqtSignal()

    def __init__(self, icon, name, championId, parent=None):
        super().__init__(parent)

        self.hBoxLayout = QHBoxLayout(self)

        self.icon = RoundIcon(icon, 26, 2, 2)
        self.name = QLabel(name)
        self.championId = championId

        self.closeButton = TransparentToolButton(FluentIcon.CLOSE)

        self.__initWidgets()
        self.__initLayout()

    def __eq__(self, other):
        return self.championId == other.championId

    def __initWidgets(self):
        self.setFixedSize(141, 47)
        self.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect)

        self.closeButton.setIconSize(QSize(12, 12))
        self.closeButton.setFixedSize(QSize(26, 26))
        self.closeButton.clicked.connect(self.closeRequested)

        self.setMinimumWidth(200)
        self.name.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

    def __initLayout(self):
        self.hBoxLayout.setContentsMargins(10, 8, 4, 8)
        self.hBoxLayout.addWidget(self.icon)
        self.hBoxLayout.addSpacing(5)
        self.hBoxLayout.addWidget(self.name)
        self.hBoxLayout.addWidget(self.closeButton, alignment=Qt.AlignmentFlag.AlignRight)

    def sizeHint(self):
        return QSize(141, 44)


class ChampionDraggableWidget(ItemsDraggableWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__initWidget()

    def __initWidget(self):
        self.setFixedHeight(334)
        self.setFixedWidth(224)

    def addItem(self, icon, name, championId):
        item = ChampionTabItem(icon, name, championId)
        if item in self.items:
            return
        if len(self.items) >= 6:
            return
        item.closeRequested.connect(lambda i=item: self._removeItem(i))
        self._addItem(item)

    def getCurrentChampionIds(self):
        return [item.championId for item in self.items]


class ChampSelectWidget(QWidget):
    def __init__(self, champs, selected, parent=None):
        super().__init__(parent)
        self.champs = champs
        self.selected_list = selected

        self.box = QHBoxLayout(self)
        self.selected_widget = ChampionDraggableWidget()

        self.champ_select_widget = QWidget()
        self.champ_select_layout = QVBoxLayout(self.champ_select_widget)
        self.search_line_edit = SearchLineEdit()

        self.champs_scroll_area = SmoothScrollArea()
        self.champs_scroll_area.setFixedSize(300, 295)
        self.champs_widget = QWidget()
        self.champs_layout = FlowLayout(needAni=True, isTight=True)

        self.__init_layout()
        self.__init_widget()

    def __init_layout(self):
        self.champs_widget.setLayout(self.champs_layout)

        self.champs_scroll_area.setWidget(self.champs_widget)
        self.champs_scroll_area.setWidgetResizable(True)

        self.champ_select_layout.setContentsMargins(0, 0, 0, 0)
        self.champ_select_layout.addWidget(self.search_line_edit)
        self.champ_select_layout.addWidget(self.champs_scroll_area)

        self.box.addWidget(self.selected_widget)
        self.box.addWidget(self.champ_select_widget)

    def __init_widget(self):

        for id in self.selected_list:
            champ = [champ for champ in self.champs if champ['id'] == id][0]
            name = champ['name']
            icon = champ['icon']
            self.selected_widget.addItem(icon, name, id)
        self.selected_widget.setStyleSheet('background-color: rgba(245, 245, 245, 0.667);')

        for champ in self.champs:
            if champ['id'] != -1:
                btn = RoundIconButton(champ)
                btn.clicked.connect(self.__on_icon_clicked)
                self.champs_layout.addWidget(btn)

    @pyqtSlot(dict)
    def __on_icon_clicked(self, champ):
        self.selected_widget.addItem(champ['icon'], champ['name'], champ['id'])

    def get_selected_champ_ids(self):
        return self.selected_widget.getCurrentChampionIds()
