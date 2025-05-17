from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form, Path
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
import uuid
from auth import get_current_user
from schemas import product_image as image_schema
from models import product_image as image_model
from models import product as product_model

# 📦 สร้าง Router สำหรับ Product Images
router = APIRouter(
    prefix="/products",
    tags=["Product Images"]
)

# กำหนดการตั้งค่าเกี่ยวกับ Images
UPLOAD_DIR = "uploads/products"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


# สร้างโฟลเดอร์เก็บรูปหากยังไม่มี
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ฟังก์ชันตรวจสอบไฟล์
def validate_image(file: UploadFile):
    # ตรวจสอบนามสกุลไฟล์
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension must be one of {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # ถ้าไฟล์ใหญ่เกินไป FastAPI จะ raise HTTPException เอง
    # แต่เราสามารถตรวจสอบเพิ่มเติมได้ที่นี่
    file_size = 0
    chunk_size = 1024  # 1KB
    while chunk := file.file.read(chunk_size):
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            file.file.seek(0)  # reset file pointer
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the limit of {MAX_FILE_SIZE / (1024 * 1024)}MB"
            )
    
    file.file.seek(0)  # reset file pointer
    return file_size


# 🔥 Endpoint สำหรับอัปโหลดรูปภาพสินค้า
@router.post("/{product_id}/images", response_model=image_schema.ProductImageResponse)
async def upload_product_image(
    product_id: int = Path(..., gt=0),
    file: UploadFile = File(...),
    image_type: image_schema.ImageType = Form(image_schema.ImageType.gallery),
    is_primary: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่อัปโหลดรูปได้)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can upload product images."
        )
    
    # ตรวจสอบว่ามี Product นี้หรือไม่
    product = product_model.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # ตรวจสอบความถูกต้องของไฟล์
    file_size = validate_image(file)
    
    # สร้างชื่อไฟล์ใหม่ด้วย UUID เพื่อป้องกันการซ้ำ
    filename = file.filename
    ext = filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename)
    
    # บันทึกไฟล์
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # สร้างข้อมูลสำหรับบันทึกลงฐานข้อมูล
    image_data = image_schema.ProductImageCreate(
        product_id=product_id,
        image_url=f"/uploads/products/{new_filename}",
        image_type=image_type,
        is_primary=is_primary,
        file_size=file_size,
        file_type=f"image/{ext}"
    )
    
    # บันทึกลงฐานข้อมูล
    new_image = image_model.create_product_image(image_data)
    return new_image


# 🔥 Endpoint สำหรับดึงรูปภาพทั้งหมดของสินค้า
@router.get("/{product_id}/images", response_model=List[image_schema.ProductImageResponse])
def get_product_images(product_id: int = Path(..., gt=0)):
    # ตรวจสอบว่ามี Product นี้หรือไม่
    product = product_model.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # ดึงรูปภาพทั้งหมด
    images = image_model.get_product_images(product_id)
    return images


# 🔥 Endpoint สำหรับดึงรูปภาพเดียวของสินค้า
@router.get("/{product_id}/images/{image_id}", response_model=image_schema.ProductImageResponse)
def get_product_image(product_id: int = Path(..., gt=0), image_id: int = Path(..., gt=0)):
    # ตรวจสอบว่ามี Product นี้หรือไม่
    product = product_model.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # ดึงรูปภาพ
    image = image_model.get_product_image_by_id(image_id)
    if not image or image['product_id'] != product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found for this product"
        )
    
    return image


# 🔥 Endpoint สำหรับอัปเดตข้อมูลรูปภาพ
@router.put("/{product_id}/images/{image_id}", response_model=image_schema.ProductImageResponse)
def update_product_image(
    product_id: int = Path(..., gt=0),
    image_id: int = Path(..., gt=0),
    image_update: image_schema.ProductImageUpdate = None,
    current_user: dict = Depends(get_current_user)
):
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่อัปเดตรูปได้)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can update product images."
        )
    
    # ตรวจสอบว่ามี Product นี้หรือไม่
    product = product_model.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # ตรวจสอบว่ามีรูปภาพนี้หรือไม่
    image = image_model.get_product_image_by_id(image_id)
    if not image or image['product_id'] != product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found for this product"
        )
    
    # อัปเดตรูปภาพ
    updated_image = image_model.update_product_image(image_id, image_update)
    return updated_image


# 🔥 Endpoint สำหรับตั้งเป็นรูปหลัก
@router.put("/{product_id}/images/{image_id}/set-primary", response_model=image_schema.ProductImageResponse)
def set_primary_image(
    product_id: int = Path(..., gt=0),
    image_id: int = Path(..., gt=0),
    current_user: dict = Depends(get_current_user)
):
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่ตั้งรูปหลักได้)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can set primary image."
        )
    
    # ตรวจสอบว่ามี Product นี้หรือไม่
    product = product_model.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # ตรวจสอบว่ามีรูปภาพนี้หรือไม่
    image = image_model.get_product_image_by_id(image_id)
    if not image or image['product_id'] != product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found for this product"
        )
    
    # ตั้งเป็นรูปหลัก
    updated_image = image_model.set_primary_image(image_id, product_id)
    return updated_image


# 🔥 Endpoint สำหรับจัดลำดับรูปภาพใหม่
@router.put("/{product_id}/images/reorder")
def reorder_images(
    product_id: int = Path(..., gt=0),
    image_order: image_schema.ImageReorder = None,
    current_user: dict = Depends(get_current_user)
):
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่จัดลำดับรูปได้)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can reorder images."
        )
    
    # ตรวจสอบว่ามี Product นี้หรือไม่
    product = product_model.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # จัดลำดับใหม่
    images = image_model.reorder_images(product_id, image_order.image_ids)
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image IDs or these images do not belong to this product"
        )
    
    return {"message": "Images reordered successfully", "images": images}


# 🔥 Endpoint สำหรับลบรูปภาพ
@router.delete("/{product_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_image(
    product_id: int = Path(..., gt=0),
    image_id: int = Path(..., gt=0),
    current_user: dict = Depends(get_current_user)
):
    # ตรวจสอบสิทธิ์ (เฉพาะ admin เท่านั้นที่ลบรูปได้)
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Only admin can delete product images."
        )
    
    # ตรวจสอบว่ามี Product นี้หรือไม่
    product = product_model.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # ตรวจสอบว่ามีรูปภาพนี้หรือไม่
    image = image_model.get_product_image_by_id(image_id)
    if not image or image['product_id'] != product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found for this product"
        )
    
    # ลบไฟล์จากดิสก์ (ถ้ามี)
    image_path = os.path.join(".", image['image_url'].lstrip('/'))
    if os.path.exists(image_path):
        os.remove(image_path)
    
    # ลบข้อมูลจากฐานข้อมูล
    image_model.delete_product_image(image_id)
    
    return None