# coding: utf-8
from __future__ import annotations


import logging

from nabu.pipeline.config import get_default_nabu_config
from nabu.pipeline.fullfield.nabu_config import (
    nabu_config as nabu_fullfield_default_config,
)
from silx.gui import icons as silx_icons
from silx.gui import qt
from enum import Enum as _Enum
from nxtomo.nxobject.nxdetector import FOV

from tomwer.core.utils.dictutils import concatenate_dict
from tomwer.core.process.reconstruction.nabu.utils import _NabuMode
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui import icons as tomwer_icons
from tomwer.gui.reconstruction.nabu.nabuflow import NabuFlowArea
from tomwer.gui.reconstruction.nabu.platform import NabuPlatformSettings
from tomwer.gui.utils.buttons import PadlockButton
from tomwer.gui.settings import TAB_LABEL_PLATFORM_SETTINGS

from ...utils.flow import FlowDirection
from tomwer.gui.configuration.action import (
    BasicConfigurationAction,
    ExpertConfigurationAction,
    FilterAction,
    MinimalisticConfigurationAction,
)
from tomwer.gui.configuration.level import ConfigurationLevel
from .nabuconfig import NabuConfiguration

_logger = logging.getLogger(__name__)


class _NabuStages(_Enum):
    INI = "initialization"
    PRE = "pre-processing"
    PHASE = "phase"
    PROC = "processing"
    POST = "post-processing"
    VOLUME = "volume"

    @staticmethod
    def getStagesOrder():
        return (
            _NabuStages.INI,
            _NabuStages.PRE,
            _NabuStages.PHASE,
            _NabuStages.PROC,
            _NabuStages.POST,
        )

    @staticmethod
    def getProcessEnum(stage):
        """Return the process Enum associated to the stage"""
        stage = _NabuStages(stage)
        if stage is _NabuStages.INI:
            raise NotImplementedError()
        elif stage is _NabuStages.PRE:
            return _NabuPreprocessing
        elif stage is _NabuStages.PHASE:
            return _NabuPhase
        elif stage is _NabuStages.PROC:
            return _NabuProcessing
        elif stage is _NabuStages.POST:
            raise NotImplementedError()
        raise NotImplementedError()


class _NabuPreprocessing(_Enum):
    """Define all the preprocessing action possible and the order they
    are applied on"""

    FLAT_FIELD_NORMALIZATION = "flat field normalization"
    CCD_FILTER = "hot spot correction"

    @staticmethod
    def getPreProcessOrder():
        return (
            _NabuPreprocessing.FLAT_FIELD_NORMALIZATION,
            _NabuPreprocessing.CCD_FILTER,
        )


class _NabuPhase(_Enum):
    """Define all the phase action possible and the order they
    are applied on"""

    PHASE = "phase retrieval"
    UNSHARP_MASK = "unsharp mask"
    LOGARITHM = "logarithm"

    @staticmethod
    def getPreProcessOrder():
        return (_NabuPhase.PHASE, _NabuPhase.UNSHARP_MASK, _NabuPhase.LOGARITHM)


class _NabuProcessing(_Enum):
    """Define all the processing action possible"""

    RECONSTRUCTION = 0

    @staticmethod
    def getProcessOrder():
        return _NabuProcessing.RECONSTRUCTION


class _NabuProcess(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent=parent)
        self.setLayout(qt.QGridLayout())
        self._stageCB = qt.QComboBox(parent=self)
        for stage in _NabuStages:
            self._stageCB.addItem(stage.value)

        self.layout().addWidget(qt.QLabel("stage:", self), 0, 0, 1, 1)
        self.layout().addWidget(self._stageCB, 0, 1, 1, 1)

        self._configurationWidget = _NabuConfiguration(parent=parent)
        self.layout().addWidget(self._configurationWidget, 1, 0, 2, 2)


