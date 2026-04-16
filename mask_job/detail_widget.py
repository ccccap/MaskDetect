from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QScrollArea, QVBoxLayout, QWidget
import sys
from sql_class import sql_class_add_people
from show import show_widget


widget_css="""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                color: #333;
                padding: 10px;
                background-color: #f0f0f0;
            }
            QLabel#label_show {
                font-size: 14px;
                color: #333;
                padding: 15px;
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
                white-space: pre-wrap;
            }
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                border: 1px solid #5b9bd5;
                border-radius: 5px;
                background-color: #5b9bd5;
                color: white;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #4a89c2;
            }
            QPushButton:pressed {
                background-color: #397baf;
            }
            QScrollArea {
                border: none;
            }
            QVBoxLayout {
                margin: 10px;
            }
            QHBoxLayout {
                margin: 10px;
                justify-content: center;
            }
        """

class detail_widget(QtWidgets.QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.sql_class = sql_class_add_people('localhost', 'root', 'root', 'photo', 'photo_list')
        self.show_ID_list = []
        self.show_widget = show_widget(self.sql_class, self)

        # 设置窗口大小
        self.resize(640, 540)

        # 创建控件
        self.label_show = QtWidgets.QLabel(self)
        self.label_show.setObjectName("label_show")
        self.label_show.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.btn_detail_show = QtWidgets.QPushButton("显示详细信息", self)
        self.btn_close = QtWidgets.QPushButton("关闭", self)

        # 创建滚动区域
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidget(self.label_show)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setMinimumSize(600, 400)

        # 创建布局
        self.layout_top = QtWidgets.QVBoxLayout()
        self.layout_bottom = QtWidgets.QHBoxLayout()
        self.layout_all = QtWidgets.QVBoxLayout()

        # 布局设置
        self.layout_top.addWidget(self.scroll_area)
        self.layout_bottom.addWidget(self.btn_detail_show)
        self.layout_bottom.addWidget(self.btn_close)

        # 设置主布局
        self.layout_all.addLayout(self.layout_top)
        self.layout_all.addLayout(self.layout_bottom)

        self.setLayout(self.layout_all)
        self.setWindowTitle("视频详情显示")

        # 信号与槽连接
        self.btn_close.clicked.connect(lambda: self.change_video_show(self.mainwindow, self))
        self.btn_detail_show.clicked.connect(lambda: self.change_get_list_video_show(self.show_widget, self))

        # 应用样式
        self.setStyleSheet(widget_css)

    def change_video_show(self, show, close):
        self.label_show.clear()
        show.show()
        close.hide()

    def change_get_list_video_show(self, show, close):
        self.get_ID_list()
        show.show()
        close.hide()

    def get_ID_list(self):
        all = self.sql_class.read_photo_list()
        self.show_ID_list.clear()
        self.show_widget.comboBox.clear()
        self.show_ID_list.append("None")
        for i in all:
            self.show_ID_list.append(i[1])
        self.show_widget.comboBox.addItems(self.show_ID_list)


if __name__ =='__main__':
    app = QApplication(sys.argv)
    window = detail_widget()
    window.show()
    sys.exit(app.exec())
