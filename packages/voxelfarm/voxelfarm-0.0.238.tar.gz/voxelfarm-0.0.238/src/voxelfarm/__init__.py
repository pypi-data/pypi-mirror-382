from datetime import datetime
from .AzureAuthClient import AzureAuthClient

voxelfarm_framework = None

class property_buffer_type:
    Buffer = 'buffer'
    Dataframe = 'dataframe'
    Voxel = 'voxels'

class special_properties:
    Merge = 'voxelfarm_merge'
    BufferType = 'voxelfarm_buffer_type'
    Compress = 'voxelfarm_compress'
    FixSelfIntersections = 'voxelfarm_fix_self_intersections'

class entity_type:
    View = 'VIEW'
    Project = 'PROJECT'
    VoxelTerrain = 'VOXSURF'
    RealtimeVoxelTerrain = 'VOXOP'
    BlockModel = 'VOXBM'
    IndexedPointCloud = 'IDXPC'
    VoxelGenerator = 'VOXGEN'
    RawPointCloud = 'RAWPC'
    RawHeightmap = 'RAWHM'
    RawBlockModel = 'RAWBM'
    RawMesh = 'RAWMESH'
    IndexedMesh = 'IDXMESH'
    VoxelMesh = 'VOXMESH'
    OrthoImagery = 'ORTHO'
    IndexedOrthoImagery = 'IDXORTHO'
    Program = 'PROGRAM'
    Folder = 'FOLDER'
    RawDensity = 'RAWDENSITY'
    IndexedDensity = 'IDXDENSITY'
    MaterialTracking = 'VOXMT'
    MaterialTrackingOperation = 'VOXMTOP'
    RawDrillHoles = 'RAWDH'
    DrillHoles = 'IDXDH'
    OrthoVox='ORTHOVOX'
    Process='PROCESS'
    Export='EXPORT'
    Report = 'REPORT'
    VoxelPC = 'VOXPC'
    RawGeoChem = 'RAWGEOCHEM'
    GeoChem = 'GEOCHEM'
    TerrainComposite = 'SURFCOMPOSITE'

class lambda_type:
    Generator = 'VOXEL'
    Report = 'REPORT'
    View = 'VIEW'
    Workflow = 'WORKFLOW'
    Process = 'PROCESS'
    
class process_lambda_type:
    Workflow = 'WORKFLOW'
    Process = 'PROCESS'

class operation_type:
    sum = 0
    min = 1
    max = 2
    avg = 3

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

version = (3,0,1,7)

# Reports and Views

voxelCount = 40*40*40
fieldCount = 45*45*45

voxels = range(0, voxelCount)
field = range(0, fieldCount)

def serialize_attributes(attributes):
    attribute_list = ''
    if attributes:
        if isinstance(attributes, str):
            attribute_list = attributes
        else:    
            attribute_list = ','.join(attributes)

    return attribute_list

def get_voxel_size():
    if voxelfarm_framework:
        return voxelfarm_framework.get_voxel_size()
    return 1.0

def input(id, label, default = 0.0):
    if voxelfarm_framework:
        return voxelfarm_framework.input(id, label, default)
    return default

def input_entity(id, label, type):
    if voxelfarm_framework:
        return voxelfarm_framework.input_entity(id, label, type)
    return -1

def input_attributes(id, label, type, entity):
    if voxelfarm_framework:
        return voxelfarm_framework.input_attributes(id, label, type, entity)
    return ''

def input_attribute(id, label, type, entity):
    if voxelfarm_framework:
        return voxelfarm_framework.input_attributes(id, label, type, entity)
    return ''

def input_query(id, label, entity):
    if voxelfarm_framework:
        return voxelfarm_framework.input_query(id, label, entity)
    return ''

def input_region(id, label):
    if voxelfarm_framework:
        return voxelfarm_framework.input_region(id, label)
    return ''

def get_entity(id):
    if voxelfarm_framework:
        return voxelfarm_framework.get_entity(id)
    return 0

