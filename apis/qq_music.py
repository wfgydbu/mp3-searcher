import requests
import random
import re
import json
from apis.base import BaseTemplate


class QQMusic(BaseTemplate):
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
            'Cookie': 'pgv_pvid={}'.format(int(random.random() * 1e10))
        }
        self.func_search = self.get_search_list_by_keyword
        self.func_detail = self.get_song_detail_by_id
        self.func_lyric = self.get_song_lyric_by_id

    def get_search_list_by_keyword(self, keyword):
        url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
        cb_fn_name = 'MusicJsonCallback{}'.format(int(random.random() * 1e17))
        params = {
            'cr': 1,
            'w': keyword,
            'p': 1,
            'n': 5,
            'format': 'jsonp',
            'jsonpCallback': cb_fn_name,
        }

        response = requests.get(url, headers=self.headers, params=params)
        page_json = re.findall(re.compile('{}\((.*?)\)$'.format(cb_fn_name)), response.text)
        if not page_json:
            return None

        songs = json.loads(page_json[0])['data']['song']['list']
        ret = []
        for song in songs:
            dict = {}.fromkeys(self.SEARCH_RES_FIELDS)
            dict['id'] = song['songmid']
            dict['ar'] = '/'.join([ar['name'] for ar in song['singer']])
            dict['name'] = song['songname']
            dict['source'] = 'qq'
            ret.append(dict)

        return ret

    def get_song_detail_by_id(self, id):
        url = 'https://i.y.qq.com/v8/playsong.html?ADTAG=newyqq.song&songmid={}'.format(id)

        response = requests.get(url, headers=self.headers)
        page_json = re.findall(re.compile('songlist = \[(.*?)\];'), response.text)
        if not page_json:
            return None

        song_detail = json.loads(page_json[0])
        dict = {}.fromkeys(self.SONG_DETAIL_FIELDS)
        dict['source'] = 'qqmusic'
        dict['id'] = song_detail.get('songid')
        dict['song_name'] = song_detail.get('songname')
        dict['song_url'] = self.pretend_https(song_detail.get('m4aUrl'))
        dict['song_pic'] = self.pretend_https(song_detail.get('pic'))
        dict['song_lyric'] = self.get_song_lyric_by_id(id)
        dict['song_interval'] = song_detail.get('interval')
        dict['ablum_id'] = song_detail.get('albumid')
        dict['ablum_name'] = song_detail.get('albumname')
        # dict['ablum_pic'] = song_detail.get('')
        # dict['ablum_intro'] = song_detail.get('')
        artists = []
        for artist in song_detail['singer']:
            t_dict = {}.fromkeys(self.SONG_ARTIST_FIELDS)
            t_dict['artist_id'] = artist['id']
            t_dict['artist_name'] = artist['name']
            # t_dict['artist_pic'] = artist['picUrl']
            # t_dict['artist_intro'] = artist['briefDesc']
            artists.append(t_dict)
        dict['artists'] = artists
        return dict

    def get_song_lyric_by_id(self, id):
        # TODO
        return None


if __name__ == "__main__":
    # ret = QQMusic().get_search_list_by_keyword('umbrella')
    ret = QQMusic().get_song_detail_by_id('00198fE71wxV4M')
    print(ret)
