# 函数名：element_extract_from_txtanddocx_v3
# 输入：用户输入的一篇合同文档
# 输出：预定义的29类合同要素 其中转让方、受让方采用先提取文档中包括的所有句子

import os
import re
import math
import jieba
import numpy as np
from docx import Document
from sklearn.externals import joblib
from save_txt_from_docx_v3 import save_txt_from_docx

basepath = os.path.dirname(__file__)

txt_save_path = os.path.join(basepath, 'static/LR_model_bow_txt/save_txt_from_docx/')
txt_file_name_list = os.listdir(txt_save_path)
txt_file_path_list = []
for txt_file_name_i in txt_file_name_list:
    txt_file_path_i = txt_save_path + txt_file_name_i
    txt_file_path_list.append(txt_file_path_i)

z_txt_bow_file_path = os.path.join(basepath,'static/LR_model_bow_txt/转让方_bow_2018.9.6_.txt')
s_txt_bow_file_path = os.path.join(basepath,'static/LR_model_bow_txt/受让方_bow_2018.9.6_.txt')



z_LR_model_file_path = os.path.join(basepath,'static/LR_model_bow_txt/转让方_LR_model_2018.9.6_.model')
s_LR_model_file_path = os.path.join(basepath,'static/LR_model_bow_txt/受让方_LR_model_2018.9.6_.model')


