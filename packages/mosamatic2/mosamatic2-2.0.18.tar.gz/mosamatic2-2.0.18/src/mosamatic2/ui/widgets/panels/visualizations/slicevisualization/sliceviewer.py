import os
import vtk
import pydicom
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from mosamatic2.ui.widgets.panels.visualizations.slicevisualization.custominteractorstyle import CustomInteractorStyle
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

COLOR_WINDOW = 400
COLOR_LEVEL = 40
IMAGE_SHIFT_SCALE = -1000


class SliceViewer(QWidget):
    def __init__(self, color_window=COLOR_WINDOW, color_level=COLOR_LEVEL):
        super(SliceViewer, self).__init__()
        self._nifti_file_or_dicom_dir = None
        self._view_orientation = 'axial'
        self._color_window = color_window
        self._color_level = color_level
        self._vtk_widget = QVTKRenderWindowInteractor(self)
        self._render_window = self._vtk_widget.GetRenderWindow()
        self._interactor = self._render_window.GetInteractor()
        self._interactor_style = None
        layout = QVBoxLayout()
        layout.addWidget(self._vtk_widget)
        self.setLayout(layout)
        self._default_renderer = vtk.vtkRenderer()
        self._default_renderer.SetBackground(0.0, 0.0, 0.0)  # black
        self._render_window.AddRenderer(self._default_renderer)
        self._render_window.Render()

    def color_window(self):
        return self._color_window

    def set_color_window(self, color_window):
        self._color_window = color_window
        if self._interactor_style:
            self._interactor_style.set_color_window(self._color_window)

    def color_level(self):
        return self._color_level

    def set_color_level(self, color_level):
        self._color_level = color_level
        if self._interactor_style:
            self._interactor_style.set_color_level(self._color_level)

    def nifti_file_or_dicom_dir(self):
        return self._nifti_file_or_dicom_dir
    
    def set_nifti_file_or_dicom_dir(self, nifti_file_or_dicom_dir):
        self._nifti_file_or_dicom_dir = nifti_file_or_dicom_dir

    def create_text_actor(self, text, x, y, font_size, align_bottom=False, normalized=False):
        text_prop = vtk.vtkTextProperty()
        text_prop.SetFontFamilyToCourier()
        text_prop.SetFontSize(font_size)
        text_prop.SetVerticalJustificationToBottom() if align_bottom else text_prop.SetVerticalJustificationToTop()
        text_prop.SetJustificationToLeft()
        text_mapper = vtk.vtkTextMapper()
        text_mapper.SetInput(text)
        text_mapper.SetTextProperty(text_prop)
        text_actor = vtk.vtkActor2D()
        text_actor.SetMapper(text_mapper)
        if normalized:
            text_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        text_actor.SetPosition(x, y)
        return text_actor
    
    def is_nifti_file(self, file_path):
        return file_path.endswith('.nii') or file_path.endswith('.nii.gz')
    
    def is_dicom_dir(self, dir_path):
        first_dicom_file = os.path.join(dir_path, os.listdir(dir_path)[0])
        return pydicom.dcmread(first_dicom_file, stop_before_pixels=True)

    def load_image(self):
        if not self.nifti_file_or_dicom_dir():
            QMessageBox.warning(self, 'Warning', 'No NIFTI file or DICOM directory set')
            return
        if self.is_nifti_file(self.nifti_file_or_dicom_dir()):
            reader = vtk.vtkNIFTIImageReader()
            reader.SetFileName(self.nifti_file_or_dicom_dir())
        elif self.is_dicom_dir(self.nifti_file_or_dicom_dir()):
            reader = vtk.vtkDICOMImageReader()
            reader.SetDirectoryName(self.nifti_file_or_dicom_dir())
        reader.Update()
        image_data = reader.GetOutput()
        xmin, xmax, ymin, ymax, zmin, zmax = image_data.GetExtent()
        axial_index = (zmin + zmax) // 2
        slice_mapper = vtk.vtkImageSliceMapper()
        slice_mapper.SetInputData(image_data)
        slice_mapper.SetOrientationToZ()  # axial orientation
        slice_mapper.SetSliceNumber(axial_index)
        slice = vtk.vtkImageSlice()
        slice.GetProperty().SetColorWindow(self.color_window())
        slice.GetProperty().SetColorLevel(self.color_level())
        slice.SetMapper(slice_mapper)
        slice_text_actor = self.create_text_actor("", 0.01, 0.01, 12, align_bottom=True, normalized=True)
        usage_text_actor = self.create_text_actor(
            "- Slice with mouse wheel or Up/Down keys (first click inside viewer)\n"
            "- Zoom with pressed right mouse button while dragging\n"
            "- Pan with Shift key and left mouse button while dragging\n"
            "- Change contrast/brightness with pressed left mouse while dragging",
            0.01, 0.99, 12, normalized=True)
        ren = vtk.vtkRenderer()
        ren.AddActor2D(slice_text_actor)
        ren.AddActor2D(usage_text_actor)
        ren.AddViewProp(slice)
        ren.ResetCamera()
        self._render_window.RemoveRenderer(self._default_renderer)
        self._render_window.AddRenderer(ren)
        self._interactor_style = CustomInteractorStyle(image_data, slice_mapper, slice_text_actor, slice)
        self._interactor.SetInteractorStyle(self._interactor_style)
        self._interactor.Initialize()
        self._render_window.Render()