class BaseTemplate(object):
    def __init__(self):
        self.func_search = None
        self.func_detail = None
        self.func_lyric = None
        self.SEARCH_RES_FIELDS = [
            'id', 'ar', 'name', 'source'
        ]
        self.SONG_DETAIL_FIELDS = [
            'source',
            'id',
            'song_name', 'song_url', 'song_pic', 'song_lyric', 'song_interval',
            'ablum_id', 'ablum_name', 'ablum_pic', 'ablum_intro',
            'artists',  # 包含'artist_id', 'artist_name', 'artist_pic', 'artist_intro'
        ]
        self.SONG_ARTIST_FIELDS = [
            'artist_id', 'artist_name', 'artist_pic', 'artist_intro'
        ]

    def pretend_https(self, url):
        if not url:
            return None
        return 'https:{}'.format(url) if url.startswith('//') else url
