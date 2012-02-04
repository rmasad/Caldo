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
# PyQt4 QtGui
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QTableView
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QStandardItemModel

# Caldo Libs
from utils import from_bit_to
from utils import list_to_tree

class SearchTabClass(QWidget):
  def __init__(self, parent = None):
    QWidget.__init__(self, parent)
    vLayout = QVBoxLayout(self)
    self.SearchTable = SearchTable()
    vLayout.addWidget(self.SearchTable)

class SearchTable(QTableView):
  def __init__(self, parent = None):
    QTableView.__init__(self, parent)
    self.ascendingIcon = QIcon("./img/ascending.png")
    self.descendingIcon = QIcon("./img/descending.png")

    self.results = []

    self.currentColumnSort = [None, None]
    self.setModel(self.makeModel([], 2))
    self.connect(self.horizontalHeader(),
                SIGNAL('sectionClicked(int)'),
                self.horizontalHeaderClicked)

    #self.setSortingEnabled(True)
    self.setCornerButtonEnabled(False)
    # Hide vertical header (numbers at left side)
    self.verticalHeader().hide()
    # Select by rows
    self.setSelectionBehavior(QAbstractItemView.SelectRows)
    # Can't edit items
    self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # Resize columns
    self.horizontalHeader().setResizeMode(0, 1)
    for i in range(1, 4):
      self.resizeColumnToContents(i)

  def horizontalHeaderClicked(self, i):
    self.setModel(self.makeModel(self.results, i))
    if self.currentColumnSort:
      self.resizeColumnToContents(self.currentColumnSort[0])

  def makeModel(self, results, index = 2):
    getAttr = [lambda obj: obj.name,
               lambda obj: obj.size[0]*(1024**obj.size[1]),
               lambda obj: obj.seed,
               lambda obj: obj.leach]

    col = len(results)

    ascending = False if index == self.currentColumnSort[0] and self.currentColumnSort[1] else True
    self.currentColumnSort = [index, ascending]

    model = QStandardItemModel(col, 4, self)
    columnHeaderItems = [QStandardItem(column) for column in "Name", "Size", "Seeds", "Leachs"]
    columnHeaderItems[index].setIcon(self.ascendingIcon if ascending else self.descendingIcon)
    for i in range(4):
      model.setHorizontalHeaderItem(i, columnHeaderItems[i])

    if results:
      results = list_to_tree(results, lambda x, y: getAttr[index](x) > getAttr[index](y))
      if ascending: results = results.postOrder()
      else: results = results.preOrder()
      self.results = results

    for i in range(col):
      result = results[i]
      size = from_bit_to(result.size[0]*1024**result.size[1])

      model.setItem(i, 0, QStandardItem(result.name))
      model.setItem(i, 1, QStandardItem(size))
      model.setItem(i, 2, QStandardItem(str(result.seed)))
      model.setItem(i, 3, QStandardItem(str(result.leach)))
    return model

  def addResults(self, results):
    for item in results:
      if item.ID not in [result.ID for result in self.results]:
        self.results.append(item)

    index = self.currentColumnSort[0]
    self.currentColumnSort[1] = not self.currentColumnSort[1]

    self.setModel(self.makeModel(self.results, index))
