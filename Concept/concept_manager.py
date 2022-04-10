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
            return
    if concept_database.empty_spaces:
        concepts.append(Concept(concept_database.empty_spaces.pop(), debug_description, attributes))
    else:
        concepts.append(Concept(concept_database.next_id, debug_description, attributes))
        concept_database.next_id += 1
    file = open('Concept/concepts.txt', 'wb')
    pickle.dump(concept_database, file)
    file.close()
    print('Concept successfully created!')


def delete_concept(debug_description: str):
    file = open('Concept/concepts.txt', 'rb')
    concept_database = pickle.load(file)
    concepts = concept_database.concepts
    file.close()
    for i, concept in enumerate(concepts):
        if concept.debug_description == debug_description:
            concept_database.empty_spaces.append(concept.concept_id)
            concepts.pop(i)
            print('Successfully deleted a concept!')
            file = open('Concept/concepts.txt', 'wb')
            pickle.dump(concept_database, file)
            file.close()
            return
    print('Unable to find the concept!')


def list_concepts():
    file = open('Concept/concepts.txt', 'rb')
    concept_database = pickle.load(file)
    file.close()
    for concept in concept_database.concepts:
        print(str(concept.concept_id) + ': ' + concept.debug_description)
    print('Finished!')


def summon_concepts(file_directory: str):
    file = open(file_directory, 'rb')
    concept_database = pickle.load(file)
    file.close()
    cid_of = dict()
    cid_reverse = dict()
    for concept in concept_database.concepts:
        cid_of.update({concept.debug_description: concept.concept_id})
        cid_reverse.update({concept.concept_id: concept.debug_description})
    return cid_of, cid_reverse


def get_debug_description(concept_id):
    file = open('Concept/concepts.txt', 'rb')
    concept_database = pickle.load(file)
    file.close()
    for concept in concept_database.concepts:
        if concept.concept_id == concept_id:
            print(concept.debug_description)
            return
    print('Cannot find target concept.')
