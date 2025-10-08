"""
contains gui to select a slice in a volume
"""

from __future__ import annotations

import logging
import pint
import os
import weakref
from contextlib import AbstractContextManager

import numpy
from matplotlib import image as _matplotlib_image
from silx.gui import qt
from silx.gui.plot import PlotWidget

from tomwer.core.process.reconstruction.utils.cor import relative_pos_to_absolute
from tomwer.core.process.reconstruction.scores.params import ScoreMethod
from tomwer.gui import icons, settings
from tomwer.gui.reconstruction.saaxis.dimensionwidget import DimensionWidget
from tomwer.gui.utils.buttons import PadlockButton
from tomwer.gui.utils.vignettes import VignettesQDialog
from tomwer.gui.visualization.dataviewer import ImageStack
from tomwer.io.utils import get_default_directory
from tomwer.io.utils.h5pyutils import DatasetReader
from tomwer.io.utils.utils import get_slice_data

_logger = logging.getLogger(__name__)


class VariableScorePlot(PlotWidget):
    sigMouseWheelActive = qt.Signal(object)
    """emit when the mouse wheel get activated"""

    MARKER_COLOR = "#ff292199"

    def __init__(self, parent, backend=None):
        PlotWidget.__init__(self, parent, backend=backend)
        self._scores = {}
        self.setAxesDisplayed(False)
        self.setMaximumHeight(150)
        self.setMinimumHeight(100)
        # cor marker
        # self.addXMarker(
        #     x=100, legend="cor", text="cor", draggable=False, color=self.MARKER_COLOR
        # )
        # self.corMarker = self._getMarker("cor")
        # self.corMarker.setLineWidth(3)
        # Retrieve PlotWidget's plot area widget
        plotArea = self.getWidgetHandle()
        # Set plot area custom context menu
        plotArea.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        plotArea.customContextMenuRequested.connect(self._contextMenu)
        self.setInteractiveMode("select", zoomOnWheel=False)
        self.setPanWithArrowKeys(False)

    def clear(self):
        super().clear()
        # cor marker
        # self.addXMarker(
        #     x=100, legend="cor", text="cor", draggable=False, color=self.MARKER_COLOR
        # )
        # self.corMarker = self._getMarker("cor")

    def wheelEvent(self, event):
        self.sigMouseWheelActive.emit(event)

    def onMouseWheel(self, xPixel, yPixel, angleInDegrees):
        pass

    def _contextMenu(self, pos: qt.QPoint):
        """Handle plot area customContextMenuRequested signal.

        :param pos: Mouse position relative to plot area
        """
        # avoir reset zoom
        pass


