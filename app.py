import logging
import json
import configure as Conf
from apis.netease_music import NeteaseMusic
from flask import Flask, Response, request, render_template

logging.basicConfig(level=Conf.LOG_LEVEL, format=Conf.LOG_FORMAT)
app = Flask(__name__)
app.jinja_env.auto_reload = True


@app.route('/')
def api_index():
    return render_template('index.html')


@app.route('/api/raw/search', methods=['GET'])
def api_searcher_raw():
    keyword = request.args.get('audio_name', '')
    if keyword:
        netease_music_res = NeteaseMusic().func_search(keyword)
        return Response(json.dumps(netease_music_res), mimetype='application/json')
    return render_template('404.html')


@app.route('/api/search', methods=['GET'])
def api_searcher():
    keyword = request.args.get('audio_name', '')
    if keyword:
        netease_music_res = NeteaseMusic().func_search(keyword)
        return render_template('search.html', audio_name=keyword, music_res_dict=netease_music_res)
    return render_template('404.html')


@app.route('/api/raw/url', methods=['GET'])
def api_url_raw():
    song_id = request.args.get('id', '')
    if song_id:
        download_url = NeteaseMusic().func_link(song_id)
        return Response(json.dumps(download_url), mimetype='application/json')
    return render_template('404.html')


@app.route('/api/url', methods=['GET'])
def api_url():
    song_id = request.args.get('id', '')
    if song_id:
        download_url = NeteaseMusic().func_link(song_id)
        if download_url['url']:
            return render_template('url.html', download_url=download_url['url'])

    return render_template('404.html')


@app.route('/api/raw/detail', methods=['GET'])
def api_detail_raw():
    song_id = request.args.get('id', '')
    if song_id:
        song_detail = NeteaseMusic().func_detail(song_id)
        return Response(json.dumps(song_detail), mimetype='application/json')
    return render_template('404.html')


@app.route('/api/detail', methods=['GET'])
def api_detail():
    song_id = request.args.get('id', '')
    if song_id:
        song_detail = NeteaseMusic().func_detail(song_id)
        if song_detail:
            return render_template('detail.html', song_detail=song_detail)

    return render_template('404.html')
