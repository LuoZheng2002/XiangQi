from AGI.struct import AGIObject, AGIList
from AGI.code_getter_fundamental import get_most_hardcoded_code
from Hardcoded import is_code_dynamic_func


# input0: code_id, input1: params
def run_hardcoded_code_func(params: AGIList, cid_of, dir_list):
    assert type(params.get_element(0)) == AGIObject
    code_id = params.get_element(0).concept_id
    function_params = params.get_element(1)
    if type(function_params) == AGIObject:
        function_params = function_params.agi_list()
    assert type(function_params) == AGIList
    assert get_most_hardcoded_code(code_id, cid_of) is not None or \
           code_id == cid_of['func::run_hardcoded_code'] or \
           code_id == cid_of['func::is_code_dynamic']
    if code_id == cid_of['func::run_hardcoded_code']:
        return run_hardcoded_code_func(function_params, cid_of, dir_list)
    if code_id == cid_of['func::is_code_dynamic']:
        return is_code_dynamic_func(function_params, cid_of, dir_list)
    return get_most_hardcoded_code(code_id, cid_of)(function_params, cid_of)


