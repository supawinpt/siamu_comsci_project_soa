from pydantic import BaseModel, Field, model_validator, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# 🚀 Schema สำหรับ Create (POST)
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None)
    price: Decimal = Field(..., gt=0)  # ราคาต้องมากกว่า 0
    stock_quantity: int = Field(..., ge=0)  # จำนวนสินค้าต้องไม่ติดลบ

    @validator('price')
    def validate_price(cls, v):
        return round(v, 2)  # ปัดเศษทศนิยม 2 ตำแหน่ง


# 🚀 Schema สำหรับ Update (PUT)
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)

    @validator('price')
    def validate_price(cls, v):
        if v is not None:
            return round(v, 2)
        return v

    class Config:
        from_attributes = True


# 🚀 Schema สำหรับการแสดงผล Product (Response)
class ProductResponse(BaseModel):
    product_id: int
    name: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True