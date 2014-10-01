import sys
import urllib2
import xml.etree.ElementTree as ET
from xbmcgui import DialogProgressBG

import xbmcplugin
import xbmcgui
import xbmc


__addon__ = "SomaFM"
__addonid__ = "plugin.audio.somafm"
__version__ = "0.0.2"


def log(msg):
    xbmc.log(str(msg))
    # print "[PLUGIN] '%s (%s)' " % (__addon__, __version__) + str(msg)


log("Initialized!")
dialog_progress_bg = DialogProgressBG()
dialog_progress_bg.create("Updating SomaFM channels")
log(sys.argv)

rootURL = "http://somafm.com/"

# pluginPath = sys.argv[0]
handle = int(sys.argv[1])
query = sys.argv[2]


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


def addEntries():
    somaXML = getHTMLFor(url="channels.xml")
    channelsContainer = ET.fromstring(somaXML)

    stations = channelsContainer.findall(".//channel")
    for idx, station in enumerate(stations):
        title = station.find('title').text
        dialog_progress_bg.update(100 * idx / len(stations), message=title)
        description = station.find('description').text
        if station.find('largeimage') is not None:
            img = rootURL + station.find('largeimage').text.replace(rootURL, "")
        else:
            img = rootURL + station.find('image').text.replace(rootURL,"")
        url = get_content_url(station)
        li = xbmcgui.ListItem(title, description, thumbnailImage=img)
        li.setProperty("IsPlayable","true")
        xbmcplugin.addDirectoryItem(
            handle=handle,
            url=url,
            listitem=li)
        # log('Added channel {}' % title.text)


addEntries()
dialog_progress_bg.close()
xbmcplugin.endOfDirectory(handle)
