#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#        Caldo       
#        Copyright 2011  Rafik Mas'ad

#        Why Caldo?
#        From Spanish: Culiados Americanos Legalizen Descargas Online
#        Irony about the SOPA law

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

# PtQt4
# QtCore
from PyQt4.QtCore import QObject
# PyQt4 QtGui
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QProgressBar
from PyQt4.QtGui import QListWidgetItem

# Caldo Libs
from utils import from_bit_to

class DownloadTab(QWidget):
  current_row = 1
  def __init__(self, parent=None):
    QWidget.__init__(self, parent)

    vLayout = QVBoxLayout(self)
    
    self.downloads_list = QListWidget()
    vLayout.addWidget(self.downloads_list)

  def addDownloadItem(self, title, size):
    downloadItem = downloadItemClass(title, size)
    item = QListWidgetItem("\n\n\n\n")
    item.setIcon(QIcon("./img/download.png"))
    self.downloads_list.insertItem(self.current_row, item)
    self.downloads_list.setItemWidget(item, downloadItem)
    self.current_row += 1
    return downloadItem

class downloadItemClass(QWidget):
  states = ['queued', 'checking', 'downloading metadata',
            'downloading', 'finished', 'seeding', 'allocating']
  def __init__(self, title, size, parent=None):
    QWidget.__init__(self, parent)
    vLayout = QVBoxLayout(self)
    vLayout.addWidget(QLabel("<b>%s</b>" % title))

    self.progressLabel = QLabel("") 
    vLayout.addWidget(self.progressLabel)

    self.downloadedBar = QProgressBar()
    vLayout.addWidget(self.downloadedBar)

    self.speedLabel = QLabel()
    vLayout.addWidget(self.speedLabel)
    self.update(size)

  def update(self, size, downloaded = 0, uploaded = 0, download_speed = 0, upload_speed = 0):
    ratio = 0 if downloaded == 0 else float(uploaded)/downloaded
    self.progressLabel.setText("%s/%s, uploaded %s (Ratio %0.1f)" % (from_bit_to(downloaded), from_bit_to(size), from_bit_to(uploaded), ratio))
    self.downloadedBar.setValue(100*downloaded/size)
    self.speedLabel.setText(QObject().trUtf8("↓ %s ↑ %s" % (from_bit_to(download_speed), from_bit_to(upload_speed))))

