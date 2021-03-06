#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#        Caldo       
#        Copyright 2011  Rafik Mas'ad


######################## GNU General Public License 3 ##########################
#                                                                              #
#      This file is part of ShareIt!.                                          #
#                                                                              #
#      Caldo is free software: you can redistribute it and/or modify           #
#      it under the terms of the GNU General Public License as published by    #
#      the Free Software Foundation, either version 3 of the License, or       #
#      (at your option) any later version.                                     #
#                                                                              #
#      Caldo is distributed in the hope that it will be useful,                #
#      but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#      GNU General Public License for more details.                            #
#                                                                              #
#      You should have received a copy of the GNU General Public License       #
#      along with Caldo.  If not, see <http://www.gnu.org/licenses/>.          #
#                                                                              #
################################################################################

import urllib2
import HTMLParser

# QThread
from PyQt4.QtCore import QThread, SIGNAL

class TorrentMetadata:
  def __init__(self):
    self.ID = None # str
    self.magnet_link = None # str
    self.name = None # str
    self.description = None # str
    self.size = [None, None] # (float, int)
    self.seed = None # int
    self.leech = None # int

  def __repr__(self):
    return self.name.encode('utf-8')

class GenericWeb:
  search_url = None

  def __init__(self, search):
    self.search = search

  def parse(self, page):
    return False, False

class ThePirateBay(GenericWeb):
  search_url = "http://thepiratebay.se/search/%s/%s/7/"
  
  def parse(self, page = 0):
    torrent_list = []
    url = self.search_url % (self.search, page)
    html = urllib2.urlopen(urllib2.Request(url)).read()
    html = html[html.find("</thead>") + 8 : html.find("</table>")]

    for torrent in html.split("<tr>")[1:]:
      torrentParsed = ThePirateBayParser()
      torrentParsed.feed(torrent.decode('utf-8'))

      if not torrentParsed.data.seed:
        return torrent_list, False

      if torrentParsed.data.name:
        torrent_list.append(torrentParsed.data)

    return torrent_list, lambda: self.parse(page+1)

class ThePirateBayParser(HTMLParser.HTMLParser):
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self)
    self.data = TorrentMetadata()
    self.tag = None

  def handle_starttag(self, tag, attrs):
    if tag == "a" and ("class", "detLink") in attrs:
      self.tag = "name"

    if tag == "a" and ("title", "Download this torrent using magnet") in attrs:
      for att in attrs:
        if att[0] == "href":
          self.data.magnet_link = att[1]
          self.data.ID = att[1][att[1].find("?xt=")+4:att[1].find("&")].split(":")[-1].upper()

    if tag == "font" and ("class", "detDesc") in attrs:
      self.tag = "size"

    if tag == "td" and ("align", "right") in attrs:
      if self.data.seed == None:
        self.tag = "seed"
      else:
        self.tag = "leach"

  def handle_endtag(self, tag):
    pass

  def handle_entityref(self, name):
    if self.tag == "size":
      self.tag = "size1"
    elif self.tag == "size1":
      self.tag = "size2"


  def handle_data(self, data):
    if self.tag == "name":
      self.data.name = data

    elif self.tag == "seed":
      self.data.seed = int(data)

    elif self.tag == "leach":
      self.data.leach = int(data)

    elif self.tag == "size":
      return

    if self.tag == "size1":
      self.data.size[0] = float(data.split()[-1])
      return

    if self.tag == "size2":
      self.data.size[1] = ["B", "K", "M", "G"].index(data[0].upper())

    self.tag = None

def search_in_all_webs(search, webs = [ThePirateBay]):
  funcs = []
  for web in webs:
    try: funcs.append(web(search).parse)
    except: pass
  return funcs

class SearchThread(QThread):
  def __init__(self, search):
    QThread.__init__(self)
    self.funcs = search_in_all_webs(search)

  def run(self):
    while self.funcs:
      new_funcs = []
      for func in self.funcs:
        torrent_list, new_func = func()
        if new_func: new_funcs.append(new_func)
        self.emit(SIGNAL("update(PyQt_PyObject)"), torrent_list)
      self.funcs = new_funcs
    self.emit(SIGNAL('finish()'))
