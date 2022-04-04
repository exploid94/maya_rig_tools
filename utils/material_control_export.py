
import json
import math

from maya import cmds as mc
from pymel import core as pm
from maya.api import OpenMaya as om2


default_shader = pm.PyNode("initialShadingGroup")


## ======================================================================
def process_mesh(mesh):
	"""
	Extract material and face assignments from
	the specified mesh as a dictionary.

	Args:
		mesh (pm.nt.Mesh, pm.nt.Transform): 
			the mesh whose materials you wish to save

	Returns:
		[dict]: Result of extraction
	"""
	mesh = pm.PyNode(mesh)
	mesh = mesh.getShape() if mesh.type() == "transform" else mesh
	shading_groups = set(mesh.listHistory(type="shadingEngine", future=True))
	if default_shader in shading_groups:
		shading_groups.remove(default_shader)
	single_material = len(shading_groups) < 2

	result = {
		"mesh_name": mesh.name(),
		"single_material": single_material,
		"materials": [
		],
	}

	if not len(shading_groups):
		## early out-- assume lambert1
		result["materials"].append({
			"name": "initialShadingGroup",
		})

		return result

	for group in shading_groups:
		data = {
			"name": group.surfaceShader.inputs()[0].longName(),
		}
		if not single_material:
			faces = sum([x.indices() for x in filter(lambda x: x.node() == mesh, pm.sets(group, q=True))], [])
			data["faces"] = faces

		result["materials"].append(data)

	return result


## ----------------------------------------------------------------------
def process_meshes(*args):
	"""
	Collects material information for all specified meshes
	and returns the info as an array of dictionaries.

	Returns:
		List[Dict]: The resulting array of material dictionaries.
	"""
	result = []
	meshes = pm.ls(args)
	for mesh in meshes:
		result.append(process_mesh(mesh))
	return result


## ----------------------------------------------------------------------
def get_unique_materials(data):
	"""
	Finds all unique materials in a material dictionary array

	Args:
		data (List[Dict]): 
			Material Dictionary Array result from process_meshes

	Returns:
		[Set[str]]: Set of unique string names
	"""
	result = []
	for item in data:
		for mat in item["materials"]:
			result.append(mat["name"])
	result = set(result) - set([default_shader.name()])
	return result


## ----------------------------------------------------------------------
def create_material_cubes(materials):
	"""
	Creates a cube per material for attaching so that on export,
	the materials stay in the maya ascii file.

	Args:
		materials (List[str]): List of materials to prep for export.
	"""
	if pm.objExists("shader_groups"):
		pm.delete("shader_groups")
	group = pm.createNode("transform", name="shader_groups")

	for index, mat in enumerate(materials):
		x = index % 10
		y = math.floor(index / 10)
		cube, = pm.polyCube(n=mat+"__shaderGeo", ch=False)
		cube.translate.set(x*2, y*2, 0)
		pm.hyperShade(cube, a=mat)
		pm.parent(cube, group)


## ----------------------------------------------------------------------
def export_materials(file_path):
	"""
	Write a maya ascii file of the shading networks of the
	selected meshes in the scene, as well as a sidecar JSON file
	representing the Material Dictionary Array for those meshes.

	Args:
		file_path ([str]): path for maya ascii file export. This file
					will be renamed with a .json extension for the
					sidecar file.

	Returns:
		List[Dict]: The resulting array of material dictionaries.
	"""
	##!TODO: support error cases.
	result = process_meshes(pm.selected())
	unique = get_unique_materials(result)

	json_file = file_path.rpartition(".")[0] + ".json"
	with open(json_file, "w") as fp:
		json.dump(result, fp, indent=4)

	options = {
		"force":   True,
		"options": "v=0;",
		"typ":     "mayaAscii",
		"pr":      True,
		"es":      True,
	}

	create_material_cubes(unique)
	pm.select("shader_groups", r=True)
	mc.file(file_path, **options)
	pm.delete("shader_groups")

	print("Exported materials to {}".format(file_path))
	print("Exported JSON mapping table to {}".format(json_file))

	return result


## ----------------------------------------------------------------------
def clean_materials_namespace():
	"""
	Remove all material namespaces and their contents from the file.
	"""
	to_kill = pm.ls("MATERIALS*::*")
	if len(to_kill):
		pm.delete(to_kill)

	namespaces = [x for x in pm.namespaceInfo(":", listOnlyNamespaces=True) if x.startswith("MATERIALS")]
	for ns in namespaces:
		pm.namespace(removeNamespace=ns)


