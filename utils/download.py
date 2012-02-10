import time

# Torrent lib
import libtorrent

# PtQt4
# QtCore
from PyQt4.QtCore import QThread, SIGNAL
# QtGui
from PyQt4.QtGui import QIcon

class TorrentDownload:
  def __init__(self):
    self.ID = None # str
    self.magnet_link = None # str
    self.name = None # str
    self.size = None # int
    self.seed = [None, None] # [int, int]
    self.leech = [None, None] # [int, int]
    self.state = None # int
    self.downloaded = None # int
    self.uploaded = None # int
    self.downspeed = None # int
    self.upspeed = None # int

states = [('Queued', QIcon("img/queued.svg")),
          ('Checking', QIcon("img/checking.svg")),
          ('Downloading metadata', QIcon("img/downloading metadata.svg")),
          ('Downloading', QIcon("img/download.svg")),
          ('Finished', QIcon("img/finished.svg")),
          ('Seeding', QIcon("img/upload.svg")),
          ('Allocating', QIcon("img/allocating.svg"))]

class session(libtorrent.session):
  def __init__(self, current_dict = {}):
    libtorrent.session.__init__(self)
    self.active_torrents = current_dict

  def add (self, torrent):
    if torrent.ID not in self.active_torrents.keys():
      self.active_torrents[torrent.ID] = torrent
      return True
    return False

class torrentThread(QThread):
  def __init__(self, torrent, session):
    QThread.__init__(self)
    self.torrent = torrent
    self.session = session

    self.speed_download = 0
    self.speed_upload = 0

  def run(self):
    params = {'save_path': './'}
    handle = libtorrent.add_magnet_uri(self.session, str(self.torrent.magnet_link), params)

    while (not handle.has_metadata()): time.sleep(1)
    
    total_download = 0
    total_upload = 0
    
    while True:
      status = handle.status()

      self.speed_download = (status.total_download - total_download)/1
      self.speed_upload = (status.total_upload - total_upload)/1

      total_download = status.total_download
      total_upload = status.total_upload

      torrent = TorrentDownload()
      torrent.ID = self.torrent.ID
      torrent.magnet_link = self.torrent.magnet_link
      torrent.name = self.torrent.name
      torrent.size = status.total_wanted
      torrent.seed = [None, None] # [int, int]
      torrent.leech = [None, None] # [int, int]
      torrent.state = status.state
      torrent.downloaded = total_download
      torrent.uploaded = total_upload
      torrent.downspeed = self.speed_download
      torrent.upspeed = self.speed_upload

      self.emit(SIGNAL('update(PyQt_PyObject)'), torrent)
      time.sleep(1)

