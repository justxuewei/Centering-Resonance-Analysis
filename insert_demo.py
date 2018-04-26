import textprocessing.pre_processing as prepcs
import textprocessing.save_to_neo4j as stn
from py2neo import Graph
from conf import *
from concurrent.futures import ThreadPoolExecutor, wait
import logging
import gc


def init(neo4j, cont):
    article = cont["article"]
    content = cont["content"]
    print('>>>>>>>>> [%s] is on processing...' % article)
    noun_words, all_words = prepcs.select(content)
    stn.create_nodes(neo4j, article, noun_words)
    stn.create_relationship_by_np(neo4j, article, noun_words)
    stn.create_relationship_by_nanp(neo4j, article, noun_words)
    stn.merge_same_word_nodes(neo4j, article, noun_words)


def insert_into_graph_db(neo4j, text_path, max_workers=10, delete_all=False):
    # 是否清空结果
    if delete_all:
        neo4j.delete_all()
    text = prepcs.load_text(path=text_path)
    structure_text = prepcs.text_parser_for_sohu_dataset(text)

    pool = ThreadPoolExecutor(max_workers=max_workers)
    futures = []
    for t in structure_text:
        futures.append(pool.submit(init, neo4j, t))
    wait(futures)

    print('data has been inserted into graph database')


# if __name__ == '__main__':
#     logger = logging.getLogger("INSERT_PROGRAM")
#     logger.setLevel(level=logging.INFO)
#     handler = logging.FileHandler("logs/save_to_db.log")
#     handler.setLevel(logging.INFO)
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#
#     neo4j_cra = Graph(bolt=neo4j_cra_blot, host=neo4j_cra_host, user=neo4j_cra_db, password="wqnmlgb")
#
#     # neo4j_cra.delete_all()
#
#     for i in range(1, 11):
#         logger.info("第%d组开始存入数据库" % i)
#         insert_into_graph_db(neo4j_cra, './datasets/biendata/groups/News_info_train_filter_%d.txt' % i,
#                              max_workers=50, delete_all=False)
#         logger.info("第%d组存入数据库完成" % i)
#         gc.collect()
