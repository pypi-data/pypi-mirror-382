import zipfile
import json
import base64
import time
import requests
from datetime import datetime, timedelta
import os
import random
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from io import StringIO
import io
import sys
import urllib3
import urllib.parse
import shutil
import voxelfarm
import logging
from enum import Enum

logger = logging.getLogger('voxelfarm')
logger.setLevel(logging.DEBUG)

class mock_workflow_framework:

    def __init__(self, project, vf_api):  
        self.project = project
        self.vf_api = vf_api

    def input_string(self, id, label, default = ""):
        if id == 'project_id':
            return self.project
        elif id == 'project':
            return self.project
        
        return default

    def log(self, message):
        print(message)

    def progress(self, progress, message):
        print(str(progress) + ' ' + message)

    def get_entity(self, id = None):
        if id is None:
            id = self.project
        return self.vf_api.get_entity(id, self.project)

    def download_entity_file(self, filename, id = None):
        return ""
    
    def query_entity_files(self, query, id = None):
        return ""
    
    def get_scrap_folder(self):
        return ""

    def get_tools_folder(self):
        return ""

    def get_entity_folder(self, id = None):
        return ""

    def download_entity_files(self, id = None):
        return ""

    def download_entity_file(self, filename, id = None):
        return ""

    def attach_file(self, filename, id = None):
        pass

    def attach_folder(self, folder, id = None):
        pass

    def upload(self, filename, name, id = None):
        pass

    def set_exit_code(self, code):
        print('Exit code: ' + str(code))

    def get_entity_file_list(self, id = None):
        return []
    
    def update_type(self):
        return None

    def stage_done(self):
        return False

    def get_vf_api(self):
        return self.vf_api
    
    def increment_counter(self, counter, offset = 1):
        return 0
    
    def decrement_counter(self, counter, offset = 1):
        return 0

    def set_counter(self, counter, value = 0):
        pass

    def get_working_dir(self):
        return ''

    def get_notify_emails(self):
        return ''

    def get_notify_users_url(self):
        return ''

    def get_workflow_api(self):
        return ''

    def publish_feed(self, filename):
        return {'success': True}
    
    def cache_entity_file(self, entity_id, file, alias):
        return ""

    def get_webex_token(self):
        return ''

class debug_framework:

    def __init__(self, vf, project, entity, update_type, scrap, tools, working_dir):  
        self.vf = vf
        self.projectId = project
        self.entityId = entity
        self.scrap = scrap
        self.tools = tools
        self.working_dir = working_dir
        if update_type:
            self.update = update_type
            self.stage = True
        else:
            self.update = ''
            self.stage = False

        self.project = self.vf.get_entity(project, project)
        self.entity = self.vf.get_entity(entity, project)

        self.inputs = {}
        self.properties = {}
        self.alias = {}

        self.inputs['project_id'] = self.projectId

        if self.entity:
            self.versionId = self.entity['file_folder']
            self.version = self.vf.get_entity(self.versionId, project)

            for key in self.entity:
                if key.startswith('input_value_'):
                    prop = key[len('input_value_'):]
                    value = self.entity[key]
                    self.inputs[prop] = value

            for key in self.version:
                if key.startswith('alias_'):
                    prop = key[len('alias_'):]
                    value = self.version[key]
                    self.alias[prop] = value
                elif key.startswith('version_'):
                    prop = key[len('version_'):]
                    value = self.version[key]
                    self.properties[prop] = value

        else:
            self.versionId = '0'
            self.entityId = self.projectId
            self.entity = self.project
            self.inputs['version_folder_id'] = '0'

        self.inputs['version_folder_id'] = self.versionId

    def input_string(self, id, label, default = ""):
        if id in self.inputs:
            return self.inputs[id]
        else:
            return default

    def log(self, message):
        print(message)

    def progress(self, progress, message):
        print(f'{progress}% {message}')

    def get_scrap_folder(self):
        return self.scrap

    def get_tools_folder(self):
        return self.tools

    def get_entity_folder(self, id = None):
        if id is None:
            id = self.entityId

        folder = os.path.join(self.get_scrap_folder(), id)    
        return folder

    def download_entity_files(self, id = None):
        if id is None:
            id = self.entityId

        entity_files = self.vf.get_file_list(self.projectId, id)
        for file in entity_files:
            self.download_entity_file(file, id)

        folder = os.path.join(self.get_scrap_folder(), id)    
        return folder
    
    def download_entity_file(self, filename, id = None):
        if id is None:
            id = self.entityId

        entity_files = self.vf.get_file_list(self.projectId, id)
        if filename in entity_files:
            folder = os.path.join(self.get_scrap_folder(), id)    
            if not os.path.exists(folder):        
                os.mkdir(folder)

            local_attr_file = os.path.join(folder, filename)
            if os.path.exists(local_attr_file):        
                return local_attr_file
            else:
                if self.vf.download_file(self.projectId, id, filename, local_attr_file):
                    if filename.lower().endswith(".zip") and os.path.isfile(local_attr_file):
                        with zipfile.ZipFile(local_attr_file, "r") as zip_ref:
                            zip_ref.extractall(folder)

                    return local_attr_file
                
        return ''

    def query_entity_files(self, query, id = None):
        if query:
            if id is None:
                id = self.entityId

            entity_files = self.vf.get_file_list(self.projectId, id)
            for file in entity_files:
                if file.startswith(query):
                    self.download_entity_file(file, id)

            folder = os.path.join(self.get_scrap_folder(), id)    
            return folder    
        else:
            return self.download_entity_files(id)
        
    def attach_file(self, filename, id = None):
        if id is None:
            id = self.entityId

        files = {'file': open(filename, 'rb')}
        self.vf.attach_files(project=self.projectId, id=id, files=files)

    def attach_folder(self, folder, id = None):
        print(f'attach filder {folder} to entity {id}')
        return True

    def remove_file(self, filename, id = None):
        print(f'remove_file {filename} from entity {id}')
        return True

    def upload(self, filename, name, id = None):
        if id is None:
            id = self.entityId

        print(f'upload {filename} to {id} with name {name}')

    def set_exit_code(self, code):
        print(f'set_exit_code {code}')

    def get_entity(self, id = None):
        if id is None:
            id = self.entityId

        entity = self.vf.get_entity(id, self.projectId)
        return entity

    def get_entity_file_list(self, id = None):
        if id is None:
            id = self.entityId

        return self.vf.get_file_list(self.projectId, id)

    def export_file(self, local_file_location, drop_zone_file_location):
        print(f'export_file {local_file_location} {drop_zone_file_location}')

    def update_type(self):
        return self.update

    def stage_done(self):
        return self.stage

    def get_vf_api(self):
        return self.vf
    
    def increment_counter(self, counter, offset = 1):
        self.entity = self.vf.get_entity(self.entityId, self.projectId)

        value = offset
        if counter in self.entity:
            value += float(self.entity[counter])

        self.vf.update_entity(
            id=self.entityId,
            project=self.projectId, 
            fields={
                f'{counter}' : f'{value}'
            })

        return value
    
    def decrement_counter(self, counter, offset = 1):
        self.entity = self.vf.get_entity(self.entityId, self.projectId)

        value = -offset
        if counter in self.entity:
            value += float(self.entity[counter])

        self.vf.update_entity(
            id=self.entityId,
            project=self.projectId, 
            fields={
                f'{counter}' : f'{value}'
            })

        return value

    def set_counter(self, counter, value = 0):
        self.vf.update_entity(
            id=self.entityId,
            project=self.projectId, 
            fields={
                f'{counter}' : f'{value}'
            })

    def get_working_dir(self):
        if self.working_dir:
            return self.working_dir
        else:
            folder = os.path.join(self.get_scrap_folder(), self.entityId)    
            return folder

    def swarm_db_upload(self, entity_id, folder, name, title):
        print(f'swarm_db_upload {entity_id} {folder} {name} {title}')
        return True

    def get_property(self, property):
        if property in self.properties:
            return self.properties[property]
        else:
            return ''

    def set_property(self, property, value):
        self.properties[property] = value

