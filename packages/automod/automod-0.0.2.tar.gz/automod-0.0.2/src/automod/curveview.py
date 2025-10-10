import numpy as np
import time

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QTransform
from PySide6.QtWidgets import QGraphicsView

from nodepoint import NodePoint


class CurveView(QGraphicsView):

    TIME: float = 0.2 * 10 ** 9
    ZOOM_SENSITIVITY: int = 200
    TRANSLATE_SENSITIVITY: int = 20
    ROTATE_SENSITIVITY: int = 200

    @staticmethod
    def rotation_matrix_y(theta):
        return np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [(-1)*np.sin(theta), 0, np.cos(theta)]])

    @staticmethod
    def rotation_matrix_x(theta):
        return np.array([[1, 0, 0], [0, np.cos(theta), (-1)*np.sin(theta)], [0, np.sin(theta), np.cos(theta)]])

    @staticmethod
    def rotation_matrix_z(theta):
        return np.array([[np.cos(theta), (-1)*np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])

    def __init__(self, curve_scene, parent=None):
        super().__init__(curve_scene, parent)
        self.zoom = False
        self.zoom_amount = 1.1
        self.x_translation = False
        self.y_translation = False
        self.z_translation = False
        self.x_rotation = False
        self.y_rotation = False
        self.z_rotation = False
        self.add_points = False
        self.connect_points = False
        self.point_x_translation = False
        self.point_y_translation = False
        self.point_z_translation = False
        self.def_transform = None
        self.scene = curve_scene
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setSceneRect(-self.scene.size/2, -self.scene.size/2, self.scene.size, self.scene.size)
        self.previous_mouse_pos = (0, 0, time.time_ns())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        self.init_fit()
        self.init_rotation()

    def init_rotation(self):
        R = self.rotation_matrix_x(0.05)
        self.scene.get_storage().rotate_all_points(R)
        R = self.rotation_matrix_z(0.05)
        self.scene.get_storage().rotate_all_points(R)

    def init_fit(self):
        dx = 100 / self.parent().get_parameters()['gs']
        dy = 100 / self.parent().get_parameters()['gs']
        self.def_transform = QTransform.fromScale(dx, dy)
        self.setTransform(self.def_transform)
        self.scale(self.zoom_amount, self.zoom_amount)

    def restore_view(self):
        self.scene.get_storage().rotate_to_default()
        self.scene.get_storage().translate_to_default()
        self.zoom_amount = 1.1
        self.init_fit()
        self.init_rotation()
        self.parent().deactivate_point_tools()
        self.scene.update()
        self.update()

    def pre_translate(self, dx, dy):
        delta = (np.dot(np.array([dx, dy]), np.array([0, -1])) /
                 (self.TRANSLATE_SENSITIVITY * self.parent().get_parameters()["ts"]))
        w = self.scene.get_w()
        if np.abs(delta) > w:
            delta = (delta/np.abs(delta)) * w
        return delta

    def activate_add_points(self):
        self.add_points = True
        self.setMouseTracking(False)

    def deactivate_add_points(self):
        self.add_points = False
        self.setMouseTracking(True)

    def activate_zoom(self):
        self.zoom = True
        self.setMouseTracking(False)

    def activate_x_translation(self):
        self.x_translation = True
        self.setMouseTracking(False)

    def activate_y_translation(self):
        self.y_translation = True
        self.setMouseTracking(False)

    def activate_z_translation(self):
        self.z_translation = True
        self.setMouseTracking(False)

    def activate_x_rotation(self):
        self.x_rotation = True
        self.setMouseTracking(False)

    def activate_y_rotation(self):
        self.y_rotation = True
        self.setMouseTracking(False)

    def activate_z_rotation(self):
        self.z_rotation = True
        self.setMouseTracking(False)

    def activate_point_x_translation(self):
        self.point_x_translation = True
        self.setMouseTracking(False)

    def activate_point_y_translation(self):
        self.point_y_translation = True
        self.setMouseTracking(False)

    def activate_point_z_translation(self):
        self.point_z_translation = True
        self.setMouseTracking(False)

    def activate_connect_points(self):
        self.connect_points = True
        self.setMouseTracking(True)
        self.scene.clearSelection()

    def deactivate_connect_points(self):
        self.connect_points = False
        self.setMouseTracking(False)
        self.scene.clearSelection()

    def deactivate_zoom(self):
        self.zoom = False
        self.setMouseTracking(True)

    def deactivate_x_translation(self):
        self.x_translation = False
        self.setMouseTracking(True)

    def deactivate_y_translation(self):
        self.y_translation = False
        self.setMouseTracking(True)

    def deactivate_z_translation(self):
        self.z_translation = False
        self.setMouseTracking(True)

    def deactivate_x_rotation(self):
        self.x_rotation = False
        self.setMouseTracking(True)

    def deactivate_y_rotation(self):
        self.y_rotation = False
        self.setMouseTracking(True)

    def deactivate_z_rotation(self):
        self.z_rotation = False
        self.setMouseTracking(True)

    def deactivate_point_x_translation(self):
        self.point_x_translation = False
        self.setMouseTracking(True)

    def deactivate_point_y_translation(self):
        self.point_y_translation = False
        self.setMouseTracking(True)

    def deactivate_point_z_translation(self):
        self.point_z_translation = False
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        if time.time_ns() - self.previous_mouse_pos[2] <= self.TIME:
            dx = event.position().x() - self.previous_mouse_pos[0]
            dy = event.position().y() - self.previous_mouse_pos[1]
            d = np.sqrt(dx ** 2 + dy ** 2)
            if self.zoom and event.buttons() != Qt.MouseButton.NoButton:
                event.accept()
                if dy <= 0:
                    delta = 1 + (d / (self.ZOOM_SENSITIVITY * self.parent().get_parameters()["zs"]))
                    self.scale(delta, delta)
                    self.zoom_amount = self.zoom_amount * delta
                else:
                    delta = 1 / (1 + (d / (self.ZOOM_SENSITIVITY * self.parent().get_parameters()["zs"])))
                    self.scale(delta, delta)
                    self.zoom_amount = self.zoom_amount * delta
                self.scene.update()
                self.update()
            elif (self.x_translation or self.y_translation or self.z_translation) and event.buttons() != Qt.MouseButton.NoButton:
                event.accept()
                delta = self.pre_translate(dx, dy)
                if self.x_translation:
                    self.scene.get_storage().translate_all_points(delta, 0, 0)
                elif self.y_translation:
                    self.scene.get_storage().translate_all_points(0, delta, 0)
                else:
                    self.scene.get_storage().translate_all_points(0, 0, delta)
                self.scene.get_storage().update_grid()
                self.scene.update()
                self.update()
            elif (self.x_rotation or self.y_rotation or self.z_rotation) and event.buttons() != Qt.MouseButton.NoButton:
                event.accept()
                theta = d / (self.ROTATE_SENSITIVITY * self.parent().get_parameters()["rs"])
                if self.y_rotation:
                    if dy > 0:
                        R = self.rotation_matrix_y(theta)
                    else:
                        R = self.rotation_matrix_y(-theta)
                elif self.x_rotation:
                    if dy > 0:
                        R = self.rotation_matrix_x(theta)
                    else:
                        R = self.rotation_matrix_x(-theta)
                else:
                    if dy > 0:
                        R = self.rotation_matrix_z(theta)
                    else:
                        R = self.rotation_matrix_z(-theta)
                self.scene.get_storage().rotate_all_points(R)
                self.scene.update()
                self.update()
            elif (self.point_x_translation or self.point_y_translation or self.point_z_translation) and event.buttons() != Qt.MouseButton.NoButton:
                event.accept()
                delta = self.pre_translate(dx, dy)
                if self.point_x_translation:
                    self.scene.get_storage().translate_node(delta, 0, 0)
                elif self.point_y_translation:
                    self.scene.get_storage().translate_node(0, delta, 0)
                else:
                    self.scene.get_storage().translate_node(0, 0, delta)
                self.scene.update()
                self.update()

        else:
            super().mouseMoveEvent(event)
        self.previous_mouse_pos = (event.position().x(), event.position().y(), time.time_ns())

    def mousePressEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            event_pos = QPointF(((event.x() - self.width()/2) / self.transform().m11()) / 2,
                                ((event.y() - self.height()/2) / self.transform().m22()) / 2)
            if self.add_points:
                self.scene.get_storage().add_node_point(event_pos)
            elif self.connect_points and self.scene.get_storage().has_node_at(event_pos):
                for item in self.scene.items():
                    if isinstance(item, NodePoint) and item.has_selection():
                        subseq_node = self.scene.get_storage().get_node_at(event_pos)
                        if ((item.get_next_node() is None) and (subseq_node.get_prev_node() is None) and
                                (item is not subseq_node)):
                            item.set_next_node(subseq_node)
                            subseq_node.set_prev_node(item)
                            self.scene.get_storage().add_path_line(item, subseq_node)
                            self.scene.get_storage().get_nodes()[item.get_node_index()][3] = subseq_node.get_node_index()
                            self.scene.get_storage().get_nodes()[subseq_node.get_node_index()][2] = item.get_node_index()
                else:
                    self.scene.get_storage().get_node_at(event_pos).mousePressEvent(event)
            elif self.point_x_translation or self.point_y_translation or self.point_z_translation:
                pass
            else:
                if self.scene.get_storage().has_node_at(event_pos):
                    self.scene.get_storage().get_node_at(event_pos).mousePressEvent(event)

    def resizeEvent(self, event):
        w1, w2, w3, w4 = self.parent().get_tool_widths()
        d = event.oldSize().width() - event.size().width()
        if d in [w1 + i for i in range(-2, 2)] or d in [w2 + i for i in range(-2, 2)]\
                or d in [-w1 + i for i in range(-2, 2)] or d in [-w2 + i for i in range(-2, 2)]:
            dx_scene = (d / self.transform().m11()) / 4
            dy_scene = ((event.oldSize().height() - event.size().height())/ self.transform().m22()) / 4
            d_vec = np.array([-dx_scene, -dy_scene, 0])
            x_hat = self.scene.get_storage().get_unit_x()
            y_hat = self.scene.get_storage().get_unit_y()
            z_hat = self.scene.get_storage().get_unit_z()
            self.scene.get_storage().translate_all_points(np.dot(d_vec, x_hat), np.dot(d_vec, y_hat), np.dot(d_vec, z_hat))
        elif d in [w3 + i for i in range(-8, 8)] or d in [w4 + i for i in range(-2, 2)]\
                or d in [-w3 + i for i in range(-6, 6)] or d in [-w4 + i for i in range(-2, 2)]:
            dx_scene = (d / self.transform().m11()) / 4
            dy_scene = ((event.oldSize().height() - event.size().height()) / self.transform().m22()) / 4
            d_vec = np.array([dx_scene, -dy_scene, 0])
            x_hat = self.scene.get_storage().get_unit_x()
            y_hat = self.scene.get_storage().get_unit_y()
            z_hat = self.scene.get_storage().get_unit_z()
            self.scene.get_storage().translate_all_points(np.dot(d_vec, x_hat), np.dot(d_vec, y_hat), np.dot(d_vec, z_hat))
        elif d in [w2 + w3 + w4 + i for i in range(-6, 6)] or d in [-(w2 + w3 + w4) + i for i in range(-6, 6)]:
            dx_scene_1 = (w2 / self.transform().m11()) / 4
            dx_scene_2 = ((-d - w2) / self.transform().m11()) / 4
            dy_scene = ((event.oldSize().height() - event.size().height()) / self.transform().m22()) / 4
            d_vec_1 = np.array([dx_scene_1, -dy_scene, 0])
            d_vec_2 = np.array([-dx_scene_2, -dy_scene, 0])
            x_hat = self.scene.get_storage().get_unit_x()
            y_hat = self.scene.get_storage().get_unit_y()
            z_hat = self.scene.get_storage().get_unit_z()
            self.scene.get_storage().translate_all_points(np.dot(d_vec_1, x_hat), np.dot(d_vec_1, y_hat), np.dot(d_vec_1, z_hat))
            self.scene.get_storage().translate_all_points(np.dot(d_vec_2, x_hat), np.dot(d_vec_2, y_hat), np.dot(d_vec_2, z_hat))
        elif d in [w3 + w4 + i for i in range(-6, 6)] or d in [-(w3 + w4) + i for i in range(-6, 6)]:
            dx_scene = (d / self.transform().m11()) / 4
            dy_scene = ((event.oldSize().height() - event.size().height()) / self.transform().m22()) / 4
            d_vec = np.array([dx_scene, -dy_scene, 0])
            x_hat = self.scene.get_storage().get_unit_x()
            y_hat = self.scene.get_storage().get_unit_y()
            z_hat = self.scene.get_storage().get_unit_z()
            self.scene.get_storage().translate_all_points(np.dot(d_vec, x_hat), np.dot(d_vec, y_hat),
                                                          np.dot(d_vec, z_hat))
        self.init_fit()
        self.scene.update()
        self.update()

    def wheelEvent(self, event):
        event.accept()

    def keyPressEvent(self, event):
        event.accept()
