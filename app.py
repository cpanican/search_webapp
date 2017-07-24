from functools import wraps
import hashlib
import os
import random
import re
import json
from datetime import datetime as dt
from itertools import zip_longest
import numpy as np
import pandas as pd
import pymysql
from flask import Flask, render_template, request, redirect, Response, url_for
from flask_bootstrap import Bootstrap

webapp = Flask(__name__)
Bootstrap(webapp)

conn = pymysql.connect(host='localhost', port=3306, user='root', password='password', db='webapp')
cur = conn.cursor()
cur2 = conn.cursor()


@webapp.route('/')
def search():
    return render_template('search.html')


@webapp.route('/', methods=['POST'])
def search_page():
    if request.method == 'POST':
        # Input form requests
        ndc_in = request.form['ndc']
        atc_in = request.form['atc']
        umls_in = request.form['umls']

        # Code numbers
        ndc_code = []
        atc_code = []
        umls_code = []

        # Names of codes
        ndc_label = []
        atc_label = []
        umls_label = []

        # Tuple (name, code) of result
        ndc_res = []
        atc_res = []
        umls_res = []

        if ndc_in:
            ndc_code.append(ndc_in)
        if atc_in:
            atc_code.append(atc_in)
        if umls_in:
            umls_code.append(umls_in)

        if ndc_in:
            for i in ndc_code:
                # cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE LIKE '{}'".format(i))
                cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE LIKE '{}' LIMIT 10".format(i))
                data = cur.fetchall()
                for row in data:
                    atc_code.append(row[0])

            for i in atc_code:
                # cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}'".format(i))
                cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}' LIMIT 10".format(i))
                data = cur.fetchall()
                for row in data:
                    umls_code.append(row[0])

        if atc_in:
            for i in atc_code:
                # cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE LIKE '{}'".format(i))
                cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE LIKE '{}' LIMIT 10".format(i))
                data = cur.fetchall()
                for row in data:
                    ndc_code.append(row[0])

                # cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}'".format(i))
                cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}' LIMIT 10".format(i))
                data = cur.fetchall()
                for row in data:
                    umls_code.append(row[0])

        if umls_in:
            for i in umls_code:
                # cur.execute("SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA LIKE '{}'".format(i))
                cur.execute("SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA LIKE '{}' LIMIT 10".format(i))
                data = cur.fetchall()
                for row in data:
                    atc_code.append(row[0])

            for i in atc_code:
                # cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE LIKE '{}'".format(i))
                cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE LIKE '{}' LIMIT 10".format(i))
                data = cur.fetchall()
                for row in data:
                    ndc_code.append(row[0])





        # works
        # Remove Duplicates
        atc_code = list(set(atc_code))
        ndc_code = list(set(ndc_code))
        umls_code = list(set(umls_code))

        #NDC LABEL
        for i in ndc_code:
            cur.execute("SELECT STR_NDC FROM ndc_label WHERE NDC_CODE LIKE '{}'".format(i))
            data = cur.fetchall()
            for row in data:
                ndc_label.append(row[0])
        for i in zip_longest(ndc_label, ndc_code):
            ndc_res.append(i)

        #ATC LABEL
        for i in atc_code:
            cur.execute("SELECT STR_IN FROM atc_label WHERE ATC_CODE LIKE '{}'".format(i))
            data = cur.fetchall()
            for row in data:
                atc_label.append(row[0])
        for i in zip_longest(atc_label, atc_code):
            atc_res.append(i)

        #UMLS LABEL
        for i in umls_code:
            cur.execute("SELECT DISTINCT SIDE_EFFECT_NAME FROM umls_label WHERE UMLSCUI_MEDDRA LIKE '{}'".format(i))
            data = cur.fetchall()
            for row in data:
                umls_label.append(row[0])
        for i in zip_longest(umls_label, umls_code):
            umls_res.append(i)

        return render_template("search.html", ndc_codes=ndc_res , atc_codes=atc_res, umls_codes=umls_res, ndc_in=ndc_in,
                               atc_in=atc_in, umls_in=umls_in)


if __name__ == '__main__':
    webapp.run()