def input_color_legend(attributes, default_value):
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

    if voxelfarm_framework:
        legend_string = voxelfarm_framework.input_color_legend(attributes, gradient_step, gradient_min, gradient_max, gradient_attribute)
        items = legend_string.split(',')
        result.gradient_attribute = items[0]
        result.gradient_min = float(items[1])
        result.gradient_max = float(items[2])
        result.gradient_step = float(items[3])
        return result

    result.gradient_attribute = gradient_attribute
    result.gradient_min = gradient_min
    result.gradient_max = gradient_max
    result.gradient_step = gradient_step
    return result
    
def input_drillhole_options(entity, default):
    result = DrillHoleOptions()
    result.show_collars = 1
    result.show_cylinders = 1
    if default != None:
        result.show_collars = 1 if default.show_collars else 0
        result.show_cylinders = 1 if default.show_cylinders else 0

    if voxelfarm_framework:
        voxelfarm_framework.input_drillhole_options(entity, result.show_collars, result.show_cylinders)
    return result

def input_date(id, label, default = datetime.now):
    if voxelfarm_framework:
        timestamp = voxelfarm_framework.input_date(id, label, 0)
        return datetime.fromtimestamp(timestamp/1000) # we lose the milliseconds
    return default    

def input_string(id, label, default = ""):
    if voxelfarm_framework:
        return voxelfarm_framework.input_string(id, label, default)
    return default    

def input_bool(id, label, default = None):
    if voxelfarm_framework:
        return voxelfarm_framework.input_bool(id, label, default)
    return default

def set_query(entity, query):
    if voxelfarm_framework:
        voxelfarm_framework.set_query(entity, query)

def set_attributes(entity, attributes):
    if voxelfarm_framework:
        voxelfarm_framework.set_attributes(entity, attributes)

def set_attribute_gradient(entity, attribute, min_value, max_value):
    if voxelfarm_framework:
        voxelfarm_framework.set_attribute_gradient(entity, attribute, min_value, max_value)

def start_composite():
    if voxelfarm_framework:
        return voxelfarm_framework.start_composite()
    return -1

def add_layer(layers, entity, merge_mode=layer_merge_mode.override):
    if voxelfarm_framework:
        voxelfarm_framework.add_layer(layers, entity, merge_mode)

def get_entity_type(entity):
    if voxelfarm_framework:
        return voxelfarm_framework.get_entity_type(entity)
    return 0

def get_entity_name(entity):
    if voxelfarm_framework:
        return voxelfarm_framework.get_entity_name(entity)
    return ''

def get_entity_date(entity):
    if voxelfarm_framework:
        timestamp = voxelfarm_framework.get_entity_date(entity)
        return datetime.fromtimestamp(timestamp/1000) #we lose the milliseconds
    return datetime.now

def get_entity_attributes(entity):
    if voxelfarm_framework:
        attributes = voxelfarm_framework.get_entity_attributes(entity)
        return attributes
    return ''

def folder_contains(folder, entity):
    if voxelfarm_framework:
        return voxelfarm_framework.folder_contains(folder, entity)
    return False

def get_attributes(attributes):
    if voxelfarm_framework:
        count = voxelfarm_framework.get_attribute_count(attributes)
        return range(0, count)

    attrs = attribute.split()   
    return range(0, len(attrs))      

def get_attribute_name(attributes, index):
    if voxelfarm_framework:
        return voxelfarm_framework.get_attribute_name(attributes, index)

    attrs = attribute.split()   
    if index < len(attrs):
        return attrs[index]
    return ''

def get_attribute_index(attributes, name):
    if voxelfarm_framework:
        return voxelfarm_framework.get_attribute_index(attributes, name)

    attrs = attribute.split()   
    if name in attrs:
        return attrs.index(name)
    return -1    

def start_sum(item, property):
    return start_operation(item, property, operation_type.sum)

def sum(id, value):
    operation(id, value)

def start_minimum(item, property):
    return start_operation(item, property, operation_type.min)

def min(id, value):
    operation(id, value)

def start_maximum(item, property):
    return start_operation(item, property, operation_type.max)

def max(id, value):
    operation(id, value)

def start_average(item, property):
    return start_operation(item, property, operation_type.avg)

def avg(id, value):
    operation(id, value)

def start_operation(item, property, operation):
    if voxelfarm_framework:
        return voxelfarm_framework.start_operation(item, property, operation)
    return -1

