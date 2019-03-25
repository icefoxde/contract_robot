#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time       : 2018/9/20 11:50
@Author     : Jiang Zesheng
@File       : jzs_list_tools.py
@Software   : PyCharm
@Description: 一些list工具
"""


def strings_to_list(ss):
    """
    将字符串用','或'，'分割，分别存在list里
    :param ss: 含有大小写的字符串
    :return:
    """
    if ss == '':
        return ['', '']
    p = ',' if ss.find(',') >= 0 else '，'
    ss = ss.split(p)
    return [ss[0], ss[1]]


elements_list = [
    '转让方',
    '转让方负责人',
    '转让方地址',
    '受让方',
    '受让方负责人',
    '受让方地址',
    '债务方',
    '债务方负责人',
    '债务方地址',
    '协议签订地点',
    '协议签订日期',
    '交易基准日',
    '债权本息总额',
    '本金余额',
    '欠息',
    '债权转让价款',
    '甲方指定账户',
    '开户银行',
    '户名',
    '账户',
    '交易保证金'
]


def get_elements_list():
    """
    得到要素名列表
    :return:
    """
    return elements_list


def list_to_dict(value_list):
    """
    将elements_list和
    :return:
    """
    dic = dict()
    if len(elements_list) != len(value_list):
        return dic

    for i in range(len(elements_list)):
        key = elements_list[i]
        dic[key] = value_list[i]
    return dic
