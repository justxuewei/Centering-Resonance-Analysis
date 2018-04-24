def betweenness_centrality(handler):
    cypher = "CALL algo.betweenness.stream(null, null, {direction:'both'}) " \
             "YIELD nodeId, centrality RETURN nodeId,centrality order by centrality desc;"

    return handler.dict_reader(cypher)
