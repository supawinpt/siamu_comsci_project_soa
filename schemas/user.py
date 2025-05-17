from pydantic import BaseModel, Field, model_validator, EmailStr
from typing import Optional
from datetime import datetime

# 🚀 Schema สำหรับ Create (POST)
class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern="^0[0-9]{9}$")  # เบอร์โทรไทย 10 หลัก
    address: Optional[str]
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    # ✨ Custom Validation: เช็คว่าชื่อห้ามเป็น "admin"
    @model_validator(mode='before')
    def validate_username(cls, values):
        # 🔥 เช็คว่า username ห้ามเป็น "admin"
        if values.get('username', '').lower() == 'admin':
            raise ValueError('Username cannot be "admin"')
        return values


# 🚀 Schema สำหรับ Update (PUT)
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr]
    phone: Optional[str] = Field(None, pattern="^0[0-9]{9}$")  # เบอร์โทรไทย 10 หลัก
    address: Optional[str]
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = Field(None)  # ✅ เพิ่ม role

    class Config:
        from_attributes = True


# 🚀 Schema สำหรับการแสดงผล User (Response)
class UserResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    full_name: Optional[str]  # ต้องเป็น Optional เพื่อให้กำหนดค่าใหม่ได้
    email: EmailStr
    phone: Optional[str] = Field(None, pattern="^0[0-9]{9}$")  # เบอร์โทรไทย 10 หลัก
    address: Optional[str]
    username: str
    created_at: datetime

    # 🔥 ใช้ model_validator แทน field_validator
    @model_validator(mode='before')
    def generate_full_name(cls, values):
        # 🔥 แก้ไขให้เข้าถึงค่าได้ถูกต้อง
        first_name = values.get('first_name', '')
        last_name = values.get('last_name', '')
        values['full_name'] = f"{first_name} {last_name}"
        return values

    class Config:
        from_attributes = True  # 🔥 แก้ไขจาก orm_mode เป็น from_attributes (Pydantic V2)


