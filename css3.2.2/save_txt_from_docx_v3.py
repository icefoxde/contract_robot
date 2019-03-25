# 函数名：save_txt_from_docx_v3
# 输入：用户上传的合同文档 一篇
# 输出：提取转让方 受让方合同要素的所有句子并分别保存为txt
# 说明：此函数将用户上传的docx文档从中提取转让方 受让方合同要素
# ---将所有句子保存为txt文件后，对每个句子计算tfidf 转化成向量形式用lr分类器预测

import os
import re
from docx import Document

basepath = os.path.dirname(__file__)
txt_save_path = os.path.join(basepath, 'static/LR_model_bow_txt/save_txt_from_docx/')
# txt_save_path = 'D:/jupyter_datafile/contract_extract/save_txt_from_docx/'


element_name_dict = {
    '转让方':['转让方','甲方'],
    '受让方': ['受让方', '乙方']
}



#输入一个合同文档 一类合同要素名称
#输出该文档中合同要素的所有句子
# 说明：此函数供内部其他函数调用
def get_one_element_all_sentences(docx_file_path,element_name):
    document = Document(docx_file_path)
    element_name_list = element_name_dict[element_name]
    one_element_all_sentences = []
    one_element_all_sentences_set = set()
    for element_name_i in element_name_list:
        compile_element = re.compile(element_name_i)
        for i_para in document.paragraphs:
            i_para_text = i_para.text.strip()
            i_para_text = ''.join(i_para_text.split())
            re_match_all_list = compile_element.findall(i_para_text)
            if re_match_all_list != []:
                i_para_all_sentences = get_i_para_sentences(i_para_text,element_name_i)
                for i_sentence in i_para_all_sentences:
                    one_element_all_sentences_set.add(i_sentence)
    for item in one_element_all_sentences_set:
        one_element_all_sentences.append(item)

    return one_element_all_sentences

# 输入一个段落文本 一个合同要素名称所对应的一个识别字段
# 输出合同要素所在的句子
# 函数说明：该函数供内部函数调用（get_one_element_all_sentences调用此函数）
def get_i_para_sentences(i_para_text,element_name_i):
    paras_len = len(i_para_text)
    element_len = len(element_name_i)
    start_loc = []
    # 合同要素起始点
    # 包括合同要素句子起始点
    # 包括合同要素句子结束点
    if element_len == 2:
        start_loc = []
        for i in range(paras_len):
            if i + 1 < paras_len and i_para_text[i] == element_name_i[0] and i_para_text[i + 1] == element_name_i[1]:
                start_loc.append(i)

    if element_len == 3:
        start_loc = []
        for i in range(paras_len):
            if i + 2 < paras_len and i_para_text[i] == element_name_i[0] and i_para_text[i + 1] == element_name_i[1] and \
                    i_para_text[i + 2] == element_name_i[2]:
                start_loc.append(i)

    if element_len == 4:
        start_loc = []
        for i in range(paras_len):
            if i + 3 < paras_len and i_para_text[i] == element_name_i[0] and i_para_text[i + 1] == element_name_i[1] and \
                    i_para_text[i + 2] == element_name_i[2] and i_para_text[i + 3] == element_name_i[3]:
                start_loc.append(i)

    if element_len == 5:
        start_loc = []
        for i in range(paras_len):
            if i + 4 < paras_len and i_para_text[i] == element_name_i[0] and i_para_text[i + 1] == element_name_i[1] and \
                    i_para_text[i + 2] == element_name_i[2] and i_para_text[i + 3] == element_name_i[3] and i_para_text[
                i + 4] == element_name_i[4]:
                start_loc.append(i)

    if element_len == 6:
        start_loc = []
        for i in range(paras_len):
            if i + 5 < paras_len and i_para_text[i] == element_name_i[0] and i_para_text[i + 1] == element_name_i[1] and \
                    i_para_text[i + 2] == element_name_i[2] and i_para_text[i + 3] == element_name_i[3] and i_para_text[
                i + 4] == element_name_i[4] and i_para_text[i + 5] == element_name_i[5]:
                start_loc.append(i)

    i_para_all_sentences = []
    for i_loc in start_loc:
        forward_loc = i_loc
        backward_loc = i_loc

        while (forward_loc > 0):
            if i_para_text[forward_loc] == '。' or i_para_text[forward_loc] == '，' or i_para_text[forward_loc] == '；' or \
                    i_para_text[forward_loc] == ',' or i_para_text[forward_loc] == '.' or i_para_text[
                forward_loc] == ';':
                break
            else:
                forward_loc -= 1

        while (backward_loc < paras_len):
            if i_para_text[backward_loc] == '。' or i_para_text[backward_loc] == '，' or i_para_text[
                backward_loc] == '；' or i_para_text[backward_loc] == ',' or i_para_text[backward_loc] == '.' or \
                    i_para_text[backward_loc] == ';':
                break
            else:
                backward_loc += 1

        if forward_loc != 0:
            forward_loc += 1
        i_line = i_para_text[forward_loc:backward_loc]
        string = ''.join(i_line)
        i_para_all_sentences.append(string)

    return i_para_all_sentences


# 此函数供外部函数调用
# 函数说明：外部函数通过调用此函数，对用户输入的一篇文档，
# 可将文档中包括的转让方、受让方合同要素的所有句子保存为txt文件
# 实际使用中需要将txt文件的保存路径更改为项目static文件夹路径
def save_txt_from_docx(docx_file_path):
    for item in element_name_dict:
        all_sentences = get_one_element_all_sentences(docx_file_path,item)
        txt_file_path = txt_save_path + item + 'save_txt_from_docx.txt'
        with open(txt_file_path,'w',encoding='utf-8') as f:
            for i_sentence in all_sentences:
                f.write(i_sentence)
                f.write('\n')



if __name__ == '__main__':
    # all_sentences = get_one_element_all_sentences('D:/jupyter_datafile/contract_extract/债权转让协议_带标注2.docx','受让方')
    # 外部函数调用说明：调用save_txt_from_docx 输入参数为文档路径 输出结果为合同要素所有句子的txt文档
    save_txt_from_docx('D:/jupyter_datafile/contract_extract/HR债权转让.docx')


