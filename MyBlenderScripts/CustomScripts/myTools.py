#custom ifc operations
#note assumes you are importing the following in the main script

"""""
#base libraries for working with IFC files 
import bpy
import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.element
from ifcopenshell.api import run
import numpy
"""""

import bpy
#custom tools to play with ifc files and do stuff, 
# for the purposes of learning and experimenting

class custom_tool:
    
    def __init__(self):
        pass
    
    def test_tool(self):
        print("custom tools imported successfully")
    
    
    def move(element,x,y,z,rot):

        #create a new matrix - for info see:https://blenderbim.org/docs-python/ifcopenshell-python/geometry_creation.html
        # Create a 4x4 identity matrix. This matrix is at the origin with no rotation.
        matrix = numpy.eye(4)
        # Rotate the matix 90 degrees anti-clockwise around the Z axis (i.e. in plan).
        # Anti-clockwise is positive. Clockwise is negative.
        matrix = ifcopenshell.util.placement.rotation(rot, "Z") @ matrix

        # Set the X, Y, Z coordinates. Notice how we rotate first then translate.
        # This is because the rotation origin is always at 0, 0, 0.
        matrix[:,3][0:3] = (x, y, z)

        # move the object.
        # `is_si=True` states that we are using SI units instead of project units.
        run("geometry.edit_object_placement", model, product=element, matrix=matrix, is_si=True)   
        
        
    def makecube(self, cube_name) -> str:
        # Add a cube
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))

        # Optional: Set the cube's name
        bpy.context.object.name = str(cube_name)