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

umls_code = []
for i in atc_code:
    cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}'".format(i))
    umls = []
    data = cur.fetchall()
    for row in data:
        umls.append(row[0])
    umls_code = list(set(umls))


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