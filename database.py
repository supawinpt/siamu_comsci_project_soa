import pymysql.cursors
import os

# 🔗 การเชื่อมต่อกับ MySQL
def get_connection():
    connection = pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', '1111'),
        database=os.environ.get('DB_NAME', 'nor_db'),
        cursorclass=pymysql.cursors.DictCursor
        #host='localhost',
        #user='root',
        #password='1111',
        #database='nor_db',
    )
    return connection
