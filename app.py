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


# Converts text input to code. Ignore whitespaces and invalid entries
def text_to_code(ndc_in, atc_in, umls_in):
    print("\nFunction: text_to_code(ndc_in, atc_in, umls_in)")
    start_time = time.time()
    ndc_code = []
    atc_code = []
    umls_code = []

    print("NDC: {}, {}".format(not ndc_in.isspace(), bool(ndc_in)))
    # IF ndc_in is not a space and ndc_in is not empty
    # isspace() returns true if str is a space
    if not ndc_in.isspace() and ndc_in:
        ndc_code = [ndc_in]
        query = "SELECT NDC_CODE FROM ndc_label WHERE STR_NDC LIKE '%{}%' OR NDC_CODE LIKE '%{}%'".format(ndc_code[0], ndc_code[0])
        if cur.execute(query):
            print("NDC conversion")
            data = cur.fetchall()
            ndc_code = [i[0] for i in data]  # Convert from tuple to list
        if cur.execute(query) == 0:
            ndc_code = []

    print("ATC: {}, {}".format(not atc_in.isspace(), bool(atc_in)))
    if not atc_in.isspace() and atc_in:
        atc_code = [atc_in]
        query = "SELECT ATC_CODE FROM atc_label WHERE STR_IN LIKE '%{}%' OR ATC_CODE LIKE '%{}%'".format(atc_code[0], atc_code[0])
        if cur.execute(query):
            print("ATC conversion")
            data = cur.fetchall()
            atc_code = [i[0] for i in data]
        if cur.execute(query) == 0:
            atc_code = []

    print("UMLS: {}, {}".format(not umls_in.isspace(), bool(umls_in)))
    if not umls_in.isspace() and umls_in:
        umls_code = [umls_in]
        query = "SELECT DISTINCT UMLSCUI_MEDDRA FROM umls_label WHERE SIDE_EFFECT_NAME LIKE '%{}%' OR UMLSCUI_MEDDRA LIKE '%{}%'".format(umls_code[0], umls_code[0])
        if cur.execute(query):
            print("UMLS conversion")
            data = cur.fetchall()
            umls_code = [i[0] for i in data]
        if cur.execute(query) == 0:
            umls_code = []

    print("Return values:\nNDC {}\nATC {}\nUMLS {}".format(ndc_code, atc_code, umls_code))
    print("Function time: {}".format(time.time() - start_time))
    return ndc_code, atc_code, umls_code