class debug_function_framework:

    def __init__(self, vf, project, inputs, scrap_folder, working_folder):  
        self.vf = vf
        self.projectId = project
        self.inputs = inputs
        self.scrap = scrap_folder
        self.working_dir = working_folder
        self.project_entity = vf.get_entity(project, project)
        self.properties = {}

    def input_string(self, id, label, default = ""):
        if id in self.inputs:
            return self.inputs[id]
        else:
            return default

    def log(self, message):
        print(message)

    def get_scrap_folder(self):
        return self.scrap

    def get_working_folder(self):
        return self.working_dir

    def download_entity_files(self, id):
        entity_files = self.vf.get_file_list(self.projectId, id)
        for file in entity_files:
            self.download_entity_file(file, id)

        folder = os.path.join(self.get_scrap_folder(), id)    
        return folder
    
    def download_entity_file(self, filename, id):
        entity_files = self.vf.get_file_list(self.projectId, id)
        if filename in entity_files:
            folder = os.path.join(self.get_scrap_folder(), id)    
            if not os.path.exists(folder):        
                os.mkdir(folder)

            local_attr_file = os.path.join(folder, filename)
            if os.path.exists(local_attr_file):        
                return local_attr_file
            else:
                if self.vf.download_file(self.projectId, id, filename, local_attr_file):
                    if filename.lower().endswith(".zip") and os.path.isfile(local_attr_file):
                        with zipfile.ZipFile(local_attr_file, "r") as zip_ref:
                            zip_ref.extractall(folder)

                    return local_attr_file
                
        return ''

    def attach_file(self, filename, id):
        files = {'file': open(filename, 'rb')}
        self.vf.attach_files(project=self.projectId, id=id, files=files)

    def remove_file(self, filename, id):
        print(f'remove_file {filename} from entity {id}')
        return True

    def set_exit_code(self, code):
        print(f'set_exit_code {code}')

    def get_entity(self, id):
        entity = self.vf.get_entity(id, self.projectId)
        return entity

    def get_entity_file_list(self, id):
        return self.vf.get_file_list(self.projectId, id)

    def get_product_property(self, product, property):
        if self.project_entity:
            product_key = "workflow_folder_" + product
            if product_key in self.project_entity:
                product_id = self.project_entity[product_key]
                product_entity = self.get_entity(product_id)
                if product_entity and ("version_active" in product_entity):
                    version_active = product_entity["version_active"]
                    version_entity = self.get_entity(version_active)
                    propertyKey = "version_" + property
                    if version_entity and (propertyKey in version_entity):
                        return version_entity[propertyKey]
        return ""
    
    def get_product_alias(self, product, alias):
        if self.project_entity:
            product_key = "workflow_folder_" + product
            if product_key in self.project_entity:
                product_id = self.project_entity[product_key]
                product_entity = self.get_entity(product_id)
                if product_entity and ("version_active" in product_entity):
                    version_active = product_entity["version_active"]
                    version_entity = self.get_entity(version_active)
                    aliasKey = "alias_" + alias
                    if version_entity and (aliasKey in version_entity):
                        return version_entity[aliasKey]
        return ""
    
    def get_product_singleton(self, product, singleton):
        if self.project_entity:
            product_key = "workflow_folder_" + product
            if product_key in self.project_entity:
                product_id = self.project_entity[product_key]
                product_entity = self.get_entity(product_id)
                if product_entity:
                    singleton_key = "workflow_singleton_" + singleton
                    if singleton_key in product_entity:
                        return product_entity[singleton_key]
        return ""
    
    def get_property(self, property):
        if property in self.properties:
            return self.properties[property]
        return ''

    def set_property(self, property, value):
        self.properties[property] = value

class AccessLevel(Enum):
    NONE = "none"
    FULL = "full"
    WRITE = "write"
    READ = "read"