# 用户输入一篇文档，先对转让方、受让方合同要素所有句子进行计算tfidf用分类器预测输出
# 再对27类合同要素，每一类单独用规则正则匹配方式进行识别输出
def output_elements_from_docx(docx_file_path):
    # 定义dict保存提取的合同要素
    elements_dict = {
        '合同编号':'',
        '业务类型': '',
        '协议签订日期': '',
        '协议签订地点': '',
        '转让方': '',
        '受让方': '',
        '债务方': '',
        '转让方负责人': '',
        '受让方法定代表人': '',
        '债务方负责人': '',
        '转让方住所': '',
        '受让方住所': '',
        '债务方住所': '',
        '账面本金余额': '',
        '利息': '',
        '其他债权': '',
        '整体债权': '',
        '转让价款': '',
        '债权金额': '',
        '违约金': '',
        '基准日': '',
        '本息总额': '',
        '本金余额': '',
        '欠息': '',
        '转让方开户银行': '',
        '转让方户名': '',
        '转让方账户': '',
        '交易保证金详情': ''
    }


    # 先提取转让方、受让方 合同要素
    save_txt_from_docx(docx_file_path)

    for item in txt_file_path_list:
        element_name = item[-25:-22]
        all_sentences = []
        with open(item,'r',encoding='utf-8') as f:
            all_lines = f.readlines()
        for i_line in all_lines:
            sentence = i_line[:-1]
            all_sentences.append(sentence)

        if element_name == '转让方':
            # print('转让方')
            # 转让方维度：1338
            
            all_sentences_vector = sentences_to_vector(z_txt_bow_file_path,all_sentences)
            all_sentences_array = np.asarray(all_sentences_vector)
            clf = joblib.load(z_LR_model_file_path)
            res = clf.predict_proba(all_sentences_array)

            loc_list = list(range(len(all_sentences)))
            res_loc = np.column_stack((res,loc_list))

            b = np.argsort(res_loc[:, 0])
            res_loc = res_loc[b]
            string = all_sentences[int(res_loc[0][2])]
            k_s = 0
            for i in range(len(string)):
                k_s = i
                if string[i] == '：' or string[i] == ':':
                    break
            start_loc = k_s+1

            k_e = len(string)-1
            for i in range(len(string)):
                if i+1 < len(string) and string[i] == '公' and string[i+1] == '司':
                    k_e = i
            end_loc = k_e + 1

            z_string = string[start_loc:end_loc+1]

            elements_dict['转让方'] = z_string



        if element_name == '受让方':
            # print('受让方')
            # 受让方维度：1154
            all_sentences_vector = sentences_to_vector(s_txt_bow_file_path,all_sentences)
            all_sentences_array = np.asarray(all_sentences_vector)
            clf = joblib.load(s_LR_model_file_path)
            res = clf.predict_proba(all_sentences_array)

            loc_list = list(range(len(all_sentences)))
            res_loc = np.column_stack((res, loc_list))

            b = np.argsort(res_loc[:, 0])
            res_loc = res_loc[b]
            string = all_sentences[int(res_loc[0][2])]
            k_s = 0
            for i in range(len(string)):
                k_s = i
                if string[i] == '：' or string[i] == ':':
                    break
            start_loc = k_s + 1

            k_e = len(string) - 1
            for i in range(len(string)):
                if i + 1 < len(string) and string[i] == '公' and string[i + 1] == '司':
                    k_e = i
            end_loc = k_e + 1

            s_string = string[start_loc:end_loc + 1]
            elements_dict['受让方'] = s_string


    # 对剩下的27类合同要素进行正则匹配

    # 首先读取用户上传的文档 将文档段落存储为 list ['段落1 text','段落2 text','']
    docx_text_string_list = []
    document = Document(docx_file_path)
    for i_para in document.paragraphs:
        i_para_text = i_para.text.strip()
        i_para_text = ''.join(i_para_text.split())
        docx_text_string_list.append(i_para_text)


    # 定义27类合同要素 string

    # 合同编号
    contract_no = ''
    # 合同类型
    business_types = ''
    # 协议签订日期
    data_of_agreement = ''
    # 协议签订地点
    place_of_signing = ''
    # 债务方
    debator = ''
    # 转让方负责人
    transferor_responsible = ''
    # 受让方法定代表人
    recipie_legal = ''
    # 债务方负责人
    debator_responsible = ''
    # 转让方住所
    transferor_location = ''
    # 受让方住所
    recipie_location = ''
    # 债务方住所
    debator_location = ''
    # 账面本金余额
    account_remain_money = ''
    account_remain_money_list = ['','']
    # 利息
    interest = ''
    interest_list = ['','']
    # 其他债权
    other_creditors = ''
    other_creditors_list = ['','']
    # 整体债权
    total_creditors = ''
    total_creditors_list = ['','']
    # 转让价款
    transfer_price = ''
    transfer_price_list = ['','']
    # 债权金额
    creditor_money = ''
    creditor_money_list = ['','']
    # 违约金
    breach_of_contract = ''
    breach_of_contract_list = ['','']
    # 基准日
    base_date = ''
    # 本息总额
    total_price_and_interest = ''
    total_price_and_interest_list = ['','']
    # 本金余额
    pricipal_remain = ''
    pricipal_remain_list = ['','']
    # 欠息
    debit_interest = ''
    debit_interest_list = ['','']
    # 转让方开户银行
    transferor_bank_account = ''
    # 转让方户名
    transferor_name = ''
    # 转让方账户
    transferor_account = ''
    # 交易保证金详情
    trade_margin_details = ''

    docx_text_list_lens = len(docx_text_string_list)
    min_space = 1000
    min_space_interst = 1000
    min_space_oc = 1000
    min_space_tc = 1000
    min_lens_tp = 1000
    min_lens_cm = 1000
    min_lens_bc = 120
    max_lens_bd = 0
    min_lens_d = 1000
    max_lens_da = 1000
    max_lens_ps = 1000
    max_lens_bt = 1000
    for i_line_num in range(docx_text_list_lens):
        string = docx_text_string_list[i_line_num]
        string_lens = len(string)
        
        # 提取合同编号
        for i in range(string_lens):
            if (i+2 < string_lens and string[i] == '编' and string[i+1] == '号' and (string[i+2] == '：' or string[i+2] == ':') and string[-1] == '号'):
                if contract_no == '':
                    contract_no = string
                    break

        # 提取合同类型
        for i in range(string_lens):
            if string[-1] == '议' and string[-2] == '协':
                if business_types == '':
                    business_types = string

        # 提取协议签订日期
        for i in range(string_lens):
            if i+6<string_lens and string[i] == '协' and string[i+1] == '议' and string[i+2] == '签' and string[i+3] == '订' and string[i+4] == '日' and string[i+5] == '期' and (string[i+6] == '：' or string[i+6] == ':'):
                if i < max_lens_da:
                    max_lens_da = i
                    data_of_agreement = string
                    break

        # 提取协议签订地点
        for i in range(string_lens):
            if i+6<string_lens and string[i] == '协' and string[i+1] == '议' and string[i+2] == '签' and string[i+3] == '订' and string[i+4] == '地' and string[i+5] == '点' and (string[i+6] == '：' or string[i+6] == ':'):
                if i < max_lens_ps:
                    max_lens_ps = i
                    place_of_signing = string
                    break

        # 提取债务方
        for i in range(string_lens):
            if i+3<string_lens and string[i] == '债' and string[i+1] == '务' and (string[i+2] == '方' or string[i+2] == '人') and (string[i+3] == '：' or string[i+3] == ':'):
                if len(string) < min_lens_d:
                    min_lens_d = len(string)
                    debator = string
                    break

        # 提取转让方负责人/法定代表人
        for i in range(string_lens):
            if ( i+3<string_lens and string[i] == '负' and string[i+1] == '责' and (string[i+2] == '方' or string[i+2] == '人') and (string[i+3] == '：' or string[i+3] == ':') ) or (i+5<string_lens and string[i] == '法' and string[i+1] == '定' and string[i+2] == '代' and string[i+3] == '表' and string[i+4] == '人' and (string[i+5] == '：' or string[i+5] == ':') ):
                if i_line_num -1 >= 0:
                    string_pre = docx_text_string_list[i_line_num-1]
                    string_pre_lens = len(string_pre)
                    for k in range(string_pre_lens):
                        if (k+1<string_pre_lens and string_pre[k] == '甲' and string_pre[k+1] == '方') or (k+2<string_pre_lens and string_pre[k] == '转' and string_pre[k+1] == '让' and string_pre[k+2] == '方'):
                            transferor_responsible = string
                            break

        # 提取受让方负责人/法定代表人
        for i in range(string_lens):
            if ( i+3<string_lens and string[i] == '负' and string[i+1] == '责' and (string[i+2] == '方' or string[i+2] == '人') and (string[i+3] == '：' or string[i+3] == ':') ) or (i+5<string_lens and string[i] == '法' and string[i+1] == '定' and string[i+2] == '代' and string[i+3] == '表' and string[i+4] == '人' and (string[i+5] == '：' or string[i+5] == ':') ):
                if i_line_num -1 >= 0:
                    string_pre = docx_text_string_list[i_line_num-1]
                    string_pre_lens = len(string_pre)
                    for k in range(string_pre_lens):
                        if (k+1<string_pre_lens and string_pre[k] == '乙' and string_pre[k+1] == '方') or (k+2<string_pre_lens and string_pre[k] == '受' and string_pre[k+1] == '让' and string_pre[k+2] == '方'):
                            recipie_legal = string
                            break


        # 提取债务方负责人/法定代表人
        for i in range(string_lens):
            if ( i+3<string_lens and string[i] == '负' and string[i+1] == '责' and (string[i+2] == '方' or string[i+2] == '人') and (string[i+3] == '：' or string[i+3] == ':') ) or (i+5<string_lens and string[i] == '法' and string[i+1] == '定' and string[i+2] == '代' and string[i+3] == '表' and string[i+4] == '人' and (string[i+5] == '：' or string[i+5] == ':') ):
                if i_line_num -1 >= 0:
                    string_pre = docx_text_string_list[i_line_num-1]
                    string_pre_lens = len(string_pre)
                    for k in range(string_pre_lens):
                        if (k+1<string_pre_lens and string_pre[k] == '债' and string_pre[k+1] == '务'):
                            debator_responsible = string
                            break

        # 提取转让方住所
        for i in range(string_lens):
            if ( i+2<string_lens and string[i] == '住' and string[i+1] == '所' and (string[i+2] == '：' or string[i+2] == ':') ) or (i+2<string_lens and string[i] == '地' and string[i+1] == '址' and (string[i+2] == '：' or string[i+2] == ':') ):
                if i_line_num -2 >= 0:
                    string_pre = docx_text_string_list[i_line_num-2]
                    string_pre_lens = len(string_pre)
                    for k in range(string_pre_lens):
                        if (k+2<string_pre_lens and string_pre[k] == '转' and string_pre[k+1] == '让' and string_pre[k+2] == '方') or (k+1<string_pre_lens and string_pre[k] == '甲' and string_pre[k+1] == '方'):
                            transferor_location = string
                            break

        # 提取受让方住所
        for i in range(string_lens):
            if ( i+2<string_lens and string[i] == '住' and string[i+1] == '所' and (string[i+2] == '：' or string[i+2] == ':') ) or (i+2<string_lens and string[i] == '地' and string[i+1] == '址' and (string[i+2] == '：' or string[i+2] == ':') ):
                if i_line_num -2 >= 0:
                    string_pre = docx_text_string_list[i_line_num-2]
                    string_pre_lens = len(string_pre)
                    for k in range(string_pre_lens):
                        if (k+2<string_pre_lens and string_pre[k] == '受' and string_pre[k+1] == '让' and string_pre[k+2] == '方') or (k+1<string_pre_lens and string_pre[k] == '乙' and string_pre[k+1] == '方'):
                            recipie_location = string
                            break

        # 提取债务方住所
        for i in range(string_lens):
            if ( i+2<string_lens and string[i] == '住' and string[i+1] == '所' and (string[i+2] == '：' or string[i+2] == ':') ) or (i+2<string_lens and string[i] == '地' and string[i+1] == '址' and (string[i+2] == '：' or string[i+2] == ':') ):
                if i_line_num -2 >= 0:
                    string_pre = docx_text_string_list[i_line_num-2]
                    string_pre_lens = len(string_pre)
                    for k in range(string_pre_lens):
                        if (k+1<string_pre_lens and string_pre[k] == '债' and string_pre[k+1] == '务'):
                            debator_location = string
                            break

        # 提取账面本金余额
        for i in range(string_lens):
            if (i+5<string_lens and string[i] == '账' and string[i+1] == '面' and string[i+2] == '本' and string[i+3] == '金' and string[i+4] == '余' and string[i+5] == '额'):
                b_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                        break

                if b_loc != -1 and abs(b_loc - i) < min_space:
                    min_space = abs(b_loc - i)
                    account_remain_money = string
                    break

        # 提取利息
        for i in range(string_lens):
            if (i+2<string_lens and string[i] == '利' and string[i+1] == '息' and (string[i+2] == '为' or string[i+2] == '是')):
                b_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                        break

                if b_loc != -1 and abs(b_loc - i) < min_space_interst:
                    min_space_interst = abs(b_loc - i)
                    interest = string
                    break

        # 提取其他债权
        for i in range(string_lens):
            if (i+3<string_lens and string[i] == '其' and string[i+1] == '他' and string[i+2] == '债' and string[i+3] == '权'):
                b_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                        break

                if b_loc != -1 and abs(b_loc - i) < min_space_oc:
                    min_space_oc = abs(b_loc - i)
                    other_creditors = string
                    break


        # 提取整体债权
        for i in range(string_lens):
            if (i+3<string_lens and string[i] == '整' and string[i+1] == '体' and string[i+2] == '债' and string[i+3] == '权'):
                b_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                        break

                if b_loc != -1 and abs(b_loc - i) < min_space_tc:
                    min_space_tc = abs(b_loc - i)
                    total_creditors = string
                    break


        # 提取转让价款
        for i in range(string_lens):
            if (i + 3 < string_lens and string[i] == '转' and string[i + 1] == '让' and string[i + 2] == '价' and string[i + 3] == '款'):
                b_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                        break

                if b_loc != -1:
                    if len(string) < min_lens_tp:
                        min_lens_tp = len(string)
                        transfer_price = string


        # 提取债权金额
        for i in range(string_lens):
            if (i+3 <string_lens and string[i] == '债' and string[i+1] == '权' and string[i+2] == '金' and string[i+3] == '额'):
                b_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                        break

                if b_loc != -1:
                    if len(string) < min_lens_cm:
                        min_lens_cm = len(string)
                        creditor_money = string


        # 提取违约金
        for i in range(string_lens):
            if (i+2 <string_lens and string[i] == '违' and string[i+1] == '约' and string[i+2] == '金'):
                b_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                        break

                if b_loc != -1:
                    if len(string) < min_lens_bc:
                        min_lens_bc = len(string)
                        breach_of_contract = string


        # 提取基准日
        # 规则：基准日下标最小、包括年月日、string长度最长
        for i in range(string_lens):
            if (i+2<string_lens and string[i] == '基' and string[i+1] == '准' and string[i+2] == '日'):
                year_indicate = 0
                for y in range(string_lens):
                    if (string[y] == '年' or string[y] == '月'):
                        year_indicate = 1
                if year_indicate == 1:
                    if len(string) > max_lens_bd and i<30:
                        max_lens_bd = len(string)
                        base_date = string


        # 提取本息总额
        for i in range(string_lens):
            if (i+3<string_lens and string[i]=='本' and string[i+1]=='息' and string[i+2]=='总' and string[i+3]=='额'):
                b_loc = -1
                y_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                    if string[b] == '元':
                        y_loc = b
                if b_loc != -1 and y_loc != -1 and i<120:
                    total_price_and_interest = string
                    break


        # 提取本金余额
        for i in range(string_lens):
            if (i+3<string_lens and string[i]=='本' and string[i+1]=='金' and string[i+2]=='余' and string[i+3]=='额'):
                b_loc = -1
                y_loc = -1
                q_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                    if string[b] == '元':
                        y_loc = b
                    if string[b] == '欠' and string[b+1] == '息':
                        q_loc = b
                if b_loc != -1 and y_loc != -1 and q_loc != -1 and i<200:
                    pricipal_remain = string
                    break

        # 提取欠息
        for i in range(string_lens):
            if (i+1<string_lens and string[i]=='欠' and string[i+1]=='息'):
                b_loc = -1
                y_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                    if string[b] == '元':
                        y_loc = b
                if b_loc != -1 and y_loc != -1 and i<300:
                    debit_interest = string
                    break


        # 提取转让方开户银行
        for i in range(string_lens):
            if (i+4<string_lens and string[i] == '开' and string[i+1] == '户' and string[i+2] == '银' and string[i+3] == '行' and (string[i+4] == '：' or string[i+4] == ':')) or (i+3<string_lens and string[i] == '开' and string[i+1] == '户' and string[i+2] == '行' and (string[i+3] == '：' or string[i+3] == ':')):
                z_loc = -1
                if i_line_num -1 >= 0:
                    string_pre = docx_text_string_list[i_line_num - 1]
                    string_pre_lens = len(string_pre)
                    for k in range(string_pre_lens):
                        if (k+2 < string_pre_lens and string_pre[k] == '转' and string_pre[k+1] == '让' and string_pre[k+2] == '方') or (k+1 < string_pre_lens and string_pre[k] == '甲' and string_pre[k+1] == '方'):
                            z_loc = k
                            break

                if z_loc != -1 and transferor_bank_account == '':
                    transferor_bank_account = string
                    break

                # if i<60:
                #     transferor_bank_account = string
                #     break


        # 提取转让方户名
        for i in range(string_lens):
            if (i+2<string_lens and string[i] == '户' and string[i+1] == '名' and (string[i+2] == '：' or string[i+2] == ':')):
                z_loc = -1
                if i_line_num - 2 >= 0:
                    string_pre = docx_text_string_list[i_line_num - 2]
                    string_pre_lens = len(string_pre)
                    for k in range(string_pre_lens):
                        if (k + 2 < string_pre_lens and string_pre[k] == '转' and string_pre[k + 1] == '让' and string_pre[k + 2] == '方') or (k + 1 < string_pre_lens and string_pre[k] == '甲' and string_pre[k + 1] == '方'):
                            z_loc = k
                            break

                if z_loc != -1 and transferor_name == '':
                    transferor_name = string
                    break

                # if i<60:
                #     transferor_name = string
                #     break


        # 提取转让方账户
        for i in range(string_lens):
            if (i+2<string_lens and string[i] == '账' and (string[i+1] == '户' or string[i+1] == '号') and (string[i+2] == '：' or string[i+2] == ':')):
                z_loc = -1
                if i_line_num - 3 >= 0:
                    string_pre = docx_text_string_list[i_line_num - 3]
                    string_pre_lens = len(string_pre)
                    for k in range(string_pre_lens):
                        if (k + 2 < string_pre_lens and string_pre[k] == '转' and string_pre[k + 1] == '让' and string_pre[k + 2] == '方') or (k + 1 < string_pre_lens and string_pre[k] == '甲' and string_pre[k + 1] == '方'):
                            z_loc = k
                            break

                if z_loc != -1 and transferor_account == '':
                    transferor_account = string
                    break


                # if i<60:
                #     transferor_account = string
                #     break


        # 提取交易保证金
        for i in range(string_lens):
            if (i+1<string_lens and string[i]=='交' and string[i+1]=='易' and string[i+2]=='保' and string[i+3]=='证' and string[i+4]=='金'):
                b_loc = -1
                y_loc = -1
                for b in range(string_lens):
                    if string[b] == '币':
                        b_loc = b
                    if string[b] == '元':
                        y_loc = b
                if b_loc != -1 and y_loc != -1:
                    trade_margin_details = string
                    break

    
    # 将已经提取的合同要素句子规范化，从中提取关键信息

    # 合同编号规范化
    string_k = contract_no
    string_lens_k = len(contract_no)
    start_loc = 0
    for i in range(string_lens_k):
        if (i+1< string_lens_k and string_k[i] == '号' and(string_k[i+1] == '：' or string_k[i+1] == ':')):
            start_loc = i+1
            break
    if start_loc+1 > string_lens_k:
        start_loc -= 1
    elements_dict['合同编号'] = string_k[start_loc+1:]


    # 合同类型规范化
    elements_dict['业务类型'] = business_types


    # 协议签订日期规范化
    string_k = data_of_agreement
    string_k = string_k.replace('[','')
    string_k = string_k.replace(']', '')
    if len(string_k) >= 7:
        string_k = string_k[7:]
    elements_dict['协议签订日期'] = string_k



    # 协议签订地点规范化
    string_k = place_of_signing
    string_k = string_k.replace('[', '')
    string_k = string_k.replace(']', '')
    if len(string_k) >= 7:
        string_k = string_k[7:]
    elements_dict['协议签订地点'] = string_k



    # 债务方规范化
    string_k = debator
    string_k = string_k.replace('[', '')
    string_k = string_k.replace(']', '')
    start_loc = string_k.find('：')
    if start_loc == -1:
        start_loc = 0
    if start_loc +1 > len(debator):
        start_loc -= 1
    string_k = string_k[start_loc+1:]
    elements_dict['债务方'] = string_k


    #转让方负责人规范化
    string_k = transferor_responsible
    string_k = string_k.replace('[', '')
    string_k = string_k.replace(']', '')
    start_loc = string_k.find('：')
    if start_loc == -1:
        start_loc = 0
    if start_loc + 1 > len(transferor_responsible):
        start_loc -= 1
    string_k = string_k[start_loc + 1:]
    elements_dict['转让方负责人'] = string_k


    # 受让方负责人规范化
    string_k = recipie_legal
    string_k = string_k.replace('[', '')
    string_k = string_k.replace(']', '')
    start_loc = string_k.find('：')
    if start_loc == -1:
        start_loc = 0
    if start_loc + 1 > len(recipie_legal):
        start_loc -= 1
    string_k = string_k[start_loc + 1:]
    elements_dict['受让方法定代表人'] = string_k



    # 债务方负责人规范化
    string_k = debator_responsible
    string_k = string_k.replace('[', '')
    string_k = string_k.replace(']', '')
    start_loc = string_k.find('：')
    if start_loc == -1:
        start_loc = 0
    if start_loc + 1 > len(debator_responsible):
        start_loc -= 1
    string_k = string_k[start_loc + 1:]
    elements_dict['债务方负责人'] = string_k


    # 转让方住所规范化
    string_k = transferor_location
    string_k = string_k.replace('[', '')
    string_k = string_k.replace(']', '')
    start_loc = string_k.find('：')
    if start_loc == -1:
        start_loc = 0
    if start_loc + 1 > len(transferor_location):
        start_loc -= 1
    string_k = string_k[start_loc + 1:]

    elements_dict['转让方住所'] = string_k



    # 受让方住所规范化
    string_k = recipie_location
    string_k = string_k.replace('[', '')
    string_k = string_k.replace(']', '')
    start_loc = string_k.find('：')
    if start_loc == -1:
        start_loc = 0
    if start_loc + 1 > len(recipie_location):
        start_loc -= 1
    string_k = string_k[start_loc + 1:]

    elements_dict['受让方住所'] = string_k



    # 债务方住所规范化
    string_k = debator_location
    string_k = string_k.replace('[', '')
    string_k = string_k.replace(']', '')
    string_k = string_k.replace('邮编：', '')
    string_k = string_k.replace('电话：', '')
    start_loc = string_k.find('：')
    if start_loc == -1:
        start_loc = 0
    if start_loc + 1 > len(debator_location):
        start_loc -= 1
    string_k = string_k[start_loc + 1:]

    elements_dict['债务方住所'] = string_k



    #账面本金余额规范化
    string_k = account_remain_money
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_lens = len(string_k)
        sentence_start_loc = 0
        sentence_end_loc = string_lens
        d_start_loc = 0
        d_end_loc = string_lens
        x_start_loc = 0
        x_end_loc = string_lens

        # 找到句子的开始、结束标记
        for i in range(string_lens):
            if i+5 < string_lens and string_k[i] == '账' and string_k[i+1] == '面' and string_k[i+2] == '本' and string_k[i+3] == '金' and string_k[i+4] == '余' and string_k[i+5] == '额':
                sentence_start_loc = i+5
                break
        for i in range(string_lens):
            if i+1 <string_lens and string_k[i] == '利' and string_k[i+1] == '息':
                sentence_end_loc = i
                break

        # 提取大写金额
        for i in range(sentence_start_loc,sentence_end_loc):
            if i+2 <= sentence_end_loc and string_k[i] == '人' and string_k[i+1] == '民' and string_k[i+2] == '币':
                d_start_loc = i+2
                break
        for i in range(sentence_start_loc,sentence_end_loc):
            if i+1 <= sentence_end_loc and string_k[i] == '小' and string_k[i+1] == '写':
                d_end_loc = i
                break

        # 提取小写金额
        for i in range(sentence_start_loc,sentence_end_loc):
            if i+2 <= sentence_end_loc and string_k[i] == '小' and string_k[i+1] == '写' and (string_k[i+2] == '：' or string_k[i+2] == ':'):
                x_start_loc = i+2
                break
        for i in range(sentence_start_loc,sentence_end_loc):
            if string_k[i] == '元':
                x_end_loc = i
                break

        d_string = string_k[d_start_loc+1:d_end_loc]
        x_string = string_k[x_start_loc+1:x_end_loc]
        account_remain_money_list[0] = d_string
        account_remain_money_list[1] = x_string
        elements_dict['账面本金余额'] = account_remain_money_list

    else:
        elements_dict['账面本金余额'] = account_remain_money_list


    # 利息规范化
    string_k = interest
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_lens = len(string_k)
        sentence_start_loc = 0
        sentence_end_loc = string_lens
        d_start_loc = 0
        d_end_loc = string_lens
        x_start_loc = 0
        x_end_loc = string_lens

        # 找到句子的开始、结束标记
        for i in range(string_lens):
            if i + 1 < string_lens and string_k[i] == '利' and string_k[i + 1] == '息':
                sentence_start_loc = i
                break
        for i in range(string_lens):
            if i + 3 < string_lens and string_k[i] == '其' and string_k[i + 1] == '他' and string_k[i + 2] == '债' and string_k[i + 3] == '权':
                sentence_end_loc = i
                break

        # 提取大写金额
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 2 <= sentence_end_loc and string_k[i] == '人' and string_k[i + 1] == '民' and string_k[i + 2] == '币':
                d_start_loc = i + 2
                break
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 1 <= sentence_end_loc and string_k[i] == '小' and string_k[i + 1] == '写':
                d_end_loc = i
                break

        # 提取小写金额
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 2 <= sentence_end_loc and string_k[i] == '小' and string_k[i + 1] == '写' and (string_k[i + 2] == '：' or string_k[i + 2] == ':'):
                x_start_loc = i + 2
                break
        for i in range(sentence_start_loc, sentence_end_loc):
            if string_k[i] == '元':
                x_end_loc = i
                break

        d_string = string_k[d_start_loc + 1:d_end_loc]
        x_string = string_k[x_start_loc + 1:x_end_loc]
        interest_list[0] = d_string
        interest_list[1] = x_string
        elements_dict['利息'] = interest_list

    else:
        elements_dict['利息'] = interest_list


    # 提取其他债权
    string_k = other_creditors
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_lens = len(string_k)
        sentence_start_loc = 0
        sentence_end_loc = string_lens
        d_start_loc = 0
        d_end_loc = string_lens
        x_start_loc = 0
        x_end_loc = string_lens

        # 找到句子的开始、结束标记
        for i in range(string_lens):
            if i + 3 < string_lens and string_k[i] == '其' and string_k[i + 1] == '他' and string_k[i + 2] == '债' and string_k[i + 3] == '权':
                sentence_start_loc = i
                break
        for i in range(string_lens):
            if i + 3 < string_lens and string_k[i] == '整' and string_k[i + 1] == '体' and string_k[i + 2] == '债' and string_k[i + 3] == '权':
                sentence_end_loc = i
                break

        # 提取大写金额
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 2 <= sentence_end_loc and string_k[i] == '人' and string_k[i + 1] == '民' and string_k[i + 2] == '币':
                d_start_loc = i + 2
                break
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 1 <= sentence_end_loc and string_k[i] == '小' and string_k[i + 1] == '写':
                d_end_loc = i
                break

        # 提取小写金额
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 2 <= sentence_end_loc and string_k[i] == '小' and string_k[i + 1] == '写' and (string_k[i + 2] == '：' or string_k[i + 2] == ':'):
                x_start_loc = i + 2
                break
        for i in range(sentence_start_loc, sentence_end_loc):
            if string_k[i] == '元':
                x_end_loc = i
                break

        d_string = string_k[d_start_loc + 1:d_end_loc]
        x_string = string_k[x_start_loc + 1:x_end_loc]
        other_creditors_list[0] = d_string
        other_creditors_list[1] = x_string
        elements_dict['其他债权'] = other_creditors_list

    else:
        elements_dict['其他债权'] = other_creditors_list


    # 提取整体债权
    string_k = total_creditors
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_lens = len(string_k)
        sentence_start_loc = 0
        sentence_end_loc = string_lens
        d_start_loc = 0
        d_end_loc = string_lens
        x_start_loc = 0
        x_end_loc = string_lens

        # 找到句子的开始、结束标记
        for i in range(string_lens):
            if i + 3 < string_lens and string_k[i] == '整' and string_k[i + 1] == '体' and string_k[i + 2] == '债' and string_k[i + 3] == '权':
                sentence_start_loc = i
                break

        # 提取大写金额
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 2 <= sentence_end_loc and string_k[i] == '人' and string_k[i + 1] == '民' and string_k[i + 2] == '币':
                d_start_loc = i + 2
                break
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 1 <= sentence_end_loc and string_k[i] == '小' and string_k[i + 1] == '写':
                d_end_loc = i
                break

        # 提取小写金额
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 2 <= sentence_end_loc and string_k[i] == '小' and string_k[i + 1] == '写' and (string_k[i + 2] == '：' or string_k[i + 2] == ':'):
                x_start_loc = i + 2
                break
        for i in range(sentence_start_loc, sentence_end_loc):
            if string_k[i] == '元':
                x_end_loc = i
                break

        d_string = string_k[d_start_loc + 1:d_end_loc]
        x_string = string_k[x_start_loc + 1:x_end_loc]
        total_creditors_list[0] = d_string
        total_creditors_list[1] = x_string
        elements_dict['整体债权'] = total_creditors_list

    else:
        elements_dict['整体债权'] = total_creditors_list


    # 提取转让价款
    string_k = transfer_price
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_k = string_k.replace('。', '')

        string_lens = len(string_k)
        start_loc = 0
        for i in range(string_lens):
            if i + 2 <= string_lens and string_k[i] == '人' and string_k[i + 1] == '民' and string_k[i + 2] == '币':
                start_loc = i
                break
        m_string = string_k[start_loc:]
        m_string = m_string.replace(':', '')
        m_string = m_string.replace('：', '')
        m_string = m_string.replace('大写', '')
        m_string = m_string.replace('小写', '')
        m_string = m_string.replace('元', '')
        m_string = m_string.replace('人民币', '')
        m_string = m_string.replace('¥', '')

        loc =0
        for i in range(len(m_string)):
            if m_string[i] >= '0' and m_string[i] <= '9':
                loc = i
                break
        d_string = m_string[:loc]
        x_string = m_string[loc:len(m_string)]
        transfer_price_list[0] = d_string
        transfer_price_list[1] = x_string
        elements_dict['转让价款'] = transfer_price_list

    else:
        elements_dict['转让价款'] = transfer_price_list


    # 提取债权金额
    string_k = creditor_money
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_lens = len(string_k)
        sentence_start_loc = 0
        sentence_end_loc = string_lens
        for i in range(0,sentence_end_loc):
            if i+3 <= sentence_end_loc and string_k[i] == '债' and string_k[i+1] == '权' and string_k[i+2] == '金' and string_k[i+3] == '额':
                sentence_start_loc = i
                break

        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 2 <= sentence_end_loc and string_k[i] == '人' and string_k[i + 1] == '民' and string_k[i + 2] == '币':
                sentence_start_loc = i
                break

        for i in range(sentence_start_loc, sentence_end_loc):
            if i+1<=sentence_end_loc and string_k[i]=='元' and (string_k[i+1] == '，' or string_k[i+1] == ',' or string_k[i+1] == '。'):
                sentence_end_loc = i+1
                break
        m_string = string_k[sentence_start_loc:sentence_end_loc]
        m_string = m_string.replace(':', '')
        m_string = m_string.replace('：', '')
        m_string = m_string.replace('大写', '')
        m_string = m_string.replace('小写', '')
        m_string = m_string.replace('元', '')
        m_string = m_string.replace('人民币', '')
        m_string = m_string.replace('¥', '')

        loc = 0
        for i in range(len(m_string)):
            if m_string[i] >= '0' and m_string[i] <= '9':
                loc = i
                break
        d_string = m_string[:loc]
        x_string = m_string[loc:len(m_string)]
        creditor_money_list[0] = d_string
        creditor_money_list[1] = x_string
        elements_dict['债权金额'] = creditor_money_list

    else:
        elements_dict['债权金额'] = creditor_money_list


    # 提取违约金
    string_k = breach_of_contract
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_lens = len(string_k)
        sentence_start_loc = 0
        sentence_end_loc = string_lens
        for i in range(0,sentence_end_loc):
            if i+2 <= sentence_end_loc and string_k[i] == '违' and string_k[i+1] == '约' and string_k[i+2] == '金':
                sentence_start_loc = i
                break
        for i in range(sentence_start_loc, sentence_end_loc):
            if i+1<=sentence_end_loc and string_k[i]=='元' and (string_k[i+1] == '，' or string_k[i+1] == ',' or string_k[i+1] == '。'):
                sentence_end_loc = i+1
                break
        m_string = string_k[sentence_start_loc:sentence_end_loc]
        m_string = m_string.replace(':', '')
        m_string = m_string.replace('：', '')
        m_string = m_string.replace('大写', '')
        m_string = m_string.replace('小写', '')
        m_string = m_string.replace('元', '')
        m_string = m_string.replace('人民币', '')
        m_string = m_string.replace('¥', '')
        m_string = m_string.replace('违约金', '')
        loc = 0
        for i in range(len(m_string)):
            if m_string[i] >= '0' and m_string[i] <= '9':
                loc = i
                break
        d_string = m_string[:loc]
        x_string = m_string[loc:len(m_string)]
        breach_of_contract_list[0] = d_string
        breach_of_contract_list[1] = x_string
        elements_dict['违约金'] = breach_of_contract_list

    else:
        elements_dict['违约金'] = breach_of_contract_list


    # 基准日规范化
    if base_date != '':
        string_k = base_date.replace('★','')
        elements_dict['基准日'] = string_k
    else:
        elements_dict['基准日'] = base_date


    # 本息总额规范化
    string_k = total_price_and_interest
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_lens = len(string_k)
        sentence_start_loc = 0
        sentence_end_loc = string_lens
        for i in range(string_lens):
            if i+3 < string_lens and string_k[i] == '本' and string_k[i+1] == '息' and string_k[i+2] == '总' and string_k[i+3] == '额':
                sentence_start_loc = i
                break
        for i in range(sentence_start_loc,sentence_end_loc):
            if i+2 <= sentence_end_loc and string_k[i] == '人' and string_k[i+1] == '民' and string_k[i+2] == '币':
                sentence_start_loc = i
                break

        for i in range(sentence_start_loc,sentence_end_loc):
            if i+1 <= sentence_end_loc and string_k[i] == '元' and (string_k[i+1] == '，' or string_k[i+1] == '。' or string_k[i+1] == ','):
                sentence_end_loc = i+1
                break
        m_string = string_k[sentence_start_loc:sentence_end_loc]
        m_string = m_string.replace(':', '')
        m_string = m_string.replace('：', '')
        m_string = m_string.replace('大写', '')
        m_string = m_string.replace('小写', '')
        m_string = m_string.replace('元', '')
        m_string = m_string.replace('人民币', '')
        m_string = m_string.replace('¥', '')
        m_string = m_string.replace('本息总额', '')
        loc = 0
        for i in range(len(m_string)):
            if m_string[i] >= '0' and m_string[i] <= '9':
                loc = i
                break
        d_string = m_string[:loc]
        x_string = m_string[loc:len(m_string)]
        total_price_and_interest_list[0] = d_string
        total_price_and_interest_list[1] = x_string
        elements_dict['本息总额'] = total_price_and_interest_list

    else:
        elements_dict['本息总额'] = total_price_and_interest_list


    # 本金余额规范化
    string_k = pricipal_remain
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_lens = len(string_k)
        sentence_start_loc = 0
        sentence_end_loc = string_lens
        for i in range(string_lens):
            if i + 3 < string_lens and string_k[i] == '本' and string_k[i + 1] == '金' and string_k[i + 2] == '余' and string_k[i + 3] == '额':
                sentence_start_loc = i
                break
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 2 <= sentence_end_loc and string_k[i] == '人' and string_k[i + 1] == '民' and string_k[i + 2] == '币':
                sentence_start_loc = i
                break

        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 1 <= sentence_end_loc and string_k[i] == '元' and (string_k[i + 1] == '，' or string_k[i + 1] == '。' or string_k[i + 1] == ','):
                sentence_end_loc = i + 1
                break
        m_string = string_k[sentence_start_loc:sentence_end_loc]
        m_string = m_string.replace(':', '')
        m_string = m_string.replace('：', '')
        m_string = m_string.replace('大写', '')
        m_string = m_string.replace('小写', '')
        m_string = m_string.replace('元', '')
        m_string = m_string.replace('人民币', '')
        m_string = m_string.replace('¥', '')
        m_string = m_string.replace('本金余额', '')
        loc = 0
        for i in range(len(m_string)):
            if m_string[i] >= '0' and m_string[i] <= '9':
                loc = i
                break
        d_string = m_string[:loc]
        x_string = m_string[loc:len(m_string)]
        pricipal_remain_list[0] = d_string
        pricipal_remain_list[1] = x_string
        elements_dict['本金余额'] = pricipal_remain_list

    else:
        elements_dict['本金余额'] = pricipal_remain_list


    # 欠息规范化
    string_k = debit_interest
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_k = string_k.replace('（', '')
        string_k = string_k.replace('）', '')
        string_lens = len(string_k)
        sentence_start_loc = 0
        sentence_end_loc = string_lens
        for i in range(string_lens):
            if i + 1 < string_lens and string_k[i] == '欠' and string_k[i + 1] == '息':
                sentence_start_loc = i
                break
        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 2 <= sentence_end_loc and string_k[i] == '人' and string_k[i + 1] == '民' and string_k[i + 2] == '币':
                sentence_start_loc = i
                break

        for i in range(sentence_start_loc, sentence_end_loc):
            if i + 1 <= sentence_end_loc and string_k[i] == '元' and (string_k[i + 1] == '，' or string_k[i + 1] == '。' or string_k[i + 1] == ','):
                sentence_end_loc = i + 1
                break
        m_string = string_k[sentence_start_loc:sentence_end_loc]
        m_string = m_string.replace(':', '')
        m_string = m_string.replace('：', '')
        m_string = m_string.replace('大写', '')
        m_string = m_string.replace('小写', '')
        m_string = m_string.replace('元', '')
        m_string = m_string.replace('人民币', '')
        m_string = m_string.replace('¥', '')
        m_string = m_string.replace('欠息', '')
        loc = 0
        for i in range(len(m_string)):
            if m_string[i] >= '0' and m_string[i] <= '9':
                loc = i
                break
        d_string = m_string[:loc]
        x_string = m_string[loc:len(m_string)]
        debit_interest_list[0] = d_string
        debit_interest_list[1] = x_string
        elements_dict['欠息'] = debit_interest_list

    else:
        elements_dict['欠息'] = debit_interest_list


    # 转让方开户银行规范化
    string_k = transferor_bank_account
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_lens = len(string_k)
        loc = 0
        for i in range(string_lens):
            if i+1 < string_lens and string_k[i] == '行' and (string_k[i+1] == '：' or string_k[i+1] == ':'):
                loc = i+1
                break
        if loc+1 > string_lens:
            loc -= 1
        m_string = string_k[loc+1:]
        elements_dict['转让方开户银行'] = m_string

    else:
        elements_dict['转让方开户银行'] = transferor_bank_account



    # 转让方户名规范化
    string_k = transferor_name
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_lens = len(string_k)
        loc = 0
        for i in range(string_lens):
            if i + 1 < string_lens and string_k[i] == '名' and (string_k[i + 1] == '：' or string_k[i + 1] == ':'):
                loc = i + 1
                break
        if loc + 1 > string_lens:
            loc -= 1
        m_string = string_k[loc + 1:]
        elements_dict['转让方户名'] = m_string

    else:
        elements_dict['转让方户名'] = transferor_name


    # 转让方账户规范化
    string_k = transferor_account
    if string_k != '':
        string_k = string_k.replace('[', '')
        string_k = string_k.replace(']', '')
        string_lens = len(string_k)
        loc = 0
        for i in range(string_lens):
            if i + 1 < string_lens and (string_k[i] == '户' or string_k[i] == '号') and (string_k[i + 1] == '：' or string_k[i + 1] == ':'):
                loc = i + 1
                break
        if loc + 1 > string_lens:
            loc -= 1
        m_string = string_k[loc + 1:]
        elements_dict['转让方账户'] = m_string

    else:
        elements_dict['转让方账户'] = transferor_account


    # 交易保证金规范化
    elements_dict['交易保证金详情'] = trade_margin_details


    # 提取的合同要素结果输出
    # for item in elements_dict:
    #     print(item,'：  ',elements_dict[item])

    return elements_dict


