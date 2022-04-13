from AGI.code_browser import add_indentation
from AGI.struct import AGIObject, AGIList
from AGI.code_browser import translate_expression, number_to_letter
from AGI.objects import to_integer
from AGI.runtime_memory import RuntimeMemory
from AGI.code_browser import translate_code

global_given_line = [None]
global_given_function = [None]

def translate_dynamic_code_line(line, cid_of, cid_reverse):
    if line.concept_id == cid_of['dcr::assign'] or line.concept_id == cid_of['dcr::assign_as_reference']:
        if line.concept_id == cid_of['dcr::assign']:
            sign = ' = '
        else:
            sign = ' &= '
        result = translate_expression(line.attributes[cid_of['dc::left_value']],
                                      cid_of, cid_reverse) + sign + translate_expression(
            line.attributes[cid_of['dc::right_value']], cid_of, cid_reverse)
        return result
    if line.concept_id == cid_of['dcr::return']:
        result = 'return ' + translate_expression(line.attributes[cid_of['dc::return_value']], cid_of,
                                                  cid_reverse)
        return result
    if line.concept_id == cid_of['dcr::assert']:
        result = 'assert ' + translate_expression(line.attributes[cid_of['dc::assert_expression']],
                                                  cid_of,
                                                  cid_reverse)
        return result
    if line.concept_id == cid_of['dcr::for']:
        iter_index = to_integer(line.attributes[cid_of['dc::iterator_index']], cid_of)
        if iter_index in number_to_letter.keys():
            iterator_name = number_to_letter[iter_index]
        else:
            iterator_name = 'iter' + str(iter_index)
        end_value = translate_expression(line.attributes[cid_of['dc::end_value']], cid_of,
                                         cid_reverse)
        result = 'for ' + iterator_name + ' in range(' + end_value + '):'
        return result
    if line.concept_id == cid_of['dcr::while']:
        expression_for_judging = translate_expression(line.attributes[cid_of['dc::expression_for_judging']],
                                                      cid_of,
                                                      cid_reverse)
        result = 'while ' + expression_for_judging + ':'
        return result
    if line.concept_id == cid_of['dcr::break']:
        result = 'break'
        return result
    if line.concept_id == cid_of['dcr::if']:
        expression_for_judging = translate_expression(line.attributes[cid_of['dc::expression_for_judging']],
                                                      cid_of,
                                                      cid_reverse)
        result = 'if ' + expression_for_judging + ':'
        return result
    if line.concept_id == cid_of['dcr::append'] or line.concept_id == cid_of['dcr::remove']:
        target_list = translate_expression(line.attributes[cid_of['dc::target_list']], cid_of,
                                           cid_reverse)
        if line.concept_id == cid_of['dcr::append']:
            element = translate_expression(line.attributes[cid_of['dc::element']], cid_of,
                                           cid_reverse)
            word = '.append('
        else:
            element = translate_expression(line.attributes[cid_of['dc::expression_for_constraint']],
                                           cid_of,
                                           cid_reverse)
            word = '.remove('
        result = target_list + word + element + ')'
        return result
    if line.concept_id == cid_of['dcr::request']:
        result = 'request '
        assert type(line.attributes[cid_of['dc::requested_registers']]) == AGIList
        for reg_id in line.attributes[cid_of['dc::requested_registers']].value:
            result += 'reg' + str(to_integer(reg_id, cid_of)) + ', '
        result += 's.t.{'
        result += translate_expression(line.attributes[cid_of['dc::expression_for_constraint']], cid_of,
                                       cid_reverse)
        result += '}, provided:'
        return result
    if line.concept_id == cid_of['dcr::call_none_return_func']:
        result = "'" + cid_reverse[line.attributes[cid_of['dc::function_name']].concept_id] + "'("
        function_params = line.attributes[cid_of['dc::function_params']].value
        for function_param in function_params:
            result += translate_expression(function_param, cid_of, cid_reverse) + ', '
        if function_params:
            result = result[:-2]
        result += ')'
        return result
    if line.concept_id == cid_of['dc::elif_module']:
        result = 'elif ' + translate_expression(line.attributes[cid_of['dc::expression_for_judging']],
                                                cid_of, cid_reverse) + ':'
        return result
    assert False

class Line:
    def __init__(self, line_ptr, indentation):
        self.line_ptr = line_ptr
        self.indentation = indentation


