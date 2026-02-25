from PyQt5 import QtWidgets, QtGui


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 400)
        MainWindow.setWindowTitle("pystock")

        central_widget = QtWidgets.QWidget(MainWindow)
        layout = QtWidgets.QVBoxLayout(central_widget)

        label = QtWidgets.QLabel("Start）")
        label.setObjectName("placeholderLabel")
        layout.addWidget(label)

        # Buttons
        btn_start = QtWidgets.QPushButton("Start")
        btn_start.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))
        btn_start.setObjectName("btnStart")
        layout.addWidget(btn_start)

        btn_stop = QtWidgets.QPushButton("Stop")
        btn_stop.setIcon(QtGui.QIcon.fromTheme("media-playback-stop"))
        btn_stop.setObjectName("btnStop")
        layout.addWidget(btn_stop)

        # Connect signals
        btn_start.clicked.connect(self.on_start_clicked)
        btn_stop.clicked.connect(self.on_stop_clicked)

        MainWindow.setCentralWidget(central_widget)

    def on_start_clicked(self):
        print("Start button clicked!")
        # 这里可以添加具体的业务逻辑

    def on_stop_clicked(self):
        print("Stop button clicked!")
        # 这里可以添加具体的业务逻辑

