from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# 🖼️ Image Type Enum
class ImageType(str, Enum):
    main = "main"
    thumbnail = "thumbnail"
    gallery = "gallery"

# 🚀 Schema สำหรับ Create (POST)
class ProductImageCreate(BaseModel):
    product_id: int
    image_url: str = Field(..., max_length=255)
    image_type: ImageType = Field(default=ImageType.gallery)
    sort_order: int = Field(default=0)
    is_primary: bool = Field(default=False)
    file_size: int = Field(..., gt=0)  # ขนาดไฟล์ต้องมากกว่า 0
    file_type: str = Field(..., max_length=50)
    
    @validator('file_type')
    def validate_file_type(cls, v):
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if v.lower() not in allowed_types:
            raise ValueError(f"File type must be one of: {', '.join(allowed_types)}")
        return v.lower()


# 🚀 Schema สำหรับ Update (PUT)
class ProductImageUpdate(BaseModel):
    image_type: Optional[ImageType] = None
    sort_order: Optional[int] = None
    is_primary: Optional[bool] = None
    
    class Config:
        from_attributes = True


# 🚀 Schema สำหรับการแสดงผล Product Image (Response)
class ProductImageResponse(BaseModel):
    image_id: int
    product_id: int
    image_url: str
    image_type: ImageType
    sort_order: int
    is_primary: bool
    file_size: int
    file_type: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# 🚀 Schema สำหรับการจัดลำดับรูปภาพ
class ImageReorder(BaseModel):
    image_ids: List[int] = Field(..., description="List of image IDs in the desired order")