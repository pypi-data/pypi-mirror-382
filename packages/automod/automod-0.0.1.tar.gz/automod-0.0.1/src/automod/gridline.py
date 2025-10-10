import numpy as np

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QBrush, QPen, QPainterPath, QLinearGradient, QColor
from PySide6.QtWidgets import QGraphicsItem


class GridLine(QGraphicsItem):

    def __init__(self, point_1, point_2, line_type):
        super().__init__()
        self.setVisible(True)
        self.point_1 = point_1
        self.point_2 = point_2
        self.line_type = line_type

    @staticmethod
    def is_grid_point():
        return False

    @staticmethod
    def is_grid_line():
        return True

    @staticmethod
    def is_corner():
        return False

    def change_start_point(self, point_1):
        self.point_1 = point_1

    def change_end_point(self, point_2):
        self.point_2 = point_2

    def get_line_type(self):
        return self.line_type

    def boundingRect(self):
        w = 20
        p1 = self.point_1.get_scene_pos_3d()
        p2 = self.point_2.get_scene_pos_3d()
        if p1[0] <= p2[0]:
            left_x = p1[0]
        else:
            left_x = p2[0]
        if p1[2] <= p2[2]:
            top_z = p1[2]
        else:
            top_z = p2[2]
        dx = np.abs(p1[0] - p2[0])
        dz = np.abs(p1[2] - p2[2])
        b_rect = QRectF(left_x - w/2, top_z - w/2, dx + w, dz + w)
        return b_rect

    def paint(self, painter, option, widget=...):
        fade = self.scene().parent().get_parameters()['gs']
        cutoff = 4 * self.scene().parent().get_parameters()['gs']
        p1 = self.point_1.get_scene_pos_3d()
        p2 = self.point_2.get_scene_pos_3d()
        start = QPointF(p1[0], p1[2])
        stop = QPointF(p2[0], p2[2])
        d = np.array([p2[0] - p1[0], p2[2] - p1[2]])
        d_3d = self.point_2.get_scene_pos_3d() - self.point_1.get_scene_pos_3d()

        if d[0] != 0 or d[1] != 0:
            grad = QLinearGradient(start, stop)
            y_s = []
            for i in range(0, 11):
                d = (self.point_1.get_scene_pos_3d() + i * (1/10) * d_3d)
                y_s.append(d[1])
                d = np.sqrt(d[0]**2 + d[1]**2 + d[2]**2)
                if d <= fade:
                    if self.line_type == 0:
                        color = QColor(int(255 - (d / fade) * 255), 0, 0)
                    elif self.line_type == 1:
                        color = QColor(0, int(255 - (d / fade) * 255), 0)
                    else:
                        color = QColor(0, 0, int(255 - (d / fade) * 255))
                elif d <= cutoff:
                    if self.line_type == 0:
                        color = QColor(int((d / cutoff) * 255), int((d / cutoff) * 255), int((d / cutoff) * 255))
                    elif self.line_type == 1:
                        color = QColor(int((d / cutoff) * 255), int((d / cutoff) * 255), int((d / cutoff) * 255))
                    else:
                        color = QColor(int((d / cutoff) * 255), int((d / cutoff) * 255), int((d / cutoff) * 255))
                else:
                    color = QColor(255, 255, 255, 0)
                grad.setColorAt(i * 0.1, color)
            brush = QBrush(grad)
            painter.setBrush(brush)

            self.setZValue(min(y_s))

            pen = QPen(Qt.GlobalColor.white)
            pen.setWidthF(0.1)
            pen.setBrush(brush)
            painter.setPen(pen)
            painter.scale(2, 2)

            path = QPainterPath(start)
            path.lineTo(stop)
            if self.scene().parent().get_parameters()['grid']:
                painter.drawPath(path)
