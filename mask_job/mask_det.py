import random
import numpy as np
import onnxruntime as ort
import onnx
import torch
import time
import cv2

class mask_det():
    def __init__(self, sql_class=None, camera_name="Unknown"):
        self.is_open_camera=False
        self.sql_class = sql_class
        self.camera_name = camera_name
        pass

    def ce(self,picture):
        cuda = torch.cuda.is_available()
        w = "E:\\dopython\\learn\\best.onnx"  # 模型名称
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if cuda else ['CPUExecutionProvider']
        session = ort.InferenceSession(w, providers=providers)
        # 类别名称，根据需要自己修改
        names = ['no mask', 'mask']
        colors = {name: [random.randint(0, 255) for _ in range(2)] for i, name in enumerate(names)}
        while True:
            if self.is_open_camera==False:
                while len(picture)!=0:
                    picture.pop()
                break
            if len(picture) != 0:
                ori_images = [picture[-1].copy()]

                # if x==5:

                image = picture[-1].copy()
                if(len(picture)!=0):
                    picture.pop()
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
                # print(outputs.shape)
                print('inference time :%.4f' % (time.time() - t1))
                print(outputs)
                # 可视化结果
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
                        print("口鼻无遮挡")
                    if cls_id == 1:
                        print("口鼻有遮挡")
                #cv2.imshow('dddd', ori_images[0])

    def letterbox(self,im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
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
        # print(shape[::-1])
        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return im, r, (dw, dh)

    def change_open(self,boo):
        self.is_open_camera=boo
