import os
import random
import urllib2
import urlparse
from xml.etree import ElementTree
import xbmc
from xbmc import PLAYLIST_MUSIC

__author__ = 'Oderik'


class Channel(object):
    def __init__(self, source=ElementTree.Element("channel")):
        self.source = source

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

    def get_playlist_file(self, playlist_url):
        url_path = urlparse.urlparse(playlist_url).path
        filename = os.path.split(url_path)[1]
        filepath = os.path.join(self.get_simple_element('updated'), filename)
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            response = urllib2.urlopen(playlist_url)
            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))
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
        return self.get_simple_element('image', 'largeimage', 'xlimage')


    def geticon(self):
        return self.get_simple_element('xlimage', 'largeimage', 'image')
