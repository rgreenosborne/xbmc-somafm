import os
import sys
import urllib2
import urlparse
import xml.etree.ElementTree as ET

from channel import Channel
from xbmcgui import ListItem
import xbmcplugin
import xbmcgui
import xbmc
from xbmcplugin import SORT_METHOD_LISTENERS, SORT_METHOD_UNSORTED, SORT_METHOD_GENRE
import xbmcvfs


CHANNELS_FILE_NAME = "channels.xml"

__addon__ = "SomaFM"
__addonid__ = "plugin.audio.somafm"
__version__ = "0.0.2"


def log(msg):
    xbmc.log(str(msg))


log(sys.argv)

rootURL = "http://somafm.com/"
tempdir = xbmc.translatePath("special://temp/somafm")
xbmcvfs.mkdirs(tempdir)

LOCAL_CHANNELS_FILE_PATH = os.path.join(tempdir, CHANNELS_FILE_NAME)

try:
    plugin_url = sys.argv[0]
    handle = int(sys.argv[1])
    query = sys.argv[2]
except:
    plugin_url = "plugin://" + __addonid__
    handle = 0
    query = ""


def fetch_remote_channel_data():
    response = urllib2.urlopen(rootURL + CHANNELS_FILE_NAME)
    channel_data = response.read()
    response.close()
    with open(LOCAL_CHANNELS_FILE_PATH, 'w') as local_channels_xml:
        local_channels_xml.write(channel_data)
    return channel_data


def fetch_local_channel_data():
    with open(LOCAL_CHANNELS_FILE_PATH) as local_channels_file:
        return local_channels_file.read()


def fetch_channel_data(*strategies):
    for strategy in strategies:
        try:
            return strategy()
        except:
            pass


def build_directory():
    channel_data = fetch_channel_data(fetch_remote_channel_data, fetch_local_channel_data)
    xml_data = ET.fromstring(channel_data)

    stations = xml_data.findall(".//channel")
    for station in stations:
        channel = Channel(handle, tempdir, station)
        li = xbmcgui.ListItem(
            channel.get_simple_element('title'),
            channel.get_simple_element('description'),
            channel.geticon(),
            channel.getthumbnail(),
            plugin_url + channel.getid())

        li.setProperty("IsPlayable", "true")

        for element, info in [('listeners', 'listeners'),
                              ('genre', 'genre'),
                              ('dj', 'artist'),
                              ('description', 'comment'),
                              ('title', 'title')]:
            value = channel.get_simple_element(element)
            li.setInfo("Music", {info: value})

        xbmcplugin.addDirectoryItem(
            handle=handle,
            url=plugin_url + channel.getid(),
            listitem=li,
            totalItems=len(stations))
    xbmcplugin.addSortMethod(handle, SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(handle, SORT_METHOD_LISTENERS)
    xbmcplugin.addSortMethod(handle, SORT_METHOD_GENRE)


def firewall_mode():
    return xbmcplugin.getSetting(handle, "firewall") == 'true'


def format_priority():
    return [
        ["mp3"],
        ["mp3", "aac"],
        ["aac", "mp3"],
        ["aac"],
    ][int(xbmcplugin.getSetting(handle, "priority_format"))]


def quality_priority():
    return [
        ['slowpls', 'fastpls', 'highestpls', ],
        ['fastpls', 'slowpls', 'highestpls', ],
        ['fastpls', 'highestpls', 'slowpls', ],
        ['highestpls', 'fastpls', 'slowpls', ],
    ][int(xbmcplugin.getSetting(handle, "priority_quality"))]


def play(item_to_play):
    channel_data = fetch_channel_data(fetch_local_channel_data, fetch_remote_channel_data)
    xml_data = ET.fromstring(channel_data)
    channel_data = xml_data.find(".//channel[@id='" + item_to_play + "']")
    channel = Channel(handle, tempdir, channel_data, quality_priority(), format_priority(), firewall_mode())
    list_item = ListItem(channel.get_simple_element('title'),
                         channel.get_simple_element('description'),
                         channel.geticon(),
                         channel.getthumbnail(),
                         channel.get_content_url())
    xbmcplugin.setResolvedUrl(handle, True, list_item)


path = urlparse.urlparse(plugin_url).path
item_to_play = os.path.basename(path)

if item_to_play:
    play(item_to_play)
else:
    build_directory()

xbmcplugin.endOfDirectory(handle)
