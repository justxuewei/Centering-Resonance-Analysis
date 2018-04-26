from py2neo import Node, Relationship, NodeSelector


def create_nodes(neo4j, article, noun_words):
    """
    根据名词词组创建节点(node)
    :param neo4j: neo4j handler
    :param article: 文章标题
    :param noun_words: 名词词组
    :return: none
    """
    print('[%s]: create_nodes...' % article)
    tx = neo4j.begin()
    for i, noun_word in enumerate(noun_words):
        word = noun_word['word']
        flag = noun_word['flag']
        index = noun_word['index']
        tx.create(Node(article, word=word, index=index, flag=flag))

    tx.commit()


def create_relationship_by_np(neo4j, article, noun_words):
    """
    根据名词短语(np)创建关系
    创建的策略是相邻名词短语相连，如果相连接节点大于等于3则节点首尾相连
    :param neo4j: neo4j handler
    :param article: 文章标题
    :param noun_words: 名词词组
    :return: none
    """
    print('[%s]: create_relationship_by_np...' % article)
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
    neo4j.run(cypher, parameters=params)


def create_relationship_by_nanp(neo4j, article, noun_words):
    """
    创建不相邻名词(not adjacent noun phrase)的关系
    :param neo4j: neo4j handler
    :param article: 文章标题
    :param noun_words: 名词词组
    :return: none
    """
    print('[%s]: create_relationship_by_nanp...' % article)
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
    neo4j.run(cypher, parameters=params)


def merge_same_word_nodes(neo4j, article, noun_words):
    """
    合并相同节点并保留原始关系
    :param neo4j: neo4j handler
    :param article: 文章标题
    :param noun_words: 名词词组
    :return: none
    """
    print('[%s]: merge_same_word_nodes...' % article)
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

            # 获取除最后一个节点
            nodes = neo4j.data(match_cypher)
            batch_node_indexs = []
            for n in nodes:
                _index = n['b']['index']
                _relationship_cypher = 'match p=(a:%s)--(b:%s) where a.index = %d and b.index = %d return p' % (
                    article, article, _index, last_idx)
                # print(_relationship_cypher)
                _relationship = neo4j.data(_relationship_cypher)
                # print(_relationship)
                if not _relationship:
                    batch_node_indexs.append({'index': _index})
            neo4j.run(delete_cypher)

            create_relationship_cypher = """
                unwind $batch as row
                match (a:%s) where a.index = %d
                match (b:%s) where b.index = row.index
                create (a)-[r:MNP]->(b)
            """ % (article, last_idx, article)
            neo4j.run(create_relationship_cypher, parameters={"batch": batch_node_indexs})
    # print('[%s]: insert done!' % article)
