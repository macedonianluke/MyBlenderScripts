#---------USEFUL LINKS FOR LEARNING-----------#

#-----SPECIAL NOTE------------
#Ensure you have the latest ifcopenshell or blender bim source code 
# use git and Sigma Dimensions method for updating git and blenderbim addon sequentially

#---important-----core knowledge---------for IFC----------: 
    #https://technical.buildingsmart.org/standards/
# go here first for learning:   https://blenderbim.org/docs-python/
# for Geometry creation you need to look at the raw source code as it is planned to be overhauled. 
        #Here: https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.7.0/src/ifcopenshell-python/ifcopenshell/api/geometry/add_slab_representation.py
# go here for live testing of ifc script with google collab( thanks to Carlos Villagrasa Silanes):  
        # https://colab.research.google.com/drive/1ieceyxgaG5bY7ODoGxBAMaBlx1yLRRnN?usp=sharing#scrollTo=09YjXEmR6-Ey
#important link for finding out what ifc class to use :  https://blenderbim.org/search-ifc-class.html


#base libraries for working with IFC files 
import bpy
import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.element
from ifcopenshell.api import run
import os
#import other libraries from custom paths on computer
import sys
#used for wall matrix creation , location, orientation
import numpy


"""
#used for reloading ifc file dynamically
import blenderbim.tool.ifcgit
import bpy
import logging
from blenderbim.bim import import_ifc
from blenderbim.bim.ifc import IfcStore
import blenderbim.tool as tool
import re
import os
"""

#libraries for shape_builder
# The shape_builder module depends on mathutils
from ifcopenshell.util.shape_builder import V





# Specify the path to your custom directory
custom_scripts_path = "C:\dev\MyBlenderScripts"

# Check if the directory exists
if os.path.exists(custom_scripts_path):
    # Add the custom directory to the sys.path
    sys.path.append(custom_scripts_path)

    # Now you can import modules or packages from the custom directory
    from CustomScripts import luke_printer
    from CustomScripts import myIfcSandbox
    from CustomScripts import myTools

    # Use the imported module or package
    printer = luke_printer.LukeIsTheBestPrinter()
    printer.print_luke_is_the_best()
    
    sb = myIfcSandbox.sandbox()
    sb.test_load()
    
    ct = myTools.custom_tool()
    ct.test_tool()

else:
    print(f"Error: The directory {custom_scripts_path} does not exist.")


# this next part forces a reload in case you edit the source after you first start the blender session
import importlib
importlib.reload(luke_printer)
importlib.reload(myIfcSandbox)
importlib.reload(myTools)

# this is optional and allows you to call the functions without specifying the package name
#from luke_printer import *


#check if can make additional custom definitions from imported custom classs working for more defintions
ct.makecube("luke's cube")


#check can use imported ifc_sandbox class instead of long script below - to reduce complexity of script for others.

sb.load_project(path_ifc = 'c:\dev\lukemod.ifc')




#step 2 ------------------ Create new ifc file


model = ifcopenshell.file()

#comment below out as was stopping the purging of types
#IfcStore.file = model

# All projects must have one IFC Project element
project = run("root.create_entity", model, ifc_class="IfcProject", name="My Project")



# Geometry is optional in IFC, but because we want to use geometry in this example, let's define units
# Assigning without arguments defaults to metric units
run("unit.assign_unit", model)

# Let's create a modeling geometry context, so we can store 3D geometry (note: IFC supports 2D too!)
context = run("context.add_context", model, context_type="Model")

# In particular, in this example we want to store the 3D "body" geometry of objects, i.e. the body shape
body = run("context.add_context", model, context_type="Model",
    context_identifier="Body", target_view="MODEL_VIEW", parent=context)

# Create a site, building, and storey. Many hierarchies are possible.
site = run("root.create_entity", model, ifc_class="IfcSite", name="My Site")
building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building A")
storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")

#create an ifc group
wallgroup = run("root.create_entity",model, ifc_class = "IfcGroup", name = "myfirstgroup")

# Since the site is our top level location, assign it to the project
# Then place our building on the site, and our storey in the building
run("aggregate.assign_object", model, relating_object=project, product=site)
run("aggregate.assign_object", model, relating_object=site, product=building)
run("aggregate.assign_object", model, relating_object=building, product=storey)

