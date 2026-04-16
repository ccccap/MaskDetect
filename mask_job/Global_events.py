import sys
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QPushButton, QWidget
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

def change_video_show(show,close):
    show.show()
    close.hide()