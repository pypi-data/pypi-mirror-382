import voxelfarm
from datetime import datetime

class property_buffer_type:
    Buffer = 'buffer'
    Dataframe = 'dataframe'
    Voxel = 'voxels'

class special_properties:
    Merge = 'voxelfarm_merge'
    BufferType = 'voxelfarm_buffer_type'
    Compress = 'voxelfarm_compress'
    FixSelfIntersections = 'voxelfarm_fix_self_intersections'

class type:
    view = 1 << 1
    project = 1 << 2
    voxel_terrain = 1 << 3
    voxel_operations = 1 << 4
    block_model = 1 << 5
    point_cloud = 1 << 6
    voxel_generator = 1 << 7
    point_cloud_raw = 1 << 8
    heightmap_raw = 1 << 9
    block_model_raw = 1 << 10
    mesh_raw = 1 << 11
    mesh = 1 << 12
    ortho = 1 << 13
    program = 1 << 14
    folder = 1 << 15
    raw_density = 1 << 16
    indexed_density = 1 << 17
    material_tracking = 1 << 18
    voxel_mesh = 1 << 19
    drill_holes = 1 << 20
    drill_holes_raw = 1 << 21
    indexed_ortho = 1 << 22
    voxel_points = 1 << 23
    voxel_plane = 1 << 24
    wms_ortho = 1 << 25
    voxel_ortho = 1 << 26
    wmts_ortho = 1 << 27
    terrain_composite = 1 << 28
    raw_geo_chem = 1 << 29
    geo_chem = 1 << 30
    value = 1
    set = 2

class attribute:
    none = 0
    volume = 1
    material = 1 << 1
    color = 1 << 2
    vector = 1 << 3
    normal = 1 << 4
    tangent = 1 << 5
    uv = 1 << 6
    color_difference = 1 << 7
    voxel_index = 1 << 8
    faces = 1 << 9

class attribute_merge_mode:
    none = 0
    add = 1
    multiply = 2
    min = 3
    max = 4
    average = 5
    unit = 6
    grade = 7

class layer_merge_mode:
    none = 0
    min = 1
    max = 2
    override = 3

class texture:
    diffuse = 0
    normal = 1
    rgb0 = 2
    rgb1 = 3
    rgb2 = 4
    rgba0 = 1
    rgba1 = 1
    rgba2 = 1

class ColorLegend:
    gradient_step = 1.0
    gradient_min = 0.0
    gradient_max = 100.0
    gradient_attribute = ""
    static_color = (0, 0, 0)

class DrillHoleOptions:
    show_collars = True
    show_cylinders = True

class Material:
    def __init__(self):  
        self.color = (1.0, 1.0, 1.0, 1.0)
        self.gradient = None
        self.diffuse = False
        self.normal = False
        self.gradient = ""
        self.simplification_error = 0.00005
    
    def serialize(self):
        result = "0,"
        result += str(self.color[0]) + ","
        result += str(self.color[1]) + ","
        result += str(self.color[2]) + ","
        result += str(self.color[3]) + ","
        result += ("1" if self.diffuse else "0") + ","
        result += ("1" if self.normal else "0") + ","
        result += self.gradient + ","
        result += str(self.simplification_error) 
        return result

