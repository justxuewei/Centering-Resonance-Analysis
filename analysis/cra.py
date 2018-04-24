def betweenness_centrality(neo4j):
    cypher = "CALL algo.betweenness.stream(null, null, {direction:'both'}) " \
             "YIELD nodeId, centrality RETURN nodeId,centrality order by centrality desc;"

    return neo4j.data(cypher)
