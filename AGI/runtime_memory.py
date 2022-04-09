class RuntimeMemory:
    def __init__(self):
        self.inputs = list()
        self.registers = list()
        self.iterators = list()

    def get_input(self, index):
        for input_param in self.inputs:
            if input_param.index == index:
                return input_param
        return None

    def has_input(self, index):
        if self.get_input(index) is not None:
            return True
        return False

    def get_input_value(self, index):
        return self.get_input(index).value

    def get_reg(self, index):
        for register in self.registers:
            if register.index == index:
                return register
        return None

    def get_reg_value(self, index):
        return self.get_reg(index).value

    def has_reg(self, index):
        if self.get_reg(index) is not None:
            return True
        return False

    def create_reg(self, index, value=None):
        assert not self.has_reg(index)
        self.registers.append(Register(index, value))

    def set_reg(self, index, value):
        register = self.get_reg(index)
        assert register is not None
        register.value = value

    def get_iterator(self, index):
        for iterator in self.iterators:
            if iterator.index == index:
                return iterator
        return None

    def get_iterator_value(self, index):
        return self.get_iterator(index).value

    def has_iterator(self, index):
        if self.get_iterator(index) is not None:
            return True
        return False

    def create_iterator(self, index, value=None):
        assert not self.has_iterator(index)
        self.iterators.append(Iterator(index, value))
        return self.iterators[-1]

    def increment_iterator(self, index):
        iterator = self.get_iterator(index)
        assert iterator is not None
        iterator.value = iterator.value + 1

    def zero_iterator(self, index):
        iterator = self.get_iterator(index)
        assert iterator is not None
        iterator.value = 0


class Register:
    def __init__(self, index, value=None):
        self.index = index
        self.value = value


class Input:
    def __init__(self, index, value=None):
        self.index = index
        self.value = value


class Iterator:
    def __init__(self, index, value=None):
        self.index = index
        self.value = value