#this doesn't add to the storey - why?
run("aggregate.assign_object", model, relating_object=storey, product=wallgroup)





#------------------------modify file---------------------------
#add some new walls





#test create pset for common wall








#try to add wall data - work more on this later
data = {
    'GlobalId': ifcopenshell.guid.new(),
    'Name': 'new wall zzz',
    'Description': 'my new wall',
    'ObjectType': 'exterior wall',
    'Tag' : 'WT1'
    
    
    
}
#model.create_entity('IfcWall', **data)




#-------------------create wall with numpy matrix-------------------

# Let's create a new wall - can use below or the data block way
#wall2 = run("root.create_entity", model, ifc_class="IfcWall")

wall2 = model.create_entity('IfcWall',**data)

#create location and rotation of new wall----------------

# Create a 4x4 identity matrix. This matrix is at the origin with no rotation.
matrix = numpy.eye(4)

# Rotate the matix 90 degrees anti-clockwise around the Z axis (i.e. in plan).
# Anti-clockwise is positive. Clockwise is negative.
matrix = ifcopenshell.util.placement.rotation(90, "Z") @ matrix

# Set the X, Y, Z coordinates. Notice how we rotate first then translate.
# This is because the rotation origin is always at 0, 0, 0.
matrix[:,3][0:3] = (2, 2, 0)


# use matrix
run("geometry.edit_object_placement", model, product=wall2, matrix = matrix)

# Add a new wall-like body geometry, 5 meters long, 3 meters high, and 200mm thick
representation = run("geometry.add_wall_representation", model, context=body, length=10, height=2.4, thickness=0.1)
# Assign our new body geometry back to our wall
run("geometry.assign_representation", model, product=wall2, representation=representation)

# Place our wall in the ground floor
run("spatial.assign_container", model, relating_structure=storey, product=wall2)

#wall2.Name = 'wall with pset'

#try add pset to wall - using buildingsmart standard property set for walls - see blender bode :
#https://github.com/IfcOpenShell/IfcOpenShell/blob/ed47b6b227a580cdd3f3fc181054bd5f75cb9021/src/ifcopenshell-python/ifcopenshell/api/pset/edit_pset.py
pset = run("pset.add_pset", model, product = wall2, name = "Pset_wallcommon")

run("pset.edit_pset", model,pset=pset, properties={"FireRating": "2HR", "ThermalTransmittance": 42.3})






# create another wall using a custom definition
# create a simple utility to make walls easier
def createwall(newname, storey, rotation, location, mythickness, mylength, myheight):
    # Let's create a new wall
    wallname = run("root.create_entity", model, ifc_class="IfcWall")


    #create location and rotation of new wall----------------

    # Create a 4x4 identity matrix. This matrix is at the origin with no rotation.
    matrix = numpy.eye(4)

    # Rotate the matix 90 degrees anti-clockwise around the Z axis (i.e. in plan).
    # Anti-clockwise is positive. Clockwise is negative.
    matrix = ifcopenshell.util.placement.rotation(rotation, "Z") @ matrix

    # Set the X, Y, Z coordinates. Notice how we rotate first then translate.
    # This is because the rotation origin is always at 0, 0, 0.
    matrix[:,3][0:3] = location


    # use matrix
    run("geometry.edit_object_placement", model, product=wallname, matrix = matrix)

    # Add a new wall-like body geometry, 5 meters long, 3 meters high, and 200mm thick
    representation = run("geometry.add_wall_representation", model, context=body, length=mylength, height=myheight, thickness=mythickness)
    # Assign our new body geometry back to our wall
    run("geometry.assign_representation", model, product=wallname, representation=representation)

    # Place our wall in the ground floor
    run("spatial.assign_container", model, relating_structure=storey, product=wallname)

    wallname.Name = newname

        

#create some walls using the custom utility

createwall('wall 1', storey, 0, [5,5,1],.3,12,1)



#-------------------------create a wall using creat_2pt_wall-------------------------
# Let's create a new wall using 2 points

#create root entity
wallfromPts = run("root.create_entity", model, ifc_class="IfcWall")

