import numpy as np

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPen, QPainterPath


class PathLine(QGraphicsItem):

    def __init__(self, point_1, point_2):
        super().__init__()
        self.setVisible(True)
        self.point_1 = point_1
        self.point_2 = point_2

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
        p1 = self.point_1.get_scene_pos_3d()
        p2 = self.point_2.get_scene_pos_3d()
        p1 = np.array([p1[0], p1[2]])
        p2 = np.array([p2[0], p2[2]])
        d_unit = (p2 - p1) / np.linalg.norm(p2 - p1)
        d_norm = self.gram_schmidt_2d(d_unit)

        pen = QPen(Qt.GlobalColor.black)
        pen.setWidthF(0.1)
        painter.setPen(pen)
        painter.scale(2, 2)

        for i in range(0, int(np.linalg.norm(p2 - p1)), 1):
            top = p1 + i * d_unit + (1/4) * d_norm - (1/4) * d_unit
            center = p1 + i * d_unit
            bottom = p1 + i * d_unit - (1/4) * d_norm - (1/4) * d_unit
            path = QPainterPath(QPointF(float(top[0]), float(top[1])))
            path.lineTo(QPointF(float(center[0]), float(center[1])))
            path.lineTo(QPointF(float(bottom[0]), float(bottom[1])))
            painter.drawPath(path)

        line_path = QPainterPath(QPointF(float(p1[0]), float(p1[1])))
        line_path.lineTo(QPointF(float(p2[0]), float(p2[1])))
        painter.drawPath(line_path)

    @staticmethod
    def gram_schmidt_2d(v):
        v = v / np.linalg.norm(v)
        try:
            u = np.array([v[0], v[1] - 1])
            u = u - (np.dot(u, v) / np.dot(v, v)) * v
            u = u / np.linalg.norm(u)
        except ZeroDivisionError:
            u = np.array([v[0] - 1, v[1]])
            u = u - (np.dot(u, v) / np.dot(v, v)) * v
            u = u / np.linalg.norm(u)
        return u

