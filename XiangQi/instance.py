from AGI.objects import num_obj
from Game.structures import *


def vector_object(numbers, cid_of):
    value = list()
    for number in numbers:
        value.append(num_obj(number, cid_of))
    return AGIObject(cid_of['vector'], {cid_of['content']: AGIList(value)})


def piece_object(owner: str, name: str, position: list, cid_of) -> AGIObject:
    return AGIObject(cid_of['xq::piece'], {cid_of['xq::piece_owner']: AGIObject(cid_of[owner], dict()),
                                           cid_of['xq::piece_name']: AGIObject(cid_of[name], dict()),
                                           cid_of['xq::position']: vector_object(position, cid_of)})


def create_xq_chessboard(cid_of):
    pieces_list = [
        piece_object('xq::red_team', 'xq::Che', [0, 0], cid_of),
        piece_object('xq::red_team', 'xq::Ma', [1, 0], cid_of),
        piece_object('xq::red_team', 'xq::Xiang', [2, 0], cid_of),
        piece_object('xq::red_team', 'xq::Shi', [3, 0], cid_of),
        piece_object('xq::red_team', 'xq::Jiang', [4, 0], cid_of),
        piece_object('xq::red_team', 'xq::Shi', [5, 0], cid_of),
        piece_object('xq::red_team', 'xq::Xiang', [6, 0], cid_of),
        piece_object('xq::red_team', 'xq::Ma', [7, 0], cid_of),
        piece_object('xq::red_team', 'xq::Che', [8, 0], cid_of),
        piece_object('xq::red_team', 'xq::Pao', [1, 2], cid_of),
        piece_object('xq::red_team', 'xq::Pao', [7, 2], cid_of),
        piece_object('xq::red_team', 'xq::Bing', [0, 3], cid_of),
        piece_object('xq::red_team', 'xq::Bing', [2, 3], cid_of),
        # piece_object('xq::red_team', 'xq::Bing', [4, 3], cid_of),
        piece_object('xq::red_team', 'xq::Bing', [6, 3], cid_of),
        piece_object('xq::red_team', 'xq::Bing', [8, 3], cid_of),
        piece_object('xq::black_team', 'xq::Che', [0, 9], cid_of),
        piece_object('xq::black_team', 'xq::Ma', [1, 9], cid_of),
        piece_object('xq::black_team', 'xq::Xiang', [2, 9], cid_of),
        piece_object('xq::black_team', 'xq::Shi', [3, 9], cid_of),
        piece_object('xq::black_team', 'xq::Jiang', [4, 9], cid_of),
        piece_object('xq::black_team', 'xq::Shi', [5, 9], cid_of),
        piece_object('xq::black_team', 'xq::Xiang', [6, 9], cid_of),
        piece_object('xq::black_team', 'xq::Ma', [7, 9], cid_of),
        piece_object('xq::black_team', 'xq::Che', [8, 9], cid_of),
        piece_object('xq::black_team', 'xq::Pao', [1, 7], cid_of),
        piece_object('xq::black_team', 'xq::Pao', [7, 7], cid_of),
        piece_object('xq::black_team', 'xq::Bing', [0, 6], cid_of),
        piece_object('xq::black_team', 'xq::Bing', [2, 6], cid_of),
        # piece_object('xq::black_team', 'xq::Bing', [4, 6], cid_of),
        piece_object('xq::black_team', 'xq::Bing', [6, 6], cid_of),
        piece_object('xq::black_team', 'xq::Bing', [8, 6], cid_of),
    ]
    pieces = AGIList(pieces_list)
    whose_turn = AGIObject(cid_of['xq::red_team'], dict())
    xq_chessboard = xq_chessboard_object(pieces, whose_turn, cid_of)
    return xq_chessboard


def create_xq_teams(cid_of):
    teams = [
        team_object('xq::red_team',
                    AGIList([player_object('xq::red_player', 'xq::player_occupation', cid_of)]),
                    'xq::player_benefit', cid_of),
        team_object('xq::black_team',
                    AGIList([player_object('xq::black_player', 'xq::player_occupation', cid_of)]),
                    'xq::player_benefit', cid_of)
    ]
    return teams


def create_xq_game(cid_of, dcd):
    operation_func = dcd.get_code(cid_of['func::operation_func'])
    occupations = [occupation_object('xq::player_occupation', operation_func, cid_of)]
    who_is_next_func = dcd.get_code(cid_of['func::who_is_next_func'])
    rule = rule_object(AGIList(create_xq_teams(cid_of)), AGIList(occupations),
                       who_is_next_func, obj('xq::red_team', cid_of), cid_of)
    end_game_func = dcd.get_code(cid_of['func::end_game_func'])
    benefit_func = dcd.get_code(cid_of['func::end_game_benefit'])
    end_game_benefits = [end_game_benefit('xq::player_benefit', benefit_func, cid_of)]
    winning_criteria = winning_criteria_object(end_game_func, AGIList(end_game_benefits), cid_of)
    elephant_chess = game_object(create_xq_chessboard(cid_of), rule, winning_criteria, cid_of)
    return elephant_chess
