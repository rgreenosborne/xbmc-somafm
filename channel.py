import os
import random
import shutil
import urllib2
import urlparse
from xml.etree import ElementTree
import xbmc
from xbmc import PLAYLIST_MUSIC

__author__ = 'Oderik'


class Channel(object):
    def prepare_cache(self):
        self.ensure_dir(self.cache_dir)
        if not os.path.exists(self.version_file_path):
            with open(self.version_file_path, 'w') as version_file:
                version_file.write(self.get_simple_element("updated"))

    def cleanup_cache(self):
        if os.path.exists(self.version_file_path):
            with open(self.version_file_path) as version_file:
                cached_version = version_file.read()
                if cached_version != self.get_simple_element("updated"):
                    version_file.close()
                    shutil.rmtree(self.cache_dir, True)

    def __init__(self, cache_dir, source=ElementTree.Element("channel")):
        self.source = source
        self.cache_dir = os.path.join(cache_dir, self.getid())
        self.version_file_path = os.path.join(self.cache_dir, "updated")
        self.cleanup_cache()
        self.prepare_cache()


    def get_simple_element(self, *tags):
        for tag in tags:
            element = self.source.find('.//' + tag)
            if element is not None:
                return element.text

    def __repr__(self):
        return self.__class__.__name__ + ': ' + self.getid()

    def get_playlist_url_and_format(self):
        for playlist_key in ['highestpls', 'fastpls', 'slowpls']:
            playlist_element = self.source.find(playlist_key)
            if playlist_element is not None:
                return playlist_element.text, playlist_element.attrib['format']

    def getid(self):
        return self.source.attrib['id']

    def ensure_dir(self, filepath):
        if not os.path.exists(filepath):
            os.makedirs(filepath)

    def get_playlist_file(self, playlist_url):
        url_path = urlparse.urlparse(playlist_url).path
        filename = os.path.split(url_path)[1]
        filepath = os.path.join(self.cache_dir, filename)
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            response = urllib2.urlopen(playlist_url)
            self.prepare_cache()
            with open(os.path.abspath(filepath), "w") as playlist_file:
                playlist_file.write(response.read())
            response.close()
        return filepath

    def get_content_url(self):
        playlist_url, media_format = self.get_playlist_url_and_format()
        filepath = self.get_playlist_file(playlist_url)
        print media_format + " " + playlist_url

        play_list = xbmc.PlayList(PLAYLIST_MUSIC)
        print "Loading playlist " + filepath
        play_list.load(filepath)
        streamurl = play_list.__getitem__(random.randrange(0, play_list.size())).getfilename()
        print "Selected stream url: " + streamurl
        return streamurl

    def getthumbnail(self):
        return self.get_simple_element('xlimage', 'largeimage', 'image')


    def geticon(self):
        return self.get_simple_element('largeimage', 'xlimage', 'image')