# 输入：一类合同要素的所有句子
# 输出：一类合同要素的句子向量
def sentences_to_vector(txt_bow_file_name_,all_sentences):
    # txt_bow_list保存的是训练集中所有句子分词后 非重复单词组成的list
    txt_bow_list = []
    with open(txt_bow_file_name_, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    for i_line in all_lines:
        string = i_line[:-1]
        txt_bow_list.append(string)

    all_sentences_new_list = []
    all_sentences_new_set = []
    sentences_lens = len(all_sentences)
    for i in range(sentences_lens):
        i_sentence = all_sentences[i]
        i_sentence_cut = list(jieba.cut(i_sentence))
        i_sentence_new_list = []
        i_sentence_new_set = set()
        for i_word in i_sentence_cut:
            if i_word in txt_bow_list:
                i_sentence_new_list.append(i_word)
                i_sentence_new_set.add(i_word)
        all_sentences_new_list.append(i_sentence_new_list)
        all_sentences_new_set.append(i_sentence_new_set)

    all_sentences_vector = []
    for i in range(sentences_lens):
        i_sentence_vector = [0] * len(txt_bow_list)
        i_sentence_set = all_sentences_new_set[i]
        i_sentence_list = all_sentences_new_list[i]
        for i_word in i_sentence_set:
            i_word_tf = 0
            for every_word in i_sentence_list:
                if i_word == every_word:
                    i_word_tf += 1

            i_word_num = 0
            for item in all_sentences_new_list:
                if i_word in item:
                    i_word_num += 1

            k = (sentences_lens + 1) / (i_word_num + 1)
            i_word_idf = math.log(k, 10) + 1

            i_word_tfidf = i_word_tf * i_word_idf
            for loc in range(len(txt_bow_list)):
                if i_word == txt_bow_list[loc]:
                    i_sentence_vector[loc] = i_word_tfidf
        all_sentences_vector.append(i_sentence_vector)

    return all_sentences_vector




# 输入：债权金额list['大写金额','小写金额']
# 输出：金额大小写是否一致
def check_equal(money_list):
    d_string = money_list[0]
    x_string = money_list[1]
    # 去除单位字符
    d_string = d_string.replace('亿','')
    d_string = d_string.replace('万', '')
    d_string = d_string.replace('仟', '')
    d_string = d_string.replace('佰', '')
    d_string = d_string.replace('拾', '')
    d_string = d_string.replace('整', '')
    d_string = d_string.replace('圆', '')
    d_string = d_string.replace('角', '')
    d_string = d_string.replace('分', '')
    d_string = d_string.replace('厘', '')
    d_string = d_string.replace('元', '')

    # 替换中文金额字符
    d_string = d_string.replace('壹', '1')
    d_string = d_string.replace('贰', '2')
    d_string = d_string.replace('叁', '3')
    d_string = d_string.replace('肆', '4')
    d_string = d_string.replace('伍', '5')
    d_string = d_string.replace('陆', '6')
    d_string = d_string.replace('陸', '6')
    d_string = d_string.replace('柒', '7')
    d_string = d_string.replace('捌', '8')
    d_string = d_string.replace('玖', '9')
    d_string = d_string.replace('零', '')


    x_string = money_list[1]
    # 替换小写金额分隔符
    x_string = x_string.replace(',','')
    x_string = x_string.replace('.', '')
    x_string = x_string.replace('，', '')
    x_string = x_string.replace('。', '')
    
    x_string_new = x_string.replace('0','')

    if d_string == x_string_new:
        return True
    else:
        return False


# 输入：合同要素抽取后的结果elements_dict
# 输出：按照顺序返回每类合同要素金额的审核信息
def check_res(elements_dict):
    check_res_dict = {
        '账面本金余额':'',
        '利息': '',
        '其他债权': '',
        '整体债权': '',
        '转让价款': '',
        '债权金额': '',
        '违约金': '',
        '本息总额': '',
        '本金余额': '',
        '欠息': ''
    }

    for element in elements_dict:
        if element == '账面本金余额' or element == '利息' or element == '其他债权' or element == '整体债权' or element == '转让价款' or element == '债权金额' or element == '违约金' or element == '本息总额' or element == '本金余额' or element == '欠息':
            if elements_dict[element] != ['','']:
                res = check_equal(elements_dict[element])
                if res == True:
                    check_res_dict[element] = '1'
                else:
                    check_res_dict[element] = '-1'
            else:
                check_res_dict[element] = ''

    return check_res_dict


# 输入：一个提取合同要素的结果list['','','','']
# 输出：一个新的list 其中金额部分将str变成了list['大写','小写']
def d_x_dic(dic):
    # 账面本金余额
    string = dic[13]
    string = string.replace('[','')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc+1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc+1:string_lens]
    dic[13] = [d_string,x_string]


    string = dic[14]
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc+1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc+1:string_lens]
    dic[14] = [d_string, x_string]

    string = dic[15]
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc+1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc+1:string_lens]
    dic[15] = [d_string, x_string]

    string = dic[16]
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc+1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc+1:string_lens]
    dic[16] = [d_string, x_string]

    string = dic[17]
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc+1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc+1:string_lens]
    dic[17] = [d_string, x_string]

    string = dic[18]
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc+1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc+1:string_lens]
    dic[18] = [d_string, x_string]

    string = dic[19]
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc+1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc+1:string_lens]
    dic[19] = [d_string, x_string]

    string = dic[21]
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc+1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc+1:string_lens]
    dic[21] = [d_string, x_string]

    string = dic[22]
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc+1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc+1:string_lens]
    dic[22] = [d_string, x_string]

    string = dic[23]
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('\'', '')
    string_lens = len(string)
    loc = 0
    for i in range(string_lens):
        if string[i] == ',':
            loc = i
            break
    if loc + 1 > string_lens:
        loc -= 1
    d_string = string[0:loc]
    x_string = string[loc + 1:string_lens]
    dic[23] = [d_string, x_string]

    return dic


