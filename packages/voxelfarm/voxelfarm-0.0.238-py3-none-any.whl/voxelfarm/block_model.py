import voxelfarm
import os
import os.path
import pandas as pd

class block_model_framework:

    def __init__(self):  
        pass

    def input_string(self, id, label, default = ""):
        return ""

    def log(self, message):
        pass

    def download_entity_file(self, filename, id = None):
        return ""

    def attach_file(self, filename, id = None):
        pass

    def get_entity_folder(self, id = None):
        return ""

    def get_entity_file_list(self, id = None):
        return []

class block_model_host:

    def __init__(self, framework = None, entity = None, file = None):    
        if framework:
            self.lambda_framework = framework
        else:
            if voxelfarm.voxelfarm_framework:
                self.lambda_framework = voxelfarm.voxelfarm_framework
            else:
                self.lambda_framework = block_model_framework()

        self.df_blockmodel = None
        self.modified_attributes = []
        self.modified_gm = False

        if entity and file:
            self.blockmodel_entity = entity
            self.blockmodel_name = file
        else:
            self.blockmodel_entity = self.lambda_framework.input_string('bm_entity', 'Block Model Entity', '')
            self.lambda_framework.log('Block Model entity: ' + self.blockmodel_entity)
            self.blockmodel_name = self.lambda_framework.input_string('bm_file', 'Block Model File', '')
            self.lambda_framework.log('Block Model name: ' + self.blockmodel_name)

        gm_file = self.lambda_framework.download_entity_file(self.blockmodel_name, self.blockmodel_entity)
        self.lambda_framework.log('Block Model file: ' + gm_file)
        if os.path.isfile(gm_file):
            self.df_blockmodel = pd.read_feather(gm_file)
        else:
            self.df_blockmodel = pd.DataFrame()

    def get_geological_model(self):
        return self.lambda_framework.download_entity_file(self.blockmodel_name, self.blockmodel_entity)

    def get_file_model(self, attribute):
        if attribute in self.df_blockmodel.columns:
            return self.get_geological_model()
        else:
            return self.lambda_framework.download_entity_file(attribute + ".ftr", self.blockmodel_entity)

    def get_geological_model_name(self):
        return self.blockmodel_name

    def get_pandas(self, vars = None):
        df_model = self.df_blockmodel.copy()
        valid = True
        if vars:
            attributes = []
            for attribute in vars:
                if not attribute in attributes:
                    attributes.append(attribute)
                    if not attribute in df_model:
                        attribute_file = self.lambda_framework.download_entity_file(attribute + ".ftr", self.blockmodel_entity)
                        if os.path.isfile(attribute_file):
                            df_attribute = pd.read_feather(attribute_file)
                            df_model = pd.concat([df_model, df_attribute], axis=1)
                        else:
                            self.lambda_framework.log('Block Model attribute file ' + attribute + ' not found')
                            valid = False

            if valid:
                df_model = df_model[attributes]
            else:
                return pd.DataFrame()
            
        return df_model                

    def put_pandas(self, df_model, vars = None):
        entity_folder = self.lambda_framework.get_entity_folder(self.blockmodel_entity)
        if not os.path.exists(entity_folder):
            os.mkdir(entity_folder)

        update_gm = False
        if vars:
            for attribute in vars:
                if attribute in df_model:
                    if attribute in self.df_blockmodel:
                        update_gm = True
                    else:
                        df_attribute = df_model[[attribute]]

                        previous_attribute_file = self.get_file_model(attribute)
                        if os.path.isfile(previous_attribute_file):
                            df_previous_attribute = pd.read_feather(previous_attribute_file)
                            if len(df_attribute) != len(df_previous_attribute):
                                df_previous_attribute.update(df_attribute)
                                df_attribute = df_previous_attribute
                        elif len(df_attribute) != len(self.df_blockmodel):
                            df_model = self.df_blockmodel.copy()
                            df_model[attribute] = -999
                            df_model = df_model[[attribute]]
                            df_model.update(df_attribute)
                            df_attribute = df_model

                        attribute_file = os.path.join(entity_folder, attribute + ".ftr")
                        df_attribute.to_feather(attribute_file)
                        if attribute_file not in self.modified_attributes:
                            self.modified_attributes.append(attribute_file)
        else:
            if self.df_blockmodel.empty:
                self.df_blockmodel = df_model.copy()
                self.modified_gm = True
            else:
                update_gm = True

        if update_gm:
            self.modified_gm = True
            self.df_blockmodel.update(df_model)

    def field_list(self):
        fields = []
        bm_files = self.lambda_framework.get_entity_file_list(self.blockmodel_entity)

        for col in self.df_blockmodel.columns:
            fields.append(col)

        for file in bm_files:
            if (file != self.blockmodel_name) and file.endswith(".ftr"):
                file_name = os.path.basename(file).split('.')[0]
                fields.append(file_name)

        return fields      

    def write_tag(self, tag):
        entity_folder = self.lambda_framework.get_entity_folder(self.blockmodel_entity)
        tag_file_path = os.path.join(entity_folder, tag + '.tag')

        if tag_file_path not in self.modified_attributes:
            tag_file = open(tag_file_path, "w")
            tag_file.write('1')
            tag_file.close()
            self.modified_attributes.append(tag_file_path)

    def read_tag(self, tag):
        tag_file = self.lambda_framework.download_entity_file(tag + '.tag', self.blockmodel_entity)
        return os.path.isfile(tag_file)

    def close(self):
        if self.modified_gm:
            entity_folder = self.lambda_framework.get_entity_folder(self.blockmodel_entity)
            if not os.path.exists(entity_folder):
                os.mkdir(entity_folder)

            gm_file = os.path.join(entity_folder, self.blockmodel_name)
            self.df_blockmodel.to_feather(gm_file)
            self.lambda_framework.attach_file(gm_file, self.blockmodel_entity)

        for attribute in self.modified_attributes:
            self.lambda_framework.attach_file(attribute, self.blockmodel_entity)

        self.modified_attributes.clear()   
        self.modified_gm = False         