class view_lambda_framework:
    def init(self):
        pass

    def get_voxel_size(self):
        return 0.5

    def input(self, id, label, default = 0.0):
        return 0.0

    def input_entity(self, id, label, type):
        return ''

    def input_attributes(self, id, label, type, entity):
        return ''

    def input_attribute(self, id, label, type, entity):
        return ''

    def input_query(self, id, label, entity):
        return ''

    def input_region(self, id, label):
        return ''

    def get_entity(self, id):
        return 0

    def input_date(self, id, label, default = datetime.now):
        return datetime.fromtimestamp(0) 

    def input_color_legend(self, attributes, default_value):
        result = ColorLegend()
        return result

    def input_drillhole_options(self, entity, default):
        result = DrillHoleOptions()
        return result    

    def input_string(self, id, label, default = ""):
        return ''

    def input_bool(self, id, label, default = None):
        return 0

    def set_query(self, entity, query):
        pass

    def set_attributes(self, entity, attributes):
        pass

    def set_attribute_gradient(self, entity, attribute, min_value, max_value):
        pass

    def start_composite(self):
        pass

    def add_layer(self, layers, entity, merge_mode=0):
        pass

    def get_entity_type(self, entity):
        return 0

    def get_entity_name(self, entity):
        return ''

    def get_entity_date(self, entity):
        return datetime.fromtimestamp(0) #we lose the milliseconds

    def folder_contains(self, folder, entity):
        return 0

    def get_attributes(self, attributes):
        count = 0
        return range(0, count)

    def get_attribute_name(self, attributes, index):
        return ''

    def get_attribute_index(self, attributes, name):
        return 0

    def get_material(self, entity, voxel):
        return 0

    def load_mesh(self, entity, attributes, custom_attributes):
        return 0

    def mesh_intersection(self, componentA, componentB, attributes, custom_attributes):
        return 0

    def mesh_union(self, componentA, componentB, attributes, custom_attributes):
        return 0

    def mesh_complement(self, componentA, componentB, attributes, custom_attributes):
        return 0

    def mesh_attributes(self, componentA, componentB, attributes, custom_attributes):
        return 0

    def load_points(self, entity, attributes, custom_attributes):
        return 0

    def load_blocktree(self, entity, attributes, custom_attributes):
        return 0

    def load_density(self, entity, attributes, custom_attributes):
        return 0
    
    def load_terrain_composite(entity, attributes, custom_attributes):
        return 0

    def load_texture(self, entity, type):
        return 0

    def load_texture_stack(self):
        return ''

    def apply_texture(self, component, texture, type):
        return 0

    def apply_texture_stack(self, component, textures, type):
        pass

    def new_region_scope(self, region):
        return 0

    def set_field(self, v, value):
        pass

    def render(self, component, material):
        pass

    def log(self, message):
        print(message)

    def input_duplicate(self, entity):
        return 0

    def new_plane(self, a, b, c, d):
        return -1    

    def set_component_attribute_merge_mode(self, component, attribute, merge_mode):
        pass

    def export(self, component, name):
        pass

    def is_meta(self):
        return True

    def add_property(self, layer, key, value):
        pass

