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

import time

# PtQt4
# QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QString
from PyQt4.QtCore import QThread
from PyQt4.QtCore import QObject
# PyQt4 QtGui
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QTabBar
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QToolButton
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QMessageBox

# Caldo Libs
from utils import new_timer
from utils import from_bit_to
# Search in all webs
from utils.search import SearchThread
# Download Thread
from utils.download import torrentThread
# UI
from UI.Search import *
from UI.Download import *

class MainWindow(QMainWindow):
  def __init__(self, session, parent = None):
    QMainWindow.__init__(self, parent)

    # Configure windows
    # Title
    self.setWindowTitle('Caldo - Fast and free BitTorrent search engine and client')
    # Windows icon
    self.setWindowIcon(QIcon("logo.svg"))
    # Minimum height
    self.setMinimumSize(600, 400)

    # Central widget
    self.MainWidget = MainWidget(session, self)
    self.setCentralWidget(self.MainWidget)

class MainWidget(QWidget):
  def __init__(self, session, parent = None):
    QWidget.__init__(self, parent)
    self.parent = parent
    
    self.threads = []
    self.timer = new_timer(10)
    self.connect(self.timer, SIGNAL("timeout()"), self.setSpacingByTimer)

    self.spacingTimers = []
    self.tabs = []
    self.session = session

    # Layout
    vLayout = QVBoxLayout(self)
    self.wLayout = QHBoxLayout()
    vLayout.addLayout(self.wLayout)

    self.netStatusLabel = QLabel()
    self.netStatusLabel.setMinimumWidth(200)
    self.wLayout.addWidget(self.netStatusLabel)

    self.updateNetStatusLabelThread = updateNetStatusThread(self)
    self.updateNetStatusLabelThread.start()
    self.connect(self.updateNetStatusLabelThread, SIGNAL('update(int, int)'), self.updateNetStatusLabel)

    # Spacing
    self.wLayout.setSpacing(self.newSpacingSize())

    # Search Box
    self.searchBox = SearchLineEdit()
    self.searchBox.setPlaceholderText("Search torrent file")
    self.connect(self.searchBox, SIGNAL('returnPressed()'), self.searchTorrent)
    self.connect(self.searchBox.searchButton, SIGNAL('clicked()'), self.searchTorrent)
    self.connect(self.searchBox, SIGNAL('focusChange()'), self.timer.start)
    self.wLayout.addWidget(self.searchBox)

    self.tabWidget = QTabWidget(self)
    #self.tabWidget.setTabPosition(QTabWidget.South)
    self.tabWidget.setMovable(True)
    vLayout.addWidget(self.tabWidget)
    # Tabs
    self.DownloadTab = DownloadTab()
    self.DownloadTabIndex = self.tabWidget.addTab(self.DownloadTab, QIcon("./img/download.svg"), 'Downloads')
    self.tabWidget.setStyleSheet('''
    QPushButton
    {
      border: none;
    }
    QToolButton
    {
      border: none;
    }
    ''')

    self.updateNetStatusLabel(0, 0)

  def searchTorrent(self):
    if str(self.searchBox.displayText()).strip():
      # Add a new search tab
      SearchTab = SearchTabClass()
      
      thread = SearchThread(self.searchBox.displayText().replace(" ", "%20"))
      thread.start()
      self.connect(thread, SIGNAL("update(PyQt_PyObject)"), SearchTab.SearchTable.addResults)
      SearchTabIndex = self.tabWidget.addTab(SearchTab, QIcon("./img/loading/loading-0.png"), 'Search "%s"' % self.searchBox.displayText())
      # Loading icon
      loadingIcon = loadingIconClass(lambda icon: self.tabWidget.setTabIcon(self.tabWidget.indexOf(SearchTab), icon))
      timer = new_timer(50)
      timer.connect(timer, SIGNAL("timeout()"), loadingIcon.update);
      self.connect(thread, SIGNAL('finish()'), lambda: loadingIcon.finish(timer))
      # Clear the search box
      self.searchBox.clear()
      # Add close button to search tab
      closeButton = QPushButton(QIcon("./img/close.png"), "")
      self.tabWidget.tabBar().setTabButton(SearchTabIndex, QTabBar.RightSide, closeButton)
      self.connect(closeButton, SIGNAL('clicked()'), thread.quit)
      self.connect(closeButton, SIGNAL('clicked()'), lambda: self.RemoveSearchTorrent(SearchTab))
      # Add a new download
      self.connect(SearchTab.SearchTable, SIGNAL('doubleClicked (const QModelIndex)'), lambda index: self.torrentAdd(SearchTab.SearchTable.results[index.row()]))

  def torrentAdd(self, torrent):
    if self.session.add(torrent):
      self.threads.append(torrentThread(torrent, self.session))
      self.threads[-1].start()
      widget = self.DownloadTab.addDownloadItem(torrent.name, torrent.size[0]*1024**torrent.size[1])
      self.connect(self.threads[-1], SIGNAL('update(PyQt_PyObject)'), widget.update)
    else:
      QMessageBox.warning(self, "Warning", "The torrent file is already downloading.")

  def RemoveSearchTorrent(self, widget):
    self.tabWidget.removeTab(self.tabWidget.indexOf(widget))
    del widget

  def updateNetStatusLabel(self, downspeed, upspeed):
    text = "<small>↓ %s/s ↑ %s/s</small>" % (from_bit_to(downspeed), from_bit_to(upspeed))
    self.netStatusLabel.setText(QObject().trUtf8(text))

  def newSpacingSize(self):
    try: focus = self.searchBox.hasFocus()
    except AttributeError: focus = False
    return ((0.5/1.618 if focus else 0.45)*int(self.parent.width())) - 80

  def resizeEvent(self, event = None):
    if event: QWidget.resizeEvent(self, event)
    self.wLayout.setSpacing(self.newSpacingSize())

  def setSpacingByTimer(self):
    "Edit the spacing to resize the Search Box"
    size = self.newSpacingSize()
    currentSize = self.wLayout.spacing()

    if abs(size - self.wLayout.spacing()) <= 10:
      self.timer.stop()
    elif self.wLayout.spacing() > size:
      self.wLayout.setSpacing(currentSize - 10)
    else:
      self.wLayout.setSpacing(currentSize + 10)

