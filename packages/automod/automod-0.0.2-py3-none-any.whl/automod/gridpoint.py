import numpy as np

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QPainterPath, QColor, QPen
from PySide6.QtWidgets import QGraphicsItem


class GridPoint(QGraphicsItem):

    def __init__(self, pos_3d, def_pos, corner, ctype, corner_index, parent=None):
        super().__init__(parent)
        self.pos_3d = pos_3d
        self.def_pos = def_pos
        self.R = np.identity(3)
        self.set_pos_3d(self.pos_3d)
        self.setVisible(False)
        self.setAcceptHoverEvents(True)
        self.corner = corner
        self.ctype = ctype
        self.corner_index = corner_index
        self.grid_lines = []
        self.text = None
        self.setToolTip("x: {}, y: {}, z: {}".format(self.def_pos[0], self.def_pos[1], self.def_pos[2]))

    def add_grid_line(self, grid_line):
        self.grid_lines.append(grid_line)

    def rotate_projection(self, R):
        self.R = np.matmul(R, self.R)
        scene_pos = np.matmul(self.R, self.pos_3d)
        self.setPos(scene_pos[0], scene_pos[2])

    def remove_grid_line(self, grid_line):
        self.grid_lines.remove(grid_line)

    def get_grid_lines(self):
        return self.grid_lines

    def get_def_pos(self):
        return self.def_pos

    def is_corner(self):
        return self.corner

    def set_corner(self, corner):
        self.corner = corner

    def get_ctype(self):
        return self.ctype

    def set_ctype(self, ctype):
        self.ctype = ctype

    def get_corner_index(self):
        return self.corner_index

    def set_corner_index(self, index):
        self.corner_index = index

    def add_to_ctype(self, a):
        self.ctype.append(a)

    def remove_from_ctype(self, b):
        self.ctype.remove(b)

    def boundingRect(self):
        scene_pos = np.matmul(self.R, self.pos_3d)
        return QRectF(scene_pos[0] - 1, scene_pos[2] - 1, 2, 2)

    def paint(self, painter, option, widget=...):
        cutoff = 20
        scene_pos = np.matmul(self.R, self.pos_3d)
        d = np.sqrt(scene_pos[0]**2 + scene_pos[1]**2 + scene_pos[2]**2)
        self.setZValue(scene_pos[1] + 2)
        if d <= cutoff:
            if self.corner:
                painter.setBrush(QBrush(QColor(255, int((d / cutoff) * 255), int((d / cutoff) * 255)), Qt.BrushStyle.SolidPattern))
                brush = QBrush(QColor(255, int((d / cutoff) * 255), int((d / cutoff) * 255)), Qt.BrushStyle.SolidPattern)
            elif self.get_def_pos()[0] == 0 and self.get_def_pos()[1] == 0 and self.get_def_pos()[2] == 0:
                painter.setBrush(QBrush(QColor(int((d / cutoff) * 255), 255, int((d / cutoff) * 255)), Qt.BrushStyle.SolidPattern))
                brush = QBrush(QColor(int((d / cutoff) * 255), 255, int((d / cutoff) * 255)), Qt.BrushStyle.SolidPattern)
            else:
                painter.setBrush(QBrush(QColor(int((d / cutoff) * 255), int((d / cutoff) * 255), int((d / cutoff) * 255)), Qt.BrushStyle.SolidPattern))
                brush = QBrush(QColor(int((d / cutoff) * 255), int((d / cutoff) * 255), int((d / cutoff) * 255)), Qt.BrushStyle.SolidPattern)
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            path = QPainterPath()
            path.addRoundedRect(QRectF(scene_pos[0] - 0.2, scene_pos[2] - 0.2, 0.4, 0.4), 0.2, 0.2)
            painter.drawPath(path)
            painter.fillPath(path, brush)

    def get_pos_3d(self):
        return self.pos_3d

    def get_scene_pos_3d(self):
        return np.matmul(self.R, self.pos_3d)

    def set_pos_3d(self, array):
        self.pos_3d = array
        scene_pos = np.matmul(self.R, self.pos_3d)
        self.setPos(scene_pos[0], scene_pos[2])