class VariableSelection(qt.QWidget):
    """Widget to select which cor to select"""

    sigSelectionModeChanged = qt.Signal()
    """Signal emitted when selection mode changed"""
    sigAutoFocusLocked = qt.Signal()
    """signal send when the 'auto' mode is locked / activated"""
    sigAutoFocusUnLocked = qt.Signal()
    """signal send when the 'auto' mode is unlocked / unactivated"""

    sigVariableValueSelected = qt.Signal(float)
    """signal emitted when the cor value is selected by the user from
    vignettes"""

    sigScoreMethodChanged = qt.Signal()
    """Signal meit when the score method (std, tv) change"""

    def __init__(self, parent=None, variable_name=None):
        if not isinstance(variable_name, str):
            raise TypeError("variable_name should be a string")
        self._variable_name = variable_name
        qt.QWidget.__init__(self, parent)
        self._scores = {}
        self._img_width = None
        self._scan = None
        self.setLayout(qt.QGridLayout())
        # score method
        self._scoreMethodLabel = qt.QLabel("score method", self)
        self.layout().addWidget(self._scoreMethodLabel, 0, 0, 1, 1)
        self._scoreMethodCB = qt.QComboBox(self)
        self.layout().addWidget(self._scoreMethodCB, 0, 1, 1, 1)
        for method in ScoreMethod:
            if method is ScoreMethod.TOMO_CONSISTENCY:
                # for now we avoid this method. Does not provide great results and is very time consuming
                # I guess when we will add it we will need to first display slices
                # and then only compute the score. It might be an "on demand" score but not computed by default.
                continue
            self._scoreMethodCB.addItem(method.value)
        # default score method is 1 / tv
        idx = self._scoreMethodCB.findText(ScoreMethod.TV_INVERSE.value)
        self._scoreMethodCB.setCurrentIndex(idx)
        # left spacer
        lspacer = qt.QWidget(self)
        lspacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self.layout().addWidget(lspacer, 0, 2, 2, 1)
        # TODO: this should be inherite by a cor plot (to display variable and absloute value)
        # cor value
        self._currentVarValue = qt.QGroupBox(self)
        self._currentVarValue.setTitle(f"current {self._variable_name} value")
        self._currentVarValue.setLayout(qt.QFormLayout())
        self.layout().addWidget(self._currentVarValue, 0, 3, 3, 2)

        # cor selection option
        self._currentcorRB = qt.QRadioButton("current value", self)
        self.layout().addWidget(self._currentcorRB, 0, 5, 1, 1)
        self._autofocusRB = qt.QRadioButton("autofocus", self)
        self._autofocusRB.setToolTip(
            f"Take the {self._variable_name} with the best score"
        )
        self.layout().addWidget(self._autofocusRB, 1, 5, 1, 1)
        # lock autofocus button
        self._lockAutofocusButton = PadlockButton(self)
        self._lockAutofocusButton.setToolTip(
            "If autofocus is locked then "
            "the best center of rotation "
            "will be pick automatically"
        )
        self.layout().addWidget(self._lockAutofocusButton, 1, 7, 1, 1)
        rspacer = qt.QWidget(self)
        rspacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        self.layout().addWidget(rspacer, 0, 8, 2, 1)

        openVignettePixmap = icons.getQPixmap("vignettes")
        openVignetteIcon = qt.QIcon(openVignettePixmap)
        self._vignetteButton = qt.QPushButton(self)
        self._vignetteButton.setFixedSize(qt.QSize(50, 50))
        self._vignetteButton.setIconSize(qt.QSize(40, 40))
        self._vignetteButton.setIcon(openVignetteIcon)
        self.layout().addWidget(self._vignetteButton, 0, 9, 2, 1)

        # radio button group
        self._buttonGrp = qt.QButtonGroup()
        self._buttonGrp.addButton(self._currentcorRB)
        self._buttonGrp.addButton(self._autofocusRB)

        # set up
        self._currentcorRB.setChecked(True)

        # connect signal / slot
        self._currentcorRB.toggled.connect(self._selectionModeChanged)
        self._autofocusRB.toggled.connect(self._selectionModeChanged)
        self._lockAutofocusButton.toggled.connect(self._lockButtonActive)
        self._vignetteButton.released.connect(self._openVignetteMode)
        self._scoreMethodCB.currentIndexChanged.connect(self._scoreMethodChanged)

        # update widget to fit set up
        self._selectionModeChanged()

    def getVarSelectionMode(self):
        if self._currentcorRB.isChecked():
            return "current value"
        elif self._autofocusRB.isChecked():
            return "autofocus"
        else:
            raise NotImplementedError("")

    def _openVignetteMode(self):
        colormap = None
        if self.parent() and hasattr(self.parent(), "getPlotWidget"):
            master_plot = self.parent().getPlotWidget()
            colormap = master_plot.getPlotWidget().getColorBarWidget().getColormap()
        dialog = VignettesQDialog(
            value_name=f"{self._variable_name} position",
            score_name="score",
            value_format="{:.3f}",
            score_format="{:.3f}",
            colormap=colormap,
        )
        dialog.setWindowTitle(f"{self.getWindowTitle()} - vignettes")

        # set scores
        dialog.setScores(self._scores, score_method=self.getScoreMethod())

        if dialog.exec_() == qt.QDialog.Accepted:
            cor_selected = dialog.selectedValue()
            if cor_selected is not None:
                self.sigVariableValueSelected.emit(cor_selected)
        dialog.setAttribute(qt.Qt.WA_DeleteOnClose)

    def _selectionModeChanged(self, *args, **kwargs):
        self.sigSelectionModeChanged.emit()

    def setValue(self, relative_value):
        raise NotImplementedError("Base class")

    def getAutoFocusLockButton(self):
        return self._lockAutofocusButton

    def _scoreMethodChanged(self):
        self.sigScoreMethodChanged.emit()

    def isAutoFocusLock(self):
        return self._lockAutofocusButton.isChecked()

    def isAutoFocusActive(self):
        return self._autofocusRB.isChecked()

    def hideAutoFocusButton(self):
        self._lockAutofocusButton.hide()

    def lockAutoFocus(self, lock):
        self._currentcorRB.setEnabled(not lock)
        if lock and not self._autofocusRB.isChecked():
            self._autofocusRB.setChecked(True)
        self._lockAutofocusButton.setChecked(lock)

    def _lockButtonActive(self, lock):
        self.lockAutoFocus(lock)
        if self._lockAutofocusButton.isChecked():
            self.sigAutoFocusLocked.emit()
        else:
            self.sigAutoFocusUnLocked.emit()

    def setScores(self, scores: dict):
        self._scores = scores

    def setImgWidth(self, width):
        self._img_width = width

    def getScoreMethod(self):
        return ScoreMethod(self._scoreMethodCB.currentText())

    def setScoreMethod(self, method):
        method_value = ScoreMethod(method).value
        index = self._scoreMethodCB.findText(method_value)
        self._scoreMethodCB.setCurrentIndex(index)


