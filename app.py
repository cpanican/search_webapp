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

        if ndc_in:
            ndc_code.append(ndc_in)
            print("ndc_in: " + ndc_in)
        if atc_in:
            atc_code.append(atc_in)
            print("atc_in: " + atc_in)
        if umls_in:
            umls_code.append(umls_in)
            print("umls_in: " + umls_in)

        # Input is NDC only
        if ndc_in and not atc_in and not umls_in:
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
        if atc_in and not ndc_in and not umls_in:
            print("atc only")
            placeholder = ', '.join(['%s']*len(atc_code))
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
        if umls_in and not ndc_in and not atc_in:
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
        if ndc_in and atc_in and not umls_in:
            print("ndc and atc")
            if cur.execute("SELECT ATC_CODE FROM ndc_atc WHERE NDC_CODE = '{}' AND ATC_CODE = '{}'".format(ndc_in, atc_in)):
                cur.execute("SELECT UMLSCUI_MEDDRA FROM atc_umls WHERE ATC_CODE IN ('{}')".format(atc_in))
                data = cur.fetchall()
                for row in data:
                    umls_code.append(row[0])

        # Input is NDC and UMLS
        if ndc_in and not atc_in and umls_in:
            print("ndc and umls")
            cur.execute("SELECT ndc_atc.ATC_CODE FROM ndc_atc INNER JOIN atc_umls ON ndc_atc.ATC_CODE = atc_umls.ATC_CODE WHERE NDC_CODE = '{}' AND UMLSCUI_MEDDRA = '{}'".format(ndc_in, umls_in))
            data = cur.fetchall()
            for row in data:
                atc_code.append(row[0])

        # Input is ATC and UMLS
        if not ndc_in and atc_in and umls_in:
            print("atc and umls")
            if (cur.execute("SELECT ATC_CODE FROM atc_umls WHERE UMLSCUI_MEDDRA = '{}' AND ATC_CODE = '{}'".format(umls_in, atc_in))):
                cur.execute("SELECT NDC_CODE FROM ndc_atc WHERE ATC_CODE IN ('{}')".format(atc_in))
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

        return render_template("search.html", ndc_codes=ndc_res, atc_codes=atc_res, umls_codes=umls_res, ndc_in=ndc_in,
                               atc_in=atc_in, umls_in=umls_in)

if __name__ == '__main__':
    webapp.run()
