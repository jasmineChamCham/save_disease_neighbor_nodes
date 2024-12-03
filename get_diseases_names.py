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
    'node_filters' : ['Disease'],
    'edge_filters': edge_types,
    'cutoff_Compound_max_phase': 3 ,
    'cutoff_Protein_source': ['SwissProt'],
    'cutoff_DaG_diseases_sources': ['knowledge', 'experiments','textmining'],
    'cutoff_DaG_textmining': 1,
    'cutoff_CtD_phase': 3,
    'cutoff_PiP_confidence': 0.7,
    'cutoff_ACTeG_level': ['Low', 'Medium', 'High'],
    'cutoff_DpL_average_prevalence': 0.001,
    'depth' : 1
}
node_type = "Disease"
attribute = "source"
node_value = "Disease Ontology"
nbr_end_point = "/api/v1/neighborhood/{}/{}/{}".format(node_type, attribute, node_value)
result = get_spoke_api_resp(BASE_URI, nbr_end_point, params=api_params)
node_context = result.json()

with open("./data/disease_all.json", "w") as file:
    json.dump(node_context, file, indent=4) 
print(f"Data saved to ./data/disease_all.json")