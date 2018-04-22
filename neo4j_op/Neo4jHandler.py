class Neo4jHandler:

    def __init__(self, driver):
        self.driver = driver

    def __repr__(self):
        """
        对本类的文字描述
        :return:
        """
        printer = 'Neo4j driver: "{0}"'.format(self.driver)
        return printer

    def cypher_executor(self, cypher, params=None):
        """
        执行neo4j的cypher命令
        :type params: 参数
        :param cypher: 命令
        :return: none
        """
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                tx.run(cypher, parameters=params)

    def delete_nodes_by_label(self, label):
        """
        根据label清楚全部节点
        :param label: 节点
        :return: none
        """
        cypher = "match (l: %s) detach delete l" % label
        self.cypher_executor(cypher)
