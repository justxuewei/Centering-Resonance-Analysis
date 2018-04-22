from neo4j_op.Neo4j import get_neo4j_handler
import textprocessing.pre_processing as prepcs
import textprocessing.save_to_neo4j as stn

if __name__ == '__main__':
    neo4j_handler = get_neo4j_handler()

    text = prepcs.load_text()
    noun_words, all_words = prepcs.select(text)
    neo4j_handler.delete_nodes_by_label('default')
    stn.create_nodes(neo4j_handler, 'default', noun_words)
    stn.create_relationship_by_noun_phrase(neo4j_handler, 'default', noun_words)
