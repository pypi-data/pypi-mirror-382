import voxelfarm
import pandas as pd
import numpy as np
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

class DrillHoleOptions:
    show_collars = True
    show_cylinders = True

class report_lambda_framework:

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

    def start_sum(self, item, property):
        return -1

    def sum(self, id, value):
        pass

    def start_minimum(self, item, property):
        return -1

    def min(self, id, value):
        pass

    def start_maximum(self, item, property):
        return -1

    def max(self, id, value):
        pass

    def start_average(self, item, property):
        return -1

    def avg(self, id, value):
        pass

    def start_operation(self, item, property, operation):
        pass

    def operation(self, id, value):
        pass

    def get_material(self, entity, voxel):
        return 0

    def get_volume(self, entity, voxel):
        return 0.0

    def get_channel_volume(self, component, voxel, channel):
        return 0.0

    def get_attribute_value(self, entity, attribute, voxel):
        return 0.0

    def get_channel_attribute_value(self, component, attribute, voxel, channel):
        return 0.0

    def load_voxels(self, entity, attributes, custom_attributes):
        return 0

    def voxels_intersection(self, componentA, componentB, attributes, custom_attributes):
        return 0

    def voxels_union(self, componentA, componentB, attributes, custom_attributes):
        return 0

    def voxels_complement(self, componentA, componentB, attributes, custom_attributes):
        return 0

    def voxels_attributes(self, componentA, componentB, attributes, custom_attributes):
        return 0

    def new_region_scope(self, region):
        return 0

    def set_field(self, v, value):
        pass

    def log(self, message):
        print(message)

    def input_duplicate(self, entity):
        return 0

    def new_plane(self, a, b, c, d):
        return -1    

    def get_enum_attribute_name_count(self, component, attribute_name):
        return 0

    def get_enum_attribute_name_value(self, component, attribute_name, index):
        return 0
        
    def get_enum_attribute_count(self, component, attribute):
        return 0

    def get_enum_attribute_value(self, component, attribute, index):
        return 0

    def set_component_attribute_merge_mode(self, component, attribute, merge_mode):
        pass
        
    def get_component_attributes(self, component):
        return []

    def get_component_data_buffers(self, component):
        return None

    def is_meta(self):
        return True

    def add_property(self, layer, key, value):
        pass

    def store(self, component):
        pass

    def get_voxel_centroid(self, v, axis):
        return 0.0

