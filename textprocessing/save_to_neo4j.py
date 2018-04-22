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


def create_relationship_by_np(handler, article, noun_words):
    """
    根据名词短语(np)创建关系
    创建的策略是相邻名词短语相连，如果相连接节点大于等于3则节点首尾相连
    :param handler: neo4j handler
    :param article: 文章标题
    :param noun_words: 名词词组
    :return: none
    """
    counter = 1
    params = {}
    relationship_data = []
    for i, noun_word in enumerate(noun_words):
        row_relationship_data = {}
        word = noun_word['word']
        index = noun_word['index']
        last_index = noun_words[i - 1]['index']

        if (index - last_index) == 1:
            row_relationship_data['a_index'] = last_index
            row_relationship_data['b_index'] = index
            relationship_data.append(row_relationship_data)
            row_relationship_data = {}
            counter += 1

        if (index - last_index) != 1 or (i + 1) == len(noun_words):
            if counter > 2:
                i_head = i - counter if (index - last_index) != 1 else i - counter + 1
                i_tail = (i - 1) if (index - last_index) != 1 else i
                row_relationship_data['a_index'] = noun_words[i_head]['index']
                row_relationship_data['b_index'] = noun_words[i_tail]['index']
                relationship_data.append(row_relationship_data)
                counter = 1

            elif counter == 2:
                counter = 1

    params["batch"] = relationship_data

    # 将关系数据插入neo4j
    cypher = """
        unwind $batch as row
        match (a:%s) where a.index = row.a_index
        match (b:%s) where b.index = row.b_index
        create (a)-[r:NP]->(b)
    """ % (article, article)
    handler.cypher_executor(cypher, params=params)


def create_relationship_by_nanp(handler, article, noun_words):
    """
    创建不相邻名词(not adjacent noun phrase)的关系
    :param handler: neo4j handler
    :param article: 文章标题
    :param noun_words: 名词词组
    :return: none
    """
    params = {}
    relationship_data = []
    for i, noun_word in enumerate(noun_words):
        # 略过第1个
        # 因为它不可能产生关系
        # 而且会造成索引越界
        if i == 0:
            continue

        last_index = noun_words[i - 1]['index']
        index = noun_word['index']
        if index - last_index > 1:
            row_relationship_data = {'a_index': last_index, 'b_index': index}
            relationship_data.append(row_relationship_data)

    params['batch'] = relationship_data

    # 将关系数据插入neo4j
    cypher = """
            unwind $batch as row
            match (a:%s) where a.index = row.a_index
            match (b:%s) where b.index = row.b_index
            create (a)-[r:NANP]->(b)
        """ % (article, article)
    handler.cypher_executor(cypher, params=params)


def merge_same_word_nodes(handler, article, noun_words):
    """
    合并相同节点并保留原始关系
    :param handler: neo4j handler
    :param article: 文章标题
    :param noun_words: 名词词组
    :return: none
    """
    word_times = {}
    for noun_word in noun_words:
        word = noun_word['word']
        index = noun_word['index']
        if word not in word_times:
            word_times[word] = [index]
        else:
            word_times[word].append(index)

    for word in word_times:
        idxs = word_times[word]
        if len(idxs) > 1:
            first_idx = word_times[word][0]
            last_idx = word_times[word][len(word_times[word]) - 1]
            # print("last_idx: " + str(last_idx))
            match_cypher = 'match (a:%s)--(b) where' % article
            delete_cypher = 'match (a:%s) where' % article
            for idx in idxs:
                if idx == last_idx:
                    break
                match_cypher += ' a.index = %d' % idx if idx == first_idx else ' or a.index = %d' % idx
                delete_cypher += ' a.index = %d' % idx if idx == first_idx else ' or a.index = %d' % idx
                # print(idx)
            match_cypher += ' return distinct b'
            delete_cypher += ' detach delete a'

            # print('cypher: ' + match_cypher)
            # print(delete_cypher)

            nodes = handler.dict_reader(match_cypher)
            print(nodes)
            handler.cypher_executor(delete_cypher)

            create_relationship_cypher = """
                unwind $batch as row
                match (a:%s) where a.index = %d
                match (b:%s) where b.index = row.index
                create (a)-[r:MNP]->(b)
            """ % (article, last_idx, article)
            handler.cypher_executor(create_relationship_cypher, params={"batch": nodes})
