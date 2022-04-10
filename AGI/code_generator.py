from AGI.struct import AGIObject, AGIList
from AGI.objects import num_obj, obj
from Exception.agi_exception import AGIException
import pickle

number_to_letter = {0: 'i', 1: 'j', 2: 'k', 3: 'l', 4: 'm', 5: 'n', 6: 'o', 7: 'p', 8: 'q', 9: 'r',
                    10: 's', 11: 't', 12: 'u', 13: 'v', 14: 'w', 15: 'x', 16: 'y', 17: 'z'}
letter_to_number = dict([(i, j) for (j, i) in number_to_letter.items()])


class Line:
    def __init__(self, line_str, indentation_count, original_line):
        self.line_str = line_str
        self.indentation_count = indentation_count
        self.original_line = original_line


def slice_code(str_code: str) -> list:
    result = list()
    print('Slicing code!')
    if str_code and str_code[0] == '\n':
        str_code = str_code[1:]
    while str_code.find('\n') != -1:
        return_pos = str_code.find('\n')
        line_str_code = str_code[: return_pos]
        if line_str_code == '':
            print('Warning: an empty line.')
        else:
            while line_str_code[-1] == ' ':
                line_str_code = line_str_code[:-1]
            print(line_str_code)
            indentation_count = 0
            original_line = line_str_code
            while line_str_code.find('    ') == 0:
                line_str_code = line_str_code[4:]
                indentation_count += 1
            result.append(Line(line_str_code, indentation_count, original_line))
        str_code = str_code[return_pos + 1:]
    if str_code != '':
        print(str_code)
        indentation_count = 0
        original_line = str_code
        while str_code.find('    ') == 0:
            str_code = str_code[4:]
            indentation_count += 1
        result.append(Line(str_code, indentation_count, original_line))
    print('')
    return result


def slice_line(line: str) -> list:
    result = list()
    in_quotation = False
    while True:
        pos = 1000
        keywords = ['.', ',', '(', ')', '&', '<', '>', '{', '}', ' ', '\'', '=', '+', '-', ':', '!', '[', ']']
        for i in keywords:
            temp_pos = line.find(i)
            if temp_pos != -1 and temp_pos < pos:
                if in_quotation:
                    if line[temp_pos] == "'":
                        pos = temp_pos
                else:
                    pos = temp_pos
        if pos != 1000:
            temp_str = line[: pos]
            if temp_str != '':
                result.append(temp_str)
            if line[pos] == ' ':
                line = line[pos + 1:]
            elif line[pos] == '=':
                if len(line) > pos + 1 and line[pos + 1] == '=':
                    if len(line) > pos + 2 and line[pos + 2] == '=':
                        line = line[pos + 3:]
                        result.append('===')
                    else:
                        line = line[pos + 2:]
                        result.append('==')
                elif len(line) > pos + 1 and line[pos + 1] == '!':
                    assert line[pos + 2] == '='
                    line = line[pos + 3:]
                    result.append('=!=')
                else:
                    line = line[pos + 1:]
                    result.append('=')
            elif line[pos] == '!':
                assert line[pos + 1] == '='
                line = line[pos + 2:]
                result.append('!=')
            elif line[pos] == '>':
                if len(line) > pos + 1 and line[pos + 1] == '=':
                    line = line[pos + 2:]
                    result.append('>=')
                else:
                    line = line[pos + 1:]
                    result.append('>')
            elif line[pos] == '<':
                if len(line) > pos + 1 and line[pos + 1] == '=':
                    line = line[pos + 2:]
                    result.append('<=')
                else:
                    line = line[pos + 1:]
                    result.append('<')
            elif line[pos] == '&':
                assert line[pos + 1] == '='
                line = line[pos + 2:]
                result.append('&=')
            elif line[pos] == "'":
                in_quotation = not in_quotation
                line = line[pos + 1:]
                result.append("'")
            else:
                temp_str2 = line[pos]
                line = line[pos + 1:]
                result.append(temp_str2)
        else:
            break
    if line != '':
        result.append(line)
    return result


def find_close_bracket(line_pieces: list, open_bracket_pos: int):
    scope = 0
    for i in range(open_bracket_pos + 1, len(line_pieces)):
        if line_pieces[i] == ')':
            if scope == 0:
                return i
            else:
                scope -= 1
        elif line_pieces[i] == '(':
            scope += 1
    return -1


