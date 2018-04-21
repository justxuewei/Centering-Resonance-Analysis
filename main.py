from text_processing import *
from neo4j_op.Neo4jHandler import Neo4jHandler
from neo4j.v1 import GraphDatabase
from constants import *

if __name__ == '__main__':
    # text = load_text()
    # noun_words, all_words = select(text, debug=True)

    # neo4j conf
    driver = GraphDatabase.driver(neo4j_cra_uri, auth={neo4j_cra_db, neo4j_cra_psw})
    neo4j_handler = Neo4jHandler(driver)


