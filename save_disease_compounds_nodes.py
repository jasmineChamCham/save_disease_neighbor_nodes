import requests
import json
import pandas as pd 
import ast
from save_neo4j import save_df_neo4j 

base_url = 'https://spoke.rbvi.ucsf.edu'

def get_spoke_api_resp(base_uri, end_point, params=None):
    uri = base_uri + end_point
    if params:
        return requests.get(uri, params=params)
    else:
        return requests.get(uri)

def get_context_using_spoke_api(node_value):
    with open('./data/spoke_types.json', 'r') as file_spoke_types: # save the result from api /types
        data_spoke_types = json.load(file_spoke_types)
    edge_types = list(data_spoke_types["edges"].keys())
    api_params = {
        'node_filters' : ['Compound'],
        'edge_filters': edge_types,
        'cutoff_Protein_source': ['SwissProt'],
        'cutoff_DaG_textmining': 3,
        'cutoff_CtD_phase': 3,
        'cutoff_PiP_confidence': 0.7,
        'cutoff_ACTeG_level': ['Low', 'Medium', 'High'],
        'cutoff_DpL_average_prevalence': 0.001,
        'depth' : 1,
    }
    
    nbr_end_point = "/api/v1/neighborhood/Disease/name/{}".format(node_value)
    result = get_spoke_api_resp(base_url, nbr_end_point, params=api_params)
    node_context = result.json()
    
    if (len(node_context) == 0)  or result.status_code != 200 :
        return pd.DataFrame()
    
    nbr_nodes = []
    nbr_edges = []
    
    compounds = [node["data"]["properties"]["name"] for node in node_context if node["data"]["neo4j_type"]=='Compound']
    if len(compounds)>0:
        compounds = "\n".join(compounds) + "\n"
        with open('./data/list_compounds.txt', 'a') as f:
            f.write(compounds)

    for item in node_context:
        if "_" not in item["data"]["neo4j_type"]: # nodes
            try:
                if item["data"]["neo4j_type"] == "Protein":
                    nbr_nodes.append((item["data"]["neo4j_type"], item["data"]["id"], item["data"]["properties"]["description"]))
                else:
                    nbr_nodes.append((item["data"]["neo4j_type"], item["data"]["id"], item["data"]["properties"]["name"]))
            except:
                nbr_nodes.append((item["data"]["neo4j_type"], item["data"]["id"], item["data"]["properties"]["identifier"]))
        else: # edges
            try:
                provenance = ", ".join(item["data"]["properties"]["sources"])
            except:
                try:
                    provenance = item["data"]["properties"]["source"]
                    if isinstance(provenance, list):
                        provenance = ", ".join(provenance)
                except:
                    try:
                        preprint_list = ast.literal_eval(item["data"]["properties"]["preprint_list"])
                        if len(preprint_list) > 0:
                            provenance = ", ".join(preprint_list)
                        else:
                            pmid_list = ast.literal_eval(item["data"]["properties"]["pmid_list"])
                            pmid_list = map(lambda x:"pubmedId:"+x, pmid_list)
                            if len(pmid_list) > 0:
                                provenance = ", ".join(pmid_list)
                            else:
                                provenance = "Based on data from Institute For Systems Biology (ISB)"
                    except:
                        provenance = "SPOKE-KG"
            try:
                evidence = item["data"]["properties"]
            except:
                evidence = None
            nbr_edges.append((item["data"]["source"], item["data"]["neo4j_type"], item["data"]["target"], provenance, evidence))
    
    nbr_nodes_df = pd.DataFrame(nbr_nodes, columns=["node_type", "node_id", "node_name"])
    nbr_edges_df = pd.DataFrame(nbr_edges, columns=["source", "edge_type", "target", "provenance", "evidence"])

    node_type_map = nbr_nodes_df.set_index('node_id')['node_type'].to_dict()
    node_name_map = nbr_nodes_df.set_index('node_id')['node_name'].to_dict()

    # Map source and target nodes in nbr_edges_df to their types and names
    df = nbr_edges_df
    df['source_type'] = df['source'].map(node_type_map)
    df['source_name'] = df['source'].map(node_name_map)
    df['target_type'] = df['target'].map(node_type_map)
    df['target_name'] = df['target'].map(node_name_map)
    df = df [
        [ 'source', 'source_type', 'source_name', 'edge_type', 'target', 'target_type', 'target_name', 'provenance', 'evidence'] # source and target: id
    ]

    df.loc[:, 'predicate'] = df['edge_type'].apply(lambda x: x.split('_')[0])
    df.loc[:, 'context'] = df['source_type'] + " " + df['source_name'] + " " + df['predicate'].str.lower() + " " + df['target_type'] + " " + df['target_name'] + ' and Provenance of this association is ' + df['provenance'] + '.'
    df.loc[:, 'context_with_edge'] = df['source_type'] + " " + df['source_name'] + " " + df['predicate'].str.lower() + " " + df['target_type'] + " " + df['target_name'] + ' and Provenance of this association is ' + df['provenance'] + " and attributes associated with this association is in the following JSON format:\n " + df['evidence'].astype('str') + "\n\n"
    return df

def get_diseases():
    with open( "./data/disease_all.json", "r") as file:
        diseases_info = json.load(file)
    list_disease_names = [x['data']['properties']['name'] for x in diseases_info  if x['data']['properties'].get('name') != None]
    return list_disease_names

list_disease_names = get_diseases() # used to save the knowledge4
index = list_disease_names.index('progressive familial intrahepatic cholestasis')
print(f'idx={index}')
for node_value in list_disease_names[index:]:
    print(f'node_value = {node_value}')
    df = get_context_using_spoke_api(node_value)
    if df.empty == False:
        df.to_csv(f'./data/graph/compound/graph_{node_value}.csv')
        save_df_neo4j(df)
        print(f'Done {node_value}')
        with open('./data/process.txt', 'w') as f:
            f.write(node_value)
    else:
        print('df is empty!')
