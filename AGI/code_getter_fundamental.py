from Hardcoded import unclassified
from AGI.struct import AGIObject
from Exception.dynamic_code_exception import ExpressionException
from Hardcoded import code_simulator
import os


def get_most_hardcoded_code(code_id, cid_of):
    hardcoded_code_dict = {
        cid_of['func::compare_concepts']: unclassified.compare_concepts,
        cid_of['func::logic_and']: unclassified.logic_and,
        cid_of['func::logic_or']: unclassified.logic_or,
        cid_of['func::logic_not']: unclassified.logic_not,
        cid_of['func::is_natural_number_single_digit']: unclassified.is_natural_number_single_digit,
        cid_of['func::compare_single_digit_natural_numbers']: unclassified.compare_single_digit_natural_numbers,
        cid_of['func::sum']: unclassified.sum_func,
        cid_of['func::difference']: unclassified.difference_func,
        cid_of['func::get_object_member']: unclassified.get_object_member_func,
        cid_of['func::set_object_member']: unclassified.set_object_member_func,
        cid_of['func::remove_element_by_index']: unclassified.remove_element_by_index,
        cid_of['func::get_input_object']: unclassified.get_input_object,
        cid_of['func::create_concept_instance']: unclassified.create_concept_instance_func,
        cid_of['func::get_dynamic_code_object']: code_simulator.get_dynamic_code_object,
        cid_of['func::remove_element_by_index']: code_simulator.remove_element_by_index,
    }
    if code_id in hardcoded_code_dict:
        return hardcoded_code_dict[code_id]
    return None


def is_code_dynamic(code_id: int, dcd, cid_of) -> bool:
    assert dcd.dir_list
    dynamic = str(code_id) + '.txt' in dcd.dir_list
    hardcoded = get_most_hardcoded_code(code_id, cid_of) is not None or \
        code_id == cid_of['func::is_code_dynamic'] or \
        code_id == cid_of['func::run_hardcoded_code']
    assert not (dynamic and hardcoded)
    if not (dynamic or hardcoded):
        print(code_id)
        raise ExpressionException('A code\'s id is not in either dynamic or hardcoded.')
    if dynamic:
        return True
    return False
