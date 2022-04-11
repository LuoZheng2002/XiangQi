import pickle
from AGI.struct import AGIObject


def get_dynamic_code(code_id: int) -> AGIObject:
    target_file = open('Formatted/' + str(code_id) + '.txt', 'rb')
    code = pickle.load(target_file)
    target_file.close()
    return code