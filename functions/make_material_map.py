import re

from typing import Union

from .tivoli_settings_node import *
from .. import utils


def get_bsdf_input(bsdf, name):
	renamed_inputs = {
	    "Subsurface": "Subsurface Weight",
	    "Emission": "Emission Color",
	}
	socket = bsdf.inputs.get(name)
	if socket is None and name in renamed_inputs:
		socket = bsdf.inputs.get(renamed_inputs[name])
	if socket is None:
		raise KeyError("Principled BSDF input not found: " + name)
	return socket


def get_opacity_map_mode(material, bsdf=None):
	blend_method = getattr(material, "blend_method", None)
	if blend_method is not None:
		if blend_method == "OPAQUE":
			return "OPACITY_MAP_OPAQUE"
		if blend_method == "CLIP":
			return "OPACITY_MAP_MASK"
		if blend_method in {"HASHED", "BLEND"}:
			return "OPACITY_MAP_BLEND"

	if material.surface_render_method == "BLENDED":
		return "OPACITY_MAP_BLEND"

	# Blender 4.2+ combines the older opaque, clip, and hashed modes into
	# DITHERED. Use blending when the Principled Alpha input is in use.
	if bsdf is not None:
		alpha = bsdf.inputs.get("Alpha")
		if alpha is not None and (
		    alpha.is_linked or alpha.default_value < 1.0
		):
			return "OPACITY_MAP_BLEND"
	return "OPACITY_MAP_OPAQUE"


def color_to_tivoli(color):
	# false means disable srgb so it's linear
	return [color[0], color[1], color[2], False]

	# def float_to_hex(value):
	# 	value = round(value * 255)
	# 	if value > 255:
	# 		value = 255
	# 	return hex(value)[2:].zfill(2)

	# return "#" + "".join(map(float_to_hex, [color[0], color[1], color[2]]))

def make_material_map(objects, to_webp=False):
	material_map = {}
	images_to_save = []
	images_to_convert = []

	for obj in objects:
		material_slots = obj.material_slots.values()
		for material_slot in material_slots:
			material = material_slot.material
			material_map_key = "mat::" + material.name

			# skip if already exists
			if material_map_key in material_map:
				continue

			# get principled shader and tivoli settings node
			nodes = material.node_tree.nodes

			material_output = None
			for node in nodes:
				if node.type == "OUTPUT_MATERIAL":
					material_output = node
			if material_output == None:
				continue

			bsdf = None
			unlit_color = None
			unlit_texture = None

			if len(material_output.inputs["Surface"].links) > 0:
				output = material_output.inputs["Surface"].links[0].from_node
				if output.type == "BSDF_PRINCIPLED":
					bsdf = output
				elif output.type == "RGB":
					unlit_color = output
				elif output.type == "TEX_IMAGE":
					unlit_texture = output
				elif output.type == "MIX_SHADER":
					# incase a mix shader is used for transparecy
					if len(output.inputs[2].links) > 0:
						output = output.inputs[2].links[0].from_node
						if output.type == "RGB":
							unlit_color = output
						elif output.type == "TEX_IMAGE":
							unlit_texture = output

			if bsdf == None and unlit_color == None and unlit_texture == None:
				continue

			tivoli = None
			for node in nodes:
				if node.type == "GROUP":
					if node.node_tree == get_tivoli_settings_node():
						tivoli = node
						break

			# write material data
			material_data = {
			    # "name": material.name,
			}

			def process(
			    input_type: Union["value", "color"],
			    input_key,
			    output_key,
			    map_only=False,
			    use_tivoli=False
			):
				if tivoli and use_tivoli:
					node_input = tivoli.inputs[input_key]
				else:
					node_input = get_bsdf_input(bsdf, input_key)

				def set_image(image):
					filepath = image.filepath
					filename = re.split(r"[\\/]", filepath).pop()

					if to_webp:
						old_filename = filename
						filename = utils.replace_filename_ext(filename, ".webp")
						images_to_convert.append([old_filename, filename])

					material_data[output_key + "Map"] = filename

					if tivoli and use_tivoli:
						images_to_save.append(image)

				if len(node_input.links) > 0:
					node = node_input.links[0].from_node

					if node.type == "TEX_IMAGE":
						set_image(node.image)

					elif node.type == "NORMAL_MAP":
						normal_input = node.inputs["Color"]
						if len(normal_input.links) > 0:
							node = normal_input.links[0].from_node
							if node.type == "TEX_IMAGE":
								set_image(node.image)

				elif map_only == False:
					if input_type == "value":
						material_data[output_key] = node_input.default_value
					else:
						material_data[output_key] = color_to_tivoli(
						    node_input.default_value
						)

			# https://apidocs.tivolicloud.com/Graphics.html#.Material

			if bsdf == None:
				material_data["unlit"] = True

				if unlit_color != None:
					material_data["albedo"] = color_to_tivoli(
					    unlit_color.outputs[0].default_value
					)

				if unlit_texture != None:
					filepath = unlit_texture.image.filepath
					filename = re.split(r"[\\/]", filepath).pop()

					if to_webp:
						old_filename = filename
						filename = utils.replace_filename_ext(filename, ".webp")
						images_to_convert.append([old_filename, filename])

					material_data["albedoMap"] = filename
					material_data["opacityMap"] = filename

					images_to_save.append(unlit_texture.image)

			else:
				process("color", "Base Color", "albedo")
				process("value", "Alpha", "opacity")
				process("value", "Roughness", "roughness")
				process("value", "Metallic", "metallic")
				process("color", "Normal", "normal", True)
				process("value", "Subsurface", "scattering")
				process("color", "Emission", "emissive")

				if tivoli:
					process("value", "Occlusion", "occlusion", True, True)
					# process("value", "Lightmap", "light", True, True)

			material_data["opacityMapMode"] = get_opacity_map_mode(
			    material, bsdf
			)
			if (
			    getattr(material, "blend_method", None) == "CLIP" and
			    hasattr(material, "alpha_threshold")
			):
				material_data["opacityCutoff"] = material.alpha_threshold

			if material.use_backface_culling:
				material_data["cullFaceMode"] = "CULL_BACK"
			else:
				material_data["cullFaceMode"] = "CULL_NONE"

			# add to map
			material_map[material_map_key] = {"materials": material_data}

	return {
	    "material_map": material_map,
	    "images_to_save": images_to_save,
	    "images_to_convert": images_to_convert
	}
