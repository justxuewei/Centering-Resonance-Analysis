import platform
import jieba.posseg as pseg
import re


def select(string, debug=False):
    """
    将输入的文本转换为名词词组
    :type debug: 调试模式
    :param string: 文本
    :return: 元祖，(名词词组, 带词性的词组)
    """
    words_with_mark = pseg.cut(string)
    noun_words = []

    # 名词相关词性标记
    # 参照 https://blog.csdn.net/li_31415/article/details/48660073
    # 名词类的正则 -> n.+
    # n -- 名词           nr -- 人名                nr1 -- 汉语姓氏
    # nr2 -- 汉语名字      nrj -- 日语人名           ns -- 地名
    # nsf -- 音译地名      nt -- 机构团体名          nz -- 其它专名
    # nl -- 名词性惯用语   ng -- 名词性语素
    # ============================================================
    # 其他与名词有关的正则 -> (vn)|(an)
    # 动名词 vn (如工作)
    # 名形词 an
    # ============================================================
    # 总正则表达式 -> ^(n.+)|(vn)|(an)$
    reg = '^(n.*)|(vn)|(an)$'

    for l in words_with_mark:
        print('%s %s' % (l.word, l.flag))
        if re.match(reg, l.flag):
            if debug:
                noun_words.append(l.word + ": " + l.flag)
            else:
                noun_words.append(l.word)
    return noun_words, words_with_mark


def load_text(path="text/default.txt"):
    """
    文本输入，输入的文本编码格式为utf-8
    :param path: 路径，默认text/default.txt
    :return: 文本
    """
    file = open(path, encoding='utf-8')

    try:
        text = file.read()
    finally:
        file.close()

    return text
