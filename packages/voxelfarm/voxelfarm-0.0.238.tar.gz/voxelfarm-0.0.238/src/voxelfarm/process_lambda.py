import os
import base64
import time
import voxelfarm
from voxelfarm import voxelfarmclient

class process_lambda_framework:

    def __init__(self):  
        pass

    def input_string(self, id, label, default = ""):
        return ""

    def log(self, message):
        pass

    def progress(self, progress, message):
        pass

    def get_scrap_folder(self):
        return ""

    def get_tools_folder(self):
        return ""

    def get_entity_folder(self, id = None):
        return ""
    
    def query_entity_files(self, query, id = None):
        return ""

    def download_entity_files(self, id = None):
        return ""

    def download_entity_file(self, filename, id = None):
        return ""

    def attach_file(self, filename, id = None):
        return True

    def attach_folder(self, folder, id = None):
        return True

    def remove_file(self, filename, id = None):
        return True

    def upload(self, filename, name, id = None):
        pass

    def set_exit_code(self, code):
        pass

    def get_entity(self, id = None):
        return None

    def get_entity_file_list(self, id = None):
        return []

    def export_file(self, local_file_location, drop_zone_file_location):
        pass

    def update_type(self):
        return None

    def stage_done(self):
        return False

    def get_vf_api(self):
        vf_api = voxelfarmclient.rest('http://localhost')
        return vf_api
    
    def increment_counter(self, counter, offset = 1):
        return 0
    
    def decrement_counter(self, counter, offset = 1):
        return 0

    def set_counter(self, counter, value = 0):
        pass

    def get_working_dir(self):
        return ''

    def swarm_db_upload(self, entity_id, folder, name, title):
        pass

    def get_property(self, property):
        return ''

    def set_property(self, property, value):
        pass

    def cache_entity_file(self, entity_id, file, alias):
        return ""
    
    def get_webex_token(self):
        return ''