## ----------------------------------------------------------------------
def import_materials(file_path):
	"""
	Import the specified maya ascii file and its shaders into the
	MATERIALS namespace, and use the sidecar json file (same name
	as the file specified by file_path but with a .json extension)
	to re-assign those shaders, to in-scene meshes, including per-
	face assignments.

	Args:
		file_path (str): 
			Path to the maya ascii file that contains
			the saved materials.
	"""	
	json_file = file_path.rpartition(".")[0] + ".json"
	with open(json_file, "r") as fp:
		reassignment_data = json.load(fp)

	options = {
		"import": True,
		"type"  : "mayaAscii",
		"ignoreVersion": True,
		"ra": True,
		"mergeNamespacesOnClash": False,
		"namespace": "MATERIALS",
		"options": "v=0;",
		"pr": True,
	}
	clean_materials_namespace()
	mc.file(file_path, **options)

	for data in reassignment_data:
		ob_name = data["mesh_name"]
		material_count = len(data["materials"])
		single_assignment = material_count < 2
		if not pm.objExists(ob_name):
			om2.MGlobal.displayError("-- Cannot find mesh {}!".format(ob_name))
			continue

		if single_assignment:
			mat_name = "MATERIALS:" + data["materials"][0]["name"]
			om2.MGlobal.displayInfo('Assigning "{}" to object "{}"...'.format(mat_name, ob_name))
			pm.select(ob_name, r=True)
			pm.hyperShade(assign=mat_name)
		else:
			## clear out all other assignments
			pm.hyperShade(ob_name, assign="lambert1")
			ob = pm.PyNode(ob_name)
			for mat in data["materials"]:
				## reassign face-assigned mats
				faces = map(lambda x: ob.f[int(x)], mat["faces"])
				mat_name = "MATERIALS:" + mat["name"]
				om2.MGlobal.displayInfo('Assigning "{}" to part of object "{}"...'.format(mat_name, ob_name))
				pm.select(faces, r=True)
				pm.hyperShade(assign=mat_name)

	if pm.objExists("MATERIALS:shader_groups"):
		pm.delete("MATERIALS:shader_groups")


## ======================================================================
## curve stuff
def get_safe_name_for_curve(curve):
	return curve.rpartition(":")[-1]


def export_curve(curve):
	curve = pm.PyNode(curve)
	shape = curve.getShape() if curve.type() == "transform" else curve
	if not (shape and shape.type() == "nurbsCurve"):
		raise ValueError("export_curve expects a nurbsCurve object to be passed in.")

	degree = shape.degree()

	result = {
		## doing a list conversion here because in python3 map
		## returns a generator, which is useless here, and you'll
		## be using python3 soon enough
		"points": list(map(lambda x:list(x), shape.getCVs(space="world"))),
		"degree": degree
	}

	if not shape.degree() == 1:
		result["knots"] = shape.getKnots()

	return result


## ----------------------------------------------------------------------
def export_curves(curves, export_folder=None):
	if export_folder is None:
		export_folder = os.path.abspath(os.sep.join((mc.workspace(q=True, rd=True), "data")))

	curves = pm.ls(curves)

	for curve in curves:
		safe_name = get_safe_name_for_curve(curve)
		data = export_curve(curve)
		file_path = os.sep.join((export_folder, safe_name+".json"))
		with open(file_path, "w") as fp:
			json.dump(data, fp, indent=4)
		om2.MGlobal.displayInfo("+ Wrote {}.".format(file_path))

	om2.MGlobal.displayInfo("+ Wrote data for {} curves.".format(len(curves)))


## ----------------------------------------------------------------------
def import_curves(curves, import_folder=None):
	if import_folder is None:
		import_folder = os.path.abspath(os.sep.join((mc.workspace(q=True, rd=True), "data")))
	
	curves = pm.ls(curves)

	for curve in curves:
		safe_name = get_safe_name_for_curve(curve)
		file_path = os.sep.join((import_folder, safe_name+".json"))
		if not os.path.exists(file_path):
			om2.MGlobal.displayWarning("-- Control {} has no saved curve file.".format(curve))
		with open(file_path, "r") as fp:
			data = json.load(fp)

		degree = data["degree"]
		points = data["points"]
		knot   = data["knots"] if degree > 1 else None

		if degree == 1:
			new_curve = pm.curve(d=degree, p=points)
		else:
			new_curve = pm.curve(d=degree, p=points, k=knot)

		## you have to do this first to make sure
		## the curve has the right number of pointss
		new_curve.getShape().worldSpace[0] >> curve.create
		new_curve.getShape().worldSpace[0] // curve.create
		pm.delete(new_curve)

		## now reset the points in worldspace
		curve.setCVs(points, space="world")
		curve.updateCurve()


## ======================================================================
## import export controls test

"""

pm.select("*_ctl", r=True)
export_curves(pm.selected())


pm.select("*_ctl", r=True)
import_curves(pm.selected())


"""




## ======================================================================
## import export materials test

"""


## export
export_path = "C:/temp/materials/exported_materials.ma"
export_materials(export_path)

unique = get_unique_materials(result)
print("Unique Materials: {}".format(len(unique)))
print("Models to Assign: {}".format(len(result)))


"""



"""



#import
import_path = "C:/temp/materials/exported_materials.ma"
import_materials(import_path)

"""







