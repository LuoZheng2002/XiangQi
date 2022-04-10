from AGI.struct import AGIObject, AGIList
from AGI.objects import obj
from AGI.code_getter_fundamental import is_code_dynamic


# input0: code_id
def is_code_dynamic_func(params: list, cid_of):
    assert type(params[0]) == AGIObject
    code_id = params[0].concept_id
    if is_code_dynamic(code_id, cid_of):
        return obj('True', cid_of)
    return obj('False', cid_of)

