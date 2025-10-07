import voxelfarm
from voxelfarm import voxelfarmclient

class function_lambda_framework:

    def __init__(self):  
        pass

    def input_string(self, id, label, default = ""):
        return ""

    def get_scrap_folder(self):
        return ""

    def get_working_folder(self):
        return ""

    def download_entity_files(self, id):
        return ""

    def download_entity_file(self, filename, id):
        return ""

    def attach_file(self, filename, id):
        return True

    def remove_file(self, filename, id):
        return True

    def set_exit_code(self, code):
        pass

    def get_entity(self, id):
        return None

    def get_entity_file_list(self, id):
        return []

    def get_product_property(self, product, property):
        return ""
    
    def get_product_alias(self, product, alias):
        return ""
    
    def get_product_singleton(self, product, singleton):
        return ""

    def log(self, message):
        pass

    def get_property(self, property):
        return ''

    def set_property(self, property, value):
        pass

class function_lambda_host:

    def __init__(self, framework = None):  
        if framework:
            self.lambda_framework = framework
        else:
            if voxelfarm.voxelfarm_framework:
                self.lambda_framework = voxelfarm.voxelfarm_framework
            else:
                self.lambda_framework = function_lambda_framework()

        self.project = self.lambda_framework.input_string('project', 'Project Id', '')
        self.function = self.lambda_framework.input_string('function', 'Function Name', '')

    def input_string(self, id, label, default = ""):
        return self.lambda_framework.input_string(id, label, default)

    def get_scrap_folder(self):
        return self.lambda_framework.get_scrap_folder()

    def get_working_folder(self):
        return self.lambda_framework.get_working_folder()

    def download_entity_files(self, id):
        return self.lambda_framework.download_entity_files(id)

    def download_entity_file(self, filename, id):
        return self.lambda_framework.download_entity_file(filename, id)

    def attach_file(self, filename, id):
        self.lambda_framework.attach_file(filename, id)

    def remove_file(self, filename, id):
        self.lambda_framework.remove_file(filename, id)

    def set_exit_code(self, code):
        self.lambda_framework.set_exit_code(code)

    def get_entity(self, id):
        return self.lambda_framework.get_entity(id)

    def get_entity_file_list(self, id):
        return self.lambda_framework.get_entity_file_list(id)

    def get_product_property(self, product, property):
        return self.lambda_framework.get_product_property(product, property)

    def get_product_alias(self, product, alias):
        return self.lambda_framework.get_product_alias(product, alias)

    def get_product_singleton(self, product, singleton):
        return self.lambda_framework.get_product_singleton(product, singleton)

    def log(self, message):
        self.lambda_framework.log(message)

    def get_property(self, property):
        return self.lambda_framework.get_property(property)

    def set_property(self, property, value):
        self.lambda_framework.set_property(property, value)

