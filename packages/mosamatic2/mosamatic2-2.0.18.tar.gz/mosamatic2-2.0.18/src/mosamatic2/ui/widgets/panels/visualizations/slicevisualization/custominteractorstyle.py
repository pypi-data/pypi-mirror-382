import vtk


class CustomInteractorStyle(vtk.vtkInteractorStyleImage):
    def __init__(self, image_data, slice_mapper, status_actor, slice_obj, orientation="axial"):
        super(CustomInteractorStyle, self).__init__()
        self.AddObserver("MouseWheelForwardEvent", self.move_slice_forward)
        self.AddObserver("MouseWheelBackwardEvent", self.move_slice_backward)
        self.AddObserver("MouseMoveEvent", self.update_overlay, 1.0)
        self.AddObserver("KeyPressEvent", self.key_press_event)

        self.image_data = image_data
        self.slice_mapper = slice_mapper
        self.status_actor = status_actor
        self.slice_obj = slice_obj
        self.orientation = orientation
        self._color_window = 0
        self._color_level = 0

        xmin, xmax, ymin, ymax, zmin, zmax = image_data.GetExtent()
        if orientation == "axial":
            self.min_slice, self.max_slice = zmin, zmax
        elif orientation == "sagittal":
            self.min_slice, self.max_slice = xmin, xmax
        elif orientation == "coronal":
            self.min_slice, self.max_slice = ymin, ymax
        else:
            raise ValueError(f"Unknown orientation: {orientation}")

        self.slice = (self.min_slice + self.max_slice) // 2
        self.slice_mapper.SetSliceNumber(self.slice)
        self.update_status_message()

    def color_window(self):
        return self._color_window

    def set_color_window(self, color_window):
        self._color_window = color_window
        self.slice_obj.GetProperty().SetColorWindow(self._color_window)
        self.GetInteractor().GetRenderWindow().Render()

    def color_level(self):
        return self._color_level

    def set_color_level(self, color_level):
        self._color_level = color_level
        self.slice_obj.GetProperty().SetColorLevel(self._color_level)
        self.GetInteractor().GetRenderWindow().Render()

    def update_status_message(self):
        window = int(self.slice_obj.GetProperty().GetColorWindow())
        level = int(self.slice_obj.GetProperty().GetColorLevel())
        message = f'Slice {self.slice + 1}/{self.max_slice + 1} | W: {window} L: {level}'
        self.status_actor.GetMapper().SetInput(message)

    def move_slice_forward(self, obj, event):
        if self.slice < self.max_slice:
            self.slice += 1
            self.slice_mapper.SetSliceNumber(self.slice)
            self.update_status_message()
            self.GetInteractor().GetRenderWindow().Render()

    def move_slice_backward(self, obj, event):
        if self.slice > self.min_slice:
            self.slice -= 1
            self.slice_mapper.SetSliceNumber(self.slice)
            self.update_status_message()
            self.GetInteractor().GetRenderWindow().Render()

    def key_press_event(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        if key == "Up":
            self.move_slice_forward(obj, event)
        elif key == "Down":
            self.move_slice_backward(obj, event)

    def update_overlay(self, obj, event):
        super(CustomInteractorStyle, self).OnMouseMove()
        self.update_status_message()
        self.GetInteractor().GetRenderWindow().Render()