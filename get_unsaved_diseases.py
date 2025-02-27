import json

def get_diseases(filename):
    with open(filename, "r") as file:
        diseases_info = json.load(file)
    list_disease_names = [{'id': x['data']['properties']['identifier'], 'name': x['data']['properties']['name']}
                           for x in diseases_info   if x['data']['properties'].get('name') != None] ## for test below
    # list_disease_names = [x['data']['properties']['name'] for x in diseases_info if x['data']['properties'].get('name') != None]
    return set(list_disease_names)

def get_unsaved_diseases():
    set_disease_names_knowledge = get_diseases("./data/disease_knowledge.json")
    set_disease_names_all = get_diseases("./data/disease_all.json")
    return list(set_disease_names_all.difference(set_disease_names_knowledge))

# Test to see should get the elements with ids or names => choose name because the diff_names len=16, diff_ids len=14 and diff_names includes all elements in diff_ids
disease_names_knowledge = get_diseases("./data/disease_knowledge.json")
disease_names_experiments = get_diseases("./data/disease_experiments.json")
disease_names_knowledge.extend(disease_names_experiments)
saved_diseases = disease_names_knowledge

disease_names_all = get_diseases("./data/disease_all.json")
set_disease_names_knowledge_ids = set(map(lambda x: x['id'], disease_names_knowledge))
set_disease_names_experiments_ids = set(map(lambda x: x['id'], disease_names_experiments))

# diff_ids = list(set_disease_names_experiments_ids.difference(set_disease_names_knowledge_ids))
# print(len(diff_ids))
# diff_elements =  [disease for disease in disease_names_experiments if disease['id'] in diff_ids ]
# print(json.dumps(diff_elements, indent=4))

# print('Diff Name')
set_disease_names_saved = set(map(lambda x: x['name'], saved_diseases))
set_disease_names_all = set(map(lambda x: x['name'], disease_names_all))
diff_names = list(set_disease_names_all.difference(set_disease_names_saved))
print(len(diff_names))
print(json.dumps(diff_names, indent=4))
