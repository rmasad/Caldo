import time

# Torrent lib
import libtorrent

# QThread
from PyQt4.QtCore import QThread, SIGNAL

def get_session():
  return libtorrent.session()

class torrentThread(QThread):
  def __init__(self, magnet_link, session):
    QThread.__init__(self)
    self.magnet_link = str(magnet_link)
    self.session = session

    self.speed_download = 0
    self.speed_upload = 0

  def run(self):
    params = {'save_path': './'}
    handle = libtorrent.add_magnet_uri(self.session, self.magnet_link, params)

    while (not handle.has_metadata()): time.sleep(1)
    
    total_download = 0
    total_upload = 0
    
    while True:
      status = handle.status()
      

      self.speed_download = (status.total_download - total_download)/1
      self.speed_upload = (status.total_upload - total_upload)/1

      total_download = status.total_download
      total_upload = status.total_upload

      self.emit(SIGNAL('update(int, int, int, int, int)'),
                status.total_wanted, total_download, total_upload,
                self.speed_download, self.speed_upload)
      time.sleep(1)

