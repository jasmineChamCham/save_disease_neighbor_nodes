from neo4j import GraphDatabase
import json
from get_diseases_names import get_spoke_api_resp, BASE_URI
import urllib.parse

# DB Neo4j Connection
uri = "bolt://localhost:7687" 
username = "neo4j"
password = "Ngoctram123"
driver = GraphDatabase.driver(uri, auth=(username, password))

def get_neo4j_nodes(tx):
    query = "MATCH (n) where n.identifier is null return n"
    result = tx.run(query)
    return [record["n"] for record in result]

def get_identifier(node_type, value):
    value = value.replace("'", "\\'")
    
    try:
        attribute = "name"
        endpoint = "/api/v1/node/{}/{}/{}".format(node_type, attribute, value)
        result = get_spoke_api_resp(BASE_URI, endpoint)
        result = result.json()
        identifier = result[0]["identifier"]
        return identifier
    except Exception as e:
        value = value.replace('/', ' ')
        print('hehe')
        endpoint = "/api/v1/search/{}".format(value)
        result = get_spoke_api_resp(BASE_URI, endpoint)
        result = result.json()
        identifier = result[0]["identifier"]
        return identifier

def update_identifier(tx, identifier, node_type, node_id):
    query = f"""
    MATCH (d:{node_type}) 
    WHERE d.id = $node_id AND d.identifier IS NULL
    SET d.identifier = $identifier 
    RETURN d
    """
    result = tx.run(query, node_id=node_id, identifier=identifier)
    
    return [dict(record["d"]) for record in result]

with driver.session() as session:
    list_neo4j_nodes = session.read_transaction(get_neo4j_nodes)
    
list_nodes = [dict(node) for node in list_neo4j_nodes]
for neo4j_node in list_nodes:
    node_id = neo4j_node["id"]
    node_type = neo4j_node["type"]
    name = neo4j_node["name"]

    identifier = get_identifier(node_type=node_type, value=name)
    with driver.session() as session:
        result = session.write_transaction(update_identifier, identifier, node_type, node_id )
    print(json.dumps(result, indent=4))
    
# Close the driver
driver.close()