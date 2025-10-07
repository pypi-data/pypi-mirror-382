from PySide6.QtWidgets import (
    QLineEdit,
    QLabel,
    QSpinBox,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QFileDialog,
)
from mosamatic2.ui.widgets.panels.visualizations.visualization import Visualization
from mosamatic2.ui.widgets.panels.visualizations.slicevisualization.sliceviewer import SliceViewer
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.ui.settings import Settings
from mosamatic2.ui.utils import is_macos

LOG = LogManager()
PANEL_TITLE = 'SliceVisualization'
PANEL_NAME = 'slicevisualization'


class SliceVisualization(Visualization):
    def __init__(self):
        super(SliceVisualization, self).__init__()
        self.set_title(PANEL_TITLE)
        self._image_line_edit = None
        self._image_select_button = None
        self._image_dir_select_button = None
        self._color_window_spinbox = None
        self._color_level_spinbox = None
        self._color_window_and_level_reset_button = None
        self._load_image_button = None
        self._slice_viewer = None
        self._form_layout = None
        self._settings = None
        self.init_layout()

    def image_line_edit(self):
        if not self._image_line_edit:
            self._image_line_edit = QLineEdit(self.settings().get(f'{PANEL_NAME}/image'))
        return self._image_line_edit
    
    def image_select_button(self):
        if not self._image_select_button:
            self._image_select_button = QPushButton('Select Image')
            self._image_select_button.clicked.connect(self.handle_image_select_button)
        return self._image_select_button
    
    def image_dir_select_button(self):
        if not self._image_dir_select_button:
            self._image_dir_select_button = QPushButton('Select Directory')
            self._image_dir_select_button.clicked.connect(self.handle_image_dir_select_button)
        return self._image_dir_select_button
    
    def color_window_spinbox(self):
        if not self._color_window_spinbox:
            self._color_window_spinbox = QSpinBox(self, minimum=0, maximum=1024, value=400)
        return self._color_window_spinbox
    
    def color_level_spinbox(self):
        if not self._color_level_spinbox:
            self._color_level_spinbox = QSpinBox(self, minimum=0, maximum=100, value=40)
        return self._color_level_spinbox
    
    def color_window_and_level_reset_button(self):
        if not self._color_window_and_level_reset_button:
            self._color_window_and_level_reset_button = QPushButton('Reset')
            self._color_window_and_level_reset_button.clicked.connect(self.handle_color_window_and_level_reset_button)
        return self._color_window_and_level_reset_button
    
    def load_image_button(self):
        if not self._load_image_button:
            self._load_image_button = QPushButton('Load')
            self._load_image_button.clicked.connect(self.handle_load_image_button)
        return self._load_image_button
    
    def slice_viewer(self):
        if not self._slice_viewer:
            self._slice_viewer = SliceViewer(
                color_window=self.color_window_spinbox().value(),
                color_level=self.color_level_spinbox().value(),
            )
        return self._slice_viewer

    def form_layout(self):
        if not self._form_layout:
            self._form_layout = QFormLayout()
            if is_macos():
                self._form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        return self._form_layout

    def settings(self):
        if not self._settings:
            self._settings = Settings()
        return self._settings

    def init_layout(self):
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_line_edit())
        image_layout.addWidget(self.image_select_button())
        image_layout.addWidget(self.image_dir_select_button())
        color_window_and_level_layout = QHBoxLayout()
        color_window_and_level_layout.addWidget(QLabel('Color window'))
        color_window_and_level_layout.addWidget(self.color_window_spinbox())
        color_window_and_level_layout.addWidget(QLabel('Color level'))
        color_window_and_level_layout.addWidget(self.color_level_spinbox())
        color_window_and_level_layout.addWidget(self.color_window_and_level_reset_button())
        self.form_layout().addRow('NIFTI file or DICOM directory', image_layout)
        self.form_layout().addRow('', color_window_and_level_layout)
        layout = QVBoxLayout()
        layout.addLayout(self.form_layout())
        layout.addWidget(self.load_image_button())
        layout.addWidget(self.slice_viewer())
        self.setLayout(layout)
        self.setObjectName(PANEL_NAME)

    def handle_image_select_button(self):
        last_directory = self.settings().get('last_directory')
        file_path, _ = QFileDialog.getOpenFileName(dir=last_directory)
        if file_path:
            self.image_line_edit().setText(file_path)
            self.settings().set('last_directory', file_path)

    def handle_image_dir_select_button(self):
        last_directory = self.settings().get('last_directory')
        dir_path = QFileDialog.getExistingDirectory(dir=last_directory)
        if dir_path:
            self.image_line_edit().setText(dir_path)
            self.settings().set('last_directory', dir_path)

    def handle_color_window_and_level_reset_button(self):
        self.slice_viewer().set_color_window(self.color_window_spinbox().value())
        self.slice_viewer().set_color_level(self.color_level_spinbox().value())

    def handle_load_image_button(self):
        self.slice_viewer().set_nifti_file_or_dicom_dir(self.image_line_edit().text())
        # self.slice_viewer().set_view_orientation('axial')
        self.slice_viewer().load_image()

    def save_inputs_and_parameters(self):
        self.settings().set(f'{PANEL_NAME}/image', self.image_line_edit().text())