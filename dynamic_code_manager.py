import os
import pickle


class DynamicCode:
    def __init__(self, concept_id, code):
        self.concept_id = concept_id
        self.code = code


class DynamicCodeDatabase:
    def __init__(self, directory: str):
        self.dynamic_codes = list()
        self.directory = directory
        self.dir_list = os.listdir(directory)
        for file_name in self.dir_list:
            if file_name[-4:] == '.txt':
                target_file = open(directory + '/' + file_name, 'rb')
                code = pickle.load(target_file)
                target_file.close()
                self.dynamic_codes.append(DynamicCode(int(file_name[:-4]), code))

    def get_code(self, code_id):
        for dynamic_code in self.dynamic_codes:
            if dynamic_code.concept_id == code_id:
                return dynamic_code.code
        assert False