class view_lambda_host:

    version = (3,0,1,7)

    def __init__(self, framework = None):  
        if framework:
            self.lambda_framework = framework
        else:
            if voxelfarm.voxelfarm_framework:
                self.lambda_framework = voxelfarm.voxelfarm_framework
            else:
                self.lambda_framework = view_lambda_framework()

        if self.lambda_framework.is_meta():
            self.voxelCount = 1   
            self.fieldCount = 1  
        else:
            self.voxelCount = 40*40*40
            self.fieldCount = 45*45*45

        self.voxels = range(0, self.voxelCount)
        self.field = range(0, self.fieldCount)

    def get_voxel_size(self):
        return self.lambda_framework.get_voxel_size()

    def input(self, id, label, default = 0.0):
        return self.lambda_framework.input(id, label, default)

    def input_entity(self, id, label, type):
        return self.lambda_framework.input_entity(id, label, type)

    def input_attributes(self, id, label, type, entity):
        return self.lambda_framework.input_attributes(id, label, type, entity)

    def input_attribute(self, id, label, type, entity):
        return self.lambda_framework.input_attributes(id, label, type, entity)

    def input_query(self, id, label, entity):
        return self.lambda_framework.input_query(id, label, entity)

    def input_region(self, id, label):
        return self.lambda_framework.input_region(id, label)
    
    def get_entity(self, id):
        return self.lambda_framework.get_entity(id)

    def input_color_legend(self, attributes, default_value):
        result = ColorLegend()
        gradient_step = 1.0
        gradient_min = 0.0
        gradient_max = 100.0
        gradient_attribute = "fe"
        if default_value != None:
            gradient_step = default_value.gradient_step
            gradient_min = default_value.gradient_min
            gradient_max = default_value.gradient_max
            gradient_attribute = default_value.gradient_attribute

        legend_string = self.lambda_framework.input_color_legend(attributes, gradient_step, gradient_min, gradient_max, gradient_attribute)
        items = legend_string.split(',')
        result.gradient_attribute = items[0]
        result.gradient_min = float(items[1])
        result.gradient_max = float(items[2])
        result.gradient_step = float(items[3])
        return result

    def input_drillhole_options(self, entity, default):
        result = DrillHoleOptions()
        show_collars = 1
        show_cylinders = 1
        if default != None:
            show_collars = 1 if default.show_collars else 0
            show_cylinders = 1 if default.show_cylinders else 0
        self.lambda_framework.input_drillhole_options(entity, show_collars, show_cylinders)
        return result

    def input_date(self, id, label, default = datetime.now):
        timestamp = self.lambda_framework.input_date(id, label, 0)
        return datetime.fromtimestamp(timestamp/1000) # we lose the milliseconds

    def input_string(self, id, label, default = ""):
        return self.lambda_framework.input_string(id, label, default)

    def input_bool(self, id, label, default = None):
        return self.lambda_framework.input_bool(id, label, default)

    def set_query(self, entity, query):
        self.lambda_framework.set_query(entity, query)

    def set_attributes(self, entity, attributes):
        self.lambda_framework.set_attributes(entity, attributes)

    def set_attribute_gradient(self, entity, attribute, min_value, max_value):
        self.lambda_framework.set_attribute_gradient(entity, attribute, min_value, max_value)

    def start_composite(self):
        return self.lambda_framework.start_composite()

    def add_layer(self, layers, entity, merge_mode=layer_merge_mode.override):
        self.lambda_framework.add_layer(layers, entity, merge_mode)

    def get_entity_type(self, entity):
        return self.lambda_framework.get_entity_type(entity)

    def get_entity_name(self, entity):
        return self.lambda_framework.get_entity_name(entity)

    def get_entity_date(self, entity):
        timestamp = self.lambda_framework.get_entity_date(entity)
        return datetime.fromtimestamp(timestamp/1000) #we lose the milliseconds

    def get_entity_attributes(self, entity):
        attributes = self.lambda_framework.get_entity_attributes(entity)
        return attributes

    def folder_contains(self, folder, entity):
        return self.lambda_framework.folder_contains(folder, entity)

    def get_attributes(self, attributes):
        count = self.lambda_framework.get_attribute_count(attributes)
        return range(0, count)

    def get_attribute_name(self, attributes, index):
        return self.lambda_framework.get_attribute_name(attributes, index)

    def get_attribute_index(self, attributes, name):
        return self.lambda_framework.get_attribute_index(attributes, name)

    def start_sum(self, item, property):
        return self.lambda_framework.start_sum(item, property)

    def sum(self, sumId, value):
        self.lambda_framework.sum(sumId, value)

    def get_material(self, component, voxel):
        return self.lambda_framework.get_material(component, voxel)

    def load_mesh(self, entity, attributes, custom_attributes):
        return self.lambda_framework.load_mesh(entity, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def mesh_intersection(self, componentA, componentB, attributes, custom_attributes):
        return self.lambda_framework.mesh_intersection(componentA, componentB, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def mesh_union(self, componentA, componentB, attributes, custom_attributes):
        return self.lambda_framework.mesh_union(componentA, componentB, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def mesh_complement(self, componentA, componentB, attributes, custom_attributes):
        return self.lambda_framework.mesh_complement(componentA, componentB, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def mesh_attributes(self, componentA, componentB, attributes, custom_attributes):
        return self.lambda_framework.mesh_attributes(componentA, componentB, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def load_points(self, entity, attributes, custom_attributes):
        return self.lambda_framework.load_points(entity, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def load_blocktree(self, entity, attributes, custom_attributes):
        return self.lambda_framework.load_blocktree(entity, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def load_density(self, entity, attributes, custom_attributes):
        return self.lambda_framework.load_density(entity, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def load_terrain_composite(self, entity, attributes, custom_attributes):
        return self.lambda_framework.load_surface_composite(entity, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def load_texture(self, entity, type):
        return self.lambda_framework.load_texture(entity, type)

    def load_texture_stack(self):
        return self.lambda_framework.load_texture_stack()

    def apply_texture(self, component, texture, type):
        return self.lambda_framework.apply_texture(component, texture, type)

    def apply_texture_stack(self, component, textures, type):
        return self.lambda_framework.apply_texture_stack(component, textures, type)

    def new_region_scope(self, region):
        return range(0, self.lambda_framework.new_region_scope(region))

    def get_voxel_origin(self, v):
        return (0,0,0)

    def get_field_origin(self, v):
        return (0,0,0)

    def set_field(self, v, value):
        self.lambda_framework.set_field(v, value)

    def render(self, component, material):
        materialData = material.serialize() if material != None else ""
        self.lambda_framework.render(component, materialData)

    def log(self, message):
        self.lambda_framework.log(message)

    def new_material(self):
        return Material()

    def input_duplicate(self, entity):
        return self.lambda_framework.input_duplicate(entity)

    def new_plane(self, a, b, c, d):
        return self.lambda_framework.new_plane(a, b, c, d)

    def set_component_attribute_merge_mode(self, component, attribute, merge_mode):
        return self.lambda_framework.set_component_attribute_merge_mode(component, attribute, merge_mode)

    def export(self, component, name):
        self.lambda_framework.export(component, name)

    def store(self, component):
        self.lambda_framework.store(component)

    def add_property(self, layer, key, value):
        self.lambda_framework.add_property(layer, key, str(value))
