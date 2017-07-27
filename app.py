from functools import wraps
import hashlib
import os
import random
import re
import json
import time
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


def text_to_code(ndc_in, atc_in, umls_in):
    print("Text to code function: ")
    ndc_code = []
    atc_code = []
    umls_code = []

    print(not ndc_in.isspace())
    print(bool(ndc_in))
    # IF ndc_in is not a space and ndc_in is not empty
    # isspace() returns true if str is a space
    if not ndc_in.isspace() and ndc_in:
        ndc_code = [ndc_in]
        query = "SELECT NDC_CODE FROM ndc_label WHERE STR_NDC LIKE '%{}%' OR NDC_CODE LIKE '%{}%'".format(ndc_code[0], ndc_code[0])
        # print(cur.execute(query))
        if cur.execute(query):
            print("ndc conversion")
            data = cur.fetchall()
            print(data)
            ndc_code = [i[0] for i in data]
            print("finished converting from tuple to list")
        if cur.execute(query) == 0:
            ndc_code = []

    print(not atc_in.isspace())
    print(bool(atc_in))
    if not atc_in.isspace() and atc_in:
        atc_code = [atc_in]
        query = "SELECT ATC_CODE FROM atc_label WHERE STR_IN LIKE '%{}%' OR ATC_CODE LIKE '%{}%'".format(atc_code[0], atc_code[0])
        print(cur.execute(query))
        if cur.execute(query):
            print("atc converison")
            data = cur.fetchall()
            atc_code = [i[0] for i in data]
        if cur.execute(query) == 0:
            atc_code = []

    print(not umls_in.isspace())
    print(bool(umls_in))
    if not umls_in.isspace() and umls_in:
        umls_code = [umls_in]
        query = "SELECT DISTINCT UMLSCUI_MEDDRA FROM umls_label WHERE SIDE_EFFECT_NAME LIKE '%{}%' OR UMLSCUI_MEDDRA LIKE '%{}%'".format(umls_code[0], umls_code[0])
        print(cur.execute(query))
        if cur.execute(query):
            print("umls conversion")
            # cur.execute(query)
            data = cur.fetchall()
            umls_code = [i[0] for i in data] # Convert from tuple to list
        if cur.execute(query) == 0:
            umls_code = []

    print("Return values after conversion: NDC {}, ATC {}, UMLS {}".format(ndc_code, atc_code, umls_code))
    return ndc_code, atc_code, umls_code


