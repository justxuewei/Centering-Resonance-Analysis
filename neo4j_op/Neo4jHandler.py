import re
import json


class Neo4jHandler:

    def __init__(self, driver):
        self.driver = driver

    def __repr__(self):
        """
        对本类的文字描述
        :return: none
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

    def dict_reader(self, cypher):
        """
        执行cypher命令读数据，以dict方式返回数据
        :param cypher: 命令
        :return: 返回数据的结构为 [{...}, {...}, ...]
        """
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                data = []
                for record in tx.run(cypher).records():
                    record_str = str(record)
                    reg = 'properties=(.+)>>$'
                    m = re.search(reg, record_str)
                    if m:
                        json_str = m.group(1)
                        json_str = json_str.replace("'", '"')
                        item = json.loads(json_str)
                        print(item)
                        data.append(item)
                return data

    def list_reader(self, cypher, keys):
        """
        执行cypher命令读数据，以list方式返回数据，可以通过keys控制获取的列
        :param cypher: 命令
        :param keys: 执行命令后返回的列
        :return: 返回数据的结构为 [[...], [...], ...].
        """
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                data = []
                result = tx.run(cypher)
                for record in result:
                    rows = []
                    for key in keys:
                        rows.append(record[key])
                    data.append(rows)
                return data

    def dict_reader_opted(self, cypher, keys=None):
        """
        dict_reader()方法的优化，如果keys为None则与dict_reader()相同
        如果不为None则根据keys过滤列
        :param cypher: 命令
        :param keys: 执行命令后返回的列
        :return: 返回数据的结构为 [{...}, {...}, ...]
        """
        if not keys:
            return self.dict_reader(cypher)
        else:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    data = []
                    result = tx.run(cypher)
                    for record in result:
                        item = {}
                        for key in keys:
                            item.update({key: record[key]})
                        data.append(item)
                    return data
