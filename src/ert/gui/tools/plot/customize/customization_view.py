from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from qtpy.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QSpacerItem,
    QSpinBox,
    QWidget,
)

from ert.gui.tools.plot.widgets.clearable_line_edit import ClearableLineEdit

from .. import style_chooser as sc

if TYPE_CHECKING:
    from ert.gui.plottery import PlotConfig


class CustomizationView(QWidget):
    def __init__(self) -> None:
        QWidget.__init__(self)

        self._layout = QFormLayout()
        self.setLayout(self._layout)
        self._widgets = {}

    def addRow(self, title: Optional[str], widget: Optional[QWidget]) -> None:
        self._layout.addRow(title, widget)

    def addLineEdit(self, attribute_name, title, tool_tip=None, placeholder=""):
        self[attribute_name] = ClearableLineEdit(placeholder=placeholder)
        self.addRow(title, self[attribute_name])

        if tool_tip is not None:
            self[attribute_name].setToolTip(tool_tip)

        def getter(self) -> Optional[str]:
            value = str(self[attribute_name].text())
            if not value:
                value = None
            return value

        def setter(self, value: Optional[str]) -> None:
            if value is None:
                value = ""
            self[attribute_name].setText(str(value))

        self.updateProperty(attribute_name, getter, setter)

    def addCheckBox(
        self, attribute_name: str, title: str, tool_tip: Optional[str] = None
    ) -> None:
        self[attribute_name] = QCheckBox()
        self.addRow(title, self[attribute_name])

        if tool_tip is not None:
            self[attribute_name].setToolTip(tool_tip)

        def getter(self) -> bool:
            return self[attribute_name].isChecked()

        def setter(self, value: bool) -> None:
            self[attribute_name].setChecked(value)

        self.updateProperty(attribute_name, getter, setter)

    def addSpinBox(
        self,
        attribute_name: str,
        title: str,
        tool_tip: Optional[str] = None,
        min_value: int = 1,
        max_value: int = 10,
        single_step: int = 1,
    ) -> QSpinBox:
        sb = QSpinBox()
        self[attribute_name] = sb
        sb.setMaximumHeight(25)
        sb_layout = QHBoxLayout()
        sb_layout.addWidget(sb)
        sb_layout.addStretch()
        self.addRow(title, sb_layout)

        if tool_tip is not None:
            sb.setToolTip(tool_tip)

        sb.setMinimum(min_value)
        sb.setMaximum(max_value)
        sb.setSingleStep(single_step)

        def getter(self) -> QWidget:
            return self[attribute_name].value()

        def setter(self, value: QWidget) -> None:
            self[attribute_name].setValue(value)

        self.updateProperty(attribute_name, getter, setter)
        return sb

    def addStyleChooser(
        self,
        attribute_name: str,
        title: str,
        tool_tip: Optional[str] = None,
        line_style_set=sc.STYLESET_DEFAULT,
    ) -> None:
        style_chooser = sc.StyleChooser(line_style_set=line_style_set)
        self[attribute_name] = style_chooser
        self.addRow(title, self[attribute_name])

        if tool_tip is not None:
            self[attribute_name].setToolTip(tool_tip)

        def getter(self) -> QWidget:
            return self[attribute_name].getStyle()

        def setter(self, style: QWidget) -> None:
            self[attribute_name].setStyle(style)

        self.updateProperty(attribute_name, getter, setter)

    def updateProperty(self, attribute_name, getter, setter):
        setattr(self.__class__, attribute_name, property(getter, setter))

    def addSpacing(self, pixels=10):
        self._layout.addItem(QSpacerItem(1, pixels))

    def addHeading(self, title):
        self.addSpacing(10)
        self._layout.addRow(title, None)
        self.addSpacing(1)

    def __getitem__(self, item: str) -> QWidget:
        return self._widgets[item]

    def __setitem__(self, key: str, value: QWidget) -> None:
        self._widgets[key] = value

    def applyCustomization(self, plot_config: PlotConfig) -> None:
        raise NotImplementedError(
            f"Class '{self.__class__.__name__}' has not implemented "
            "the applyCustomization() function!"
        )

    def revertCustomization(self, plot_config: "PlotConfig") -> None:
        raise NotImplementedError(
            f"Class '{self.__class__.__name__}' has not implemented "
            "the revertCustomization() function!"
        )


class WidgetProperty:
    def __get__(self, instance: Any, owner: Any) -> Any:
        raise UserWarning("Property is invalid!")

    def __set__(self, instance: Any, value: Any) -> Any:
        raise UserWarning("Property is invalid!")
