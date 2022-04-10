from AGI.struct import AGIObject, AGIList
from AGI.objects import to_integer


def print_chessboard(xq_chessboard: AGIObject, cid_of, cid_reverse):
    chessboard = [[None for i in range(9)] for i in range(10)]
    for i in xq_chessboard.attributes[cid_of['xq::pieces']].value:
        name = cid_reverse[i.attributes[cid_of['xq::piece_name']].concept_id][4:]
        if i.attributes[cid_of['xq::piece_owner']].concept_id == cid_of['xq::red_team']:
            name = name.upper()
        else:
            name = name.lower()
        position = [None, None]
        position[0] = to_integer(i.attributes[cid_of['xq::position']].agi_list().get_element(0), cid_of)
        position[1] = to_integer(i.attributes[cid_of['xq::position']].agi_list().get_element(1), cid_of)
        chessboard[position[1]][position[0]] = name
    print('#################################################################################')
    print('####### 0 ##### 1 ##### 2 ##### 3 ##### 4 ##### 5 ##### 6 ##### 7 ##### 8 #######')

    for k, j in enumerate(chessboard):
        print(str(k).rjust(4, '#') + ' ', end='')
        for i in j:
            if i is None:
                print('[     ] ', end='')
            else:
                if len(i) <= 3:
                    i = ' ' + i
                print('[' + i.ljust(5, ' ') + '] ', end='')
        print('####')
    print('#################################################################################')