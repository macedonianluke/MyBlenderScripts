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
custom_scripts_path = "C:\dev\python-ifc-learn\MyBlenderScripts"

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
#ct.makecube("luke's cube")


#check can use imported ifc_sandbox class instead of long script below - to reduce complexity of script for others.

sb.load_project(path_ifc = 'c:\dev\studTest.ifc')




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






#-----------------create a vertical stud----------------#
def createstud(x,y,z):
    #Create a new ShapeBuilder Object - think i need an new object???
    studBuilder = ifcopenshell.util.shape_builder.ShapeBuilder(model)
    

    #create vertical stud
    stud1 = run("root.create_entity",model, ifc_class = "IfcBuildingElementPart")

    # Parameters to define our stud
    studWidth = 45
    studDepth = 90
    studHeight = 2700
    studSpacing = 450


    # Extrude a rectangle profile for the tabletop
    studProfile = studBuilder.rectangle(size=V(studWidth, studDepth))
    stud = studBuilder.extrude(studBuilder.profile(studProfile), studHeight, V(0, 0, 0))
    
   

    # Create a body representation
    stud_rep = studBuilder.get_representation(context=body, items=stud)

    #assign representation to table1 
    run("geometry.assign_representation",model, product = stud1, representation = stud_rep)

    #add to container
    run("spatial.assign_container", model, relating_structure = storey, product = stud1)
    
    
     #need to allow for change of object placement
    # Create a 4x4 identity matrix. This matrix is at the origin with no rotation.
    matrix = numpy.eye(4)

    # Rotate the matix 90 degrees anti-clockwise around the Z axis (i.e. in plan).
    # Anti-clockwise is positive. Clockwise is negative.
    matrix = ifcopenshell.util.placement.rotation(90, "Z") @ matrix

    # Set the X, Y, Z coordinates. Notice how we rotate first then translate.
    # This is because the rotation origin is always at 0, 0, 0.
    matrix[:,3][0:3] = (x, y, z)

    # Set our wall's Object Placement using our matrix.
    # `is_si=True` states that we are using SI units instead of project units.
    run("geometry.edit_object_placement", model, product=stud1, matrix=matrix, is_si=True)
    

    #we may create the stud as a single object that is then instanced across the wall assembly

    #rename it
    stud1.Name = "stud"

for i in range(10):
    y = i * 0.45
    createstud(0,y,0)



#create an IfcElementAssembly Object

#create wall assemlby
wallAssem1 = run("root.create_entity",model, ifc_class = "IfcElementAssembly")

wallAssem1.Name = "myAssem"

#representation - join mesh?
#assign representation to table1 
#run("geometry.assign_representation",model, product = stud1, representation = stud_rep)

#assign container
run("spatial.assign_container", model, relating_structure = storey, product = wallAssem1)

#need to get studs as a product (not contained in a def so cant access)
studtoadd = model.by_type("IfcBuildingElementPart")[0]

#create list of stud
Studs = model.by_type("IfcBuildingElementPart")

#print(Studs)
#loop through studs and add to assembly
print(Studs)



for stud in Studs:
    #maybe need to create an aggregator object from the aggregate class to use it definitions
    run(
            "aggregate.assign_object", model, product=stud, relating_object=wallAssem1
        )
        #parent to wallAssem1
        
#get list of studs in collection for parenting
collection_name = "IfcElementAssembly/myAssem"

collection = bpy.data.collections.get(collection_name) 

if collection:
    # Get all objects in the collection
    collection_objects = collection.objects

    # Filter out only the mesh objects
    mesh_objects = [obj for obj in collection_objects if obj.type == 'MESH']

    # Get a list of mesh names
    mesh_names = [obj.name for obj in mesh_objects]    
    
    
      
        
for mesh in mesh_names:   
        
    #bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
    #this needs to be a string or in below    
    child1 = bpy.data.objects.get(mesh)
    parent1 = bpy.data.objects.get(collection_name)
    child1.parent = parent1



assembly = model.by_type("IfcElementAssembly")
print(assembly)
print(assembly[0].Name)

#probably need to parent the studs to the assembly in blender


#add building element parts to the assembly 
# i think using core - aggregate.py  --- assign_object






#---------------manually create your own type-----------------

"""
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
#ct.move(customrect, -1, 0,0)


"""





#---------------this writes the file above to ifc file
#re write file
model.write('c:\dev\studTest.ifc')