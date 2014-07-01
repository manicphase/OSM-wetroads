import json
import os
import csv
from bottle import route, run, template, static_file, request

workingdir = os.getcwd()

# CSV downloaded from wetroads.co.uk
import csv
import sqlite3


fordtypes = {1: "icon/suitableforall.png",
            2: "icon/irishbridge.png",
            3: "icon/4by4.png",
            4: "icon/restricted.png"}

def assignicon(index):
    try:
        return fordtypes[int(index)]
    except:
        return "icon/unknown.png"

conn = sqlite3.connect(":memory:")
cur = conn.cursor()
cur.execute("CREATE TABLE fords (LA real, LO real, CLASS text, NAME text, GRADE real);")

def s(string):
    return float(string.strip("'"))

with open('Fords.csv', 'rb') as f:
    dr = csv.DictReader(f)
    to_db = [(s(i['LA']), s(i['LO']), assignicon(i['CLASS']), i['NAME'], s(i['GRADE'])) for i in dr if i['LA'] != ""]

cur.executemany("INSERT INTO fords (LA, LO, CLASS, NAME, GRADE) VALUES (?, ?, ?, ?, ?);", to_db)
conn.commit()

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
        locations = cur.fetchall()
    except:
        pass
    return template(open("template.html").read(), coords = coords)
    
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
    port = int(os.environ.get('PORT', 8080))
    run(host='0.0.0.0', port=port, debug=True)
