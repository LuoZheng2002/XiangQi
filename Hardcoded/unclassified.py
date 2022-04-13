from AGI.struct import AGIObject, AGIList
from Exception.agi_exception import AGIException
from AGI.objects import obj, num_obj, to_integer
from AGI.concept_instance_creator import create_concept_instance
from Exception.hardcoded_code_exception import HardcodedCodeException
from dynamic_simulator_inputs import dynamic_simulator_inputs


def compare_concepts(params: AGIList, cid_of) -> AGIObject:
    if params.size() != 2:
        raise AGIException('Function should receive 2 params.')
    param1 = params.get_element(0)
    param2 = params.get_element(1)
    if not ((type(param1) == AGIObject or type(param1) == AGIList) and
            (type(param2) == AGIObject or type(param2) == AGIList)):
        raise HardcodedCodeException('Parameters should be AGIObjects.', 'func::compare_concepts')
    if type(param1) == AGIList or type(param2) == AGIList:
        return AGIObject(cid_of['False'], dict())
    if param1.concept_id == param2.concept_id:
        return AGIObject(cid_of['True'], dict())
    else:
        return AGIObject(cid_of['False'], dict())


def logic_and(params: AGIList, cid_of) -> AGIObject:
    if params.size() != 2:
        raise AGIException('logic_and function should receive 2 params.')
    param1 = params.get_element(0)
    param2 = params.get_element(1)
    if type(param1) != AGIObject or type(param2) != AGIObject:
        raise AGIException('Parameters should be AGIObjects.')
    if (param1.concept_id != cid_of['True'] and param1.concept_id != cid_of['False'] and param1.concept_id != cid_of[
        'Fail']) or \
            (param2.concept_id != cid_of['True'] and param2.concept_id != cid_of['False'] and param2.concept_id !=
             cid_of['Fail']):
        raise HardcodedCodeException('Invalid parameters in logic_and function.', 'func::logic_and')
    if param1.concept_id == cid_of['False'] or param2.concept_id == cid_of['False']:
        return AGIObject(cid_of['False'], dict())
    elif param1.concept_id == cid_of['Fail'] or param2.concept_id == cid_of['Fail']:
        return AGIObject(cid_of['Fail'], dict())
    else:
        return AGIObject(cid_of['True'], dict())


def logic_or(params: AGIList, cid_of) -> AGIObject:
    if params.size() != 2:
        raise AGIException('logic_and function should receive 2 params.')
    param1 = params.get_element(0)
    param2 = params.get_element(1)
    if type(param1) != AGIObject or type(param2) != AGIObject:
        raise AGIException('Parameters should be AGIObjects.')
    if (param1.concept_id != cid_of['True'] and param1.concept_id != cid_of['False'] and param1.concept_id != cid_of[
        'Fail']) or \
            (param2.concept_id != cid_of['True'] and param2.concept_id != cid_of['False'] and param2.concept_id !=
             cid_of['Fail']):
        raise AGIException('Invalid parameters in logic_and function.')
    if param1.concept_id == cid_of['True'] or param2.concept_id == cid_of['True']:
        return AGIObject(cid_of['True'], dict())
    elif param1.concept_id == cid_of['Fail'] or param2.concept_id == cid_of['Fail']:
        return AGIObject(cid_of['Fail'], dict())
    else:
        return AGIObject(cid_of['False'], dict())


def logic_not(params: AGIList, cid_of) -> AGIObject:
    if params.size() != 1:
        raise AGIException('logic_not function should receive 1 param.')
    param = params.get_element(0)
    if type(param) != AGIObject:
        print(param)
        raise AGIException('Parameters should be AGIObjects.')
    if param.concept_id != cid_of['True'] and param.concept_id != cid_of['False']\
            and param.concept_id != cid_of['Fail']:
        raise AGIException('Invalid parameter in logic_not function.')
    if param.concept_id == cid_of['Fail']:
        return AGIObject(cid_of['Fail'], dict())
    elif param.concept_id == cid_of['True']:
        return AGIObject(cid_of['False'], dict())
    else:
        return AGIObject(cid_of['True'], dict())


def is_natural_number_single_digit(params: AGIList, cid_of) -> AGIObject:
    if params.size() != 1:
        raise AGIException('This function should receive 1 param.')
    param = params.get_element(0)
    if type(param) != AGIObject:
        raise AGIException('Parameters should be AGIObjects.')
    if param.concept_id == cid_of['Fail']:
        return obj('Fail', cid_of)
    if param.concept_id != cid_of['natural_number']:
        raise HardcodedCodeException('Parameter should be natural number.', 'func::is_natural_number_single_digit')
    if param.attributes[cid_of['content']].size() == 1:
        return AGIObject(cid_of['True'], dict())
    else:
        return AGIObject(cid_of['False'], dict())


