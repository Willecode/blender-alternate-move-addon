from pickle import FLOAT, OBJ
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import numpy as np
from bpy.props import FloatVectorProperty, FloatProperty
import mathutils
from mathutils import Color

def draw_callback(self, context):
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'POINTS', {"pos": self.coords})
    shader.bind()
    shader.uniform_float("color", self.preview_color)
    view_proj = bpy.context.region_data.perspective_matrix
    shader.uniform_float("ModelViewProjectionMatrix", view_proj @ self.model)
    batch.draw(shader)

class OBJECT_OT_alternate_move(bpy.types.Operator):
    """Move an object with the mouse"""
    bl_idname = "object.alternate_move"
    bl_label = "Alternate Move Operator"
    move_fac = 0.01
    obj: bpy.types.Object
    coords = []
    model: mathutils.Matrix
    view: mathutils.Matrix
    first_mouse_xy = []
    preview_color = (0, 1, 0, 1)

    preview_pos: FloatProperty(name="Preview Position", default=0)
    # ****************************

    def modal(self, context, event):
        mouse_x_offset = event.mouse_x - self.first_mouse_xy[0]
        mouse_y_offset = event.mouse_y - self.first_mouse_xy[1]

        camera_right_vec = np.array(self.view[0][:3])
        camera_up_vec = np.array(self.view[1][:3])

        view_inv = np.linalg.inv(self.view)
        camera_pos = np.array([view_inv[0][3], view_inv[1][3], view_inv[2][3]])
        camera_dist = np.linalg.norm(camera_pos)
        move_fac = camera_dist * 0.001
        
        context.area.tag_redraw() # Force area redraw
        
        if event.type == 'MOUSEMOVE':
            matrix_world = self.obj.matrix_world.copy()

            obj_pos = [
                matrix_world[0][3],
                matrix_world[1][3],
                matrix_world[2][3]
            ]

            obj_pos += (camera_right_vec * mouse_x_offset * move_fac)
            obj_pos += (camera_up_vec * mouse_y_offset * move_fac)

            matrix_world[0][3] = obj_pos[0]
            matrix_world[1][3] = obj_pos[1]
            matrix_world[2][3] = obj_pos[2]

            self.model = matrix_world

        elif event.type == 'LEFTMOUSE':
            bpy.context.object.matrix_world = self.model
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object and context.area.type == 'VIEW_3D':
            self.view = context.region_data.view_matrix
            self.first_mouse_xy = [event.mouse_x, event.mouse_y]
            self.obj = context.object

            if self.obj.active_material is not None:
                nodes = self.obj.active_material.node_tree.nodes
                principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
                base_color = principled.inputs['Base Color']
                value = base_color.default_value
                self.preview_color = (value[0], value[1], value[2], 1)
            self.processObjMesh()

            # Add the drawing callback function to view3D region
            # This will run every time the region is drawn
            args = (self, context)
            self.handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback,
             args, 'WINDOW', 'POST_VIEW')
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}
    
    def processObjMesh(self):
        self.coords = []
        verts = bpy.context.object.data.vertices.values()
        for v in verts:
            self.coords.append(v.co)


