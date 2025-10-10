import numpy as np

from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsTextItem
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPen, QBrush, QPainterPath, QColor, QTransform

from helixpoint import ReferencePoint, HelixPoint


class NodePoint(QGraphicsItem):

    def __init__(self, pos_3d, def_pos, node_index,
                 old_scene=None, ref_point=None, theta=None, transform=None, lattice_type=None, parent=None):
        super().__init__(parent)
        self.pos_3d = pos_3d
        self.def_pos = def_pos
        self.node_index = node_index
        self.R = np.identity(3)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.selected = False
        self.prev_node = None
        self.next_node = None
        self.curve = False
        if old_scene is None:
            self.cs_scene = QGraphicsScene()
            self.cs_scene.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
            self.ref_point = None
            self.cs_angle = 0
            self.cs_transform = None
            self.lattice_type = None
        else:
            self.cs_scene = old_scene
            self.ref_point = ref_point
            self.cs_angle = theta
            self.cs_transform = transform
            self.lattice_type = lattice_type

    def set_lattice_type(self, type_number):
        self.lattice_type = type_number

    def get_lattice_type(self):
        return self.lattice_type

    def redraw_lattice(self):
        if self.lattice_type is None:
            return
        elif self.lattice_type == 1:
            for item in self.cs_scene.items():
                if isinstance(item, HelixPoint):
                    item.update_radius()
                    item.recalc_pos()
        elif self.lattice_type == 2:
            for item in self.cs_scene.items():
                if isinstance(item, HelixPoint):
                    item.update_radius()
                    item.recalc_pos()

    def save_cs_angle(self, theta):
        self.cs_angle = theta

    def save_cs_transform(self, transform):
        self.cs_transform = transform

    def change_scene(self, scene_lst):
        self.cs_scene = QGraphicsScene()
        self.cs_scene.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
        self.cs_scene.setSceneRect(scene_lst[0].sceneRect())
        for item in scene_lst[0].items():
            if isinstance(item, HelixPoint):
                new_helix = HelixPoint(item.get_ref_point(), item.get_x_ind(), item.get_y_ind(),
                                       item.get_window(), item.get_lattice_type())
                new_helix.set_selection(item.has_selection())
                new_helix.set_count(item.get_count())
                if item.has_set_number():
                    new_helix.renumber(item.get_number())
                new_helix.set_pure_number(item.get_pure_number())
                text = QGraphicsTextItem(item.get_text().toPlainText())
                text.setDefaultTextColor(Qt.GlobalColor.black)
                self.cs_scene.addItem(text)
                text.setPos(2 * item.x() - item.get_radius(), 2 * item.y() - item.get_radius())
                text.setTransformOriginPoint(item.get_radius(), item.get_radius())
                text.setZValue(5)
                text.hide()
                new_helix.set_text(text)
                self.cs_scene.addItem(new_helix)
            if isinstance(item, ReferencePoint):
                self.ref_point = ReferencePoint(item.x(), item.y(), item.get_radius())
                self.ref_point.setZValue(10)
                self.cs_scene.addItem(self.ref_point)
        self.cs_transform = QTransform(scene_lst[3].m11(), scene_lst[3].m12(), scene_lst[3].m13(),
                                       scene_lst[3].m21(), scene_lst[3].m22(), scene_lst[3].m23(),
                                       scene_lst[3].m31(), scene_lst[3].m32(), scene_lst[3].m33())
        self.cs_angle = scene_lst[2]
        self.lattice_type = scene_lst[4]

    def get_ref_point(self):
        return self.ref_point

    def set_ref_point(self, ref_point):
        self.ref_point = ref_point

    def get_cs_angle(self):
        return self.cs_angle

    def get_cs_transform(self):
        return self.cs_transform

    def has_selection(self):
        return self.selected

    def set_selection(self, state):
        self.selected = state
        if not state:
            if self.scene().parent().point_tools_active():
                self.scene().parent().deactivate_point_tools()
                self.scene().parent().deactivate_cs_tool()
            if self.scene().parent().connection_tools_active():
                self.scene().parent().deactivate_connection_tools()
        else:
            for item in self.scene().items():
                if isinstance(item, NodePoint) and item is not self and item.has_selection():
                    item.set_selection(False)
            if self.scene().parent().connect_points_active() and not self.scene().parent().connection_tools_active():
                self.scene().parent().activate_connection_tools()
            if not self.scene().parent().connect_points_active() and not self.scene().parent().point_tools_active():
                self.scene().parent().activate_point_tools()
                self.scene().parent().activate_cs_tool()

    def get_cs_scene(self):
        return self.cs_scene

    def set_prev_node(self, prev_node):
        self.prev_node = prev_node

    def remove_prev_node(self):
        self.prev_node = None

    def has_curve(self, state=None):
        if state is None:
            return self.curve
        else:
            self.curve = state

    def get_prev_node(self):
        return self.prev_node

    def set_next_node(self, next_node):
        self.next_node = next_node

    def remove_next_node(self):
        self.next_node = None

    def get_next_node(self):
        return self.next_node

    def rotate_projection(self, R):
        self.R = np.matmul(R, self.R)
        scene_pos = np.matmul(self.R, self.pos_3d)
        self.setPos(scene_pos[0], scene_pos[2])

    def set_pos_3d(self, array):
        self.pos_3d = array
        scene_pos = np.matmul(self.R, self.pos_3d)
        self.setPos(scene_pos[0], scene_pos[2])

    def get_pos_3d(self):
        return self.pos_3d

    def get_def_pos(self):
        return self.def_pos

    def get_node_index(self):
        return self.node_index

    def set_def_pos(self, array):
        self.def_pos = array

    def get_scene_pos_3d(self):
        return np.matmul(self.R, self.pos_3d)

    def boundingRect(self):
        scene_pos = np.matmul(self.R, self.pos_3d)
        return QRectF(scene_pos[0] - 2, scene_pos[2] - 2, 4, 4)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.selected:
                self.set_selection(False)
            else:
                self.set_selection(True)
            self.update()

    def paint(self, painter, option, widget=...):
        scene_pos = np.matmul(self.R, self.pos_3d)
        self.setZValue(scene_pos[1] + 2)
        if not self.selected:
            painter.setBrush(QBrush(Qt.GlobalColor.red, Qt.BrushStyle.SolidPattern))
            painter.setPen(QPen(Qt.GlobalColor.red))
        elif self.selected and self.scene().parent().connect_points_active():
            painter.setBrush(QBrush(QColor(100, 255, 100), Qt.BrushStyle.SolidPattern))
            painter.setPen(QPen(QColor(150, 255, 150)))
        else:
            painter.setBrush(QBrush(QColor(100, 100, 255), Qt.BrushStyle.SolidPattern))
            painter.setPen(QPen(QColor(150, 150, 255)))
            self.scene().parent().update_point_value(self.def_pos)
        path = QPainterPath()
        path.addRoundedRect(QRectF(scene_pos[0] - 1, scene_pos[2] - 1, 2, 2), 2, 2)
        painter.drawPath(path)
        painter.fillPath(path, painter.brush())