class _NabuConfiguration(qt.QWidget):
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent=parent)
        self.setLayout(qt.QFormLayout)

    def filter(self, stage=None, process=None):
        """Apply a filter on the options to show

        :param stage:
        :param process:
        """
        pass

    def setStages(self, stages: dict) -> None:
        """

        :param stages: contains stages the user can edit and for each
                            stages the associated processes.
        """
        self.clear()
        for stage, processes in stages.items():
            self.addStage(stage=stage, processes=processes)

    def addStage(self, stage, processes):
        stage = _NabuStages(value=stage)
        for process in processes:
            _NabuStages.getProcessEnum(stage=stage)


class NabuDialog(qt.QDialog):
    sigComputationRequested = qt.Signal()
    """Signal emitted when a computation is requested"""

    def __init__(self, parent):
        qt.QDialog.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())

        self._widget = NabuWindow(self)
        self.layout().addWidget(self._widget)

        self._computePB = qt.QPushButton("compute", self)
        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.addButton(self._computePB, qt.QDialogButtonBox.ActionRole)
        self.layout().addWidget(self._buttons)

        # set up

        # expose API
        self.setOutputDir = self._widget.setOutputDir

    def setScan(self, scan):
        self._widget.setScan(scan)

    def getWidget(self):
        return self._widget

    def getConfiguration(self):
        return self._widget.getConfiguration()


