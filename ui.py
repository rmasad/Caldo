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

import sys

# PyQt4
from PyQt4 import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtWebKit

class MainWindow(QtGui.QMainWindow):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)

    # Configure windows
    # Title
    self.setWindowTitle('Caldo - Fast and free BitTorrent search engine and client')
    # Windows icon
    #self.setWindowIcon(QtGui.QIcon(""))
    # Minimum height
    self.resize(600, 400)

    # Central widget
    self.MainWidget = MainWidget(self)
    self.setCentralWidget(self.MainWidget)


class MainWidget(QtGui.QWidget):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self,parent)
    
    # Layout
    vLayout = QtGui.QVBoxLayout(self)
    wLayout = QtGui.QHBoxLayout()
    vLayout.addLayout(wLayout)

    self.netStatusLabel = QtGui.QLabel(QtCore.QObject().trUtf8("<small>↓ 0 Kb ↑ 0 Kb</small>"))
    wLayout.addWidget(self.netStatusLabel)


    wLayout.addStretch()
    searchBox = QtGui.QLineEdit()
    searchBox.setPlaceholderText("Search torrent file")
    wLayout.addWidget(searchBox)

    self.tabWidget = QtGui.QTabWidget(self)
    vLayout.addWidget(self.tabWidget)
    # Tabs
    self.MainTab = MainTab()
    self.MainTabIndex = self.tabWidget.addTab(self.MainTab, QtGui.QIcon("./img/download.svg"), 'Downloads')


class MainTab(QtGui.QWidget):
  current_row = 1
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)

    vLayout = QtGui.QVBoxLayout(self)
    
    self.downloads_list = QtGui.QListWidget()
    vLayout.addWidget(self.downloads_list)
    self.addDownloadItem("Archivo 1", 1024, 555, 222, 24, 12)
    self.addDownloadItem("Archivo 2", 10224, 555, 2222, 24, 12)
    self.addDownloadItem("Archivo 3", 10224, 5525, 2222, 24, 12)
    self.addDownloadItem("Archivo 14", 1024, 655, 2222, 24, 12)
    self.addDownloadItem("Archivo 231", 10224, 5525, 1222, 24, 12)


  def addDownloadItem(self, title, size, downloaded, uploaded, download_speed, upload_speed):
    downloadItem = downloadItemClass(title, size, downloaded, uploaded, download_speed, upload_speed)
    item = QtGui.QListWidgetItem("\n\n\n\n")
    item.setIcon(QtGui.QIcon("./img/download.png"))
    self.downloads_list.insertItem(self.current_row, item)
    self.downloads_list.setItemWidget(item, downloadItem)
    self.current_row += 1


class downloadItemClass(QtGui.QWidget):
  def __init__(self, title, size, downloaded, uploaded, download_speed, upload_speed, parent=None):
    QtGui.QWidget.__init__(self, parent)
    vLayout = QtGui.QVBoxLayout(self)
    vLayout.addWidget(QtGui.QLabel("<b>%s</b>" % title))
    vLayout.addWidget(QtGui.QLabel("%s/%s, uploaded %s (Range %0.1f)" % (self.from_bit_to(downloaded), self.from_bit_to(size), self.from_bit_to(uploaded), float(uploaded)/downloaded)))
    downloadedBar = QtGui.QProgressBar()
    downloadedBar.setValue(100*downloaded/size)
    vLayout.addWidget(downloadedBar)
    vLayout.addWidget(QtGui.QLabel(QtCore.QObject().trUtf8("↓ %s ↑ %s" % (self.from_bit_to(download_speed), self.from_bit_to(upload_speed)))))

  def from_bit_to(self, size):
    i = 0
    while size > 1024:
      size /= 1024
      i+= 1
    return "%d %s" % (size, ["Bit", "Kbi", "Gbi"][i])

app = QtGui.QApplication(sys.argv)
qb = MainWindow()
qb.show()
app.exec_()
