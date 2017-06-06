#!/usr/bin/env python
"""
.. py:currentmodule:: gui.application
.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Main module for x-ray phase map application GUI.
"""

###############################################################################
# Copyright 2016 Hendrix Demers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

# Standard library modules.
import logging
from logging.handlers import RotatingFileHandler
import os.path
import sys


# Third party modules.
from PySide import QtCore, QtGui
import matplotlib
matplotlib.use('Qt4Agg', warn=False)
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Local modules.

# Project modules

# Globals and constants variables.
APPLICATION_NAME = "pyXRayPhaseMap"
ORGANIZATION_NAME = "McGill University"
LOG_FILENAME = APPLICATION_NAME + '.log'

MODULE_LOGGER = logging.getLogger(APPLICATION_NAME)

class MainWindow(QtGui.QMainWindow):
    NumGridRows = 3
    def __init__(self):
        self.logger = logging.getLogger(APPLICATION_NAME + '.MainWindow')
        self.logger.info("MainWindow.__init__")

        super(MainWindow, self).__init__()

        self.curFile = ''

        self.textEdit = QtGui.QTextEdit()
        #self.setCentralWidget(self.textEdit)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

        self.createGridGroupBox()

        self.readSettings()

        self.textEdit.document().contentsChanged.connect(self.documentWasModified)

        self.setCurrentFile('')
        self.setUnifiedTitleAndToolBarOnMac(True)

        self.plotGroupBox = QtGui.QGroupBox("Plot layout")
        # generate the plot
        fig = Figure(figsize=(600,600), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
        ax = fig.add_subplot(111)
        ax.plot([0,1])
        # generate the canvas to display the plot
        canvas1 = FigureCanvas(fig)
        # create a layout inside the blank widget and add the matplotlib widget
        layout = QtGui.QVBoxLayout()
        layout.addWidget(canvas1, 1)

        # generate the plot
        fig = Figure(figsize=(600,600), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
        ax = fig.add_subplot(111)
        ax.plot([0,2])
        # generate the canvas to display the plot
        canvas2 = FigureCanvas(fig)
        # create a layout inside the blank widget and add the matplotlib widget
        layout.addWidget(canvas2, 2)
        self.plotGroupBox.setLayout(layout)

        mainLayout = QtGui.QVBoxLayout()
        #mainLayout.setMenuBar(self.menuBar)
        #mainLayout.addWidget(self.horizontalGroupBox)
        #mainLayout.addWidget(self.gridGroupBox)
        #mainLayout.addWidget(self.formGroupBox)
        #mainLayout.addWidget(bigEditor)
        mainLayout.addWidget(self.plotGroupBox)
        #self.setLayout(mainLayout)
        self.mainGroupBox = QtGui.QGroupBox("Main layout")
        self.mainGroupBox.setLayout(mainLayout)
        self.setCentralWidget(self.mainGroupBox)

    def createGridGroupBox(self):
        self.logger.info("MainWindow.createGridGroupBox")

        self.gridGroupBox = QtGui.QGroupBox("Grid layout")
        layout = QtGui.QGridLayout()

        for i in range(MainWindow.NumGridRows):
            label = QtGui.QLabel("Line %d:" % (i + 1))
            lineEdit = QtGui.QLineEdit()
            layout.addWidget(label, i + 1, 0)
            layout.addWidget(lineEdit, i + 1, 1)

        self.smallEditor = QtGui.QTextEdit()
        self.smallEditor.setPlainText("This widget takes up about two thirds "
                                      "of the grid layout.")
        layout.addWidget(self.smallEditor, 0, 2, 4, 1)
        layout.setColumnStretch(1, 10)
        layout.setColumnStretch(2, 20)
        self.gridGroupBox.setLayout(layout)

    def closeEvent(self, event):
        self.logger.info("MainWindow.closeEvent")

        if self.maybeSave():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    def newFile(self):
        self.logger.info("MainWindow.newFile")

        if self.maybeSave():
            self.textEdit.clear()
            self.setCurrentFile('')

    def open(self):
        self.logger.info("MainWindow.open")

        if self.maybeSave():
            fileName, _filtr = QtGui.QFileDialog.getOpenFileName(self)
            if fileName:
                self.loadFile(fileName)

    def save(self):
        self.logger.info("MainWindow.save")

        if self.curFile:
            return self.saveFile(self.curFile)

        return self.saveAs()

    def saveAs(self):
        self.logger.info("MainWindow.saveAs")

        fileName, _filtr = QtGui.QFileDialog.getSaveFileName(self)
        if fileName:
            return self.saveFile(fileName)

        return False

    def about(self):
        self.logger.info("MainWindow.about")

        QtGui.QMessageBox.about(self, "About Application",
                "The <b>Application</b> example demonstrates how to write "
                "modern GUI applications using Qt, with a menu bar, "
                "toolbars, and a status bar.")

    def documentWasModified(self):
        self.logger.info("MainWindow.documentWasModified")

        self.setWindowModified(self.textEdit.document().isModified())

    def createActions(self):
        self.logger.info("MainWindow.createActions")

        self.newAct = QtGui.QAction(QtGui.QIcon(':/images/new.png'), "&New",
                self, shortcut=QtGui.QKeySequence.New,
                statusTip="Create a new file", triggered=self.newFile)

        self.openAct = QtGui.QAction(QtGui.QIcon(':/images/open.png'),
                "&Open...", self, shortcut=QtGui.QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.open)

        self.saveAct = QtGui.QAction(QtGui.QIcon(':/images/save.png'),
                "&Save", self, shortcut=QtGui.QKeySequence.Save,
                statusTip="Save the document to disk", triggered=self.save)

        self.saveAsAct = QtGui.QAction("Save &As...", self,
                shortcut=QtGui.QKeySequence.SaveAs,
                statusTip="Save the document under a new name",
                triggered=self.saveAs)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)

        self.cutAct = QtGui.QAction(QtGui.QIcon(':/images/cut.png'), "Cu&t",
                self, shortcut=QtGui.QKeySequence.Cut,
                statusTip="Cut the current selection's contents to the clipboard",
                triggered=self.textEdit.cut)

        self.copyAct = QtGui.QAction(QtGui.QIcon(':/images/copy.png'),
                "&Copy", self, shortcut=QtGui.QKeySequence.Copy,
                statusTip="Copy the current selection's contents to the clipboard",
                triggered=self.textEdit.copy)

        self.pasteAct = QtGui.QAction(QtGui.QIcon(':/images/paste.png'),
                "&Paste", self, shortcut=QtGui.QKeySequence.Paste,
                statusTip="Paste the clipboard's contents into the current selection",
                triggered=self.textEdit.paste)

        self.aboutAct = QtGui.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QtGui.qApp.aboutQt)

        self.cutAct.setEnabled(False)
        self.copyAct.setEnabled(False)
        self.textEdit.copyAvailable.connect(self.cutAct.setEnabled)
        self.textEdit.copyAvailable.connect(self.copyAct.setEnabled)

    def createMenus(self):
        self.logger.info("MainWindow.createMenus")

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator();
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.logger.info("MainWindow.createToolBars")

        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)

        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)

    def createStatusBar(self):
        self.logger.info("MainWindow.createStatusBar")

        self.statusBar().showMessage("Ready")

    def readSettings(self):
        self.logger.info("MainWindow.readSettings")

        settings = QtCore.QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        pos = settings.value("pos", QtCore.QPoint(200, 200))
        size = settings.value("size", QtCore.QSize(400, 400))
        self.resize(size)
        self.move(pos)

    def writeSettings(self):
        self.logger.info("MainWindow.writeSettings")

        settings = QtCore.QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())

    def maybeSave(self):
        self.logger.info("MainWindow.maybeSave")

        if self.textEdit.document().isModified():
            ret = QtGui.QMessageBox.warning(self, "Application",
                    "The document has been modified.\nDo you want to save "
                    "your changes?",
                    QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                    QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Save:
                return self.save()
            elif ret == QtGui.QMessageBox.Cancel:
                return False
        return True

    def loadFile(self, fileName):
        self.logger.info("MainWindow.loadFile")

        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, "Application",
                    "Cannot read file %s:\n%s." % (fileName, file.errorString()))
            return

        inf = QtCore.QTextStream(file)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.textEdit.setPlainText(inf.readAll())
        QtGui.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        self.statusBar().showMessage("File loaded", 2000)

    def saveFile(self, fileName):
        self.logger.info("MainWindow.saveFile")

        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, "Application",
                    "Cannot write file %s:\n%s." % (fileName, file.errorString()))
            return False

        outf = QtCore.QTextStream(file)
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        outf << self.textEdit.toPlainText()
        QtGui.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName);
        self.statusBar().showMessage("File saved", 2000)
        return True

    def setCurrentFile(self, fileName):
        self.logger.info("MainWindow.setCurrentFile")

        self.curFile = fileName
        self.textEdit.document().setModified(False)
        self.setWindowModified(False)

        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'untitled.txt'

        self.setWindowTitle("%s[*] - Application" % shownName)

    def strippedName(self, fullFileName):
        self.logger.info("MainWindow.strippedName")

        return QtCore.QFileInfo(fullFileName).fileName()

