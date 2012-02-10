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

from PyQt4.QtCore import QTimer

class BST:
  def __init__(self, value):
    self.value = value
    self.left = None
    self.right = None

  def add_left(self, value, higher = None):
    if not self.left:
      self.left = BST(value)
    else:
      self.left.add(value, higher)

  def add_right(self, value, higher = None):
    if not self.right:
      self.right = BST(value)
    else:
      self.right.add(value, higher)

  def add(self, value, higher):
    if higher(self.value, value):
      self.add_left(value, higher)
    else:
      self.add_right(value, higher)

  def preOrder(self):
    preOrderResult = []

    if self.left: preOrderResult += self.left.preOrder()
    preOrderResult.append(self.value)
    if self.right: preOrderResult += self.right.preOrder()

    return preOrderResult

  def postOrder(self):
    postOrderResult = []

    if self.right: postOrderResult += self.right.postOrder()
    postOrderResult.append(self.value)
    if self.left: postOrderResult += self.left.postOrder()

    return postOrderResult

def list_to_tree(values, higher):
  Tree = BST(values.pop())
  while values:
    Tree.add(values.pop(), higher)
  return Tree

def from_bit_to(size):
    i = 0
    while size > 1024:
      size /= 1024.
      i+= 1
    unit = ["Bytes", "KBi", "MBi", "GBi"][i]
    if not int(10*(size%1)): return "%d %s" % (int(size), unit)
    elif not int(10*((10*size)%1)): return "%0.1f %s" % (size, unit)
    else: return "%0.2f %s" % (size, unit)

def new_timer(time):
  timer = QTimer()
  timer.setSingleShot(False)
  timer.start(time)
  return timer
