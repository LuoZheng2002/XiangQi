from Exception.dynamic_code_exception import DynamicCodeException, show_dynamic_code_exception
from Concept.concept_manager import summon_concepts
from XiangQi.instance import create_xq_game
from XiangQi.chessboard_browser import print_chessboard
from AGI.code_driver import run_dynamic_code
from AGI.struct import AGIObject, AGIList
from AGI.objects import obj
from AGI.translate_struct import print_obj
from dynamic_code_manager import DynamicCodeDatabase
from copy import deepcopy

cid_of, cid_reverse = summon_concepts('Concept/concepts.txt')
dcd = DynamicCodeDatabase('Formatted')
try:
    xq_game = create_xq_game(cid_of, dcd)
    current_chessboard = xq_game.attributes[cid_of['tb_game::chessboard']]
    # print_obj(current_chessboard, cid_reverse)
    # assert False
    while True:
        print('Now chessboard is:')
        print_chessboard(current_chessboard, cid_of, cid_reverse)
        whose_turn = run_dynamic_code(cid_of['func::who_is_next_func'], AGIList([current_chessboard]), cid_of, cid_reverse, dcd)
        if whose_turn.concept_id == cid_of['xq::red_team']:
            print('Now it\'s red team\'s turn to go!')
        elif whose_turn.concept_id == cid_of['xq::black_team']:
            print('Now it\'s black team\'s turn to go!')
        chessboard = run_dynamic_code(cid_of['func::run_dynamic_code_object'],
                                      AGIList([dcd.get_code(cid_of['func::operation_func']),
                                               AGIList([current_chessboard, whose_turn])]), cid_of, cid_reverse, dcd)
        # print_obj(chessboard, cid_reverse)
        # break
        current_chessboard = deepcopy(chessboard)
        end_game = run_dynamic_code(cid_of['func::end_game_func'], AGIList([current_chessboard]), cid_of, cid_reverse, dcd)
        if end_game.concept_id == cid_of['True']:
            print_chessboard(current_chessboard, cid_of, cid_reverse)
            print('Game ended!')
            red_benefit = run_dynamic_code(cid_of['func::end_game_benefit'],
                                           AGIList([current_chessboard, obj('xq::red_team', cid_of)]), cid_of, cid_reverse, dcd)
            black_benefit = run_dynamic_code(cid_of['func::end_game_benefit'],
                                             AGIList([current_chessboard,
                                                      obj('xq::black_team', cid_of)]), cid_of, cid_reverse, dcd)
            print('Red team\'s benefit is:')
            print_obj(red_benefit, cid_reverse)
            print('Black team\'s benefit is:')
            print_obj(black_benefit, cid_reverse)
            break
except DynamicCodeException as d:
    show_dynamic_code_exception(d, cid_of, cid_reverse)
