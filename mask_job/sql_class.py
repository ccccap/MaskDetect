import pymysql
import numpy as np
class sql_class():
    def __init__(self,host,user,password,database_name,table_name):
        self.host=host
        self.user=user
        self.password=password
        self.database_name = database_name
        self.table_name = table_name
        self.create_database()
        self.check_table()


    def create_database(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password)
        self.cursor = self.conn.cursor()
        database_name = self.database_name
        # 查询所有数据库
        self.cursor.execute("SHOW DATABASES")
        # 获取所有数据库名
        databases = [db[0] for db in self.cursor.fetchall()]
        # 检查指定的数据库是否存在
        if database_name in databases:
            print(f"数据库 '{database_name}' 已存在。")
            self.connect_cap_database()
        else:
            print(f"数据库 '{database_name}' 不存在，可以创建。")
            str="CREATE DATABASE "+database_name
            self.cursor.execute(str)
            self.connect_cap_database()

    def check_table(self):
        self.cursor.execute("SHOW TABLES")
        # 获取所有表名
        tables = [table[0] for table in self.cursor.fetchall()]

        # 检查指定的表是否存在
        if self.table_name in tables:
            print(f"表 '{self.table_name}' 已存在。")
        else:
            print(f"表 '{self.table_name}' 不存在，可以创建。")
            self.create_cap_table()

    def connect_cap_database(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password,database=self.database_name)
        self.cursor = self.conn.cursor()
        print("数据库 "+self.database_name+" 连接成功")

    def create_cap_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                name VARCHAR(255) PRIMARY KEY,
                ip VARCHAR(255) ,
                account VARCHAR(255),
                password VARCHAR(255)
            )
        """)
        self.conn.commit()

    def cap_insert(self,name,ip,account,password):
        self.cursor.execute("""
            INSERT INTO cap_list (name, ip, account, password) 
            VALUES (%s, %s, %s, %s)
        """, (name, ip, account, password))
        self.conn.commit()

    def cap_delete(self,delname):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE name = %s", (delname,))
        self.conn.commit()

    def read_cap_list(self):
        # 执行查询获取表的内容
        self.cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = self.cursor.fetchall()
        return rows




class sql_class_face():
    def __init__(self,host,user,password,database_name,table_name):
        self.host=host
        self.user=user
        self.password=password
        self.database_name = database_name
        self.table_name = table_name
        self.create_database()
        self.check_table()



    def create_database(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password)
        self.cursor = self.conn.cursor()
        database_name = self.database_name
        # 查询所有数据库
        self.cursor.execute("SHOW DATABASES")
        # 获取所有数据库名
        databases = [db[0] for db in self.cursor.fetchall()]
        # 检查指定的数据库是否存在
        if database_name in databases:
            print(f"数据库 '{database_name}' 已存在。")
            self.connect_face_database()
        else:
            print(f"数据库 '{database_name}' 不存在，可以创建。")
            str="CREATE DATABASE "+database_name
            self.cursor.execute(str)
            self.connect_face_database()

    def check_table(self):
        self.cursor.execute("SHOW TABLES")
        # 获取所有表名
        tables = [table[0] for table in self.cursor.fetchall()]

        # 检查指定的表是否存在
        if self.table_name in tables:
            print(f"表 '{self.table_name}' 已存在。")
        else:
            print(f"表 '{self.table_name}' 不存在，可以创建。")
            self.create_face_table()

    def connect_face_database(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password,database=self.database_name)
        self.cursor = self.conn.cursor()
        print("数据库 "+self.database_name+" 连接成功")

    def create_face_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                encoding BLOB ,
                o_id VARCHAR (255),
                o_name VARCHAR (255)
            )
        """)
        self.conn.commit()

    def face_insert(self,name,encoding):

        encoding = np.array(encoding)


        encoding_blob = encoding.tobytes()
        self.cursor.execute("""
            INSERT INTO face_list (name, encoding) 
            VALUES (%s, %s)
        """, (name, encoding_blob))
        self.conn.commit()

    def face_delete(self,delname):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE name = %s", (delname,))
        self.conn.commit()

    def read_face_list(self):
        # 执行查询获取表的内容
        self.cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = self.cursor.fetchall()
        return rows

    def o_id_inser(self,name,str):
        self.cursor.execute(f"""
                    INSERT INTO face_list (name,o_id ) 
                    VALUES (%s, %s)
                """, (name, str))

    def o_name_inser(self, name, str):
        self.cursor.execute(f"""
                    INSERT INTO face_list (name,o_name ) 
                    VALUES (%s, %s)
                """, (name, str))


class sql_class_add_people():
    def __init__(self,host,user,password,database_name,table_name):
        self.host=host
        self.user=user
        self.password=password
        self.database_name = database_name
        self.table_name = table_name
        self.create_database()
        self.check_table()


    def create_database(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password)
        self.cursor = self.conn.cursor()
        database_name = self.database_name
        # 查询所有数据库
        self.cursor.execute("SHOW DATABASES")
        # 获取所有数据库名
        databases = [db[0] for db in self.cursor.fetchall()]
        # 检查指定的数据库是否存在
        if database_name in databases:
            print(f"数据库 '{database_name}' 已存在。")
            self.connect_photo_database()
        else:
            print(f"数据库 '{database_name}' 不存在，可以创建。")
            str="CREATE DATABASE "+database_name
            self.cursor.execute(str)
            self.connect_photo_database()

    def check_table(self):
        self.cursor.execute("SHOW TABLES")
        # 获取所有表名
        tables = [table[0] for table in self.cursor.fetchall()]

        # 检查指定的表是否存在
        if self.table_name in tables:
            print(f"表 '{self.table_name}' 已存在。")
        else:
            print(f"表 '{self.table_name}' 不存在，可以创建。")
            self.create_photo_table()

    def connect_photo_database(self):
        self.conn = pymysql.connect(host=self.host, user=self.user, password=self.password,database=self.database_name)
        self.cursor = self.conn.cursor()
        print("数据库 "+self.database_name+" 连接成功")

    def create_photo_table(self):
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                name VARCHAR(255) ,
                ID VARCHAR(255) PRIMARY KEY ,
                gender VARCHAR(255),
                photo VARCHAR(255),
                image LONGBLOB,
                num INT
            )
        """)
        self.conn.commit()

    def photo_insert(self,name,ID,gender,photo,image,num=0):
        self.cursor.execute("""
            INSERT INTO photo_list (name, ID, gender, photo,image,num) 
            VALUES (%s, %s, %s, %s,%s,%s)
        """, (name, ID, gender, photo,image,num))
        self.conn.commit()

    def photo_delete(self,delname):
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE ID = %s", (delname,))
        self.conn.commit()

    def read_photo_list(self):
        # 执行查询获取表的内容
        self.cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = self.cursor.fetchall()
        return rows

    def disconnect(self):
        self.cursor.close()
        self.conn.close()

    def num_inster(self,ID):
        self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE ID = {ID}")
        all=self.cursor.fetchone()
        num=all[5]+1
        self.cursor.execute(f"UPDATE {self.table_name} SET num = {num} WHERE ID = {ID}")
        self.conn.commit()

    def read_ID(self,ID):
        self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE ID = {ID}")
        rows=self.cursor.fetchall()
        return rows