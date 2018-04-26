import jieba.posseg as pseg
import re


def select(string):
    """
    将输入的文本转换为名词词组
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

    counter = 0
    for l in words_with_mark:
        counter += 1
        if re.match(reg, l.flag):
            noun_words.append({
                'word': l.word,
                'flag': l.flag,
                'index': counter
            })
    return noun_words, words_with_mark


def load_text(path="datasets/default.txt"):
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


def text_parser_for_sohu_dataset(text):
    """
    文本解析器，用于搜狐比赛数据集
    :param text: 原始文本
    :return: 结构化数据字典
    """
    text_array = text.split('\t')
    return {
        "article": text_array[0],
        "content": text_array[1],
        "pics": text_array[2]
    }
    # reg = '(D\d{7})(.*?)((P\d{7}\.JPEG.*\.JPEG)|(NULL))'
    # match_iteration = re.finditer(reg, text)
    structure_text = []
    # if match_iteration:
    #     for match in match_iteration:
    #         article = match.group(1)
    #         content = match.group(2)
    #         pics = match.group(3)
    #         structure_text.append({
    #             "article": article,
    #             "content": content,
    #             "pics": pics
    #         })
    # else:
    #     print("The data cannot be parsed by embedded regex expression.")
    # return structure_text
