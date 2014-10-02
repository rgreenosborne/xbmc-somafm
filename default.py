import sys
import urllib2
import xml.etree.ElementTree as ET
from channel import Channel

import xbmcplugin
import xbmcgui
import xbmc
from xbmcplugin import SORT_METHOD_LISTENERS, SORT_METHOD_UNSORTED, SORT_METHOD_GENRE


__addon__ = "SomaFM"
__addonid__ = "plugin.audio.somafm"
__version__ = "0.0.2"


def log(msg):
    xbmc.log(str(msg))
    # print "[PLUGIN] '%s (%s)' " % (__addon__, __version__) + str(msg)


log("Initialized!")
log(sys.argv)

rootURL = "http://somafm.com/"

# pluginPath = sys.argv[0]
try:
    handle = int(sys.argv[1])
    query = sys.argv[2]
except:
    handle = 0
    query = ""


def getHeaders(withReferrer=None):
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3'
    if withReferrer:
        headers['Referrer'] = withReferrer
    return headers


def getHTMLFor(url, withData=None, withReferrer=None):
    url = rootURL + url
    log("Get HTML for URL: " + url)
    req = urllib2.Request(url, withData, getHeaders(withReferrer))
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    return data


def get_best_playlist(station):
    for playlist_key in ['highestpls', 'fastpls', 'slowpls']:
        playlist = station.find(playlist_key)
        if playlist is not None:
            log('Using {} playlist {}'.format(playlist_key, playlist.text))
            return playlist


def get_content_url(station):
    url = rootURL + get_best_playlist(station).text.replace(rootURL, "")
    play_list = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    play_list.load(url)
    item = play_list.__getitem__(0)
    return item.getfilename()


def transfer_info(li, station, key):
    listeners = station.find(key)
    if listeners is not None:
        li.setInfo(type="Music", infoLabels={key: listeners.text})


def addEntries():
    somaXML = getHTMLFor(url="channels.xml")
    channelsContainer = ET.fromstring(somaXML)

    stations = channelsContainer.findall(".//channel")
    for station in stations:
        channel = Channel(station)
        li = xbmcgui.ListItem(channel.get_simple_element('title'), channel.get_simple_element('description'), thumbnailImage=channel.getthumbnail())
        li.setProperty("IsPlayable", "true")
        transfer_info(li, station, 'listeners')
        transfer_info(li, station, 'genre')
        xbmcplugin.addDirectoryItem(
            handle=handle,
            url=channel.get_content_url(),
            listitem=li,
            totalItems=len(stations))
        # log('Added channel {}' % title.text)


addEntries()
xbmcplugin.addSortMethod(handle, SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(handle, SORT_METHOD_LISTENERS)
xbmcplugin.addSortMethod(handle, SORT_METHOD_GENRE)
xbmcplugin.endOfDirectory(handle)
