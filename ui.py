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

# Search in torrent webs lib
import search
import utils

class MainWindow(QtGui.QMainWindow):
  def __init__(self, parent = None):
    QtGui.QWidget.__init__(self, parent)

    # Configure windows
    # Title
    self.setWindowTitle('Caldo - Fast and free BitTorrent search engine and client')
    # Windows icon
    #self.setWindowIcon(QtGui.QIcon(""))
    # Minimum height
    self.setMinimumSize(600, 400)

    # Central widget
    self.MainWidget = MainWidget(self)
    self.setCentralWidget(self.MainWidget)


class MainWidget(QtGui.QWidget):
  def __init__(self, parent = None):
    QtGui.QWidget.__init__(self,parent)
    
    # Layout
    vLayout = QtGui.QVBoxLayout(self)
    wLayout = QtGui.QHBoxLayout()
    vLayout.addLayout(wLayout)

    self.netStatusLabel = QtGui.QLabel(QtCore.QObject().trUtf8("<small>↓ 0 Kb ↑ 0 Kb</small>"))
    wLayout.addWidget(self.netStatusLabel)


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
    SearchTab = SearchTabClass(self.searchBox.displayText())
    SearchTabIndex = self.tabWidget.addTab(SearchTab, QtGui.QIcon("./img/search.svg"), 'Search "%s"' % self.searchBox.displayText())
    self.searchBox.clear()
    closeButton = QtGui.QPushButton(QtGui.QIcon("./img/close.png"), "")
    self.tabWidget.tabBar().setTabButton(SearchTabIndex, QtGui.QTabBar.RightSide, closeButton)
    self.connect(closeButton, QtCore.SIGNAL('clicked()'), lambda: self.RemoveSearchTorrent(SearchTab, SearchTabIndex))

  def RemoveSearchTorrent(self, widget, index):
    self.tabWidget.removeTab(index)
    del widget

class MainTab(QtGui.QWidget):
  current_row = 1
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)

    vLayout = QtGui.QVBoxLayout(self)
    
    self.downloads_list = QtGui.QListWidget()
    vLayout.addWidget(self.downloads_list)
    self.addDownloadItem("Archivo 1", 1024, 595, 222, 24, 12)
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


class SearchTabClass(QtGui.QWidget):
  def __init__(self, text, parent = None):
    QtGui.QWidget.__init__(self, parent)
    vLayout = QtGui.QVBoxLayout(self)
    vLayout.addWidget(SearchTable(text))

class SearchTable(QtGui.QTableView):
  def __init__(self, text, parent = None):
    self.ascendingIcon = QtGui.QIcon("./img/ascending.png")
    self.descendingIcon = QtGui.QIcon("./img/descending.png")

    QtGui.QWidget.__init__(self, parent)

    self.results = search.search_in_all_webs(text)

    self.currentColumnSort = None
    self.setModel(self.makeModel(self.results, 2))
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
    self.setModel(self.makeModel(self.results, i))
    if self.currentColumnSort:
      self.resizeColumnToContents(self.currentColumnSort)

  def makeModel(self, results, index):
    getAttr = [lambda obj: obj.name,
               lambda obj: obj.size[0]*(1024**obj.size[1]),
               lambda obj: obj.seed,
               lambda obj: obj.leach]

    col = len(results.keys())

    ascending = False if index == self.currentColumnSort else True
    self.currentColumnSort = index if ascending else None

    model = QtGui.QStandardItemModel(col, 4, self)
    columnHeaderItems = [QtGui.QStandardItem(column) for column in "Name", "Size", "Seeds", "Leachs"]
    columnHeaderItems[index].setIcon(self.ascendingIcon if ascending else self.descendingIcon)
    for i in range(4):
      model.setHorizontalHeaderItem(i, columnHeaderItems[i])

    if results:
      results = utils.list_to_tree(results.values(), lambda x, y: getAttr[index](x) > getAttr[index](y))
      if ascending: results = results.postOrder()
      else: results = results.preOrder()
    else: results = []


    for i in range(col):
      model.setItem(i, 0, QtGui.QStandardItem(results[i].name))
      size_tuple = results[i].size
      size = "%d %s" % (size_tuple[0], ["B", "KiB", "MiB", "GiB"][size_tuple[1]])
      model.setItem(i, 1, QtGui.QStandardItem(size))
      model.setItem(i, 2, QtGui.QStandardItem(str(results[i].seed)))
      model.setItem(i, 3, QtGui.QStandardItem(str(results[i].leach)))

    return model

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

app = QtGui.QApplication(sys.argv)
qb = MainWindow()
qb.show()
app.exec_()