def get_results(ndc_in, atc_in, umls_in):
    # Code numbers
    ndc_code, atc_code, umls_code = text_to_code(ndc_in, atc_in, umls_in)
    print()
    print("get_results inputs:")
    print("NDC {}, ATC {}, UMLS {}".format(ndc_code, atc_code, umls_code))
    print()

    # if ndc_in:
    #     ndc_code.append(ndc_in)
    #     print("ndc_in: " + ndc_in)
    # if atc_in:
    #     atc_code.append(atc_in)
    #     print("atc_in: " + atc_in)
    # if umls_in:
    #     umls_code.append(umls_in)
    #     print("umls_in: " + umls_in)

    # Input is NDC only
    print(bool(ndc_code))
    print(bool(atc_code))
    print(bool(umls_code))

    if ndc_code and not atc_code and not umls_code:
        print("ndc only")
        placeholder = ', '.join(['%s'] * len(ndc_code))
        query = 'SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE IN ({})'.format(placeholder)
        cur.execute(query, tuple(ndc_code))
        data = cur.fetchall()
        for row in data:
            atc_code.append(row[0])

        placeholder = ', '.join(['%s'] * len(atc_code))
        query = 'SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ({})'.format(placeholder)
        cur.execute(query, tuple(atc_code))
        data = cur.fetchall()
        for row in data:
            umls_code.append(row[0])

    # Input is ATC only
    if atc_code and not ndc_code and not umls_code:
        print("atc only")
        placeholder = ', '.join(['%s'] * len(atc_code))
        query = 'SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE IN ({})'.format(placeholder)
        cur.execute(query, tuple(atc_code))
        data = cur.fetchall()
        for row in data:
            ndc_code.append(row[0])

        query = 'SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ({})'.format(placeholder)
        cur.execute(query, tuple(atc_code))
        data = cur.fetchall()
        for row in data:
            umls_code.append(row[0])

    # Input is UMLS only
    if umls_code and not ndc_code and not atc_code:
        print("umls only")
        placeholder = ', '.join(['%s'] * len(umls_code))
        query = 'SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA IN ({}) LIMIT 1000'.format(placeholder)
        cur.execute(query, tuple(umls_code))
        data = cur.fetchall()
        for row in data:
            atc_code.append(row[0])

        placeholder = ', '.join(['%s'] * len(atc_code))
        query = 'SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE IN ({}) LIMIT 1000'.format(placeholder)
        cur.execute(query, tuple(atc_code))
        data = cur.fetchall()
        for row in data:
            ndc_code.append(row[0])

    # Input is NDC and ATC
    if ndc_code and atc_code and not umls_code:
        print("ndc and atc")
        # remove [ ] on the list
        ndc = ', '.join(repr(i) for i in ndc_code)
        atc = ', '.join(repr(i) for i in atc_code)
        if cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE IN ({}) AND ATC_CODE IN ({})".format(ndc, atc)):
            cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ({})".format(atc))
            data = cur.fetchall()
            for row in data:
                umls_code.append(row[0])

    # Input is NDC and UMLS
    if ndc_code and not atc_code and umls_code:
        print("ndc and umls")
        ndc = ', '.join(repr(i) for i in ndc_code)
        umls = ', '.join(repr(i) for i in umls_code)
        cur.execute("SELECT ndc_atc.ATC_CODE FROM ndc_atc INNER JOIN atc_umls ON ndc_atc.ATC_CODE = atc_umls.ATC_CODE WHERE NDC_CODE IN ({}) AND UMLSCUI_MEDDRA IN ({})".format(ndc, umls))
        data = cur.fetchall()
        for row in data:
            atc_code.append(row[0])

    # Input is ATC and UMLS
    if not ndc_code and atc_code and umls_code:
        print("atc and umls")
        atc = ', '.join(repr(i) for i in atc_code)
        umls = ', '.join(repr(i) for i in umls_code)
        if (cur.execute("SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA IN ({}) AND ATC_CODE IN ({})".format(umls, atc))):
            cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE IN ({})".format(atc))
            data = cur.fetchall()
            for row in data:
                ndc_code.append(row[0])

    # Remove Duplicates
    atc_code = list(set(atc_code))
    ndc_code = list(set(ndc_code))
    umls_code = list(set(umls_code))

    # NDC LABEL
    if ndc_code:
        placeholder = ', '.join(['%s'] * len(ndc_code))
        query = 'SELECT * FROM ndc_label WHERE NDC_CODE IN ({})'.format(placeholder)
        cur.execute(query, tuple(ndc_code))
        ndc_res = cur.fetchall()
    else:
        ndc_res = []

    # ATC LABEL
    if atc_code:
        placeholder = ', '.join(['%s'] * len(atc_code))
        query = 'SELECT * FROM atc_label WHERE ATC_CODE IN ({})'.format(placeholder)
        cur.execute(query, tuple(atc_code))
        atc_res = cur.fetchall()
    else:
        atc_res = []

    # UMLS LABEL
    if umls_code:
        placeholder = ', '.join(['%s'] * len(umls_code))
        query = 'SELECT DISTINCT * FROM umls_label WHERE UMLSCUI_MEDDRA IN ({})'.format(placeholder)
        cur.execute(query, tuple(umls_code))
        umls_res = cur.fetchall()
    else:
        umls_res = []

    return ndc_res, atc_res, umls_res



print("first route")
@webapp.route('/')
def search():
    return render_template('search.html')




print("second route")
@webapp.route('/', methods=['POST'])
def search_page():
    print("pre post request")
    if request.method == 'POST':
        # Input form requests
        print("pre inputs")
        ndc_in = request.form['ndc']
        atc_in = request.form['atc']
        umls_in = request.form['umls']

        print("inputted values: " + ndc_in + ", " + atc_in + ", " + umls_in)
        start_time = time.time()
        ndc_res, atc_res, umls_res = get_results(ndc_in, atc_in, umls_in)

        print("Program time: {}".format(time.time()- start_time))
        print(url_for('search', search_page=(ndc_in, atc_in, umls_in)))
        return render_template("search.html", ndc_codes=ndc_res, atc_codes=atc_res, umls_codes=umls_res, ndc_in=ndc_in,
                               atc_in=atc_in, umls_in=umls_in)

if __name__ == '__main__':
    webapp.run()
