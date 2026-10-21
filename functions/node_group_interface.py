import bpy


def add_input_socket(node_group, socket_type, name):
	if bpy.app.version >= (4, 0, 0):
		node_group.interface.new_socket(
		    name=name, in_out="INPUT", socket_type=socket_type
		)
	else:
		node_group.inputs.new(socket_type, name)
