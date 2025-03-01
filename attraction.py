from flask import *
site = Blueprint('attraction', __name__)
from numpy import integer
import json
import pymysql
import pymysql.cursors
from dbutils.pooled_db import PooledDB
import ast
pymysql.install_as_MySQLdb()
from collections import OrderedDict
import os
from urllib import response
import sys, traceback
from flask_jwt_extended import *
import member

# connect to the local DB
pool = PooledDB(creator=pymysql, host = "127.0.0.1", user = "root", password="12345678", database='website', port= 3306)


"""
# conenct the pool
conn = pool.get_conn()
cursor = conn.cursor()

# create a table in the database
sql="CREATE TABLE IF NOT EXISTS TPtrip (id INT AUTO_INCREMENT, info VARCHAR(255), stitle VARCHAR(10) UNIQUE, longitude VARCHAR(10), latitude VARCHAR(10), MRT VARCHAR(10), CAT2 VARCHAR(10), MEMO_TIME LONGTEXT, file LONGTEXT, xbody LONGTEXT, address VARCHAR(255), PRIMARY KEY (id))"
cursor.execute(sql)
# release the connection back to the pool for reuse
pool.release(conn)
cursor.close()

# conenct the pool
conn = pool.get_conn()
cursor = conn.cursor()

sql = "ALTER TABLE TPtrip AUTO_INCREMENT=1"
cursor.execute(sql)
# release the connection back to the pool for reuse
pool.release(conn)
cursor.close()


# import the JSON file
with open('data/taipei-attractions.json', 'r') as f:   	
    data = json.load(f)
# attraction list
dataList = data["result"]["results"] 

# insert values into database without duplicate values
sql = "INSERT IGNORE INTO TPtrip (info, stitle , longitude, latitude, MRT, CAT2, MEMO_TIME, file, xbody, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %r, %s, %s)"

# add the data into the database
for k in range(len(dataList)):
    image =  ["https" + e for e in dataList[k]["file"].split("https") if e]
    # conenct the pool
    conn = pool.get_conn()
    cursor = conn.cursor()
	# filter out URLs which are not ended with jpg or png
    for i in image:
        if not (i.endswith("JPG") or i.endswith("jpg") or i.endswith("png") or i.endswith("PNG")):
            image.remove(i)
    val = (dataList[k]["info"], dataList[k]["stitle"], dataList[k]["longitude"], dataList[k]["latitude"], dataList[k]["MRT"], dataList[k]["CAT2"], dataList[k]["MEMO_TIME"],image, dataList[k]["xbody"], dataList[k]["address"])
    cursor.execute(sql, val)
    conn.commit()
    # release the connection back to the pool for reuse
    pool.release(conn)
    cursor.close()
"""


@site.route("/api/attractions", methods=["GET"])
def attractionAPI():
	# API parameter: page & keyword
    keyword = request.args.get('keyword')
    page = int(float(request.args.get("page")))
    # if there is a keyword
    if keyword != None and keyword != "":
        # conenct the pool
        conn = pool.connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id,stitle,CAT2,xbody,address,info,MRT,latitude,longitude,file FROM website.TPtrip WHERE stitle LIKE %s LIMIT %s, %s",(("%"+str(keyword)+"%"),(page+1)*12-12,(page+1)*12))
        result = cursor.fetchall()
        dataLen = len(result)
        rowcount = cursor.rowcount
        # the organized result
        finalResult = []
        for site in result:
            data = OrderedDict(id = site[0], name = site[1], category = site[2], description = site[3], address = site[4], transport = site[5], mrt = site[6], latitude = site[7], longitude = site[8], images = site[9])
            # convert the set of images to a list
            data["images"] =  data["images"].split(',')
            finalResult.append(data)
        if dataLen > 0:
            # output
            if rowcount < 12 :
                return jsonify({"nextPage": None, 'data' : finalResult}) 
            else:
                return jsonify({"nextPage": page+1, 'data' : finalResult}) 
        # release the connection back to the pool for reuse
        conn.close()
        cursor.close()       
        return jsonify({"error":True, "message": "No relevant data"})
    # if there is no input of keyword
    else:
        if page == None:
            page = 0
        conn = pool.connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id,stitle,CAT2,xbody,address,info,MRT,latitude,longitude,file FROM website.TPtrip LIMIT %s, %s",((page+1)*12-11,(page+1)*12))
        result = cursor.fetchall()
        # release the connection back to the pool for reuse
        conn.close()
        cursor.close()
        dataLen = len(result)
        rowcount = cursor.rowcount
        # the organized result
        finalResult = []
        # convert the set of images to a list
        for site in result:
            data = OrderedDict(id = site[0], name = site[1], category = site[2], description = site[3], address = site[4], transport = site[5], mrt = site[6], latitude = site[7], longitude = site[8], images = site[9])
            # convert the set of images to a list
            data["images"] =  data["images"].split(',')
            finalResult.append(data)
        if dataLen > 0:
            # output
            if rowcount < 12 :
                return jsonify({"nextPage": None, 'data' : finalResult}) 
            else:
                return jsonify({"nextPage": page+1, 'data' : finalResult})
        return jsonify({"error":True, "message": "No relevant data"})
		

@site.route("/api/attraction/<attractionId>", methods=["GET"])
def attractionIdApi(attractionId):
    try:
        # conenct the pool
        conn = pool.connection()
        cursor = conn.cursor()
	    # API parameter: page & keyword
        cursor.execute("SELECT id,stitle,CAT2,xbody,address,info,MRT,latitude,longitude,file FROM website.TPtrip WHERE id = %s",(attractionId))
        site=cursor.fetchone()
        if site != 0:   
            finalResult = {"data":OrderedDict(id = site[0], name = site[1], category = site[2], description = site[3], address = site[4], transport = site[5], mrt = site[6], latitude = site[7], longitude = site[8], images = site[9])}
            # convert the set of images to a list
            finalResult["data"]["images"] = finalResult["data"]["images"].split(',')
            return jsonify(finalResult)
    except:
        return jsonify({"error":True,"message":"No relevant data"})
    finally:
       # release the connection back to the pool for reuse
        conn.close()
        cursor.close()