# 参数：两个一位自然数
def compare_single_digit_natural_numbers(params: AGIList, cid_of) -> AGIObject:
    if params.size() != 2:
        raise AGIException('This function should receive 2 params.')
    param1 = params.get_element(0)
    param2 = params.get_element(1)
    if type(param1) != AGIObject or type(param2) != AGIObject:
        raise AGIException('Parameters should be AGIObjects.')
    if param1.concept_id == cid_of['Fail'] or param2.concept_id == cid_of['Fail']:
        return obj('Fail', cid_of)
    if param1.concept_id != cid_of['natural_number'] or param2.concept_id != cid_of['natural_number']:
        raise AGIException('Parameters should be natural numbers.')
    if param1.attributes[cid_of['content']].size() != 1 or param2.attributes[cid_of['content']].size() != 1:
        raise AGIException('Parameters should be single-digit.')
    digits = [None, None]
    digits[0] = param1.attributes[cid_of['content']].get_element(0)
    digits[1] = param2.attributes[cid_of['content']].get_element(0)
    integers = [None, None]
    for i in range(2):
        if digits[i].concept_id == cid_of['0']:
            integers[i] = 0
        elif digits[i].concept_id == cid_of['1']:
            integers[i] = 1
        elif digits[i].concept_id == cid_of['2']:
            integers[i] = 2
        elif digits[i].concept_id == cid_of['3']:
            integers[i] = 3
        elif digits[i].concept_id == cid_of['4']:
            integers[i] = 4
        elif digits[i].concept_id == cid_of['5']:
            integers[i] = 5
        elif digits[i].concept_id == cid_of['6']:
            integers[i] = 6
        elif digits[i].concept_id == cid_of['7']:
            integers[i] = 7
        elif digits[i].concept_id == cid_of['8']:
            integers[i] = 8
        elif digits[i].concept_id == cid_of['9']:
            integers[i] = 9
        else:
            raise AGIException('Unexpected element as digit.')
    if integers[0] < integers[1]:
        return AGIObject(cid_of['less_than'], dict())
    elif integers[0] == integers[1]:
        return AGIObject(cid_of['math_equal'], dict())
    else:
        return AGIObject(cid_of['greater_than'], dict())


def sum_func(params: AGIList, cid_of) -> AGIObject:
    if params.size() != 2:
        raise AGIException('This function should receive 2 params.')
    param1 = params.get_element(0)
    param2 = params.get_element(1)
    if type(param1) != AGIObject or type(param2) != AGIObject:
        raise AGIException('Parameters should be AGIObjects.')
    if param1.concept_id == cid_of['Fail'] or param2.concept_id == cid_of['Fail']:
        return obj('Fail', cid_of)
    if param1.concept_id != cid_of['natural_number'] or param2.concept_id != cid_of['natural_number']:
        raise AGIException('Parameters should be natural numbers.')
    number1 = to_integer(param1, cid_of)
    number2 = to_integer(param2, cid_of)
    return num_obj(number1 + number2, cid_of)


def difference_func(params: AGIList, cid_of) -> AGIObject:
    if params.size() != 2:
        raise AGIException('This function should receive 2 params.')
    param1 = params.get_element(0)
    param2 = params.get_element(1)
    if type(param1) != AGIObject or type(param2) != AGIObject:
        raise AGIException('Parameters should be AGIObjects.')
    if param1.concept_id == cid_of['Fail'] or param2.concept_id == cid_of['Fail']:
        return obj('Fail', cid_of)
    if param1.concept_id != cid_of['natural_number'] or param2.concept_id != cid_of['natural_number']:
        raise AGIException('Parameters should be natural numbers.')
    number1 = to_integer(param1, cid_of)
    number2 = to_integer(param2, cid_of)
    if number1 - number2 < 0:
        return obj('Fail', cid_of)
    return num_obj(number1 - number2, cid_of)


# params.get_element(0): object, params.get_element(1): member object
def get_object_member_func(params: AGIList, cid_of) -> AGIObject:
    target_object = params.get_element(0)
    member_object = params.get_element(1)
    assert type(target_object) == AGIObject and type(member_object) == AGIObject
    if not member_object.concept_id in target_object.attributes.keys():
        raise HardcodedCodeException('Can not find target object\'s member!', 'func::get_object_member')
    return target_object.attributes[member_object.concept_id]


# params.get_element(0): object, params.get_element(1): member object, params[2]: value
def set_object_member_func(params: AGIList, cid_of):
    target_object = params.get_element(0)
    member_object = params.get_element(1)
    value = params.get_element(2)
    assert type(target_object) == AGIObject and type(member_object) == AGIObject
    assert member_object.concept_id in target_object.attributes.keys()
    target_object.attributes[member_object.concept_id] = value


#
def remove_element_by_index(params: AGIList, cid_of):
    target_list = params.get_element(0)
    index = params.get_element(1)
    if type(target_list) == AGIObject:
        target_list = target_list.agi_list()
    assert type(target_list) == AGIList
    if target_list.size() == 0:
        raise AGIException('empty list', special_name='index', special_str=str(to_integer(index, cid_of)))
    target_list.remove(to_integer(index, cid_of))


def get_input_object(params: AGIList, cid_of):
    if dynamic_simulator_inputs:
        print('Obtained an input from cache!')
        input_object = num_obj(dynamic_simulator_inputs.pop(0), cid_of)
    else:
        input_object = num_obj(int(input('Dynamic code simulator asks you to input one param.\n')), cid_of)
    return input_object


def create_concept_instance_func(params: AGIList, cid_of):
    assert type(params.get_element(0)) == AGIObject
    concept_id = params.get_element(0).concept_id
    return create_concept_instance(concept_id, cid_of)
