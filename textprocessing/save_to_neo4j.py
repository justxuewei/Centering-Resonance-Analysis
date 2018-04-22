def create_nodes(handler, article, noun_words):
    """
    根据名词词组创建节点(node)
    :param handler: neo4j handler
    :param article: 文章标题
    :param noun_words: 名词词组
    :return: none
    """
    cypher = 'create '
    for i, noun_word in enumerate(noun_words):
        word = noun_word['word']
        flag = noun_word['flag']
        index = noun_word['index']
        cypher += '(:%s {word: "%s", index: %d, flag: "%s"})' % (article, word, index, flag)
        if (i + 1) != len(noun_words):
            cypher += ", "

    handler.cypher_executor(cypher)


def create_relationship_by_noun_phrase(handler, article, noun_words):
    """
    根据名词短语(np)创建关系
    创建的策略是相邻名词短语相连，如果相连接节点大于等于3则节点首尾相连
    :param handler: neo4j handler
    :param article: 文章标题
    :param noun_words: 名词词组
    :return: none
    """
    temp_index = 0
    counter = 1
    params = {}
    relationship_data = []
    for i, noun_word in enumerate(noun_words):
        row_relationship_data = {}
        word = noun_word['word']
        index = noun_word['index']

        if (index - temp_index) == 1:
            row_relationship_data['a_index'] = noun_words[i - 1]['index']
            row_relationship_data['a_word'] = noun_words[i - 1]['word']
            row_relationship_data['b_index'] = index
            row_relationship_data['b_word'] = word
            relationship_data.append(row_relationship_data)
            row_relationship_data = {}
            counter += 1

        if (index - temp_index) != 1 or (i + 1) == len(noun_words):
            if counter > 2:
                i_head = i - counter if (index - temp_index) != 1 else i - counter + 1
                i_tail = (i - 1) if (index - temp_index) != 1 else i
                row_relationship_data['a_index'] = noun_words[i_head]['index']
                row_relationship_data['a_word'] = noun_words[i_head]['word']
                row_relationship_data['b_index'] = noun_words[i_tail]['index']
                row_relationship_data['b_word'] = noun_words[i_tail]['word']
                relationship_data.append(row_relationship_data)
                counter = 1

            elif counter == 2:
                counter = 1
        temp_index = index

    params["batch"] = relationship_data

    # 将关系数据插入neo4j
    cypher = """
        unwind $batch as row
        match (a:%s) where a.index = row.a_index and a.word = row.a_word 
        match (b:%s) where b.index = row.b_index and b.word = row.b_word
        create (a)-[r:NOUN_PHRASE]->(b)
    """ % (article, article)
    handler.cypher_executor(cypher, params=params)
