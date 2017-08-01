from functools import wraps
import hashlib
import os
import random
import re
import json
from datetime import datetime as dt
import numpy as np
import pandas as pd
import pymysql
from itertools import zip_longest
from flask import Flask, render_template, request, redirect, Response
from flask_bootstrap import Bootstrap


conn = pymysql.connect(host='localhost', port=3306, user='root', password='password', db='webapp')
cur = conn.cursor()

ndc_code_in = '54868034000'
cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE NDC_CODE LIKE '{}'".format(ndc_code_in))
ndc = []
data = cur.fetchall()
for row in data:
    ndc.append(row[0])
ndc_code = list(set(ndc))

cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE LIKE '{}'".format(ndc_code_in))
atc = []
data = cur.fetchall()
for row in data:
    atc.append(row[0])
atc_code = list(set(atc))
print(atc)
print(atc_code)

umls_code = []
for i in atc_code:
    cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}'".format(i))
    data = cur.fetchall()
    for row in data:
        umls_code.append(row[0])
    umls_code = list(set(umls_code))

################################################## Webapp optimization ################################################
umls_code = []
placeholders = ', '.join(['%s']*len(atc_code))
query = 'SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE atc_umls.ATC_CODE IN ({})'.format(placeholders)
cur.execute(query, tuple(atc_code))
data = cur.fetchall()
for row in data:
    umls_code.append(row[0])
umls_code = list(set(umls_code))

print(cur.execute(query, tuple(atc_code)))
print(len(umls_code))
print(umls_code)

#NDC LABEL
ndc_label = []
for i in ndc_code:
    cur.execute("SELECT STR_NDC FROM ndc_label WHERE NDC_CODE LIKE '{}'".format(i))
    data = cur.fetchall()
    for row in data:
        ndc_label.append(row[0])

ndc_res = []
for i in zip_longest(ndc_label, ndc_code):
    ndc_res.append(i)


atc_label = []
for i in atc_code:
    cur.execute("SELECT STR_IN FROM atc_label WHERE ATC_CODE LIKE '{}'".format(i))
    data = cur.fetchall()
    for row in data:
        atc_label.append(row[0])

atc_res = []
for i in zip_longest(atc_code, atc_label):
    atc_res.append(i)

print(atc_res)

umls_label = []
for i in umls_code:
    cur.execute("SELECT DISTINCT SIDE_EFFECT_NAME FROM umls_label WHERE UMLSCUI_MEDDRA LIKE '{}'".format(i))
    data = cur.fetchall()
    for row in data:
        umls_label.append(row[0])

umls_res = []
for i in zip_longest(umls_label, umls_code):
    umls_res.append(i)

print(umls_label)
print(umls_code)
print(umls_res)

test = ' '
if test:
    print("noice")




# ndc_in = []
# atc_in = ['N02AJ06']
# umls_in = []
# # Code numbers
# ndc_code = []
# atc_code = []
# umls_code = []
#
# # Names of codes
# ndc_label = []
# atc_label = []
# umls_label = []
#
# # Tuple (name, code) of result
# ndc_res = []
# atc_res = []
# umls_res = []
#
# if ndc_in:
#     ndc_code.append(ndc_in)
#
# if atc_in:
#     atc_code.append(atc_in)
#
# if umls_in:
#     umls_code.append(umls_in)
#
# # ATC Code is the easiest to search if user only put NDC or UMLS
# if not atc_in:
#     if ndc_in:
#         cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE LIKE '{}'".format(ndc_in))
#         data = cur.fetchall()
#         for row in data:
#             atc_code.append(row[0])
#         atc_code = list(set(atc_code))
#     elif umls_in:
#         cur.execute("SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA LIKE '{}'".format(umls_in))
#         data = cur.fetchall()
#         for row in data:
#             atc_code.append(row[0])
#         atc_code = list(set(atc_code))
#
# # Since ATC Code was already searched, only look at ndc_atc, and atc_umls files
# if not ndc_in:
#     for i in atc_code:
#         cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE LIKE '{}'".format(i))
#         data = cur.fetchall()
#         for row in data:
#             ndc_code.append(row[0])
#         ndc_code = list(set(ndc_code))
#
# if not umls_in:
#     for i in atc_code:
#         cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}'".format(i))
#         data = cur.fetchall()
#         for row in data:
#             umls_code.append(row[0])
#         umls_code = list(set(umls_code))
#
#
# #NDC LABEL
# for i in ndc_code:
#     cur.execute("SELECT STR_NDC FROM ndc_label WHERE NDC_CODE LIKE '{}'".format(i))
#     data = cur.fetchall()
#     for row in data:
#         ndc_label.append(row[0])
# for i in zip_longest(ndc_label, ndc_code):
#     ndc_res.append(i)
#
# #ATC LABEL
# for i in atc_code:
#     cur.execute("SELECT STR_IN FROM atc_label WHERE ATC_CODE LIKE '{}'".format(i))
#     data = cur.fetchall()
#     for row in data:
#         atc_label.append(row[0])
# for i in zip_longest(atc_label, atc_code):
#     atc_res.append(i)
#
# #UMLS LABEL
# for i in umls_code:
#     cur.execute("SELECT DISTINCT SIDE_EFFECT_NAME FROM umls_label WHERE UMLSCUI_MEDDRA LIKE '{}'".format(i))
#     data = cur.fetchall()
#     for row in data:
#         umls_label.append(row[0])
# for i in zip_longest(umls_label, umls_code):
#     umls_res.append(i)

# I have NDC = 54868034000 and ATC = R06AA10
qery = cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE = '54868034000' AND ATC_CODE = 'R06AA10'")
print(qery)
umls_code = []
atc_code = ['R06AA10']
ndc_in = '54868034000'
atc_in = 'R06AA10'
if (cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE = '{}' AND ATC_CODE = '{}'".format(ndc_in, atc_in))):
    cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ('{}')".format(atc_in))
    data = cur.fetchall()
    print(data)
    for row in data:
        umls_code.append(row[0])

type(umls_code)
umls_code = list(set(umls_code))
print(umls_code)
print(umls_code[1])
print(len(umls_code))
print("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE = '{}' AND ATC_CODE = '{}'".format(ndc_in, atc_in))
print(', '.join(repr(i) for i in umls_code))


print(atc_res)

res_list = [x[0] for x in atc_res]
print(res_list)
atc_desc = []

for string in res_list:
    # 1 character Level 1
    lv1 = string[:1]

    # 1-3 characters Level 2
    lv2 = string[:3]

    # 1-4 characters Level 3
    lv3 = string[:4]

    # 1-5 characters Level 4
    lv4 = string[:5]

    # 1-7 characters Level 5
    lv5 = string[:7]

    print("{}, {}, {}, {}, {}".format(lv1, lv2, lv3, lv4, lv5))

    query = "SELECT DISTINCT * FROM atc_index WHERE atc_index IN ('{}', '{}', '{}', '{}', '{}')".format(lv1, lv2, lv3, lv4, lv5)
    cur.execute(query)
    atc_tupl = cur.fetchall()
    atc_desc.append(atc_tupl)

print(atc_desc)

for atc_d in atc_desc:
    print(atc_d[4][1])
    print(atc_d[4][0])
    print(atc_d[0][1]) #Stage 1
    print(atc_d[1][1]) #Stage 2
    print(atc_d[2][1]) #Stage 3
    print(atc_d[3][1]) #Stage 4
    print(atc_d[4][2]) #DDD

    print()