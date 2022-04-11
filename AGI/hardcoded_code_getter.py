from AGI.code_getter_fundamental import get_most_hardcoded_code
from Hardcoded.is_code_dynamic_func import is_code_dynamic_func
from Hardcoded.run_hardcoded_code_func import run_hardcoded_code_func


def get_hardcoded_code(code_id, cid_of):
    result = get_most_hardcoded_code(code_id, cid_of)
    if result is not None:
        return result
    if code_id == cid_of['func::is_code_dynamic']:
        return is_code_dynamic_func
    if code_id == cid_of['func::run_hardcoded_code']:
        return run_hardcoded_code_func
    return None