class SingleValueSelection(VariableSelection):
    def __init__(self, *args, **kwargs):
        VariableSelection.__init__(self, *args, **kwargs)
        self._valueLE = qt.QLineEdit(self)
        self._valueLE.setReadOnly(True)
        self._currentVarValue.layout().addRow("value:", self._valueLE)

    def setValue(self, value):
        self._valueLE.setText(f"{value:.2f}")

    def getWindowTitle(self):
        raise NotImplementedError("Base class")


class DelaBetaSelection(SingleValueSelection):
    # FIXME: fix typo Dela vs Delta
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        idx = self._scoreMethodCB.findText(ScoreMethod.TOMO_CONSISTENCY.value)
        if idx >= 0:
            self._scoreMethodCB.removeItem(idx)

    def getWindowTitle(self):
        return "sa delta/beta vignettes"


class CorSelection(VariableSelection):
    def __init__(self, *args, **kwargs):
        VariableSelection.__init__(self, *args, **kwargs)
        self._relativeVarValueLE = qt.QLineEdit(self)
        self._relativeVarValueLE.setReadOnly(True)
        self._currentVarValue.layout().addRow("relative:", self._relativeVarValueLE)
        self._absoluteVarValueLE = qt.QLineEdit(self)
        self._absoluteVarValueLE.setReadOnly(True)
        self._currentVarValue.layout().addRow(
            "absolute:",
            self._absoluteVarValueLE,
        )
        try:
            import pyopencl  # noqa F401 pylint: disable=E0401
        except Exception:
            idx = self._scoreMethodCB.findText(ScoreMethod.TOMO_CONSISTENCY.value)
            if idx >= 0:
                self._scoreMethodCB.removeItem(idx)

    def setValue(self, relative_value):
        if relative_value is None:
            self._relativeVarValueLE.clear()
        else:
            self._relativeVarValueLE.setText(f"{relative_value:.3f}")
        if relative_value is None or self._img_width is None:
            self._absoluteVarValueLE.clear()
        else:
            absolute_value = relative_pos_to_absolute(
                relative_pos=relative_value, det_width=self._img_width
            )
            self._absoluteVarValueLE.setText(f"{absolute_value:.3f}")

    def getWindowTitle(self):
        return "sa axis - vignettes"


class PainterRotationCM(AbstractContextManager):
    """
    On enter move the painter to the position and rotate it of provided angle.
    On exits rotate back then translate back to the original position
    """

    def __init__(self, painter, x: float, y: float, angle: float):
        self.painter = painter
        self.x = x
        self.y = y
        self.angle = angle

    def __enter__(self):
        self.painter.translate(self.x, self.y)
        self.painter.rotate(self.angle)
        return self.painter

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.painter.rotate(-self.angle)
        self.painter.translate(-self.x, -self.y)


