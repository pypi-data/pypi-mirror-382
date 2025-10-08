import os
import mosamatic2.constants as constants
from PySide6.QtWidgets import (
    QMainWindow,
)
from PySide6.QtGui import (
    QGuiApplication,
    QAction,
    QIcon,
)
from PySide6.QtCore import Qt, QByteArray
from mosamatic2.ui.utils import version, resource_path, is_macos
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.ui.settings import Settings
from mosamatic2.ui.widgets.panels.mainpanel import MainPanel
from mosamatic2.ui.widgets.panels.logpanel import LogPanel
from mosamatic2.ui.widgets.panels.tasks.rescaledicomimagestaskpanel import RescaleDicomImagesTaskPanel
from mosamatic2.ui.widgets.panels.tasks.segmentmusclefatl3tensorflowtaskpanel import SegmentMuscleFatL3TensorFlowTaskPanel
from mosamatic2.ui.widgets.panels.tasks.createpngsfromsegmentationstaskpanel import CreatePngsFromSegmentationsTaskPanel
from mosamatic2.ui.widgets.panels.tasks.calculatescorestaskpanel import CalculateScoresTaskPanel
from mosamatic2.ui.widgets.panels.tasks.dicom2niftitaskpanel import Dicom2NiftiTaskPanel
from mosamatic2.ui.widgets.panels.tasks.createdicomsummarytaskpanel import CreateDicomSummaryTaskPanel
from mosamatic2.ui.widgets.panels.tasks.selectslicefromscanstaskpanel import SelectSliceFromScansTaskPanel
from mosamatic2.ui.widgets.panels.tasks.totalsegmentatortaskpanel import TotalSegmentatorTaskPanel
from mosamatic2.ui.widgets.panels.tasks.calculatemaskstatisticstaskpanel import CalculateMaskStatisticsTaskPanel
from mosamatic2.ui.widgets.panels.pipelines.defaultpipelinepanel import DefaultPipelinePanel
from mosamatic2.ui.widgets.panels.pipelines.defaultdockerpipelinepanel import DefaultDockerPipelinePanel
from mosamatic2.ui.widgets.panels.pipelines.boadockerpipelinepanel import BoaDockerPipelinePanel
from mosamatic2.ui.widgets.panels.pipelines.liveranalysispipelinepanel import LiverAnalysisPipelinePanel
from mosamatic2.ui.widgets.panels.visualizations.slicevisualization.slicevisualization import SliceVisualization

