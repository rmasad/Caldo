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
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject
# PyQt4 QtGui
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QToolButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QProgressBar
from PyQt4.QtGui import QStackedWidget
from PyQt4.QtGui import QListWidgetItem

# Caldo Libs
from utils import from_bit_to
from utils.download import states

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
    self.downloads_list.insertItem(self.current_row, item)
    self.downloads_list.setItemWidget(item, downloadItem)
    self.current_row += 1
    return downloadItem

class downloadItemClass(QWidget):
  def __init__(self, title, size, parent=None):
    QWidget.__init__(self, parent)
    self.mainLayout = QHBoxLayout(self)

    self.size = size

    self.statusButton = QToolButton()
    self.mainLayout.addWidget(self.statusButton)

    self.downloadItemInfo = StackedWidget()
    self.mainLayout.addWidget(self.downloadItemInfo)
    self.downloadItemMainInfo = downloadItemMainInfoClass(title)
    self.downloadItemInfo.addWidget(self.downloadItemMainInfo)

    self.connect(self.statusButton, SIGNAL('clicked()'), self.downloadItemInfo.next)

    self.update()

  def update(self, torrent = None):
    if not torrent:
      self.downloadItemMainInfo.fillData(self.size, 0, 0, 0, 0, 0, 0, 2)
      self.statusButton.setIcon(states[2][1])
    else:
      size = torrent.size
      downloaded = torrent.downloaded
      uploaded = torrent.uploaded
      ratio = 0 if downloaded == 0 else uploaded/float(downloaded)
      self.downloadItemMainInfo.fillData(size,
                                         downloaded, uploaded, ratio,
                                         100*(float(downloaded)/size),
                                         torrent.downspeed,
                                         torrent.upspeed,
                                         torrent.state)
      self.statusButton.setIcon(states[torrent.state][1])

class downloadItemMainInfoClass(QWidget):
  def __init__(self, title, parent = None):
    QWidget.__init__(self, parent)
    self.vLayout = QVBoxLayout(self)
    margins = self.vLayout.contentsMargins()
    self.vLayout.setContentsMargins(margins.left(), 0, margins.right(), 0)


    # Torrent primary data
    self.title = title

    # Torrent title
    self.vLayout.addWidget(QLabel("<b>%s</b>" % title))

    self.progressLabel = QLabel() 
    self.vLayout.addWidget(self.progressLabel)

    # Progress percent
    self.progressLayout = QHBoxLayout()
    self.vLayout.addLayout(self.progressLayout)
    # Progress percent label
    self.percentLabel = QLabel("0%")
    self.progressLayout.addWidget(self.percentLabel)
    # Progress percent bar
    self.downloadedBar = QProgressBar()
    self.downloadedBar.setTextVisible(False)
    self.progressLayout.addWidget(self.downloadedBar)
    # Pause/Stop/etc buttons...

    # Speed
    self.speedLabel = QLabel()
    self.vLayout.addWidget(self.speedLabel)

  def fillData(self, size, downloaded, uploaded, ratio, percent, downspeed, upspeed, state):
    progressLabel = "%s/%s, uploaded %s (Ratio %0.1f)"
    speedLabel = "%s, ↓ %s/s ↑ %s/s"
    self.progressLabel.setText(progressLabel % (from_bit_to(downloaded), from_bit_to(size), from_bit_to(uploaded), ratio))
    self.percentLabel.setText(("%0.1f" % percent) + "%")
    self.speedLabel.setText(self.trUtf8(speedLabel % (states[state][0], from_bit_to(downspeed), from_bit_to(upspeed))))
    self.downloadedBar.setValue(percent)

class StackedWidget(QWidget):
  def __init__(self, parent = None):
    QWidget.__init__(self, parent)
    self.vLayout = QVBoxLayout(self)
    self.vLayout.setContentsMargins(0, 0, 0, 0)

    self.widgets = []
    self.index = 0

    self.vLayout.addStretch()

  def addWidget(self, widget):
    self.widgets.append(widget)
    self.vLayout.addWidget(self.widgets[-1])
    if len(self.widgets) > 1:
      self.widgets[-1].hide()

  def next(self):
    self.widgets[self.index].hide()
    self.index += 1
    self.index %= len(self.widgets)
    self.widgets[self.index].show()

  def previous(self):
    self.widgets[self.index].hide()
    self.index -= 1
    self.index %= len(self.widgets)
    self.widgets[self.index].show()
