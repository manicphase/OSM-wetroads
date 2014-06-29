import os
import csv
from bottle import route, run, template, static_file

workingdir = os.getcwd()

# CSV downloaded from wetroads.co.uk
fordtypes = {1: "icon/suitableforall.png",
            2: "icon/irishbridge.png",
            3: "icon/4by4.png",
            4: "icon/restricted.png"}
            
def assignicon(index):
    try:
        return fordtypes[int(index)]
    except:
        return "icon/unknown.png"

coords = []
with open('Fords.csv', 'rb') as f:
    reader = csv.reader(f)
    reader.next()
    for row in reader:
        if row[0] != "":
            coords.append([row[3], row[2], assignicon(row[8])])

@route('/')
def index():
    return template(open("template.html").read(), coords = coords)
    
@route('/icon/<filename>')
def icon(filename):
    return static_file(filename, root=workingdir)
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    run(host='0.0.0.0', port=port, debug=True)
