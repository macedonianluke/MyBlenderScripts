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
import math


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


# And/Or, if we plan to store 2D geometry, we need a "Plan" context
plan = run("context.add_context", model, context_type="Plan")

# A 2D annotation subcontext for plan views are important for door
# swings, window cuts, and symbols for equipment like GPOs, fire
# extinguishers, and so on.
run("context.add_context", model,
    context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent=plan)



#------------------------modify file---------------------------

#----------------------------CREATE IFC CARTESIAN POINT----------------------#

#next goal is to create cartesian points and lines.  below doesn't work yet
#myPoint = ("root.create_entity",model, ifc_class = "IfcCartesianPoint", name = "myPoint")
def createpoint(name, x,y,z):        


        #create a 2d annotation point
        annoPt1 = run("root.create_entity", model, ifc_class = "IfcAnnotation", name = str(name))


        #instead create ifc directly.
        myPoint1 = model.createIfcCartesianPoint((x,y,z))


        #may need to do something with si units

        #create representation (can I use a single vertice as a mesh representation?)
        vert1 = [(x,y,z)]


        vert_rep = model.createIfcShapeRepresentation(
                ContextOfItems=body, 
                RepresentationIdentifier="Body", 
                RepresentationType="Point", 
                Items= [myPoint1])        

        #assign representation
        run("geometry.assign_representation", model, product = annoPt1, representation = vert_rep)

        #create object placement
        run("geometry.edit_object_placement",model, product = myPoint1)

        #assign to container
        run("spatial.assign_container", model, relating_structure = storey, product = annoPt1)
        
        return myPoint1



#creates start and endpoint of our wall axis line

pt1 = createpoint("pt1",0.0,00.0,0.0)

pt2 = createpoint("pt2",0.0,3000.0,0.0)

ptlist = [pt1,pt2]


#create a line between the points
def createline(name, pt1,pt2):           


        #create a 2d annotation point
        annoLine = run("root.create_entity", model, ifc_class = "IfcAnnotation", name = str(name))
        
        #plane = lambda f: [f.createIfcPlane(f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0., 0., 0.))))]

        #instead create ifc directly.
        myLine = model.createIfcPolyLine(ptlist)


        line_rep = model.createIfcShapeRepresentation(
                ContextOfItems=body, 
                RepresentationIdentifier="Body", 
                RepresentationType="Curve2d", 
                Items= [myLine])        

        #assign representation
        run("geometry.assign_representation", model, product = annoLine, representation = line_rep)

        #create object placement
        run("geometry.edit_object_placement",model, product = myLine)

        #assign to container
        run("spatial.assign_container", model, relating_structure = storey, product = annoLine)
        
        

createline("line1",pt1,pt2)



#------------now trying to get points of line so can build from line up--------------#
#test get points back from line created
def get_element_by_name(ifc_file, element_type, element_name):
    elements = ifc_file.by_type(element_type)
    for element in elements:
        if hasattr(element, "Name") and element.Name == element_name:
            return element
    return None

# Replace "IfcWall" with the specific type of element you're looking for
element_type = "IfcAnnotation"

# Replace "YourWallName" with the name of the element you're looking for
element_name = "line1"

found_element = get_element_by_name(model, element_type, element_name)

if found_element:
    print(f"Element found: {found_element}")
else:
    print(f"Element with name {element_name} not found.")
    
    
    

# Assuming you have an IfcCurve instance, replace this with your actual instance
ifc_curve = model.by_type("IfcCurve")[0]

# Get the start and end points of the curve
if hasattr(ifc_curve, "Points"):
    # IfcPolyline or IfcTrimmedCurve
    points = ifc_curve.Points
    start_point = points[0]
    end_point = points[-1]
    print("Start Point:", start_point)
    print("End Point:", end_point)
elif hasattr(ifc_curve, "StartPoint") and hasattr(ifc_curve, "EndPoint"):
    # IfcLine, IfcCircle, or similar
    start_point = ifc_curve.StartPoint
    end_point = ifc_curve.EndPoint
    print("Start Point:", start_point)
    print("End Point:", end_point)
else:
    print("Could not determine curve type or endpoints.")



#----------------------- get coords

def get_coordinates_of_polyline(ifc_polyline):
    coordinates = []
    for point in ifc_polyline.Points:
        x, y, z = point.Coordinates[:3] if point.Coordinates else (None, None, None)
        coordinates.append((x, y, z))
    return coordinates

def create_points_along_vector(start_point, end_point, num_points=10):
    direction_vector = [(end - start) / (num_points - 1) for start, end in zip(start_point, end_point)]
    new_points = [
        tuple(start + i * step for start, step in zip(start_point, direction_vector))
        for i in range(num_points)
    ]
    return new_points


# Replace "IfcPolyline" with the specific type of curve you're working with
ifc_polyline_type = "IfcPolyline"

# Assuming you have an IfcPolyline instance, replace this with your actual instance
ifc_polyline = model.by_type(ifc_polyline_type)[0]

# Get coordinates of points in the polyline
point_coordinates = get_coordinates_of_polyline(ifc_polyline)

# Display the coordinates
for i, coordinates in enumerate(point_coordinates):
    print(f"Point {i + 1}: {coordinates}")



# Get coordinates of points in the polyline
point_coordinates = get_coordinates_of_polyline(ifc_polyline)

# Assuming you have at least two points
start_point = point_coordinates[0]
end_point = point_coordinates[-1]

# Create new points along the vector between start and end points
new_points = create_points_along_vector(start_point, end_point, num_points=20)

# Display the new points
for i, coordinates in enumerate(new_points):
    print(f"New Point {i + 1}: {coordinates}")





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
    stud = studBuilder.extrude(studBuilder.profile(studProfile), studHeight, V(0, 0, studWidth))
    
   

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


#new definition for sill plates (rotated


"""
#will replace in future to fit a 2d annotation line
for i in range(10):
    y = i * 0.45
    createstud(0,y,0)
"""



for point in new_points:
    createstud(point[0]/1000,point[1]/1000,point[2]/1000)
















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
#print(Studs)



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
#print(assembly)
#print(assembly[0].Name)

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