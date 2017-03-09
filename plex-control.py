import urllib2, os, sys, json
from flask import Flask, jsonify, request
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring
import requests

CONFIG_FILE = 'config.json'

app = Flask(__name__)

def open_and_load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        print "File [%s] doesn't exist, aborting." % (CONFIG_FILE)
        sys.exit(1)

@app.route("/")
def hello():
    url = config['plex-url']
    params = {"X-Plex-Token": config['plex-token']}
    r = requests.get(url, params=params)
    res = bf.data(fromstring(r.text))
    m = res["MediaContainer"]
    datas = {
        "mapping": m["@myPlexMappingState"],
        "sync": m["@sync"],
        "sessions": m["@transcoderActiveVideoSessions"]
    }
    return jsonify(datas)

@app.route("/servers")
def server():
    url = config['plex-url'] + "servers"
    params = {"X-Plex-Token": config['plex-token']}
    r = requests.get(url, params=params)
    res = bf.data(fromstring(r.text))
    return jsonify(res)

@app.route("/status")
def status():
    url = config['plex-url'] + "status/sessions"
    params = {"X-Plex-Token": config['plex-token']}
    r = requests.get(url, params=params)
    res = bf.data(fromstring(r.text))
    datas = []
    s = res["MediaContainer"]["@size"]
    for v in res["MediaContainer"]["Video"]:
        tmp = {"title":v["@title"],
                      "kind":v["@type"],
                      "user":v["User"]["@title"],
                      "player":v["Player"]["@title"],
                      "state":v["Player"]["@state"],
                      "address":v["Player"]["@address"],
                      "media":v["Media"]["Part"]["@file"]
           }
        if (v["@type"] == "episode" and "@grandparentTitle" in v):
            tmp['title'] = v["@grandparentTitle"]
            if ("@parentIndex" in v and "@index" in v):
                tmp['title'] = tmp['title'] + " S" + str(v["@parentIndex"]) + "E" + str(v["@index"]) + " " + v["@title"]
        datas.append(tmp)
    return jsonify(datas)

@app.route("/sessions")
def sessions():
    url = config['plex-url'] + "status/sessions"
    params = {"X-Plex-Token": config['plex-token']}
    r = requests.get(url, params=params)
    res = bf.data(fromstring(r.text))
    return jsonify(res)

if __name__ == "__main__":
    config = open_and_load_config()
    app.run(host="0.0.0.0", port=5000)
