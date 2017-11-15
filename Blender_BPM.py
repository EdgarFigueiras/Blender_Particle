import bpy
import cArray
import time
import math
import random
import struct
import binascii
import os.path
import numpy as np
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

# ------------------------------------------------------------------------
#    Panel which allows the user to interact with the simulator
# ------------------------------------------------------------------------

#Clean the scene
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()


image_format = (
    ('BMP', 'BMP', ''),
    ('IRIS', 'IRIS', ''),
    ('PNG', 'PNG', ''),
    ('JPEG', 'JPEG', ''),
    ('JPEG2000', 'JPEG2000', ''),
    ('TARGA', 'TARGA', ''),
    ('TARGA_RAW', 'TARGA_RAW', ''), 
    ('CINEON', 'CINEON', ''),
    ('DPX', 'DPX', ''),
    ('OPEN_EXR_MULTILAYER', 'OPEN_EXR_MULTILAYER', ''),
    ('OPEN_EXR', 'OPEN_EXR', ''), 
    ('HDR', 'HDR', ''),
    ('TIFF', 'TIFF', '')
)

video_format = (
    ('AVI_JPEG', 'AVI_JPEG', ''),
    ('AVI_RAW', 'AVI_RAW', ''), 
    ('FRAMESERVER', 'FRAMESERVER', ''), 
    ('H264', 'H264', ''),
    ('FFMPEG', 'FFMPEG', ''),
    ('THEORA', 'THEORA', '')
)

enum_items = (
    ('FOO', 'Foo', ''),
    ('BAR', 'Bar', '')
)