class _VariableValueLabels(qt.QWidget):
    """
    Display labels for center of rotation
    """

    # TODO: could be used to define the current value displayed by underlying
    # and the one selected in red.

    _LABEL_WIDTH = 60
    """Label width with rotation"""

    MIN_WIDTH_PER_LABEL = 40
    """Label width without rotation"""

    # DEBUG OPTIONS: Deformation is not handled so you should put rotation to 0
    PLOT_TICKS = False

    PLOT_CANVAS_LIM = False

    PLOT_LABEL_RECT = False

    def __init__(self, parent=None, angle: float = 45.0):
        qt.QWidget.__init__(self, parent)
        self._var_values = tuple()
        self._right_shift = 0
        self._slider_ticks_margin = 0
        self.rotation_angle_degree = angle

    def setVarValues(self, values):
        self._var_values = numpy.array(values)

    def setRightShift(self, shift: int):
        self._right_shift = shift

    def setSliderTicksMargin(self, margin: int):
        self._slider_ticks_margin = margin

    def getVarSteps(self) -> int:
        """
        Return step for the cor values to be displayed.
        1: display all cor values
        2: display one cor per each 2 values
        :return:
        """
        if len(self._var_values) == 0:
            return 1
        width = self.width()
        # 1.8: as we are a 45 degree then / 2.0 should be good. Dividing by 1.8
        # instead will increase visibility
        n_var_values = self._var_values.size
        for i in range(1, 9):
            if ((n_var_values / i) * self.MIN_WIDTH_PER_LABEL) < width:
                return i
        return 10

    def paintEvent(self, event):
        n_var_values = len(self._var_values)
        if n_var_values == 0:
            return
        elif n_var_values < 5:
            var_indexes = numpy.arange(n_var_values)
        else:
            var_indexes = numpy.arange(0, self._var_values.size)[:: self.getVarSteps()]

        from_ = self._slider_ticks_margin
        to_ = self.width() - self._right_shift - self._slider_ticks_margin
        var_px_positions = numpy.linspace(
            from_, to_, self._var_values.size, endpoint=True
        )

        painter = qt.QPainter(self)
        # painter.translate(self.rect().topLeft())
        font = qt.QFont("Helvetica", 10)
        painter.setFont(font)

        txt_width = self._LABEL_WIDTH
        txt_height = self.height()

        for i_var in var_indexes:
            var_value = self._var_values[i_var]
            var_px_pos = var_px_positions[i_var]
            txt_value = f"{var_value:.3f}"
            # apply rotation to "invert" the painter rotation requested to
            # paint oblique text
            with PainterRotationCM(
                painter=painter,
                x=var_px_pos + (self._slider_ticks_margin / 2.0),
                y=0,
                angle=self.rotation_angle_degree,
            ) as l_painter:
                var_rect = qt.QRect(0, 0, txt_width, txt_height)
                l_painter.drawText(var_rect, qt.Qt.AlignLeft, txt_value)

                if self.PLOT_LABEL_RECT:
                    painter.drawRect(var_rect)

        # print all ticks
        if self.PLOT_TICKS:
            painter.setPen(qt.QPen(qt.QColor(35, 234, 32)))
            tick_positions = numpy.linspace(
                from_, to_, len(self._var_values), endpoint=True
            )
            for pos in tick_positions:
                var_rect = qt.QRect(pos, 0, 2, 6)
                painter.drawRect(var_rect)

        # print canvas
        if self.PLOT_CANVAS_LIM:
            painter.setPen(qt.QPen(qt.QColor(168, 34, 32)))
            x, y = self.width() - 2, self.height() - 2
            var_rect = qt.QRect(0, 0, x, y)
            painter.drawRect(var_rect)


