### Centering Resonance Analysis (CRA)

![](https://img.shields.io/badge/version-v0.0.1-brightgreen.svg)

这个项目是对Centering Resonance Analysis(CRA)的实现，其主要针对于中文语言的实现。

目前打算将CRA应用到假新闻检测中，但是我认为CRA还有一些地方不足以支撑其对假新闻的辨别：

- 缺乏对数量词的分析。假新闻中对于数据的造假是很普遍的，但是原始的CRA方法仅仅是通过连接名词短语来实现的。

# 实现效果

文章摘自[习近平致信祝贺首届数字中国建设峰会开幕](http://www.xinhuanet.com/2018-04/22/c_1122722221.htm)，最终效果图如下：

![](https://res.niuxuewei.com/group.svg)

参考资料

- Corman, S. R., Kuhn, T., McPhee, R., and K. Dooley (2002). Studying Complex Discursive Systems: Centering Resonance Analysis of Communication. Human Communication Research, 28(2), 157-206.
- [Visone - CRA](http://visone.info/wiki/index.php/CRA)
- [jieba中文分词](https://github.com/fxsjy/jieba)

---

本项目使用Neo4j作为图数据库存储单词与单词之间的关系，所以需要指定图数据库的uri、dbname和password。

所以在使用时需要创建conf.py，然后添加一些相关配置

- neo4j_cra_uri: neo4j的uri
- neo4j_cra_db: neo4j的数据库名
- neo4j_cra_psw: neo4j的密码

但是目前仍然存在一些问题

- 在节点合并时效率过低
- neo4j存储时必须是有向图，虽然查询时可以忽略，但是对于查看数据图有很大的影响

---

联系我

- E-Mail: a@niuxuewei.com
- 个人主页: http://www.niuxuewei.com