#create two points
pt1 = (1,2,3)
pt2 = (2,2,3)

element = wallfromPts

newrepresentation = run ("geometry.create_2pt_wall", model, element = element, context = body, p1 = pt1, p2 = pt2, elevation = 0, height = 2.4, thickness = 0.2, is_si = True)

#assign representation to new wall
run ("geometry.assign_representation",model, product = wallfromPts, representation = newrepresentation)

#assign new wall to spatial container
run("spatial.assign_container", model, relating_structure = storey, product = wallfromPts)
 
#change its name if you want

wallfromPts.Name = "wallfromPts"




#-----------------create a profile------------------






#-----------need help to create slab with profile-----------------

#now create a slab with with the api
#-------------------------create slab from profile ------ use arbitrary curves

#parameters for slab profile, play with this
slab_pt1 = (0.,0.)
slablength = float(2000)
slab_pt2 = (slablength, 0.)
slabwidth = float(1000)
slab_pt3 = (slablength, slabwidth)
slab_pt4 = (0., slabwidth)
slabdepth = 0.1



#create element
mySlab = run("root.create_entity", model, ifc_class = "IfcSlab")

#create profile for slab
builder = ifcopenshell.util.shape_builder.ShapeBuilder(model)

outer_curve = builder.polyline([slab_pt1, slab_pt2, slab_pt3, slab_pt4],
    arc_points=[4], closed=True)
#creates a hole inside
inner_curve = builder.circle((500.,500.), radius=200.)
slab_profile = builder.profile(outer_curve, inner_curves=[inner_curve], name="Arbitrary")


# A profile-based representation, custom shape using shapebuilder above
prof_rep = run("geometry.add_profile_representation", model, context=body, profile=slab_profile, depth=slabdepth)

#create representation
#slabrepo = run("geometry.add_slab_representation", model, element = mySlab, context = body, profile = slabprofile, thickness = 0.5 )

#assign representation
run("geometry.assign_representation", model, product = mySlab, representation = prof_rep)

#assign to container
run("spatial.assign_container", model, relating_structure = storey, product = mySlab)



#-------------------create a custom mesh---------------
#create a custom mesh ifc furniture
mesh1 = run("root.create_entity",model, ifc_class = "IfcFurniture")










#create a mesh representation then add it to furniture

# These vertices and faces represent a 2m square 1m high pyramid in SI units.
# Note how they are nested lists. Each nested list represents a "mesh". There may be multiple meshes.
vertices = [[(0.,0.,0.), (0.,2.,0.), (2.,2.,0.), (2.,0.,0.), (1.,1.,1.)]]
faces = [[(0,1,2,3), (0,4,1), (1,4,2), (2,4,3), (3,4,0)]]
mesh_rep = run("geometry.add_mesh_representation", model, context=body, vertices=vertices, faces=faces)

#assign representation to furniture 
run("geometry.assign_representation",model, product = mesh1, representation = mesh_rep)

#add to container
run("spatial.assign_container", model, relating_structure = storey, product = mesh1)

#rename it, need to know whre you can put the name earlier - help on this
mesh1.Name = "mymeshfurn1"



#-----------------let move the mesh out the way-------------------
#-----------change the object_placement-----------------

#create a new matrix - for info see:https://blenderbim.org/docs-python/ifcopenshell-python/geometry_creation.html
# Create a 4x4 identity matrix. This matrix is at the origin with no rotation.
matrix = numpy.eye(4)
# Rotate the matix 90 degrees anti-clockwise around the Z axis (i.e. in plan).
# Anti-clockwise is positive. Clockwise is negative.
matrix = ifcopenshell.util.placement.rotation(90, "Z") @ matrix

# Set the X, Y, Z coordinates. Notice how we rotate first then translate.
# This is because the rotation origin is always at 0, 0, 0.
matrix[:,3][0:3] = (-5, 0, 0)

# move the object.
# `is_si=True` states that we are using SI units instead of project units.
run("geometry.edit_object_placement", model, product=mesh1, matrix=matrix, is_si=True)







#create a parametric table using Dion's script at copy pasted from below
# https://blenderbim.org/docs-python/ifcopenshell-python/geometry_creation.html