class ScorePlot(qt.QWidget):
    """
    Plot to display the scores
    """

    sigConfigurationChanged = qt.Signal()
    """signal emitted when the configuration change"""

    _CENTRAL_SLICE_NAME = "central slice"

    def __init__(
        self,
        parent=None,
        variable_name=None,
        dims_colors=("#ffff5a", "#62efff", "#ff5bff"),
        backend=None,
    ):
        if not isinstance(variable_name, str):
            raise TypeError("a variable name should be provided as a string")
        self._dim_colors = dims_colors
        self._var_values = tuple()
        self._scores = {}
        self.__scan = None

        qt.QWidget.__init__(self, parent)
        # define GUI
        self.setLayout(qt.QGridLayout())
        # main plot
        self._plot = ImageStack(self, show_overview=False, backend=backend)
        self._plot.getPlotWidget().setYAxisInverted(settings.Y_AXIS_DOWNWARD)

        self._plot.getPlotWidget().setKeepDataAspectRatio(True)
        self._plot._sliderDockWidget.hide()
        self._plot.getPlotWidget().getColorBarWidget().hide()
        self._plot.getPlotWidget().getPositionInfoWidget().hide()
        # add save all action
        save_all_icon = icons.getQIcon("multi-document-save")
        self._saveAllSnapshot = qt.QAction(
            save_all_icon, "save all screenshot as png", self
        )
        toolbar = self._plot.getPlotWidget().toolBar()
        toolbar.addSeparator()
        toolbar.addAction(self._saveAllSnapshot)
        # hide dock widget
        self._plot._reconsInfoDockWidget.hide()
        self._plot._tableDockWidget.hide()
        self.layout().addWidget(self._plot, 0, 0, 1, 2)
        right_shift = 40  # pixel
        # cor score plot
        self._varScore = VariableScorePlot(self)
        self._varScore.setContentsMargins(15, 10, right_shift + 15, 0)
        self.layout().addWidget(self._varScore, 1, 0, 1, 2)
        # slider
        self._varSlider = _VarSlider(self, orientation=qt.Qt.Horizontal)
        self.layout().addWidget(self._varSlider, 2, 0, 1, 2)
        self._varSlider.setContentsMargins(0, 0, right_shift, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.layout().addWidget(self._varSlider, 3, 0, 1, 2)
        # cor labels
        self._varLabels = _VariableValueLabels(self)
        self._varLabels.setContentsMargins(0, 0, 0, 0)
        self._varLabels.setFixedHeight(60)
        self.layout().addWidget(self._varLabels, 4, 0, 1, 2)
        self._varLabels.setRightShift(right_shift)
        self._varLabels.setSliderTicksMargin(15)
        # cor value
        self._varValueWidget = self._CorSlectionBuilder(self, variable_name)
        self._varValueWidget.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._varValueWidget, 5, 0, 1, 1)
        # voxel size
        self._voxelSizeW = DimensionWidget(
            title="Voxel size",
            dims_name=("x:", "y:", "z:"),
            dims_colors=self._dim_colors,
        )
        self._voxelSizeW.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._voxelSizeW, 6, 0, 1, 1)
        # volume size W
        self._volumeSizeW = DimensionWidget(
            title="Volume size",
            dims_name=("x:", "y:", "z:"),
            dims_colors=self._dim_colors,
        )
        self._volumeSizeW.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self._volumeSizeW, 6, 0, 1, 1)
        # axis
        self.setContentsMargins(0, 0, 0, 0)
        self._axisLabel = qt.QLabel(parent=self)
        icon = icons.getQIcon("axis")
        self._axisLabel.setPixmap(icon.pixmap(qt.QSize(96, 96)))
        self.layout().addWidget(self._axisLabel, 7, 1, 2, 1)

        # connect signal / slot
        self._varSlider.valueChanged.connect(self._plot.setCurrentUrlIndex)
        self._varSlider.valueChanged.connect(self._sliderReleased)
        self._varSlider.valueChanged.connect(self._updateVarValue)
        self._varScore.sigMouseWheelActive.connect(self._varSlider.wheelEvent)
        self._varValueWidget.sigAutoFocusLocked.connect(self._autoFocusLockChanged)
        self._varValueWidget.sigAutoFocusUnLocked.connect(self._autoFocusLockChanged)
        self._varValueWidget.sigSelectionModeChanged.connect(
            self._varSelectionModeChanged
        )
        self._varValueWidget.sigVariableValueSelected.connect(
            self._varSelectedFromVignettes
        )
        self._varValueWidget.sigScoreMethodChanged.connect(self._updateScores)
        self._saveAllSnapshot.triggered.connect(self._saveAllReconstructedSlices)

        # set up
        # for now we don't want to use the volume and voxel size
        self._volumeSizeW.hide()
        self._voxelSizeW.hide()
        self._axisLabel.hide()
        # use mean mean+/-3std for the cor
        plotWidget = self._plot.getPlotWidget()
        colormap = plotWidget.getDefaultColormap()
        colormap.setAutoscaleMode(colormap.STDDEV3)
        plotWidget.setDefaultColormap(colormap=colormap)

    def __init_subclass__(cls, constructor, **kwargs):  # pylint: disable=E0302
        super().__init_subclass__()
        cls._CorSlectionBuilder = constructor

    def getScoreMethod(self):
        return self._varValueWidget.getScoreMethod()

    def setScoreMethod(self, method):
        self._varValueWidget.setScoreMethod(method)

    def _configurationChanged(self, *args, **kwargs):
        self.sigConfigurationChanged.emit()

    def getPlotWidget(self):
        return self._plot

    def close(self):
        self._plot.close()
        self._plot = None
        super().close()

    def getCurrentVarValue(self):
        cor_idx = self._varSlider.value()
        if cor_idx < len(self._var_values):
            return self._var_values[cor_idx]

    def setCurrentVarValue(self, value):
        self._varSlider.setVarValue(value=value)
        self._varValueWidget.setValue(value)

    def lockAutoFocus(self, lock):
        self._varValueWidget.lockAutoFocus(lock)

    def isAutoFocusLock(self):
        return self._varValueWidget.isAutoFocusLock()

    def hideAutoFocusButton(self):
        self._varValueWidget.hideAutoFocusButton()

    def isAutoFocusActive(self):
        return self._varValueWidget.isAutoFocusActive()

    def _autoFocusLockChanged(self):
        if self.isAutoFocusLock():
            self._applyAutofocus()
        self._configurationChanged()

    def getVarSelectionMode(self):
        return self._varValueWidget.getVarSelectionMode()

    def _applyAutofocus(self):
        raise NotImplementedError("Base class")

    def _varSelectionModeChanged(self):
        if self.getVarSelectionMode() == "autofocus":
            self._applyAutofocus()

    def _updateVarValue(self):
        self._varValueWidget.setValue(self.getCurrentVarValue())

    def _varSelectedFromVignettes(self, value):
        self._varSlider.setVarValue(value)

    def _get_closest_var(self, value):
        """return the closest cor value to value or None if no cor value
        defined"""
        if len(self._var_values) > 0:
            idx_closest = numpy.argmin(numpy.abs(self._var_values - value))
            return self._var_values[idx_closest]
        else:
            return None

    def _markerReleased(self):
        return

    def _sliderReleased(self):
        return

    def setScan(self, scan):
        self.clear()
        self.__scan = weakref.ref(scan)

    def _updateScores(self):
        raise NotImplementedError("Base class")

    def setVarScores(
        self,
        scores: dict,
        score_method: str | ScoreMethod,
        img_width=None,
        update_only_scores=False,
    ):
        """

        :param scores: cor value (float) as key and
                            tuple(url: DataUrl, score: float) as value
        """
        score_method = ScoreMethod(score_method)
        if not update_only_scores:
            self.clear()
            self._scores = scores
            self.setImgWidth(img_width)
        # set image width to deduce absolute position from relative
        self._var_values = []
        score_list = []
        self._urls = []

        if scores is None or len(scores) == 0:
            return
        for cor_value, cor_info in scores.items():
            url, score = cor_info
            if score is None:
                continue  # in case score calculation failed
            self._var_values.append(cor_value)
            score_list.append(score.get(score_method))
            self._urls.append(url)
        # insure cor and scores are numpy arrays
        self._var_values = list(self._var_values)
        score_list = numpy.array(score_list)
        # set zoom a priori
        if not update_only_scores and len(self._urls) > 0:
            try:
                with DatasetReader(url=self._urls[0]) as dataset:
                    dataset.shape
            except Exception as e:
                _logger.warning(e)
            else:
                self._plot.setResetZoomOnNextIteration(True)

        if not update_only_scores:
            self._plot.setUrls(urls=self._urls)
            self._varSlider.setVarValues(self._var_values)
            old = self._varSlider.blockSignals(True)
            if len(self._var_values) > 0:
                self._varSlider.setVarValue(self._var_values[0])
            self._varSlider.blockSignals(old)

        old = self._varValueWidget.blockSignals(True)
        self.setScoreMethod(score_method)
        self._varValueWidget.blockSignals(old)

        self._varScore.addCurve(
            x=numpy.array(self._var_values),
            y=score_list,
            baseline=0,
            fill=True,
            color="#0288d190",
        )
        self._varLabels.setVarValues(self._var_values)
        # update cor marker position according to the slider position
        self._sliderReleased()
        self._varValueWidget.setScores(scores)
        scan = self.__scan() if self.__scan else None
        if scan is not None and self.isAutoFocusActive():
            self._applyAutofocus()

    def setImgWidth(self, width):
        self._varValueWidget.setImgWidth(width)

    def clear(self):
        self._varSlider.setVarValues(tuple())
        self._varScore.clear()
        self._varLabels.setVarValues(tuple())
        self._plot.getPlotWidget().clear()
        self._varValueWidget.setImgWidth(None)

    def setVoxelSize(
        self, dim0: pint.Quantity, dim1: pint.Quantity, dim2: pint.Quantity
    ):
        """

        :param dim0:
        :param dim1:
        :param dim2:
        :param unit:
        """
        self._voxelSizeW.setQuantities(dim0=dim0, dim1=dim1, dim2=dim2)

    def setVolumeSize(
        self, dim0: pint.Quantity, dim1: pint.Quantity, dim2: pint.Quantity
    ):
        """

        :param dim0:
        :param dim1:
        :param dim2:
        :param unit:
        """
        self._volumeSizeW.setQuantities(dim0=dim0, dim1=dim1, dim2=dim2)

    def getDim0N(self):
        """return the number of elements in dimension 0 according to voxel
        size and volume size"""
        return int(
            numpy.ceil(
                self._volumeSizeW.getDim0Quantity().to_base_units().magnitude
                / self._voxelSizeW.getDim0Quantity().to_base_units().magnitude
            )
        )

    def getDim1N(self):
        """return the number of elements in dimension 1 according to voxel
        size and volume size"""
        return int(
            numpy.ceil(
                self._volumeSizeW.getDim1Quantity().to_base_units().magnitude
                / self._voxelSizeW.getDim1Quantity().to_base_units().magnitude
            )
        )

    def getDim2N(self):
        """return the number of elements in dimension 2 according to voxel
        size and volume size"""
        return int(
            numpy.ceil(
                self._volumeSizeW.getDim2Quantity().to_base_units().magnitude
                / self._voxelSizeW.getDim2Quantity().to_base_units().magnitude
            )
        )

    def _saveAllReconstructedSlices(self):  # pragma: no cover
        """
        save all reconstructed slices to a folder provided by the user
        """
        dialog = qt.QFileDialog(self, directory=get_default_directory())
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)
        if not dialog.exec_():
            dialog.close()
            return

        output_folder = dialog.selectedFiles()[0]
        try:
            self.saveReconstructedSlicesTo(output_folder=output_folder)
        except Exception as e:
            _logger.error(f"Fail to save snapshots. Error is {e}")
        else:
            _logger.info(f"snapshots have been saved to {output_folder}")

    def saveReconstructedSlicesTo(self, output_folder):
        """dump all slices with score as name"""
        # make sure the output dir exists
        os.makedirs(output_folder, exist_ok=True)

        i_missing_score = 0
        for score, slice_url in zip(self._var_values, self._urls):
            try:
                data = get_slice_data(slice_url)
                if score is None:
                    file_name = f"no_score_{i_missing_score}.png"
                    i_missing_score += 1
                else:
                    file_name = f"{score}.png"
                _matplotlib_image.imsave(
                    os.path.join(output_folder, file_name),
                    data,
                    format="png",
                )

            except Exception as e:
                _logger.error(f"Failed to dump {slice_url.path()}. Raison is {e}")


class _VarSlider(qt.QWidget):
    def __init__(self, parent, orientation):
        self._values = None
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self._slider = qt.QSlider(self)
        self.layout().addWidget(self._slider)
        self._slider.setMaximum(0)
        self._slider.setOrientation(orientation)
        self._slider.setTickPosition(qt.QSlider.TicksBelow)

        # connect signal / slot
        self.valueChanged = self._slider.valueChanged

    def wheelEvent(self, event) -> None:
        self._slider.wheelEvent(event)

    def setVarValues(self, values):
        self._slider.setRange(0, len(values) - 1)
        self._values = numpy.array(values, dtype=numpy.float32)

    def setVarValue(self, value):
        if value in self._values:
            where = numpy.where(self._values == value)
            if len(where) > 0:
                value = where[0]
                if isinstance(value, numpy.ndarray):
                    value = value[0]
                self._slider.setValue(int(value))

    def value(self):
        return self._slider.value()