def find_naked_symbol(line_pieces: list, symbol: str, is_left: bool, start_pos=None, end_pos=None) -> int:
    if start_pos is None:
        start_pos = 0
    if end_pos is None:
        end_pos = len(line_pieces)
    if end_pos < 0:
        end_pos += len(line_pieces)
    scope = 0
    if is_left:
        result = 1000
    else:
        result = -1
    for i in range(start_pos, end_pos):
        if line_pieces[i] == '(':
            scope += 1
        elif line_pieces[i] == ')':
            if scope == 0:
                raise AGIException('Wrong bracket match.')
            scope -= 1
        elif line_pieces[i] == symbol and scope == 0:
            if is_left and i < result:
                result = i
            elif not is_left and i > result:
                result = i
    if result == 1000:
        result = -1
    return result


def generate_expression(expr: list, cid_of) -> AGIObject:
    if expr[0] == 'not':
        not_expr = generate_expression(expr[1:], cid_of)
        return AGIObject(cid_of['dcr::call'],
                         {cid_of['dc::function_name']: obj('func::logic_not', cid_of),
                          cid_of['dc::function_params']: AGIList([not_expr])})
    if ('and' in expr and find_naked_symbol(expr, 'and', False) != -1) or \
            ('or' in expr and find_naked_symbol(expr, 'or', False) != -1):
        and_pos = find_naked_symbol(expr, 'and', False)
        or_pos = find_naked_symbol(expr, 'or', False)
        pos = max(and_pos, or_pos)
        if expr[pos] == 'and':
            function_name = obj('func::logic_and', cid_of)
        else:
            function_name = obj('func::logic_or', cid_of)
        function_params = list()
        function_params.append(generate_expression(expr[:pos], cid_of))
        function_params.append(generate_expression(expr[pos + 1:], cid_of))
        return AGIObject(cid_of['dcr::call'],
                         {cid_of['dc::function_name']: function_name,
                          cid_of['dc::function_params']: AGIList(function_params)})
    elif ('==' in expr and find_naked_symbol(expr, '==', True) != -1) or \
            ('===' in expr and find_naked_symbol(expr, '===', True) != -1) or \
            ('>' in expr and find_naked_symbol(expr, '>', True) != -1) or \
            ('<' in expr and find_naked_symbol(expr, '<', True) != -1) or \
            ('>=' in expr and find_naked_symbol(expr, '>=', True) != -1) or \
            ('<=' in expr and find_naked_symbol(expr, '<=', True) != -1) or \
            ('+' in expr and find_naked_symbol(expr, '+', False) != -1) or \
            ('-' in expr and find_naked_symbol(expr, '-', False) != -1) or \
            ('and' in expr and find_naked_symbol(expr, 'and', False) != -1) or \
            ('or' in expr and find_naked_symbol(expr, 'or', False) != -1):
        if '==' in expr and find_naked_symbol(expr, '==', True) != -1:
            pos = find_naked_symbol(expr, '==', True)
            function_name = obj('func::compare_concepts', cid_of)
        elif '===' in expr and find_naked_symbol(expr, '===', True) != -1:
            pos = find_naked_symbol(expr, '===', True)
            function_name = obj('func::math_equal', cid_of)
        elif '>' in expr and find_naked_symbol(expr, '>', True) != -1:
            pos = find_naked_symbol(expr, '>', True)
            function_name = obj('func::greater_than', cid_of)
        elif '<' in expr and find_naked_symbol(expr, '<', True) != -1:
            pos = find_naked_symbol(expr, '<', True)
            function_name = obj('func::less_than', cid_of)
        elif '>=' in expr and find_naked_symbol(expr, '>=', True) != -1:
            pos = find_naked_symbol(expr, '>=', True)
            function_name = obj('func::greater_than_or_equal_to', cid_of)
        elif '<=' in expr and find_naked_symbol(expr, '<=', True) != -1:
            pos = find_naked_symbol(expr, '<=', True)
            function_name = obj('func::less_than_or_equal_to', cid_of)
        elif ('+' in expr and find_naked_symbol(expr, '+', False) != -1) or \
                ('-' in expr and find_naked_symbol(expr, '-', False) != -1):
            plus_pos = find_naked_symbol(expr, '+', False)
            minus_pos = find_naked_symbol(expr, '-', False)
            pos = max(plus_pos, minus_pos)
            if expr[pos] == '+':
                function_name = obj('func::sum', cid_of)
            else:
                function_name = obj('func::difference', cid_of)
        else:
            assert False
        function_params = list()
        function_params.append(generate_expression(expr[:pos], cid_of))
        function_params.append(generate_expression(expr[pos + 1:], cid_of))
        return AGIObject(cid_of['dcr::call'],
                         {cid_of['dc::function_name']: function_name,
                          cid_of['dc::function_params']: AGIList(function_params)})
    if ('!=' in expr and find_naked_symbol(expr, '!=', True) != -1) or \
            ('=!=' in expr and find_naked_symbol(expr, '=!=', True) != -1):
        if '!=' in expr and find_naked_symbol(expr, '!=', True) != -1:
            pos = find_naked_symbol(expr, '!=', True)
            function_name = obj('func::compare_concepts', cid_of)
        elif '=!=' in expr and find_naked_symbol(expr, '=!=', True) != -1:
            pos = find_naked_symbol(expr, '=!=', True)
            function_name = obj('func::compare_concepts', cid_of)
        else:
            assert False
        function_params = list()
        function_params.append(generate_expression(expr[:pos], cid_of))
        function_params.append(generate_expression(expr[pos + 1:], cid_of))
        not_expr = AGIObject(cid_of['dcr::call'],
                             {cid_of['dc::function_name']: function_name,
                              cid_of['dc::function_params']: AGIList(function_params)})
        return AGIObject(cid_of['dcr::call'],
                         {cid_of['dc::function_name']: obj('func::logic_not', cid_of),
                          cid_of['dc::function_params']: AGIList([not_expr])})
    if expr[-1] == ']':
        open_square_pos = find_naked_symbol(expr, '[', False, 0, -1)
        assert open_square_pos != -1
        return AGIObject(cid_of['dcr::at'],
                         {cid_of['dc::target_list']: generate_expression(expr[:open_square_pos], cid_of),
                          cid_of['dc::element_index']: generate_expression(expr[open_square_pos + 1: -1], cid_of)})
    if find_naked_symbol(expr, '.', False) != -1:
        dot_pos = find_naked_symbol(expr, '.', False)
        if expr[dot_pos + 1] == "'":
            assert expr[dot_pos + 3] == "'"
            assert len(expr) == dot_pos + 4
            return AGIObject(cid_of['dcr::get_member'],
                             {cid_of['dc::target_object']: generate_expression(expr[:dot_pos], cid_of),
                              cid_of['dc::member_name']: obj(expr[dot_pos + 2], cid_of)})
        if expr[dot_pos + 1] == 'find' or expr[dot_pos + 1] == 'exist' or expr[dot_pos + 1] == 'count':
            assert expr[dot_pos + 2] == '('
            assert expr[-1] == ')'
            if expr[dot_pos + 1] == 'find':
                concept_id = cid_of['dcr::find']
            elif expr[dot_pos + 1] == 'exist':
                concept_id = cid_of['dcr::exist']
            else:
                concept_id = cid_of['dcr::count']
            return AGIObject(concept_id,
                             {cid_of['dc::target_list']: generate_expression(expr[:dot_pos], cid_of),
                              cid_of['dc::expression_for_constraint']:
                                  generate_expression(expr[dot_pos + 3:-1], cid_of)})
        if expr[dot_pos + 1] == 'size':
            if not len(expr) == dot_pos + 2:
                print(expr)
                assert False
            return AGIObject(cid_of['dcr::size'],
                             {cid_of['dc::target_list']: generate_expression(expr[:dot_pos], cid_of)})
        assert False
    if expr[0] == "'":
        if expr[-1] == "'":
            assert len(expr) == 3
            return AGIObject(cid_of['dcr::concept_instance'],
                             {cid_of['dc::concept_name']: obj(expr[1], cid_of)})

        if expr[-1] == ')':
            assert expr[2] == "'"
            assert expr[3] == '('
            sub_expr = expr[4:-1]
            function_params = list()
            if sub_expr:
                while find_naked_symbol(sub_expr, ',', True) != -1:
                    comma_pos = find_naked_symbol(sub_expr, ',', True)
                    function_params.append(generate_expression(sub_expr[:comma_pos], cid_of))
                    sub_expr = sub_expr[comma_pos + 1:]
                if sub_expr:
                    function_params.append(generate_expression(sub_expr, cid_of))
            return AGIObject(cid_of['dcr::call'],
                             {cid_of['dc::function_name']: obj(expr[1], cid_of),
                              cid_of['dc::function_params']: AGIList(function_params)})
        assert False
    if len(expr) == 1:
        if expr[0][:5] == 'input' or expr[0][:3] == 'reg' or expr[0][:4] == 'iter':
            if expr[0][:5] == 'input':
                concept_id = cid_of['dcr::input']
                assert expr[0][5:].isdigit()
                index = num_obj(int(expr[0][5:]), cid_of)
            elif expr[0][:3] == 'reg':
                concept_id = cid_of['dcr::reg']
                assert expr[0][3:].isdigit()
                index = num_obj(int(expr[0][3:]), cid_of)
            else:
                concept_id = cid_of['dcr::iterator']
                if not expr[0][4:].isdigit():
                    print(expr[0])
                    assert False
                index = num_obj(int(expr[0][4:]), cid_of)
            return AGIObject(concept_id,
                             {cid_of['dc::index']: index})
        if expr[0] == 'target':
            return AGIObject(cid_of['dcr::target'])
        if expr[0] == 'True' or expr[0] == 'False' or expr[0] == 'Fail' or expr[0] == 'None':
            return AGIObject(cid_of['dcr::constexpr'], {cid_of['value']: obj(expr[0], cid_of)})
        if expr[0].isdigit():
            return AGIObject(cid_of['dcr::constexpr'],
                             {cid_of['value']: num_obj(int(expr[0]), cid_of)})
        if len(expr[0]) == 1 and expr[0].isalpha():
            assert expr[0] in letter_to_number.keys()
            return AGIObject(cid_of['dcr::iterator'],
                             {cid_of['dc::index']: num_obj(letter_to_number[expr[0]], cid_of)})
        assert False
    if expr[0] == '(' and expr[-1] == ')':
        return generate_expression(expr[1:-1], cid_of)
    print(expr)
    assert False


