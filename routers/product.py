from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional
from auth import get_current_user
from schemas import product as product_schema
from models import product as product_model

# 📦 สร้าง Router สำหรับ Product
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# 🔥 Endpoint สำหรับสร้าง Product ใหม่
@router.post("/", response_model=product_schema.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: product_schema.ProductCreate, current_user: dict = Depends(get_current_user)):
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่สร้าง product ได้)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can create products."
        )
        
    # สร้าง product
    new_product = product_model.create_product(product)
    return new_product


# 🔥 Endpoint สำหรับดึงข้อมูล Products ทั้งหมด
@router.get("/", response_model=List[product_schema.ProductResponse])
def read_products():
    products = product_model.get_products()
    return products


# 🔥 Endpoint สำหรับดึงข้อมูล Product ตาม ID
@router.get("/{product_id}", response_model=product_schema.ProductResponse)
def read_product(product_id: int):
    product = product_model.get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


# 🔥 Endpoint สำหรับอัปเดต Product
@router.put("/{product_id}", response_model=product_schema.ProductResponse)
def update_product(
    product_id: int, 
    product_update: product_schema.ProductUpdate, 
    current_user: dict = Depends(get_current_user)
):
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่อัปเดต product ได้)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can update products."
        )
        
    # ตรวจสอบว่ามี Product นี้หรือไม่
    existing_product = product_model.get_product_by_id(product_id)
    if existing_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        
    # อัปเดต Product
    updated_product = product_model.update_product(product_id, product_update)
    return updated_product


# 🔥 Endpoint สำหรับลบ Product
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, current_user: dict = Depends(get_current_user)):
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่ลบ product ได้)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can delete products."
        )
        
    # ตรวจสอบว่ามี Product นี้หรือไม่
    existing_product = product_model.get_product_by_id(product_id)
    if existing_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        
    # ลบ Product
    product_model.delete_product(product_id)
    return None