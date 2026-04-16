import pymysql
import numpy as np
# 创建连接
conn = pymysql.connect(host="localhost", user="root", password="root",database="face_data")

# 创建游标
cursor = conn.cursor()

# 执行SQL
#cursor.execute("CREATE DATABASE text1")  # 创建数据库text1
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS cap_list (
#         name VARCHAR(255),
#         ip VARCHAR(255) PRIMARY KEY,
#         account VARCHAR(255),
#         password VARCHAR(255)
#     )
# """) //创建表
# cursor.execute("""
#     INSERT INTO cap_list (name, ip, account, password)
#     VALUES (%s, %s, %s, %s)
# """, ('John Doe', '192.168.0.1', 'root', 'root'))

cursor.execute(f"SELECT * FROM face_list")
rows = cursor.fetchall()
a=[]

for i in rows:
    print(i)
    a.append(i[2])

face_encodings_retrieved = np.frombuffer(a[1], dtype=np.float32).reshape(4,)
print(face_encodings_retrieved.shape)
# 提交，不然无法保存新建或者修改的数据
conn.commit()

# 关闭游标和连接
cursor.close()
conn.close()