LOG = LogManager()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self._settings = None
        self._main_panel = None
        self._log_panel = None
        self._decompress_dicom_files_task_panel = None
        self._rescale_dicom_images_task_panel = None
        self._segment_muscle_fat_l3_tensorflow_task_panel = None
        self._create_pngs_from_segmentations_task_panel = None
        self._calculate_scores_task_panel = None
        self._dicom2nifti_task_panel = None
        self._create_dicom_summary_task_panel = None
        self._select_slice_from_scans_task_panel = None
        self._total_segmentator_task_panel = None
        self._calculate_mask_statistics_task_panel = None
        self._default_pipeline_panel = None
        self._default_docker_pipeline_panel = None
        self._boa_docker_pipeline_panel = None
        self._liver_analysis_pipeline_panel = None
        self._slice_visualization = None
        self.init_window()

    def init_window(self):
        self.setWindowTitle(f'{constants.MOSAMATIC2_WINDOW_TITLE} {version()}')
        icon_file_name = constants.MOSAMATIC2_APP_ICON_FILE_NAME_MAC if is_macos() else constants.MOSAMATIC2_APP_ICON_FILE_NAME_WIN
        icon_path = resource_path(os.path.join(constants.MOSAMATIC2_ICONS_DIR_PATH, icon_file_name))
        self.setWindowIcon(QIcon(icon_path))
        if not self.load_geometry_and_state():
            self.set_default_size_and_position()
        self.init_menus()
        self.init_status_bar()
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.main_panel())
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_panel())

    def init_menus(self):
        self.init_app_menu()
        self.init_tasks_menu()
        self.init_pipelines_menu()
        self.init_visualizations_menu()
        if is_macos():            
            self.menuBar().setNativeMenuBar(False)

    def init_app_menu(self):
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        app_menu = self.menuBar().addMenu('Application')
        app_menu.addAction(exit_action)

    def init_tasks_menu(self):
        rescale_dicom_images_task_action = QAction('RescaleDicomImagesTask', self)
        rescale_dicom_images_task_action.triggered.connect(self.handle_rescale_dicom_images_task_action)
        segment_muscle_fat_l3_tensorflow_task_action = QAction('SegmentMuscleAndFatTask (TensorFlow)', self)
        segment_muscle_fat_l3_tensorflow_task_action.triggered.connect(self.handle_segment_muscle_fat_l3_tensorflow_task_action)
        calculate_scores_task_action = QAction('CalculateScoresTask', self)
        calculate_scores_task_action.triggered.connect(self.handle_calculate_scores_task_action)
        create_pngs_from_segmentations_task_action = QAction('CreatePngsFromSegmentationsTask', self)
        create_pngs_from_segmentations_task_action.triggered.connect(self.handle_create_pngs_from_segmentations_task_action)
        dicom2nifti_task_action = QAction('Dicom2NiftiTask', self)
        dicom2nifti_task_action.triggered.connect(self.handle_dicom2nifti_task_action)
        create_dicom_summary_task_action = QAction('CreateDicomSummaryTask', self)
        create_dicom_summary_task_action.triggered.connect(self.handle_create_dicom_summary_task_action)
        select_slice_from_scans_task_action = QAction('SelectSliceFromScansTask', self)
        select_slice_from_scans_task_action.triggered.connect(self.handle_select_slice_from_scans_task_action)
        total_segmentator_task_action = QAction('TotalSegmentatorTask', self)
        total_segmentator_task_action.triggered.connect(self.handle_total_segmentator_task_action)
        calculate_mask_statistics_task_action = QAction('CalculateMaskStatisticsTask', self)
        calculate_mask_statistics_task_action.triggered.connect(self.handle_calculate_mask_statistics_task_action)
        tasks_menu = self.menuBar().addMenu('Tasks')
        tasks_menu.addAction(rescale_dicom_images_task_action)
        tasks_menu.addAction(segment_muscle_fat_l3_tensorflow_task_action)
        tasks_menu.addAction(calculate_scores_task_action)
        tasks_menu.addAction(create_pngs_from_segmentations_task_action)
        tasks_menu.addAction(dicom2nifti_task_action)
        tasks_menu.addAction(create_dicom_summary_task_action)
        tasks_menu.addAction(select_slice_from_scans_task_action)
        tasks_menu.addAction(total_segmentator_task_action)
        tasks_menu.addAction(calculate_mask_statistics_task_action)

    def init_pipelines_menu(self):
        default_pipeline_action = QAction('DefaultPipeline', self)
        default_pipeline_action.triggered.connect(self.handle_default_pipeline_action)
        default_docker_pipeline_action = QAction('DefaultDockerPipeline', self)
        default_docker_pipeline_action.triggered.connect(self.handle_default_docker_pipeline_action)
        boa_docker_pipeline_action = QAction('BoaDockerPipeline', self)
        boa_docker_pipeline_action.triggered.connect(self.handle_boa_docker_pipeline_action)
        liver_analysis_pipeline_action = QAction('LiverAnalysisPipeline', self)
        liver_analysis_pipeline_action.triggered.connect(self.handle_liver_analysis_pipeline_action)
        pipelines_menu = self.menuBar().addMenu('Pipelines')
        pipelines_menu.addAction(default_pipeline_action)
        pipelines_menu.addAction(default_docker_pipeline_action)
        pipelines_menu.addAction(boa_docker_pipeline_action)
        pipelines_menu.addAction(liver_analysis_pipeline_action)

    def init_visualizations_menu(self):
        slice_visualization_action = QAction('SliceVisualization', self)
        slice_visualization_action.triggered.connect(self.handle_slice_visualization_action)
        visualizations_menu = self.menuBar().addMenu('Visualizations')
        visualizations_menu.addAction(slice_visualization_action)

    def init_status_bar(self):
        self.set_status('Ready')

    # GET

    def settings(self):
        if not self._settings:
            self._settings = Settings()
        return self._settings

    def main_panel(self):
        if not self._main_panel:
            self._main_panel = MainPanel(self)
            self._main_panel.add_panel(self.rescale_dicom_images_task_panel(), 'rescaledicomimagestaskpanel')
            self._main_panel.add_panel(self.segment_muscle_fat_l3_tensorflow_task_panel(), 'segmentmusclefatl3tensorflowtaskpanel')
            self._main_panel.add_panel(self.create_pngs_from_segmentations_task_panel(), 'createpngsfromsegmentationstaskpanel')
            self._main_panel.add_panel(self.calculate_scores_task_panel(), 'calculatescorestaskpanel')
            self._main_panel.add_panel(self.dicom2nifti_task_panel(), 'dicom2niftitaskpanel')
            self._main_panel.add_panel(self.create_dicom_summary_task_panel(), 'createdicomsummarytaskpanel')
            self._main_panel.add_panel(self.select_slice_from_scans_task_panel(), 'selectslicefromscanstaskpanel')
            self._main_panel.add_panel(self.total_segmentator_task_panel(), 'totalsegmentatortaskpanel')
            self._main_panel.add_panel(self.calculate_mask_statistics_task_panel(), 'calculatemaskstatisticstaskpanel')
            self._main_panel.add_panel(self.default_pipeline_panel(), 'defaultpipelinepanel')
            self._main_panel.add_panel(self.default_docker_pipeline_panel(), 'defaultdockerpipelinepanel')
            self._main_panel.add_panel(self.boa_docker_pipeline_panel(), 'boadockerpipelinepanel')
            self._main_panel.add_panel(self.liver_analysis_pipeline_panel(), 'liveranalysispipelinepanel')
            self._main_panel.add_panel(self.slice_visualization(), 'slicevisualization')
            self._main_panel.select_panel('defaultpipelinepanel')
        return self._main_panel
    
    def log_panel(self):
        if not self._log_panel:
            self._log_panel = LogPanel()
            LOG.add_listener(self._log_panel)
        return self._log_panel

    # MISCELLANEOUS

    def rescale_dicom_images_task_panel(self):
        if not self._rescale_dicom_images_task_panel:
            self._rescale_dicom_images_task_panel = RescaleDicomImagesTaskPanel()
        return self._rescale_dicom_images_task_panel
    
    def segment_muscle_fat_l3_tensorflow_task_panel(self):
        if not self._segment_muscle_fat_l3_tensorflow_task_panel:
            self._segment_muscle_fat_l3_tensorflow_task_panel = SegmentMuscleFatL3TensorFlowTaskPanel()
        return self._segment_muscle_fat_l3_tensorflow_task_panel

    def create_pngs_from_segmentations_task_panel(self):
        if not self._create_pngs_from_segmentations_task_panel:
            self._create_pngs_from_segmentations_task_panel = CreatePngsFromSegmentationsTaskPanel()
        return self._create_pngs_from_segmentations_task_panel
    
    def calculate_scores_task_panel(self):
        if not self._calculate_scores_task_panel:
            self._calculate_scores_task_panel = CalculateScoresTaskPanel()
        return self._calculate_scores_task_panel
    
    def dicom2nifti_task_panel(self):
        if not self._dicom2nifti_task_panel:
            self._dicom2nifti_task_panel = Dicom2NiftiTaskPanel()
        return self._dicom2nifti_task_panel
    
    def create_dicom_summary_task_panel(self):
        if not self._create_dicom_summary_task_panel:
            self._create_dicom_summary_task_panel = CreateDicomSummaryTaskPanel()
        return self._create_dicom_summary_task_panel

    def select_slice_from_scans_task_panel(self):
        if not self._select_slice_from_scans_task_panel:
            self._select_slice_from_scans_task_panel = SelectSliceFromScansTaskPanel()
        return self._select_slice_from_scans_task_panel

    def total_segmentator_task_panel(self):
        if not self._total_segmentator_task_panel:
            self._total_segmentator_task_panel = TotalSegmentatorTaskPanel()
        return self._total_segmentator_task_panel
    
    def calculate_mask_statistics_task_panel(self):
        if not self._calculate_mask_statistics_task_panel:
            self._calculate_mask_statistics_task_panel = CalculateMaskStatisticsTaskPanel()
        return self._calculate_mask_statistics_task_panel
    
    def default_pipeline_panel(self):
        if not self._default_pipeline_panel:
            self._default_pipeline_panel = DefaultPipelinePanel()
        return self._default_pipeline_panel

    def default_docker_pipeline_panel(self):
        if not self._default_docker_pipeline_panel:
            self._default_docker_pipeline_panel = DefaultDockerPipelinePanel()
        return self._default_docker_pipeline_panel

    def boa_docker_pipeline_panel(self):
        if not self._boa_docker_pipeline_panel:
            self._boa_docker_pipeline_panel = BoaDockerPipelinePanel()
        return self._boa_docker_pipeline_panel
    
    def liver_analysis_pipeline_panel(self):
        if not self._liver_analysis_pipeline_panel:
            self._liver_analysis_pipeline_panel = LiverAnalysisPipelinePanel()
        return self._liver_analysis_pipeline_panel
    
    def slice_visualization(self):
        if not self._slice_visualization:
            self._slice_visualization = SliceVisualization()
        return self._slice_visualization

    # SETTERS

    def set_status(self, message):
        self.statusBar().showMessage(message)

    # EVENT HANDLERS

    def handle_rescale_dicom_images_task_action(self):
        self.main_panel().select_panel('rescaledicomimagestaskpanel')

    def handle_segment_muscle_fat_l3_tensorflow_task_action(self):
        self.main_panel().select_panel('segmentmusclefatl3tensorflowtaskpanel')

    def handle_create_pngs_from_segmentations_task_action(self):
        self.main_panel().select_panel('createpngsfromsegmentationstaskpanel')

    def handle_calculate_scores_task_action(self):
        self.main_panel().select_panel('calculatescorestaskpanel')

    def handle_dicom2nifti_task_action(self):
        self.main_panel().select_panel('dicom2niftitaskpanel')

    def handle_create_dicom_summary_task_action(self):
        self.main_panel().select_panel('createdicomsummarytaskpanel')

    def handle_select_slice_from_scans_task_action(self):
        self.main_panel().select_panel('selectslicefromscanstaskpanel')

    def handle_total_segmentator_task_action(self):
        self.main_panel().select_panel('totalsegmentatortaskpanel')

    def handle_calculate_mask_statistics_task_action(self):
        self.main_panel().select_panel('calculatemaskstatisticstaskpanel')

    def handle_default_pipeline_action(self):
        self.main_panel().select_panel('defaultpipelinepanel')

    def handle_default_docker_pipeline_action(self):
        self.main_panel().select_panel('defaultdockerpipelinepanel')

    def handle_boa_docker_pipeline_action(self):
        self.main_panel().select_panel('boadockerpipelinepanel')

    def handle_liver_analysis_pipeline_action(self):
        self.main_panel().select_panel('liveranalysispipelinepanel')

    def handle_slice_visualization_action(self):
        self.main_panel().select_panel('slicevisualization')

    def showEvent(self, event):
        return super().showEvent(event)

    def closeEvent(self, event):
        self.save_geometry_and_state()
        # Save inputs and parameters of relevant panels
        self.rescale_dicom_images_task_panel().save_inputs_and_parameters()
        self.segment_muscle_fat_l3_tensorflow_task_panel().save_inputs_and_parameters()
        self.create_pngs_from_segmentations_task_panel().save_inputs_and_parameters()
        self.calculate_scores_task_panel().save_inputs_and_parameters()
        self.dicom2nifti_task_panel().save_inputs_and_parameters()
        self.create_dicom_summary_task_panel().save_inputs_and_parameters()
        self.select_slice_from_scans_task_panel().save_inputs_and_parameters()
        self.total_segmentator_task_panel().save_inputs_and_parameters()
        self.calculate_mask_statistics_task_panel().save_inputs_and_parameters()
        self.default_pipeline_panel().save_inputs_and_parameters()
        self.default_docker_pipeline_panel().save_inputs_and_parameters()
        self.boa_docker_pipeline_panel().save_inputs_and_parameters()
        self.liver_analysis_pipeline_panel().save_inputs_and_parameters()
        self.slice_visualization().save_inputs_and_parameters()
        return super().closeEvent(event)

    def load_geometry_and_state(self):
        geometry = self.settings().get(constants.MOSAMATIC2_WINDOW_GEOMETRY_KEY)
        state = self.settings().get(constants.MOSAMATIC2_WINDOW_STATE_KEY)
        if isinstance(geometry, QByteArray) and self.restoreGeometry(geometry):
            if isinstance(state, QByteArray):
                self.restoreState(state)
            return True
        return False

    def save_geometry_and_state(self):
        self.settings().set(constants.MOSAMATIC2_WINDOW_GEOMETRY_KEY, self.saveGeometry())
        self.settings().set(constants.MOSAMATIC2_WINDOW_STATE_KEY, self.saveState())

    def set_default_size_and_position(self):
        self.resize(constants.MOSAMATIC2_WINDOW_W, constants.MOSAMATIC2_WINDOW_H)
        self.center_window()

    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.geometry().width()) / 2
        y = (screen.height() - self.geometry().height()) / 2
        self.move(int(x), int(y))