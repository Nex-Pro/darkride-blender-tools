bl_info = {
    "name": "Tivoli Blender Tools",
    "author": "Tivoli Cloud VR, Inc.",
    "description": "",
    "version": (0, 0, 0),
    "blender": (4, 2, 0),
    "location": "View 3D > Sidebar > Tivoli",
    "warning": "",
    "category": "3D View",
}

import bpy

from .settings import *

from .operators.avatar.add_armature import *
from .operators.avatar.add_tivoli_settings_node import *
from .operators.avatar.add_gltf_settings_node import *
from .operators.avatar.export_avatar import *
from .operators.avatar.force_tpose import *
from .operators.avatar.fix_bone_rotations import *
from .operators.avatar.ensure_root_bone import *

from .operators.lightmap.prepare_uv_maps import *
from .operators.lightmap.prepare_materials import *
from .operators.lightmap.bake_scene import *
from .operators.lightmap.export_scene import *

from .operators.export_scene import *

from .operators.animation.shape_key_animation_to_bones import *
from .operators.animation.bake_physics_with_mdd import *

from .panels.avatar import *
from .panels.lightmap import *
from .panels.export_scene import *
from .panels.animation import *

classes = (
    TivoliSettings,
    # avatar operators
    AvatarAddArmature,
    AvatarExportAvatar,
    AvatarAddTivoliSettingsNode,
    AvatarAddGltfSettingsNode,
    AvatarForceTPose,
    AvatarFixBoneRotations,
    AvatarEnsureRootBone,
    # lightmap operators
    LightmapPrepareUVMaps,
    LightmapPrepareMaterials,
    LightmapBakeScene,
    LightmapExportScene,
    # export scene operators
    ExportScene,
    # animation operators
    AnimationBakePhysicsWithMdd,
    AnimationShapeKeyAnimationToBones,
    # panels
    AvatarPanel,
    ExportScenePanel,
    LightmapPanel,
    AnimationPanel
)

# main_register, main_unregister = bpy.utils.register_classes_factory(classes)

def menu_func_export(self, context):
	self.layout.operator(
	    AvatarExportAvatar.bl_idname, text="Tivoli Avatar (.fst)"
	)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

	bpy.types.Scene.tivoli_settings = bpy.props.PointerProperty(
	    type=TivoliSettings
	)

def unregister():
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
	del bpy.types.Scene.tivoli_settings

	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
