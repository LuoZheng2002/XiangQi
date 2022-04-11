from Exception.dynamic_code_exception import DynamicCodeException, show_dynamic_code_exception
from Concept.concept_manager import summon_concepts
from XiangQi.instance import create_xq_game
from XiangQi.chessboard_browser import print_chessboard
from AGI.code_driver import run_dynamic_code
from AGI.struct import AGIObject, AGIList
from AGI.objects import obj
from AGI.translate_struct import print_obj
from dynamic_code_manager import DynamicCodeDatabase

cid_of, cid_reverse = summon_concepts('Concept/concepts.txt')
dcd = DynamicCodeDatabase('Formatted')
try:
    result = run_dynamic_code(cid_of['func::run_dynamic_code_object'],
                              AGIList([dcd.get_code(cid_of['func::test']),
                                       AGIList([])]), cid_of, dcd)
    print_obj(result, cid_reverse)
except DynamicCodeException as d:
    show_dynamic_code_exception(d, cid_of, cid_reverse, True)
