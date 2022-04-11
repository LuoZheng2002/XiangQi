from Exception.agi_exception import AGIException
from Exception.structure_exception import StructureException


class AGIObject:
    def __init__(self, concept_id: int, attributes=None):
        self.concept_id = concept_id
        if attributes is not None:
            self.attributes = attributes
        else:
            self.attributes = dict()

    def agi_list(self):
        if len(self.attributes) != 1:
            raise StructureException('Trying to get list from AGIObject but AGIObject has more than one attribute')
        for i in self.attributes.keys():
            if self.attributes[i] is None:
                self.attributes[i] = AGIList()
            elif type(self.attributes[i]) != AGIList:
                raise StructureException('The element in AGIObject is not AGIList.')
            return self.attributes[i]


class AGIList:
    def __init__(self, value: list = None):
        if value is None:
            self.value = list()
        else:
            self.value = value

    def set_value(self, index, value):
        if len(self.value) == index:
            self.value.append(value)
        elif len(self.value) < index:
            self.value += [[None] * (index - len(self.value))]
            self.value.append(value)
        else:
            self.value[index] = value

    def get_element(self, index):
        return self.value[index]

    def get_target_element(self, index):
        return self.value[index]

    def append(self, value):
        self.value.append(value)

    def remove(self, index):
        self.value.pop(index)

    def size(self):
        return len(self.value)