class NabuWindow(qt.QMainWindow):
    sigConfigChanged = qt.Signal()
    """Signal emitted when the configuration change"""

    def __init__(self, parent, flow_direction="vertical"):
        qt.QMainWindow.__init__(self, parent=parent)
        self.setWindowFlags(qt.Qt.Widget)

        self._mainWidget = NabuTabWidget(parent=self, flow_direction=flow_direction)
        self.setCentralWidget(self._mainWidget)
        style = qt.QApplication.style()

        # add toolbar
        toolbar = qt.QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(qt.Qt.TopToolBarArea, toolbar)

        # add filtering
        self._filterAction = FilterAction(toolbar)
        toolbar.addAction(self._filterAction)
        self._filterAction.triggered.connect(self._filteringChanged)

        # add configuration mode
        self.__configurationModesAction = qt.QAction(self)
        self.__configurationModesAction.setCheckable(False)
        menu = qt.QMenu(self)
        self.__configurationModesAction.setMenu(menu)
        toolbar.addAction(self.__configurationModesAction)

        self.__configurationModesGroup = qt.QActionGroup(self)
        self.__configurationModesGroup.setExclusive(True)
        self.__configurationModesGroup.triggered.connect(self._userModeChanged)

        self._minimalisticAction = MinimalisticConfigurationAction(toolbar)
        menu.addAction(self._minimalisticAction)
        self.__configurationModesGroup.addAction(self._minimalisticAction)
        self._basicConfigAction = BasicConfigurationAction(toolbar)
        menu.addAction(self._basicConfigAction)
        self.__configurationModesGroup.addAction(self._basicConfigAction)
        self._expertConfiguration = ExpertConfigurationAction(toolbar)
        menu.addAction(self._expertConfiguration)
        self.__configurationModesGroup.addAction(self._expertConfiguration)

        # add load option
        self.__loadAction = qt.QAction(self)
        self.__loadAction.setToolTip("load nabu configuration from a text file")
        # load_icon = style.standardIcon(qt.QStyle.SP_)
        load_icon = silx_icons.getQIcon("document-open")
        self.__loadAction.setIcon(load_icon)
        toolbar.addAction(self.__loadAction)
        self.__loadAction.triggered.connect(self._loadParameters)

        # add save option
        self.__saveAction = qt.QAction(self)
        self.__saveAction.setToolTip("save nabu configuration to a text file")
        save_icon = silx_icons.getQIcon("document-save")
        self.__saveAction.setIcon(save_icon)
        toolbar.addAction(self.__saveAction)
        self.__saveAction.triggered.connect(self._saveParameters)

        # reset configuration option
        self.__resetAction = qt.QAction(self)
        self.__resetAction.setToolTip("reset nabu configuration")
        reset_icon = style.standardIcon(qt.QStyle.SP_DialogResetButton)
        self.__resetAction.setIcon(reset_icon)
        toolbar.addAction(self.__resetAction)
        self.__resetAction.triggered.connect(self._resetParameters)

        # toolbar spacer
        self.__tSpacer = qt.QWidget(toolbar)
        self.__tSpacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Preferred)
        toolbar.addWidget(self.__tSpacer)

        # connect signal / slot
        self._mainWidget.sigConfigChanged.connect(self.sigConfigChanged)

        # set up
        self._resetParameters()
        self._filterAction.setChecked(True)
        self._basicConfigAction.setChecked(True)
        self._userModeChanged()

    def getConfiguration(self):
        configuration = self._mainWidget.getConfiguration()
        assert (
            "configuration_level" not in configuration
        ), "configuration_level is a reserved key"
        configuration["configuration_level"] = self.getConfigurationLevel().value
        configuration["mode_locked"] = self.isModeLocked()
        return configuration

    def setConfiguration(self, config):
        conf = config.copy()
        if "configuration_level" in conf:
            configuration_level = conf["configuration_level"]
            del conf["configuration_level"]
        else:
            configuration_level = None
        modeLocked = conf.get("mode_locked", None)
        if modeLocked is not None:
            self.setModeLocked(modeLocked)
        self._mainWidget.setConfiguration(conf)
        if configuration_level is not None:
            self.setConfigurationLevel(level=configuration_level)

    def _saveParameters(self):
        from nabu.pipeline.config import generate_nabu_configfile

        from tomwer.core.process.reconstruction.nabu.nabuslices import (
            interpret_tomwer_configuration,
        )

        # request output file
        config = interpret_tomwer_configuration(
            config=self.getConfiguration(), scan=None
        )
        if len(config) == 0:
            return
        elif len(config) > 1:
            _logger.warning(
                "You requested several paganin values." "Only one will be saved"
            )
        config = config[0][0]
        fname = self.askForNabuconfigFile()
        if fname is None:
            return
        generate_nabu_configfile(
            fname,
            nabu_fullfield_default_config,
            config=config,
            options_level="advanced",
        )

    def _resetParameters(self):
        # reset nabu settings
        default_config = get_default_nabu_config(nabu_fullfield_default_config)
        self._mainWidget.nabuSettingsWidget._configuration._preProcessingWidget._sinoRingsOpts.resetConfiguration()
        default_config["tomwer_slices"] = "middle"
        default_config["preproc"]["ccd_filter_enabled"] = False
        default_config["preproc"]["double_flatfield"] = False
        default_config["preproc"]["flatfield"] = True
        default_config["preproc"]["take_logarithm"] = True
        self.setConfiguration(default_config)

    def _loadParameters(self):
        inputFile = self.askForNabuconfigFile(acceptMode=qt.QFileDialog.AcceptOpen)
        import os

        if inputFile and os.path.exists(inputFile):
            from nabu.pipeline.config import parse_nabu_config_file

            config = parse_nabu_config_file(inputFile)
            self.setConfiguration(config)

    def askForNabuconfigFile(  # pragma: no cover
        self, acceptMode=qt.QFileDialog.AcceptSave
    ):
        dialog = qt.QFileDialog(self)
        dialog.setNameFilters(
            [
                "Configuration files (*.cfg *.conf *.config)",
                "Any files (*)",
            ]
        )

        dialog.setAcceptMode(acceptMode)
        dialog.setFileMode(qt.QFileDialog.AnyFile)

        if not dialog.exec_():
            dialog.close()
            return

        filesSelected = dialog.selectedFiles()
        if filesSelected is not None and len(filesSelected) > 0:
            output = filesSelected[0]
            if not output.endswith((".cfg", ".conf", ".config")):
                output = f"{output}.conf"
            return output

    def _userModeChanged(self, *args, **kwargs):
        selectedAction = self.__configurationModesGroup.checkedAction()
        self.__configurationModesAction.setIcon(selectedAction.icon())
        self.__configurationModesAction.setToolTip(selectedAction.tooltip())
        self._mainWidget.setConfigurationLevel(self.getConfigurationLevel())
        self.sigConfigChanged.emit()

    def _filteringChanged(self, *args, **kwargs):
        self._mainWidget.setFilteringActive(self.isFilteringActive())

    def isFilteringActive(self):
        return self._filterAction.isChecked()

    def setConfigurationLevel(self, level):
        level = ConfigurationLevel(level)
        if level == ConfigurationLevel.REQUIRED:
            self._minimalisticAction.setChecked(True)
        elif level == ConfigurationLevel.ADVANCED:
            self._expertConfiguration.setChecked(True)
        elif level == ConfigurationLevel.OPTIONAL:
            self._basicConfigAction.setChecked(True)
        else:
            raise ValueError("Level not recognize")
        self._userModeChanged()

    def getConfigurationLevel(self):
        if self._basicConfigAction.isChecked():
            return ConfigurationLevel.OPTIONAL
        elif self._expertConfiguration.isChecked():
            return ConfigurationLevel.ADVANCED
        elif self._minimalisticAction.isChecked():
            return ConfigurationLevel.REQUIRED
        else:
            raise ValueError("Level not recognize")

    # expose API

    def setModeLocked(self, locked: bool):
        self._mainWidget.nabuSettingsWidget.setModeLocked(locked)

    def isModeLocked(self):
        return self._mainWidget.nabuSettingsWidget.isModeLocked()

    def setOutputDir(self, dir: str):
        self._mainWidget.nabuSettingsWidget.setOutputDir(dir=dir)

    def setScan(self, scan: TomwerScanBase):
        self._mainWidget.nabuSettingsWidget.setScan(scan=scan)

    def getMode(self):
        return self._mainWidget.nabuSettingsWidget.getMode()

    def setMode(self, mode):
        self._mainWidget.nabuSettingsWidget.setMode(mode=mode)

    def hideSlicesInterface(self):
        self._mainWidget.nabuSettingsWidget.hideSlicesInterface()

    def hidePaganinInterface(self):
        self._mainWidget.nabuSettingsWidget.hidePaganinInterface()


