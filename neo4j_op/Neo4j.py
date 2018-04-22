from neo4j_op.Neo4jHandler import Neo4jHandler
from conf import *
from neo4j.v1 import GraphDatabase


def get_neo4j_handler():
    # neo4j conf
    driver = GraphDatabase.driver(neo4j_cra_uri, auth=(neo4j_cra_db, neo4j_cra_psw))
    neo4j_handler = Neo4jHandler(driver)
    return neo4j_handler
