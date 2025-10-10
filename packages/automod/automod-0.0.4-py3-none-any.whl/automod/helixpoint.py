import numpy as np

from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush


class ReferencePoint(QGraphicsItem):
    def __init__(self, scene_x, scene_y, radius, parent=None):
        super().__init__(parent)
        self.setPos(scene_x, scene_y)
        self.radius = radius

    def get_radius(self):
        return self.radius

    def boundingRect(self):
        return QRectF(self.x() - 2 * self.radius, self.y() - 2 * self.radius, 4 * self.radius, 4 * self.radius)

    def paint(self, painter, option, widget=...):
        painter.setPen(QPen(Qt.GlobalColor.red))
        painter.setBrush(QBrush(Qt.GlobalColor.red))
        painter.drawEllipse(QPointF(self.x(), self.y()), 2 * self.radius, 2 * self.radius)


class HelixPoint(QGraphicsItem):

    def __init__(self, ref_point, x_ind, y_ind, window, lattice_type, parent=None):
        super().__init__(parent)
        self.ref_point = ref_point
        self.x_ind = x_ind
        self.y_ind = y_ind
        if (self.y_ind % 2) == 0:
            if (self.x_ind % 2) == 0:
                self.odd = False
            else:
                self.odd = True
        else:
            if (self.x_ind % 2) == 0:
                self.odd = True
            else:
                self.odd = False
        self.count = 0
        if self.odd:
            self.number = 1
        else:
            self.number = 0
        self.set_number = None
        self.window = window
        self.radius = (self.window.get_parameters()['hd'] * 10) / 2
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.selected = False
        self.editable = False
        self.renumbering = False
        self.connected = False
        self.text = QGraphicsTextItem("{:d}".format(self.number))
        self.text.setDefaultTextColor(Qt.GlobalColor.black)
        self.text2 = QGraphicsTextItem("{:d}{:d}".format(self.y_ind, self.x_ind))
        self.text2.setDefaultTextColor(Qt.GlobalColor.black)
        self.lattice_type = lattice_type
        self.recalc_pos()

    def recalc_pos(self):
        if self.lattice_type == 1:
            rd = (self.window.get_parameters()['hd'] * 10) / 2 + (self.window.get_parameters()['ihg'] * 10) / 2
            dx = np.sqrt(3) * rd
            if self.y_ind % 2 == 0:
                if self.x_ind % 2 == 0:
                    y_pos = self.y_ind * 2 * rd - rd + (self.y_ind // 2) * 2 * rd
                    x_pos = self.x_ind * dx
                else:
                    y_pos = self.y_ind * 2 * rd + (self.y_ind // 2) * 2 * rd
                    x_pos = self.x_ind * dx
            else:
                if self.x_ind % 2 == 0:
                    y_pos = self.y_ind * 2 * rd + rd + (self.y_ind // 2) * 2 * rd
                    x_pos = self.x_ind * dx
                else:
                    y_pos = self.y_ind * 2 * rd + (self.y_ind // 2) * 2 * rd
                    x_pos = self.x_ind * dx
            self.setPos(x_pos, y_pos)
            self.text.setPos(2 * self.x() - self.radius, 2 * self.y() - self.radius)
        elif self.lattice_type == 2:
            rd = (self.window.get_parameters()['hd'] * 10) / 2 + (self.window.get_parameters()['ihg'] * 10) / 2
            x_pos = rd + self.x_ind * 2 * rd
            y_pos = rd + self.y_ind * 2 * rd
            self.setPos(x_pos, y_pos)
            self.text.setPos(2 * self.x() - self.radius, 2 * self.y() - self.radius)

    def update_radius(self):
        self.radius = (self.window.get_parameters()['hd'] * 10) / 2

    def update_text_rotation(self):
        self.text.setRotation(-self.window.get_cs_view().get_rotation_amount())

    def increment_count(self):
        self.count += 1

    def is_odd(self):
        return self.odd

    def get_count(self):
        return self.count

    def set_count(self, count):
        self.count = count

    def enable_editing(self):
        self.editable = True

    def disable_editing(self):
        self.editable = False

    def enable_renumbering(self):
        self.renumbering = True

    def disable_renumbering(self):
        self.renumbering = False

    def get_number(self):
        if self.set_number is None:
            return self.number
        else:
            return self.set_number

    def set_pure_number(self, number):
        self.number = number

    def get_pure_number(self):
        return self.number

    def get_ref_point(self):
        return self.ref_point

    def get_lattice_type(self):
        return self.lattice_type

    def get_x_ind(self):
        return self.x_ind

    def get_y_ind(self):
        return self.y_ind

    def get_radius(self):
        return self.radius

    def get_window(self):
        return self.window

    def has_set_number(self):
        if self.set_number is None:
            return False
        else:
            return True

    def renumber(self, set_number):
        self.set_number = set_number
        self.text.setPlainText("{:d}".format(self.set_number))

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text

    def has_selection(self):
        return self.selected

    def set_selection(self, state):
        self.selected = state

    def reduce_count(self):
        self.count -= 1

    def reduce_number(self):
        self.number -= 2

    def boundingRect(self):
        return QRectF(self.x() - 2*self.radius, self.y() - 2*self.radius, 4*self.radius, 4*self.radius)

    def paint(self, painter, option, widget=...):
        if self.text.scene() is None:
            self.scene().addItem(self.text)
            self.text.setPos(2*self.x() - self.radius, 2*self.y() - self.radius)
            self.text.setTransformOriginPoint(self.radius, self.radius)
            self.text.setZValue(5)
            self.text.hide()
        if self.selected:
            if self.connected:
                painter.setBrush(QBrush(Qt.GlobalColor.darkBlue))
            elif self.odd:
                painter.setBrush(QBrush(Qt.GlobalColor.darkGreen))
            else:
                painter.setBrush(QBrush(Qt.GlobalColor.green))
            self.text.show()
        else:
            painter.setBrush(QBrush(Qt.GlobalColor.lightGray))
            self.text.hide()
        painter.setPen(QPen(Qt.GlobalColor.darkGray))
        painter.drawEllipse(QPointF(self.x(), self.y()), 2*self.radius, 2*self.radius)

    def mousePressEvent(self, event):
        if self.editable:
            if self.selected and event.buttons() == Qt.MouseButton.LeftButton:
                self.selected = False
                event.accept()
                for item in self.scene().items():
                    if isinstance(item, HelixPoint):
                        if (self.is_odd() and item.is_odd()) or (not self.is_odd() and not item.is_odd()):
                            item.reduce_count()
                        if item.get_number() > self.get_number() and not item.has_set_number():
                            if (self.is_odd() and item.is_odd()) or (not self.is_odd() and not item.is_odd()):
                                item.reduce_number()
                                item.get_text().setPlainText("{:d}".format(item.get_number()))
            elif not self.selected and event.buttons() == Qt.MouseButton.LeftButton:
                self.selected = True
                event.accept()
                if self.is_odd():
                    self.number = self.count * 2 + 1
                else:
                    self.number = self.count * 2
                if self.set_number is None:
                    self.text.setPlainText("{:d}".format(self.number))
                else:
                    self.text.setPlainText("{:d}".format(self.set_number))
                for item in self.scene().items():
                    if isinstance(item, HelixPoint):
                        if (self.is_odd() and item.is_odd()) or (not self.is_odd() and not item.is_odd()):
                            item.increment_count()
            self.update()
        elif self.renumbering:
            if self.selected and event.buttons() == Qt.MouseButton.LeftButton:
                event.accept()
                self.window.connect_to_renumber(self)

    def connected_to_renumber(self, state=None):
        if state is None:
            return self.connected
        else:
            self.connected = state