class MySettings(PropertyGroup):

    folder_path = StringProperty(
        name="Data Folder",
        description="Select the folder with the simulation data.",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    path = StringProperty(
        name="Data File",
        description="Select the file with the simulation data.",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

    image_path = StringProperty(
        name="Store Path",
        description="Path where renders will be stored, by default uses the path of the simulation data",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

    int_box_n_particulas = IntProperty(
        name="Particles N ", 
        description="Total number of particles of the simulation",
        min = 50, max = 100000,
        default = 150)

    int_box_granularity = IntProperty(
        name="Granularity ", 
        description="Modifies the granularity. Min = 1 , Max = 10",
        min = 1, max = 10,
        default = 5)

    int_box_saturation = IntProperty(
        name="Saturation ", 
        description="Modify the saturation. Min = 1, Max = 10",
        min = 1, max = 10,
        default = 5)

    int_box_state = IntProperty(
        name="State ", 
        description="Modify the State",
        min = -1, max = 999,
        default = -1)
     

#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Panel class                                                          #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class OBJECT_OT_ResetButton(bpy.types.Operator):
    bl_idname = "reset.image"
    bl_label = "Reiniciar entorno"
    country = bpy.props.StringProperty()

    def execute(self, context):

        def confirm_message(self, context):
            self.layout.label("The system environment was cleaned")

        total_spheres = bpy.context.scene.my_tool.int_box_n_particulas-1

        for cnt in range(0, int(total_spheres)):
            nombreObjeto = "Sphere"
            if (cnt>0 and cnt<10):
                nombreObjeto = "Sphere.00" + str(cnt)
            if (cnt>=10 and cnt<100):
                nombreObjeto = "Sphere.0" + str(cnt)   
            if (cnt>=100):
                nombreObjeto = "Sphere." + str(cnt)       

            bpy.data.objects[nombreObjeto].hide = False

        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()
        bpy.context.scene.frame_current = 0

        bpy.data.scenes["Scene"].my_tool.int_box_state = -1
        bpy.context.window_manager.popup_menu(confirm_message, title="Reset", icon='VIEW3D_VEC')

        return{'FINISHED'} 



class OBJECT_OT_RenderButton(bpy.types.Operator):
    bl_idname = "render.image"
    bl_label = "RenderizarImagen"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):

        dir_image_path = bpy.data.scenes['Scene'].my_tool.image_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Render. Try again with other path")


        try:    
            #Set the image format, PNG by default
            bpy.context.scene.render.image_settings.file_format = bpy.context.scene['ImageFormat']

        except:        
            bpy.context.scene.render.image_settings.file_format = 'PNG'

        try:

            #Sets the path where the file will be stored, by default the same as the datafile
            if dir_image_path == "":
                bpy.data.scenes['Scene'].render.filepath = bpy.data.scenes['Scene'].my_tool.path + time.strftime("%c%s") + '.jpg'
                
                #Define a confirmation message to the default path            
                def confirm_message(self, context):
                    self.layout.label("Render image saved at: " + bpy.data.scenes['Scene'].my_tool.path )

            else:                
                bpy.data.scenes['Scene'].render.filepath = dir_image_path + time.strftime("%c%s") + '.jpg'
               
                #Define a confirmation message to the selected path 
                def confirm_message(self, context):
                    self.layout.label("Rendered image saved at: " + dir_image_path )   

            bpy.ops.render.render( write_still=True ) 


            bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        return{'FINISHED'} 


#Renders all objects one by one jumping between states
class OBJECT_OT_RenderAllButton(bpy.types.Operator):
    bl_idname = "render_all.image"
    bl_label = "RenderizarAllImagen"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):

        dir_image_path = bpy.data.scenes['Scene'].my_tool.image_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Renders. Try again with other path")

        #Calculate the total of states
        #Calculate the total of states
        try:
            path = bpy.data.scenes['Scene'].my_tool.path #Origin from where the data will be readen, selected by the first option in the Panel
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

            total_states = len(array_3d)

            file_with_binary_data.close()

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        for x in range(int(total_states)-1):

            try:    
                #Set the image format, PNG by default
                bpy.context.scene.render.image_settings.file_format = bpy.context.scene['ImageFormat']

            except:        
                bpy.context.scene.render.image_settings.file_format = 'PNG'

            try:

                #Sets the path where the file will be stored, by default the same as the datafile
                if dir_image_path == "":
                    bpy.data.scenes['Scene'].render.filepath = bpy.data.scenes['Scene'].my_tool.path + str(x) + '.jpg'
                    
                    #Define a confirmation message to the default path            
                    def confirm_message(self, context):
                        self.layout.label("Render image saved at: " + bpy.data.scenes['Scene'].my_tool.path )

                else:                
                    bpy.data.scenes['Scene'].render.filepath = dir_image_path + str(x) + '.jpg'
                   
                    #Define a confirmation message to the selected path 
                    def confirm_message(self, context):
                        self.layout.label("Rendered image saved at: " + dir_image_path )   

                bpy.ops.render.render( write_still=True ) 

                bpy.ops.particle.forward()
                

            except:
                bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        return{'FINISHED'} 


class OBJECT_OT_RenderVideoButton(bpy.types.Operator):
    bl_idname = "render.video"
    bl_label = "RenderizarVideo"
    country = bpy.props.StringProperty()


    #This code 
    def execute(self, context):

        dir_image_path = bpy.data.scenes['Scene'].my_tool.image_path

        #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Unable to save the Render. Try again with other path")


        try:    
            #Set the video format, AVI_JPEG by default            
            bpy.context.scene.render.image_settings.file_format = bpy.context.scene['VideoFormat'] 

        except:        
            bpy.context.scene.render.image_settings.file_format = 'AVI_JPEG' 
        
        try:

            #Sets the path where the file will be stored, by default the same as the datafile
            if dir_image_path == "":
                bpy.data.scenes['Scene'].render.filepath = bpy.data.scenes['Scene'].my_tool.path + time.strftime("%c%s") + '.avi'
                
                #Define a confirmation message to the default path            
                def confirm_message(self, context):
                    self.layout.label("Rendered video saved at: " + bpy.data.scenes['Scene'].my_tool.path )

            else:                
                bpy.data.scenes['Scene'].render.filepath = dir_image_path + time.strftime("%c%s") + '.avi'
               
                #Define a confirmation message to the selected path 
                def confirm_message(self, context):
                    self.layout.label("Rendered video saved at: " + dir_image_path )   

            bpy.ops.render.render(animation=True, write_still=True )


            bpy.context.window_manager.popup_menu(confirm_message, title="Saved successful", icon='SCENE')

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        return{'FINISHED'}
      


class OBJECT_PT_my_panel(Panel):
    bl_idname = "OBJECT_PT_my_panel"
    bl_label = "Simulation Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "objectmode"

class Panel(bpy.types.Panel):
    """Panel para añadir al entorno 3D"""
    bl_label = "Simulation Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column(align=True)
        box0 = layout.box()
        box1 = layout.box()
        box2 = layout.box()
        box22 = layout.box()
        box3 = layout.box()
        box4 = layout.box()

        box0.label(text="CALCULATION")

        box0.label(text="Select the folder with the data", icon='LIBRARY_DATA_DIRECT')

        box0.prop(scn.my_tool, "folder_path", text="")

        box0.operator("particle.calculation", text="Calculate data")
       


        box1.label(text="PARAMETERS")

        box1.label(text="Select the data file", icon='LIBRARY_DATA_DIRECT')

        box1.prop(scn.my_tool, "path", text="")

        box1.label(text="Select the number of particles", icon='PARTICLE_DATA')

        box1.prop(scn.my_tool, "int_box_n_particulas")

        #box1.label(text="Select the granularity", icon='GROUP_VERTEX')

        #box1.prop(scn.my_tool, "int_box_granularity")

        #box1.label(text="Select the saturation", icon='GROUP_VCOL')

        #box1.prop(scn.my_tool, "int_box_saturation")



        box2.label(text="SIMULATION")

        box2.operator("particle.calculator", text="Run Simulation")

        box2.operator("reset.image", text="Reset Environment")


        #Box to move back and forward between states

        box22.label(text="STATES")

        row_box = box22.row()

        row_box.prop(scn.my_tool, "int_box_state")

        row_box.enabled = False    

        row = box22.row()

        row.operator("particle.backward", text="Previous State", icon='BACK')

        row.operator("particle.forward", text="Next State", icon='FORWARD')



        box3.label(text="RENDER")

        box3.label(text="Select the folder to store renders")

        box3.prop(scn.my_tool, "image_path", text="")

        box3.label(text="Select the image format (PNG as default)", icon='SCENE')

        box3.prop_search(context.scene, "ImageFormat", context.scene, "imageformats", text="" , icon='OBJECT_DATA')

        box3.operator("render.image", text="Save image")

        box3.operator("render_all.image", text="Save all images")

        box3.label(text="Select the video format (AVI as default)", icon='RENDER_ANIMATION')

        box3.prop_search(context.scene, "VideoFormat", context.scene, "videoformats", text="" , icon='OBJECT_DATA')

        box3.operator("render.video", text="Save video")

        box4.label(text="SHORTCUTS")

        box4.label(text="To switch view press SHIFT + Z", icon='INFO')

        box4.label(text="To start the animation press ALT + A", icon='INFO')



        


# ------------------------------------------------------------------------
#    Register and unregister functions
# ------------------------------------------------------------------------

def rellenar_selectores(scene):
    bpy.app.handlers.scene_update_pre.remove(rellenar_selectores)
    scene.imageformats.clear()
    scene.videoformats.clear()

    for identifier, name, description in image_format:
        scene.imageformats.add().name = name

    for identifier, name, description in video_format:
        scene.videoformats.add().name = name


def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.imageformats = bpy.props.CollectionProperty(
            type=bpy.types.PropertyGroup
        )

    bpy.types.Scene.videoformats = bpy.props.CollectionProperty(
            type=bpy.types.PropertyGroup
        )

    bpy.types.Scene.ImageFormat = bpy.props.StringProperty()

    bpy.types.Scene.VideoFormat = bpy.props.StringProperty()

    bpy.app.handlers.scene_update_pre.append(rellenar_selectores)

    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)

    

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool
    del bpy.types.Scene.coll
    del bpy.types.Scene.coll_string

