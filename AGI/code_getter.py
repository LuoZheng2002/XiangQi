from AGI.struct import AGIObject
from AGI.code_getter_fundamental import get_most_hardcoded_code
from Hardcoded.is_code_dynamic_func import is_code_dynamic_func
from Hardcoded.run_hardcoded_code import run_hardcoded_code
import pickle


def get_hardcoded_code(code_id, cid_of):
    result = get_most_hardcoded_code(code_id, cid_of)
    if result is not None:
        return result
    if code_id == cid_of['func::is_code_dynamic']:
        return is_code_dynamic_func
    if code_id == cid_of['func::run_hardcoded_code']:
        return run_hardcoded_code
    return None


def get_dynamic_code(code_id: int) -> AGIObject:
    target_file = open('Formatted/' + str(code_id) + '.txt', 'rb')
    code = pickle.load(target_file)
    target_file.close()
    return code