class NabuWidget(qt.QWidget):
    """
    Widget containing the entire gui for nabu (control flow + parameters
    settings)
    """

    sigConfigChanged = qt.Signal()
    """Signal emitted when the configuration change"""

    def __init__(self, parent, flow_direction="vertical"):
        qt.QWidget.__init__(self, parent=parent)
        flow_direction = FlowDirection(flow_direction)
        self.setLayout(qt.QGridLayout())
        self._filteringActive = True
        self._configuration_level = ConfigurationLevel.OPTIONAL

        # reconstruction type
        self._widget_recons = qt.QWidget(parent=self)
        self._widget_recons.setLayout(qt.QHBoxLayout())
        self._modeLabel = qt.QLabel("mode:")
        self._widget_recons.layout().addWidget(self._modeLabel)
        self._nabuModeCB = qt.QComboBox(parent=self)
        for mode in _NabuMode:
            self._nabuModeCB.addItem(mode.value)
        self._widget_recons.layout().addWidget(self._nabuModeCB)
        self.layout().addWidget(self._widget_recons, 0, 1, 1, 2)
        # mode lock button
        self._lockModeButton = PadlockButton(parent=self)
        self._lockModeButton.setToolTip(
            "mode can be deduced automatically from the dataset "
            "if it contains information on Field of view. "
            "If you want to enforce the mode you can lock it. "
            "This way automatic deduction will be ignored."
        )
        self._lockModeButton.setMaximumWidth(30)
        self._widget_recons.layout().addWidget(self._lockModeButton)

        # spacer
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.layout().addWidget(spacer, 1, 8, 1, 1)

        # flow
        self._flow = NabuFlowArea(parent=self, direction=flow_direction)
        self._flow.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum)
        self.layout().addWidget(self._flow, 1, 1, 5, 1)

        # nabu configuration
        self._configurationScrollArea = qt.QScrollArea(self)
        self._configurationScrollArea.setWidgetResizable(True)
        self._configuration = NabuConfiguration(parent=self)
        self._configurationScrollArea.setWidget(self._configuration)
        self._configurationScrollArea.setHorizontalScrollBarPolicy(
            qt.Qt.ScrollBarAlwaysOff
        )
        self.layout().addWidget(self._configurationScrollArea, 1, 2, 5, 1)
        self._configuration.setSizePolicy(
            qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum
        )
        self._configurationScrollArea.setSizePolicy(
            qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum
        )

        # expose API
        self.setIniProcessing = self._flow.setIniProcessing
        self.setPreProcessing = self._flow.setPreProcessing
        self.setPhaseProcessing = self._flow.setPhaseProcessing
        self.setProcessing = self._flow.setProcessing
        self.setPostProcessing = self._flow.setPostProcessing

        self.setOutputDir = self._configuration.setOutputDir
        self.getActiveProcess = self._flow.getProcessFocused

        # set up
        pre_processing = ("pre processing",)
        roman_one_icon = tomwer_icons.getQIcon("roman_one")
        self.setPreProcessing(pre_processing, icons=(roman_one_icon,))
        phase_processing = ("phase",)
        roman_two_icon = tomwer_icons.getQIcon("roman_two")
        phase_icons = (roman_two_icon,)
        self.setPhaseProcessing(phase_processing, icons=phase_icons)
        processing = ("reconstruction",)
        processing_icons = (tomwer_icons.getQIcon("roman_three"),)
        self.setProcessing(processes=processing, icons=processing_icons)
        post_processing = ("save",)
        post_processing_icons = (tomwer_icons.getQIcon("roman_four"),)
        self.setPostProcessing(post_processing, icons=post_processing_icons)
        index_mode = self._nabuModeCB.findText(_NabuMode.FULL_FIELD.value)
        assert index_mode >= 0, "full filed should be registered in the widget"
        self._nabuModeCB.setCurrentIndex(index_mode)
        self._flow.setMaximumWidth(240)

        # signal / slot connections
        self._flow.sigConfigurationChanged.connect(self._processSelectionChanged)
        self._flow.sigResetConfiguration.connect(self._processSelectionChanged)
        self._configuration.sigConfChanged.connect(self._triggerConfigChanged)
        self._nabuModeCB.currentIndexChanged.connect(self._triggerConfigChanged)

    def _triggerConfigChanged(self, *args, **kwargs):
        self.sigConfigChanged.emit()

    def isModeLocked(self) -> True:
        """
        Return True if the mode is locked (in this case there is no automatic detection of it)
        """
        return self._lockModeButton.isLocked()

    def setModeLocked(self, locked: bool):
        if not isinstance(locked, bool):
            raise TypeError(f"locked is expeced to be a bool not {type(locked)}")
        self._lockModeButton.setLock(locked)

    def setScan(self, scan):
        """Tune the configuration from scan information if possible"""
        assert isinstance(scan, TomwerScanBase)
        if scan.field_of_view is not None and not self.isModeLocked():
            if scan.field_of_view == FOV.FULL:
                self.setMode(_NabuMode.FULL_FIELD)
            elif scan.field_of_view == FOV.HALF:
                self.setMode(_NabuMode.HALF_ACQ)
        if scan.sa_delta_beta_params is not None:
            db = scan.sa_delta_beta_params.selected_delta_beta_value
            if db is not None:
                self.setDeltaBetaValue(db)

    def getConfiguration(self):
        conf = self._configuration.getConfiguration()
        enable_ht = int(self.getMode() is _NabuMode.HALF_ACQ)
        conf["reconstruction"]["enable_halftomo"] = enable_ht
        return conf

    def setConfiguration(self, config):
        if "reconstruction" in config and "enable_halftomo" in config["reconstruction"]:
            if config["reconstruction"]["enable_halftomo"] == 1:
                index = self._nabuModeCB.findText(_NabuMode.HALF_ACQ.value)
            else:
                index = self._nabuModeCB.findText(_NabuMode.FULL_FIELD.value)
            self._nabuModeCB.setCurrentIndex(index)
        self._configuration.setConfiguration(config=config)

    def setDeltaBetaValue(self, value):
        self._configuration.setDeltaBetaValue(value=value)

    def hideSlicesInterface(self):
        self._configuration.hideSlicesInterface()

    def hidePaganinInterface(self):
        self._configuration.hidePaganinInterface()

    def getMode(self):
        return _NabuMode(self._nabuModeCB.currentText())

    def setMode(self, mode):
        mode = _NabuMode(mode)
        idx = self._nabuModeCB.findText(mode.value)
        self._nabuModeCB.setCurrentIndex(idx)

    def _processSelectionChanged(self, *arg):
        if self.isConfigFiltered():
            self.updateConfigurationFilter()

    def isConfigFiltered(self):
        return self._filteringActive

    def updateConfigurationFilter(self, *args, **kwargs):
        if self.isConfigFiltered():
            stage, option = self.getActiveProcess()
        else:
            stage = None
            option = None
        self._configuration.applyFilter(stage=stage, option=option)
        self._configuration.setConfigurationLevel(self.getConfigurationLevel())
        # force scroll bar to update
        self._configurationScrollArea.updateGeometry()

    def setConfigurationLevel(self, level):
        level = ConfigurationLevel(level)
        self._configuration_level = level
        self.updateConfigurationFilter()

    def getConfigurationLevel(self):
        return self._configuration_level

    def setFilteringActive(self, active):
        self._filteringActive = active
        self.updateConfigurationFilter()


