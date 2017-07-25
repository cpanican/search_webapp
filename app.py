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
        # Initialize variables and inputs
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
            print("ndc_in: " + ndc_in)
        if atc_in:
            atc_code.append(atc_in)
            print("atc_in: " + atc_in)
        if umls_in:
            umls_code.append(umls_in)
            print("umls_in: " + umls_in)




        # Process the inputs and place them into variables
        # Input is ndc only
        if ndc_in and not atc_in and not umls_in:
            print("ndc only")
            placeholder = ', '.join(['%s'] * len(ndc_code))
            query = 'SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE IN ({}) LIMIT 10'.format(placeholder)
            cur.execute(query, tuple(ndc_code))
            data = cur.fetchall()
            for row in data:
                atc_code.append(row[0])

            placeholder = ', '.join(['%s'] * len(atc_code))
            query = 'SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ({}) LIMIT 10'.format(placeholder)
            cur.execute(query, tuple(atc_code))
            data = cur.fetchall()
            for row in data:
                umls_code.append(row[0])

            # for i in ndc_code:
            #     # cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE LIKE '{}'".format(i))
            #     cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE LIKE '{}' LIMIT 10".format(i))
            #     data = cur.fetchall()
            #     for row in data:
            #         atc_code.append(row[0])
            #
            # for i in atc_code:
            #     # cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}'".format(i))
            #     cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}' LIMIT 10".format(i))
            #     data = cur.fetchall()
            #     for row in data:
            #         umls_code.append(row[0])

        # Input is atc only
        if atc_in and not ndc_in and not umls_in:
            print("atc only")
            placeholder = ', '.join(['%s']*len(atc_code))
            query = 'SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE IN ({}) LIMIT 10'.format(placeholder)
            cur.execute(query, tuple(atc_code))
            data = cur.fetchall()
            for row in data:
                ndc_code.append(row[0])

            query = 'SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ({}) LIMIT 10'.format(placeholder)
            cur.execute(query, tuple(atc_code))
            data = cur.fetchall()
            for row in data:
                umls_code.append(row[0])

            # for i in atc_code:
            #     # cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE LIKE '{}'".format(i))
            #     cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE LIKE '{}' LIMIT 10".format(i))
            #     data = cur.fetchall()
            #     for row in data:
            #         ndc_code.append(row[0])
            #
            #     # cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}'".format(i))
            #     cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE LIKE '{}' LIMIT 10".format(i))
            #     data = cur.fetchall()
            #     for row in data:
            #         umls_code.append(row[0])

        # Input is umls only
        if umls_in and not ndc_in and not atc_in:
            print("umls only")
            placeholder = ', '.join(['%s'] * len(umls_code))
            query = 'SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA IN ({}) LIMIT 10'.format(placeholder)
            cur.execute(query, tuple(umls_code))
            data = cur.fetchall()
            for row in data:
                atc_code.append(row[0])

            placeholder = ', '.join(['%s'] * len(atc_code))
            query = 'SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE IN ({}) LIMIT 10'.format(placeholder)
            cur.execute(query, tuple(atc_code))
            data = cur.fetchall()
            for row in data:
                ndc_code.append(row[0])


            # for i in umls_code:
            #     # cur.execute("SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA LIKE '{}'".format(i))
            #     cur.execute("SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA LIKE '{}' LIMIT 10".format(i))
            #     data = cur.fetchall()
            #     for row in data:
            #         atc_code.append(row[0])
            #
            # for i in atc_code:
            #     # cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE LIKE '{}'".format(i))
            #     cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE LIKE '{}' LIMIT 10".format(i))
            #     data = cur.fetchall()
            #     for row in data:
            #         ndc_code.append(row[0])

        # Input is ndc and atc
        # If input is ndc and atc, then atc will be used to find umls. First, make sure that ndc match atc.
        if ndc_in and atc_in and not umls_in:
            print("ndc and atc")
            if (cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE = '{}' AND ATC_CODE = '{}'".format(ndc_in, atc_in))):
                cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ('{}')".format(atc_in))
                data = cur.fetchall()
                for row in data:
                    umls_code.append(row[0])


        # Input is ndc and umls
        # ???? Since atc is needed to match/connect ndc and umls, what results should be shown ???
        if ndc_in and not atc_in and umls_in:
            print("ndc and umls")
            cur.execute("SELECT ndc_atc.ATC_CODE FROM ndc_atc INNER JOIN atc_umls ON ndc_atc.ATC_CODE = atc_umls.ATC_CODE WHERE NDC_CODE = '{}' AND UMLSCUI_MEDDRA = '{}'".format(ndc_in, umls_in))
            data = cur.fetchall()
            for row in data:
                atc_code.append(row[0])

        # Input is atc and umls
        if not ndc_in and atc_in and umls_in:
            print("atc and umls")
            if (cur.execute("SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA = '{}' AND ATC_CODE = '{}'".format(umls_in, atc_in))):
                cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE IN ('{}') LIMIT 10".format(atc_in))
                data = cur.fetchall()
                for row in data:
                    ndc_code.append(row[0])





        # Match codes with names
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