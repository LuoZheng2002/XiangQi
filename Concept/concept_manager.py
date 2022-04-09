import pickle

class ConceptDatabase:
    def __init__(self):
        self.concepts = list()
        self.next_id = 0
        self.empty_spaces = list()
class Concept:
    def __init__(self, concept_id, debug_description, attributes=None):
        self.concept_id = concept_id
        self.debug_description = debug_description
        if attributes is None:
            self.attributes = dict()
        else:
            self.attributes = attributes


def create_concept(debug_description: str, attributes=None):
    file = open('Concept/concepts.txt', 'rb')
    concept_database = pickle.load(file)
    concepts = concept_database.concepts
    file.close()
    for concept in concepts:
        if concept.debug_description == debug_description:
            print('Concept already created!')
        else:
            if concept_database.empty_spaces:
                concepts.append(Concept(concept_database.empty_spaces.pop(), debug_description, attributes))
                