class rest:

    OrgId = '2343243456678890'
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

    CRSFields = [
        "coord_origin_x",
        "coord_origin_y",
        "coord_origin_z",
        "coord_hdatum",
        "coord_vdatum",
        "coord_projection",
        "coord_unit",
        "voxel_size",
        "coord_projection_tm_falseEasting",
        "coord_projection_tm_falseNorthing",
        "coord_projection_tm_latOriginDeg",
        "coord_projection_tm_longMeridianDeg",
        "coord_projection_tm_scaleFactor",
        "coord_projection_lcc_falseEasting",
        "coord_projection_lcc_falseNorthing",
        "coord_projection_lcc_latOfOriginDeg",
        "coord_projection_lcc_longOfOriginDeg", 
        "coord_projection_lcc_firstStdParallelDeg",
        "coord_projection_lcc_secondStdParallelDeg",
        "coord_projection_aeac_falseEasting",
        "coord_projection_aeac_falseNorthing",
        "coord_projection_aeac_latOfOriginDeg",
        "coord_projection_aeac_longOfOriginDeg", 
        "coord_projection_aeac_firstStdParallelDeg",
        "coord_projection_aeac_secondStdParallelDeg",
        "coord_projection_amg_zone",
        "coord_projection_utm_easting",
        "coord_projection_utm_northing"]

    DefaultFields = {
        entity_type.VoxelTerrain : {
            'include_classification' : '0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31',
        },
        entity_type.VoxelMesh : {
            'translate_x' : '0',
            'translate_y' : '0',
            'translate_z' : '0',
            'scale_x' : '1',
            'scale_y' : '1',
            'scale_z' : '1',
            'rotate_x' : '0',
            'rotate_y' : '0',
            'rotate_z' : '0',
            'rotation_order' : 'ZXZ',
        },
        entity_type.IndexedMesh : {
            'translate_x' : '0',
            'translate_y' : '0',
            'translate_z' : '0',
            'scale_x' : '1',
            'scale_y' : '1',
            'scale_z' : '1',
            'rotate_x' : '0',
            'rotate_y' : '0',
            'rotate_z' : '0',
            'rotation_order' : 'ZXZ',
        },
        entity_type.BlockModel : {
            'translate_x' : '0',
            'translate_y' : '0',
            'translate_z' : '0',
            'scale_x' : '1',
            'scale_y' : '1',
            'scale_z' : '1',
            'rotate_x' : '0',
            'rotate_y' : '0',
            'rotate_z' : '0',
            'rotation_order' : 'ZXZ',
            'bm_type': 'VOXBM1'
        },
        entity_type.OrthoVox : {
            'translate_x' : '0',
            'translate_y' : '0',
            'translate_z' : '0',
            'scale_x' : '1',
            'scale_y' : '1',
            'scale_z' : '1',
            'rotate_x' : '0',
            'rotate_y' : '0',
            'rotate_z' : '0',
            'rotation_order' : 'ZXZ'
        },
        entity_type.TerrainComposite : {
            'translate_x' : '0',
            'translate_y' : '0',
            'translate_z' : '0',
            'scale_x' : '1',
            'scale_y' : '1',
            'scale_z' : '1',
            'rotate_x' : '0',
            'rotate_y' : '0',
            'rotate_z' : '0',
            'rotation_order' : 'ZXZ'
        }
    }

    def __init__(self, apiurl=None):
        self.proxy = None
        if apiurl == None:
            self.VFAPIURL = os.getenv('VF_API')
            if (self.VFAPIURL == None):
                self.VFAPIURL = "http://localhost.com"      # "https://api.voxelfarm.com"
        else:
            self.VFAPIURL = apiurl
        self.VFAPIURL_ENTITY = self.VFAPIURL + '/entity.ashx'
        self.VFAPIURL_FILE = self.VFAPIURL + '/file.ashx'
        self.VFAPIURL_EVENT = self.VFAPIURL + '/events.ashx'

        self.token: str = None
        self.aad_credentials : dict = None
        self.ts_api_version = "2020-07-31"
        self.ts_environmentName = os.getenv('vf_ts_hub_name')
        self.ts_applicationName = os.getenv('vf_ts_app_name')
        self.HTTPSession = urllib3.PoolManager()   

    def set_proxy(self, proxy):
        self.proxy = proxy

    class api_result:
        def __init__(self):      
            self.success = False
            self.error_info = ''

    class creation_result(api_result):
        def __init__(self):      
            self.id = ''

    class counter_result(api_result):
        def __init__(self):      
            self.value = ''

    class multiple_creation_result():
        def __init__(self):      
            self.success = False
            self.error_info = ''
            self.ids = []

    class wait_result(api_result):
        def __init__(self):      
            self.complete = False
            self.times = {}

    def add_default_fields(self, type, fields):
        if type in self.DefaultFields:
            for field in self.DefaultFields[type]:
                if not field in fields:
                    fields[field] = self.DefaultFields[type][field]
        if not 'file_date' in fields:
            fields['file_date'] = str(1000 * int(time.time()))

    class crs_result(api_result):
        def __init__(self):      
            self.crs = {}

    def get_project_crs(self, project):
        result = self.crs_result()
        params = {'id': project, 'project': project}

        #projectRequest = self.HTTPSession.get(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), proxies=self.proxy)
        request = self.HTTPSession.request(method="GET", url=self.VFAPIURL_ENTITY, fields=params, headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}' 
            return result
        
        try:        
            entityJson = json.loads(request.data.decode("utf-8"))

            values = {
                'coord_hunit': entityJson['coord_unit'],
                'coord_vunit': entityJson['coord_unit']
            }
            for field in self.CRSFields:
                if field in entityJson:
                    values[field] = entityJson[field]
                else:
                    values[field] = '0'
            result.crs = values
            result.success = True
        except Exception as e:
            result.success = False
            result.error_info = f'Exception: {e}'
        return result

    def get_entity(self, id, project = None):
        params={'id': id}
        if project:
            params['project'] = project
        #projectRequest = self.HTTPSession.get(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), proxies=self.proxy)
        request = self.HTTPSession.request(method="GET", url=self.VFAPIURL_ENTITY, fields=params, headers=self.get_auth_headers())

        if request.status != 200:
            return None
        entityJson = json.loads(request.data.decode("utf-8"))
        return entityJson

    def get_projects_names(self):
        result = self.collection_result()
        #entityRequest = self.HTTPSession.get(self.VFAPIURL_ENTITY, headers=self.get_auth_headers())
        request = self.HTTPSession.request(method="GET", url=self.VFAPIURL_ENTITY, headers=self.get_auth_headers())

        if (request.status == 200):
            entityJson = json.loads(request.data.decode("utf-8"))
            items = []
            for x in entityJson:
                v = entityJson[x]
                if v["type"] == "PROJECT_REF":
                    items.append(v["project_ref"])

            result.items = items
            result.success = True
        else:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'  
        return result

    def create_project(self, name, fields):
        result = self.creation_result()
        if fields == None:
            fields = {}
        fields['name'] = name
        self.add_default_fields(type, fields)
        data = {'operation': 'create', 'data': json.dumps(fields)}
        request = self.HTTPSession.request(method="POST", url=self.VFAPIURL_ENTITY, fields=data, headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        result.success = True
        result.id = apiResult['id']
        return result

    def delete_project(self, project):
        items = []
        # Get all entities in project
        result = self.get_collection(project)
        if not result.success:
            print(result.error_info)
            exit(3)
        entities = result.items
        for e in entities:
            items.append(e)
        #    entity = entities[e]
        #    if entity['type'] != 'USER':
        #        items.append(entity["ID"])

        # Get all user_ref objects for project (users associated with the project)
        result = self.get_collection('users:' + project)
        if not result.success:
            print(result.error_info)
            exit(4)
        user_refs = result.items
        for user_ref in user_refs:
            if user_refs[user_ref]['type'] == 'USER_REF':
                user_id = user_refs[user_ref]['user_ref']
                items.append(user_id + ':' + project)
                items.append(project + ':' + user_id)
        items.append('R3Vlc3Q=:' + project) # guest user
        self.delete_entities(project, items)

    def clean_project(self, project):
        items = []
        # Get all entities in project
        result = self.get_collection(project)
        if not result.success:
            print(result.error_info)
            exit(3)
        entities = result.items
        for e in entities:
            entity = entities[e]
            try:
                if entity['type'] != 'USER' and entity['type'] != 'PROJECT':
                    items.append(entity["ID"])
            except Exception as e:
                None
                # print(f"{e}")                    

        self.delete_entities(project, items)        

    def create_entity_raw(self, project, type, name, fields, crs):
        result = self.creation_result()
        if fields == None:
            fields = {}
            
        fields['name'] = name
        fields['type'] = 'FILE'
        fields['file_type'] = type

        if 'state' not in fields:
            fields['state'] = 'COMPLETE'

        fields['project'] = project
        for key, value in crs.items():
            fields['entity_' + key] = value
        self.add_default_fields(type, fields)
        params={'project': project}
        
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}' 
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        result.success = True
        result.id = apiResult['id']
        return result

    def add_value_atomically(self, project, id, property, value):
        result = self.counter_result()
        params = {'project': project, 'org': self.OrgId}
        data = {'operation': 'atomic_increment', 'id': id, 'property': property, 'value': value}
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, fields=data, headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = 'Error calling REST API atomic_increment operation'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success') or (property not in apiResult):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        else:    
            result.success = True
            result.value = apiResult[property]

        return result

    def update_entity(self, project, id, fields):
        result = self.creation_result()
        if fields == None:
            fields = {}
        fields['ID'] = id
        fields['project'] = project
        params={'project': project, 'id': id}
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result

        result.success = True
        result.id = id
        return result

    def create_folder(self, project, folder, name, fields = {}):
        result = self.creation_result()
        if folder == None:
            folder = '0'

        if fields == None:
            fields = {}

        fields['name'] = name
        fields['type'] = 'FILE'
        fields['file_type'] = 'FOLDER'
        fields['state'] = 'COMPLETE'
        fields['project'] = project
        fields['file_folder'] = folder
        self.add_default_fields(type, fields)
        params={'project': project}
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result

        result.success = True
        result.id = apiResult['id']
        return result

    def create_entity_processed(self, project, type, name, fields, crs, callback=None, update_type = None):
        result = self.creation_result()
        if fields == None:
            fields = {}
        fields['name'] = name
        fields['type'] = 'FILE'
        fields['file_type'] = type
        fields['project'] = project
        fields['state'] = 'PARTIAL'
        if update_type:
            fields['callback_update_type'] = update_type
        for key, value in crs.items():
            fields[key] = value

        self.add_default_fields(type, fields)
        params={'project': project}
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result

        result.id = apiResult['id']
        params={'project': project, 'org': self.OrgId, 'id': result.id}
        data={'process':'PROCESS'}
        if callback != None:
            data['callback'] = callback
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_EVENT, params=params, headers=self.get_auth_headers(), data=data, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_EVENT}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, fields=data, headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result
        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        result.success = True
        return result

    def create_process_entity(self, project, name, code, fields, inputs, files = None, callback = None, update_type = None):
        result = self.creation_result()

        # Create the Entity
        if fields == None:
            fields = {}
        fields['name'] = name
        fields['type'] = 'FILE'
        fields['file_type'] = 'PROCESS'
        fields['state'] = 'PARTIAL'
        fields['project'] = project

        fields['code'] = code

        python_file = False
        code_origin = None
        if files:
            for file in files:
                if code in file:
                    python_file = True
                    break

        if python_file:
            code_origin = 'PYTHON_FILE'
        else:
            program_entity = self.get_entity(code)
            if program_entity:
                code_origin = 'PROGRAM'

        if code_origin:
            fields['code_origin'] = code_origin
        else:
            result.success = False
            result.error_info = f'We cannot detect the code_origin from this code {code}'
            return result

        if update_type:
            fields['callback_update_type'] = update_type

        if inputs:
            for input in inputs:
                fields['input_value_' + input] = inputs[input]
                fields['input_filter_' + input] = '0'
                fields['input_type_' + input] = '0'
                fields['input_label_' + input] = '0'

        self.add_default_fields(type, fields)
        params={'project': project}
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result

        result.id = apiResult['id']

        # Attach files to the entity
        if files:
            for file in files:
                if (not os.path.exists(file)):
                    result.success = False
                    result.error_info = 'File not found: ' + file
                    return result

                attach_files = {'file': open(file, 'rb')}
                apiResult = self.attach_files(project=project, id=result.id, files=attach_files)
                if not apiResult.success:
                    result.success = False
                    result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
                    return result

        fields.clear()
        fields['partial_status'] = ""
        fields['partial_progress'] = "0"

        result = self.update_entity(
            project=project, 
            id=result.id, 
            fields=fields)

        # Process the Entity
        params={'project': project, 'org': self.OrgId, 'id': result.id}
        data={'process':'PROCESS'}
        if callback != None:
            data['callback'] = callback
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_EVENT, params=params, headers=self.get_auth_headers(), data=data, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_EVENT}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, fields=data, headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        result.success = True
        return result        

    def create_workflow_entity(self, project, name, fields, inputs):
        result = self.creation_result()

        # Create the Entity
        if fields == None:
            fields = {}
        fields['name'] = name
        fields['type'] = 'FILE'
        fields['file_type'] = 'PROCESS'
        fields['process_type'] = 'WORKFLOW'
        fields['state'] = 'PARTIAL'
        fields['background_process'] = '1'
        fields['project'] = project

        for input in inputs:
            fields['input_value_' + input] = inputs[input]
            fields['input_filter_' + input] = '0'
            fields['input_type_' + input] = '0'
            fields['input_label_' + input] = '0'

        self.add_default_fields(type, fields)
        params={'project': project}
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result

        result.id = apiResult['id']

        fields.clear()
        fields['partial_status'] = ""
        fields['partial_progress'] = "0"

        result = self.update_entity(
            project=project, 
            id=result.id, 
            fields=fields)

        # Process the Entity
        params={'project': project, 'org': self.OrgId, 'id': result.id}
        data={'process':'PROCESS'}
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_EVENT, params=params, headers=self.get_auth_headers(), data=data, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_EVENT}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, fields=data, headers=self.get_auth_headers())

        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        result.success = True
        return result        

    def create_report(self, project, program, lod, region, name, fields, inputs, callback=None, update_type = None):
        result = self.creation_result()
        if fields == None:
            fields = {}
        fields['name'] = name
        fields['type'] = 'FILE'
        fields['file_type'] = 'REPORT'
        fields['program'] = program
        fields['project'] = project
        fields['region'] = region
        fields['lod'] = str(lod)
        fields['state'] = 'PARTIAL'
        if update_type:
            fields['callback_update_type'] = update_type
        for input in inputs:
            fields['input_value_' + input] = inputs[input]
            fields['input_filter_' + input] = '0'
            fields['input_type_' + input] = '0'
            fields['input_label_' + input] = '0'
        self.add_default_fields(type, fields)
        params={'project': project}
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result

        result.id = apiResult['id']
        params={'project': project, 'org': self.OrgId, 'id': result.id}
        data={'process':'RUN_REPORT'}
        if callback != None:
            data['callback'] = callback
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_EVENT, params=params, headers=self.get_auth_headers(), data=data, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_EVENT}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, fields=data, headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
        else:
            result.success = True

        return result

    def create_export(self, project, program, lod, region, name, fields, inputs, callback=None):
        result = self.creation_result()
        if fields == None:
            fields = {}
        fields['name'] = name
        fields['type'] = 'FILE'
        fields['file_type'] = 'EXPORT'
        fields['program'] = program
        fields['project'] = project
        fields['region'] = region
        fields['lod'] = str(lod)
        fields['state'] = 'PARTIAL'

        for input in inputs:
            fields['input_value_' + input] = inputs[input]
            fields['input_filter_' + input] = '0'
            fields['input_type_' + input] = '0'
            fields['input_label_' + input] = '0'
        self.add_default_fields(type, fields)
        params={'project': project}
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        result.id = apiResult['id']
        params={'project': project, 'org': self.OrgId, 'id': result.id}
        data={'process':'RUN_EXPORT'}
        if callback != None:
            data['callback'] = callback
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_EVENT, params=params, headers=self.get_auth_headers(), data=data, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_EVENT}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, fields=data, headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
        else:
            result.success = True

        return result

    def create_view(self, project, name, view_type, inputs, fields):
        input_fields = {
            'file_folder' : '0',
            'view_type' : view_type,
            'virtual' : '1',
            'state' : 'COMPLETE',
            'color_legend_attribute' : '',
            'color_legend_attribute_index' : '-1',
            'color_legend_gradient' : 'isoluminant_cgo_70_c39_n256',
            'color_legend_interpolate_gradient' : '1',
            'color_legend_mode' : '2',
            'color_legend_range_max' : '100',
            'color_legend_range_min' : '0',
            'color_legend_range_step' : '1',
            'color_legend_reverse_gradient' : '0',
            'file_date' : str(1000 * int(time.time())),
            'file_type' : 'VIEW',
            'input_filter_colors' : '0',
            'input_filter_e' : '8',
            'input_filter_normals' : '0',
            'input_label_colors' : 'Use Ortho-imagery',
            'input_label_e' : 'Terrain',
            'input_label_normals' : 'Use high resolution detail',
            'input_type_colorlegend' : '7',
            'input_type_colors' : '6',
            'input_type_e' : '3',
            'input_type_normals' : '6',
            'input_value_colors' : '0',
            'input_value_normals' : '0',         
        }
            
        if inputs:    
            for key in inputs:
                input_fields['input_value_' + key] = inputs[key]

        if fields:
            for key in fields:
                input_fields[key] = fields[key]
            
        api_result = self.create_entity_raw(
            project=project,
            type=self.entity_type.View,
            name=name,
            fields=input_fields,
            crs={}
        )

        if not api_result.success:
            result = self.creation_result()
            result.error_info = api_result.error_info
            return result
        
        view_object = api_result.id

        view_fields={
            'file_folder' : '0',
            'view_type' : 'container',
            'state' : 'COMPLETE',
            'entity_container' : view_object
        }
        if fields:
            if 'file_folder' in fields:    
                view_fields['file_folder'] = fields['file_folder']

        result = self.create_entity_raw(
            project=project,
            type=self.entity_type.View,
            name=name,
            fields=view_fields,
            crs={}
        )

        return result

    def reprocess_entity(self, id):
        result = self.creation_result()
        result.id = id

        report_entity = self.get_entity(id)
        if report_entity:
            project = report_entity["project"]

            params = {
                'project': project,
                'id' : id
            }

            fields = {
                'state': 'PARTIAL',
                'partial_progress': '0',
                'partial_status': '',
                'proccessing_time': '0'
            }

            #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
            url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
            request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())
            if request.status != 200:
                result.success = False
                result.error_info = f'HTTP Error code {request.status}'
                return result

            apiResult = json.loads(request.data.decode("utf-8"))
            if ('result' not in apiResult) or (apiResult['result'] != 'success'):
                result.success = False
                if 'error_info' in apiResult:
                    result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
                else:    
                    result.error_info = 'error_info not found'
                return result

            params={'project': project, 'org': self.OrgId, 'id': id}
            data={'process':'RUN_REPORT'}
            #entityRequest = self.HTTPSession.post(self.VFAPIURL_EVENT, params=params, headers=self.get_auth_headers(), data=data, proxies=self.proxy)
            url_parameters = f"{self.VFAPIURL_EVENT}?{urllib.parse.urlencode(params)}"               
            request = self.HTTPSession.request(method="POST", url=url_parameters, fields=data, headers=self.get_auth_headers())
            if request.status != 200:
                result.success = False
                result.error_info = f'HTTP Error code {request.status}'
                return result
            apiResult = json.loads(request.data.decode("utf-8"))
            if ('result' not in apiResult) or (apiResult['result'] != 'success'):
                result.success = False
                if 'error_info' in apiResult:
                    result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
                else:    
                    result.error_info = 'error_info not found'
            else:
                result.success = True
        else:
            result.success = False

        return result        

    def create_lambda_python(self, project, type, name, code, fields, files=None):
        result = self.creation_result()
        if fields == None:
            fields = {}

        fields['name'] = name
        fields['type'] = 'FILE'
        fields['file_type'] = 'PROGRAM'
        fields['program_type'] = type
        fields['state'] = 'COMPLETE'

        if code.endswith('.py'):
            fields['code_origin'] = 'PYTHON_FILE'
            fields['code'] = code
        else:
            generatorLambdaCode = code.encode('ascii')
            generatorLambdaCode = base64.b64encode(generatorLambdaCode).decode('ascii')
            fields['code'] = generatorLambdaCode

        fields['project'] = project
        self.add_default_fields(type, fields)
        params={'project': project}
        #entityRequest = requests.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        
        lambda_id = apiResult['id']
        if files:
            for file in files:
                if (not os.path.exists(file)):
                    result.success = False
                    result.error_info = 'File not found: ' + file
                    return result

                attach_files = {'file': open(file, 'rb')}
                apiResult = self.attach_files(project=project, id=lambda_id, files=attach_files)
                if not apiResult.success:
                    result.success = False
                    result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
                    return result
                        
        result.success = True
        result.id = lambda_id
        return result
    
    def create_generator(self, project, program, name, fields, inputs):
        result = self.creation_result()
        if fields == None:
            fields = {}
        fields['name'] = name
        fields['type'] = 'FILE'
        fields['file_type'] = 'VOXGEN'
        fields['program'] = program
        fields['state'] = 'COMPLETE'
        fields['project'] = project
        for input in inputs:
            fields['input_value_' + input] = inputs[input]
            fields['input_filter_' + input] = '0'
            fields['input_type_' + input] = '0'
            fields['input_label_' + input] = '0'
        self.add_default_fields(type, fields)
        params={'project': project}
        #entityRequest = requests.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), json=fields, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, body=json.dumps(fields), headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        result.success = True
        result.id = apiResult['id']
        return result

    def is_processing_complete(self, project, ids):
        result = self.wait_result()
        for id in ids:
            params = {'id': id, 'project': project}
            #entityRequest = self.HTTPSession.get(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers())
            request = self.HTTPSession.request(method="GET", url=self.VFAPIURL_ENTITY, fields=params, headers=self.get_auth_headers())
            if request.status == 200:
                entityJson = json.loads(request.data.decode("utf-8"))
                if not 'state' in entityJson:
                    result.complete = False
                    result.success = False
                    result.error_info = json.dumps(entityJson)
                    break
                if entityJson['state'] == 'PARTIAL':
                    result.complete = False
                    result.success = True
                    break
                if entityJson['state'] == 'COMPLETE':
                    result.complete = True
                    result.success = True
                    if 'processing_time' in entityJson:
                        result.times[id] = entityJson['processing_time']
                    else:    
                        result.times[id] = ''
                if entityJson['state'] == 'ERROR':
                    result.complete = False
                    result.success = False
                    result.error_info = base64.b64decode(entityJson['error_info']).decode('ascii')
                    break
            else:
                result.complete = False
                result.success = False
                result.error_info = 'HTTP Error ' + str(request.status)
                break

        return result

    def delete_entities(self, project, ids):
        result = self.api_result()
        deleteIdentifierList = ''
        for id in ids:
            deleteIdentifierList = deleteIdentifierList + id + ' '
        params = {'project': project, 'org': self.OrgId, 'operation': 'delete'}
        data = {'operation': 'delete', 'items': deleteIdentifierList}
        #entityRequest = self.HTTPSession.post(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers(), data=data, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"               
        request = self.HTTPSession.request(method="POST", url=url_parameters, fields=data, headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = 'Error deleting entities'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        else:    
            result.success = True
        return result
    
    def run_lambda(self, project, lambda_name, inputs):
        result = self.api_result()

        inputs['function'] = lambda_name
        inputs['project'] = project
        params = {'project': project, 'org': self.OrgId, 'program': 'function', 'function' : lambda_name}

        body = json.dumps(inputs)
        
        url_parameters = f"{self.VFAPIURL_ENTITY}?{urllib.parse.urlencode(params)}"   
                   
        request = self.HTTPSession.request(
            method="POST", 
            url=url_parameters,
            headers=self.get_auth_headers(),
            body=body)

        if request.status != 200:
            result.success = False
            result.error_info = 'Error running lambda'
            return result

        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        else:    
            result.success = True
        return result    

    def attach_files(self, project, id, files):
        result = self.api_result()
        params = {'project': project, 'org': self.OrgId, 'id': id}
        #request = self.HTTPSession.post(self.VFAPIURL_FILE, params=params, headers=self.get_auth_headers(), files=files, proxies=self.proxy)
        url_parameters = f"{self.VFAPIURL_FILE}?{urllib.parse.urlencode(params)}"  

        fields={}
        for file in files:
            filename = files[file].name
            name = os.path.basename(filename)
            fields[file] = (name, files[file].read())

        request = self.HTTPSession.request(method="POST", url=url_parameters, fields=fields, headers=self.get_auth_headers())
        if request.status != 200:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
            return result
        apiResult = json.loads(request.data.decode("utf-8"))
        if ('result' not in apiResult) or (apiResult['result'] != 'success'):
            result.success = False
            if 'error_info' in apiResult:
                result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
            else:    
                result.error_info = 'error_info not found'
            return result
        else:    
            result.success = True
        return result

    def get_file(self, project, entity, filename):
        params = {'id': entity, 'project': project, 'org': self.OrgId, 'filename': filename}
        #entityRequest = self.HTTPSession.get(self.VFAPIURL_FILE, params=params, headers=self.get_auth_headers(), proxies=self.proxy)
        request = self.HTTPSession.request(method="GET", url=self.VFAPIURL_FILE, fields=params, headers=self.get_auth_headers())
        if request.status != 200:
            return ''
        return request.data.decode("utf-8")

    def get_binary_file(self, project, entity, filename):
        params = {'id': entity, 'project': project, 'org': self.OrgId, 'filename': filename}
        #entityRequest = self.HTTPSession.get(self.VFAPIURL_FILE, params=params, headers=self.get_auth_headers(), proxies=self.proxy)
        request = self.HTTPSession.request(method="GET", url=self.VFAPIURL_FILE, fields=params, headers=self.get_auth_headers())
        if request.status != 200:
            return None
        return request.data

    def download_file(self, project, entity, filename, destination):
        params = {'id': entity, 'project': project, 'org': self.OrgId, 'filename': filename}
        #entityRequest = self.HTTPSession.get(self.VFAPIURL_FILE, params=params, headers=self.get_auth_headers(), proxies=self.proxy)
        request = self.HTTPSession.request(method="GET", url=self.VFAPIURL_FILE, fields=params, headers=self.get_auth_headers())
        if (request.status) != 200:
            return False
        with open(destination, 'wb') as file:
            file.write(request.data)
        return True

    def get_file_list(self, project, entity):
        params = {'id': entity, 'project': project, 'org': self.OrgId}
        #entityRequest = self.HTTPSession.get(self.VFAPIURL_FILE, params=params, headers=self.get_auth_headers(), proxies=self.proxy)
        request = self.HTTPSession.request(method="GET", url=self.VFAPIURL_FILE, fields=params, headers=self.get_auth_headers())

        list = []
        if request.status == 200:
            text = request.data.decode("utf-8")
            for line in text.split("\n"):
                if not line.strip():
                    continue
                list.append(line.lstrip())        
        return list

    class collection_result(api_result):
        items = None

    def get_collection(self, id):
        result = self.collection_result()
        params = {'project': id}
        #entityRequest = self.HTTPSession.get(self.VFAPIURL_ENTITY, params=params, headers=self.get_auth_headers())
        request = self.HTTPSession.request(method="GET", url=self.VFAPIURL_ENTITY, fields=params, headers=self.get_auth_headers())
        if (request.status == 200):
            entityJson = json.loads(request.data.decode("utf-8"))
            result.items = entityJson
            result.success = True
        else:
            result.success = False
            result.error_info = f'HTTP Error code {request.status}'
        return result

    def compute_region_from_aabbs(self, entity_id):
        entity = self.get_entity(entity_id)
        min_x = float(entity["aabb_min_x"]) - 20
        max_x = float(entity["aabb_max_x"]) + 20
        min_y = float(entity["aabb_min_y"]) - 20
        max_y = float(entity["aabb_max_y"]) + 20
        min_z = float(entity["aabb_min_z"]) - 20
        max_z = float(entity["aabb_max_z"]) + 20
        region = '1'
        region += "," + str(min_z)
        region += "," + str(max_z)
        region += "," + str(min_x)
        region += "," + str(min_y)
        region += "," + str(max_x)
        region += "," + str(min_y)
        region += "," + str(max_x)
        region += "," + str(max_y)
        region += "," + str(min_x)
        region += "," + str(max_y)
        return region
    
    def get_dataframe(self, project_id, entity_id, file_name):
        file = self.get_file(project_id, entity_id, 'report.csv')
        if file:
            content = StringIO(file)
            return pd.read_csv(content)

        return pd.DataFrame()

    def deploy_workflow(self, projects, code_path, code):
        print('Deploying Workflow')

        print(f'Compress code files')
        code_file = os.path.join(code_path, 'code.zip')

        def zipdir(path, ziph):
            for root, dirs, files in os.walk(path):
                if '__pycache__' not in root:
                    for file in files:
                        if file != 'code.zip':
                            p = os.path.relpath(os.path.join(root, file), path)
                            ziph.write(os.path.join(root, file), p)

        with zipfile.ZipFile(code_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(code_path, zipf)

        sys.path.append(code_path)
        run_code_file = os.path.join(code_path, code)

        project_ids = projects.split(',')    

        for project in project_ids:
            print(f'Fetch project entity: {project}')
            project_entity = self.get_entity(project, project)

            if project_entity:
                create_workflow = True
                if 'workflow_id' in project_entity:
                    print(f'Workflow already initialized')
                    print(f'Check if entity exists {project_entity["workflow_id"]}')
                    if self.get_entity(project_entity['workflow_id'], project):
                        print(f'Update entity code')

                        workflow_id = project_entity['workflow_id']
                        create_workflow = False

                        fields = {
                            'code' : code
                        }
                        result = self.update_entity(
                            project=project, 
                            id=workflow_id, 
                            fields=fields)

                        #attach code  
                        workflow_code_file = open(code_file, 'rb')
                        files = {'file': workflow_code_file}
                        result = self.attach_files(
                            project=project,
                            id=workflow_id,
                            files=files)
                        
                        workflow_code_file.close()

                        if not result.success:
                            print('Error uploading workflow code ' + result.error_info)
                            exit()
                    else:
                        print(f'Entity {project_entity["workflow_id"]} does not exist. Check your .env variables')
                        exit()

                if create_workflow:
                    print(f'Create program entity')
                    result = self.create_lambda_python(
                            project=project, 
                            type=voxelfarm.lambda_type.Workflow,
                            name='workflow', 
                            code=code, 
                            fields={
                                'virtual': '1',
                                'background_process' : '1',
                                'file_folder': '0'
                            },
                            files=[code_file])

                    if not result.success:
                        print('Error creating workflow folder.')
                        exit()

                    workflow_id = result.id
                    print(f'Program entity {workflow_id} created')

                    fields = {
                        'workflow_id' : workflow_id
                    }

                    print(f'Saving changes to project {project}...')

                    result = self.update_entity(
                        project=project, 
                        id=project, 
                        fields=fields)

                    if result.success:
                        print('Saved changes to project')
                    else:
                        print(f'Error saving project: {result.error_info}')

                print('Code file uploaded.')

                voxelfarm.voxelfarm_framework = mock_workflow_framework(project, self)

                with open(run_code_file, "r") as python_file:
                    python_code = python_file.read()
                    exec(python_code)
            else:
                print(f'Project {project} not found')        

        print(f'Remove code file {code_file}')
        os.remove(code_file)
        print('Done.')

    def deploy_workflow_project_list(self, projects, code_path, code):
        print('Deploying Workflow')

        print(f'Compress code files')
        code_file = os.path.join(code_path, 'code.zip')

        def zipdir(path, ziph):
            for root, dirs, files in os.walk(path):
                if '__pycache__' not in root:
                    for file in files:
                        if file != 'code.zip':
                            p = os.path.relpath(os.path.join(root, file), path)
                            ziph.write(os.path.join(root, file), p)

        with zipfile.ZipFile(code_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(code_path, zipf)

        sys.path.append(code_path)
        run_code_file = os.path.join(code_path, code)

        for project in projects:
            try:
                print(f'Fetch project entity: {project}')
                project_entity = self.get_entity(project, project)

                if project_entity:
                    create_workflow = True
                    if 'workflow_id' in project_entity:
                        print(f'Workflow already initialized')
                        print(f'Check if entity exists {project_entity["workflow_id"]}')
                        if self.get_entity(project_entity['workflow_id'], project):
                            print(f'Update entity code')

                            workflow_id = project_entity['workflow_id']
                            create_workflow = False

                            fields = {
                                'code' : code
                            }
                            result = self.update_entity(
                                project=project, 
                                id=workflow_id, 
                                fields=fields)

                            #attach code  
                            workflow_code_file = open(code_file, 'rb')
                            files = {'file': workflow_code_file}
                            result = self.attach_files(
                                project=project,
                                id=workflow_id,
                                files=files)
                            
                            workflow_code_file.close()

                            if not result.success:
                                print('Error uploading workflow code ' + result.error_info)
                                exit()
                        else:
                            print(f'Entity {project_entity["workflow_id"]} does not exist. Check your .env variables')
                            exit()

                    if create_workflow:
                        print(f'Create program entity')
                        result = self.create_lambda_python(
                                project=project, 
                                type=voxelfarm.lambda_type.Workflow,
                                name='workflow', 
                                code=code, 
                                fields={
                                    'virtual': '1',
                                    'background_process' : '1',
                                    'file_folder': '0'
                                },
                                files=[code_file])

                        if not result.success:
                            print('Error creating workflow folder.')
                            exit()

                        workflow_id = result.id
                        print(f'Program entity {workflow_id} created')

                        fields = {
                            'workflow_id' : workflow_id
                        }

                        print(f'Saving changes to project {project}...')

                        result = self.update_entity(
                            project=project, 
                            id=project, 
                            fields=fields)

                        if result.success:
                            print('Saved changes to project')
                        else:
                            print(f'Error saving project: {result.error_info}')

                    print('Code file uploaded.')
                    try:
                        voxelfarm.voxelfarm_framework = mock_workflow_framework(project, self)

                        with open(run_code_file, "r") as python_file:
                            python_code = python_file.read()
                            exec(python_code)
                    except Exception as e:
                        print(f'Exception on mock workflow: {e}')
                else:
                    print(f'Project {project} not found')        

            except Exception as e:
                print(f'Exception {e}')        
                
        
        os.remove(code_file)
        print('Done.')

    def workflow_get_product_property(self, project_id, product_id, property, version = 0):
        project = self.get_entity(project_id, project_id)
        if project:
            product_key = 'workflow_folder_' + product_id
            if product_key in project:
                product_folder_id = project[product_key]
                if version > 0:
                    apiResult = self.get_collection(project_id)
                    if apiResult.success:
                        version_name = 'Version ' + str(version)
                        entities = apiResult.items
                        for e in entities:
                            entity = entities[e]
                            if ('file_folder' in entity) and (entity['file_folder'] == product_folder_id) and ('file_type' in entity) and (entity['file_type'] == 'FOLDER'):
                                if entity["name"] == version_name:
                                    extended_prop = 'version_' + property
                                    if extended_prop in entity:
                                        return entity[extended_prop]
                                    break    
                else:
                    product_entity = self.get_entity(product_folder_id, project_id)
                    if product_entity and ('version_active' in product_entity):
                        active_version_id = product_entity['version_active']
                        active_version = self.get_entity(active_version_id, project_id)
                        if active_version:
                            extended_prop = 'version_' + property
                            if extended_prop in active_version:
                                return active_version[extended_prop]
        return None

    def workflow_get_parameter_dataframe(self, project_id, product_id, version = 0):
        attribute_product = self.workflow_get_product_property(project_id, product_id, 'report_entity', version)
        if attribute_product:
            attribute = self.get_file(project_id, attribute_product, 'report.csv')
            if attribute:
                content = StringIO(attribute)
                return pd.read_csv(content)
        return pd.DataFrame()

    def workflow_get_singleton(self, project_id, product_id, singleton_id):
        project_entity = self.get_entity(project_id, project_id)
        if project_entity:
            product_key = 'workflow_folder_' + product_id
            if product_key in project_entity:
                product_id = project_entity[product_key]
                product_entity = self.get_entity(product_id, project_id)
                if product_entity:
                    singleton_key = f'workflow_singleton_{singleton_id}'
                    if singleton_key in product_entity:
                        return product_entity[singleton_key]

        return None

    def workflow_get_entity_id(self, project_id, product_id, alias_id, version = 0):
        project = self.get_entity(project_id, project_id)
        if project:
            product_key = 'workflow_folder_' + product_id
            if product_key in project:
                product_folder_id = project[product_key]
                if version > 0:
                    apiResult = self.get_collection(project_id)
                    if apiResult.success:
                        version_name = 'Version ' + str(version)
                        entities = apiResult.items
                        for e in entities:
                            entity = entities[e]
                            if ('file_folder' in entity) and (entity['file_folder'] == product_folder_id) and ('file_type' in entity) and (entity['file_type'] == 'FOLDER'):
                                if entity["name"] == version_name:
                                    extended_prop = 'alias_' + alias_id
                                    if extended_prop in entity:
                                        return entity[extended_prop]
                                    break    
                else:
                    product_entity = self.get_entity(product_folder_id, project_id)
                    if product_entity and ('version_active' in product_entity):
                        active_version_id = product_entity['version_active']
                        active_version = self.get_entity(active_version_id, project_id)
                        if active_version:
                            extended_prop = 'alias_' + alias_id
                            if extended_prop in active_version:
                                return active_version[extended_prop]
        return None

    def workflow_get_dataframe(self, project_id, product_id, alias_id, file_name = None, version = 0):
        attribute_product = self.workflow_get_entity_id(project_id, product_id, alias_id, version)
        if attribute_product:
            dataframe_file = 'report.csv'
            if file_name:
                dataframe_file = file_name

            split_tup = os.path.splitext(dataframe_file)
            file_extension = split_tup[1].lower()
            if file_extension == '.csv':
                attribute = self.get_file(project_id, attribute_product, dataframe_file)
                if attribute:
                    content = StringIO(attribute)
                    return pd.read_csv(content)
            elif file_extension == '.ftr':
                attribute = self.get_binary_file(project_id, attribute_product, dataframe_file)
                if attribute:
                    content = io.BytesIO(attribute)
                    return pd.read_feather(content)

        return pd.DataFrame()

    def workflow_get_timings(self, project_id):
        entities = []
        collections = self.get_collection(project_id).items
        
        for entity_id in collections:
            entity = collections[entity_id]
            if "processing_start_date" in entity and "file_folder" in entity and entity["file_folder"] in collections:
                file_folder_entity = collections[entity["file_folder"]]
                processing_time = float(entity["processing_time"]) if "processing_time" in entity else 0
                if processing_time > 0 and "version_number" in file_folder_entity:
                    file_date = int(entity["file_date"]) if "file_date" in entity else 0
                    if file_date > 0:
                        processing_start_date = int(entity["processing_start_date"])
                    queue_time = processing_start_date - file_date
                    workflow_time = file_date - int(file_folder_entity["file_date"]) if "file_date" in file_folder_entity and int(file_folder_entity["file_date"]) > 0 else 0
                    entities.append({
                            "id": entity["ID"],
                            "file_folder": entity["file_folder"],
                        "file_date": pd.to_datetime(file_date / 1000, unit='s'),
                        "workflow_name": file_folder_entity["workflow_product"] if "workflow_product" in file_folder_entity else "N/A",
                            "name": entity["name"],
                            "state": entity["state"],
                            "version": int(file_folder_entity["version_number"]),
                        "workflow_time_ms": workflow_time,
                        "processing_time_ms": processing_time,
                        "queue_time_ms": queue_time
                    })

        return pd.DataFrame.from_dict(entities)    

    def get_entity_property(self, project_id, entity_id, property):
        entity = self.get_entity(entity_id, project_id)
        extended_prop = 'property_' + property
        if entity and (extended_prop in entity):
            return entity[extended_prop]

        return None

    def workflow_create_product_version(self, project_id, product_id, inputs = None, files = None):
        project_entity = self.get_entity(project_id, project_id)
        if project_entity:
            # Get the coordinate system of the project
            api_result = self.get_project_crs(project_id)
            if api_result.success:
                crs = api_result.crs
                field_id = f'workflow_folder_{product_id}'
                if ('workflow_id' in project_entity) and (field_id in project_entity):
                    workflow_id = project_entity['workflow_id']
                    product_folder_id = project_entity[field_id]
                    product_entity = self.get_entity(product_folder_id, project_id)
                    if product_entity:
                        # Get new version number for product
                        result_atomic = self.add_value_atomically(project=project_id, id=product_folder_id, property='version_last', value=1)
                        if result_atomic and result_atomic.success:
                            version_number = result_atomic.value

                            now = datetime.now()
                            version_label = now.strftime("%d/%m/%Y %H:%M:%S:%f") 

                            capture_date = ''
                            user = ''
                            comment = ''
                            if inputs and ('capture_date' in inputs):
                                capture_date = inputs['capture_date']
                            else:
                                capture_date = str(int(time.time()))

                            if inputs and ('user' in inputs):
                                user = inputs['user']

                            if inputs and ('comment' in inputs):
                                comment = inputs['comment']
                            
                            api_result = self.create_folder(
                                project=project_id, 
                                folder=product_folder_id,
                                name=f'Version {version_number}',
                                fields={
                                    'workflow_product' : product_id,
                                    'workflow_id' : workflow_id,
                                    'version_label' : version_label,
                                    'version_number' : f'{version_number}',
                                    'capture_date' : capture_date,
                                    'user': user,
                                    'comment': comment
                                })
                            
                            if api_result.success:
                                version_folder_id = api_result.id

                                # Create raw object
                                api_result = self.create_entity_raw(
                                    project=project_id, 
                                    type='RAW', 
                                    name=f'New {product_id}', 
                                    fields={
                                        'file_folder': version_folder_id,
                                        'capture_date' : str(1000 * int(time.time())),
                                        'user': user,
                                        'comment': comment
                                    },
                                    crs=crs)
                                
                                if api_result.success:
                                    entity_id = api_result.id

                                    if files:
                                        for file in files:
                                            files = {'file': open(file, 'rb')}
                                            apiResult = self.attach_files(project=project_id, id=entity_id, files=files)  
                                            if not apiResult.success:
                                                return None

                                    if not inputs:
                                        inputs = {}

                                    inputs['raw_entity_id'] = entity_id
                                    inputs['product_folder_id'] = product_folder_id
                                    inputs['version_folder_id'] = version_folder_id
                                    inputs['project_id'] = project_id
                                    inputs['product_id'] = product_id

                                    apiResult = self.create_workflow_entity(
                                        project=project_id,
                                        name="Workflow Lambda",
                                        fields={
                                            'file_folder' : version_folder_id
                                        },
                                        inputs=inputs)

                                    if apiResult.success:
                                        return apiResult.id

        return None
# region users
    def __set_global_user(self, user_name, level: AccessLevel = AccessLevel.WRITE, last_name = "", description = "", op="" ):

        # Encode username in base64
        user_name_base64 = base64.b64encode(user_name.encode()).decode()
        
        # Common headers
        headers = {
            "accept": "*/*",
            "content-type": "application/json; charset=UTF-8"
        }

        # Add authentication headers if available
        auth_headers = self.get_auth_headers()
        if auth_headers:
            headers.update(auth_headers)

        result = {
            "success": False,
            "errors": [],
            "responses": []
        }

        try:
            body = json.dumps({
                    "project": user_name_base64,
                    "name": user_name_base64,
                    "last_name": base64.b64encode(last_name.encode()).decode(),
                    "description": base64.b64encode(description.encode()).decode(),
                    "type": "USER",
                    "access_level": level.value
                })
            
            request = self.HTTPSession.request(
                method="POST", 
                url=f"{self.VFAPIURL_ENTITY}?id={user_name_base64}&project={user_name_base64}",
                headers=headers,
                body=body)
            
            result["responses"].append(request.status)

            if all(200 <= status < 300 for status in result["responses"]):
                result["success"] = True
            else:
                result["errors"] = [f"Request failed with status {status}" for status in result["responses"]]

        except Exception as e:
            result["errors"].append(str(e))
        
        return result
    
    def add_global_user(self, user_name, level: AccessLevel = AccessLevel.WRITE, last_name = "", description = "" ):
        return self.__set_global_user(user_name, level, last_name, description, "&op=create")

    def update_global_user(self, user_name, level: AccessLevel = AccessLevel.WRITE, last_name = "", description = "" ):
        return self.__set_global_user(user_name, level, last_name, description)


    def add_project_user(self, project_id, user_name, level: AccessLevel = AccessLevel.WRITE):	
        """
        Creates a user in a project using a series of REST requests.
        
        :param project_id: Project ID (GUID)
        :param user_name: Username or email
        :return: Dictionary with creation result
        """
        # Encode username in base64
        user_name_base64 = base64.b64encode(user_name.encode()).decode()
        
        # Common headers
        headers = {
            "accept": "*/*",
            "content-type": "application/json; charset=UTF-8"
        }
        
        # Add authentication headers if available
        auth_headers = self.get_auth_headers()
        if auth_headers:
            headers.update(auth_headers)

        # Prepare results dictionary
        result = {
            "success": False,
            "errors": [],
            "responses": []
        }
        
        try:
            request1 = self.HTTPSession.request(
                method="POST", 
                url=f"{self.VFAPIURL_ENTITY}?id={project_id}:{user_name_base64}&project={project_id}",
                headers=headers,
                body=json.dumps({
                    "project": project_id,
                    "user_ref": user_name_base64,
                    "type": "USER_REF",
                    "access_level": level.value
                })
            )
            result["responses"].append(request1.status)
            
            request2 = self.HTTPSession.request(
                method="POST", 
                url=f"{self.VFAPIURL_ENTITY}?id=users:{project_id}:{user_name_base64}&project=users:{project_id}",
                headers=headers,
                body=json.dumps({
                    "project": f"users:{project_id}",
                    "user_ref": user_name_base64,
                    "type": "USER_REF",
                    "access_level": level.value
                })
            )
            result["responses"].append(request2.status)
            
            request3 = self.HTTPSession.request(
                method="POST", 
                url=f"{self.VFAPIURL_ENTITY}?id={user_name_base64}:{project_id}&project={user_name_base64}",
                headers=headers,
                body=json.dumps({
                    "project": user_name_base64,
                    "project_ref": project_id,
                    "type": "PROJECT_REF",
                    "access_level": level.value
                })
            )

            result["responses"].append(request3.status)
            
            # Check if all requests were successful (status 200-299)
            if all(200 <= status < 300 for status in result["responses"]):
                result["success"] = True
            else:
                result["errors"] = [f"Request failed with status {status}" for status in result["responses"]]
        
        except Exception as e:
            result["errors"].append(str(e))
        
        return result
    
    def update_project_user_level(self, project_id, user_name, level: AccessLevel = AccessLevel.WRITE):
        """
        Removes a user from a project using a series of REST requests.
        
        :param project_id: Project ID (GUID)
        :param user_name: Username or email to remove
        :return: Dictionary with removal result
        """
        # Encode username in base64
        user_name_base64 = base64.b64encode(user_name.encode()).decode()
        
        # Prepare headers
        headers = {
            "accept": "*/*",
            "content-type": "application/json; charset=UTF-8"
        }
        
        # Add authentication headers if available
        auth_headers = self.get_auth_headers()
        if auth_headers:
            headers.update(auth_headers)
        
        # Prepare results dictionary
        result = {
            "success": False,
            "errors": [],
            "responses": []
        }
        
        try:
            request1 = self.HTTPSession.request(
                method="POST", 
                url=f"{self.VFAPIURL_ENTITY}?id={project_id}:{user_name_base64}&project={project_id}",
                headers=headers,
                body=json.dumps({
                    "access_level": "none"
                })
            )
            result["responses"].append(request1.status)
            
            request2 = self.HTTPSession.request(
                method="POST", 
                url=f"{self.VFAPIURL_ENTITY}?id=users:{project_id}:{user_name_base64}&project=users:{project_id}",
                headers=headers,
                body=json.dumps({
                    "access_level": "none"
                })
            )
            result["responses"].append(request2.status)
            
            request3 = self.HTTPSession.request(
                method="POST", 
                url=f"{self.VFAPIURL_ENTITY}?id={user_name_base64}:{project_id}&project={user_name_base64}",
                headers=headers,
                body=json.dumps({
                    "access_level": "none"
                })
            )
            result["responses"].append(request3.status)
            
            if all(200 <= status < 300 for status in result["responses"]):
                result["success"] = True
            else:
                result["errors"] = [f"Request failed with status {status}" for status in result["responses"]]
        
        except Exception as e:
            result["errors"].append(str(e))
        
        return result    

    def remove_project_user(self, project_id, user_name):
        return self.update_project_user_level(project_id, user_name, AccessLevel.NONE)
    
# endregion users


# region AAD_Credentials
    def set_file_credentials(self, filename: str):
        self.aad_credentials = self.get_env_file_as_dict(filename)
        self.token, error = self.get_token()
        if (self.token == None):
            print("credentials file: "+filename )
            raise Exception(f"Check that the credentials are correct, error: {error}")

    def set_credentials(self, tenant: str, client_id: str, client_secret: str):
        self.aad_credentials = {
            "TENANT": tenant,
            "CLIENT_ID": client_id,
            "CLIENT_SECRET":client_secret
        }
        self.token, error = self.get_token()
        if (self.token == None):
            print("Set Credentials failed ClientId : "+ client_id)
            raise Exception(f"Check that the credentials are correct, error: {error}")

    def get_env_file_as_dict(self, path: str) -> dict:
        if not os.path.isfile(path):
            t_path = os.path.dirname(__file__)+ path
            if os.path.isfile(t_path):    
                path = t_path
        with open(path, 'r') as f:
            return dict(tuple(line.replace('\n', '').split('=')) for line 
                        in f.readlines() if not line.startswith('#'))

    def get_token(self, ressource=None):
        if ressource is None:
            ressource = self.aad_credentials["CLIENT_ID"]

        if (self.aad_credentials["TENANT"] != None):
            authority = "https://login.microsoftonline.com/"+self.aad_credentials["TENANT"]+"/oauth2/token"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                "grant_type" : "client_credentials",
                "client_id" : self.aad_credentials["CLIENT_ID"],
                "client_secret": self.aad_credentials["CLIENT_SECRET"],
                "scope" : "https://graph.microsoft.com/.default",
                "resource": ressource,
            }

            #tokenRequest = HTTPSession.post(authority, data=data, headers=headers)
            data = urllib.parse.urlencode(data)
            request = self.HTTPSession.request(method="POST", url=authority, body=data, headers=headers)

            if request.status == 200:
                tokenResult = json.loads(request.data.decode("utf-8"))
                return tokenResult["access_token"], 0
            
        response = {
            "status": request.status if 'status' in request else '',
            "headers": request.headers if 'headers' in request else '',
            "content": request.data.decode('utf-8') if 'data' in request else ''
        }
        return None, response

    def check_ExpiredToken(self, token: str):
        body = token.split(".")[1]
        body += "=" * ((4 - len(body) % 4) % 4) #ugh
        txt = base64.b64decode(body).decode('utf-8')
        jwt = json.loads(txt)
        expire = int(jwt["exp"])
        return (datetime.fromtimestamp(expire)) < (datetime.now()+timedelta(minutes=2))

    def get_auth_headers(self):
        if (self.aad_credentials==None):
            env_token = os.getenv('VF_USER_TOKEN')
            if env_token!=None:
                self.token = env_token

        if (self.token==None):
            return None
        if self.check_ExpiredToken(self.token) and self.aad_credentials!=None:
            self.token, error = self.get_token()    

        return { 'Authorization': f'Bearer {self.token}' }
# endregion AAD_Credentials

# region GetTimeSeriesData
    def get_time_series_data_by_search(self, timespan, projectID, spatialID=None, objectID=None, properties=None, filter=None):
        authorizationToken, error = self.get_token(
            ressource="https://api.timeseries.azure.com")
        searchString = ""
        if spatialID is not None and spatialID != "" and spatialID != "*":
            searchString = searchString + spatialID + ", "
        if objectID is not None and objectID != "" and objectID != "*":
            searchString = searchString + objectID

        if(searchString[len(searchString)-2:] == ", "):
            searchString = searchString[:len(searchString)-2]

        url = (
            "https://"
            + self.get_environment_id(authorizationToken)
            + ".env.timeseries.azure.com/timeseries/instances/search?"
        )
        querystring = {"api-version": self.ts_api_version}

        payload = {"searchString": f"\"{searchString}\"",
                   "instances": {"pageSize": 100}}

        headers = {
            "Authorization": f"Bearer {authorizationToken}",
            "Content-Type": "application/json",
            "cache-control": "no-cache",
        }

        try:
            jsonResponse = requests.request(
                "POST",
                url,
                data=json.dumps(payload),
                headers=headers,
                params=querystring,
            )
            jsonResponse.raise_for_status()
        except requests.exceptions.ConnectTimeout:
            raise Exception("The request to the TSI api timed out.")
        except requests.exceptions.HTTPError:
            raise Exception(
                "The request to the TSI api returned an unsuccessfull status code.")

        response = json.loads(jsonResponse.text)
        if response["instances"]["hits"]:
            result = response["instances"]["hits"]
            processes = []
            with ThreadPoolExecutor(max_workers=100) as executor:
                for i, _ in enumerate(result):
                    processes.append(
                        executor.submit(
                            lambda p: self.get_data_by_id(*p),
                            [
                                result[i]["timeSeriesId"],
                                properties,
                                filter,
                                timespan,
                                authorizationToken,
                            ],
                        )
                    )

                while "continuationToken" in list(response["instances"].keys()):
                    headers["x-ms-continuation"] = response["instances"]["continuationToken"]
                    jsonResponse = requests.request(
                        "POST",
                        url,
                        data=json.dumps(payload),
                        headers=headers,
                        params=querystring,
                    )
                    jsonResponse.raise_for_status()

                    response = json.loads(jsonResponse.text)
                    result = response["instances"]["hits"]
                    for i, _ in enumerate(result):
                        processes.append(
                            executor.submit(
                                lambda p: self.get_data_by_id(*p),
                                [
                                    result[i]["timeSeriesId"],
                                    properties,
                                    filter,
                                    timespan,
                                    authorizationToken,
                                ],
                            )
                        )
            return self.build_dataframe_from_processes(processes, properties)
        else:
            return pd.DataFrame()

    def get_time_series_data_by_ids(self, projectID, timeseriesIDs, timespan):
        authorizationToken, error = self.get_token(
            ressource="https://api.timeseries.azure.com")

        processes = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            for i, id in enumerate(timeseriesIDs):
                processes.append(
                    executor.submit(
                        lambda p: self.get_data_by_id(*p),
                        [
                            [id["spatialID"], id["objectID"]],
                            id["properties"] if "properties" in id else None,
                            id["filter"] if "filter" in id else None,
                            timespan,
                            authorizationToken,
                        ],
                    )
                )

        return self.build_dataframe_from_processes(processes, None)

    def get_environment_id(self, authorizationToken):
        url = "https://api.timeseries.azure.com/environments"

        querystring = {"api-version": self.ts_api_version}

        payload = ""
        headers = {
            "x-ms-client-application-name": self.ts_applicationName,
            "Authorization": f"Bearer {authorizationToken}",
            "Content-Type": "application/json",
            "cache-control": "no-cache",
        }

        try:
            response = requests.request(
                "GET",
                url,
                data=payload,
                headers=headers,
                params=querystring,
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectTimeout:
            raise Exception("The request to the TSI api timed out.")
        except requests.exceptions.HTTPError:
            raise Exception(
                "The request to the TSI api returned an unsuccessfull status code.")

        environments = json.loads(response.text)["environments"]
        environmentId = None
        for environment in environments:
            if environment["displayName"] == self.ts_environmentName:
                environmentId = environment["environmentId"]
                break
        if environmentId == None:
            raise Exception(
                "TSI environment not found. Check the spelling or create an environment in Azure TSI.")

        return environmentId

    def get_data_by_id(
        self,
        timeseries,
        properties,
        filter,
        timespan,
        authorizationToken,
    ):

        url = (
            "https://"
            + self.get_environment_id(authorizationToken)
            + ".env.timeseries.azure.com/timeseries/query?"
        )
        querystring = {"api-version": self.ts_api_version}
        requestType = "getEvents"

        result = {}

        projectedProperties = None
        if(properties != "*" and properties != None and properties != ["*"]):
            projectedProperties = properties
        retry = 0

        payload = {
            requestType: {
                "timeSeriesId": timeseries,
                "searchSpan": {"from": timespan[0], "to": timespan[1]},
                "take": 250000,
                "projectedProperties": projectedProperties,
            }
        }

        if filter is not None and filter != "":
            payload[requestType]["filter"] = {
                "tsx": filter
            }

        headers = {
            "x-ms-client-application-name": self.ts_applicationName,
            "Authorization": f"Bearer {authorizationToken}",
            "Content-Type": "application/json",
            "cache-control": "no-cache",
        }

        while retry < 50:  # Looping with a small random wait if the API returns us problems. This solve an issue where consicutive requests goes beyond TSI max number of concurrent requests.
            try:
                jsonResponse = requests.request(
                    "POST",
                    url,
                    data=json.dumps(payload),
                    headers=headers,
                    params=querystring,
                )
                jsonResponse.raise_for_status()
                break
            except requests.exceptions.HTTPError:
                error = json.loads(jsonResponse.text)
                if(error["error"]["code"] == "TooManyRequests"):
                    # Too many requests at the same time. Waiting for a bit before retrying."
                    time.sleep(random.randint(1, 5))
                    retry += 1
                    continue
                else:
                    raise Exception(
                        "The request to the TSI api returned an unsuccessfull status code.")

        response = json.loads(jsonResponse.text)
        result = response
        result["timeseries"] = timeseries
        retry = 0

        while "continuationToken" in list(response.keys()):
            headers = {
                "x-ms-client-application-name": self.ts_applicationName,
                "Authorization": f"Bearer {authorizationToken}",
                "Content-Type": "application/json",
                "cache-control": "no-cache",
                "x-ms-continuation": response["continuationToken"],
            }
            while retry < 50:
                try:
                    jsonResponse = requests.request(
                        "POST",
                        url,
                        data=json.dumps(payload),
                        headers=headers,
                        params=querystring,
                    )
                    jsonResponse.raise_for_status()
                    break
                except requests.exceptions.HTTPError:
                    error = json.loads(jsonResponse.text)
                    if(error["error"]["code"] == "TooManyRequests"):
                        # Too many requests at the same time. Waiting for a bit before retrying."
                        time.sleep(random.randint(1, 5))
                        retry += 1
                        continue
                    else:
                        raise Exception(
                            "The request to the TSI api returned an unsuccessfull status code.")

            response = json.loads(jsonResponse.text)
            result["timestamps"].extend(response["timestamps"])
            for i, property in enumerate(response["properties"]):
                result["properties"][i]["values"].extend(property["values"])
        retry = 0
        return result

    def build_dataframe_from_processes(self, processes, dTypes):
        if processes is None or len(processes) == 0:
            return pd.DataFrame()

        lambdaData = []
        dfColumns = ["timestamp", "spatialID", "objectID"]
        for task in as_completed(processes):
            result = task.result()
            if "timestamps" in result:
                for i, (timestamp) in enumerate(result["timestamps"]):
                    lambdaData.append({ "timestamp": timestamp,
                                        "spatialID": result["timeseries"][0],
                                        "objectID": result["timeseries"][1],
                                        "properties": []})
                    properties = []
                    for (j, property) in enumerate(result["properties"]):
                        if property["name"] == "spatialId" or property["name"] == "objectId":
                            continue
                        properties.append({
                            "name": property["name"],
                            "value": property["values"][i],
                        })
                        if not property["name"] in dfColumns:
                            dfColumns.append(property["name"])
                    lambdaData[len(lambdaData)-1]["properties"] = properties

        dataframe = pd.DataFrame(columns=dfColumns)
        arDf = []
        for i, (event) in enumerate(lambdaData):
            values = [pd.to_datetime(event["timestamp"]), event["spatialID"], event["objectID"]]
            indexes = ['timestamp', 'spatialID', 'objectID']
            for _, (property) in enumerate(event["properties"]):
                if(property["name"] in indexes):
                    # Received multiple different values for the exact same date and property. Update the value to the latest data we received.
                    values[indexes.index(property["name"])] = property["value"]
                else :
                    values.append(property["value"])
                    indexes.append(property["name"])
            arDf.append(pd.DataFrame([values], columns=indexes))
        dataframe = pd.concat([dataframe, pd.concat(arDf)])

        # Force dtype to what has been requestion in the properties object when calling a search, if any.
        for dtype in enumerate(dTypes):
            name = dtype[1]["name"]
            type = dtype[1]["type"]
            if name in dataframe.columns and type.lower() == 'double':
                dataframe[name] = dataframe[name].astype('float64')
        return dataframe
# endregion GetTimeSeriesData
