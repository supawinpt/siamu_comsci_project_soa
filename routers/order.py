from fastapi import APIRouter, HTTPException, status, Depends, Path
from typing import List
from auth import get_current_user
from schemas import order as order_schema
from models import order as order_model
from models import user as user_model

# 📦 สร้าง Router สำหรับ Orders
router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# 🛒 Endpoint สำหรับสร้าง Order ใหม่
@router.post("/", response_model=order_schema.OrderDetailResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: order_schema.OrderCreate, current_user: dict = Depends(get_current_user)):
    # ตรวจสอบว่า user_id ใน order ตรงกับ user ที่ login หรือไม่ หรือเป็น admin
    username = current_user.get("sub")
    user = user_model.get_user_by_username(username)
    if current_user.get("role") != "admin" and order.user_id != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create orders for yourself"
        )
    
    # ตรวจสอบว่ามี User นี้หรือไม่
    user = user_model.get_user_by_id(order.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # สร้าง order
        new_order = order_model.create_order(order)
        return new_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# 🛒 Endpoint สำหรับดึงข้อมูล Orders ทั้งหมด
@router.get("/", response_model=List[order_schema.OrderResponse])
def read_orders(current_user: dict = Depends(get_current_user)):
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่ดูได้ทุก order)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can view all orders."
        )
    
    orders = order_model.get_orders()
    return orders


# 🛒 Endpoint สำหรับดึงข้อมูล Order ตาม ID
@router.get("/{order_id}", response_model=order_schema.OrderDetailResponse)
def read_order(order_id: int = Path(..., gt=0), current_user: dict = Depends(get_current_user)):
    # ดึงข้อมูล order
    order = order_model.get_order_with_items(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # ตรวจสอบสิทธิ์ (เฉพาะ admin หรือเจ้าของ order เท่านั้นที่ดูได้)
    username = current_user.get("sub")
    user = user_model.get_user_by_username(username)
    if current_user.get("role") != "admin" and order['user_id'] != user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders"
        )
    
    return order


# 🛒 Endpoint สำหรับอัปเดตสถานะ Order
@router.put("/{order_id}", response_model=order_schema.OrderDetailResponse)
def update_order(
    order_id: int = Path(..., gt=0),
    order_update: order_schema.OrderUpdate = None,
    current_user: dict = Depends(get_current_user)
):
    # ดึงข้อมูล order
    order = order_model.get_order_with_items(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่อัปเดตสถานะได้)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can update order status."
        )
    
    # อัปเดตสถานะ
    updated_order = order_model.update_order_status(order_id, order_update.status)
    return updated_order


# 🛒 Endpoint สำหรับดึงประวัติการสั่งซื้อของ User
@router.get("/users/{user_id}/orders", response_model=List[order_schema.OrderResponse], tags=["Users"])
def read_user_orders(user_id: int = Path(..., gt=0), current_user: dict = Depends(get_current_user)):
    # ตรวจสอบว่ามี User นี้หรือไม่
    user = user_model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # ตรวจสอบสิทธิ์ (เฉพาะ admin หรือเจ้าของข้อมูลเท่านั้นที่ดูได้)
    username = current_user.get("sub")
    current_user_obj = user_model.get_user_by_username(username)
    if current_user.get("role") != "admin" and user_id != current_user_obj["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own order history"
        )
    
    # ดึงประวัติการสั่งซื้อ
    orders = order_model.get_user_orders(user_id)
    return orders