if __name__ == "__main__":
    register()

bl_info = {    
    "name": "Particles calculator",    
    "category": "Object",
}


#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particle calculator                                                  #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticleCalculator(bpy.types.Operator):
    """My Object Moving Script"""                 # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.calculator"             # unique identifier for buttons and menu items to reference.
    bl_label = "Particle calculator"              # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}             # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.
       
        def sphere_object(x):
            if x == 0 : 
                emitter = bpy.data.objects['Sphere']
            if (x > 0 and x < 10) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            if (x >= 10 and x < 100) :
                emitter = bpy.data.objects['Sphere.0' + str(x)]
            if (x >= 100) :
                emitter = bpy.data.objects['Sphere.' + str(x)]
            return emitter

        
        #Vortex
        def size_prob(prob):
            size = 0.10
            if (prob > 0.05):
                size = 0.22
            if (prob <= 0.05 and prob > 0.02):
                size = 0.15     
            if (prob <= 0.02 and prob > 0.005):
                size = 0.10  
            if (prob <= 0.005):
                size = 0.08      
            return size 
        



        def material_prob(prob):
            #Fixes the brightness according to the probability of appearing, 
            # helps to improve the visual final effect
            if (prob > 0.05):
                mat = bpy.data.materials['m1']
            if (prob <= 0.05 and prob > 0.02):
                mat = bpy.data.materials['m2']  
            if (prob <= 0.02 and prob > 0.005):
                mat = bpy.data.materials['m3']
            if (prob <= 0.005):
                mat = bpy.data.materials['m4']   
            return mat    
            

        #Define an error message if occurs a problem during the run, is showed using a popup 
        def error_message(self, context):
            self.layout.label("No datafile selected. Remember to select a compatible datafile")

        bpy.context.space_data.viewport_shade = 'MATERIAL'
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()
        bpy.context.scene.frame_current = 0    
        bpy.data.scenes["Scene"].my_tool.int_box_state = -1
        
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)   #Refresh the actual visualization with the new generator object placed  

        #Reading the data to generate the function who originated it
        #Read the data from te panel 
        path = bpy.data.scenes['Scene'].my_tool.path #Origin from where the data will be readen, selected by the first option in the Panel
        
        try:
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')

        N = len(array_3d[0])   #Size of the matrix

        particles_number = bpy.data.scenes['Scene'].my_tool.int_box_n_particulas #Read from the panel 
        

        #Create materials
        #Creating a material type
        mat1 = bpy.data.materials.new('m1')
        mat1.diffuse_color = (0.8, 0, 0.0327172)
        mat1.type='VOLUME'
        mat1.volume.density=0.5
        mat1.volume.transmission_color = (1, 0.0039, 0.071)
        mat1.volume.density = 0.3
        mat1.volume.emission = 2.5
        mat1.volume.emission_color = (1, 0, 0.25)
        mat1.volume.density_scale = 0.25
        #mat1.node_tree.nodes["Emission"].inputs[0].default_value = (0.8,0,0.016,1)

        #Creating a material type
        mat2 = bpy.data.materials.new('m2')
        mat2.diffuse_color = (0.8, 0, 0.0327172)
        mat2.type='VOLUME'
        mat2.volume.density=0.5
        mat2.volume.transmission_color = (1, 0.0039, 0.071)
        mat2.volume.density = 0.5
        mat2.volume.emission = 2.5
        mat2.volume.emission_color = (1, 0, 0.25)
        mat2.volume.density_scale = 0.5
        #mat2.node_tree.nodes["Emission"].inputs[0].default_value = (0.8,0,0.016,1)

        #Creating a material type
        mat3 = bpy.data.materials.new('m3')
        mat3.diffuse_color = (0.8, 0, 0.0327172)
        mat3.type='VOLUME'
        mat3.volume.density=0.5
        mat3.volume.transmission_color = (1, 0.0039, 0.071)
        mat3.volume.density = 0.8
        mat3.volume.emission = 2.5
        mat3.volume.emission_color = (1, 0, 0.25)
        mat3.volume.density_scale = 2
        #mat3.node_tree.nodes["Emission"].inputs[0].default_value = (0.8,0,0.016,1)

        #Creating a material type
        mat4 = bpy.data.materials.new('m4')
        mat4.diffuse_color = (0.8, 0, 0.0327172)
        mat4.type='VOLUME'
        mat4.volume.density=0.5
        mat4.volume.transmission_color = (1, 0.0039, 0.071)
        mat4.volume.density = 1
        mat4.volume.emission = 2.5
        mat4.volume.emission_color = (1, 0, 0.25)
        mat4.volume.density_scale = 10
        #mat4.node_tree.nodes["Emission"].inputs[0].default_value = (0.8,0,0.016,1)


        #Set the world color to black
        bpy.context.scene.world.horizon_color = (0, 0, 0)
        x_pos = 0
        y_pos = 0
        z_pos = 0

        prob = 0

        #Calculate the coordinates of each particle
        for cont in range(particles_number):
            x_pos = array_3d[0][cont][0] 
            y_pos = array_3d[0][cont][1] 
            z_pos = array_3d[0][cont][2]
            prob = array_3d[0][cont][3]  
            bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, enter_editmode=False, location=(x_pos, y_pos, z_pos), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.transform.translate(value=(0, 0, 0.223949), constraint_axis=(False, False, True), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, release_confirm=True)
            ob = bpy.context.active_object
            ob.dimensions = (size_prob(prob), size_prob(prob), size_prob(prob))
            ob.active_material = material_prob(prob)

        
        bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1   #Goes one frame forward to show particles clear at rendering MANDATORY


        file_with_binary_data.close()


        #bpy.ops.particle.generation() #Next step, go to particle generation

        return {'FINISHED'}            # this lets blender know the operator finished successfully.

