if "bpy" in locals():
    # Runs if add-ons are being reloaded from blender
    import importlib
    importlib.reload(alternate_move_operator)
    print('Alternate move addon reloaded modules')
else:         
    from . import alternate_move_operator
    print('Alternate move addon imported modules')

import bpy
bl_info = {
    "name": "Alternate move operator",
    "author": "Wilkan",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D",
    "description": "Move active object with mouse",
    "category": "Development",
}

def register():
    bpy.utils.register_class(alternate_move_operator.OBJECT_OT_alternate_move)
    print("Alternate move operator registered")
    pass              

def unregister():
    bpy.utils.unregister_class(alternate_move_operator.OBJECT_OT_alternate_move)
    print("Alternate move operator unregistered")

    pass              
            
if __name__  == '__main__':
    register()