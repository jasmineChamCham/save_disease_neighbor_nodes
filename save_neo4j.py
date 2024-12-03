from neo4j import GraphDatabase
import json

# DB Neo4j Connection
uri = "bolt://localhost:7687" 
username = "neo4j"
password = "Ngoctram123"
driver = GraphDatabase.driver(uri, auth=(username, password))
def create_nodes_and_relationships(tx, row):
    source_type = row['source_type']
    target_type = row['target_type']

    tx.run(f"""
        MERGE (source:{source_type} {{id: $source_id, name: $source_name, type: $source_type}})
    """, source_id=row['source'], source_name=row['source_name'], source_type=source_type)
    
    # Node Target
    tx.run(f"""
        MERGE (target:{target_type} {{id: $target_id, name: $target_name, type: $target_type}})
    """, target_id=row['target'], target_name=row['target_name'], target_type=target_type)

    # Serialize non-primitive types like dictionaries into strings
    evidence = json.dumps(row['evidence']) if isinstance(row['evidence'], dict) else row['evidence']
    context_with_edge = json.dumps(row['context_with_edge']) if isinstance(row['context_with_edge'], dict) else row['context_with_edge']

    # Create relationship between source and target with properties
    tx.run("""
        MATCH (source {id: $source_id})
        MATCH (target {id: $target_id})
        MERGE (source)-[r:RELATIONSHIP_TYPE {type: $edge_type}]->(target)
        SET r.provenance = $provenance,
            r.evidence = $evidence,
            r.predicate = $predicate,
            r.context = $context,
            r.context_with_edge = $context_with_edge
    """, source_id=row['source'], target_id=row['target'], edge_type=row['edge_type'],
         provenance=row['provenance'], evidence=evidence, predicate=row['predicate'],
         context=row['context'], context_with_edge=context_with_edge)
    
def save_df_neo4j(df):
    with driver.session() as session:
        for _, row in df.iterrows():
            session.write_transaction(create_nodes_and_relationships, row)