import sys
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QPushButton, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap, QImage, QGuiApplication
import cv2
import math
from threading import Thread
import time
import requests
import random
import numpy as np
import onnxruntime as ort
import onnx
import torch
from PyQt6 import uic

import threading
from video_change import Ui_video_change
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import facenet.predict
import sql_class
import facenet.retinaface
from add_people import Ui_add_people
from detail_widget import detail_widget

btn_css = """
            QPushButton {
                background-color: #4CAF50;  /* 按钮背景颜色 */
                color: white;  /* 按钮文字颜色 */
                border-radius: 12px;  /* 圆角按钮 */
                font-size: 18px;  /* 字体大小 */
                padding: 10px 20px;  /* 按钮内边距 */
                border: none;  /* 去掉默认边框 */
                transition: all 0.3s;  /* 动效 */
            }
            QPushButton:hover {
                background-color: #45a049;  /* 鼠标悬停时按钮颜色 */
            }
            QPushButton:pressed {
                background-color: #388e3c;  /* 按钮按下时稍微缩小 */
                transform: scale(0.95);
            }
        """

widget_css = """
            #all {
                background-image : url('image_css/video_widget.png');
                border-radius: 15px;  /* 圆角 */
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);  /* 阴影效果 */
            }
        """

label_css = '''
          display: inline-block;
          font-size: 16px;
          font-weight: 600;
          background: linear-gradient(135deg, #4a90e2, #50e3c2);
          border-radius: 30px; /* 圆角边框 */
          border: 2px solid black;
          background-clip: padding-box;
          cursor: pointer;
          transition: all 0.3s ease-in-out;
        '''


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print(__file__)
        print(os.path.abspath(__file__))  # 获取当前文件的绝对路径
        print(os.path.dirname(os.path.abspath(__file__)))  # 去掉文件名，返回目录
        print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 返回上2级目录

        self.sql_class = sql_class.sql_class('localhost', 'root', 'root', 'caps', 'cap_list')
        self.retinaface = facenet.retinaface.Retinaface()
        self.cap_thread_list = []
        self.grid = QGridLayout()
        self.grid_btn = QGridLayout()
        self.layout_all = QVBoxLayout()
        self.bottom_widget = QWidget()
        self.all_widget = QWidget()

        self.video_cap_list = {}  # 摄像头字典对象 存放key=名称 value=[ip,账号,密码]
        self.create_video_cap_list()
        self.lbl_img_list = []  # 展示摄像头视频流的labels列表
        self.btn_list = []

        # 初始化线程锁（关键修改1：统一锁对象）
        self.picture_lock = threading.Lock()
        self.face_img_lock = threading.Lock()

        with open('./param.txt', 'r') as f:  # 读取需要创建的labels个数
            self.param = f.readlines()
            self.label_num = int(self.param[0])

        self.setWindowTitle('pyqt6显示opencv获取的摄像头图像')
        self.btn_camera = QPushButton('打开摄像头')  # 控制摄像头的状态
        self.btn_check = QPushButton('修改摄像头')  # 切换至添加摄像头页面
        self.btn_check_add = QPushButton('添加人脸')  # 添加人脸
        self.btn_detail = QPushButton('个人信息')  # 获取个人信息
        self.btn_list.append(self.btn_camera)
        self.btn_list.append(self.btn_check)
        self.btn_list.append(self.btn_check_add)
        self.btn_list.append(self.btn_detail)

        self.top_widget = QWidget()
        self.video_change = Ui_video_change(self.video_cap_list, self, self.sql_class)  # 创建增添删改摄像头对象的控件类对象 传递存储摄像头的字典对象
        self.add_people = Ui_add_people(self, self.retinaface)
        self.detail_widget = detail_widget(self)

        self.create_label()  # 初始化labels
        self.picture = []
        self.face_img_list = []
        self.btn_camera.clicked.connect(self.btn_camera_click)

        self.is_open_camera = [False]  # 是否打开了摄像头标志位
        self.video_cap = []
        self.btn_check.clicked.connect(lambda: self.change_video_show(self.video_change, self))
        self.btn_check_add.clicked.connect(lambda: self.change_video_show(self.add_people, self))
        self.btn_detail.clicked.connect(lambda: self.change_video_show(self.detail_widget, self))
        self.camera_timer = QtCore.QTimer(self)  # 创建读取摄像头图像的定时器
        self.camera_timer.timeout.connect(self.play_camera_video)
        self.resize(1080, 640)

    def create_video_cap_list(self):
        self.video_cap_list.clear()
        tuple_cap = self.sql_class.read_cap_list()
        for i in tuple_cap:
            self.video_cap_list[i[0]] = [i[1], i[2], i[3]]
        print(self.video_cap_list)

    def create_label(self):
        '''
        创建展示视频流的labels列表 并布局
        :param n: 需要创建的labels个数
        :return: 无
        '''
        del self.grid
        self.lbl_img_list.clear()
        del self.top_widget
        del self.layout_all
        del self.bottom_widget
        del self.all_widget
        self.create_video_cap_list()
        print(len(self.video_cap_list))

        self.layout_all = QVBoxLayout()
        self.grid = QGridLayout()
        self.top_widget = QWidget()
        self.bottom_widget = QWidget()
        self.all_widget = QWidget()

        data = ''
        if (len(self.video_cap_list) + 1) % 2 == 0:
            n = len(self.video_cap_list) + 1
        else:
            n = len(self.video_cap_list) + 1 + 1
        with open('./param.txt', 'r') as f:
            param = f.readlines()
            param[0] = str(n)
            for i in param:
                if i != '\n':
                    data += i + '\n'
        with open('./param.txt', 'w') as f:
            f.write(data)
        self.label_num = n
        for i in range(self.label_num):
            self.lbl_img_list.append(QLabel('显示摄像头' + str(i)))
        for i in range(self.label_num):
            self.lbl_img_list[i].setStyleSheet(label_css)  # 给标签设置黑色边框
            self.lbl_img_list[i].setAlignment(Qt.AlignmentFlag.AlignCenter)  # 让标签要显示的内容居中
            self.lbl_img_list[i].setMinimumSize(int(960 / self.label_num),
                                                int(640 / self.label_num))  # 宽和高保持和摄像头获取的默认大小一致
            self.grid.addWidget(self.lbl_img_list[i], int(i / math.ceil(self.label_num ** 0.5)),
                                i % math.ceil(self.label_num ** 0.5))

        self.btn_camera.setStyleSheet(btn_css)
        self.btn_detail.setStyleSheet(btn_css)
        self.btn_check.setStyleSheet(btn_css)
        self.btn_check_add.setStyleSheet(btn_css)
        self.grid_btn.addWidget(self.btn_camera, 0, 0, QtCore.Qt.AlignmentFlag.AlignBottom)  # 放置底部
        self.grid_btn.addWidget(self.btn_check, 0, 1, QtCore.Qt.AlignmentFlag.AlignBottom)  # 放置底部
        self.grid_btn.addWidget(self.btn_check_add, 1, 0, QtCore.Qt.AlignmentFlag.AlignBottom)  # 放置底部
        self.grid_btn.addWidget(self.btn_detail, 1, 1, QtCore.Qt.AlignmentFlag.AlignBottom)  # 放置底部
        self.top_widget.setLayout(self.grid)
        self.bottom_widget.setLayout(self.grid_btn)
        self.layout_all.addWidget(self.top_widget, 4)
        self.layout_all.addWidget(self.bottom_widget, 1)
        self.all_widget.setLayout(self.layout_all)
        self.all_widget.setObjectName("all")
        self.all_widget.setStyleSheet(widget_css)
        self.setCentralWidget(self.all_widget)

    def btn_camera_click(self):
        if not self.is_open_camera[0]:  # 按下 打开摄像头 按钮
            self.is_open_camera[0] = True
            for i in self.video_cap_list:
                rtsp_url = f"rtsp://{self.video_cap_list[i][1]}:{self.video_cap_list[i][2]}@{self.video_cap_list[i][0]}/stream0"
                cap = cv2.VideoCapture(rtsp_url)
                self.video_cap.append(cap)

            cap = cv2.VideoCapture(0)
            self.video_cap.append(cap)

            self.play_camera_video()
            # 启动线程（关键修改2：传递统一的锁对象）
            p = Thread(target=self.ce, args=(self.picture, self.picture_lock,))
            p1 = Thread(target=facenet.predict.face_rec,
                        args=(self.face_img_list, self.retinaface, self.is_open_camera))
            p1.start()
            p.start()

            self.btn_camera.setText('关闭摄像头')

        else:  # 按下 关闭摄像头 按钮
            n = len(self.video_cap)
            for i in self.video_cap:
                i.release()
            for i in range(self.label_num):
                self.lbl_img_list[i].clear()
            self.video_cap.clear()
            self.btn_camera.setText('打开摄像头')
            self.is_open_camera[0] = False

    def play_camera_video(self):
        if self.is_open_camera[0]:
            n = 0
            for i in self.video_cap:
                # 关键修改3：传递统一的锁对象，避免重复创建锁
                p = Thread(target=self.get_picture, args=(i, n, self.picture_lock, self.is_open_camera,))
                self.cap_thread_list.append(p)
                p.start()
                n += 1

    def get_picture(self, i, n, mutex_camera, is_open_camera):
        # 关键修改4：优化循环逻辑，避免无限循环
        # 确定摄像头名称
        camera_name = "Local Camera" if n == len(self.video_cap_list) else list(self.video_cap_list.keys())[n]
        
        while is_open_camera[0]:
            ret, frame = i.read()  # 读取视频流的每一帧
            if not ret:  # 读取失败直接跳过
                time.sleep(0.01)
                continue

            mutex_camera.acquire()
            try:
                # 限制列表长度，避免内存溢出
                if len(self.picture) < self.label_num * 2:
                    self.picture.append((frame, camera_name))
                # 超过长度时替换最旧的帧
                elif len(self.picture) >= self.label_num * 2:
                    self.picture.pop(0)
                    self.picture.append((frame, camera_name))
            finally:
                mutex_camera.release()

            # 转换并显示图像
            height, width, channel = frame.shape
            img = QImage(frame.data, width, height, QImage.Format.Format_RGB888)
            img = img.rgbSwapped()
            pixmap = QPixmap.fromImage(img)

            lbl_width = self.lbl_img_list[n].size().width()
            lbl_height = self.lbl_img_list[n].size().height()

            pixmap = pixmap.scaled(
                lbl_width - 10, lbl_height - 10,
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)

            self.lbl_img_list[n].setPixmap(pixmap)
            time.sleep(0.01)  # 降低CPU占用

    def ce(self, picture, mutex):
        cuda = torch.cuda.is_available()
        w = "./best.onnx"  # 模型名称
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if cuda else ['CPUExecutionProvider']
        session = ort.InferenceSession(w, providers=providers)
        # 类别名称，根据需要自己修改
        names = ['no mask', 'mask']
        colors = {name: [random.randint(0, 255) for _ in range(2)] for i, name in enumerate(names)}

        while True:
            if not self.is_open_camera[0]:
                mutex.acquire()
                try:
                    # 清空列表
                    while len(picture) > 0:
                        picture.pop(0)
                finally:
                    mutex.release()
                break

            mutex.acquire()
            # 关键修改5：多层空值检查，核心修复点
            has_valid_frame = False
            ori_images = []
            camera_name = "Unknown"
            if len(picture) > 0:
                # 检查picture[0]是否为None
                if picture[0] is not None:
                    try:
                        # 现在picture中存储的是 (frame, camera_name) 元组
                        frame, camera_name = picture[0]
                        ori_images = [frame.copy()]
                        picture.pop(0)
                        has_valid_frame = True
                    except Exception as e:
                        print(f"复制帧失败: {e}")
                        picture.pop(0)
                else:
                    picture.pop(0)
            mutex.release()

            # 没有有效帧则跳过
            if not has_valid_frame:
                time.sleep(0.01)
                continue

            # 处理帧数据
            image = ori_images[0].copy()
            image, ratio, dwdh = self.letterbox(image, auto=False)
            image = image.transpose((2, 0, 1))
            image = np.expand_dims(image, 0)
            image = np.ascontiguousarray(image)

            # 归一化
            im = image.astype(np.float32)
            im /= 255

            outname = [i.name for i in session.get_outputs()]
            inname = [i.name for i in session.get_inputs()]

            # 调用模型得出结果，并记录时间
            inp = {inname[0]: im}
            t1 = time.time()
            outputs = session.run(outname, inp)[0]

            app = None
            for i, (batch_id, x0, y0, x1, y1, cls_id, score) in enumerate(outputs):
                image = ori_images[int(batch_id)]
                box = np.array([x0, y0, x1, y1])
                box -= np.array(dwdh * 2)
                box /= ratio
                box = box.round().astype(np.int32).tolist()
                cls_id = int(cls_id)
                score = round(float(score), 3)
                name = names[cls_id]
                color = colors[name]
                name += ' ' + str(score)
                cv2.rectangle(image, box[:2], box[2:], color, 2)
                cv2.putText(image, name, (box[0], box[1] - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.75, [225, 255, 255],
                            thickness=2)
                if cls_id == 0:
                    print(f"[{camera_name}] 口鼻无遮挡")
                    app = True
                    # 记录违规日志
                    if self.sql_class:
                        try:
                            self.sql_class.log_violation("Unknown", "Unknown", camera_name, "未戴口罩", score)
                            print(f"已记录违规日志: {camera_name} - 未戴口罩")
                        except Exception as e:
                            print(f"记录日志失败: {e}")
                if cls_id == 1:
                    print(f"[{camera_name}] 口鼻有遮挡")

            if app:
                self.face_img_lock.acquire()
                try:
                    if len(self.face_img_list) < self.label_num * 2:
                        # 传递帧和摄像头名称到人脸识别模块
                        self.face_img_list.append((ori_images[0], camera_name))
                finally:
                    self.face_img_lock.release()

    def letterbox(self, im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return im, r, (dw, dh)

    def change_video_show(self, show, close):
        if not self.is_open_camera[0]:
            show.show()
            close.hide()
        else:
            self.camera_timer.stop()
            for i in self.video_cap:
                i.release()
            for i in range(self.label_num):
                self.lbl_img_list[i].clear()
            self.video_cap.clear()
            self.btn_camera.setText('打开摄像头')
            self.is_open_camera[0] = False
            show.show()
            close.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())