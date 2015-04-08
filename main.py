#qpy:webapp:Wetroads map
#qpy:fullscreen
#qpy://localhost:8080/

import json
import androidhelper
import csv
from bottle import route, run, template, static_file, request

#workingdir = os.getcwd()
workingdir = "/sdcard/com.hipipal.qpyplus/projects/wetroads"

# CSV downloaded from wetroads.co.uk
import sqlite3

helper = androidhelper.Android()

fordtypes = {1: "icon/suitableforall.png",
            2: "icon/irishbridge.png",
            3: "icon/4by4.png",
            4: "icon/restricted.png"}

def assignicon(index):
    try:
        return fordtypes[int(index)]
    except:
        return "icon/unknown.png"

conn = sqlite3.connect(workingdir + "/fords.db")
cur = conn.cursor()
try:
    cur.execute("CREATE TABLE fords (LA real, LO real, CLASS text, NAME text, GRADE real);")

    def s(string):
        return float(string.strip("'"))

    with open(workingdir+'/Fords.csv', 'rb') as f:
        dr = csv.DictReader(f)
        to_db = [(s(i['LA']), s(i['LO']), assignicon(i['CLASS']), i['NAME'], s(i['GRADE'])) for i in dr if i['LA'] != ""]

    cur.executemany("INSERT INTO fords (LA, LO, CLASS, NAME, GRADE) VALUES (?, ?, ?, ?, ?);", to_db)
    conn.commit()
    print "created sql db"
except:
    print "using already present db"
    pass

cur.execute('SELECT * FROM fords ORDER BY GRADE DESC')
coords = cur.fetchall()[:200]


@route('/')
def index():
    global coords
    try:
        left = request.query["left"]
        bottom = request.query["bottom"]
        right = request.query["right"]
        top = request.query["top"]
        cur.execute('SELECT * FROM fords where LO>'+left+' AND LO<'+right+' AND LA>'+bottom+' AND LA<'+top+' ORDER BY GRADE DESC')
        coords = cur.fetchall()
    except:
        pass
    coords = helper.getLastKnownLocation()
    longitude = coords.result["passive"]["longitude"]
    latitude = coords.result["passive"]["latitude"]
    return template(open(workingdir+"/template.html").read(), longitude = longitude, latitude = latitude)

@route('/locations')
def locations():
    left = request.query["left"]
    bottom = request.query["bottom"]
    right = request.query["right"]
    top = request.query["top"]
    cur.execute('SELECT * FROM fords where LO>'+left+' AND LO<'+right+' AND LA>'+bottom+' AND LA<'+top+' ORDER BY GRADE DESC')
    locations = cur.fetchall()[:200]
    jsonobj = json.dumps(locations)
    return jsonobj


@route('/icon/<filename>')
def icon(filename):
    return static_file(filename, root=workingdir)


if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 8080))
    run(host='localhost', port=8080)