class Debugger:
    def __init__(self, code_id, code_object: AGIObject, cid_of, cid_reverse, runtime_memory: RuntimeMemory):
        self.cid_of = cid_of
        self.cid_reverse = cid_reverse
        self.code_id = code_id
        self.code_object = code_object
        self.lines = list()
        self.get_lines(self.code_object, self.lines, 0)
        self.debug_signal = None
        self.runtime_memory = runtime_memory

    def get_lines(self, code_object, lines, indentation):
        for line in code_object.agi_list().value:
            if line.concept_id == self.cid_of['dcr::for']:
                lines.append(Line(line, indentation))
                self.get_lines(line.attributes[self.cid_of['dc::for_block']], lines, indentation + 1)
            elif line.concept_id == self.cid_of['dcr::while']:
                lines.append(Line(line, indentation))
                self.get_lines(line.attributes[self.cid_of['dc::while_block']], lines, indentation + 1)
            elif line.concept_id == self.cid_of['dcr::if']:
                lines.append(Line(line, indentation))
                self.get_lines(line.attributes[self.cid_of['dc::if_block']], lines, indentation + 1)
                for elif_module in line.attributes[self.cid_of['dc::elif_modules']].value:
                    lines.append(Line(elif_module, indentation))
                    self.get_lines(elif_module.attributes[self.cid_of['dc::elif_block']], lines, indentation + 1)
                if line.attributes[self.cid_of['dc::else_block']].agi_list().size() > 0:
                    lines.append(Line('else', indentation))
                    self.get_lines(line.attributes[self.cid_of['dc::else_block']], lines, indentation + 1)
            elif line.concept_id == self.cid_of['dcr::request']:
                lines.append(Line(line, indentation))
                self.get_lines(line.attributes[self.cid_of['dc::provided_block']], lines, indentation + 1)
            else:
                lines.append(Line(line, indentation))

    def translate_single_line(self, line_index):
        assert line_index > 0
        line = self.lines[line_index - 1].line_ptr
        indentation = self.lines[line_index - 1].indentation
        if line == 'else':
            return add_indentation('else:', indentation, 0, False)
        if line.concept_id == self.cid_of['dcr::assign'] or line.concept_id == self.cid_of['dcr::assign_as_reference']:
            if line.concept_id == self.cid_of['dcr::assign']:
                sign = ' = '
            else:
                sign = ' &= '
            result = translate_expression(line.attributes[self.cid_of['dc::left_value']],
                                          self.cid_of, self.cid_reverse) + sign + translate_expression(
                line.attributes[self.cid_of['dc::right_value']], self.cid_of, self.cid_reverse)
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dcr::return']:
            result = 'return ' + translate_expression(line.attributes[self.cid_of['dc::return_value']], self.cid_of,
                                                      self.cid_reverse)
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dcr::assert']:
            result = 'assert ' + translate_expression(line.attributes[self.cid_of['dc::assert_expression']],
                                                      self.cid_of,
                                                      self.cid_reverse)
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dcr::for']:
            iter_index = to_integer(line.attributes[self.cid_of['dc::iterator_index']], self.cid_of)
            if iter_index in number_to_letter.keys():
                iterator_name = number_to_letter[iter_index]
            else:
                iterator_name = 'iter' + str(iter_index)
            end_value = translate_expression(line.attributes[self.cid_of['dc::end_value']], self.cid_of,
                                             self.cid_reverse)
            result = 'for ' + iterator_name + ' in range(' + end_value + '):'
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dcr::while']:
            expression_for_judging = translate_expression(line.attributes[self.cid_of['dc::expression_for_judging']],
                                                          self.cid_of,
                                                          self.cid_reverse)
            result = 'while ' + expression_for_judging + ':'
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dcr::break']:
            result = 'break'
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dcr::if']:
            expression_for_judging = translate_expression(line.attributes[self.cid_of['dc::expression_for_judging']],
                                                          self.cid_of,
                                                          self.cid_reverse)
            result = 'if ' + expression_for_judging + ':'
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dcr::append'] or line.concept_id == self.cid_of['dcr::remove']:
            target_list = translate_expression(line.attributes[self.cid_of['dc::target_list']], self.cid_of,
                                               self.cid_reverse)
            if line.concept_id == self.cid_of['dcr::append']:
                element = translate_expression(line.attributes[self.cid_of['dc::element']], self.cid_of,
                                               self.cid_reverse)
                word = '.append('
            else:
                element = translate_expression(line.attributes[self.cid_of['dc::expression_for_constraint']],
                                               self.cid_of,
                                               self.cid_reverse)
                word = '.remove('
            result = target_list + word + element + ')'
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dcr::request']:
            result = 'request '
            assert type(line.attributes[self.cid_of['dc::requested_registers']]) == AGIList
            for reg_id in line.attributes[self.cid_of['dc::requested_registers']].value:
                result += 'reg' + str(to_integer(reg_id, self.cid_of)) + ', '
            result += 's.t.{'
            result += translate_expression(line.attributes[self.cid_of['dc::expression_for_constraint']], self.cid_of,
                                           self.cid_reverse)
            result += '}, provided:'
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dcr::call_none_return_func']:
            result = "'" + self.cid_reverse[line.attributes[self.cid_of['dc::function_name']].concept_id] + "'("
            function_params = line.attributes[self.cid_of['dc::function_params']].value
            for function_param in function_params:
                result += translate_expression(function_param, self.cid_of, self.cid_reverse) + ', '
            if function_params:
                result = result[:-2]
            result += ')'
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        if line.concept_id == self.cid_of['dc::elif_module']:
            result = 'elif ' + translate_expression(line.attributes[self.cid_of['dc::expression_for_judging']],
                                                    self.cid_of, self.cid_reverse) + ':'
            return add_indentation(result, indentation,
                                   to_integer(line.attributes[self.cid_of['dc::line_index']], self.cid_of), False)
        assert False

    def print_single_line(self, line_index, highlighted):
        if highlighted:
            print('->' + self.translate_single_line(line_index))
        else:
            print('  ' + self.translate_single_line(line_index))

    def get_debug_input(self):
        while True:
            debug_input = input('')
            if debug_input == '':
                self.debug_signal = 'step_over'
                break
            elif debug_input == 'si':
                self.debug_signal = 'step_into'
                break
            elif debug_input == 'so':
                self.debug_signal = 'step_out'
                break
            elif debug_input[:3] == 'reg':
                reg_index = int(debug_input[3:])
                target_object = self.runtime_memory.get_reg_value(reg_index)
                print(debug_input + ' is:')
                print_debug_object(target_object, self.cid_of, self.cid_reverse)
            elif debug_input[:4] == 'iter':
                iter_index = int(debug_input[4:])
                target_object = self.runtime_memory.get_iterator_value(iter_index)
                print(debug_input + ' is:')
                if type(target_object) == int:
                    print(target_object)
                else:
                    print_debug_object(target_object, self.cid_of, self.cid_reverse)
            elif debug_input[:5] == 'input':
                input_index = int(debug_input[5:])
                target_object = self.runtime_memory.get_input_value(input_index)
                print(debug_input + ' is:')
                print_debug_object(target_object, self.cid_of, self.cid_reverse)
            elif debug_input.isdigit():
                self.debug_signal = int(debug_input)
                break
            elif debug_input[:4] == 'set ':
                rest = debug_input[4:]
                space_pos = rest.find(' ')
                assert space_pos != -1
                function_name = rest[:space_pos]
                line_number = int(rest[space_pos+1:])
                global global_given_function, global_given_line
                global_given_function[0] = self.cid_of[function_name]
                global_given_line[0] = line_number
                print(global_given_line[0])
                print(global_given_function[0])
            else:
                print('Unknown command.')


