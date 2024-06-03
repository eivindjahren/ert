from typing import Optional

from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QColor, QFocusEvent, QIcon, QKeyEvent, QResizeEvent
from qtpy.QtWidgets import QLineEdit, QPushButton, QStyle


class ClearableLineEdit(QLineEdit):
    passive_color = QColor(194, 194, 194)

    def __init__(self, placeholder: str = "yyyy-mm-dd") -> None:
        QLineEdit.__init__(self)

        self._placeholder_text = placeholder
        self._active_color = self.palette().color(self.foregroundRole())
        self._placeholder_active = False

        self._clear_button = QPushButton(self)
        self._clear_button.setIcon(QIcon("img:remove_outlined.svg"))
        self._clear_button.setFlat(True)
        self._clear_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._clear_button.setFixedSize(17, 17)
        self._clear_button.setCursor(Qt.CursorShape.ArrowCursor)

        self._clear_button.clicked.connect(self.clearButtonClicked)
        self._clear_button.setVisible(False)

        self.textChanged.connect(self.toggleClearButtonVisibility)

        self.showPlaceholder()

    def toggleClearButtonVisibility(self) -> None:
        self._clear_button.setVisible(
            len(self.text()) > 0 and not self._placeholder_active
        )

    def sizeHint(self) -> QSize:
        size = QLineEdit.sizeHint(self)
        return QSize(size.width() + self._clear_button.width() + 3, size.height())

    def minimumSizeHint(self) -> QSize:
        size = QLineEdit.minimumSizeHint(self)
        return QSize(size.width() + self._clear_button.width() + 3, size.height())

    def resizeEvent(self, event: Optional[QResizeEvent]) -> None:
        if event and (style := self.style()) is not None:
            right = self.rect().right()
            frame_width = style.pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth)
            self._clear_button.move(
                right - frame_width - self._clear_button.width(),
                int((self.height() - self._clear_button.height()) / 2),
            )
        QLineEdit.resizeEvent(self, event)

    def clearButtonClicked(self) -> None:
        self.setText("")

    def showPlaceholder(self) -> None:
        if not self._placeholder_active:
            self._placeholder_active = True
            QLineEdit.setText(self, self._placeholder_text)
            palette = self.palette()
            palette.setColor(self.foregroundRole(), self.passive_color)
            self.setPalette(palette)

    def hidePlaceHolder(self) -> None:
        if self._placeholder_active:
            self._placeholder_active = False
            QLineEdit.setText(self, "")
            palette = self.palette()
            palette.setColor(self.foregroundRole(), self._active_color)
            self.setPalette(palette)

    def focusInEvent(self, focus_event: Optional[QFocusEvent]) -> None:
        QLineEdit.focusInEvent(self, focus_event)
        self.hidePlaceHolder()

    def focusOutEvent(self, focus_event: Optional[QFocusEvent]) -> None:
        QLineEdit.focusOutEvent(self, focus_event)
        if not QLineEdit.text(self):
            self.showPlaceholder()

    def keyPressEvent(self, key_event: Optional[QKeyEvent]) -> None:
        if key_event and key_event.key() == Qt.Key.Key_Escape:
            self.clear()
            self.clearFocus()
            key_event.accept()

        QLineEdit.keyPressEvent(self, key_event)

    def setText(self, string: Optional[str]) -> None:
        self.hidePlaceHolder()

        QLineEdit.setText(self, string)

        if len(str(string)) == 0 and not self.hasFocus():
            self.showPlaceholder()

    def text(self) -> str:
        if self._placeholder_active:
            return ""
        else:
            return QLineEdit.text(self)