class loadingIconClass(list):
  def __init__(self, func):
    self.i = 0
    self.func = func
    for i in range(16):
      self.append(QIcon("./img/loading/loading-%d.png" % i))

  def update(self):
    self.i += 1
    self.func(self[self.i%16])

  def finish(self, timer):
    self.func(QIcon("./img/download.png"))
    timer.stop()

class updateNetStatusThread(QThread):
  def __init__(self, threads):
    QThread.__init__(self)
    self.threads = threads

  def run(self):
    while True:
      time.sleep(1)
      speed_download = 0
      speed_upload = 0
      for thread in self.threads.threads:
        speed_download += thread.speed_download
        speed_upload += thread.speed_upload

      self.emit(SIGNAL('update(int, int)'),
                speed_download, speed_upload)

class SearchLineEdit(QLineEdit):
  def __init__(self, parent = None):
    QLineEdit.__init__(self, parent)
    self.searchButton = QToolButton(self)
    self.searchButton.setCursor(QCursor())
    self.searchButton.setIcon(QIcon("./img/search.svg"))
    frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth);
    self.searchButton.setStyleSheet("QToolButton {border: none; padding: 0px;}")
    self.setStyleSheet(QString(
    '''QLineEdit
    {
      padding-right: %1px;
      padding-left: 2px;
      padding-top: 1px;
      padding-bottom: 1px;
    }
    ''').arg(self.searchButton.sizeHint().width() + frameWidth + 1));

  def resizeEvent(self, event = None):
    if event: QLineEdit.resizeEvent(self, event)
    sz = self.searchButton.sizeHint()
    frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
    self.searchButton.move(self.rect().right() - frameWidth - sz.width(), (self.rect().bottom() + 1 - sz.height())/2)

  def focusInEvent(self, event = None):
    QLineEdit.focusInEvent(self, event)
    self.emit(SIGNAL("focusChange()"))

  def focusOutEvent(self, event = None):
    QLineEdit.focusOutEvent(self, event)
    self.emit(SIGNAL("focusChange()"))
