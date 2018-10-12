import logging
import json
import configure as Conf
from apis.netease_music import NeteaseMusic
from apis.qq_music import QQMusic
from flask import Flask, Response, request, render_template

logging.basicConfig(level=Conf.LOG_LEVEL, format=Conf.LOG_FORMAT)
app = Flask(__name__)
app.jinja_env.auto_reload = True

err = {
    '404': '404.html'
}

platforms = ['netease', 'qq']
platform_to_class = {
    'netease': NeteaseMusic,
    'qq': QQMusic,
}


def exception_handler(err_type, msg=''):
    if msg:
        logging.exception("Exception_handler detects an error, type[{}], msg[{}].".format(err_type, msg))

    return render_template(err.get(str(err_type), '404.html'), msg=msg)


@app.route('/')
def api_index():
    return render_template('index.html')


@app.route('/api/search', methods=['GET'])
def api_searcher_raw():
    keyword = request.args.get('song_name', '')
    raw = request.args.get('raw', '')
    platform = request.args.get('platform', '')
    if keyword:
        music_res = []
        if platform in platforms:
            music_res = platform_to_class[platform]().func_search(keyword)
        else:
            for p in platform_to_class.values():
                music_res += p().func_search(keyword)

        if raw and raw is '1':
            return Response(json.dumps(music_res), mimetype='application/json')
        else:
            return render_template('search.html', audio_name=keyword, music_res_list=music_res)
    return exception_handler(404)


@app.route('/api/detail', methods=['GET'])
def api_detail_raw():
    song_id = request.args.get('id', '')
    raw = request.args.get('raw', '')
    platform = request.args.get('platform', '')
    if platform not in platforms:
        return exception_handler(404)

    if song_id:
        song_detail = platform_to_class[platform]().func_detail(song_id)
        if raw and raw is '1':
            return Response(json.dumps(song_detail), mimetype='application/json')
        else:
            return render_template('detail.html', song_detail=song_detail)
    return exception_handler(404)
