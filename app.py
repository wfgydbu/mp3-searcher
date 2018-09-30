import logging
import json
import configure as Conf
from apis.netease_music import NeteaseMusic
from flask import Flask, Response, request

logging.basicConfig(level=Conf.LOG_LEVEL, format=Conf.LOG_FORMAT)
app = Flask(__name__)


@app.route('/api/search', methods=['GET'])
def api_link_extractor():
    keyword = request.args.get('audio_name', '')
    if keyword:
        netease_music_res = NeteaseMusic().func_search(keyword)
        return Response(json.dumps(netease_music_res), mimetype='application/json')

    return Response('{}', mimetype='application/json')
