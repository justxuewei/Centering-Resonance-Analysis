import textprocessing.pre_processing as prepcs
import textprocessing.save_to_neo4j as stn
import analysis.cra as cra
from py2neo import Graph, Node, Relationship, NodeSelector
from conf import *


def init(neo4j):
    text = prepcs.load_text()
    noun_words, all_words = prepcs.select(text)
    stn.create_nodes(neo4j, 'default', noun_words)
    stn.create_relationship_by_np(neo4j, 'default', noun_words)
    stn.create_relationship_by_nanp(neo4j, 'default', noun_words)
    stn.merge_same_word_nodes(neo4j, 'default', noun_words)


def analysis(neo4j):
    r = cra.betweenness_centrality(neo4j)
    return r


if __name__ == '__main__':
    neo4j_cra = Graph(bolt=neo4j_cra_blot, host=neo4j_cra_host, user=neo4j_cra_db, password="wqnmlgb")
    # neo4j_cra.delete_all()
    # init(neo4j_cra)
    result = analysis(neo4j_cra)
