### 关于此项目

这个项目是对Centering Resonance Analysis(CRA)的实现，其主要针对于中文语言的实现。

目前打算将CRA应用到假新闻检测中，但是我认为CRA还有一些地方不足以支撑其对假新闻的辨别：

- 缺乏对数量词的分析。假新闻中对于数据的造假是很普遍的，但是原始的CRA方法仅仅是通过连接名词短语来实现的。

参考资料

- Corman, S. R., Kuhn, T., McPhee, R., and K. Dooley (2002). Studying Complex Discursive Systems: Centering Resonance Analysis of Communication. Human Communication Research, 28(2), 157-206.
- [Visone - CRA](http://visone.info/wiki/index.php/CRA)
- [jieba中文分词](https://github.com/fxsjy/jieba)

---

本项目使用Neo4j作为图数据库存储单词与单词之间的关系，所以需要指定图数据库的uri、dbname和password。

所以在使用时需要创建conf.py，然后添加一些相关常亮:

- neo4j_cra_uri: neo4j的uri
- neo4j_cra_db: neo4j的数据库名
- neo4j_cra_psw: neo4j的密码

---

联系我

- E-Mail: a@niuxuewei.com
- 个人主页: http://www.niuxuewei.com