def generate_block(block: list, indentation_count: int, is_sub_block: bool, cid_of, real_line_index=None):
    if is_sub_block:
        block_cid = cid_of['dc::sub_block']
    else:
        block_cid = cid_of['dynamic_code']
    if not block:
        return AGIObject(block_cid, {cid_of['dc::lines']: AGIList()})
    if real_line_index is None:
        real_line_index = [1]
    lines = list()
    assert type(block[0]) == Line
    assert block[0].indentation_count == indentation_count
    line_index = 0
    while line_index < len(block):
        print(block[line_index].original_line)
        line_pieces = slice_line(block[line_index].line_str)
        if '=' in line_pieces or '&=' in line_pieces:
            if '=' in line_pieces:
                equal_pos = line_pieces.index('=')
                cid = cid_of['dcr::assign']
            elif '&=' in line_pieces:
                equal_pos = line_pieces.index('&=')
                cid = cid_of['dcr::assign_as_reference']
            else:
                assert False
            line_object = AGIObject(cid,
                                    {cid_of['dc::left_value']: generate_expression(line_pieces[:equal_pos], cid_of),
                                     cid_of['dc::right_value']: generate_expression(line_pieces[equal_pos + 1:],
                                                                                    cid_of),
                                     cid_of['dc::line_index']: num_obj(real_line_index[0], cid_of)})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'return':
            line_object = AGIObject(cid_of['dcr::return'],
                                    {cid_of['dc::return_value']: generate_expression(line_pieces[1:], cid_of),
                                     cid_of['dc::line_index']: num_obj(real_line_index[0], cid_of)})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'assert':
            line_object = AGIObject(cid_of['dcr::assert'],
                                    {cid_of['dc::assert_expression']: generate_expression(line_pieces[1:], cid_of),
                                     cid_of['dc::line_index']: num_obj(real_line_index[0], cid_of)})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'for':
            for_statement_line_index = real_line_index[0]
            real_line_index[0] += 1
            assert line_pieces[2] == 'in'
            assert line_pieces[3] == 'range'
            assert line_pieces[4] == '('
            assert line_pieces[-2] == ')'
            assert line_pieces[-1] == ':'
            iter_id_str = line_pieces[1]
            if iter_id_str in letter_to_number.keys():
                iter_id = num_obj(letter_to_number[iter_id_str], cid_of)
            else:
                assert iter_id_str[:4] == 'iter'
                assert iter_id_str[4:].isdigit()
                iter_id = num_obj(int(iter_id_str[4:]), cid_of)
            close_bracket_pos = find_close_bracket(line_pieces, 4)
            assert close_bracket_pos != -1
            end_value = generate_expression(line_pieces[5: close_bracket_pos], cid_of)
            line_index += 1
            if line_index == len(block):
                raise AGIException('Unexpected end of code after for statement.')
            for_block = list()
            while block[line_index].indentation_count >= indentation_count + 1:
                for_block.append(block[line_index])
                line_index += 1
                if line_index == len(block):
                    break
            line_object = AGIObject(cid_of['dcr::for'],
                                    {cid_of['dc::iterator_index']: iter_id,
                                     cid_of['dc::end_value']: end_value,
                                     cid_of['dc::for_block']: generate_block(for_block, indentation_count + 1, True,
                                                                             cid_of, real_line_index),
                                     cid_of['dc::line_index']: num_obj(for_statement_line_index, cid_of)})
            lines.append(line_object)
        elif line_pieces[0] == 'while':
            while_statement_line_index = real_line_index[0]
            real_line_index[0] += 1
            assert line_pieces[-1] == ':'
            expression_for_judging = generate_expression(line_pieces[1:-1], cid_of)
            line_index += 1
            if line_index == len(block):
                raise AGIException('Unexpected end of code after while statement.')
            while_block = list()
            while block[line_index].indentation_count >= indentation_count + 1:
                while_block.append(block[line_index])
                line_index += 1
                if line_index == len(block):
                    break
            line_object = AGIObject(cid_of['dcr::while'],
                                    {cid_of['dc::expression_for_judging']: expression_for_judging,
                                     cid_of['dc::while_block']: generate_block(while_block, indentation_count + 1,
                                                                               True, cid_of, real_line_index),
                                     cid_of['dc::line_index']: num_obj(while_statement_line_index, cid_of)})
            lines.append(line_object)
        elif line_pieces[0] == 'break':
            assert len(line_pieces) == 1
            line_object = AGIObject(cid_of['dcr::break'],
                                    {cid_of['dc::line_index']: num_obj(real_line_index, cid_of)})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'if':
            if_statement_line_index = real_line_index[0]
            real_line_index[0] += 1
            assert line_pieces[-1] == ':'
            expression_for_judging = generate_expression(line_pieces[1:-1], cid_of)
            line_index += 1
            if line_index == len(block):
                raise AGIException('Unexpected end of code after if statement.')
            if_block = list()
            elif_modules = list()
            else_block = list()
            while block[line_index].indentation_count >= indentation_count + 1:
                if_block.append(block[line_index])
                line_index += 1
                if line_index == len(block):
                    break
            if_block = generate_block(if_block, indentation_count + 1, True, cid_of, real_line_index)
            if line_index != len(block):
                while len(block) > line_index and block[line_index].line_str[:4] == 'elif':
                    elif_statement_line_index = real_line_index[0]
                    real_line_index[0] += 1
                    line_pieces = slice_line(block[line_index].line_str)
                    assert line_pieces[0] == 'elif'
                    assert line_pieces[-1] == ':'
                    elif_expression = generate_expression(line_pieces[1:-1], cid_of)
                    print(block[line_index].original_line)
                    line_index += 1
                    if line_index == len(block):
                        raise AGIException('Unexpected end of code after elif statement.')
                    elif_block = list()
                    while block[line_index].indentation_count >= indentation_count + 1:
                        elif_block.append(block[line_index])
                        line_index += 1
                        if line_index == len(block):
                            break
                    elif_module = AGIObject(cid_of['dc::elif_module'],
                                            {cid_of['dc::expression_for_judging']: elif_expression,
                                             cid_of['dc::elif_block']: generate_block(elif_block,
                                                                                      indentation_count + 1,
                                                                                      True, cid_of, real_line_index),
                                             cid_of['dc::line_index']: num_obj(elif_statement_line_index, cid_of)})
                    elif_modules.append(elif_module)
            if line_index != len(block) and block[line_index].line_str == 'else:':
                real_line_index[0] += 1
                print(block[line_index].original_line)
                line_index += 1
                if line_index == len(block):
                    raise AGIException('Unexpected end of code after else statement.')
                while block[line_index].indentation_count >= indentation_count + 1:
                    else_block.append(block[line_index])
                    line_index += 1
                    if line_index == len(block):
                        break
            line_object = AGIObject(cid_of['dcr::if'],
                                    {cid_of['dc::expression_for_judging']: expression_for_judging,
                                     cid_of['dc::if_block']: if_block,
                                     cid_of['dc::elif_modules']: AGIList(elif_modules),
                                     cid_of['dc::else_block']: generate_block(else_block,
                                                                              indentation_count + 1, True, cid_of,
                                                                              real_line_index),
                                     cid_of['dc::line_index']: num_obj(if_statement_line_index, cid_of)})
            lines.append(line_object)
        elif 'append' in line_pieces or 'remove' in line_pieces:
            if 'append' in line_pieces:
                is_append = True
                pos = line_pieces.index('append')
            else:
                is_append = False
                pos = line_pieces.index('remove')
            assert pos != 0 and line_pieces[pos - 1] == '.'
            assert line_pieces[pos + 1] == '('
            assert line_pieces[-1] == ')'
            if is_append:
                line_object = AGIObject(cid_of['dcr::append'],
                                        {cid_of['dc::target_list']: generate_expression(line_pieces[:pos - 1], cid_of),
                                         cid_of['dc::element']: generate_expression(line_pieces[pos + 2:-1], cid_of),
                                         cid_of['dc::line_index']: num_obj(real_line_index[0], cid_of)})
            else:
                line_object = AGIObject(cid_of['dcr::remove'],
                                        {cid_of['dc::target_list']: generate_expression(line_pieces[:pos - 1], cid_of),
                                         cid_of['dc::expression_for_constraint']:
                                             generate_expression(line_pieces[pos + 2:-1], cid_of),
                                         cid_of['dc::line_index']: num_obj(real_line_index[0], cid_of)})
            real_line_index[0] += 1
            lines.append(line_object)
            line_index += 1
        elif line_pieces[0] == 'request':
            request_statement_line_index = real_line_index[0]
            real_line_index[0] += 1
            assert 's' in line_pieces
            s_pos = line_pieces.index('s')
            assert line_pieces[s_pos + 1] == '.'
            assert line_pieces[s_pos + 2] == 't'
            assert line_pieces[s_pos + 3] == '.'
            assert line_pieces[s_pos + 4] == '{'
            sub_pieces = line_pieces[1: s_pos]
            register_indices = list()
            for piece in sub_pieces:
                if piece != ',':
                    assert piece[:3] == 'reg'
                    assert piece[3:].isdigit()
                    register_indices.append(num_obj(int(piece[3:]), cid_of))
            close_curly_pos = line_pieces.index('}')
            expression_for_constraint = generate_expression(line_pieces[s_pos + 5:close_curly_pos], cid_of)
            assert line_pieces[-2] == 'provided'
            assert line_pieces[-1] == ':'
            line_index += 1
            if line_index == len(block):
                raise AGIException('Unexpected end of code after request statement.')
            provided_block = list()
            while block[line_index].indentation_count >= indentation_count + 1:
                provided_block.append(block[line_index])
                line_index += 1
                if line_index == len(block):
                    break
            line_object = AGIObject(cid_of['dcr::request'],
                                    {cid_of['dc::requested_registers']: AGIList(register_indices),
                                     cid_of['dc::expression_for_constraint']: expression_for_constraint,
                                     cid_of['dc::provided_block']:
                                         generate_block(provided_block,
                                                        indentation_count + 1, True, cid_of, real_line_index),
                                     cid_of['dc::line_index']: num_obj(request_statement_line_index, cid_of)})
            lines.append(line_object)
        elif line_pieces[0] == "'" and line_pieces[-1] == ')':
            assert line_pieces[2] == "'"
            assert line_pieces[3] == '('
            code_object = obj(line_pieces[1], cid_of)
            sub_pieces = line_pieces[4:-1]
            code_params = list()
            if sub_pieces:
                while find_naked_symbol(sub_pieces, ',', True) != -1:
                    comma_pos = find_naked_symbol(sub_pieces, ',', True)
                    code_params.append(generate_expression(sub_pieces[:comma_pos], cid_of))
                    sub_pieces = sub_pieces[comma_pos + 1:]
                if sub_pieces:
                    code_params.append(generate_expression(sub_pieces, cid_of))

            line_object = AGIObject(cid_of['dcr::call_none_return_function'],
                                    {cid_of['dc::function_name']: code_object,
                                     cid_of['dc::function_params']: AGIList(code_params),
                                     cid_of['dc::line_index']: num_obj(real_line_index, cid_of)})
            real_line_index += 1
            lines.append(line_object)
            line_index += 1
        else:
            raise AGIException('Unknown line.')
    return AGIObject(block_cid, {cid_of['dc::lines']: AGIList(lines)})


def generate_code(code_name: str, cid_of):
    source_file = open('Visualized/' + code_name + '.txt', 'r')
    str_code = source_file.read()
    sliced_code = slice_code(str_code)
    print('Generating code!')
    result = generate_block(sliced_code, 0, False, cid_of)
    target_file = open('Formatted/' + str(cid_of['func::' + code_name]) + '.txt', 'wb')
    pickle.dump(result, target_file)
    print('Successfully generated!')
