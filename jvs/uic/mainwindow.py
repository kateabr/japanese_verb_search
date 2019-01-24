# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(761, 585)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layout = QtWidgets.QGridLayout(self.centralwidget)
        self.layout.setObjectName("layout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.filesView = QtWidgets.QListView(self.splitter)
        self.filesView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.filesView.setAlternatingRowColors(True)
        self.filesView.setObjectName("filesView")
        self.textView = HighlightTextEdit(self.splitter)
        font = QtGui.QFont()
        font.setFamily("Yu Gothic")
        font.setPointSize(11)
        self.textView.setFont(font)
        self.textView.setReadOnly(True)
        self.textView.setObjectName("textView")
        self.layout.addWidget(self.splitter, 1, 1, 1, 2)
        self.searchBox = QtWidgets.QLineEdit(self.centralwidget)
        self.searchBox.setObjectName("searchBox")
        self.layout.addWidget(self.searchBox, 0, 2, 1, 1)
        self.searchLabel = QtWidgets.QLabel(self.centralwidget)
        self.searchLabel.setObjectName("searchLabel")
        self.layout.addWidget(self.searchLabel, 0, 1, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName("progressBar")
        self.layout.addWidget(self.progressBar, 2, 1, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 761, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpenDir = QtWidgets.QAction(MainWindow)
        self.actionOpenDir.setObjectName("actionOpenDir")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOpenDir)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Japanese Verb Search"))
        self.searchLabel.setText(_translate("MainWindow", "Search"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpenDir.setText(_translate("MainWindow", "Open Directory"))
        self.actionOpenDir.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionExit.setShortcut(_translate("MainWindow", "Ctrl+Q"))

from jvs.highlighttextedit import HighlightTextEdit