#maybe need to create a new builder
builder2 = ifcopenshell.util.shape_builder.ShapeBuilder(model)

#create table entity
#create a custom mesh ifc furniture
table1 = run("root.create_entity",model, ifc_class = "IfcFurniture")

# Parameters to define our table
width = 1200
depth = 700
height = 750
leg_size = 50.0
thickness = 50.0

# Extrude a rectangle profile for the tabletop
rectangle = builder2.rectangle(size=V(width, depth))
tabletop = builder2.extrude(builder.profile(rectangle), thickness, V(0, 0, height - thickness))

# Create a table leg curve, mirror it along two axes, and extrude.
leg_curve = builder.rectangle(size=V(leg_size, leg_size))
legs_curves = [leg_curve] + builder2.mirror(
    leg_curve,
    mirror_axes=[V(1, 0), V(0, 1), V(1, 1)],
    mirror_point=V(width / 2, depth / 2),
    create_copy=True,
)
legs_profiles = [builder.profile(leg) for leg in legs_curves]
legs = [builder2.extrude(leg, height - thickness) for leg in legs_profiles]

# Shift our table such that the object origin is in the center.
items = [tabletop] + legs
shift_to_center = V(-width / 2, -depth / 2)
builder.translate(items, shift_to_center.to_3d())

# Create a body representation
#already have body context
#body = ifcopenshell.util.representation.get_context(model, "Model", "Body", "MODEL_VIEW")

table_rep = builder2.get_representation(context=body, items=items)

#assign representation to table1 
run("geometry.assign_representation",model, product = table1, representation = table_rep)

#add to container
run("spatial.assign_container", model, relating_structure = storey, product = table1)

#rename it
table1.Name = "myTable"



#--------------use custom python defintion to move an element---------------
#lets use our custom, move definition to move the table
move(table1, -3,0,0,0)




#---------------------create a swept curve--------------------
#usecase - reo bars, cables, circular railings etc, is a special type of extrusion

#dont forget to create root entity element

sweptbar1 = run("root.create_entity", model, ifc_class = "IfcRailing")

builder3 = ifcopenshell.util.shape_builder.ShapeBuilder(model)

# Sweep a 10mm radius disk along a polyline with a couple of straight segments and an arc.
curve = builder3.polyline(
    [(0., 0., 0.), (100., 0., 0.), (171., 29., 0.), (200., 100., 0.), (200., 200., 0.)],
    arc_points=[2])
swept_curve = builder3.create_swept_disk_solid(curve, 10)

# Create a body representation
body = ifcopenshell.util.representation.get_context(model, "Model", "Body", "MODEL_VIEW")
rep_bar1 = builder3.get_representation(body, swept_curve)

#assign representation
run("geometry.assign_representation", model, product = sweptbar1, representation = rep_bar1)

#add to container
run("spatial.assign_container", model, relating_structure = storey, product = sweptbar1)

#rename 
sweptbar1.Name = "my_new_railing"





#---------------manually create your own type-----------------


#dont forget to create root element

customrect = run("root.create_entity",model, ifc_class = "IfcFurniture")


#create the representation for your custom object
rectangle = model.createIfcRectangleProfileDef(ProfileType="AREA", XDim=500, YDim=300)
direction = model.createIfcDirection((0., 0., 1.))
extrusion = model.createIfcExtrudedAreaSolid(SweptArea=rectangle, ExtrudedDirection=direction, Depth=500)
body = ifcopenshell.util.representation.get_context(model, "Model", "Body", "MODEL_VIEW")
custom_rep = model.createIfcShapeRepresentation(
    ContextOfItems=body, RepresentationIdentifier="Body", RepresentationType="SweptSolid", Items=[extrusion])

#add representation to the if object element you instantiated above
run("geometry.assign_representation", model, product = customrect, representation = custom_rep)

#assign the ifc object to a container
run("spatial.assign_container", model, relating_structure = storey, product = customrect)

#rename it
customrect.Name = "YourNewRect"

#move it
move(customrect, -1, 0,0,0)





#-------------------create a type----------------for example airconditioner wall box---------
#note ----------- ifc types dont need object placements
element_type = run("root.create_entity", model, ifc_class = "IfcFurnitureType", name = "FURN02")

