import jwt
import bcrypt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database import get_connection

# 🔒 ค่าความปลอดภัยของ JWT
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 🔐 การใช้ PassLib ช่วยจัดการ bcrypt ได้มีประสิทธิภาพมากกว่า
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str):
    """ 🔒 แปลงรหัสผ่านเป็น Hash ก่อนบันทึก """
    # ใช้ pwd_context แทนการเรียก bcrypt โดยตรง
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """ 🔍 ตรวจสอบรหัสผ่านที่ผู้ใช้กรอกกับ Hash ในฐานข้อมูล 
    PassLib จะจัดการเรื่อง encoding ให้เอง ไม่ต้องแปลงเป็น bytes ด้วยตัวเอง
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """ 🔥 สร้าง JWT Token """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """ 🧐 ตรวจสอบ JWT Token """
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """ ✅ ดึงข้อมูล User จาก JWT Token """
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

def authenticate_user(username: str, password: str):
    """ 🔐 ตรวจสอบชื่อผู้ใช้และรหัสผ่านกับฐานข้อมูลจริง """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()
            
            # ต้องตรวจสอบว่าพบผู้ใช้ก่อน เพื่อป้องกัน None error
            if not user:
                print("❌ ไม่พบผู้ใช้นี้ในระบบ")
                return None
                
            # 👇 พ่น Log ตรวจสอบว่าเจอ user หรือไม่
            print("🟡 ตรวจพบข้อมูลผู้ใช้จาก DB:", user)
            print("🔑 plain_password ที่กรอก:", password)
            print("🔐 hashed_password จาก DB:", user["password"])
            
            # ตรวจสอบรหัสผ่านด้วย PassLib (จัดการเรื่อง encoding อัตโนมัติ)
            if verify_password(password, user["password"]):
                print("✅ รหัสผ่านถูกต้อง")
                return user
            else:
                print("❌ รหัสผ่านไม่ถูกต้อง")
    finally:
        conn.close()
    
    return None  # ❌ ไม่พบหรือรหัสผ่านไม่ถูกต้อง
