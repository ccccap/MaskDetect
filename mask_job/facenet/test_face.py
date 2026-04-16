import os
import pymysql
from mask_job.facenet.retinaface import Retinaface
from mask_job.sql_class import sql_class_add_people
'''
在更换facenet网络后一定要重新进行人脸编码，运行encoding.py。
'''
def encoding(sql_class_add):
    rmpath_list=os.listdir(os.path.dirname(__file__)+"\\face_dataset")
    for i in rmpath_list:
        os.remove(os.path.dirname(__file__)+"\\face_dataset\\"+i)

    retinaface = Retinaface(1)
    sql_class=sql_class_add
    all=sql_class.read_photo_list()
    image_paths = []
    names = []
    ID=[]
    for i in all:
        print(os.path.dirname(__file__)+"\\face_dataset\\"+i[0]+".jpg")
        with open(os.path.dirname(__file__)+"\\face_dataset\\"+i[0]+".jpg", "wb") as file:
            file.write(i[4])
        image_paths.append(os.path.dirname(__file__)+"face_dataset\\" + i[0]+".jpg")
        names.append(i[0])
        ID.append(i[1])


    print(image_paths)
    print(ID)
    retinaface.encode_face_dataset(image_paths,names,ID)



if __name__ == '__main__':
    rmpath_list=os.listdir(os.path.dirname(__file__)+"\\face_dataset")
    for i in rmpath_list:
        os.remove(os.path.dirname(__file__)+"\\face_dataset\\"+i)

    retinaface = Retinaface(1)
    sql_class=sql_class_add_people('localhost','root','root','photo','photo_list')
    all=sql_class.read_photo_list()
    image_paths = []
    names = []
    ID=[]
    for i in all:
        print(os.path.dirname(__file__)+"\\face_dataset\\"+i[0]+".jpg")
        with open(os.path.dirname(__file__)+"\\face_dataset\\"+i[0]+".jpg", "wb") as file:
            file.write(i[4])
        image_paths.append("face_dataset/" + i[0]+".jpg")
        names.append(i[0])
        ID.append(i[1])


    print(image_paths)
    print(ID)
    retinaface.encode_face_dataset(image_paths,names,ID)