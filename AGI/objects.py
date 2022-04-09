from AGI.struct import AGIObject, AGIList
from AGI.concept_ids import cid_of
from AGI.concept_instance_creator import create_concept_instance
from Exception.agi_exception import AGIException

def num_obj(number: int) -> AGIObject:
    number_str = str(number)
    object_list = []
    for digit in number_str:
        object_list.append(AGIObject(cid_of[digit], dict()))
    return AGIObject(cid_of['natural_number'], {cid_of['content']: AGIList(object_list)})


def obj(concept: int or str) -> AGIObject:
    if type(concept) == int:
        return create_concept_instance(concept)
    if type(concept) == str:
        return create_concept_instance(cid_of[concept])
    assert False


def to_integer(natural_number: AGIObject) -> int:
    if type(natural_number) != AGIObject:
        raise AGIException('Expect AGIObject', special_name='type', special_str=str(type(natural_number)))
    if natural_number.concept_id != cid_of['natural_number']:
        raise AGIException('Expect natural number')
    integer_str = str()
    for i in range(natural_number.attributes[cid_of['content']].size()):
        digit_obj = natural_number.attributes[cid_of['content']].get_element(i)
        digit_id = digit_obj.concept_id
        if digit_id == cid_of['0']:
            integer_str += '0'
        elif digit_id == cid_of['1']:
            integer_str += '1'
        elif digit_id == cid_of['2']:
            integer_str += '2'
        elif digit_id == cid_of['3']:
            integer_str += '3'
        elif digit_id == cid_of['4']:
            integer_str += '4'
        elif digit_id == cid_of['5']:
            integer_str += '5'
        elif digit_id == cid_of['6']:
            integer_str += '6'
        elif digit_id == cid_of['7']:
            integer_str += '7'
        elif digit_id == cid_of['8']:
            integer_str += '8'
        elif digit_id == cid_of['9']:
            integer_str += '9'
        else:
            raise AGIException('Unexpected thing as digit.', special_name='thing', special_str=str(cid_reverse[digit_id]))
    return int(integer_str)