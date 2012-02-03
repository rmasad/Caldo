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
import time

# PyQt4
from PyQt4 import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtWebKit

# Search in torrent webs lib
import search
import utils
import download

class MainWindow(QtGui.QMainWindow):
  def __init__(self, parent = None):
    QtGui.QWidget.__init__(self, parent)

    # Configure windows
    # Title
    self.setWindowTitle('Caldo - Fast and free BitTorrent search engine and client')
    # Windows icon
    self.setWindowIcon(QtGui.QIcon("logo.svg"))
    # Minimum height
    self.setMinimumSize(600, 400)

    # Central widget
    self.MainWidget = MainWidget(self)
    self.setCentralWidget(self.MainWidget)

class MainWidget(QtGui.QWidget):
  def __init__(self, parent = None):
    QtGui.QWidget.__init__(self,parent)
    
    self.threads = []
    self.session = download.get_session()

    # Layout
    vLayout = QtGui.QVBoxLayout(self)
    wLayout = QtGui.QHBoxLayout()
    vLayout.addLayout(wLayout)

    self.netStatusLabel = QtGui.QLabel()
    wLayout.addWidget(self.netStatusLabel)
    self.updateNetStatusLabel(0, 0)

    self.updateNetStatusLabelThread = updateNetStatusThread(self)
    self.updateNetStatusLabelThread.start()
    self.connect(self.updateNetStatusLabelThread, QtCore.SIGNAL('update(int, int)'), self.updateNetStatusLabel)


    wLayout.addStretch()
    self.searchBox = SearchLineEdit()
    self.searchBox.setPlaceholderText("Search torrent file")
    self.connect(self.searchBox, QtCore.SIGNAL('returnPressed()'), self.searchTorrent)
    self.connect(self.searchBox.searchButton, QtCore.SIGNAL('clicked()'), self.searchTorrent)
    wLayout.addWidget(self.searchBox)

    self.tabWidget = QtGui.QTabWidget(self)
    vLayout.addWidget(self.tabWidget)
    # Tabs
    self.MainTab = MainTab()
    self.MainTabIndex = self.tabWidget.addTab(self.MainTab, QtGui.QIcon("./img/download.svg"), 'Downloads')

    self.tabWidget.setStyleSheet("QPushButton { border: none;}")

  def searchTorrent(self):
    SearchTab = SearchTabClass(self.searchBox.displayText().replace(" ", "%20"))
    SearchTabIndex = self.tabWidget.addTab(SearchTab, QtGui.QIcon("./img/search.svg"), 'Search "%s"' % self.searchBox.displayText())
    self.searchBox.clear()
    closeButton = QtGui.QPushButton(QtGui.QIcon("./img/close.png"), "")
    self.tabWidget.tabBar().setTabButton(SearchTabIndex, QtGui.QTabBar.RightSide, closeButton)
    self.connect(closeButton, QtCore.SIGNAL('clicked()'), lambda: self.RemoveSearchTorrent(SearchTab, SearchTabIndex))
    self.connect(SearchTab.SearchTable, QtCore.SIGNAL('doubleClicked (const QModelIndex)'), lambda index: self.torrentAdd(SearchTab.SearchTable.results_list[index.row()]))

  def torrentAdd(self, torrent):
    self.threads.append(download.torrentThread(torrent.magnet_link, self.session))
    self.threads[-1].start()
    widget = self.MainTab.addDownloadItem(torrent.name, torrent.size[0]*1024**torrent.size[1])
    self.connect(self.threads[-1], QtCore.SIGNAL('update(int, int, int, int, int)'), widget.update)

  def RemoveSearchTorrent(self, widget, index):
    self.tabWidget.removeTab(index)
    del widget

  def updateNetStatusLabel(self, downspeed, upspeed):
    text = "<small>↓ %s ↑ %s</small>" % (utils.from_bit_to(downspeed), utils.from_bit_to(upspeed))
    self.netStatusLabel.setText(QtCore.QObject().trUtf8(text))

class updateNetStatusThread(QtCore.QThread):
  def __init__(self, threads):
    QtCore.QThread.__init__(self)
    self.threads = threads

  def run(self):
    while not time.sleep(1):
      speed_download = 0
      speed_upload = 0
      for thread in self.threads.threads:
        speed_download += thread.speed_download
        speed_upload += thread.speed_upload

      self.emit(QtCore.SIGNAL('update(int, int)'),
                speed_download, speed_upload)

class SearchLineEdit(QtGui.QLineEdit):
  def __init__(self, parent = None):
    QtGui.QLineEdit.__init__(self, parent)
    self.searchButton = QtGui.QToolButton(self)
    self.searchButton.setCursor(QtGui.QCursor())
    self.searchButton.setIcon(QtGui.QIcon("./img/search.svg"))
    frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth);
    self.searchButton.setStyleSheet("QToolButton { border: none; padding: 0px;}")
    self.setStyleSheet(QtCore.QString("QLineEdit { padding-right: %1px; } ").arg(self.searchButton.sizeHint().width() + frameWidth + 1));


  def resizeEvent(self, event = None):
    sz = self.searchButton.sizeHint()
    frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
    self.searchButton.move(self.rect().right() - frameWidth - sz.width(), (self.rect().bottom() + 1 - sz.height())/2)