# Get code outputs from text_to_code and process the inputs.
def get_results(ndc_in, atc_in, umls_in):
    ndc_code, atc_code, umls_code = text_to_code(ndc_in, atc_in, umls_in)
    start_time = time.time()

    print("\nFunction: get_results(ndc_in, atc_in, umls_in) after calling text_to_code")
    print("Converted inputs:\nNDC {}\nATC {}\nUMLS {}".format(ndc_code, atc_code, umls_code))
    print("NDC: {}, ATC: {}, UMLS: {}".format(bool(ndc_code), bool(atc_code), bool(umls_code)))

    # Input is NDC only
    if ndc_code and not atc_code and not umls_code:
        # if there are also inputs for ats or umls, put it on array to show results for those inputs
        print("NDC only")
        if atc_in and not atc_in.isspace():
            atc_code = [atc_in]
        else:
            placeholder = ', '.join(['%s'] * len(ndc_code))
            query = 'SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE IN ({})'.format(placeholder)
            cur.execute(query, tuple(ndc_code))
            data = cur.fetchall()
            for row in data:
                atc_code.append(row[0])

        if umls_in and not umls_in.isspace():
            umls_code = [umls_in]
        else:
            placeholder = ', '.join(['%s'] * len(atc_code))
            query = 'SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ({})'.format(placeholder)
            cur.execute(query, tuple(atc_code))
            data = cur.fetchall()
            for row in data:
                umls_code.append(row[0])

    # Input is ATC only
    elif atc_code and not ndc_code and not umls_code:
        print("ATC only")
        if ndc_in and not ndc_in.isspace():
            ndc_code = [ndc_in]
        else:
            placeholder = ', '.join(['%s'] * len(atc_code))
            query = 'SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE IN ({})'.format(placeholder)
            cur.execute(query, tuple(atc_code))
            data = cur.fetchall()
            for row in data:
                ndc_code.append(row[0])

        if umls_in and not umls_in.isspace():
            umls_code = [umls_in]
        else:
            query = 'SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ({})'.format(placeholder)
            cur.execute(query, tuple(atc_code))
            data = cur.fetchall()
            for row in data:
                umls_code.append(row[0])

    # Input is UMLS only
    elif umls_code and not ndc_code and not atc_code:
        print("UMLS only")
        if atc_in and not atc_in.isspace():
            atc_code = [atc_in]
        else:
            placeholder = ', '.join(['%s'] * len(umls_code))
            query = 'SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA IN ({}) LIMIT 1000'.format(placeholder)
            cur.execute(query, tuple(umls_code))
            data = cur.fetchall()
            for row in data:
                atc_code.append(row[0])

        if ndc_in and not ndc_in.isspace():
            ndc_code = [ndc_in]
        else:
            placeholder = ', '.join(['%s'] * len(atc_code))
            query = 'SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE IN ({}) LIMIT 1000'.format(placeholder)
            cur.execute(query, tuple(atc_code))
            data = cur.fetchall()
            for row in data:
                ndc_code.append(row[0])

    # Input is NDC and ATC
    elif ndc_code and atc_code and not umls_code:
        print("NDC and ATC")
        # remove [ ] on the list
        if umls_in and not umls_in.isspace():
            umls_code = [umls_in]
        else:
            ndc = ', '.join(repr(i) for i in ndc_code)
            atc = ', '.join(repr(i) for i in atc_code)
            if cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE IN ({}) AND ATC_CODE IN ({})".format(ndc, atc)):
                cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ({})".format(atc))
                data = cur.fetchall()
                for row in data:
                    umls_code.append(row[0])

    # Input is NDC and UMLS
    elif ndc_code and not atc_code and umls_code:
        print("NDC and UMLS")
        if atc_in and not atc_in.isspace():
            atc_code = [atc_in]
        else:
            ndc = ', '.join(repr(i) for i in ndc_code)
            umls = ', '.join(repr(i) for i in umls_code)
            cur.execute("SELECT ndc_atc.ATC_CODE FROM ndc_atc INNER JOIN atc_umls ON ndc_atc.ATC_CODE = atc_umls.ATC_CODE WHERE NDC_CODE IN ({}) AND UMLSCUI_MEDDRA IN ({})".format(ndc, umls))
            data = cur.fetchall()
            for row in data:
                atc_code.append(row[0])

    # Input is ATC and UMLS
    elif not ndc_code and atc_code and umls_code:
        print("ATC and UMLS")
        if ndc_in and not ndc_in.isspace():
            ndc_code = [ndc_in]
        else:
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
    print("\nRemove Duplicates (resulting codes)")
    print("NDC {}\nATC {}\nUMLS {}".format(ndc_code, atc_code, umls_code))

    # Statements below will convert codes into text. name_res variables are tuples[][]
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

    print("Function time: {}".format(time.time() - start_time))
    return ndc_res, atc_res, umls_res


@webapp.route('/')
def search():
    print("first route")
    return render_template('search.html')


@webapp.route('/', methods=['POST'])
def search_page():
    print("second route")
    print("pre post request")
    if request.method == 'POST':
        # Input form requests
        print("pre inputs")
        ndc_in = request.form['ndc']
        atc_in = request.form['atc']
        umls_in = request.form['umls']

        print("Input values: " + ndc_in + ", " + atc_in + ", " + umls_in)
        start_time = time.time()
        ndc_res, atc_res, umls_res = get_results(ndc_in, atc_in, umls_in)

        print("\nProgram time: {}".format(time.time()- start_time))
        print(url_for('search', search_page=(ndc_in, atc_in, umls_in)))
        return render_template("search.html", ndc_codes=ndc_res, atc_codes=atc_res, umls_codes=umls_res, ndc_in=ndc_in,
                               atc_in=atc_in, umls_in=umls_in)

if __name__ == '__main__':
    webapp.run()
