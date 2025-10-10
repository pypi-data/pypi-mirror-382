import numpy as np

from gridpoint import GridPoint
from gridline import GridLine
from pathline import PathLine
from pathcurve import PathCurve
from nodepoint import NodePoint
from helixpoint import HelixPoint


class Storage3D:

    def __init__(self, scene):
        self.scene = scene
        self.R = np.identity(3)
        self.origin = np.array([0, 0, 0])
        self.local_origin = np.array([0, 0, 0])
        self.corners = [GridPoint(np.array([0, 0, 0]), np.array([0, 0, 0]), False, 0, 0) for _ in range(8)]
        self.points = {}
        self.nodes = {}
        self.path_lines = {}
        self.path_curves = {}
        self.node_index = 0
        self.path = True
        self.curve = False

    def get_unit_x(self):
        return np.matmul(self.R, np.array([1, 0, 0]))

    def get_unit_y(self):
        return np.matmul(self.R, np.array([0, 1, 0]))

    def get_unit_z(self):
        return np.matmul(self.R, np.array([0, 0, 1]))

    def get_nodes(self):
        return self.nodes

    def get_helix_knots(self):
        if len(self.path_curves) == 1:
            for ind, curve in self.path_curves.items():
                return curve.get_hknots()

    def translate_origin(self, dx, dy, dz):
        self.origin = np.array([self.origin[0] + dx, self.origin[1] + dy, self.origin[2] + dz])

    def has_mod_map(self):
        if len(self.path_curves) >= 1:
            for indices, curve in self.path_curves.items():
                if curve.has_mods():
                    return True
            else:
                return False
        else:
            return False

    def get_curve(self):
        for inds, curve in self.path_curves.items():
            return curve

    def get_mod_maps(self):
        maps = []
        for indices, curve in self.path_curves.items():
            if curve.has_mods():
                maps.append((curve.get_mods(), curve.get_twist(), curve.get_twist_num()))
        return maps

    def get_all_helices(self):
        helices = {}
        for index, node in self.nodes.items():
            scene = node[0].get_cs_scene()
            for item in scene.items():
                if isinstance(item, HelixPoint):
                    if item.has_selection() and item.get_number() not in helices:
                        helices[item.get_number()] = (item.get_x_ind(), item.get_y_ind(), item.is_odd())
        return helices

    def interpolate(self):
        for points, curve in self.path_curves.items():
            curve.hide()
        self.path_curves.clear()
        for indices, item in self.nodes.items():
            item[0].has_curve(False)
        all_open_paths_defined = False
        all_closed_paths_defined = False
        while not all_open_paths_defined:
            for node_index, node_point_lst in self.nodes.items():
                if ((node_point_lst[0].get_prev_node() is None)
                        and (node_point_lst[0].get_next_node() is not None) and (not node_point_lst[0].has_curve())):
                    start = node_point_lst[0]
                    start.has_curve(True)
                    next_point = start.get_next_node()
                    next_point.has_curve(True)
                    while next_point.get_next_node() is not None:
                        next_point = next_point.get_next_node()
                        next_point.has_curve(True)
                    stop = next_point
                    stop.has_curve(True)
                    curve = PathCurve(start, stop, self.R, self.scene)
                    self.path_curves[(start.get_node_index(), stop.get_node_index())] = curve
                    self.scene.addItem(curve)
            else:
                all_open_paths_defined = True
        while not all_closed_paths_defined:
            for node_index, node_point_lst in self.nodes.items():
                if ((node_point_lst[0].get_prev_node() is not None) and (node_point_lst[0].get_next_node() is not None)
                        and (not node_point_lst[0].has_curve())):
                    start = node_point_lst[0]
                    start.has_curve(True)
                    next_point = start.get_next_node()
                    next_point.has_curve(True)
                    while next_point.get_next_node() is not start:
                        next_point = next_point.get_next_node()
                        next_point.has_curve(True)
                    stop = next_point.get_next_node()
                    stop.has_curve(True)
                    curve = PathCurve(start, stop, self.R, self.scene)
                    self.path_curves[(start.get_node_index(), stop.get_node_index())] = curve
                    self.scene.addItem(curve)
            else:
                all_closed_paths_defined = True
        if len(self.path_curves) >= 1:
            for points, line in self.path_lines.items():
                line.hide()
            self.path = False
            self.curve = True

    def rotate_all_points(self, R):
        self.R = np.matmul(R, self.R)
        for item in self.scene.items():
            if isinstance(item, GridPoint) or isinstance(item, NodePoint) or isinstance(item, PathCurve):
                item.rotate_projection(R)
        self.scene.update()

    def translate_all_points(self, dx, dy, dz):
        translation = np.array([dx, dy, dz])
        for item in self.scene.items():
            if isinstance(item, GridPoint):
                item.set_pos_3d(item.get_pos_3d() + translation)
            if isinstance(item, NodePoint) and item.isVisible():
                item.set_pos_3d(item.get_pos_3d() + translation)
                self.nodes[item.get_node_index()][1] = item.get_pos_3d()
            if isinstance(item, PathCurve):
                item.translate(dx, dy, dz)
        self.translate_origin(dx, dy, dz)

    def translate_node(self, dx, dy, dz):
        translation = np.array([dx, dy, dz])
        for item in self.scene.items():
            if isinstance(item, NodePoint) and item.has_selection():
                item.set_pos_3d(item.get_pos_3d() + translation)
                item.set_def_pos(item.get_def_pos() + translation)
                self.nodes[item.get_node_index()][1] = item.get_pos_3d()
                self.scene.parent().update_point_value(item.get_def_pos())
                if item.has_curve():
                    self.path = True
                    self.curve = False
                    for indices, item2 in self.path_curves.items():
                        item2.hide()
                    for indices, item2 in self.path_lines.items():
                        item2.show()
                    for indices, item2 in self.nodes.items():
                        item2[0].has_curve(False)
                    self.path_curves.clear()

    def add_node_from_file(self, x, y, z):
        pos_3d = np.array([x, y, z])
        def_pos = np.array([x, y, z])
        node_point = NodePoint(pos_3d, def_pos, self.node_index)
        self.scene.addItem(node_point)
        node_point.rotate_projection(self.R)
        ref_point = node_point.get_ref_point()
        theta = node_point.get_cs_angle()
        cs_transform = node_point.get_cs_transform()
        self.nodes[self.node_index] = [node_point, def_pos, None, None, node_point.get_cs_scene(), ref_point, theta, cs_transform]
        self.node_index += 1

    def get_selected_node_pos(self):
        for item in self.scene.items():
            if isinstance(item, NodePoint) and item.has_selection():
                return item.get_def_pos()
        else:
            return np.array([0, 0, 0])

    def delete_selected_point(self):
        for item in self.scene.items():
            if isinstance(item, NodePoint) and item.has_selection():
                if item.get_prev_node() is not None:
                    self.path_lines[(item.get_prev_node().get_node_index(), item.get_node_index())].hide()
                    del self.path_lines[(item.get_prev_node().get_node_index(), item.get_node_index())]
                    item.get_prev_node().remove_next_node()
                    self.nodes[item.get_prev_node().get_node_index()][3] = None
                    item.remove_prev_node()
                    self.nodes[item.get_node_index()][2] = None
                if item.get_next_node() is not None:
                    self.path_lines[(item.get_node_index(), item.get_next_node().get_node_index())].hide()
                    del self.path_lines[(item.get_node_index(), item.get_next_node().get_node_index())]
                    item.get_next_node().remove_prev_node()
                    self.nodes[item.get_next_node().get_node_index()][2] = None
                    item.remove_next_node()
                    self.nodes[item.get_node_index()][3] = None
                if item.has_curve():
                    self.path = True
                    self.curve = False
                    for indices, curve in self.path_curves.items():
                        curve.hide()
                    self.path_curves.clear()
                    for indices, line in self.path_lines.items():
                        line.show()
                item.hide()
                del self.nodes[item.get_node_index()]
                if self.scene.parent().point_tools_active():
                    self.scene.parent().deactivate_point_tools()
                if self.scene.parent().cs_tool_active():
                    self.scene.parent().deactivate_cs_tool()

    def delete_selected_prev(self):
        for item in self.scene.items():
            if isinstance(item, NodePoint) and item.has_selection() and item.get_prev_node() is not None:
                self.path_lines[(item.get_prev_node().get_node_index(), item.get_node_index())].hide()
                del self.path_lines[(item.get_prev_node().get_node_index(), item.get_node_index())]
                self.nodes[item.get_prev_node().get_node_index()][3] = None
                item.get_prev_node().remove_next_node()
                self.nodes[item.get_node_index()][2] = None
                item.remove_prev_node()
                self.path = True
                self.curve = False
                for indices, curve in self.path_curves.items():
                    curve.hide()
                self.path_curves.clear()
                for indices, line in self.path_lines.items():
                    line.show()

    def delete_selected_next(self):
        for item in self.scene.items():
            if isinstance(item, NodePoint) and item.has_selection() and item.get_next_node() is not None:
                self.path_lines[(item.get_node_index(), item.get_next_node().get_node_index())].hide()
                del self.path_lines[(item.get_node_index(), item.get_next_node().get_node_index())]
                self.nodes[item.get_next_node().get_node_index()][2] = None
                item.get_next_node().remove_prev_node()
                self.nodes[item.get_node_index()][3] = None
                item.remove_next_node()
                self.path = True
                self.curve = False
                for indices, curve in self.path_curves.items():
                    curve.hide()
                self.path_curves.clear()
                for indices, line in self.path_lines.items():
                    line.show()

    def rotate_to_default(self):
        self.rotate_all_points(np.linalg.inv(self.R))

    def translate_to_default(self):
        self.translate_all_points(-self.origin[0], -self.origin[1], -self.origin[2])
        self.delete_grid()
        self.create_grid()
        self.restore_nodes()
        self.restore_path()
        self.restore_curve()
        self.local_origin = np.array([0, 0, 0])

    def redraw_grid(self):
        self.delete_grid()
        self.create_grid()
        self.restore_nodes()
        self.restore_path()
        self.restore_curve()

    def add_grid_point(self, pos_3d, def_pos, corner, ctype, corner_index):
        grid_point = GridPoint(pos_3d, def_pos, corner, ctype, corner_index)
        grid_point.rotate_projection(self.R)
        self.scene.addItem(grid_point)
        if corner:
            if self.corners[corner_index] is not None:
                self.corners[corner_index].set_corner(False)
                self.corners[corner_index].set_ctype([])
                self.corners[corner_index].set_corner_index(-1)
            self.corners[corner_index] = grid_point
            self.scene.replace_corner(grid_point, corner_index)
        self.points[(def_pos[0], def_pos[1], def_pos[2])] = grid_point
        return grid_point

    def add_path_line(self, point_1, point_2):
        path_line = PathLine(point_1, point_2)
        self.scene.addItem(path_line)
        self.path_lines[(point_1.get_node_index(), point_2.get_node_index())] = path_line

    def get_node_at(self, scene_pos):
        for node_index, node_point in self.nodes.items():
            d_2d = np.sqrt((scene_pos.x() - node_point[0].get_scene_pos_3d()[0]) ** 2 + (
                    scene_pos.y() - node_point[0].get_scene_pos_3d()[2]) ** 2)
            if d_2d <= 3/4:
                return node_point[0]

    def has_node_at(self, scene_pos):
        for node_index, node_point in self.nodes.items():
            d_2d = np.sqrt((scene_pos.x() - node_point[0].get_scene_pos_3d()[0]) ** 2 + (
                    scene_pos.y() - node_point[0].get_scene_pos_3d()[2]) ** 2)
            if d_2d <= 3/4:
                return True
        else:
            return False

    def add_node_point(self, scene_pos):
        scene_pos = np.array([scene_pos.x(), self.local_origin[1], scene_pos.y()])
        closest_grid_point = [None, 0, 0]

        for def_pos, grid_point in self.points.items():
            d_2d = np.sqrt((grid_point.get_scene_pos_3d()[0] - scene_pos[0]) ** 2 + (
                    grid_point.get_scene_pos_3d()[2] - scene_pos[0]) ** 2)
            if ((closest_grid_point[0] is None) or (d_2d < closest_grid_point[1]) or
                    (d_2d == closest_grid_point[1] and grid_point.get_scene_pos_3d()[1] > closest_grid_point[2])):
                scene_pos[1] = grid_point.get_scene_pos_3d()[1]
                closest_grid_point[0] = grid_point
                closest_grid_point[1] = d_2d
                closest_grid_point[2] = grid_point.get_scene_pos_3d()[1]
        pos_3d = np.matmul(np.linalg.inv(self.R), scene_pos)
        def_pos = pos_3d - self.origin

        for old_node_index, old_node_point in self.nodes.items():
            old_node_pos = old_node_point[0].get_scene_pos_3d()
            d_2d = np.sqrt((old_node_pos[0] - scene_pos[0]) ** 2 + (old_node_pos[2] - scene_pos[2]) ** 2)
            if d_2d <= 1:
                if old_node_point[0].get_prev_node() is not None:
                    self.path_lines[(old_node_point[0].get_prev_node().get_node_index(), old_node_index)].hide()
                    del self.path_lines[(old_node_point[0].get_prev_node().get_node_index(), old_node_index)]
                    old_node_point[0].get_prev_node().remove_next_node()
                    self.nodes[old_node_point[0].get_prev_node().get_node_index()][3] = None
                    old_node_point[0].remove_prev_node()
                    self.nodes[old_node_index][2] = None
                if old_node_point[0].get_next_node() is not None:
                    self.path_lines[(old_node_index, old_node_point[0].get_next_node().get_node_index())].hide()
                    del self.path_lines[(old_node_index, old_node_point[0].get_next_node().get_node_index())]
                    old_node_point[0].get_next_node().remove_prev_node()
                    self.nodes[old_node_point[0].get_next_node().get_node_index()][2] = None
                    old_node_point[0].remove_next_node()
                    self.nodes[old_node_index][3] = None
                if old_node_point[0].has_curve():
                    self.path = True
                    self.curve = False
                    for indices, item in self.path_curves.items():
                        item.hide()
                    self.path_curves.clear()
                    for indices, item in self.path_lines.items():
                        item.show()
                if old_node_point[0].has_selection():
                    self.scene.parent().deactivate_point_tools()
                    self.scene.parent().deactivate_cs_tool()
                old_node_point[0].hide()
                del self.nodes[old_node_index]
                break
        else:
            node_point = NodePoint(pos_3d, def_pos, self.node_index)
            self.scene.addItem(node_point)
            node_point.rotate_projection(self.R)
            ref_point = node_point.get_ref_point()
            theta = node_point.get_cs_angle()
            cs_transform = node_point.get_cs_transform()
            self.nodes[self.node_index] = [node_point, def_pos, None, None, node_point.get_cs_scene(), ref_point, theta,
                                           cs_transform]
            self.node_index += 1

    def restore_nodes(self):
        for node_index, node_point in self.nodes.items():
            new_node = NodePoint(np.matmul(self.R, node_point[1] + self.origin), node_point[1], node_index,
                                 node_point[4], node_point[5], node_point[6], node_point[7])
            self.scene.addItem(new_node)
            new_node.rotate_projection(self.R)
            self.nodes[node_index][0] = new_node
        for node_index, node_point in self.nodes.items():
            if node_point[2] is not None:
                node_point[0].set_prev_node(self.nodes[node_point[2]][0])
            if node_point[3] is not None:
                node_point[0].set_next_node(self.nodes[node_point[3]][0])

    def restore_path(self):
        for point_indices, path_line in self.path_lines.items():
            new_line = PathLine(self.nodes[point_indices[0]][0], self.nodes[point_indices[1]][0])
            self.scene.addItem(new_line)
            self.path_lines[(point_indices[0], point_indices[1])] = new_line
            if not self.path:
                new_line.hide()

    def restore_curve(self):
        for point_indices, path_curve in self.path_curves.items():
            start = self.nodes[point_indices[0]][0]
            stop = self.nodes[point_indices[1]][0]
            new_curve = PathCurve(start, stop, self.R, self.scene)
            self.scene.addItem(new_curve)
            self.path_curves[(point_indices[0], point_indices[1])] = new_curve
            if not self.curve:
                new_curve.hide()

    def update_grid(self):
        w = self.scene.get_w()
        limit = 10
        for i in range(8):
            ctype = self.corners[i].get_ctype()
            if np.abs(self.corners[i].get_pos_3d()[0]) <= int(limit):
                if -1 in ctype:
                    self.local_origin = self.local_origin + np.array([-w, 0, 0])
                    self.add_grid_layer_left()
                    self.remove_grid_layer_right()
                elif 1 in ctype:
                    self.local_origin = self.local_origin + np.array([w, 0, 0])
                    self.add_grid_layer_right()
                    self.remove_grid_layer_left()
            if np.abs(self.corners[i].get_pos_3d()[1]) <= int(limit):
                if -2 in ctype:
                    self.local_origin = self.local_origin + np.array([0, -w, 0])
                    self.add_grid_layer_in()
                    self.remove_grid_layer_out()
                if 2 in ctype:
                    self.local_origin = self.local_origin + np.array([0, w, 0])
                    self.add_grid_layer_out()
                    self.remove_grid_layer_in()
            if np.abs(self.corners[i].get_pos_3d()[2]) <= int(limit):
                if -3 in ctype:
                    self.local_origin = self.local_origin + np.array([0, 0, -w])
                    self.add_grid_layer_top()
                    self.remove_grid_layer_bottom()
                elif 3 in ctype:
                    self.local_origin = self.local_origin + np.array([0, 0, w])
                    self.add_grid_layer_bottom()
                    self.remove_grid_layer_top()

    def add_grid_layer_left(self):
        w = self.scene.get_w()
        size_i = int(np.round(np.abs(self.corners[1].get_def_pos()[2] - self.corners[5].get_def_pos()[2]) / w))
        size_j = int(np.round(np.abs(self.corners[5].get_def_pos()[1] - self.corners[4].get_def_pos()[1]) / w))
        ref_pos = self.corners[1].get_def_pos()
        for i in range(size_i + 1):
            for j in range(size_j + 1):
                def_pos = np.array([ref_pos[0] - w, ref_pos[1] + w * j, ref_pos[2] + w * i])
                pos_3d = def_pos + self.origin
                ctype = [-1]
                corner = False
                corner_index = -1
                if j == 0:
                    ctype.append(-2)
                if j == size_j:
                    ctype.append(2)
                if i == 0:
                    ctype.append(-3)
                if i == size_i:
                    ctype.append(3)
                if len(ctype) >= 3:
                    corner = True
                    if ctype == [-1, -2, -3]:
                        corner_index = 1
                    if ctype == [-1, 2, -3]:
                        corner_index = 0
                    if ctype == [-1, -2, 3]:
                        corner_index = 5
                    if ctype == [-1, 2, 3]:
                        corner_index = 4
                new_point = self.add_grid_point(pos_3d, def_pos, corner, ctype, corner_index)
                old_point = self.points[(def_pos[0] + w, def_pos[1], def_pos[2])]
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 0:
                        grid_line.change_start_point(new_point)
                        new_point.add_grid_line(grid_line)
                    elif grid_line.get_line_type() == 1 and j == size_j:
                        new_line = GridLine(self.points[(def_pos[0], def_pos[1] - size_j * w, def_pos[2])], new_point,
                                            1)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0], def_pos[1] - size_j * w, def_pos[2])].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                    elif grid_line.get_line_type() == 2 and i == size_i:
                        new_line = GridLine(self.points[(def_pos[0], def_pos[1], def_pos[2] - size_i * w)], new_point,
                                            2)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0], def_pos[1], def_pos[2] - size_i * w)].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 0:
                        old_point.remove_grid_line(grid_line)

    def add_grid_layer_right(self):
        w = self.scene.get_w()
        size_i = int(np.round(np.abs(self.corners[2].get_def_pos()[2] - self.corners[6].get_def_pos()[2]) / w))
        size_j = int(np.round(np.abs(self.corners[2].get_def_pos()[1] - self.corners[3].get_def_pos()[1]) / w))
        ref_pos = self.corners[2].get_def_pos()
        for i in range(size_i + 1):
            for j in range(size_j + 1):
                def_pos = np.array([ref_pos[0] + w, ref_pos[1] + w * j, ref_pos[2] + w * i])
                pos_3d = def_pos + self.origin
                ctype = [1]
                corner = False
                corner_index = -1
                if j == 0:
                    ctype.append(-2)
                if j == size_j:
                    ctype.append(2)
                if i == 0:
                    ctype.append(-3)
                if i == size_i:
                    ctype.append(3)
                if len(ctype) >= 3:
                    corner = True
                    if ctype == [1, -2, -3]:
                        corner_index = 2
                    if ctype == [1, 2, -3]:
                        corner_index = 3
                    if ctype == [1, -2, 3]:
                        corner_index = 6
                    if ctype == [1, 2, 3]:
                        corner_index = 7
                new_point = self.add_grid_point(pos_3d, def_pos, corner, ctype, corner_index)
                old_point = self.points[(def_pos[0] - w, def_pos[1], def_pos[2])]
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 0:
                        grid_line.change_end_point(new_point)
                        new_point.add_grid_line(grid_line)
                    elif grid_line.get_line_type() == 1 and j == size_j:
                        new_line = GridLine(self.points[(def_pos[0], def_pos[1] - size_j * w, def_pos[2])], new_point,
                                            1)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0], def_pos[1] - size_j * w, def_pos[2])].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                    elif grid_line.get_line_type() == 2 and i == size_i:
                        new_line = GridLine(self.points[(def_pos[0], def_pos[1], def_pos[2] - size_i * w)], new_point,
                                            2)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0], def_pos[1], def_pos[2] - size_i * w)].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 0:
                        old_point.remove_grid_line(grid_line)

    def add_grid_layer_in(self):
        w = self.scene.get_w()
        size_i = int(np.round(np.abs(self.corners[5].get_def_pos()[2] - self.corners[1].get_def_pos()[2]) / w))
        size_k = int(np.round(np.abs(self.corners[2].get_def_pos()[0] - self.corners[1].get_def_pos()[0]) / w))
        ref_pos = self.corners[1].get_def_pos()
        for i in range(size_i + 1):
            for k in range(size_k + 1):
                def_pos = np.array([ref_pos[0] + w * k, ref_pos[1] - w, ref_pos[2] + w * i])
                pos_3d = def_pos + self.origin
                ctype = []
                corner = False
                corner_index = -1
                if k == 0:
                    ctype.append(-1)
                if k == size_k:
                    ctype.append(1)
                ctype.append(-2)
                if i == 0:
                    ctype.append(-3)
                if i == size_i:
                    ctype.append(3)
                if len(ctype) >= 3:
                    corner = True
                    if ctype == [-1, -2, -3]:
                        corner_index = 1
                    if ctype == [-1, -2, 3]:
                        corner_index = 5
                    if ctype == [1, -2, 3]:
                        corner_index = 6
                    if ctype == [1, -2, -3]:
                        corner_index = 2
                new_point = self.add_grid_point(pos_3d, def_pos, corner, ctype, corner_index)
                old_point = self.points[(def_pos[0], def_pos[1] + w, def_pos[2])]
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 0 and k == size_k:
                        new_line = GridLine(self.points[(def_pos[0] - size_k * w, def_pos[1], def_pos[2])], new_point,
                                            0)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0] - size_k * w, def_pos[1], def_pos[2])].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                    elif grid_line.get_line_type() == 1:
                        grid_line.change_start_point(new_point)
                        new_point.add_grid_line(grid_line)
                    elif grid_line.get_line_type() == 2 and i == size_i:
                        new_line = GridLine(self.points[(def_pos[0], def_pos[1], def_pos[2] - size_i * w)], new_point,
                                            2)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0], def_pos[1], def_pos[2] - size_i * w)].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 1:
                        old_point.remove_grid_line(grid_line)

    def add_grid_layer_out(self):
        w = self.scene.get_w()
        size_i = int(np.round(np.abs(self.corners[0].get_def_pos()[2] - self.corners[4].get_def_pos()[2]) / w))
        size_k = int(np.round(np.abs(self.corners[0].get_def_pos()[0] - self.corners[3].get_def_pos()[0]) / w))
        ref_pos = self.corners[0].get_def_pos()
        for i in range(size_i + 1):
            for k in range(size_k + 1):
                def_pos = np.array([ref_pos[0] + w * k, ref_pos[1] + w, ref_pos[2] + w * i])
                pos_3d = def_pos + self.origin
                ctype = []
                corner = False
                corner_index = -1
                if k == 0:
                    ctype.append(-1)
                if k == size_k:
                    ctype.append(1)
                ctype.append(2)
                if i == 0:
                    ctype.append(-3)
                if i == size_i:
                    ctype.append(3)
                if len(ctype) >= 3:
                    corner = True
                    if ctype == [-1, 2, -3]:
                        corner_index = 0
                    if ctype == [-1, 2, 3]:
                        corner_index = 4
                    if ctype == [1, 2, 3]:
                        corner_index = 7
                    if ctype == [1, 2, -3]:
                        corner_index = 3
                new_point = self.add_grid_point(pos_3d, def_pos, corner, ctype, corner_index)
                old_point = self.points[(def_pos[0], def_pos[1] - w, def_pos[2])]
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 0 and k == size_k:
                        new_line = GridLine(self.points[(def_pos[0] - size_k * w, def_pos[1], def_pos[2])], new_point,
                                            0)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0] - size_k * w, def_pos[1], def_pos[2])].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                    elif grid_line.get_line_type() == 1:
                        grid_line.change_end_point(new_point)
                        new_point.add_grid_line(grid_line)
                    elif grid_line.get_line_type() == 2 and i == size_i:
                        new_line = GridLine(self.points[(def_pos[0], def_pos[1], def_pos[2] - size_i * w)], new_point,
                                            2)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0], def_pos[1], def_pos[2] - size_i * w)].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 1:
                        old_point.remove_grid_line(grid_line)

    def add_grid_layer_bottom(self):
        w = self.scene.get_w()
        size_j = int(np.round(np.abs(self.corners[5].get_def_pos()[1] - self.corners[4].get_def_pos()[1]) / w))
        size_k = int(np.round(np.abs(self.corners[4].get_def_pos()[0] - self.corners[7].get_def_pos()[0]) / w))
        ref_pos = self.corners[5].get_def_pos()
        for j in range(size_j + 1):
            for k in range(size_k + 1):
                def_pos = np.array([ref_pos[0] + w * k, ref_pos[1] + w * j, ref_pos[2] + w])
                pos_3d = def_pos + self.origin
                ctype = []
                corner = False
                corner_index = -1
                if k == 0:
                    ctype.append(-1)
                if k == size_k:
                    ctype.append(1)
                if j == 0:
                    ctype.append(-2)
                if j == size_j:
                    ctype.append(2)
                ctype.append(3)
                if len(ctype) >= 3:
                    corner = True
                    if ctype == [-1, 2, 3]:
                        corner_index = 4
                    if ctype == [-1, -2, 3]:
                        corner_index = 5
                    if ctype == [1, -2, 3]:
                        corner_index = 6
                    if ctype == [1, 2, 3]:
                        corner_index = 7
                new_point = self.add_grid_point(pos_3d, def_pos, corner, ctype, corner_index)
                old_point = self.points[(def_pos[0], def_pos[1], def_pos[2] - w)]
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 0 and k == size_k:
                        new_line = GridLine(self.points[(def_pos[0] - size_k * w, def_pos[1], def_pos[2])], new_point,
                                            0)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0] - size_k * w, def_pos[1], def_pos[2])].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                    if grid_line.get_line_type() == 1 and j == size_j:
                        new_line = GridLine(self.points[(def_pos[0], def_pos[1] - size_j * w, def_pos[2])], new_point,
                                            1)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0], def_pos[1] - size_j * w, def_pos[2])].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                    if grid_line.get_line_type() == 2:
                        grid_line.change_end_point(new_point)
                        new_point.add_grid_line(grid_line)
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 2:
                        old_point.remove_grid_line(grid_line)

    def add_grid_layer_top(self):
        w = self.scene.get_w()
        size_j = int(np.round(np.abs(self.corners[1].get_def_pos()[1] - self.corners[0].get_def_pos()[1]) / w))
        size_k = int(np.round(np.abs(self.corners[0].get_def_pos()[0] - self.corners[3].get_def_pos()[0]) / w))
        ref_pos = self.corners[1].get_def_pos()
        for j in range(size_j + 1):
            for k in range(size_k + 1):
                def_pos = np.array([ref_pos[0] + w * k, ref_pos[1] + w * j, ref_pos[2] - w])
                pos_3d = def_pos + self.origin
                ctype = []
                corner = False
                corner_index = -1
                if k == 0:
                    ctype.append(-1)
                if k == size_k:
                    ctype.append(1)
                if j == 0:
                    ctype.append(-2)
                if j == size_j:
                    ctype.append(2)
                ctype.append(-3)
                if len(ctype) >= 3:
                    corner = True
                    if ctype == [-1, 2, -3]:
                        corner_index = 0
                    if ctype == [-1, -2, -3]:
                        corner_index = 1
                    if ctype == [1, -2, -3]:
                        corner_index = 2
                    if ctype == [1, 2, -3]:
                        corner_index = 3
                new_point = self.add_grid_point(pos_3d, def_pos, corner, ctype, corner_index)
                old_point = self.points[(def_pos[0], def_pos[1], def_pos[2] + w)]
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 0 and k == size_k:
                        new_line = GridLine(self.points[(def_pos[0] - size_k * w, def_pos[1], def_pos[2])], new_point,
                                            0)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0] - size_k * w, def_pos[1], def_pos[2])].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                    elif grid_line.get_line_type() == 1 and j == size_j:
                        new_line = GridLine(self.points[(def_pos[0], def_pos[1] - size_j * w, def_pos[2])], new_point,
                                            1)
                        self.scene.addItem(new_line)
                        self.points[(def_pos[0], def_pos[1] - size_j * w, def_pos[2])].add_grid_line(new_line)
                        new_point.add_grid_line(new_line)
                    elif grid_line.get_line_type() == 2:
                        grid_line.change_start_point(new_point)
                        new_point.add_grid_line(grid_line)
                for grid_line in old_point.get_grid_lines():
                    if grid_line.get_line_type() == 2:
                        old_point.remove_grid_line(grid_line)

    def remove_grid_layer_left(self):
        w = self.scene.get_w()
        size_i = int(np.round(np.abs(self.corners[1].get_def_pos()[2] - self.corners[5].get_def_pos()[2]) / w))
        size_j = int(np.round(np.abs(self.corners[1].get_def_pos()[1] - self.corners[0].get_def_pos()[1]) / w))
        ref_pos = self.corners[1].get_def_pos()
        for i in range(size_i + 1):
            for j in range(size_j + 1):
                def_pos = np.array([ref_pos[0], ref_pos[1] + w * j, ref_pos[2] + w * i])
                point = self.points[(def_pos[0], def_pos[1], def_pos[2])]
                if point.is_corner():
                    point_2 = self.points[(def_pos[0] + w, def_pos[1], def_pos[2])]
                    point_2.set_corner(True)
                    point_2.set_ctype(point.get_ctype())
                    c_i = point.get_corner_index()
                    point_2.set_corner_index(c_i)
                    self.corners[point.get_corner_index()] = point_2
                    self.scene.replace_corner(point_2, point.get_corner_index())
                    point.set_corner(False)
                    point.set_ctype([])
                    point.set_corner_index(-1)
                for grid_line in point.get_grid_lines():
                    if grid_line.get_line_type() == 0:
                        grid_line.change_start_point(self.points[(def_pos[0] + w, def_pos[1], def_pos[2])])
                        self.points[(def_pos[0] + w, def_pos[1], def_pos[2])].add_grid_line(grid_line)
                    else:
                        grid_line.hide()
                        del grid_line
                point.hide()
                del point
                del self.points[(def_pos[0], def_pos[1], def_pos[2])]

    def remove_grid_layer_right(self):
        w = self.scene.get_w()
        size_i = int(np.round(np.abs(self.corners[2].get_def_pos()[2] - self.corners[6].get_def_pos()[2]) / w))
        size_j = int(np.round(np.abs(self.corners[2].get_def_pos()[1] - self.corners[3].get_def_pos()[1]) / w))
        ref_pos = self.corners[2].get_def_pos()
        for i in range(size_i + 1):
            for j in range(size_j + 1):
                def_pos = np.array([ref_pos[0], ref_pos[1] + w * j, ref_pos[2] + w * i])
                point = self.points[(def_pos[0], def_pos[1], def_pos[2])]
                if point.is_corner():
                    point_2 = self.points[(def_pos[0] - w, def_pos[1], def_pos[2])]
                    point_2.set_corner(True)
                    point_2.set_ctype(point.get_ctype())
                    c_i = point.get_corner_index()
                    point_2.set_corner_index(c_i)
                    self.corners[point.get_corner_index()] = point_2
                    self.scene.replace_corner(point_2, point.get_corner_index())
                    point.set_corner(False)
                    point.set_ctype([])
                    point.set_corner_index(-1)
                for grid_line in point.get_grid_lines():
                    if grid_line.get_line_type() == 0:
                        grid_line.change_end_point(self.points[(def_pos[0] - w, def_pos[1], def_pos[2])])
                        self.points[(def_pos[0] - w, def_pos[1], def_pos[2])].add_grid_line(grid_line)
                    else:
                        grid_line.hide()
                        del grid_line
                point.hide()
                del point
                del self.points[(def_pos[0], def_pos[1], def_pos[2])]

    def remove_grid_layer_out(self):
        w = self.scene.get_w()
        size_i = int(np.round(np.abs(self.corners[0].get_def_pos()[2] - self.corners[4].get_def_pos()[2]) / w))
        size_k = int(np.round(np.abs(self.corners[0].get_def_pos()[0] - self.corners[3].get_def_pos()[0]) / w))
        ref_pos = self.corners[0].get_def_pos()
        for i in range(size_i + 1):
            for k in range(size_k + 1):
                def_pos = np.array([ref_pos[0] + w * k, ref_pos[1], ref_pos[2] + w * i])
                point = self.points[(def_pos[0], def_pos[1], def_pos[2])]
                if point.is_corner():
                    point_2 = self.points[(def_pos[0], def_pos[1] - w, def_pos[2])]
                    point_2.set_corner(True)
                    point_2.set_ctype(point.get_ctype())
                    c_i = point.get_corner_index()
                    point_2.set_corner_index(c_i)
                    self.corners[point.get_corner_index()] = point_2
                    self.scene.replace_corner(point_2, point.get_corner_index())
                    point.set_corner(False)
                    point.set_ctype([])
                    point.set_corner_index(-1)
                for grid_line in point.get_grid_lines():
                    if grid_line.get_line_type() == 1:
                        grid_line.change_end_point(self.points[(def_pos[0], def_pos[1] - w, def_pos[2])])
                        self.points[(def_pos[0], def_pos[1] - w, def_pos[2])].add_grid_line(grid_line)
                    else:
                        grid_line.hide()
                        del grid_line
                point.hide()
                del point
                del self.points[(def_pos[0], def_pos[1], def_pos[2])]

    def remove_grid_layer_in(self):
        w = self.scene.get_w()
        size_i = int(np.round(np.abs(self.corners[1].get_def_pos()[2] - self.corners[5].get_def_pos()[2]) / w))
        size_k = int(np.round(np.abs(self.corners[1].get_def_pos()[0] - self.corners[2].get_def_pos()[0]) / w))
        ref_pos = self.corners[1].get_def_pos()
        for i in range(size_i + 1):
            for k in range(size_k + 1):
                def_pos = np.array([ref_pos[0] + w * k, ref_pos[1], ref_pos[2] + w * i])
                point = self.points[(def_pos[0], def_pos[1], def_pos[2])]
                if point.is_corner():
                    point_2 = self.points[(def_pos[0], def_pos[1] + w, def_pos[2])]
                    point_2.set_corner(True)
                    point_2.set_ctype(point.get_ctype())
                    c_i = point.get_corner_index()
                    point_2.set_corner_index(c_i)
                    self.corners[point.get_corner_index()] = point_2
                    self.scene.replace_corner(point_2, point.get_corner_index())
                    point.set_corner(False)
                    point.set_ctype([])
                    point.set_corner_index(-1)
                for grid_line in point.get_grid_lines():
                    if grid_line.get_line_type() == 1:
                        grid_line.change_start_point(self.points[(def_pos[0], def_pos[1] + w, def_pos[2])])
                        self.points[(def_pos[0], def_pos[1] + w, def_pos[2])].add_grid_line(grid_line)
                    else:
                        grid_line.hide()
                        del grid_line
                point.hide()
                del point
                del self.points[(def_pos[0], def_pos[1], def_pos[2])]

    def remove_grid_layer_top(self):
        w = self.scene.get_w()
        size_j = int(np.round(np.abs(self.corners[1].get_def_pos()[1] - self.corners[0].get_def_pos()[1]) / w))
        size_k = int(np.round(np.abs(self.corners[0].get_def_pos()[0] - self.corners[3].get_def_pos()[0]) / w))
        ref_pos = self.corners[1].get_def_pos()
        for j in range(size_j + 1):
            for k in range(size_k + 1):
                def_pos = np.array([ref_pos[0] + w * k, ref_pos[1] + w * j, ref_pos[2]])
                point = self.points[(def_pos[0], def_pos[1], def_pos[2])]
                if point.is_corner():
                    point_2 = self.points[(def_pos[0], def_pos[1], def_pos[2] + w)]
                    point_2.set_corner(True)
                    point_2.set_ctype(point.get_ctype())
                    c_i = point.get_corner_index()
                    point_2.set_corner_index(c_i)
                    self.corners[point.get_corner_index()] = point_2
                    self.scene.replace_corner(point_2, point.get_corner_index())
                    point.set_corner(False)
                    point.set_ctype([])
                    point.set_corner_index(-1)
                for grid_line in point.get_grid_lines():
                    if grid_line.get_line_type() == 2:
                        grid_line.change_start_point(self.points[(def_pos[0], def_pos[1], def_pos[2] + w)])
                        self.points[(def_pos[0], def_pos[1], def_pos[2] + w)].add_grid_line(grid_line)
                    else:
                        grid_line.hide()
                        del grid_line
                point.hide()
                del point
                del self.points[(def_pos[0], def_pos[1], def_pos[2])]

    def remove_grid_layer_bottom(self):
        w = self.scene.get_w()
        size_j = int(np.round(np.abs(self.corners[5].get_def_pos()[1] - self.corners[4].get_def_pos()[1]) / w))
        size_k = int(np.round(np.abs(self.corners[4].get_def_pos()[0] - self.corners[7].get_def_pos()[0]) / w))
        ref_pos = self.corners[5].get_def_pos()
        for j in range(size_j + 1):
            for k in range(size_k + 1):
                def_pos = np.array([ref_pos[0] + w * k, ref_pos[1] + w * j, ref_pos[2]])
                point = self.points[(def_pos[0], def_pos[1], def_pos[2])]
                if point.is_corner():
                    point_2 = self.points[(def_pos[0], def_pos[1], def_pos[2] - w)]
                    point_2.set_corner(True)
                    point_2.set_ctype(point.get_ctype())
                    c_i = point.get_corner_index()
                    point_2.set_corner_index(c_i)
                    self.corners[point.get_corner_index()] = point_2
                    self.scene.replace_corner(point_2, point.get_corner_index())
                    point.set_corner(False)
                    point.set_ctype([])
                    point.set_corner_index(-1)
                for grid_line in point.get_grid_lines():
                    if grid_line.get_line_type() == 2:
                        grid_line.change_end_point(self.points[(def_pos[0], def_pos[1], def_pos[2] - w)])
                        self.points[(def_pos[0], def_pos[1], def_pos[2] - w)].add_grid_line(grid_line)
                    else:
                        grid_line.hide()
                        del grid_line
                point.hide()
                del point
                del self.points[(def_pos[0], def_pos[1], def_pos[2])]

    def create_grid(self):
        w = self.scene.get_w()
        size = int(np.round(self.scene.get_size() / (2 * w)))
        previous_k = []
        previous_i = []
        for i in range(-size, size + 1):
            previous_j = []
            for j in range(-size, size + 1):
                for k in range(-size, size + 1):
                    ctype = []
                    corner = False
                    c_index = -1
                    if k == -size:
                        ctype.append(-1)
                    if k == size:
                        ctype.append(+1)
                    if j == -size:
                        ctype.append(-2)
                    if j == size:
                        ctype.append(2)
                    if i == -size:
                        ctype.append(-3)
                    if i == size:
                        ctype.append(+3)
                    if len(ctype) >= 3:
                        corner = True
                        if ctype == [-1, 2, -3]:
                            c_index = 0
                        if ctype == [-1, -2, -3]:
                            c_index = 1
                        if ctype == [1, -2, -3]:
                            c_index = 2
                        if ctype == [1, 2, -3]:
                            c_index = 3
                        if ctype == [-1, 2, 3]:
                            c_index = 4
                        if ctype == [-1, -2, 3]:
                            c_index = 5
                        if ctype == [1, -2, 3]:
                            c_index = 6
                        if ctype == [1, 2, 3]:
                            c_index = 7
                    current = self.add_grid_point(w * np.array([k, j, i]), w * np.array([k, j, i]),
                                                  corner, ctype, c_index)
                    previous_k.append(current)
                    previous_j.append(current)
                    previous_i.append(current)
                    if k == size and previous_k[0] != current:
                        new_line = GridLine(previous_k[0], current, 0)
                        self.scene.addItem(new_line)
                        previous_k[0].add_grid_line(new_line)
                        current.add_grid_line(new_line)
                        previous_k = []
                    if j == size and previous_j[k + size] != current:
                        new_line = GridLine(previous_j[k + size], current, 1)
                        self.scene.addItem(new_line)
                        previous_j[k + size].add_grid_line(new_line)
                        current.add_grid_line(new_line)
                    if i == size and previous_i[(j + size) * len(range(-size, size + 1)) + (k + size)] != current:
                        new_line = GridLine(previous_i[(j + size) * len(range(-size, size + 1)) + (k + size)], current,
                                            2)
                        self.scene.addItem(new_line)
                        previous_i[(j + size) * len(range(-size, size + 1)) + (k + size)].add_grid_line(new_line)
                        current.add_grid_line(new_line)

    def delete_grid(self):
        for item in self.scene.items():
            if isinstance(item, NodePoint):
                ind = item.get_node_index()
                if ind in self.nodes:
                    self.nodes[ind][4] = item.get_cs_scene()
                    self.nodes[ind][5] = item.get_ref_point()
                    self.nodes[ind][6] = item.get_cs_angle()
                    self.nodes[ind][7] = item.get_cs_transform()
        self.scene.clear()
        self.scene.remove_all_corners()
        self.corners = [GridPoint(np.array([0, 0, 0]), np.array([0, 0, 0]), False, 0, 0) for _ in range(8)]
        self.points.clear()