class MainTab(QtGui.QWidget):
  current_row = 1
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)

    vLayout = QtGui.QVBoxLayout(self)
    
    self.downloads_list = QtGui.QListWidget()
    vLayout.addWidget(self.downloads_list)

  def addDownloadItem(self, title, size):
    downloadItem = downloadItemClass(title, size)
    item = QtGui.QListWidgetItem("\n\n\n\n")
    item.setIcon(QtGui.QIcon("./img/download.png"))
    self.downloads_list.insertItem(self.current_row, item)
    self.downloads_list.setItemWidget(item, downloadItem)
    self.current_row += 1
    return downloadItem

class downloadItemClass(QtGui.QWidget):
  states = ['queued', 'checking', 'downloading metadata',
            'downloading', 'finished', 'seeding', 'allocating']
  def __init__(self, title, size, parent=None):
    QtGui.QWidget.__init__(self, parent)
    vLayout = QtGui.QVBoxLayout(self)
    vLayout.addWidget(QtGui.QLabel("<b>%s</b>" % title))

    self.progressLabel = QtGui.QLabel("") 
    vLayout.addWidget(self.progressLabel)

    self.downloadedBar = QtGui.QProgressBar()
    vLayout.addWidget(self.downloadedBar)

    self.speedLabel = QtGui.QLabel()
    vLayout.addWidget(self.speedLabel)
    self.update(size)

  def update(self, size, downloaded = 0, uploaded = 0, download_speed = 0, upload_speed = 0):
    ratio = 0 if downloaded == 0 else float(uploaded)/downloaded
    self.progressLabel.setText("%s/%s, uploaded %s (Ratio %0.1f)" % (utils.from_bit_to(downloaded), utils.from_bit_to(size), utils.from_bit_to(uploaded), ratio))
    self.downloadedBar.setValue(100*downloaded/size)
    self.speedLabel.setText(QtCore.QObject().trUtf8("↓ %s ↑ %s" % (utils.from_bit_to(download_speed), utils.from_bit_to(upload_speed))))

class SearchTabClass(QtGui.QWidget):
  def __init__(self, text, parent = None):
    QtGui.QWidget.__init__(self, parent)
    vLayout = QtGui.QVBoxLayout(self)
    self.SearchTable = SearchTable(text)
    vLayout.addWidget(self.SearchTable)

class SearchTable(QtGui.QTableView):
  def __init__(self, text, parent = None):
    self.ascendingIcon = QtGui.QIcon("./img/ascending.png")
    self.descendingIcon = QtGui.QIcon("./img/descending.png")

    QtGui.QWidget.__init__(self, parent)

    self.results = search.search_in_all_webs(text)
    self.results_list = self.results.values()

    self.currentColumnSort = None
    self.setModel(self.makeModel(self.results_list, 2))
    self.connect(self.horizontalHeader(),
                QtCore.SIGNAL('sectionClicked(int)'),
                self.horizontalHeaderClicked)

    #self.setSortingEnabled(True)
    self.setCornerButtonEnabled(False)
    # Hide vertical header (numbers at left side)
    self.verticalHeader().hide()
    # Select by rows
    self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    # Can't edit items
    self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

    # Resize columns
    self.horizontalHeader().setResizeMode(0, 1)
    for i in range(1, 4):
      self.resizeColumnToContents(i)

  def horizontalHeaderClicked(self, i):
    self.setModel(self.makeModel(self.results_list, i))
    if self.currentColumnSort:
      self.resizeColumnToContents(self.currentColumnSort)

  def makeModel(self, results, index):
    getAttr = [lambda obj: obj.name,
               lambda obj: obj.size[0]*(1024**obj.size[1]),
               lambda obj: obj.seed,
               lambda obj: obj.leach]

    col = len(results)

    ascending = False if index == self.currentColumnSort else True
    self.currentColumnSort = index if ascending else None

    model = QtGui.QStandardItemModel(col, 4, self)
    columnHeaderItems = [QtGui.QStandardItem(column) for column in "Name", "Size", "Seeds", "Leachs"]
    columnHeaderItems[index].setIcon(self.ascendingIcon if ascending else self.descendingIcon)
    for i in range(4):
      model.setHorizontalHeaderItem(i, columnHeaderItems[i])

    if results:
      results = utils.list_to_tree(results, lambda x, y: getAttr[index](x) > getAttr[index](y))
      if ascending: results = results.postOrder()
      else: results = results.preOrder()
      self.results_list = results

    for i in range(col):
      model.setItem(i, 0, QtGui.QStandardItem(results[i].name))
      size_tuple = results[i].size
      size = utils.from_bit_to(size_tuple[0]*1024**size_tuple[1])
      model.setItem(i, 1, QtGui.QStandardItem(size))
      model.setItem(i, 2, QtGui.QStandardItem(str(results[i].seed)))
      model.setItem(i, 3, QtGui.QStandardItem(str(results[i].leach)))

    return model

app = QtGui.QApplication(sys.argv)
qb = MainWindow()
qb.show()
app.exec_()
