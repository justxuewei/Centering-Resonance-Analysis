# coding=utf-8
# ===========================================
# 本示例使用多线程技术加速CRA网络建立以及计算bc过程
# 运行环境
# - CPU: Intel(R) Core(TM) i7-6700 CPU @ 3.40GHz
# - RAM: 16.0 GB
# - OS: Windows 10 x64
# 运行时间
# - 48000+条数据CRA网络建立 6h(max_workers=50)
# - 计算BC 7h(max_workers=1)
# ===========================================
# author: MrN1u<a@niuxuewei.com>
import textprocessing.pre_processing as prepcs
import textprocessing.save_to_neo4j as stn
from py2neo import Graph, NodeSelector
from conf import *
from concurrent.futures import ThreadPoolExecutor, wait
import logging
import cx_Oracle
import gc
import os
import analysis.cra as cra


def insert(neo4j, cont):
    article = cont["article"]
    content = cont["content"]
    print('>>>>>>>>> [%s] is on processing...' % article)
    noun_words, all_words = prepcs.select(content)
    stn.create_nodes(neo4j, article, noun_words)
    stn.create_relationship_by_np(neo4j, article, noun_words)
    stn.create_relationship_by_nanp(neo4j, article, noun_words)
    stn.merge_same_word_nodes(neo4j, article, noun_words)
    print('[%s]: done!' % article)


def cra_analysis(neo4j, article, cur, db, sel, lg):
    print('[%s]: analysis...' % article)
    bc = cra.betweenness_centrality(neo4j, article, sel, lg)
    if not bc:
        return None
    for b in bc:
        _word = '%s' % b['word']
        # print(_b['centrality'])
        sql = 'insert into CRA_BETWEENNESS_CENTRALITY ' \
              'values (CRA_BC_ID_SEQ.nextval, \'%s\', \'%s\', %.18f, %d, \'%s\')' \
              % (article, _word, b['centrality'], b['index'], b['flag'])
        cur.execute(sql)
        db.commit()


if __name__ == '__main__':
    os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
    # logger
    logger = logging.getLogger("INSERT_AND_ANALYSIS_PROGRAM")
    logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler("logs/insert_and_analysis.log")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # neo4j handler
    neo4j_cra = Graph(bolt=neo4j_cra_blot, host=neo4j_cra_host, user=neo4j_cra_db, password=neo4j_cra_psw)
    pool = ThreadPoolExecutor(max_workers=50)

    # insert part
    for i in range(1, 11):
        logger.info("第%d组开始存入neo4j数据库" % i)
        # counter = 0
        futures = []

        file = open('./datasets/biendata/groups/News_info_train_filter_%d.txt' % i, encoding='utf-8')
        line = file.readline()

        while line:
            # print(line)
            text_dict = prepcs.text_parser_for_sohu_dataset(line)
            futures.append(pool.submit(insert, neo4j_cra, text_dict))
            line = file.readline()
        wait(futures)
        logger.info("第%d组存入neo4j数据库完成" % i)
        gc.collect()
    pool.shutdown()

    # calculate betweenness centrality and save to oracle db
    with cx_Oracle.connect('cra/cra@192.168.199.130:1521/orcl') as orcl_cra:
        pool = ThreadPoolExecutor(max_workers=2)
        selector = NodeSelector(neo4j_cra)
        for i in range(1, 11):
            futures = []
            logger.info("第%d组开始分析" % i)
            cursor = orcl_cra.cursor()
            file = open('./datasets/biendata/groups/News_info_train_filter_%d.txt' % i, encoding='utf-8')
            line = file.readline()
            while line:
                text_dict = prepcs.text_parser_for_sohu_dataset(line)
                # cra_analysis(neo4j_cra, text_dict['article'], cursor, orcl_cra, selector, logger)
                futures.append(pool.submit(cra_analysis, neo4j_cra, text_dict['article'], cursor,
                                           orcl_cra, selector, logger))
                line = file.readline()
            wait(futures)
            file.close()
            logger.info("第%d组分析结束" % i)
        pool.shutdown()
