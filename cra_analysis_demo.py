# coding=utf-8
from py2neo import Graph
from conf import *
from concurrent.futures import ThreadPoolExecutor, wait
import analysis.cra as cra
import cx_Oracle
import logging
import math
import os


def cal_betweenness_centrality(neo4j, cursor, num):
    _article = "D%07d" % num
    print('[%s] start to insert into db.' % _article)
    _bc = cra.betweenness_centrality(neo4j, _article)
    for _b in _bc:
        _word = '%s' % _b['word']
        # print(_b['centrality'])
        sql = 'insert into CRA_BETWEENNESS_CENTRALITY ' \
              'values (CRA_BC_ID_SEQ.nextval, \'%s\', \'%s\', %.18f, %d, \'%s\')' \
              % (_article, _word, _b['centrality'], _b['index'], _b['flag'])
        cursor.execute(sql)
    print('[%s] is inserted into db.' % _article)


def cal_all_nodes_betweenness_centrality(neo4j, orcl, total_loop_times, groups=50, max_workers=10):
    logger = logging.getLogger("ANALYSIS_PROGRAM")
    logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler("logs/cra_analysis.log")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    group_loop_times = math.ceil(total_loop_times / groups)
    total = 0
    counter = 0
    # pool = ThreadPoolExecutor(max_workers=max_workers)
    for i in range(0, groups):
        logger.info("第%d组开始分析" % i)
        if counter >= total_loop_times:
            logger.info("全部完成")
            break
        else:
            _total = total + group_loop_times
            if _total >= total_loop_times:
                group_loop_times = total_loop_times - total
            total = total + group_loop_times

        cursor = orcl.cursor()
        # futures = []
        for l in range(0, group_loop_times):
            counter += 1
            # futures.append(pool.submit(cal_betweenness_centrality, neo4j, cursor, counter))
            cal_betweenness_centrality(neo4j, cursor, counter)
        # wait(futures)
        orcl.commit()
        cursor.close()
        print('>>>>>>> [GROUP %d] done.' % (i + 1))
        logger.info("第%d组完成分析并存入数据库" % i)


os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
neo4j_cra = Graph(bolt=neo4j_cra_blot, host=neo4j_cra_host, user=neo4j_cra_db, password=neo4j_cra_psw)
with cx_Oracle.connect('cra/cra@192.168.199.130:1521/orcl') as orcl_cra:
    cal_all_nodes_betweenness_centrality(neo4j_cra, orcl_cra, 48480, groups=50, max_workers=1)
# for i in range(1, 21):
#     print("%03d" % i)
# bc = cra.betweenness_centrality(neo4j_cra, "D0000020")
# cursor = orcl_db.cursor()
# cursor.execute("select * from CRA_BETWEENNESS_CENTRALITY")
# data = cursor.fetchall()
# cursor.close()
# orcl_db.close()