if __name__ == '__main__':
    file_list = [
        'D:/jupyter_datafile/contract_extract/债权转让协议_带标注2.docx',
        'D:/jupyter_datafile/contract_extract/债权转让协议-电信.docx',
        'D:/jupyter_datafile/contract_extract/HR债权转让.docx',
        'D:/jupyter_datafile/contract_extract/债务重组协议.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-01-F1-债权转让协议（单户收购）（三方签署）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-01-F2-债权转让协议（单户收购）（双方签署）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-02-E-债权转让协议（打包收购）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-03-E-债权转让协议（信托公司自有资金信托贷款债权）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-04-E-债权转让协议（信托公司信托资金信托贷款债权）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-05-E-债权转让协议（信托计划下回购特定资产形成债权）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-06-G-债权转让协议（工程款债权）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-07-G-债权转让协议（一般企业债权）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-08-G-债权转让协议（委托贷款债权三方签署）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-09-G-债权转让协议（委托贷款债权四方签署）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-10-G-债务重组协议（适用于金融债或非金债收购委托贷款项目单个债务人） (3)_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-10-G-债务重组协议（适用于金融债或非金债收购委托贷款项目单个债务人）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-35-D-债权转让协议（我司对外转让）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-117-A-债权转让协议（因供货或提供服务而形成的应收账款债权）_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/打包收购_sgcz_zqzr.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/三方签署_sgcz_zqzr.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/实例1.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/实例2.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/实例3.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/双方签署_sgcz_zqzr.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/我司对外转让_sgcz_zqzr.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/债权转让协议金科_标注.docx',
        'D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/债权转让协议签署版1225_标注.docx'
    ]
    # 测试输出
    # for item in file_list:
    #     print(item)
    #     elements_dict = output_elements_from_docx(item)
    #     check_res(elements_dict)
    #     # for element in elements_dict:
    #     #     if element == '账面本金余额' or element == '利息' or element == '其他债权' or element == '整体债权' or element == '转让价款' or element == '债权金额' or element == '违约金' or element == '本息总额' or element == '本金余额' or element == '欠息':
    #     #         print(element, '：', elements_dict[element])
    #     #     else:
    #     #         print(element,'：',elements_dict[element])
    #     print('\n'*3)

    # output_elements_from_docx('D:/jupyter_datafile/contract_extract/合同文件集_带标注_2018_9_4/HR-CK-01-F1-债权转让协议（单户收购）（三方签署）_标注.docx')
    # 审核内容、审核规则、审核结果
    # 金额大写小写        一致/不一致



