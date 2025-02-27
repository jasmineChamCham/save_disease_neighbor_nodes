import requests
import json

BASE_URI = 'https://spoke.rbvi.ucsf.edu'
def get_spoke_api_resp(base_uri, end_point, params=None):
    uri = base_uri + end_point
    if params:
        return requests.get(uri, params=params)
    else:
        return requests.get(uri)
    
with open('./data/spoke_types.json', 'r') as file_spoke_types: # save the result from api /types
    data_spoke_types = json.load(file_spoke_types)
    
edge_types = list(data_spoke_types["edges"].keys())
api_params = {
    'node_filters' : ['Compound'],
    'depth' : 1
}
node_type = "Compound"
attribute = "source"
node_value = "Disease Ontology"
nbr_end_point = "/api/v1/neighborhood/{}/{}/{}".format(node_type, attribute, node_value)
result = get_spoke_api_resp(BASE_URI, nbr_end_point, params=api_params)
node_context = result.json()

with open("./data/disease_all.json", "w") as file:
    json.dump(node_context, file, indent=4) 
print(f"Data saved to ./data/disease_all.json")