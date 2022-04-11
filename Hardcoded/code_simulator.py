from AGI.struct import AGIObject, AGIList
from Exception.hardcoded_code_exception import HardcodedCodeException
from AGI.objects import obj, num_obj, to_integer


def get_dynamic_code_object(params: AGIList, cid_of, dcd):
    code_id = params.get_element(0).concept_id
    return dcd.get_code(code_id)


def remove_element_by_index(params: AGIList, cid_of):
    target_list = params.get_element(0)
    index = params.get_element(1)
    if type(target_list) == AGIObject:
        target_list = target_list.agi_list()
    assert type(target_list) == AGIList
    if target_list.size() == 0:
        raise HardcodedCodeException('empty list', 'func::remove_element_by_index')
    target_list.remove(to_integer(index, cid_of))
