from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

import pandas as pd

from ert.gui.tools.plot.plot_api import EnsembleObject

from .plot_tools import PlotTools

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from pandas import DataFrame

    from ert.gui.plottery import PlotConfig, PlotContext


class DistributionPlot:
    def __init__(self) -> None:
        self.dimensionality = 1

    @staticmethod
    def plot(
        figure: Figure,
        plot_context: PlotContext,
        ensemble_to_data_map: dict[str, DataFrame],
        _observation_data: DataFrame,
        std_dev_images: Any,
    ) -> None:
        plotDistribution(figure, plot_context, ensemble_to_data_map, _observation_data)


def plotDistribution(
    figure: Figure,
    plot_context: PlotContext,
    ensemble_to_data_map: Dict[EnsembleObject, pd.DataFrame],
    _observation_data: pd.DataFrame,
) -> None:
    config = plot_context.plotConfig()
    axes = figure.add_subplot(111)

    plot_context.deactivateDateSupport()

    plot_context.y_axis = plot_context.VALUE_AXIS

    if plot_context.log_scale:
        axes.set_yscale("log")

    ensemble_list = plot_context.ensembles()
    ensemble_indexes: List[int] = []
    previous_data = None
    for ensemble_index, (ensemble, data) in enumerate(ensemble_to_data_map.items()):
        ensemble_indexes.append(ensemble_index)

        if not data.empty:
            _plotDistribution(
                axes, config, data, ensemble.name, ensemble_index, previous_data
            )
            config.nextColor()

        previous_data = data

    axes.set_xticks([-1] + ensemble_indexes + [len(ensemble_indexes)])

    rotation = 0
    if len(ensemble_list) > 3:
        rotation = 30

    axes.set_xticklabels(
        [""]
        + [
            f"{ensemble.experiment_name} : {ensemble.name}"
            for ensemble in ensemble_list
        ]
        + [""],
        rotation=rotation,
    )
    config.setLegendEnabled(False)

    PlotTools.finalizePlot(
        plot_context, figure, axes, default_x_label="Ensemble", default_y_label="Value"
    )


def _plotDistribution(
    axes: "Axes",
    plot_config: "PlotConfig",
    data: pd.DataFrame,
    label: str,
    index: int,
    previous_data: pd.DataFrame,
) -> None:
    _data = pd.Series(dtype="float64") if data.empty else data[0]
    if xlabel := plot_config.xLabel():
        axes.set_xlabel(xlabel)
    if ylabel := plot_config.yLabel():
        axes.set_ylabel(ylabel)
    style = plot_config.distributionStyle()

    if _data.dtype == "object":
        try:
            _data = pd.to_numeric(_data, errors="coerce")
        except AttributeError:
            _data = _data.convert_objects(convert_numeric=True)

    if _data.dtype == "object":
        dots = []
    else:
        dots = axes.plot(
            [index] * len(_data),
            _data,
            color=style.color,
            alpha=style.alpha,
            marker=style.marker,
            linestyle=style.line_style,
            markersize=style.size,
        )

        if plot_config.isDistributionLineEnabled() and previous_data is not None:
            line_style = plot_config.distributionLineStyle()
            x = [index - 1, index]
            y = [previous_data[0], _data]
            axes.plot(
                x,
                y,
                color=line_style.color,
                alpha=line_style.alpha,
                linestyle=line_style.line_style,
                linewidth=line_style.width,
            )

    if len(dots) > 0:
        plot_config.addLegendItem(label, dots[0])
