import logging

import configure as Conf
from apis.link_extractor import LinkExtractor
from flask import Flask, request

logging.basicConfig(level=Conf.LOG_LEVEL, format=Conf.LOG_FORMAT)
app = Flask(__name__)


@app.route('/api/link', methods=['GET'])
def api_link_extractor():
    keyword = request.args.get('audio_name', '')
    if keyword:
        return LinkExtractor(keyword)
    return None