def operation(id, value):
    if voxelfarm_framework:
        voxelfarm_framework.operation(id, value)

def get_material(component, voxel):
    if voxelfarm_framework:
        return voxelfarm_framework.get_material(component, voxel)
    return None

def get_channels(component):
    if voxelfarm_framework:
        count = voxelfarm_framework.get_channel_count(component)
        return range(0, count)
    return range(0)

def get_volume(component, voxel):
    if voxelfarm_framework:
        return voxelfarm_framework.get_volume(component, voxel)
    return 0

def get_channel_volume(component, voxel, channel):
    if voxelfarm_framework:
        return voxelfarm_framework.get_volume_channel(component, voxel, channel)
    return 0

def get_attribute_value(component, attribute, voxel):
    if voxelfarm_framework:
        return voxelfarm_framework.get_attribute(component, attribute, voxel)
    return 0

def get_channel_attribute_value(component, attribute, voxel, channel):
    if voxelfarm_framework:
        return voxelfarm_framework.get_attribute_channel(component, attribute, voxel, channel)
    return 0

def load_voxels(entity, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.load_voxels(entity, attributes, serialize_attributes(custom_attributes))
    return -1

def voxels_intersection(componentA, componentB, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.voxels_intersection(componentA, componentB, attributes, serialize_attributes(custom_attributes))
    return -1

def voxels_union(componentA, componentB, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.voxels_union(componentA, componentB, attributes, serialize_attributes(custom_attributes))
    return -1

def voxels_complement(componentA, componentB, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.voxels_complement(componentA, componentB, attributes, serialize_attributes(custom_attributes))
    return -1

def voxels_attributes(componentA, componentB, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.voxels_attributes(componentA, componentB, attributes, serialize_attributes(custom_attributes))
    return -1

def load_mesh(entity, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.load_mesh(entity, attributes, serialize_attributes(custom_attributes))
    return -1

def mesh_intersection(componentA, componentB, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.mesh_intersection(componentA, componentB, attributes, serialize_attributes(custom_attributes))
    return -1

def mesh_union(componentA, componentB, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.mesh_union(componentA, componentB, attributes, serialize_attributes(custom_attributes))
    return -1

def mesh_complement(componentA, componentB, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.mesh_complement(componentA, componentB, attributes, serialize_attributes(custom_attributes))
    return -1

def mesh_attributes(componentA, componentB, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.mesh_attributes(componentA, componentB, attributes, serialize_attributes(custom_attributes))
    return -1

def load_points(entity, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.load_points(entity, attributes, serialize_attributes(custom_attributes))
    return -1

def load_blocktree(entity, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.load_blocktree(entity, attributes, serialize_attributes(custom_attributes))
    return -1

def load_density(entity, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.load_density(entity, attributes, serialize_attributes(custom_attributes))
    return -1

def load_terrain_composite(entity, attributes, custom_attributes):
    if voxelfarm_framework:
        return voxelfarm_framework.load_surface_composite(entity, attributes, serialize_attributes(custom_attributes))
    return -1

def load_texture(entity, type):
    if voxelfarm_framework:
        return voxelfarm_framework.load_texture(entity, type)
    return -1

def load_texture_stack():
    if voxelfarm_framework:
        return voxelfarm_framework.load_texture_stack()
    return ''

def apply_texture(component, texture, type):
    if voxelfarm_framework:
        return voxelfarm_framework.apply_texture(component, texture, type)

def apply_texture_stack(component, textures, type):
    if voxelfarm_framework:
        return voxelfarm_framework.apply_texture_stack(component, textures, type)

def new_region_scope(region):
    if voxelfarm_framework:
        return range(0, voxelfarm_framework.new_region_scope(region))
    return range(0)        

def render(component, material):
    if voxelfarm_framework:
        materialData = material.serialize() if material != None else ""
        voxelfarm_framework.render(component, materialData)

def log(message):
    if voxelfarm_framework:
        voxelfarm_framework.log(message)
    else:
        print(message)    

def new_material():
    return Material()

def input_duplicate(entity):
    if voxelfarm_framework:
        return voxelfarm_framework.input_duplicate(entity)
    return -1

def new_plane(a, b, c, d):
    if voxelfarm_framework:
        return voxelfarm_framework.new_plane(a, b, c, d)
    return -1

def get_enum_attribute_name_count(component, attribute_name):
    if voxelfarm_framework:
        return voxelfarm_framework.get_enum_attribute_count(component, attribute_name)
    return 0

def get_enum_attribute_name_value(component, attribute_name, index):
    if voxelfarm_framework:
        return voxelfarm_framework.get_enum_attribute_name_value(component, attribute_name, index)
    return ''
    
def get_enum_attribute_count(component, attribute):
    if voxelfarm_framework:
        return voxelfarm_framework.get_enum_attribute_count(component, attribute)
    return 0

def get_enum_attribute_value(component, attribute, index):
    if voxelfarm_framework:
        return voxelfarm_framework.get_enum_attribute_value(component, attribute, index)
    return ''
    
def set_component_attribute_merge_mode(component, attribute, merge_mode):
    if voxelfarm_framework:
        return voxelfarm_framework.set_component_attribute_merge_mode(component, attribute, merge_mode)

def valid_volume_channel(component, channel):
    if voxelfarm_framework:
        return voxelfarm_framework.valid_volume_buffer(component, channel)
    return False

def valid_attribute_channel(component, attribute, channel):
    if voxelfarm_framework:
        return voxelfarm_framework.valid_attribute_buffer(component, attribute, channel)
    return False

def valid_volume_buffer(component):
    if voxelfarm_framework:
        return voxelfarm_framework.valid_volume_buffer(component)
    return False

def valid_attribute_buffer(component, attribute):
    if voxelfarm_framework:
        return voxelfarm_framework.valid_attribute_buffer(component, attribute)
    return False

def get_voxel_volume():
    if voxelfarm_framework:
        return voxelfarm_framework.get_voxel_volume()
    return False

def load_pandas_dataframe(component):
    return None

def sum_pandas_result(name, df):
    pass

def export(component, name):
    if voxelfarm_framework:
        voxelfarm_framework.export(component, name)

def store(component):
    if voxelfarm_framework:
        voxelfarm_framework.store(component)

def add_property(layer, key, value):
    if voxelfarm_framework:
        voxelfarm_framework.add_property(layer, key, str(value))

# Generator

def init():
    pass

def set_vector(index, vx, vy, vz):
    if voxelfarm_framework:
        voxelfarm_framework.set_vector(index, vx, vy, vz)

def set_material(index, id):
    if voxelfarm_framework:
        voxelfarm_framework.set_material(index, id)

def set_field(index, value):
    if voxelfarm_framework:
        voxelfarm_framework.set_field(index, value)

def get_voxel_origin(index):
    if voxelfarm_framework:
        return voxelfarm_framework.get_voxel_origin(index, 44)
    return (0,0,0)

def get_field_origin(index):
    if voxelfarm_framework:
        return voxelfarm_framework.get_voxel_origin(index, 45)
    return (0,0,0)

def set_entity_bounds_x(v0, v1):
    if voxelfarm_framework:
        if voxelfarm_framework.set_entity_bounds(0, v0, v1) == 0:
            cellIsEmpty()

def set_entity_bounds_y(v0, v1):
    if voxelfarm_framework:
        if voxelfarm_framework.set_entity_bounds(1, v0, v1) == 0:
            cellIsEmpty()

def set_entity_bounds_z(v0, v1):
    if voxelfarm_framework:
        if voxelfarm_framework.set_entity_bounds(2, v0, v1) == 0:
            cellIsEmpty()

def get_field_origin_x(index):
    if voxelfarm_framework:
        return voxelfarm_framework.get_voxel_origin_axis(index, 45, 0)
    return 0.0

def get_field_origin_y(index):
    if voxelfarm_framework:
        return voxelfarm_framework.get_voxel_origin_axis(index, 45, 1)
    return 0.0

def get_field_origin_z(index):
    if voxelfarm_framework:
        return voxelfarm_framework.get_voxel_origin_axis(index, 45, 2)
    return 0.0

def get_voxel_origin_axis(index, dimension, axis):
    return (0,0,0)

def cellIsEmpty():
    pass

def test():
    pass