# ------------------------------------------------------------------------
#    Register and unregister functions
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_class(ParticleCalculator)


def unregister():
    bpy.utils.unregister_class(ParticleCalculator)
    
# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()   

bl_info = {    
    "name": "Particles Forward",    
    "category": "Object",
}

import bpy
import time
import math
import random
import struct
import binascii
import numpy as np

#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particles forward                                                    #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticlesForward(bpy.types.Operator):
    """My Object Moving Script"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.forward"           # unique identifier for buttons and menu items to reference.
    bl_label = "Particles Forward"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}           # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.
    #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Imposible to read from original file. Try to Run simulation again")

        def draw(self, context):
            self.layout.label("Returned to the origin state")

        def sphere_object(x):
            if x == 0 : 
                emitter = bpy.data.objects['Sphere']
            if (x > 0 and x < 10) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            if (x >= 10 and x < 100) :
                emitter = bpy.data.objects['Sphere.0' + str(x)]
            if (x >= 100) :
                emitter = bpy.data.objects['Sphere.' + str(x)]
            return emitter

        def size_prob(prob):
            size = 0.10
            if (prob > 0.05):
                size = 0.22
            if (prob <= 0.05 and prob > 0.02):
                size = 0.15     
            if (prob <= 0.02 and prob > 0.005):
                size = 0.10  
            if (prob <= 0.005):
                size = 0.08      
            return size 

        def material_prob(prob):
            #Fixes the brightness according to the probability of appearing, 
            # helps to improve the visual final effect
            if (prob > 0.05):
                mat = bpy.data.materials['m1']
            if (prob <= 0.05 and prob > 0.02):
                mat = bpy.data.materials['m2']  
            if (prob <= 0.02 and prob > 0.005):
                mat = bpy.data.materials['m3']
            if (prob <= 0.005):
                mat = bpy.data.materials['m4']   
            return mat    

        #Calculates the position of spheres in a state given
        def sphere_placement(state, array_3d):
            actual_state = bpy.data.scenes["Scene"].my_tool.int_box_state 
            particles_number = bpy.context.scene.my_tool.int_box_n_particulas

            x_pos = 0
            y_pos = 0
            z_pos = 0

            prob = 0

            for cont in range(particles_number):
                x_pos = array_3d[actual_state][cont][0] 
                y_pos = array_3d[actual_state][cont][1] 
                z_pos = array_3d[actual_state][cont][2]
                prob = array_3d[actual_state][cont][3] 

                em = sphere_object(cont)
                em.dimensions = (size_prob(prob), size_prob(prob), size_prob(prob))
                em.location = (x_pos,y_pos,z_pos)
                em.active_material = material_prob(prob)

        #Take the actual state
        actual_state = bpy.data.scenes["Scene"].my_tool.int_box_state
        
        #Calculate the total of states
        try:
            path = bpy.data.scenes['Scene'].my_tool.path #Origin from where the data will be readen, selected by the first option in the Panel
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

            total_states = len(array_3d)

            file_with_binary_data.close()

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')


        #First time do this
        if(actual_state == -1):
            #Calculate the coordinates of each particle
            sphere_placement(1, array_3d)
            bpy.data.scenes["Scene"].my_tool.int_box_state = 1
        
        else:
            #If is not the last state
            if((actual_state+1) < int(total_states)):
                #Take the name of the Sphere to make the complete name and disable it
                sphere_placement(actual_state+1, array_3d)
                bpy.data.scenes["Scene"].my_tool.int_box_state = actual_state + 1
            
            #If its the last state 
            if((actual_state+1) == int(total_states)):
                sphere_placement(0, array_3d)
                bpy.data.scenes["Scene"].my_tool.int_box_state = 0

        #Goes one frame forward
        bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1




        return {'FINISHED'}            # this lets blender know the operator finished successfully.

# ------------------------------------------------------------------------
#    Register and unregister functions
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_class(ParticlesForward)


def unregister():
    bpy.utils.unregister_class(ParticlesForward)
    
# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()   

bl_info = {    
    "name": "Particles Backward",    
    "category": "Object",
}


#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particles backward                                                   #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticlesBackward(bpy.types.Operator):
    """My Object Moving Script"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.backward"           # unique identifier for buttons and menu items to reference.
    bl_label = "Particles Backward"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}           # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.
    #Define an error message if occurs a problem during the run, is showed using a popup
        def error_message(self, context):
            self.layout.label("Imposible to read from original file. Try to Run simulation again")

        def draw(self, context):
            self.layout.label("Returned to the origin state")

        def sphere_object(x):
            if x == 0 : 
                emitter = bpy.data.objects['Sphere']
            if (x > 0 and x < 10) :
                emitter = bpy.data.objects['Sphere.00' + str(x)]
            if (x >= 10 and x < 100) :
                emitter = bpy.data.objects['Sphere.0' + str(x)]
            if (x >= 100) :
                emitter = bpy.data.objects['Sphere.' + str(x)]
            return emitter

        def size_prob(prob):
            size = 0.10
            if (prob > 0.05):
                size = 0.22
            if (prob <= 0.05 and prob > 0.02):
                size = 0.15     
            if (prob <= 0.02 and prob > 0.005):
                size = 0.10  
            if (prob <= 0.005):
                size = 0.08      
            return size 

        def material_prob(prob):
            #Fixes the brightness according to the probability of appearing, 
            # helps to improve the visual final effect
            if (prob > 0.05):
                mat = bpy.data.materials['m1']
            if (prob <= 0.05 and prob > 0.02):
                mat = bpy.data.materials['m2']  
            if (prob <= 0.02 and prob > 0.005):
                mat = bpy.data.materials['m3']
            if (prob <= 0.005):
                mat = bpy.data.materials['m4']   
            return mat   

        #Calculates the position of spheres in a state given
        def sphere_placement(state, array_3d):
            actual_state = bpy.data.scenes["Scene"].my_tool.int_box_state 
            particles_number = bpy.context.scene.my_tool.int_box_n_particulas

            x_pos = 0
            y_pos = 0
            z_pos = 0

            prob = 0

            for cont in range(particles_number):
                x_pos = array_3d[actual_state][cont][0] 
                y_pos = array_3d[actual_state][cont][1] 
                z_pos = array_3d[actual_state][cont][2]
                prob = array_3d[actual_state][cont][3] 

                em = sphere_object(cont)
                em.dimensions = (size_prob(prob), size_prob(prob), size_prob(prob))
                em.location = (x_pos,y_pos,z_pos)
                em.active_material = material_prob(prob)


        #Take the actual state
        actual_state = bpy.data.scenes["Scene"].my_tool.int_box_state
        
        #Calculate the total of states
        try:
            path = bpy.data.scenes['Scene'].my_tool.path #Origin from where the data will be readen, selected by the first option in the Panel
            file_with_binary_data = open(path, 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)
       
            #Matrix with the data of the 2D grid
            array_3d = array_with_all_data['arr_0'] 

            total_states = len(array_3d)

            file_with_binary_data.close()

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')



        #First time do this
        if(actual_state == -1):
            sphere_placement(total_states-1,array_3d)
            bpy.data.scenes["Scene"].my_tool.int_box_state = total_states - 1
        
        else:
            #If is not the last state
            if((actual_state-1) >= 0):
                sphere_placement(actual_state-1,array_3d)
                bpy.data.scenes["Scene"].my_tool.int_box_state = actual_state - 1

            #If its the last state
            if((actual_state-1) < 0):
                sphere_placement(total_states-1,array_3d)
                bpy.data.scenes["Scene"].my_tool.int_box_state = total_states - 1


        #Goes one frame forward
        bpy.context.scene.frame_current = bpy.context.scene.frame_current + 1


        return {'FINISHED'}            # this lets blender know the operator finished successfully.

