# routers/user.py

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import create_access_token, verify_password
from typing import List
from schemas import user as user_schema
from models import user as user_model

# 📦 สร้าง Router สำหรับ User
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """ ตรวจสอบ Username/Password และคืนค่า JWT Token """
    user = next((u for u in user_model.get_users() if u["username"] == form_data.username), None)

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # สร้าง JWT Token
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})

    return {"access_token": access_token, "token_type": "bearer"}


# 🎨 Endpoint สำหรับ Insert User
@router.post("/", response_model=user_schema.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: user_schema.UserCreate):
    # 🔍 ตรวจสอบ Email ซ้ำ
    existing_users = user_model.get_users()
    for u in existing_users:
        if u['email'] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    # 💾 Insert ข้อมูลและ Return User ที่เพิ่งสร้าง
    new_user = user_model.create_user(user)
    return new_user  # 🔥 Return User ที่มีครบทุก Field


# 🎨 Endpoint สำหรับ Get Users ทั้งหมด
@router.get("/", response_model=List[user_schema.UserResponse])
def read_users():
    users = user_model.get_users()
    return users


# 🎨 Endpoint สำหรับ Get User โดยใช้ user_id
@router.get("/{user_id}", response_model=user_schema.UserResponse)
def read_user(user_id: int):
    user = user_model.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ✨ Endpoint สำหรับ Update User โดยใช้ user_id
@router.put("/{user_id}", response_model=user_schema.UserResponse)
def update_user(user_id: int, user_update: user_schema.UserUpdate):
    # 🔍 ตรวจสอบว่ามี User อยู่หรือไม่
    existing_user = user_model.get_user_by_id(user_id)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # 💾 Update ข้อมูล
    updated_user = user_model.update_user(user_id, user_update)
    return updated_user  # 🔥 Return User ที่อัปเดตแล้ว


# 🔥 Endpoint สำหรับ Delete User โดยใช้ user_id
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    # 🔍 ตรวจสอบว่ามี User อยู่หรือไม่
    existing_user = user_model.get_user_by_id(user_id)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # ❌ ลบ User
    user_model.delete_user(user_id)
    return None  # 🔥 ไม่มี Response Body