class NabuTabWidget(qt.QTabWidget):
    """
    Widget that group Nabu reconstruction settings and (local) platform settings
    """

    sigConfigChanged = qt.Signal()

    def __init__(self, parent=None, flow_direction: str = "vertical"):
        super().__init__(parent=parent)
        self._nabuSettingsWidget = NabuWidget(
            parent=self, flow_direction=flow_direction
        )
        self.addTab(self._nabuSettingsWidget, "reconstruction settings")
        self._platformSettingsWidget = NabuPlatformSettings(parent=self)
        self.addTab(self._platformSettingsWidget, TAB_LABEL_PLATFORM_SETTINGS)

        # connect signal / slot
        self._nabuSettingsWidget.sigConfigChanged.connect(self.sigConfigChanged)
        self._platformSettingsWidget.sigConfigChanged.connect(self.sigConfigChanged)

    def getConfiguration(self) -> dict:
        config = self._nabuSettingsWidget.getConfiguration()
        config = concatenate_dict(
            config, self._platformSettingsWidget.getConfiguration()
        )
        return config

    def setConfiguration(self, config: dict):
        self._nabuSettingsWidget.setConfiguration(config=config)
        self._platformSettingsWidget.setConfiguration(config=config)

    def setConfigurationLevel(self, level):
        self._nabuSettingsWidget.setConfigurationLevel(level=level)
        self._platformSettingsWidget.setConfigurationLevel(level=level)

    def getConfigurationLevel(self):
        return self._nabuSettingsWidget.getConfigurationLevel()

    @property
    def nabuSettingsWidget(self):
        return self._nabuSettingsWidget

    @property
    def platformSettings(self):
        return self._platformSettingsWidget
