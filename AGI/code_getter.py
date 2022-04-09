from AGI.struct import AGIObject, AGIList
from AGI.concept_ids import cid_of, cid_reverse
import pickle
import os
hardcoded_code_dict = {
    cid_of['func::sum']: None
}


def is_code_dynamic(code_id: int) -> bool:
    dynamic = str(code_id) + '.txt' in os.listdir('../Formatted')
    hardcoded = code_id in hardcoded_code_dict
    assert not (dynamic and hardcoded)
    assert dynamic or hardcoded
    if dynamic:
        return True
    return False


def get_dynamic_code(code_id: int) -> AGIObject:
    target_file = open('Formatted/' + str(code_id) + '.txt', 'rb')
    code = pickle.load(target_file)
    target_file.close()
    return code
