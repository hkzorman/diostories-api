import json
import logging
import os
import sys

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

diostories = {}

# TODO: Add logging

# Initialization - make sure uploads directory exists
uploadPath = os.path.join(app.root_path, 'uploads', 'assets', 'img')
if not os.path.exists(uploadPath):
	os.makedirs(uploadPath)

# Load diostories file
try:
    data_file = open("data.json", "x")
except:
    # file already exists, let's read it
    data_file = open("data.json")
    contents = data_file.read()
    if contents:
        diostories = json.loads(contents)
finally:
    pass
    #logger.info("Loaded diostories from file")

@app.route('/')
def hello():
    return "OK"

# Serves images from the uploaded directory
@app.route('/img/<path:path>')
def serve_image(path):
    root = os.path.join(app.root_path, 'uploads')
    return send_from_directory(root, path)

@app.route('/save', methods=['POST'])
def save():
    global diostories

    data = request.get_json(force=True)
    print(data, file=sys.stderr)
    #app.logger.info(f"Received data: {data}")
    if (data != None):
        diostory = data['payload']

        # Find max key for diostory
        max_id = 0
        for key in diostories:
            intKey = int(key)
            if intKey > max_id:
                max_id = intKey
        
        id = max_id
        if ("id" in diostory):
            id = diostory["id"]

        # Save diostory
        diostories[id] = {
            "title": diostory["title"],
            "panels": diostory["panels"]
        }

        # Save playlists into file
        data_file = open("data.json", "w")
        data_file.write(json.dumps(diostories))

        #app.logger.info(f"Succesfully added playlist {name} with {len(items)} items")
        #logger.info(f"Saved diostory")

        return jsonify({
            "success": True
        })

    return jsonify({
        "success": False
    })

@app.route('/list')
def list():
    global diostories
    result = []
    for key in diostories:
        print("This is the key: ", key, file=sys.stderr)
        result.append({
            "id" : key, 
            "title": diostories[key]["title"]
        })

    return jsonify(result)

@app.route('/get/<id>')
def get(id):
    global diostories
    result = {}
    if (id not in diostories):
        return jsonify({
            "success": False,
            "message": "ID is not valid"
        })
    
    return jsonify(diostories[id])

@app.route('/uploadImage', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        path = os.path.join(app.root_path, 'uploads', 'assets', 'img', secure_filename(file.filename))
        file.save(f"{path}")
        return jsonify({
            "success": True,
            "url": f"/assets/img/{secure_filename(file.filename)}"
        })

    return jsonify({
        "success": False,
        "message": "Use a POST method to upload."
    })