class report_lambda_host:

    version = (3,0,1,7)

    def __init__(self, framework = None):  
        if framework:
            self.lambda_framework = framework
        else:
            if voxelfarm.voxelfarm_framework:
                self.lambda_framework = voxelfarm.voxelfarm_framework
            else:
                self.lambda_framework = report_lambda_framework()

        if self.lambda_framework.is_meta():
            self.voxelCount = 1   
            self.fieldCount = 1  
        else:
            self.voxelCount = 40*40*40
            self.fieldCount = 45*45*45

        self.voxels = range(0, self.voxelCount)
        self.field = range(0, self.fieldCount)

    def get_voxels(self, component):
        voxel_count = self.lambda_framework.get_voxels(component)
        return range(0, voxel_count)

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
        return self.start_operation(item, property, operation_type.sum)

    def sum(self, id, value):
        self.operation(id, value)

    def start_minimum(self, item, property):
        return self.start_operation(item, property, operation_type.min)

    def min(self, id, value):
        self.operation(id, value)

    def start_maximum(self, item, property):
        return self.start_operation(item, property, operation_type.max)

    def max(self, id, value):
        self.operation(id, value)

    def start_average(self, item, property):
        return self.start_operation(item, property, operation_type.avg)

    def avg(self, id, value):
        self.operation(id, value)

    def start_operation(self, item, property, operation):
        return self.lambda_framework.start_operation(item, property, operation)

    def operation(self, id, value):
        self.lambda_framework.operation(id, value)

    def get_material(self, component, voxel):
        return self.lambda_framework.get_material(component, voxel)

    def get_channels(self, component):
        count = self.lambda_framework.get_channel_count(component)
        return range(0, count)

    def get_volume(self, component, voxel):
        return self.lambda_framework.get_volume(component, voxel)

    def get_channel_volume(self, component, voxel, channel):
        return self.lambda_framework.get_volume_channel(component, voxel, channel)

    def get_attribute_value(self, component, attribute, voxel):
        return self.lambda_framework.get_attribute(component, attribute, voxel)

    def get_channel_attribute_value(self, component, attribute, voxel, channel):
        return self.lambda_framework.get_attribute_channel(component, attribute, voxel, channel)

    def load_voxels(self, entity, attributes, custom_attributes):
        return self.lambda_framework.load_voxels(entity, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def voxels_intersection(self, componentA, componentB, attributes, custom_attributes):
        return self.lambda_framework.voxels_intersection(componentA, componentB, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def voxels_union(self, componentA, componentB, attributes, custom_attributes):
        return self.lambda_framework.voxels_union(componentA, componentB, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def voxels_complement(self, componentA, componentB, attributes, custom_attributes):
        return self.lambda_framework.voxels_complement(componentA, componentB, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def voxels_attributes(self, componentA, componentB, attributes, custom_attributes):
        return self.lambda_framework.voxels_attributes(componentA, componentB, attributes, voxelfarm.serialize_attributes(custom_attributes))

    def new_region_scope(self, region):
        return range(0, self.lambda_framework.new_region_scope(region))

    def get_voxel_origin(self, v):
        return (0,0,0)

    def get_voxel_centroid(self, component, v):
        x = self.lambda_framework.get_voxel_centroid(component, v, 0)    
        y = self.lambda_framework.get_voxel_centroid(component, v, 1)    
        z = self.lambda_framework.get_voxel_centroid(component, v, 2)    
        return (x,y,z)

    def get_field_origin(self, v):
        return (0,0,0)

    def set_field(self, v, value):
        self.lambda_framework.set_field(v, value)

    def log(self, message):
        self.lambda_framework.log(message)

    def input_duplicate(self, entity):
        return self.lambda_framework.input_duplicate(entity)

    def new_plane(self, a, b, c, d):
        return self.lambda_framework.new_plane(a, b, c, d)

    def get_enum_attribute_name_count(self, component, attribute_name):
        return self.lambda_framework.get_enum_attribute_count(component, attribute_name)

    def get_enum_attribute_name_value(self, component, attribute_name, index):
        return self.lambda_framework.get_enum_attribute_name_value(component, attribute_name, index)
        
    def get_enum_attribute_count(self, component, attribute):
        return self.lambda_framework.get_enum_attribute_count(component, attribute)

    def get_enum_attribute_value(self, component, attribute, index):
        return self.lambda_framework.get_enum_attribute_value(component, attribute, index)
        
    def set_component_attribute_merge_mode(self, component, attribute, merge_mode):
        return self.lambda_framework.set_component_attribute_merge_mode(component, attribute, merge_mode)

    def valid_volume_channel(self, component, channel):
        return self.lambda_framework.valid_volume_buffer(component, channel)

    def valid_attribute_channel(self, component, attribute, channel):
        return self.lambda_framework.valid_attribute_buffer(component, attribute, channel)

    def get_voxel_volume(self):
        return self.lambda_framework.get_voxel_volume()
    
    def convert_series_to_alphanumerical(self, metadata_component, attribute, values):
        return values.apply(lambda x: self.get_enum_attribute_name_value(metadata_component, attribute, int(x)))
    
    def convert_to_alphanumerical(self, metadata_component, column, df):
        if not df.empty:
            if column:
                if column in df:
                    metadata_column = column
                    if metadata_column == 'mesh_id':
                        metadata_column = 'mesh_name'

                    return df.apply(lambda row : self.get_enum_attribute_name_value(metadata_component, metadata_column, int(row[column])-1), axis = 1)
            else:            
                metadata_column = 'mesh_name'
                return df.apply(lambda row : self.get_enum_attribute_name_value(metadata_component, metadata_column, int(row.name)-1), axis = 1)

        return np.nan

    def load_pandas_dataframe(self, component):
        component_data = []
        component_columns = self.lambda_framework.get_component_attributes(component)
        attrCount = len(component_columns)
        component_buffers = self.lambda_framework.get_component_data_buffers(component)
        if component_buffers:
            serialData = np.array(component_buffers)
            component_data = serialData.reshape(-1, attrCount)
        
        df = pd.DataFrame(data=component_data, columns=component_columns)
        if 'volume' in df:
            volume = self.get_voxel_volume()
            df['volume'] *= volume

        return df

    def sum_pandas_result(self, name, df):
        if not df.empty: 
            if isinstance(df, pd.DataFrame):
                indices = []
                if isinstance(df.index, pd.core.indexes.multi.MultiIndex):
                    for index_list in df.index:
                        multi_index = ''
                        for index in index_list:
                            if multi_index:
                                multi_index += ';' + str(index)
                            else:
                                multi_index = str(index)

                        indices.append(multi_index)
                else:
                    indices = df.index.astype(str).tolist()

                columns = df.columns.tolist()
                data = df.to_numpy().tolist()
                self.lambda_framework.sum_data_buffers(name, indices, columns, data)
            elif isinstance(df, pd.Series):
                indices = df.index.astype(str).tolist()
                columns = None
                data = df.to_numpy().tolist()
                self.lambda_framework.sum_data_buffers(name, indices, columns, data)

    def add_property(self, item, key, value):
        self.lambda_framework.add_property(item, key, str(value))

    def store(self, component):
        self.lambda_framework.store(component)
