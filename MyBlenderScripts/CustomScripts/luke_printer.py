import bpy

class LukeIsTheBestPrinter:
    def __init__(self):
        pass

    def print_luke_is_the_best(self):
        print("Luke is the best!")
        print("Now we can use a program structure to reduce complexity of code")
        
    def makecube(self, cube_name) -> str:
        # Add a cube
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))

        # Optional: Set the cube's name
        bpy.context.object.name = str(cube_name)