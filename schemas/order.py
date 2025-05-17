from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

# 📦 Order Status Enum
class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

# 📦 Schema สำหรับ Order Item ในการสร้าง Order
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)  # จำนวนต้องมากกว่า 0


# 📦 Schema สำหรับ Create Order (POST)
class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate] = Field(..., min_items=1)  # ต้องมีอย่างน้อย 1 รายการ


# 📦 Schema สำหรับ Update Order (PUT)
class OrderUpdate(BaseModel):
    status: OrderStatus

    class Config:
        from_attributes = True


# 📦 Schema สำหรับ Order Item Response
class OrderItemResponse(BaseModel):
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_time: Decimal
    subtotal: Decimal
    product_name: Optional[str] = None  # ชื่อสินค้า (จะมาจากการ Join)

    class Config:
        from_attributes = True


# 📦 Schema สำหรับ Order Response
class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime]
    items: Optional[List[OrderItemResponse]] = None

    class Config:
        from_attributes = True


# 📦 Schema สำหรับ Order Detail Response (รวม items)
class OrderDetailResponse(OrderResponse):
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True