# ------------------------------------------------------------------------
#    Register and unregister functions
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_class(ParticlesBackward)


def unregister():
    bpy.utils.unregister_class(ParticlesBackward)
    
# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register() 

bl_info = {    
    "name": "Particles Calculation",    
    "category": "Object",
}

#*************************************************************************# 
# ----------------------------------------------------------------------- #
#    Particles calculation                                                #
# ----------------------------------------------------------------------- #
#*************************************************************************# 

class ParticlesCalculation(bpy.types.Operator):
    """My Object Moving Script"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "particle.calculation"           # unique identifier for buttons and menu items to reference.
    bl_label = "Particles Calculation"        # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}           # enable undo for the operator.
   
    def execute(self,context):        # execute() is called by blender when running the operator.
        
        def error_message(self, context):
            self.layout.label("Imposible to read psi data from the selected folder.")

        #Takes the data from the folder with all psi files
        try:
            path = bpy.data.scenes['Scene'].my_tool.folder_path #Origin from where the data will be readen, selected by the first option in the Panel
            
            psi_files_number=0

            while (os.path.isfile(path+ str(psi_files_number) +"psi")):
                psi_files_number += 1

        except:
            bpy.context.window_manager.popup_menu(error_message, title="An error ocurred", icon='CANCEL')
    
        #number of 3D points for each step
        number_of_points=1000
        #3D matrix creation
        matrix_3d = np.zeros((psi_files_number,number_of_points,4))

        #Data storage matrix
        array_aux = np.zeros((number_of_points, 4))

        for cont_file in range(0, psi_files_number):

            file_with_binary_data = open(path+ str(cont_file) +"psi", 'rb+') #File with binary data

            array_with_all_data = np.load(file_with_binary_data) #Gets the binary data as an array with 6 vectors (x_data, x_probability, y_data, y_probability, z_data, z_probability)

            #Matrix with the data of the 2D grid
            Z = array_with_all_data['arr_0'] 

            cArray.matrix2Dprob(Z, array_aux)
            matrix_3d[cont_file]=array_aux
        
        path=bpy.data.scenes['Scene'].my_tool.folder_path
        
        f = open(path + '3dData.3d', 'wb+')
        np.savez(f, matrix_3d)
        f.close()

        return {'FINISHED'}            # this lets blender know the operator finished successfully.

# ------------------------------------------------------------------------
#    Register and unregister functions
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_class(ParticlesCalculation)


def unregister():
    bpy.utils.unregister_class(ParticlesCalculation)