def createApplication():
    application = QtGui.QApplication(sys.argv)
    application.setApplicationName(APPLICATION_NAME)
    application.setOrganizationName(ORGANIZATION_NAME)

    return application

def startLogging():
    dataLocation = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.DataLocation)
    if not os.path.isdir(dataLocation):
        os.makedirs(dataLocation)

    logFilepath = os.path.join(dataLocation, LOG_FILENAME)
    fh = RotatingFileHandler(logFilepath, maxBytes=1024*30, backupCount=10)
    MODULE_LOGGER.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
    fh.setFormatter(formatter)
    MODULE_LOGGER.addHandler(fh)
    MODULE_LOGGER.info("startLogging")

    MODULE_LOGGER.debug("Data location: %s", dataLocation)
    MODULE_LOGGER.debug("Applications location: %s", QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.ApplicationsLocation))
    MODULE_LOGGER.debug("Home location: %s", QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.HomeLocation))
    MODULE_LOGGER.debug("Temp location: %s", QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.TempLocation))
    MODULE_LOGGER.debug("Cache location: %s", QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.CacheLocation))

def run():
    # Note application and mainWin have to be declared in the same method.
    application = createApplication()
    startLogging()
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(application.exec_())

if __name__ == '__main__': #pragma: no cover
    run()
