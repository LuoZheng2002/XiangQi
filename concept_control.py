from Concept.concept_manager import create_concept, delete_concept, list_concepts, get_debug_description

while True:
    operation = input('Please input your operation:\n')
    if ' ' in operation:
        sliced = [operation[:operation.find(' ')], operation[operation.find(' ') + 1:]]
    else:
        sliced = [operation]
    if sliced[0] == 'c':
        create_concept(sliced[1])
    elif sliced[0] == 'd':
        delete_concept(sliced[1])
    elif sliced[0] == 'list':
        list_concepts()
    elif sliced[0].isdigit():
        get_debug_description(int(sliced[0]))
    elif sliced[0] == 'exit':
        break
    else:
        print('Invalid operation!')