def translate_debug_AGIList(target: AGIList, cid_of, cid_reverse, indentation, attribute_name):
    result = str()
    for i in range(indentation):
        result += '|   '
    if attribute_name != '':
        result += "'" + attribute_name + "': "
    result += 'AGIList\n'
    if target.size() > 0 and type(target.get_element(0)) == AGIObject \
            and target.get_element(0).concept_id == cid_of['xq::piece']:
        result += 'Some xq::piece s.\n'
    else:
        for i in target.value:
            if type(i) == AGIObject:
                result += translate_debug_AGIObject(i, cid_of, cid_reverse, indentation + 1, str())
            elif type(i) == AGIList():
                result += translate_debug_AGIList(i, cid_of, cid_reverse, indentation + 1, str())
            elif type(i) is None:
                for j in range(indentation + 1):
                    result += '    '
                result += 'None\n'
            else:
                assert False
    return result


def translate_debug_AGIObject(target, cid_of, cid_reverse, indentation, attribute_name):
    result = str()
    for i in range(indentation):
        result += '|   '
    if attribute_name != '':
        result += "'" + attribute_name + "': "
    result += "'" + cid_reverse[target.concept_id] + "'\n"
    line_concepts = [cid_of['dcr::assign'],
                     cid_of['dcr::assign_as_reference'],
                     cid_of['dcr::return'],
                     cid_of['dcr::assert'],
                     cid_of['dcr::for'],
                     cid_of['dcr::while'],
                     cid_of['dcr::break'],
                     cid_of['dcr::if'],
                     cid_of['dcr::append'],
                     cid_of['dcr::remove'],
                     cid_of['dcr::request'],
                     cid_of['dcr::call_none_return_func']]
    if target.concept_id == cid_of['natural_number']:
        result += '(natural_number)' + str(to_integer(target, cid_of)) + '\n'
    elif target.concept_id == cid_of['xq::chessboard']:
        result += 'A chessboard.\n'
    elif target.concept_id == cid_of['xq::pieces']:
        result += 'Some pieces.\n'
    elif target.concept_id in line_concepts:
        result += translate_dynamic_code_line(target, cid_of, cid_reverse) + '\n'
    else:
        for i in target.attributes:
            if type(target.attributes[i]) == AGIObject:
                result += translate_debug_AGIObject(target.attributes[i], cid_of, cid_reverse, indentation + 1,
                                                    cid_reverse[i])
            elif type(target.attributes[i]) == AGIList:
                result += translate_debug_AGIList(target.attributes[i], cid_of, cid_reverse, indentation + 1,
                                                  cid_reverse[i])
            elif target.attributes[i] is None:
                for j in range(indentation + 1):
                    result += '|   '
                result += "'" + cid_reverse[i] + '\': None\n'
            else:
                print(cid_reverse[target.attributes[i]])
                assert False
    return result


def print_debug_object(target, cid_of, cid_reverse):
    if type(target) == AGIObject:
        print(translate_debug_AGIObject(target, cid_of, cid_reverse, 0, str()))
    elif type(target) == AGIList:
        print(translate_debug_AGIList(target, cid_of, cid_reverse, 0, str()))
    else:
        print(type(target))
        assert False
