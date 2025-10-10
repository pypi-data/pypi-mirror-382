import time

import numpy as np

from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QPointF

from helixpoint import HelixPoint


class CSView(QGraphicsView):

    TIME: float = 0.2 * 10 ** 9
    ZOOM_SENSITIVITY: int = 200

    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom = False
        self.translate_ref = False
        self.rotate_lat = False
        self.previous_mouse_pos = (0, 0, time.time_ns())
        self.ref_point = None
        self.rotation_amount = 0

    def set_ref_point(self, point):
        self.ref_point = point

    def get_ref_point(self):
        return self.ref_point

    def get_rotation_amount(self):
        return self.rotation_amount

    def set_rotation_amount(self, theta):
        self.rotation_amount = theta

    def enable_helix_editing(self):
        for item in self.scene().items():
            if isinstance(item, HelixPoint):
                item.enable_editing()

    def disable_helix_editing(self):
        for item in self.scene().items():
            if isinstance(item, HelixPoint):
                item.disable_editing()

    def enable_helix_renumbering(self):
        for item in self.scene().items():
            if isinstance(item, HelixPoint):
                item.enable_renumbering()

    def disable_helix_renumbering(self):
        for item in self.scene().items():
            if isinstance(item, HelixPoint):
                item.disable_renumbering()

    def activate_zoom(self):
        self.zoom = True
        self.setMouseTracking(False)

    def deactivate_zoom(self):
        self.zoom = False
        self.setMouseTracking(True)

    def activate_translate_ref(self):
        self.translate_ref = True
        self.setMouseTracking(False)

    def deactivate_translate_ref(self):
        self.translate_ref = False
        self.setMouseTracking(True)

    def activate_rotate(self):
        self.rotate_lat = True
        self.setMouseTracking(False)

    def deactivate_rotate(self):
        self.rotate_lat = False
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        event.accept()
        if time.time_ns() - self.previous_mouse_pos[2] <= self.TIME:
            dx = event.x() - self.previous_mouse_pos[0]
            dy = event.y() - self.previous_mouse_pos[1]
            d = np.sqrt(dx**2 + dy**2)
            if self.zoom and event.buttons() != Qt.MouseButton.NoButton:
                event.accept()
                if dy <= 0:
                    self.scale(1 + d / self.ZOOM_SENSITIVITY, 1 + d / self.ZOOM_SENSITIVITY)
                else:
                    self.scale(1 / (1 + d / self.ZOOM_SENSITIVITY), 1 / (1 + d / self.ZOOM_SENSITIVITY))
                self.scene().update()
                self.update()
            elif self.translate_ref and event.buttons() != Qt.MouseButton.NoButton:
                event.accept()
                inverse, _ = self.transform().inverted()
                mapped_move = inverse.map(QPointF(dx, dy))
                self.ref_point.setPos(self.ref_point.x() + mapped_move.x(), self.ref_point.y() + mapped_move.y())
                self.parent().parent().update_ref_point_value(self.ref_point.x(), self.ref_point.y())
                self.scene().update()
                self.update()
            elif self.rotate_lat and event.buttons() != Qt.MouseButton.NoButton:
                event.accept()
                if dy <= 0:
                    self.rotate(d)
                    self.parent().parent().update_cs_angle(d)
                    self.rotation_amount += d
                else:
                    self.rotate(-d)
                    self.parent().parent().update_cs_angle(-d)
                    self.rotation_amount -= d
                for item in self.scene().items():
                    if isinstance(item, HelixPoint):
                        item.update_text_rotation()
                self.scene().update()
                self.update()
        else:
            super().mouseMoveEvent(event)
        self.previous_mouse_pos = (event.x(), event.y(), time.time_ns())
