from PyQt4.QtCore import QObject, SIGNAL
from PyQt4.QtGui import QApplication, QLineEdit
import time,sys
from utils.search import SearchThread

def test(lista):
  print lista


app = QApplication(sys.argv)

algo = SearchThread("windows")
algo.start()
a = QObject()
a.connect(algo, SIGNAL('update(PyQt_PyObject)'), test)

app.exec_()
