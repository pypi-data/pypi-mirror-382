from PySide6.QtWidgets import QGraphicsScene

from storage3d import Storage3D


class CurveScene(QGraphicsScene):

    def __init__(self, size, w, parent=None):
        super().__init__(parent=parent)
        self.storage = Storage3D(self)
        self.corners = [None for _ in range(8)]
        self.size = size
        self.w = w
        self.storage.create_grid()
        self.setSceneRect(-w/2, -w/2, w, w)

    def remove_all_corners(self):
        self.corners = [None for _ in range(8)]

    def replace_corner(self, grid_corner, index):
        self.corners[index] = grid_corner

    def update_grid_scale(self):
        self.size = 8 * self.parent().get_parameters()['gs']
        self.w = self.parent().get_parameters()['gs']

    def get_storage(self):
        return self.storage

    def get_corners(self):
        return self.corners

    def get_w(self):
        return self.w

    def get_size(self):
        return self.size
