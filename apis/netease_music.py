import base64
import codecs
import hashlib
import math
import random

import requests
from base import BaseTemplate
from Crypto.Cipher import AES


class NeteaseEncryptionScheme(object):
    '''
    NeteaseMusic的加密框架，直接调用encrypt即可。
    加密的对象是js中的变量d，需要在chrome中调试才能获取。
    之所以选择自己实现而不是直接调用js是因为后者不能兼容中文搜索词（和padding有关）。
    加密部分参考：https://github.com/pengshiqi/NetEaseMusicCrawl/blob/master/NetEaseMusicCrawl.py，略作修改。
    '''

    def __init__(self):
        self.pubkey = '010001'
        self.modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.nouce = '0CoJUm6Qyw8W8jud'
        self.random_padding = self.__get_random_padding()

    def __get_random_padding(self):
        str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        res = ''
        for x in range(16):
            index = math.floor(random.random() * len(str))
            res += str[index]
        return res

    def __aes_encrypt(self, text, key):
        iv = '0102030405060708'
        pad = 16 - len(text.encode('utf-8')) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypted_text = base64.b64encode(encryptor.encrypt(text))
        return encrypted_text

    def __rsa_encrypt(self):
        text = self.random_padding[::-1]
        rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(self.pubkey, 16) % int(self.modulus, 16)
        return format(rs, 'x').zfill(256)

    def encrypt(self, text):
        params = self.__aes_encrypt(text, self.nouce)
        params = self.__aes_encrypt(params.decode('utf-8'), self.random_padding)
        encSecKey = self.__rsa_encrypt()
        return {
            'params': params,
            'encSecKey': encSecKey
        }


class NeteaseMusic(BaseTemplate):
    def __init__(self):
        with open('asserts/netease.js', 'r') as f:
            self.js = f.read()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Referer': 'https://music.163.com/'
        }
        self.func_search = self.get_search_list_by_keyword
        self.func_link = self.get_song_link_by_id
        self.func_detail = self.get_song_detail_by_id

    def __get_id_md5(self, id):
        if not id:
            return None

        h = hashlib.md5()
        h.update(str(id).encode(encoding='utf-8'))
        return h.hexdigest()

    def __get_json(self, url, formdata=None, headers=None):
        if not headers:
            headers = self.headers

        resp = requests.post(url, headers=headers, data=formdata) if formdata else requests.post(url, headers=headers)

        if resp.status_code != requests.codes.ok or not resp.text:
            print("Request Failed. Info: [{}]".format(resp.text))
            return None

        return resp.json()

    def get_search_list_by_keyword(self, keyword):
        url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        formdata = NeteaseEncryptionScheme().encrypt('{"hlpretag":"<span class=\\"s-fc7\\">","hlposttag":"</span>","s":"%s","type":"1","offset":"0","total":"true","limit":"30","csrf_token":""}' % keyword)

        songCount = self.__get_json(url, formdata)['result'].get('songCount', '')
        if not songCount or int(songCount) == 0:
            return None

        songs = self.__get_json(url, formdata)['result']['songs']
        ret = []
        for song in songs:
            dict = {}
            dict['id'] = song['id']
            dict['ar'] = '/'.join([ar['name'] for ar in song['ar']])
            dict['name'] = song['name']
            ret.append(dict)

        return {'list': ret}

    def get_song_link_by_id(self, id):
        url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token='
        headers = dict({
            'Cookie': '_ntes_nuid=%s' % self.__get_id_md5(id)
        }, **self.headers)

        formdata = NeteaseEncryptionScheme().encrypt('{"ids":"[%s]","br":128000,"csrf_token":""}' % id)

        ret = self.__get_json(url, formdata, headers)
        return {'url': ret['data'][0]['url']} if ret else None

    def get_song_detail_by_id(self, id):
        url = 'https://music.163.com/api/song/detail/?id=%s&ids=[%s]&csrf_token=' % (id, id)

        ret = self.__get_json(url)
        return ret['songs'][0] if ret else None


if __name__ == '__main__':
    print(NeteaseMusic().get_search_list_by_keyword('折子戏'))
    # print(NeteaseMusic().get_song_detail_by_id('440464202'))
    # print(NeteaseMusic().get_song_link_by_id('440464202'))
