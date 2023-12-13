#ifc load/reload extract from ifc git
#used for reloading ifc file dynamically for learning purposes
import bpy
import blenderbim.tool.ifcgit
import logging
from blenderbim.bim import import_ifc
from blenderbim.bim.ifc import IfcStore
import blenderbim.tool as tool
import re
import os


class sandbox:
    
    def __init__(self):
        pass
    
    
    def test_load(self):
            print("load ifc sandbox lib successful")
            
    
    #need this additional definition
    def delete_collection(self, blender_collection):
            for obj in blender_collection.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(blender_collection)
            
            
    # bruno's definition from IfcGit Tool in blenderbim-blenderbim-tools-
    def load_project(self, path_ifc=""):
            """Clear and load an ifc project"""

            if path_ifc:
                IfcStore.purge()
            else:
                print("No ifc path in def load project")
                pass
            # delete any IfcProject/* collections
            for collection in bpy.data.collections:
                if re.match("^IfcProject/", collection.name):
                    self.delete_collection(collection)
                else:
                    pass
            # delete any Ifc* objects not in IfcProject/ heirarchy
            for obj in bpy.data.objects:
                if re.match("^Ifc", obj.name):
                    bpy.data.objects.remove(obj, do_unlink=True)

            bpy.data.orphans_purge(do_recursive=True)


            settings = import_ifc.IfcImportSettings.factory(bpy.context, path_ifc, logging.getLogger("ImportIFC"))
            settings.should_setup_viewport_camera = False
            ifc_importer = import_ifc.IfcImporter(settings)
            #has an issue here when previously create a ifc group now the next line doesn't work
            #so if fixed this issue by turning the loadproject def off for a pass then loading ifc and turning back on.
            ifc_importer.execute()
            tool.Project.load_pset_templates()
            tool.Project.load_default_thumbnails()
            tool.Project.set_default_context()
            tool.Project.set_default_modeling_dimensions()
            bpy.ops.object.select_all(action="DESELECT")
            
            print("load success")    
    