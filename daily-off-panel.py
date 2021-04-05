#!/usr/bin/env python
from string import digits

from flask import Flask, flash, redirect, render_template, \
    request, url_for

import requests
import psycopg2.extras
import rstr
from datetime import datetime, timedelta
import jalali
import jdatetime
from persiantools.jdatetime import JalaliDate
from persiantools import characters, digits

from flask import Flask
from waitress import serve
from psycopg2 import sql, extras

DB_HOST = '185.142.159.178'
DB_PORT = 12321
DB_NAME = 'basalam.ir'
DB_USER = 'marketing_lmtdr_mmohammadi'
DB_PASS = 'PE!y65qoy8>e>.FH?~Q+|de!.i3Lws<'
DB_SCHEMA = 'laravel'

ps_connection = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME,
                                 user=DB_USER, password=DB_PASS)
ps_cursor = ps_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
#ps_cursor.execute("SET search_path TO " + DB_SCHEMA)

app = Flask(__name__)
# @app.route('/api/v1/')
# def myendpoint():
#     return 'We are computering now'

@app.route('/')
def dailyoffpanel():
    return render_template("daily-off-panel2.html")


@app.route("/daily-off-panel", methods=['GET', 'POST'])
def test():
    dd = request

    Product_Id = request.form.get('Product_Id')
    Product_Id_split = Product_Id.split(",")
    new_Product_Id_split = []

    print('a')
    # exit(0)
    for e in Product_Id_split:
        for sub_e in e.split(","):
            new_Product_Id_split.append(int(sub_e))

    Daily_off_DateTime = request.form.get('Daily_off_DateTime')
    if Daily_off_DateTime == '':
        Daily_off_DateTime = datetime.min
    else:
        Date = Daily_off_DateTime[:-9]
        Time = Daily_off_DateTime[10:]
        Time = digits.fa_to_en(Time)
        Date_split = Date.split("-")
        Daily_off_DateTime = JalaliDate(int(Date_split[0]), int(Date_split[1]), int(Date_split[2])).to_gregorian()
        Daily_off_DateTime = str(Daily_off_DateTime) + Time
    Daily_Off_Category = request.form.get('Daily-Off_Category')
    Owner_Id = request.form.get('Owner_Id')

    # return (str(select))  # just to see what select is
    #segment = """
    #insert into bi.dailyoff_products (producer_id , created_at ) values (""" + Product_Id + """
    #, """ + Daily_off_DateTime + """ ) """

    new_Product_Id_split = tuple(new_Product_Id_split)

    #params = {'new_Product_Id_split': new_Product_Id_split}
    Products = get_Product(new_Product_Id_split, Daily_off_DateTime)
    if Products == []:
        Products.append(0)
    connect = None
    cur = None
    for p_id in Product_Id_split:

        connect = get_connection()
        cur = connect.cursor()
        if int(p_id) not in Products:
            #continue

            try:
                segment = """ INSERT INTO bi.dailyoff_products (product_id , created_at ,type ,tag) values  (%s,%s,%s,%s)"""
                record_to_insert = (int(p_id), Daily_off_DateTime , Daily_Off_Category , Owner_Id)


                cur.execute(segment, record_to_insert)

                connect.commit()
                count = cur.rowcount
                print(count, "Record inserted successfully into dailyoff_products table")
                #ps_cursor.executemany()
                # ps_cursor.execute(segment)
                # records = ps_cursor.fetchall()
            except (Exception, psycopg2.Error) as error:
                if connect:
                    print("Failed to insert record into mobile table", error)
            #finally:
                # closing database connection.
    if connect:
        cur.close()
        print("PostgreSQL connection is closed")

    return 'done!'

def get_connection():
    connection = None
    if not ps_connection or ps_connection.closed:
        connection = psycopg2.connect(user="marketing_lmtdr_mmohammadi",
                                      password="PE!y65qoy8>e>.FH?~Q+|de!.i3Lws<",
                                      host="185.142.159.178",
                                      port=12321,
                                      database="basalam.ir",
                                      connection_factory=extras.RealDictConnection)
        connection.autocommit = True
    else:
        connection = ps_connection
    return connection

def get_Product(Product_Id,Daily_off_DateTime):
    # INSERT SEGMENT QUERY
    try:
        # query = """
        #     select product_id from bi.dailyoff_products where created_at = ? and product_id in (?)
        # """
        # record_to_insert = (Daily_off_DateTime, Product_Id)
        connect = get_connection()
        cur = connect.cursor()
        cur.execute(
            'select product_id from bi.dailyoff_products where created_at = %s and product_id in %s'
        , (Daily_off_DateTime, Product_Id))

        res = cur.fetchall()
        if res:
            return [i[0] for i in res]
        return res
    except(Exception, psycopg2.Error) as error:
        print("can't get Products")


if __name__ == '__main__':
    app.run(debug=True , host='0.0.0.0',port=8081)#, host='0.0.0.0'

    #serve(app, host='172.16.10.170', port=8080, threads=1) #WAITRESS!
    serve(app, host='127.0.0.1', port=4000, threads=1) #WAITRESS!