class process_lambda_host:

    def __init__(self, framework = None):  
        if framework:
            self.lambda_framework = framework
        else:
            if voxelfarm.voxelfarm_framework:
                self.lambda_framework = voxelfarm.voxelfarm_framework
            else:
                self.lambda_framework = process_lambda_framework()

        self.vf_api = self.lambda_framework.get_vf_api()
        if self.vf_api:
            if type(self.vf_api) == str:
                self.lambda_framework.log(f'vf_api: {self.vf_api}')
                self.vf_api = voxelfarmclient.rest(self.vf_api)
        else:    
            self.vf_api = voxelfarmclient.rest('http://localhost')

        entity = self.lambda_framework.get_entity()
        self.entity_id = entity['ID']
        self.project = entity['project']

        self.lambda_framework.log(f'entity_id: {self.entity_id}')
        self.lambda_framework.log(f'project: {self.project}')

        self.lambda_framework.log('Request project crs')
        apiResult = self.vf_api.get_project_crs(self.project)
        self.crs = None
        if apiResult.success:
            self.lambda_framework.log('crs requested')
            self.crs = apiResult.crs
        else:    
            self.lambda_framework.log(f'crs error: {apiResult.error_info}')

    def input_string(self, id, label, default = ""):
        return self.lambda_framework.input_string(id, label, default)

    def log(self, message):
        self.lambda_framework.log(message)

    def progress(self, progress, message):
        self.lambda_framework.progress(progress, message)

    def get_scrap_folder(self):
        return self.lambda_framework.get_scrap_folder()

    def get_tools_folder(self):
        return self.lambda_framework.get_tools_folder()

    def get_entity_folder(self, id = None):
        return self.lambda_framework.get_entity_folder(id)

    def query_entity_files(self, query, id = None):
        if query:
            return self.lambda_framework.query_entity_files(query, id)
        else:
            return self.lambda_framework.download_entity_files(id)

    def download_entity_files(self, id = None):
        return self.lambda_framework.download_entity_files(id)

    def download_entity_file(self, filename, id = None):
        return self.lambda_framework.download_entity_file(filename, id)

    def attach_file(self, filename, id = None):
        self.lambda_framework.attach_file(filename, id)

    def attach_folder(self, folder, id = None):
        self.lambda_framework.attach_folder(folder, id)

    def remove_file(self, filename, id = None):
        self.lambda_framework.remove_file(filename, id)

    def upload(self, filename, name, id = None):
        self.lambda_framework.Upload(filename, name, id)

    def set_exit_code(self, code):
        self.lambda_framework.set_exit_code(code)

    def get_entity(self, id = None):
        return self.lambda_framework.get_entity(id)

    def get_entity_file_list(self, id = None):
        return self.lambda_framework.get_entity_file_list(id)

    def export_file(self, local_file_location, drop_zone_file_location):
        return self.lambda_framework.export_file(local_file_location, drop_zone_file_location)

    def update_type(self):
        if self.lambda_framework.stage_done():
            return self.lambda_framework.update_type()
        
        return None

    def stage_done(self):
        return self.lambda_framework.stage_done()

    def increment_counter(self, counter, offset = 1):
        return self.lambda_framework.increment_counter(counter, offset)
    
    def decrement_counter(self, counter, offset = 1):
        return self.lambda_framework.decrement_counter(counter, offset)

    def set_counter(self, counter, value = 0):
        self.lambda_framework.set_counter(counter, value)

    def get_entity_property(self, entity_id, property):
        self.lambda_framework.log(f'getting {entity_id} property:{property}...')
        extended_prop = 'property_' + property
        entity = self.vf_api.get_entity(entity_id, self.project)
        if entity and (extended_prop in entity):
            return entity[extended_prop]

        return None
    
    def get_property(self, property):
        return self.lambda_framework.get_property(property)

    def set_property(self, property, value):
        self.lambda_framework.set_property(property, value)

    def get_file_path(self, file):
        if os.path.exists(file):
            return file
        else:
            script_dir = self.lambda_framework.get_working_dir()
            self.lambda_framework.log(f'file is a relative path to {script_dir}')
            file_path = os.path.join(script_dir, file)
            self.lambda_framework.log(f'file_path: {file_path}')

            if os.path.exists(file_path):
                return file_path
    
        return None

    def load_file(self, file):
        file_path = self.get_file_path(file)
        self.lambda_framework.log(f'file_path: {file_path}')

        if os.path.exists(file_path):
            self.lambda_framework.log('open file')
            return open(file_path)
    
        return None

    def get_working_dir(self):
        return self.lambda_framework.get_working_dir()

    def create_view(self, folder, name, view_type, view_lambda, inputs, props):
        self.lambda_framework.log(f'create_view:name:{name}|view_type:{view_type}|view_lambda:{view_lambda}|inputs:{inputs}|props:{props}')

        if view_type == None:
            self.lambda_framework.log(f'load_file: {view_lambda}')
            lambda_file = self.load_file(view_lambda)
            if lambda_file == None:
                return {'success': False, 'error_info': 'Lambda file not found'}

            self.lambda_framework.log('file loaded successfully')

            result = self.vf_api.create_lambda_python(
                project=self.project, 
                type=self.vf_api.lambda_type.View,
                name=name, 
                fields={
                    'file_folder': folder,
                    'virtual': '1'
                },
                code=lambda_file.read())
            
            if not result.success:
                self.lambda_framework.log(f'Error creating lambda: {name}')
                return {'success': False, 'error_info': result.error_info}

            view_type = result.id
            self.lambda_framework.log(f'view_type: {view_type}')

        input_fields = {
                'file_folder' : folder,
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
            
        self.lambda_framework.log('Inputs:')
        for key in inputs:
            input_fields['input_value_' + key] = inputs[key]
            self.lambda_framework.log(f'{key} = {inputs[key]}')

        self.lambda_framework.log('Properties:')
        for key in props:
            input_fields[key] = props[key]
            self.lambda_framework.log(f'{key} = {props[key]}')
            
        self.lambda_framework.log(f'Creating raw entity {name}')
        result = self.vf_api.create_entity_raw(
            project=self.project,
            type=self.vf_api.entity_type.View,
            name=name,
            fields=input_fields,
            crs={}
        )

        if not result.success:
            return {'success': False, 'error_info': result.error_info}
        
        view_object = result.id
        
        self.lambda_framework.log(f'created_view:name:{name}|view_object:{view_object}')

        result = self.vf_api.create_entity_raw(
            project=self.project,
            type=self.vf_api.entity_type.View,
            name=name,
            fields={
                'file_folder' : folder,
                'view_type' : 'container',
                'state' : 'COMPLETE',
                'entity_container' : view_object
            },
            crs={}
        )

        if not result.success:
            return {'success': False, 'error_info': result.error_info}
        
        self.lambda_framework.log(f'create_entity_raw: {result.id}')

        return {'success': True, 'id': result.id, 'error_info': 'None'}

    def create_report(self, folder, name, report_lambda, region, lod, inputs, fields = None, update_type = None):
        report_lambda_id = report_lambda
        if report_lambda.endswith('.py'):
            lambda_file = self.load_file(report_lambda)
            if lambda_file == None:
                return {'success': False, 'error_info': 'Lambda file not found'}

            result = self.vf_api.create_lambda_python(
                project=self.project, 
                type=self.vf_api.lambda_type.Report,
                name=f"Lambda for: {name}", 
                fields={
                    'virtual': '1',
                    'file_folder': folder
                },
                code=lambda_file.read())
            
            if not result.success:
                return {'success': False, 'error_info': result.error_info}
        
            report_lambda_id = result.id

        if fields == None:
            fields = {}

        fields['file_folder'] = folder

        if update_type:
            fields['callback_update_type'] = self.generate_callback(update_type)

        result = self.vf_api.create_report(
            project=self.project, 
            program=report_lambda_id, 
            region=region,
            lod=str(lod),
            name=name, 
            fields=fields,
            inputs=inputs)
        
        if result.success:
            if update_type:
                value = self.increment_counter(f'update_type_{update_type}')
                self.log(f'Increment counter update_type_{update_type} : {value}')
                if value < 1:
                    return {'success': False, 'lambda_id': report_lambda_id, 'error_info': 'Counter does not increment properly'}
        else:
            return {'success': False, 'lambda_id': report_lambda_id, 'error_info': result.error_info}
        
        return {'success': True, 'id': result.id, 'lambda_id': report_lambda_id, 'error_info': 'None'}

    def create_lambda(self, folder, name, type, lambda_code):
        lambda_file = self.load_file(lambda_code)
        if lambda_file == None:
            return {'success': False, 'error_info': 'Lambda file not found'}

        result = self.vf_api.create_lambda_python(
            project=self.project, 
            type=type,
            name=name, 
            fields={
                'file_folder': folder
            },
            code=lambda_file.read())
        
        if not result.success:
            return {'success': False, 'error_info': result.error_info}
        
        report_lambda_id = result.id
        return {'success': True, 'id': report_lambda_id}

    def create_export(self, folder, name, export_lambda, region, lod, inputs, fields = None, update_type = None):
        lambda_file = self.load_file(export_lambda)
        if lambda_file == None:
            return {'success': False, 'error_info': 'Lambda file not found'}

        result = self.vf_api.create_lambda_python(
            project=self.project, 
            type=self.vf_api.lambda_type.Report,
            name="Export Lambda for " + name, 
            fields={
                'virtual': '1',
                'file_folder': folder
            },
            code=lambda_file.read())
        if not result.success:
            return {'success': False, 'error_info': result.error_info}
        report_lambda_id = result.id

        if fields == None:
            fields = {}

        fields['file_folder'] = folder
        fields['export_type'] = 'mesh'

        if update_type:
            fields['callback_update_type'] = self.generate_callback(update_type)

        result = self.vf_api.create_export(
            project=self.project, 
            program=report_lambda_id, 
            region=region,
            lod=str(lod),
            name=name, 
            fields=fields,
            inputs=inputs)

        if result.success:
            if update_type:
                value = self.increment_counter(f'update_type_{update_type}')
                self.log(f'Increment counter update_type_{update_type} : {value}')
                if value < 1:
                    return {'success': False, 'lambda_id': report_lambda_id, 'error_info': 'Counter does not increment properly'}
        else:
            return {'success': False, 'lambda_id': report_lambda_id, 'error_info': result.error_info}

        return {'success': True, 'id': result.id, 'lambda_id': report_lambda_id, 'error_info': 'None'}

    def upload_db(self, entity_id, folder, name, title):
        return self.lambda_framework.upload_db(entity_id, folder, name, title)

    def process_entity(self, folder, type, name, fields = None, update_type = None):

        if fields == None:
            fields = {}

        fields['file_folder'] = folder

        if update_type:
            fields['callback_update_type'] = self.generate_callback(update_type)

        result = self.vf_api.create_entity_processed(
            project=self.project, 
            type=type, 
            name=name, 
            fields=fields, 
            crs=self.crs, 
            callback=None)
        
        if update_type and result.success:
            value = self.increment_counter(f'update_type_{update_type}')
            self.log(f'Increment counter update_type_{update_type} : {value}')
            if value < 1:
                result.success = False
                result.error_info = 'Counter does not increment properly'

        return result     

    def process_lambda(self, folder, name, inputs, code, files, fields = None, update_type = None):
        verified_files = []
        if files:
            for file in files:
                verified_files.append(self.get_file_path(file))

        if fields == None:
            fields = {}

        fields['file_folder'] = folder

        if update_type:
            fields['callback_update_type'] = self.generate_callback(update_type)

        result = self.vf_api.create_process_entity(
            project=self.project, 
            name=name, 
            fields=fields, 
            inputs=inputs,
            code=code,
            files=verified_files, 
            callback=None)
        
        if update_type and result.success:
            value = self.increment_counter(f'update_type_{update_type}')
            self.log(f'Increment counter update_type_{update_type} : {value}')
            if value < 1:
                result.success = False
                result.error_info = 'Counter does not increment properly'

        return result     

    def create_entity_raw(self, type, name, fields, files = None):
        result = self.vf_api.create_entity_raw(self.project, type, name, fields, self.crs)
        if result.success:
            # Attach files to the entity
            if files:
                for file in files:
                    if (not os.path.exists(file)):
                        result.success = False
                        result.error_info = 'File not found: ' + file
                        return result

                    attach_files = {'file': open(file, 'rb')}
                    apiResult = self.vf_api.attach_files(project=self.project, id=result.id, files=attach_files)
                    if not apiResult.success:
                        result.success = False
                        result.error_info = base64.b64decode(apiResult['error_info']).decode('ascii')
                    
        return result

    def set_lambda_definition(self, on_init, on_stage_done):
        update_type = self.lambda_framework.update_type()
        if update_type:
            if on_stage_done:
                self.lambda_framework.log(f'update_type: {update_type}')
                result = on_stage_done(self.vf_api, self, update_type)
                if result:
                    if 'success' in result and result['success']:
                        if 'complete' in result and result['complete']:
                            self.lambda_framework.log('on_stage_done complete')
                            self.lambda_framework.set_exit_code(0)
                        else:
                            self.lambda_framework.log('on_stage_done success')
                            self.lambda_framework.set_exit_code(-1)
                    else:    
                        if 'error_info' in result:
                            self.lambda_framework.log('on_init Error: ' + result['error_info'])
                        else:    
                            self.lambda_framework.log('on_init Error')
                        self.lambda_framework.set_exit_code(1)
                else:
                    self.lambda_framework.log('on_stage_done result not found')
                    self.lambda_framework.set_exit_code(1)
            else:
                self.lambda_framework.log('on_stage_done not found')
                self.lambda_framework.set_exit_code(0)
        else:
            if on_init:
                result = on_init(self.vf_api, self)
                if result:
                    if 'success' in result and result['success']:
                        if 'complete' in result and result['complete']:
                            self.lambda_framework.log('on_init complete')
                            self.lambda_framework.set_exit_code(0)
                        else:
                            self.lambda_framework.log('on_init success')
                            self.lambda_framework.set_exit_code(-1)
                    else:
                        if 'error_info' in result:
                            self.lambda_framework.log('on_init Error: ' + result['error_info'])
                        else:    
                            self.lambda_framework.log('on_init Error')
                        self.lambda_framework.set_exit_code(1)
                else:
                    self.lambda_framework.log('on_init result not found')
                    self.lambda_framework.set_exit_code(1)
            else:
                self.lambda_framework.log('on_init not found')
                self.lambda_framework.set_exit_code(0)

    def generate_callback(self, update_type):
        return self.entity_id + "/" + update_type

    def cache_entity_file(self, entity_id, file, alias):
        return self.lambda_framework.cache_file_load(entity_id, file, alias)

    def get_webex_token(self):
        return self.lambda_framework.get_webex_token()
