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

class Torrent:
  def __init__(self):
    self.ID = None # str
    self.magnet_link = None # str
    self.name = None # str
    self.description = None # str
    self.size = [None, None] # (float, float)
    self.seed = None # int
    self.leech = None # int

  def __repr__(self):
    return self.name.encode('utf-8')

class GenericWeb:
  search_url = None

  def __init__(self, search, torrent_dict = {}):
    self.torrent_dict = torrent_dict
    i = 0
    while self.parse(search, i): i += 1;

  def parse(self, search, page):
    return False

class ThePirateBay(GenericWeb):
  search_url = "http://thepiratebay.org/search/%s/%s/7/"
  
  def parse(self, search, page):
    url = self.search_url % (search, page)
    html = urllib2.urlopen(urllib2.Request(url)).read()
    html = html[html.find("</thead>") + 8 : html.find("</table>")]

    for torrent in html.split("<tr>")[1:]:
      torrentParsed = ThePirateBayParser()
      torrentParsed.feed(torrent.decode('utf-8'))

      if not torrentParsed.data.seed:
        return False

      if torrentParsed.data.ID in self.torrent_dict.keys():
        print self.torrent_dict[torrentParsed.data.ID], torrentParsed.data.name

      if torrentParsed.data.name and torrentParsed.data.ID not in self.torrent_dict.keys():
        self.torrent_dict[torrentParsed.data.ID] = torrentParsed.data

    return False

class ThePirateBayParser(HTMLParser.HTMLParser):
  def __init__(self):
    HTMLParser.HTMLParser.__init__(self)
    self.data = Torrent()
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
    #print data
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
  torrent_dict = {}
  for web in webs:
    try: torrent_dict = web(search, torrent_dict).torrent_dict
    except: pass
  return torrent_dict
