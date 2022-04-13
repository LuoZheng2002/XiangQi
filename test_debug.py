from AGI.code_browser import CodeTranslator
from AGI.dynamic_code_getter import get_dynamic_code
from Exception.dynamic_code_exception import DynamicCodeException, show_dynamic_code_exception
from Concept.concept_manager import summon_concepts
from XiangQi.instance import create_xq_game
from XiangQi.chessboard_browser import print_chessboard
from AGI.code_driver import run_dynamic_code
from AGI.struct import AGIObject, AGIList
from AGI.objects import obj
from AGI.translate_struct import print_obj
from dynamic_code_manager import DynamicCodeDatabase
from AGI.code_browser import CodeTranslator

cid_of, cid_reverse = summon_concepts('Concept/concepts.txt')
dcd = DynamicCodeDatabase('Formatted')
try:
    ct = CodeTranslator(get_dynamic_code(cid_of['func::operation_func']), cid_of, cid_reverse)
    for i in range(20):
        print(ct.translate_single_line(i + 1))
except DynamicCodeException as d:
    show_dynamic_code_exception(d, cid_of, cid_reverse, True)