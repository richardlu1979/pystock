#coding:utf-8
import mainwindow

from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
if __name__=='__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = mainwindow.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

