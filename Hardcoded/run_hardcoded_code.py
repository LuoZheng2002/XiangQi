from AGI.struct import AGIObject, AGIList
from AGI.code_getter_fundamental import get_most_hardcoded_code
from Hardcoded import is_code_dynamic_func


# input0: code_id, input1: params
def run_hardcoded_code(params: list, cid_of):
    assert type(params[0]) == AGIObject
    code_id = params[0].concept_id
    function_params = params[1]
    if type(function_params) == AGIObject:
        function_params = function_params.agi_list()
    assert type(function_params) == AGIList
    assert get_most_hardcoded_code(code_id, cid_of) is not None or \
           code_id == cid_of['func::run_hardcoded_code'] or \
           code_id == cid_of['func::is_code_dynamic']
    if code_id == cid_of['func::run_hardcoded_code']:
        return run_hardcoded_code(function_params.get_list(), cid_of)
    elif code_id == cid_of['func::is_code_dynamic']:
        return is_code_dynamic_func(function_params.get_list(), cid_of)
    return get_most_hardcoded_code(code_id, cid_of)(function_params.get_list())


