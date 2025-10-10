import json, random

import numpy as np

from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QAction, QBrush, QIcon, QTransform, QPixmap
from PySide6.QtWidgets import (QMainWindow, QToolBar, QErrorMessage, QDockWidget, QStatusBar, QDoubleSpinBox,
                               QGraphicsView, QPushButton, QSpinBox, QFileDialog, QMenuBar, QMenu, QWidget, QGridLayout,
                               QLabel, QTabWidget, QCheckBox)

from curvescene import CurveScene
from curveview import CurveView
from csview import CSView
from nodepoint import NodePoint
from helixpoint import HelixPoint, ReferencePoint

import icons


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parameters = {"ihg": 0.5, "hd": 2.0, "ntl": 0.34, "ml": 0.21, "tl": 10.5, "gs": 20, "mods": True, "cos": True, "sl": True, "seed": 0,
                           "zs": 1, "ts": 1, "rs": 1, "grid": True, "min_d": 8, "buffer": 5, "tt_max": 3.1, 'rho_start': 0.060, "margin_over": 0.005, "margin_under": 0.005}

        self.scene = CurveScene(8 * self.parameters['gs'], self.parameters['gs'], parent=self)
        self.scene.setBackgroundBrush(QBrush(Qt.GlobalColor.white))

        self.ehandler = QErrorMessage.qtHandler()

        self.view = CurveView(self.scene, parent=self)
        self.setCentralWidget(self.view)
        self.view.show()

        self.lattice = 1

        ''' CURVE VIEW TOOLS '''

        curve_view_tools = QToolBar(parent=self)
        curve_view_tools.setFloatable(False)
        curve_view_tools.setMovable(False)
        curve_view_tools.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        curve_view_tools.setIconSize(QSize(32, 32))
        self.addToolBar(curve_view_tools)

        x_translate = QAction("XMove", self)
        x_translate.setStatusTip("XMove tool: Choose for moving main view items in the x-direction")
        x_translate.toggled.connect(self.x_translate_action)
        x_translate.setCheckable(True)
        arrow_red_map = QPixmap(":/icons/arrow_red.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        x_translate.setIcon(QIcon(arrow_red_map))
        x_translate.setIconText("XMove")
        curve_view_tools.addAction(x_translate)
        self.x_translate = x_translate

        y_translate = QAction("YMove", self)
        y_translate.setStatusTip("YMove tool: Choose for moving main view items in the y-direction")
        y_translate.toggled.connect(self.y_translate_action)
        y_translate.setCheckable(True)
        arrow_green_map = QPixmap(":/icons/arrow_green.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        y_translate.setIcon(QIcon(arrow_green_map))
        y_translate.setIconText("YMove")
        curve_view_tools.addAction(y_translate)
        self.y_translate = y_translate

        z_translate = QAction("ZMove", self)
        z_translate.setStatusTip("ZMove tool: Choose for moving main view items in the z-direction")
        z_translate.toggled.connect(self.z_translate_action)
        z_translate.setCheckable(True)
        arrow_blue_map = QPixmap(":/icons/arrow_blue.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        z_translate.setIcon(QIcon(arrow_blue_map))
        z_translate.setIconText("ZMove")
        curve_view_tools.addAction(z_translate)
        self.z_translate = z_translate

        x_rotate = QAction("XRotate", self)
        x_rotate.setStatusTip("XRotate tool: Choose for rotating main view items around the x-axis")
        x_rotate.toggled.connect(self.x_rotate_action)
        x_rotate.setCheckable(True)
        rotate_red_map = QPixmap(":/icons/rotate_red.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        x_rotate.setIcon(QIcon(rotate_red_map))
        x_rotate.setIconText("XRotate")
        curve_view_tools.addAction(x_rotate)
        self.x_rotate = x_rotate

        y_rotate = QAction("YRotate", self)
        y_rotate.setStatusTip("YRotate tool: Choose for rotating main view items around the y-axis")
        y_rotate.toggled.connect(self.y_rotate_action)
        y_rotate.setCheckable(True)
        rotate_green_map = QPixmap(":/icons/rotate_green.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        y_rotate.setIcon(QIcon(rotate_green_map))
        y_rotate.setIconText("YRotate")
        curve_view_tools.addAction(y_rotate)
        self.y_rotate = y_rotate

        z_rotate = QAction("ZRotate", self)
        z_rotate.setStatusTip("ZRotate tool: Choose for rotating main view items around the z-axis")
        z_rotate.toggled.connect(self.z_rotate_action)
        z_rotate.setCheckable(True)
        rotate_blue_map = QPixmap(":/icons/rotate_blue.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        z_rotate.setIcon(QIcon(rotate_blue_map))
        z_rotate.setIconText("ZRotate")
        curve_view_tools.addAction(z_rotate)
        self.z_rotate = z_rotate

        zoom = QAction("Zoom", self)
        zoom.setStatusTip("Zoom tool: Choose for scaling the main view")
        zoom.toggled.connect(self.zoom_action)
        zoom.setCheckable(True)
        zoom_map = QPixmap(":/icons/zoom.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        zoom.setIcon(QIcon(zoom_map))
        zoom.setIconText("Zoom")
        curve_view_tools.addAction(zoom)
        self.zoom = zoom

        restore = QAction("Restore", self)
        restore.setStatusTip("Restore: Click to restore the main view")
        restore.toggled.connect(self.restore_action)
        restore.setCheckable(True)
        restore_map = QPixmap(":/icons/restore.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        restore.setIcon(QIcon(restore_map))
        restore.setIconText("Restore")
        curve_view_tools.addAction(restore)
        self.restore = restore

        curve_view_tools.addSeparator()

        ''' DRAWING TOOLS '''

        drawing_tools = QToolBar(parent=self)
        drawing_tools.setFloatable(False)
        drawing_tools.setMovable(False)
        drawing_tools.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        drawing_tools.setIconSize(QSize(32, 32))
        self.addToolBar(drawing_tools)

        add_points = QAction("Insert", self)
        add_points.setStatusTip("Insert points tool: Click within the main view to create a new point")
        add_points.toggled.connect(self.add_points_action)
        add_points.setCheckable(True)
        add_points_map = QPixmap(":/icons/insert_plus.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        add_points.setIcon(QIcon(add_points_map))
        drawing_tools.addAction(add_points)
        self.add_points = add_points

        connect_points = QAction("Connect", self)
        connect_points.setStatusTip("Connect points tool: Click on two points to connect them")
        connect_points.toggled.connect(self.connect_points_action)
        connect_points.setCheckable(True)
        connect_points_map = QPixmap(":/icons/connect.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        connect_points.setIcon(QIcon(connect_points_map))
        drawing_tools.addAction(connect_points)
        self.connect_points = connect_points

        interpolate = QAction("Interpolate", self)
        interpolate.setStatusTip("Interpolate tool: Calculate and display curves")
        interpolate.toggled.connect(self.interpolate_action)
        interpolate.setCheckable(True)
        interpolate_map = QPixmap(":/icons/interpolate.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        interpolate.setIcon(QIcon(interpolate_map))
        drawing_tools.addAction(interpolate)
        self.interpolate = interpolate

        drawing_tools.addSeparator()

        ''' OUTPUT/INPUT TOOLS '''

        inout_tools = QToolBar(parent=self)
        inout_tools.setFloatable(False)
        inout_tools.setMovable(False)
        inout_tools.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        inout_tools.setIconSize(QSize(32, 32))
        self.addToolBar(inout_tools)

        write_tool = QAction("Save", self)
        write_tool.setStatusTip("Save: Click to save current design as a cadnano file")
        write_tool.toggled.connect(self.write_tool_action)
        write_tool_map = QPixmap(":/icons/save.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        write_tool.setIcon(QIcon(write_tool_map))
        write_tool.setCheckable(True)
        inout_tools.addAction(write_tool)
        self.write_tool = write_tool

        read_tool = QAction("Import", self)
        read_tool.setStatusTip("Import: Click to import node coordinates from a csv file")
        read_tool.toggled.connect(self.read_tool_action)
        read_tool_map = QPixmap(":/icons/import.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        read_tool.setIcon(QIcon(read_tool_map))
        read_tool.setCheckable(True)
        inout_tools.addAction(read_tool)
        self.read_tool = read_tool

        ''' POINT TOOLS '''

        self.point_tools = QToolBar(parent=self)
        self.point_tools.setFloatable(False)
        self.point_tools.setMovable(False)
        self.point_tools.setVisible(False)
        self.point_tools.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.point_tools.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.point_tools)

        point_z_translate = QAction("PointZMove", self)
        point_z_translate.setStatusTip("PointZMove tool: Choose for moving the selected point in the z-direction")
        point_z_translate.toggled.connect(self.point_z_translate_action)
        point_z_translate.setCheckable(True)
        point_z_translate.setIcon(QIcon(arrow_blue_map))
        point_z_translate.setIconText("PointZMove")
        self.point_tools.addAction(point_z_translate)
        self.point_z_translate = point_z_translate

        point_z_value = QDoubleSpinBox()
        point_z_value.setMaximum(1000000)
        point_z_value.setMinimum(-1000000)
        point_z_value.setSingleStep(0.01)
        point_z_value.setDecimals(2)
        point_z_value.setSuffix(' nm')
        point_z_value.valueChanged.connect(self.point_z_spin_translate_action)
        self.point_tools.addWidget(point_z_value)
        self.point_z_value = point_z_value

        point_y_translate = QAction("PointYMove", self)
        point_y_translate.setStatusTip("PointYMove tool: Choose for moving the selected point in the y-direction")
        point_y_translate.toggled.connect(self.point_y_translate_action)
        point_y_translate.setCheckable(True)
        point_y_translate.setIcon(QIcon(arrow_green_map))
        point_y_translate.setIconText("PointYMove")
        self.point_tools.addAction(point_y_translate)
        self.point_y_translate = point_y_translate

        point_y_value = QDoubleSpinBox()
        point_y_value.setMaximum(1000000)
        point_y_value.setMinimum(-1000000)
        point_y_value.setSingleStep(0.01)
        point_y_value.setDecimals(2)
        point_y_value.setSuffix(' nm')
        point_y_value.valueChanged.connect(self.point_y_spin_translate_action)
        self.point_tools.addWidget(point_y_value)
        self.point_y_value = point_y_value

        point_x_translate = QAction("PointXMove", self)
        point_x_translate.setStatusTip("PointXMove tool: Choose for moving the selected point in the x-direction")
        point_x_translate.toggled.connect(self.point_x_translate_action)
        point_x_translate.setCheckable(True)
        point_x_translate.setIcon(QIcon(arrow_red_map))
        point_x_translate.setIconText("PointXMove")
        self.point_tools.addAction(point_x_translate)
        self.point_x_translate = point_x_translate

        point_x_value = QDoubleSpinBox()
        point_x_value.setMaximum(1000000)
        point_x_value.setMinimum(-1000000)
        point_x_value.setSingleStep(0.01)
        point_x_value.setDecimals(2)
        point_x_value.setSuffix(' nm')
        point_x_value.valueChanged.connect(self.point_x_spin_translate_action)
        self.point_tools.addWidget(point_x_value)
        self.point_x_value = point_x_value

        delete_point = QAction("Delete", self)
        delete_point.setStatusTip("Delete tool: Click to delete the selected point")
        delete_point.setCheckable(True)
        delete_point_map = QPixmap(":/icons/trash.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        delete_point.setIcon(QIcon(delete_point_map))
        delete_point.toggled.connect(self.delete_point_action)
        self.point_tools.addAction(delete_point)
        self.delete_point = delete_point

        ''' CONNECTION TOOLS '''

        self.connection_tools = QToolBar(parent=self)
        self.connection_tools.setFloatable(False)
        self.connection_tools.setMovable(False)
        self.connection_tools.setVisible(False)
        self.connection_tools.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.connection_tools.setIconSize(QSize(64, 32))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.connection_tools)

        self.disconnect_prev = QAction("Disconnect previous", self)
        self.disconnect_prev.setStatusTip("Disconnect previous tool: Click to break the connection "
                                          "between the selected point and its predecessor")
        self.disconnect_prev.toggled.connect(self.disconnect_prev_action)
        self.disconnect_prev.setCheckable(True)
        disconnect_prev_map = QPixmap(":/icons/disconnect_prev.png").scaled(QSize(512, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        self.disconnect_prev.setIcon(QIcon(disconnect_prev_map))
        self.disconnect_prev.setIconText("Disconnect previous")
        self.connection_tools.addAction(self.disconnect_prev)

        self.disconnect_next = QAction("Disconnect next", self)
        self.disconnect_next.setStatusTip("Disconnect next tool: "
                                          "Click to break the connection between the selected point and its successor")
        self.disconnect_next.toggled.connect(self.disconnect_next_action)
        self.disconnect_next.setCheckable(True)
        disconnect_next_map = QPixmap(":/icons/disconnect_next.png").scaled(QSize(512, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        self.disconnect_next.setIcon(QIcon(disconnect_next_map))
        self.disconnect_next.setIconText("Disconnect next")
        self.connection_tools.addAction(self.disconnect_next)

        ''' CROSS SECTION TOOL '''

        cs_tool = QDockWidget("Cross section tool")
        cs_tool.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        cs_tool.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.cs_scene = None
        self.cs_node = None
        self.cs_view = CSView(parent=self)
        self.cs_view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        cs_tool.setWidget(self.cs_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, cs_tool)
        self.cs_tool = cs_tool
        cs_tool.setVisible(False)

        self.cs_toolbar = QToolBar(parent=self)
        self.cs_toolbar.setFloatable(False)
        self.cs_toolbar.setMovable(False)
        self.cs_toolbar.setVisible(False)
        self.cs_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.cs_toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.cs_toolbar)

        draw_hc = QAction("HC", self)
        draw_hc.setStatusTip("HC: Click to draw a honeycomb lattice on the cross section plane")
        draw_hc.toggled.connect(self.draw_hc_action)
        draw_hc.setCheckable(True)
        hc_map = QPixmap(":/icons/honeycomb.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        draw_hc.setIcon(QIcon(hc_map))
        draw_hc.setIconText("Honeycomb")
        self.cs_toolbar.addAction(draw_hc)
        self.draw_hc = draw_hc

        draw_sq = QAction("SQ", self)
        draw_sq.setStatusTip("SQ: Click to draw a square lattice on the cross section plane")
        draw_sq.toggled.connect(self.draw_sq_action)
        draw_sq.setCheckable(True)
        sq_map = QPixmap(":/icons/square.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        draw_sq.setIcon(QIcon(sq_map))
        draw_sq.setIconText("Square")
        self.cs_toolbar.addAction(draw_sq)
        self.draw_sq = draw_sq

        zoom_cs = QAction("Zoom", self)
        zoom_cs.setStatusTip("Zoom: Choose for scaling the cross section plane view")
        zoom_cs.toggled.connect(self.zoom_cs_action)
        zoom_cs.setCheckable(True)
        zoom_cs.setIcon(QIcon(zoom_map))
        zoom_cs.setIconText("Zoom")
        self.cs_toolbar.addAction(zoom_cs)
        self.zoom_cs = zoom_cs

        translate_ref = QAction("PointMove", self)
        translate_ref.setStatusTip("PointMove: Choose for moving the reference point of the cross section plane")
        translate_ref.toggled.connect(self.translate_ref_action)
        translate_ref.setCheckable(True)
        arrow_black_map = QPixmap(":/icons/arrow_black.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        translate_ref.setIcon(QIcon(arrow_black_map))
        translate_ref.setIconText("PointMove")
        self.cs_toolbar.addAction(translate_ref)
        self.translate_ref = translate_ref

        ref_point_x_value = QDoubleSpinBox()
        ref_point_x_value.setPrefix("X: ")
        ref_point_x_value.setMaximum(1000000)
        ref_point_x_value.setMinimum(-1000000)
        ref_point_x_value.valueChanged.connect(self.ref_point_x_spin_translate_action)
        self.cs_toolbar.addWidget(ref_point_x_value)
        self.ref_point_x_value = ref_point_x_value

        ref_point_y_value = QDoubleSpinBox()
        ref_point_y_value.setPrefix("Y: ")
        ref_point_y_value.setMaximum(1000000)
        ref_point_y_value.setMinimum(-1000000)
        ref_point_y_value.valueChanged.connect(self.ref_point_y_spin_translate_action)
        self.cs_toolbar.addWidget(ref_point_y_value)
        self.ref_point_y_value = ref_point_y_value

        rotate_lattice = QAction("Rotate", self)
        rotate_lattice.setStatusTip("Rotate: Choose for rotating the cross section plane view")
        rotate_lattice.toggled.connect(self.rotate_lattice_action)
        rotate_lattice.setCheckable(True)
        rotate_map = QPixmap(":/icons/rotate_black.png").scaled(QSize(256, 256), Qt.AspectRatioMode.IgnoreAspectRatio)
        rotate_lattice.setIcon(QIcon(rotate_map))
        rotate_lattice.setIconText("Rotate")
        self.cs_toolbar.addAction(rotate_lattice)
        self.rotate_lattice = rotate_lattice

        cs_angle = QDoubleSpinBox()
        cs_angle.setSuffix("°")
        cs_angle.setMaximum(1000000)
        cs_angle.setMinimum(-1000000)
        cs_angle.valueChanged.connect(self.spin_rotate_lattice_action)
        self.cs_toolbar.addWidget(cs_angle)
        self.cs_angle = cs_angle

        add_remove_helices = QAction("Add/Remove", self)
        add_remove_helices.setStatusTip("Add/Remove: Choose for editing the cross section")
        add_remove_helices.toggled.connect(self.add_remove_helices_action)
        add_remove_helices.setIcon(QIcon(add_points_map))
        add_remove_helices.setCheckable(True)
        self.cs_toolbar.addAction(add_remove_helices)
        self.add_remove_helices = add_remove_helices

        renumber = QAction("Renumber", self)
        renumber.setStatusTip("Renumber: Choose for manually setting helix numbers")
        renumber.toggled.connect(self.renumber_helices)
        renumber_map = QPixmap(":/icons/renum.png").scaled(QSize(256, 128), Qt.AspectRatioMode.IgnoreAspectRatio)
        renumber.setIcon(QIcon(renumber_map))
        renumber.setCheckable(True)
        self.cs_toolbar.addAction(renumber)
        self.renumber = renumber

        self.connected_helix = None
        renumber_box = QSpinBox()
        renumber_box.setMinimum(0)
        renumber_box.setMaximum(400)
        renumber_box.valueChanged.connect(self.spin_renumber_action)
        renumber_action = self.cs_toolbar.addWidget(renumber_box)
        self.renumber_box = renumber_box
        self.renumber_action = renumber_action
        self.renumber_action.setVisible(False)

        self.stored_cs = None
        cs_copy = QPushButton("Copy")
        cs_copy.clicked.connect(self.copy_cs_action)
        self.cs_toolbar.addWidget(cs_copy)

        cs_paste = QPushButton("Paste")
        cs_paste.clicked.connect(self.paste_cs_action)
        self.cs_toolbar.addWidget(cs_paste)

        menu_bar = QMenuBar(None)
        main_menu = QMenu("AutoMod")
        user_settings = QAction("User Settings", self)
        user_settings.triggered.connect(self.set_settings_action)
        main_menu.addAction(user_settings)
        export_hnodes = QAction("Export Helix Nodes", self)
        export_hnodes.triggered.connect(self.export_tool_action)
        self.export_tool = export_hnodes
        main_menu.addAction(export_hnodes)
        menu_bar.addMenu(main_menu)

        self.setMenuBar(menu_bar)
        self.settings_window = QWidget()
        self.init_settings_window()

        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)

        self.setWindowTitle("AutoMod")

    @Slot(float)
    def spin_interhelical_gap_action(self, value):
        self.parameters['ihg'] = value
        for _, node_lst in self.scene.get_storage().get_nodes().items():
            node_lst[0].redraw_lattice()

    @Slot(float)
    def spin_helix_diameter_action(self, value):
        self.parameters['hd'] = value
        for _, node_lst in self.scene.get_storage().get_nodes().items():
            node_lst[0].redraw_lattice()

    @Slot(float)
    def spin_nucleotide_length_action(self, value):
        self.parameters['ntl'] = value

    @Slot(float)
    def spin_mod_length_action(self, value):
        self.parameters['ml'] = value

    @Slot(float)
    def spin_turn_length_action(self, value):
        self.parameters['tl'] = value

    @Slot(float)
    def spin_mind_action(self, value):
        self.parameters['min_d'] = int(value)

    @Slot(float)
    def spin_grid_scale_action(self, value):
        self.parameters['gs'] = value
        self.scene.update_grid_scale()
        self.scene.get_storage().redraw_grid()
        self.view.init_fit()
        self.view.update()

    @Slot(bool)
    def check_mods_action(self, state):
        if state == Qt.CheckState.Checked:
            self.parameters['mods'] = True
        else:
            self.parameters['mods'] = False

    @Slot(bool)
    def check_cos_action(self, state):
        if state == Qt.CheckState.Checked:
            self.parameters['cos'] = True
        else:
            self.parameters['cos'] = False

    @Slot(bool)
    def check_staple_loops_action(self, state):
        if state == Qt.CheckState.Checked:
            self.parameters['sl'] = True
        else:
            self.parameters['sl'] = False

    @Slot(bool)
    def spin_buffer_action(self, value):
        self.parameters["buffer"] = value

    @Slot(float)
    def spin_twist_max_action(self, value):
        self.parameters["tt_max"] = value

    @Slot(float)
    def spin_rho_start_action(self, value):
        self.parameters["rho_start"] = value

    @Slot(float)
    def spin_margin_over_action(self, value):
        self.parameters["margin_over"] = value

    @Slot(float)
    def spin_margin_under_action(self, value):
        self.parameters["margin_under"] = value

    @Slot(float)
    def spin_zoom_value(self, value):
        self.parameters['zs'] = (1 / value)

    @Slot(float)
    def spin_translate_value(self, value):
        self.parameters['ts'] = (1 / value)

    @Slot(float)
    def spin_rotate_value(self, value):
        self.parameters['rs'] = (1 / value)

    @Slot(bool)
    def grid_bool_action(self, state):
        if state == Qt.CheckState.Checked:
            self.parameters['grid'] = True
        else:
            self.parameters['grid'] = False

    @Slot(float)
    def set_seed(self, value):
        random.seed(int(value))

    def init_settings_window(self):
        self.settings_window.setWindowTitle("User Settings")
        self.settings_window.setMinimumWidth(400)
        self.settings_window.setMinimumHeight(200)
        window_layout = QGridLayout()
        self.settings_window.setLayout(window_layout)

        tabs = QTabWidget()
        window_layout.addWidget(tabs)
        parameter_page = QWidget()
        parameter_layout = QGridLayout()
        parameter_page.setLayout(parameter_layout)
        tabs.addTab(parameter_page, "Parameters")
        view_control_page = QWidget()
        view_control_layout = QGridLayout()
        view_control_page.setLayout(view_control_layout)
        tabs.addTab(view_control_page, "View control")

        view_control_layout.addWidget(QLabel("Zoom sensitivity:"), 0, 0)
        zoom_value = QDoubleSpinBox()
        zoom_value.setSingleStep(0.01)
        zoom_value.setMinimum(0.01)
        zoom_value.setValue(self.parameters["zs"])
        zoom_value.valueChanged.connect(self.spin_zoom_value)
        view_control_layout.addWidget(zoom_value, 1, 0)

        view_control_layout.addWidget(QLabel("Translate sensitivity:"), 2, 0)
        translate_value = QDoubleSpinBox()
        translate_value.setSingleStep(0.01)
        translate_value.setMinimum(0.01)
        translate_value.setValue(self.parameters["ts"])
        translate_value.valueChanged.connect(self.spin_translate_value)
        view_control_layout.addWidget(translate_value, 3, 0)

        view_control_layout.addWidget(QLabel("Rotate sensitivity:"), 4, 0)
        rotate_value = QDoubleSpinBox()
        rotate_value.setSingleStep(0.01)
        rotate_value.setMinimum(0.01)
        rotate_value.setValue(self.parameters["rs"])
        rotate_value.valueChanged.connect(self.spin_rotate_value)
        view_control_layout.addWidget(rotate_value, 5, 0)

        view_control_layout.addWidget(QLabel("Grid scale"), 6, 0)
        grid_scale_value = QSpinBox()
        grid_scale_value.setSuffix(" nm/interval")
        grid_scale_value.setSingleStep(1)
        grid_scale_value.setMinimum(1)
        grid_scale_value.setMaximum(99)
        grid_scale_value.setValue(self.parameters["gs"])
        grid_scale_value.valueChanged.connect(self.spin_grid_scale_action)
        view_control_layout.addWidget(grid_scale_value, 7, 0)

        grid_bool = QCheckBox("Show grid")
        view_control_layout.addWidget(grid_bool)
        grid_bool.setChecked(True)
        grid_bool.checkStateChanged.connect(self.grid_bool_action)
        view_control_layout.addWidget(grid_bool, 8, 0)

        parameter_layout.addWidget(QLabel("Interhelical gap:"), 0, 0)
        interhelical_gap_value = QDoubleSpinBox()
        interhelical_gap_value.setSuffix(" nm")
        interhelical_gap_value.setSingleStep(0.01)
        interhelical_gap_value.setMinimum(0)
        interhelical_gap_value.setMaximum(10)
        interhelical_gap_value.setValue(self.parameters["ihg"])
        interhelical_gap_value.valueChanged.connect(self.spin_interhelical_gap_action)
        parameter_layout.addWidget(interhelical_gap_value, 1, 0)

        parameter_layout.addWidget(QLabel("Helix diameter:"), 2, 0)
        helix_diameter_value = QDoubleSpinBox()
        helix_diameter_value.setSuffix(" nm")
        helix_diameter_value.setSingleStep(0.01)
        helix_diameter_value.setMinimum(0.01)
        helix_diameter_value.setMaximum(10)
        helix_diameter_value.setValue(self.parameters["hd"])
        helix_diameter_value.valueChanged.connect(self.spin_helix_diameter_action)
        parameter_layout.addWidget(helix_diameter_value, 3, 0)

        parameter_layout.addWidget(QLabel("Rise per base pair:"), 4, 0)
        nucleotide_length_value = QDoubleSpinBox()
        nucleotide_length_value.setSuffix(" nm")
        nucleotide_length_value.setSingleStep(0.01)
        nucleotide_length_value.setValue(self.parameters["ntl"])
        nucleotide_length_value.valueChanged.connect(self.spin_nucleotide_length_action)
        parameter_layout.addWidget(nucleotide_length_value, 5, 0)

        parameter_layout.addWidget(QLabel("Base pairs per turn:"), 6, 0)
        turn_length_value = QDoubleSpinBox()
        turn_length_value.setSuffix(" bp")
        turn_length_value.setSingleStep(0.1)
        turn_length_value.setDecimals(1)
        turn_length_value.setValue(self.parameters["tl"])
        turn_length_value.valueChanged.connect(self.spin_turn_length_action)
        parameter_layout.addWidget(turn_length_value, 7, 0)

        parameter_layout.addWidget(QLabel("Min. crossover separation"), 8, 0)
        min_d_value = QDoubleSpinBox()
        min_d_value.setSuffix(" bp")
        min_d_value.setSingleStep(1.0)
        min_d_value.setDecimals(0)
        min_d_value.setValue(self.parameters["min_d"])
        min_d_value.valueChanged.connect(self.spin_mind_action)
        parameter_layout.addWidget(min_d_value, 9, 0)

        parameter_layout.addWidget(QLabel("Seed"), 10, 0)
        seed_value = QDoubleSpinBox()
        seed_value.setSingleStep(1.0)
        seed_value.setDecimals(0)
        seed_value.setValue(self.parameters["seed"])
        seed_value.valueChanged.connect(self.set_seed)
        parameter_layout.addWidget(seed_value, 11, 0)

        parameter_layout.setColumnMinimumWidth(1, 10)

        mods_value = QCheckBox("Write modifications to output file")
        mods_value.setChecked(True)
        mods_value.checkStateChanged.connect(self.check_mods_action)
        parameter_layout.addWidget(mods_value, 0, 2)

        cos_value = QCheckBox("Write crossovers to output file")
        cos_value.setChecked(True)
        cos_value.checkStateChanged.connect(self.check_cos_action)
        parameter_layout.addWidget(cos_value, 1, 2)

        sl_value = QCheckBox("Allow staple loops between adjacent helices")
        sl_value.setChecked(True)
        sl_value.checkStateChanged.connect(self.check_staple_loops_action)
        parameter_layout.addWidget(sl_value, 2, 2)

        parameter_layout.addWidget(QLabel("No crossovers over last/first:"), 3, 2)
        buffer_value = QDoubleSpinBox()
        buffer_value.setSuffix(" bp")
        buffer_value.setSingleStep(1.0)
        buffer_value.setDecimals(0)
        buffer_value.setValue(self.parameters["buffer"])
        buffer_value.valueChanged.connect(self.spin_buffer_action)
        parameter_layout.addWidget(buffer_value, 4, 2)

        parameter_layout.addWidget(QLabel("Max. phase offset at crossover:"), 5, 2)
        twist_max_value = QDoubleSpinBox()
        twist_max_value.setSuffix(" rad")
        twist_max_value.setSingleStep(0.01)
        twist_max_value.setValue(self.parameters["tt_max"])
        twist_max_value.valueChanged.connect(self.spin_twist_max_action)
        parameter_layout.addWidget(twist_max_value, 6, 2)

        parameter_layout.addWidget(QLabel("Target crossover density:"), 7, 2)
        rho_start_value = QDoubleSpinBox()
        rho_start_value.setSuffix(" (1/bp)")
        rho_start_value.setSingleStep(0.001)
        rho_start_value.setDecimals(3)
        rho_start_value.setValue(self.parameters["rho_start"])
        rho_start_value.valueChanged.connect(self.spin_rho_start_action)
        parameter_layout.addWidget(rho_start_value, 8, 2)

        parameter_layout.addWidget(QLabel("Effective rise per modification:"), 13, 2)
        mod_length_value = QDoubleSpinBox()
        mod_length_value.setSuffix(" nm")
        mod_length_value.setSingleStep(0.001)
        mod_length_value.setDecimals(3)
        mod_length_value.setValue(self.parameters["ml"])
        mod_length_value.valueChanged.connect(self.spin_mod_length_action)
        parameter_layout.addWidget(mod_length_value, 14, 2)

        parameter_layout.addWidget(QLabel("Margin (over):"), 9, 2)
        margin_value = QDoubleSpinBox()
        margin_value.setSuffix(" (1/bp)")
        margin_value.setSingleStep(0.001)
        margin_value.setDecimals(3)
        margin_value.setValue(self.parameters["margin_over"])
        margin_value.valueChanged.connect(self.spin_margin_over_action)
        parameter_layout.addWidget(margin_value, 10, 2)

        parameter_layout.addWidget(QLabel("Margin (under):"), 11, 2)
        margin_value = QDoubleSpinBox()
        margin_value.setSuffix(" (1/bp)")
        margin_value.setSingleStep(0.001)
        margin_value.setDecimals(3)
        margin_value.setValue(self.parameters["margin_under"])
        margin_value.valueChanged.connect(self.spin_margin_under_action)
        parameter_layout.addWidget(margin_value, 12, 2)

    @Slot(bool)
    def set_settings_action(self):
        self.settings_window.show()

    def create_json_dct(self, json_name, maps):
        json_dct = {}
        json_dct["name"] = json_name.split(sep="/")[-1] + ".json"
        helices = self.scene.get_storage().get_all_helices()
        json_dct["vstrands"] = []
        max_len = 0
        for helix, mod_array in maps[0][0].items():
            cur_len = len(mod_array.tolist()[0])
            if cur_len > max_len:
                max_len = cur_len
        for number, pos in helices.items():
            helix_dct = {}
            helix_dct["row"] = pos[1]
            helix_dct["col"] = pos[0]
            helix_dct["num"] = int(number)
            scaf_lst = []
            stap_lst = []
            loops = []
            skips = []
            if self.lattice == 1:
                modulo = 21
            else:
                modulo = 32
            for i in range(max_len):
                loops.append(0)
                skips.append(0)
                if pos[2]:
                    # odd helix
                    if i == 0:
                        scaf_lst.append([number, i+1, -1, -1])
                        stap_lst.append([-1, -1, number, i+1])
                    elif i == max_len-1:
                        scaf_lst.append([-1, -1, number, i-1])
                        stap_lst.append([number, i-1, -1, -1])
                    else:
                        scaf_lst.append([number, i+1, number, i-1])
                        stap_lst.append([number, i-1, number, i+1])
                else:
                    # even helix
                    if i == 0:
                        scaf_lst.append([-1, -1, number, i+1])
                        stap_lst.append([number, i+1, -1, -1])
                    elif i == max_len-1:
                        scaf_lst.append([number, i-1, -1, -1])
                        stap_lst.append([-1, -1, number, i-1])
                    else:
                        scaf_lst.append([number, i-1, number, i+1])
                        stap_lst.append([number, i+1, number, i-1])
            for i in range(modulo - max_len % modulo):
                loops.append(0)
                skips.append(0)
                scaf_lst.append([-1, -1, -1, -1])
                stap_lst.append([-1, -1, -1, -1])
            helix_dct["scaf"] = scaf_lst
            helix_dct["stap"] = stap_lst
            helix_dct["loop"] = loops
            helix_dct["skip"] = skips
            helix_dct["scafLoop"] = []
            helix_dct["stapLoop"] = []
            helix_dct["stap_colors"] = []
            helix_dct["scaf_colors"] = []
            json_dct["vstrands"].append(helix_dct)
        return json_dct 

    @Slot(bool)
    def write_tool_action(self, checked):
        if checked and self.scene.get_storage().has_mod_map():
            maps = self.scene.get_storage().get_mod_maps()
            file_name = QFileDialog.getSaveFileName(self, caption="Write to file", filter="caDNAno files (*.json)")
            if not file_name[0] == '':
                if len(maps) > 1:
                    self.ehandler.showMessage("There are several curves defined at the moment. "
                                              "Remove redundant curves.")
                else:
                    dct = self.create_json_dct(file_name[0], maps)
                    if self.parameters["cos"]:
                        pruned_cos, stats, solved = self.prune_cos_new(self.scene.get_storage().get_curve())
                        if not solved:
                            self.ehandler.showMessage("No crossover pattern found.")
                        else:
                            with open(file_name[0] + "_stats.txt", "w", encoding="utf-8") as f:
                                f.write(stats)
                            for helix_number, mod_array in maps[0][0].items():
                                self.write_cos(dct, helix_number, pruned_cos[helix_number])
                    if self.parameters["mods"]:
                        for helix_number, mod_array in maps[0][0].items():
                            self.write_loops_skips(dct, helix_number, mod_array)
                    with open(file_name[0] + ".json", "w", encoding="utf-8") as f:
                        json.dump(dct, f)
        self.write_tool.setChecked(False)

    @Slot(bool)
    def read_tool_action(self, checked):
        if checked:
            file_name = QFileDialog.getOpenFileName(self, caption="Read nodes from", filter="csv files (*.txt *.csv)")
            if not file_name[0] == '':
                with open(file_name[0], "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            coords = line.split(',')
                            x = float(coords[0])
                            y = float(coords[1])
                            z = float(coords[2])
                            self.scene.get_storage().add_node_from_file(x, y, z)
                        except:
                            self.ehandler.showMessage("File format error. Give x, y, z as comma separated values, one position per line.")
        self.read_tool.setChecked(False)

    @Slot(bool)
    def export_tool_action(self):
        file_name = QFileDialog.getSaveFileName(self, caption="Export to file", filter="csv files (*.txt *.csv)")
        if not file_name[0] == '':
            with open(file_name[0] + ".txt", "w", encoding="utf-8") as f:
                hnodes = self.scene.get_storage().get_helix_knots()
                if hnodes is not None:
                    for h, nodes in hnodes.items():
                        f.write("{}\n".format(int(h)))
                        for i in range(len(nodes[0])):
                            f.write("{}, {}, {}\n".format(nodes[0][i], nodes[1][i], nodes[2][i]))                       

    @staticmethod
    def find_next_crossover(helices, adjacency_check, mods, curve, max_tol, margin_over, min_d, twist_dict, new_twist_dict, co_counts_matrix, rho_target):
        current_rho = np.zeros(len(helices))
        for i, h in enumerate(helices):
            current_rho[i] = np.count_nonzero(adjacency_check[i, :]) / (len(adjacency_check[i, :])+ np.sum(mods[h]))
        ind1 = np.argsort(current_rho)[0]
        helix1 = helices[ind1]     
        neighbours = curve.get_neighbours(helix1)
        n_inds = []
        for neighbor in neighbours:
            n_inds.append(np.argwhere(np.array(helices) == neighbor)[0][0])         
        inds2 = np.argsort(current_rho[n_inds])
        prev_found = False
        new_co = ""
        for i in range(len(inds2)):
            tolerance = 0.00
            ind2 = n_inds[inds2[i]]
            helix2 = helices[ind2]
            pos_lst = list(range(len(twist_dict[helix1])))
            random.shuffle(pos_lst)
            print('Looking for a co between helices {} and {}.'.format(helix1, helix2))
            while not prev_found and tolerance <= max_tol:
                tolerance += 0.10
                for j in pos_lst:
                    for helix, d_rad in twist_dict[helix1][j].items():
                        place = False
                        if d_rad[0] < tolerance and helix == helix2:
                            if np.count_nonzero(adjacency_check[ind1, max(0, j-min_d-2):min(adjacency_check.shape[1]-1, j+min_d-1)]) == 0:
                                if np.count_nonzero(adjacency_check[ind2, max(0, j-min_d-2):min(adjacency_check.shape[1]-1, j+min_d-1)]) == 0:
                                    if np.flatnonzero(adjacency_check[ind1, :]).size == 0:
                                        place = True
                                    elif np.flatnonzero(adjacency_check[ind1, 0:j]).size != 0 and np.flatnonzero(adjacency_check[ind1, j+1:-1]).size == 0:
                                        if (helix2 + 1) != adjacency_check[ind1, np.flatnonzero(adjacency_check[ind1, 0:j])[-1]]:
                                            place = True
                                    elif np.flatnonzero(adjacency_check[ind1, j+1:-1]).size != 0 and np.flatnonzero(adjacency_check[ind1, 0:j]).size == 0:
                                        if (helix2 + 1) != adjacency_check[ind1, np.flatnonzero(adjacency_check[ind1, j+1:-1])[0]+j+1]:
                                            place = True
                                    elif np.flatnonzero(adjacency_check[ind1, 0:j]).size != 0 and np.flatnonzero(adjacency_check[ind1, j+1:-1]).size != 0:
                                        if (helix2 + 1) != adjacency_check[ind1, np.flatnonzero(adjacency_check[ind1, 0:j])[-1]] and (ind2 + 1) != adjacency_check[ind1, np.flatnonzero(adjacency_check[ind1, j+1:-1])[0]+j+1]:
                                            place = True
                                    c1 = np.count_nonzero(adjacency_check[ind1, :]) / (len(adjacency_check[ind1, :])+np.sum(mods[helix1])) < rho_target + margin_over
                                    c2 = np.count_nonzero(adjacency_check[ind2, :]) / len(adjacency_check[ind2, :]+np.sum(mods[helix2])) < rho_target + margin_over
                                    if place and c1 and c2:
                                        co_counts_matrix[ind1, ind2] += 1
                                        co_counts_matrix[ind2, ind1] += 1
                                        adjacency_check[ind1, j] = helix2 + 1
                                        adjacency_check[ind2, j] = helix1 + 1
                                        new_twist_dict[helix1][j][helix2] = (True, False)
                                        new_twist_dict[helix2][j][helix1] = (True, False)
                                        prev_found = True
                                        new_co += "{:}, {:}, {:}, {:.1f}\n".format(int(np.sum(co_counts_matrix)/2), helix1, helix2, tolerance)
                                        print("Found crossover number {:} between helix {:} and helix {:} with phase offsets below {:.1f} (rad).".format(int(np.sum(co_counts_matrix)/2), helix1, helix2, tolerance))
                                        break
                    if prev_found:
                        break
                else:
                    prev_found = False

            if prev_found:
                break
        else:
            return False, new_co
        return True, new_co

    @staticmethod
    def find_next_loop(helices, adjacency_check, mods, curve, max_tol, margin_over, min_d, twist_dict, new_twist_dict, co_counts_matrix, rho_target):
        current_rho = np.zeros(len(helices))
        for i, h in enumerate(helices):
            current_rho[i] = np.count_nonzero(adjacency_check[i, :]) / (len(adjacency_check[i, :])+ np.sum(mods[h]))
        ind1 = np.argsort(current_rho)[0]
        helix1 = helices[ind1]        
        neighbours = curve.get_neighbours(helix1)
        n_inds = []
        for neighbor in neighbours:
            n_inds.append(np.argwhere(np.array(helices) == neighbor)[0][0])
        inds2 = np.argsort(current_rho[n_inds])
        prev_found = False
        new_loop = ""
        for i in range(len(inds2)):
            tolerance = 0.00  
            ind2 = n_inds[inds2[i]]
            helix2 = helices[ind2]
            pos_lst = list(range(len(twist_dict[helix1])))
            random.shuffle(pos_lst)
            print('Looking for a co (LOOP) between helices {} and {}.'.format(helix1, helix2))
            while not prev_found and tolerance <= max_tol:
                tolerance += 0.10
                for j in pos_lst:
                    for helix, d_rad in twist_dict[helix1][j].items():
                        if d_rad[0] < tolerance and helix == helix2:
                            if np.count_nonzero(adjacency_check[ind1, max(0, j-min_d-2):min(adjacency_check.shape[1]-1, j+min_d-1)]) == 0:
                                c1 = np.count_nonzero(adjacency_check[ind1, :]) / (len(adjacency_check[ind1, :])+np.sum(mods[helix1])) < rho_target + margin_over
                                c2 = np.count_nonzero(adjacency_check[ind2, :]) / (len(adjacency_check[ind2, :])+np.sum(mods[helix2])) < rho_target + margin_over
                                if np.count_nonzero(adjacency_check[ind2, max(0, j-min_d-2):min(adjacency_check.shape[1]-1, j+min_d-1)]) == 0 and c1 and c2:
                                    co_counts_matrix[ind1, ind2] += 1
                                    co_counts_matrix[ind2, ind1] += 1
                                    adjacency_check[ind1, j] = helix2 + 1
                                    adjacency_check[ind2, j] = helix1 + 1
                                    new_twist_dict[helix1][j][helix2] = (True, False)
                                    new_twist_dict[helix2][j][helix1] = (True, False)
                                    prev_found = True
                                    new_loop += "{:}, {:}, {:}, {:.1f}, LOOP\n".format(int(np.sum(co_counts_matrix)/2), helix1, helix2, tolerance)
                                    print("Found crossover number {:} between helix {:} and helix {:} with phase offsets below {:.1f} (rad), LOOP.".format(int(np.sum(co_counts_matrix)/2), helix1, helix2, tolerance))
                                    break
                    if prev_found:
                        break
                else:
                    prev_found = False

            if prev_found:
                break
        else:
            return False, new_loop
        return True, new_loop

    @staticmethod
    def check_density(adjacency_check, mods, helices, rho_target, margin_under):
        correct_density = True
        print("Checking densities...")
        for h in range(adjacency_check.shape[0]):
            if np.count_nonzero(adjacency_check[h, :]) / (len(adjacency_check[h, :])+np.sum(mods[helices[h]]))  < max(0, rho_target - margin_under):
                correct_density = False
                print("Densities not correct. Helix {:} has density {:.4f} (1/bp) below target {:.4f} (1/bp).".format(helices[h], np.count_nonzero(adjacency_check[h, :]) / (len(adjacency_check[h, :])+np.sum(mods[helices[h]])), max(0, rho_target)))
                break
        return correct_density

    def prune_cos_new(self, curve):
        min_d = self.parameters['min_d']
        max_tol = self.parameters['tt_max']
        margin_over = self.parameters['margin_over']
        margin_under = self.parameters['margin_under']
        rho_target = self.parameters['rho_start']

        print("Searching correct densities with target {} (1/bp).\n".format(rho_target))
        twist_dict = curve.get_twist_num()
        mods = curve.get_mods()
        new_twist_dict = {}
        co_counts_matrix = np.zeros((len(list(twist_dict)), len(list(twist_dict))))
        helices = sorted(twist_dict)
        for helix in helices:
            new_twist_dict[helix] = [{} for _ in range(len(twist_dict[helices[0]]))]
        adjacency_check = np.zeros((len(list(twist_dict)), len(twist_dict[helices[0]])))

        co_stats = ""
        loop_stats = ""
        
        prev_found = True
        prev_co_found = True
        prev_loop_found = True
        while prev_found:
            while prev_co_found and not self.check_density(adjacency_check, mods, helices, rho_target, margin_under):
                prev_co_found, new_co = self.find_next_crossover(helices, adjacency_check, mods, curve, max_tol, margin_over, min_d, twist_dict, new_twist_dict, co_counts_matrix, rho_target)
                co_stats += new_co
            if self.parameters['sl'] and not self.check_density(adjacency_check, mods, helices, rho_target, margin_under):
                prev_loop_found, new_loop = self.find_next_loop(helices, adjacency_check, mods, curve, max_tol, margin_over, min_d, twist_dict, new_twist_dict, co_counts_matrix, rho_target)
                loop_stats += new_loop
            else:
                prev_loop_found = False
            if (not prev_co_found and not prev_loop_found) or self.check_density(adjacency_check, mods, helices, rho_target, margin_under):
                prev_found = False
            else:
                prev_co_found = True

        if self.check_density(adjacency_check, mods, helices, rho_target, margin_under):
            print("Solved.")
        else:
            print("Not solved.")
            return new_twist_dict, co_stats + loop_stats, False

        summary = ""
        for h in range(adjacency_check.shape[0]):
            summary += "Helix {:} has an average crossover density of {:}/{:} = {:.4f} (1/bp). Target is {:.4f} (1/bp).\n".format(helices[h], np.count_nonzero(adjacency_check[h, :]), int(len(adjacency_check[h, :])+np.sum(mods[helices[h]])),
                                                                                                                                   np.count_nonzero(adjacency_check[h, :]) / (len(adjacency_check[h, :])+np.sum(mods[helices[h]])), rho_target)            
        return new_twist_dict, co_stats + loop_stats + summary, True
            

    @staticmethod
    def write_loops_skips(dct, helix_number, mod_array):
        if "vstrands" in dct:
            for strand in dct["vstrands"]:
                if strand["num"] == helix_number:
                    strand["loop"][0:len(np.where(mod_array == 1, 1, 0).tolist()[0])] = np.where(mod_array == 1, 1, 0).tolist()[0]
                    strand["skip"][0:len(np.where(mod_array == -1, -1, 0).tolist()[0])] = np.where(mod_array == -1, -1, 0).tolist()[0]
                    return True
            else:
                return False
        else:
            return False

    def write_cos(self, dct, helix_number, twist_lst):
        if "vstrands" in dct:
            buffer = self.parameters["buffer"]
            for strand in dct["vstrands"]:
                if strand["num"] == helix_number:
                    skip = False
                    for i, pos in enumerate(strand["scaf"][0:len(twist_lst)]):
                        if buffer-1 < i < len(twist_lst) - buffer and len(twist_lst[i]) > 0 and not skip:
                            for helix, co_type in twist_lst[i].items():
                                if co_type[1] and pos[0] == helix_number and pos[2] == helix_number and helix_number % 2 == 0:
                                    pos[2] = helix
                                    pos[3] = pos[1] + 1
                                    skip = True
                                    strand["scaf"][i+1][0] = -1
                                    strand["scaf"][i+1][1] = -1
                                elif co_type[1] and pos[0] == helix_number and pos[2] == helix_number and helix_number % 2 == 1:
                                    pos[0] = helix
                                    pos[1] = pos[3] + 1
                                    skip = True
                                    strand["scaf"][i+1][2] = -1
                                    strand["scaf"][i+1][3] = -1
                                break
                        else:
                            skip = False
                    skip = False
                    for i, pos in enumerate(strand["stap"][0:len(twist_lst)]):
                        if buffer-1 < i < len(twist_lst) - buffer and len(twist_lst[i]) > 0 and not skip:
                            for helix, co_type in twist_lst[i].items():
                                if co_type[0] and pos[0] == helix_number and pos[2] == helix_number and helix_number % 2 == 0:
                                    strand["stap"][i][0] = helix
                                    strand["stap"][i][1] = i
                                    skip = True
                                    strand["stap"][i+1][2] = helix
                                    strand["stap"][i+1][3] = i+1
                                elif co_type[0] and pos[0] == helix_number and pos[2] == helix_number and helix_number % 2 == 1:
                                    strand["stap"][i][2] = helix
                                    strand["stap"][i][3] = i
                                    skip = True
                                    strand["stap"][i+1][0] = helix
                                    strand["stap"][i+1][1] = i+1
                                break
                        else:
                            skip = False
                    return True
            else:
                return False
        else:
            return False

    def connect_to_renumber(self, helix):
        if self.connected_helix is not None:
            self.connected_helix.connected_to_renumber(False)
        self.connected_helix = helix
        self.connected_helix.connected_to_renumber(True)
        self.renumber_box.setValue(self.connected_helix.get_number())

    def disconnect_from_renumber(self):
        if self.connected_helix is not None:
            self.connected_helix.connected_to_renumber(False)
            self.connected_helix.update()
            self.connected_helix = None

    @Slot(int)
    def spin_renumber_action(self, value):
        if self.connected_helix is not None:
            if value < self.connected_helix.get_number() and self.connected_helix.get_number() - 2 >= 0:
                self.connected_helix.renumber(self.connected_helix.get_number() - 2)
            elif value > self.connected_helix.get_number():
                self.connected_helix.renumber(self.connected_helix.get_number() + 2)

    @Slot()
    def copy_cs_action(self):
        self.translate_ref.setChecked(False)
        self.zoom_cs.setChecked(False)
        self.rotate_lattice.setChecked(False)
        self.add_remove_helices.setChecked(False)
        self.renumber.setChecked(False)
        if self.cs_node is not None:
            self.cs_node.save_cs_angle(self.cs_view.get_rotation_amount())
            self.cs_node.save_cs_transform(self.cs_view.transform())
            self.cs_node.set_ref_point(self.cs_view.get_ref_point())
            self.stored_cs = [self.cs_node.get_cs_scene(), self.cs_view.get_ref_point(),
                              self.cs_view.get_rotation_amount(), self.cs_view.transform(),
                              self.cs_node.get_lattice_type()]

    @Slot()
    def paste_cs_action(self):
        if self.cs_node is not None and self.stored_cs is not None:
            self.cs_node.change_scene(self.stored_cs)
            self.activate_cs_tool()

    @Slot(float)
    def ref_point_x_spin_translate_action(self, dx):
        if self.cs_view.get_ref_point() is not None:
            try:
                delta = dx - self.cs_view.get_ref_point().x()
                if np.abs(delta) >= 0.01:
                    self.cs_view.get_ref_point().setPos(self.cs_view.get_ref_point().x() + delta, self.cs_view.get_ref_point().y())
            except RuntimeError:
                pass

    @Slot(float)
    def ref_point_y_spin_translate_action(self, dy):
        if self.cs_view.get_ref_point() is not None:
            try:
                delta = dy - self.cs_view.get_ref_point().y()
                if np.abs(delta) >= 0.01:
                    self.cs_view.get_ref_point().setPos(self.cs_view.get_ref_point().x(), self.cs_view.get_ref_point().y() + delta)
            except RuntimeError:
                pass

    @Slot(float)
    def spin_rotate_lattice_action(self, theta):
        delta = theta - self.cs_view.get_rotation_amount()
        if np.abs(delta) >= 0.01:
            self.cs_view.rotate(delta)
            self.cs_view.set_rotation_amount(self.cs_view.get_rotation_amount() + delta)

    @Slot(bool)
    def zoom_cs_action(self, checked):
        if checked:
            self.translate_ref.setChecked(False)
            self.rotate_lattice.setChecked(False)
            self.renumber.setChecked(False)
            self.add_remove_helices.setChecked(False)
            self.cs_view.activate_zoom()
        else:
            self.cs_view.deactivate_zoom()

    @Slot(bool)
    def renumber_helices(self, checked):
        if checked:
            self.renumber_action.setVisible(True)
            self.translate_ref.setChecked(False)
            self.rotate_lattice.setChecked(False)
            self.zoom_cs.setChecked(False)
            self.add_remove_helices.setChecked(False)
            self.cs_view.enable_helix_renumbering()
        else:
            self.disconnect_from_renumber()
            self.cs_view.disable_helix_renumbering()
            self.renumber_action.setVisible(False)

    @Slot(bool)
    def add_remove_helices_action(self, checked):
        if checked:
            self.translate_ref.setChecked(False)
            self.rotate_lattice.setChecked(False)
            self.zoom_cs.setChecked(False)
            self.renumber.setChecked(False)
            self.cs_view.enable_helix_editing()
        else:
            self.cs_view.disable_helix_editing()

    @Slot(bool)
    def translate_ref_action(self, checked):
        if checked:
            self.zoom_cs.setChecked(False)
            self.rotate_lattice.setChecked(False)
            self.add_remove_helices.setChecked(False)
            self.renumber.setChecked(False)
            self.cs_view.activate_translate_ref()
        else:
            self.cs_view.deactivate_translate_ref()

    @Slot(bool)
    def rotate_lattice_action(self, checked):
        if checked:
            self.zoom_cs.setChecked(False)
            self.translate_ref.setChecked(False)
            self.add_remove_helices.setChecked(False)
            self.cs_view.activate_rotate()
        else:
            self.cs_view.deactivate_rotate()

    @Slot(bool)
    def draw_hc_action(self, checked):
        if checked:
            self.cs_scene.clear()
            self.cs_angle.setValue(0)
            self.cs_view.setTransform(QTransform())
            rd = (self.parameters['hd'] * 10) / 2 + (self.parameters['ihg'] * 10) / 2
            n = 30
            dx = np.sqrt(3) * rd
            self.cs_scene.setSceneRect(0, 0, ((n - 1) * 2 * dx), 4 * ((n - 1) * rd + ((n - 1) // 2) * rd))
            ref_point = ReferencePoint(((n - 1) * dx) / 2, (n - 1) * rd + ((n - 1) // 2) * rd, 2)
            self.cs_scene.addItem(ref_point)
            self.cs_node.set_ref_point(ref_point)
            self.cs_node.set_lattice_type(1)
            self.lattice = 1
            ref_point.setZValue(10)
            self.cs_view.set_ref_point(ref_point)
            self.ref_point_x_value.setValue(ref_point.x())
            self.ref_point_y_value.setValue(ref_point.y())
            for i in range(n):
                for j in range(n+2):
                    self.cs_scene.addItem(HelixPoint(self.cs_node.get_ref_point(), j, i, self, 1))
            self.cs_view.centerOn(2 * ref_point.x(), 2 * ref_point.y())
            self.cs_view.update()
            self.draw_hc.setChecked(False)

    @Slot(bool)
    def draw_sq_action(self, checked):
        if checked:
            self.cs_scene.clear()
            self.cs_angle.setValue(0)
            self.cs_view.setTransform(QTransform())
            rd = (self.parameters['hd'] * 10) / 2 + (self.parameters["ihg"] * 10) / 2
            n = 50
            self.cs_scene.setSceneRect(0, 0, 2 * (rd + (n - 1) * 2 * rd), 2 * (rd + (n - 1) * 2 * rd) + 6 * rd)
            ref_point = ReferencePoint((rd + rd + (n - 1) * 2 * rd) / 2, (rd + rd + (n - 1) * 2 * rd) / 2, 2)
            self.cs_scene.addItem(ref_point)
            self.cs_node.set_ref_point(ref_point)
            self.cs_node.set_lattice_type(2)
            self.lattice = 2
            ref_point.setZValue(10)
            self.cs_view.set_ref_point(ref_point)
            self.ref_point_x_value.setValue(ref_point.x())
            self.ref_point_y_value.setValue(ref_point.y())
            for i in range(n):
                for j in range(n):
                    self.cs_scene.addItem(HelixPoint(self.cs_node.get_ref_point(), j, i, self, 2))
            self.cs_view.centerOn(2 * ref_point.x(), 2 * ref_point.y())
            self.cs_view.update()
            self.draw_sq.setChecked(False)

    def get_lattice(self):
        return self.lattice

    @Slot(bool)
    def add_points_action(self, checked):
        if checked:
            self.cutoff_view_tools()
            self.connect_points.setChecked(False)
            self.remove_point_selection()
            self.view.activate_add_points()
        else:
            self.view.deactivate_add_points()

    @Slot(bool)
    def delete_point_action(self, checked):
        if checked:
            self.scene.get_storage().delete_selected_point()
            self.delete_point.setChecked(False)

    @Slot(bool)
    def disconnect_prev_action(self, checked):
        if checked:
            self.scene.get_storage().delete_selected_prev()
            self.disconnect_prev.setChecked(False)

    @Slot(bool)
    def disconnect_next_action(self, checked):
        if checked:
            self.scene.get_storage().delete_selected_next()
            self.disconnect_next.setChecked(False)

    @Slot(bool)
    def interpolate_action(self, checked):
        if checked:
            if self.cs_node is not None:
                self.cs_node.save_cs_angle(self.cs_view.get_rotation_amount())
                self.cs_node.save_cs_transform(self.cs_view.transform())
            self.scene.get_storage().interpolate()
            self.interpolate.setChecked(False)

    @Slot(bool)
    def connect_points_action(self, checked):
        if checked:
            self.cutoff_view_tools()
            self.deactivate_point_tools()
            self.add_points.setChecked(False)
            self.remove_point_selection()
            self.deactivate_cs_tool()
            self.view.activate_connect_points()
        else:
            self.view.deactivate_connect_points()
            self.deactivate_connection_tools()
            self.remove_point_selection()

    @Slot(bool)
    def point_x_translate_action(self, checked):
        if checked:
            self.cutoff_view_tools()
            self.cutoff_drawing_tools()
            self.point_z_translate.setChecked(False)
            self.point_y_translate.setChecked(False)
            self.view.activate_point_x_translation()
        else:
            self.view.deactivate_point_x_translation()

    @Slot(bool)
    def point_y_translate_action(self, checked):
        if checked:
            self.cutoff_view_tools()
            self.cutoff_drawing_tools()
            self.point_x_translate.setChecked(False)
            self.point_z_translate.setChecked(False)
            self.view.activate_point_y_translation()
        else:
            self.view.deactivate_point_y_translation()

    @Slot(bool)
    def point_z_translate_action(self, checked):
        if checked:
            self.cutoff_view_tools()
            self.cutoff_drawing_tools()
            self.point_x_translate.setChecked(False)
            self.point_y_translate.setChecked(False)
            self.view.activate_point_z_translation()
        else:
            self.view.deactivate_point_z_translation()

    @Slot(bool)
    def x_translate_action(self, checked):
        if checked:
            self.y_translate.setChecked(False)
            self.z_translate.setChecked(False)
            self.x_rotate.setChecked(False)
            self.y_rotate.setChecked(False)
            self.z_rotate.setChecked(False)
            self.zoom.setChecked(False)
            self.cutoff_drawing_tools()
            self.view.activate_x_translation()
        else:
            self.view.deactivate_x_translation()

    @Slot(bool)
    def y_translate_action(self, checked):
        if checked:
            self.x_translate.setChecked(False)
            self.z_translate.setChecked(False)
            self.x_rotate.setChecked(False)
            self.y_rotate.setChecked(False)
            self.z_rotate.setChecked(False)
            self.zoom.setChecked(False)
            self.cutoff_drawing_tools()
            self.view.activate_y_translation()
        else:
            self.view.deactivate_y_translation()

    @Slot(bool)
    def z_translate_action(self, checked):
        if checked:
            self.x_translate.setChecked(False)
            self.y_translate.setChecked(False)
            self.x_rotate.setChecked(False)
            self.y_rotate.setChecked(False)
            self.z_rotate.setChecked(False)
            self.zoom.setChecked(False)
            self.cutoff_drawing_tools()
            self.view.activate_z_translation()
        else:
            self.view.deactivate_z_translation()

    @Slot(bool)
    def x_rotate_action(self, checked):
        if checked:
            self.x_translate.setChecked(False)
            self.y_translate.setChecked(False)
            self.z_translate.setChecked(False)
            self.z_rotate.setChecked(False)
            self.zoom.setChecked(False)
            self.y_rotate.setChecked(False)
            self.z_rotate.setChecked(False)
            self.cutoff_drawing_tools()
            self.view.activate_x_rotation()
        else:
            self.view.deactivate_x_rotation()

    @Slot(bool)
    def y_rotate_action(self, checked):
        if checked:
            self.x_translate.setChecked(False)
            self.y_translate.setChecked(False)
            self.z_translate.setChecked(False)
            self.zoom.setChecked(False)
            self.x_rotate.setChecked(False)
            self.z_rotate.setChecked(False)
            self.cutoff_drawing_tools()
            self.view.activate_y_rotation()
        else:
            self.view.deactivate_y_rotation()

    @Slot(bool)
    def z_rotate_action(self, checked):
        if checked:
            self.x_translate.setChecked(False)
            self.y_translate.setChecked(False)
            self.z_translate.setChecked(False)
            self.zoom.setChecked(False)
            self.x_rotate.setChecked(False)
            self.y_rotate.setChecked(False)
            self.cutoff_drawing_tools()
            self.view.activate_z_rotation()
        else:
            self.view.deactivate_z_rotation()

    @Slot(bool)
    def zoom_action(self, checked):
        if checked:
            self.x_translate.setChecked(False)
            self.y_translate.setChecked(False)
            self.z_translate.setChecked(False)
            self.x_rotate.setChecked(False)
            self.y_rotate.setChecked(False)
            self.z_rotate.setChecked(False)
            self.cutoff_drawing_tools()
            self.view.activate_zoom()
        else:
            self.view.deactivate_zoom()

    @Slot(bool)
    def restore_action(self, checked):
        if checked:
            self.x_translate.setChecked(False)
            self.y_translate.setChecked(False)
            self.z_translate.setChecked(False)
            self.x_rotate.setChecked(False)
            self.y_rotate.setChecked(False)
            self.z_rotate.setChecked(False)
            self.zoom.setChecked(False)
            self.cutoff_drawing_tools()
            self.deactivate_cs_tool()
            self.view.restore_view()
            self.restore.setChecked(False)

    @Slot(float)
    def point_x_spin_translate_action(self, d):
        delta = d - self.scene.get_storage().get_selected_node_pos()[0]
        if np.abs(delta) >= 0.005:
            self.scene.get_storage().translate_node(delta, 0, 0)

    @Slot(float)
    def point_y_spin_translate_action(self, d):
        delta = d - self.scene.get_storage().get_selected_node_pos()[1]
        if np.abs(delta) >= 0.005:
            self.scene.get_storage().translate_node(0, delta, 0)

    @Slot(float)
    def point_z_spin_translate_action(self, d):
        delta = d - self.scene.get_storage().get_selected_node_pos()[2]
        if np.abs(delta) >= 0.005:
            self.scene.get_storage().translate_node(0, 0, delta)

    def disable_view_tools(self):
        self.x_translate.setCheckable(False)
        self.y_translate.setCheckable(False)
        self.z_translate.setCheckable(False)
        self.x_rotate.setCheckable(False)
        self.y_rotate.setCheckable(False)
        self.z_rotate.setCheckable(False)
        self.zoom.setCheckable(False)

    def enable_view_tools(self):
        self.x_translate.setCheckable(True)
        self.y_translate.setCheckable(True)
        self.y_translate.setCheckable(True)
        self.x_rotate.setCheckable(True)
        self.y_rotate.setCheckable(True)
        self.z_rotate.setCheckable(True)
        self.zoom.setCheckable(True)

    def cutoff_view_tools(self):
        self.x_translate.setChecked(False)
        self.y_translate.setChecked(False)
        self.z_translate.setChecked(False)
        self.view.deactivate_x_translation()
        self.view.deactivate_y_translation()
        self.view.deactivate_z_translation()
        self.x_rotate.setChecked(False)
        self.y_rotate.setChecked(False)
        self.z_rotate.setChecked(False)
        self.view.deactivate_x_rotation()
        self.view.deactivate_y_rotation()
        self.view.deactivate_z_rotation()
        self.zoom.setChecked(False)
        self.view.deactivate_zoom()

    def cutoff_drawing_tools(self):
        self.add_points.setChecked(False)
        self.connect_points.setChecked(False)

    def cutoff_point_tools(self):
        self.point_x_translate.setChecked(False)
        self.point_y_translate.setChecked(False)
        self.point_z_translate.setChecked(False)
        self.view.deactivate_point_x_translation()
        self.view.deactivate_point_y_translation()
        self.view.deactivate_point_z_translation()

    def activate_point_tools(self):
        self.point_tools.setVisible(True)

    def activate_connection_tools(self):
        self.connection_tools.setVisible(True)

    def activate_cs_tool(self):
        for item in self.scene.items():
            if isinstance(item, NodePoint) and item.has_selection():
                self.cs_scene = item.get_cs_scene()
                self.cs_node = item
        self.cs_view.setScene(self.cs_scene)
        if self.cs_node.get_ref_point() is not None:
            self.ref_point_x_value.setValue(self.cs_node.get_ref_point().x())
            self.ref_point_y_value.setValue(self.cs_node.get_ref_point().y())
            self.cs_view.set_ref_point(self.cs_node.get_ref_point())
            self.cs_view.centerOn(2 * self.cs_node.get_ref_point().x(), 2 * self.cs_node.get_ref_point().y())
        else:
            self.ref_point_x_value.setValue(0)
            self.ref_point_y_value.setValue(0)
        self.cs_angle.setValue(self.cs_node.get_cs_angle())
        if self.cs_node.get_cs_transform() is not None:
            self.cs_view.setTransform(self.cs_node.get_cs_transform())
        else:
            self.cs_view.setTransform(QTransform())
        self.cs_tool.setVisible(True)
        self.cs_toolbar.setVisible(True)

    def deactivate_point_tools(self):
        self.point_tools.setVisible(False)
        self.cutoff_point_tools()

    def deactivate_connection_tools(self):
        self.connection_tools.setVisible(False)

    def deactivate_cs_tool(self):
        self.translate_ref.setChecked(False)
        self.zoom_cs.setChecked(False)
        self.rotate_lattice.setChecked(False)
        self.add_remove_helices.setChecked(False)
        self.renumber.setChecked(False)
        if self.cs_node is not None:
            self.cs_node.save_cs_angle(self.cs_view.get_rotation_amount())
            self.cs_node.save_cs_transform(self.cs_view.transform())
            self.cs_view.set_ref_point(None)
        self.cs_tool.setVisible(False)
        self.cs_toolbar.setVisible(False)

    def point_tools_active(self):
        return self.point_tools.isVisible()

    def connection_tools_active(self):
        return self.connection_tools.isVisible()

    def connect_points_active(self):
        return self.connect_points.isChecked()

    def cs_tool_active(self):
        return self.cs_tool.isVisible()

    def update_point_value(self, pos_3d):
        self.point_x_value.setValue(pos_3d[0])
        self.point_y_value.setValue(pos_3d[1])
        self.point_z_value.setValue(pos_3d[2])

    def update_ref_point_value(self, x, y):
        self.ref_point_x_value.setValue(x)
        self.ref_point_y_value.setValue(y)

    def update_cs_angle(self, theta):
        self.cs_angle.setValue(self.cs_angle.value() - theta)

    def get_view(self):
        return self.view

    def get_cs_view(self):
        return self.cs_view

    def remove_point_selection(self):
        for item in self.scene.items():
            if isinstance(item, NodePoint) and item.has_selection():
                item.set_selection(False)

    def get_tool_widths(self):
        return self.connection_tools.width(), self.point_tools.width(), self.cs_tool.width(), self.cs_toolbar.width()

    def closeEvent(self, event):
        self.settings_window.close()

    def get_parameters(self):
        return self.parameters
