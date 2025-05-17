from database import get_connection
from passlib.context import CryptContext

# ใช้ bcrypt ในการ Hash Password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """ 🔒 แปลงรหัสผ่านเป็น Hash ก่อนบันทึก """
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """ 🔍 ตรวจสอบรหัสผ่านที่ผู้ใช้กรอกกับ Hash ในฐานข้อมูล """
    return pwd_context.verify(plain_password, hashed_password)

# 🚀 CREATE: Insert User และ Return User ที่เพิ่ง Insert
def create_user(user):
    conn = get_connection()
    with conn.cursor() as cursor:
        # 💾 Insert User (Hash Password ก่อน)
        sql = """
            INSERT INTO users (first_name, last_name, email, phone, address, username, password, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            user.first_name,
            user.last_name,
            user.email,
            user.phone,
            user.address,
            user.username,
            hash_password(user.password),  # 🔒 Hash Password ก่อนเก็บลงฐานข้อมูล
            user.role
        ))
        conn.commit()
        
        # 🔍 ดึงข้อมูล User ที่เพิ่ง Insert มาเพื่อตอบกลับ
        user_id = cursor.lastrowid  # ได้ `user_id` ที่เพิ่ง Insert
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        new_user = cursor.fetchone()
        
        # 🎨 สร้าง full_name ก่อน Return
        new_user['full_name'] = f"{new_user['first_name']} {new_user['last_name']}"

    conn.close()
    return new_user  # 🔥 Return ครบทุก Field

# 🚀 READ: Select Users ทั้งหมด
def get_users():
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM users"
        cursor.execute(sql)
        users = cursor.fetchall()
        
        # 🔥 คำนวณ full_name ในระดับ Model
        for user in users:
            user['full_name'] = f"{user['first_name']} {user['last_name']}"

    conn.close()
    return users

# 🚀 READ: Select User โดยใช้ user_id
def get_user_by_id(user_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM users WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        user = cursor.fetchone()
        
        # 🔥 คำนวณ full_name ในระดับ Model
        if user:
            user['full_name'] = f"{user['first_name']} {user['last_name']}"

    conn.close()
    return user

# 🚀 READ: Select User โดยใช้ Username (ใช้สำหรับ Login)
def get_user_by_username(username: str):
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        
        if user:
            user['full_name'] = f"{user['first_name']} {user['last_name']}"

    conn.close()
    return user

# 🚀 UPDATE: แก้ไขข้อมูล User โดยใช้ user_id
def update_user(user_id: int, user):
    conn = get_connection()
    with conn.cursor() as cursor:
        # 🔄 Update User
        sql = """
            UPDATE users 
            SET first_name = %s, last_name = %s, email = %s, phone = %s, address = %s, username = %s, password = %s, role = %s
            WHERE user_id = %s
        """
        cursor.execute(sql, (
            user.first_name,
            user.last_name,
            user.email,
            user.phone,
            user.address,
            user.username,
            hash_password(user.password),  # 🔒 Hash Password ใหม่ (ถ้ามีการอัปเดต)
            user.role,
            user_id
        ))
        conn.commit()
        
        # 🔍 ดึงข้อมูล User ที่ถูก Update มาเพื่อตอบกลับ
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        updated_user = cursor.fetchone()
        
        # 🎨 สร้าง full_name ก่อน Return
        if updated_user:
            updated_user['full_name'] = f"{updated_user['first_name']} {updated_user['last_name']}"

    conn.close()
    return updated_user

# 🚀 DELETE: ลบข้อมูล User โดยใช้ user_id
def delete_user(user_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        # ❌ ลบ User
        sql = "DELETE FROM users WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        conn.commit()

        # 🔄 ตรวจสอบว่ามีการลบหรือไม่
        affected_rows = cursor.rowcount

    conn.close()
    return affected_rows > 0  # ✅ Return True ถ้าลบสำเร็จ
