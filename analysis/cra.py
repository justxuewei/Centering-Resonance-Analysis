# coding=utf-8


def betweenness_centrality(neo4j, article):
    centrality_cypher = "CALL algo.betweenness.stream('%s', null, {direction:'both'}) " \
             "YIELD nodeId, centrality RETURN nodeId,centrality order by centrality desc;" % article

    centralities = neo4j.data(centrality_cypher)

    bc = []
    centralities_len = len(centralities)
    # print("article centrality_len: %d" % centralities_len)
    for centrality in centralities:
        node_id = centrality['nodeId']
        _centrality = centrality['centrality']
        q_cypher = "match (a) where id(a)=%d return a" % node_id
        q_result = neo4j.data(q_cypher)
        _word = q_result[0]['a']['word']
        _index = q_result[0]['a']['index']
        _flag = q_result[0]['a']['flag']
        bc.append({
            "centrality": _centrality / ((centralities_len - 1) * (centralities_len - 2) / 2)
            if (centralities_len - 1) * (centralities_len - 2) / 2 != 0 else 0,
            "word": _word,
            "index": _index,
            "flag": _flag
        })

    return bc


def resonance_based_on_common_words(bc1, bc2):
    """
    根据公共词确定resonance
    :param bc1: 第一个词网络的betweenness_centrality
    :param bc2: 第二个词网络的betweenness_centrality
    :return: resonance
    """
    total = 0
    for b1 in bc1:
        for b2 in bc2:
            if b1['word'] == b2['word']:
                total += (b1['centrality'] * b2['centrality'])
    return total