# Create our element type. Types do not have an object placement.
#element_type = run("root.create_entity", model, ifc_class="IfcFurnitureType")

#dont forget to change the names of the variables if ifc creation is in same script

#create the representation
#create the representation for your custom object
rectangle2 = model.createIfcRectangleProfileDef(ProfileType="AREA", XDim=820, YDim=195)
direction2 = model.createIfcDirection((0., 0., 1.))
extrusion2 = model.createIfcExtrudedAreaSolid(SweptArea=rectangle2, ExtrudedDirection=direction2, Depth=306)
body = ifcopenshell.util.representation.get_context(model, "Model", "Body", "MODEL_VIEW")
new_rep2 =  model.createIfcShapeRepresentation(
    ContextOfItems=body, RepresentationIdentifier="Body", RepresentationType="SweptSolid", Items=[extrusion2])

#assign representation to element type
# Assign our representation to the element type.
run("geometry.assign_representation", model, product=element_type, representation=new_rep2)

#Note - can rename in same instantiation def below

#-----------------map a type to an element occurance-----------------
newFurn = run("root.create_entity", model, ifc_class = "IfcFurniture", name = "myFURN01")

#create an object plament for it
run("geometry.edit_object_placement",model, product = newFurn)

#assign IfcUnitaryEquipment to the IfcUnitaryEquipmentType
run("type.assign_type",model, related_object = newFurn, relating_type = element_type)

#dont forget assign to container
run("spatial.assign_container",model, relating_structure = storey, product = newFurn)


#move it
move (newFurn, -9,0,0,0)



#-------------------material layers sets---------------------

#issue here----------------wall type name not updating
#create a new wall type
wall_type = run("root.create_entity", model, ifc_class = "IfcWallType", name="CLT01")


#create a material set
material_set = run("material.add_material_set", model, name = "CRK100-MEM1-CLT90", set_type = "IfcMaterialLayerSet")

#create the materials
clt = run ("material.add_material",model, name = "CLT90", category = "cross_laminated_timber")
membrane = run ("material.add_material",model, name = "MEM1", category = "membrane")
cork = run ("material.add_material",model, name = "CRK100", category = "cork")

#create 3 layers for the new walltype
#note - python note - here you can see that the layer variable is overidden each new run of api function
layer = run("material.add_layer", model, layer_set=material_set, material=clt)
run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 90})
layer = run("material.add_layer", model, layer_set=material_set, material=membrane)
run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 1})
layer = run("material.add_layer", model, layer_set=material_set, material=cork)
run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 100})


#assign material to wall type
run("material.assign_material", model, product = wall_type, material = material_set)

#create a new wall
newwall2 = run("root.create_entity", model, ifc_class = "IfcWall", name = "cltwall1")

#create object placement for new wall
run("geometry.edit_object_placement",model, product = newwall2)



#assign the type to the wall
#run("type.assign_type", model, related_object = newwall2, relating_type = walltype)
ifcopenshell.api.run("type.assign_type", model, related_object=newwall2, relating_type=wall_type)

#now you have explicity create the geometry in the representation to match the layer thickness above
#ie is manual to make sure correct, unless we create a utility to help out here
#NOTE - THICKNESS MUST EQUAL LAYERS THICKNESS ABOVES - YOU NEED TO DO THIS MANUALLY
newwall_rep = run("geometry.add_wall_representation",model, context = body, length = 4, height = 2.4, thickness = 0.191)

#assign representation to new wall
run("geometry.assign_representation", model, product = newwall2, representation = newwall_rep)

#assign to container
run("spatial.assign_container", model, relating_structure = storey, product = newwall2)

#move the wall
move(newwall2, -12, 0,0,90) 


#next goal is to create cartesian points and lines.  below doesn't work yet
#myPoint = ("root.create_entity",model, ifc_class = "IfcCartesianPoint", name = "myPoint")

#need to figure out how to access the definitions under the geomoetry module, as not exposed to api yet
#run("geometry.create_cartesian_point",model, product = myPoint, matrix = myMatrix)




#---------------this writes the file above to ifc file
#re write file
model.write('c:\dev\lukemod.ifc')