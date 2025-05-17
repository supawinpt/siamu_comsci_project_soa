# Admin product routes for template rendering
from fastapi import APIRouter, Request, Depends, HTTPException, status, Form, File, UploadFile, Path
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import os
import shutil
import uuid
from auth import get_current_user
from database import get_connection
from schemas import product as product_schema
from schemas import product_image as image_schema
from models import product as product_model
from models import product_image as image_model

# Templates setup
templates = Jinja2Templates(directory="templates")

# Router for admin products
router = APIRouter(
    prefix="/admin/products",
    tags=["Admin Products"]
)

# Default pagination values
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 10

# Admin product list page
@router.get("", response_class=HTMLResponse)
async def admin_products_list(
    request: Request,
    page: int = DEFAULT_PAGE,
    per_page: int = DEFAULT_PER_PAGE,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    stock_status: Optional[str] = None,
    sort: Optional[str] = None,
    reverse: bool = False
):
    # Get connection
    conn = get_connection()
    
    # Build SQL query with filters
    sql_query = "SELECT p.*, COUNT(pi.image_id) AS image_count FROM products p "
    sql_query += "LEFT JOIN product_images pi ON p.product_id = pi.product_id "
    where_clauses = []
    params = []
    
    # Apply search filter
    if search:
        where_clauses.append("(p.name LIKE %s OR p.description LIKE %s)")
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    # Apply price filters
    if min_price is not None:
        where_clauses.append("p.price >= %s")
        params.append(min_price)
    if max_price is not None:
        where_clauses.append("p.price <= %s")
        params.append(max_price)
    
    # Apply stock status filter
    if stock_status:
        if stock_status == "in_stock":
            where_clauses.append("p.stock_quantity > 0")
        elif stock_status == "low_stock":
            where_clauses.append("p.stock_quantity > 0 AND p.stock_quantity < 10")
        elif stock_status == "out_of_stock":
            where_clauses.append("p.stock_quantity = 0")
    
    # Combine where clauses
    if where_clauses:
        sql_query += "WHERE " + " AND ".join(where_clauses) + " "
    
    # Group by product_id to handle the LEFT JOIN
    sql_query += "GROUP BY p.product_id "
    
    # Count total products for pagination
    count_query = f"SELECT COUNT(*) as count FROM ({sql_query}) AS filtered_products"
    
    # Apply sorting
    order_column = "p.created_at"  # Default sort
    order_dir = "DESC"
    
    if sort:
        if sort == "id":
            order_column = "p.product_id"
        elif sort == "name":
            order_column = "p.name"
        elif sort == "price":
            order_column = "p.price"
        elif sort == "stock":
            order_column = "p.stock_quantity"
        elif sort == "created_at":
            order_column = "p.created_at"
    
    if reverse:
        order_dir = "ASC" if order_dir == "DESC" else "DESC"
    
    sql_query += f"ORDER BY {order_column} {order_dir} "
    
    # Apply pagination
    offset = (page - 1) * per_page
    sql_query += "LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    
    try:
        with conn.cursor() as cursor:
            # Get total count for pagination
            cursor.execute(count_query, params[:-2] if params else [])
            total_count = cursor.fetchone()['count']
            
            # Get products
            cursor.execute(sql_query, params)
            products = cursor.fetchall()
            
            # Get primary images for each product
            for product in products:
                cursor.execute(
                    "SELECT * FROM product_images WHERE product_id = %s AND is_primary = 1", 
                    (product['product_id'],)
                )
                primary_image = cursor.fetchone()
                product['primary_image'] = primary_image
    finally:
        conn.close()
    
    # Calculate pagination values
    total_pages = (total_count + per_page - 1) // per_page
    
    # Render template with data
    return templates.TemplateResponse(
        "admin/products/list.html",
        {
            "request": request,
            "products": products,
            "total_products": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "offset": offset,
            "search": search,
            "min_price": min_price,
            "max_price": max_price,
            "stock_status": stock_status,
            "sort": sort,
            "reverse": reverse,
            "active_page": "products",
            "user": {"username": "admin", "role": "admin"}  # Temporary hardcoded user, should be from token
        }
    )

# Add product page
@router.get("/add", response_class=HTMLResponse)
async def add_product_page(request: Request):
    return templates.TemplateResponse(
        "admin/products/form.html",
        {
            "request": request,
            "active_page": "products",
            "user": {"username": "admin", "role": "admin"}  # Temporary hardcoded user, should be from token
        }
    )

# Edit product page
@router.get("/edit/{product_id}", response_class=HTMLResponse)
async def edit_product_page(request: Request, product_id: int = Path(..., gt=0)):
    # Get product data
    conn = get_connection()
    
    try:
        with conn.cursor() as cursor:
            # Get product details
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            
            if not product:
                return HTMLResponse(status_code=404, content="Product not found")
            
            # Get product images
            cursor.execute(
                "SELECT * FROM product_images WHERE product_id = %s ORDER BY sort_order", 
                (product_id,)
            )
            product_images = cursor.fetchall()
    finally:
        conn.close()
    
    return templates.TemplateResponse(
        "admin/products/form.html",
        {
            "request": request,
            "product": product,
            "product_images": product_images,
            "active_page": "products",
            "user": {"username": "admin", "role": "admin"}  # Temporary hardcoded user, should be from token
        }
    )

# Create product
@router.post("", response_class=HTMLResponse)
async def create_product(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    temp_images: Optional[List[str]] = Form(None)
):
    # Validate form inputs
    validation_errors = {}
    
    # Validate name
    if not name or len(name.strip()) < 2:
        validation_errors["name"] = "Product name must be at least 2 characters long"
    elif len(name) > 100:
        validation_errors["name"] = "Product name cannot exceed 100 characters"
    
    # Validate price
    if price <= 0:
        validation_errors["price"] = "Price must be greater than zero"
        
    # Validate stock quantity
    if stock_quantity < 0:
        validation_errors["stock_quantity"] = "Stock quantity cannot be negative"
    
    # If validation errors exist, return them
    if validation_errors:
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "validation_errors": validation_errors,
                "error": "Please fix the validation errors",
                "form_data": {
                    "name": name,
                    "description": description,
                    "price": price,
                    "stock_quantity": stock_quantity
                },
                "active_page": "products",
                "user": {"username": "admin", "role": "admin"}
            },
            status_code=422
        )
    
    try:
        # Create product data
        product_data = product_schema.ProductCreate(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity
        )
        
        # Create product in database
        new_product = product_model.create_product(product_data)
        product_id = new_product['product_id']
        product_images = []
        
        # Process any temporary images
        if temp_images:
            temp_dir = "uploads/products/temp"
            dest_dir = "uploads/products"
            
            # Ensure destination directory exists
            os.makedirs(dest_dir, exist_ok=True)
            
            # Get connection for database operations
            conn = get_connection()
            
            try:
                for idx, temp_image in enumerate(temp_images if isinstance(temp_images, list) else [temp_images]):
                    temp_path = os.path.join(temp_dir, temp_image)
                    
                    # Skip if file doesn't exist
                    if not os.path.exists(temp_path):
                        continue
                    
                    # Move file from temp to permanent location
                    dest_path = os.path.join(dest_dir, temp_image)
                    shutil.move(temp_path, dest_path)
                    
                    # Determine content type based on extension
                    file_ext = temp_image.split('.')[-1].lower()
                    content_type = {
                        'jpg': 'image/jpeg',
                        'jpeg': 'image/jpeg',
                        'png': 'image/png',
                        'gif': 'image/gif',
                        'webp': 'image/webp'
                    }.get(file_ext, 'application/octet-stream')
                    
                    # Create image data object
                    image_data = image_schema.ProductImageCreate(
                        product_id=product_id,
                        image_url=f"/uploads/products/{temp_image}",
                        image_type=image_schema.ImageType.gallery,
                        is_primary=(idx == 0),  # First image is primary
                        file_size=os.path.getsize(dest_path),
                        file_type=content_type
                    )
                    
                    # Save to database
                    image_model.create_product_image(image_data)
            except Exception as e:
                print(f"Error processing temporary images: {str(e)}")
            finally:
                # Get all images for the product
                try:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            "SELECT * FROM product_images WHERE product_id = %s ORDER BY sort_order", 
                            (product_id,)
                        )
                        product_images = cursor.fetchall()
                except Exception as e:
                    print(f"Error fetching product images: {str(e)}")
                finally:
                    conn.close()
        
        # Return success response
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "product": new_product,
                "product_images": product_images,
                "success": "Product created successfully!",
                "active_page": "products",
                "user": {"username": "admin", "role": "admin"}
            }
        )
    except ValueError as ve:
        # Handle validation errors from Pydantic
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "error": f"Validation error: {str(ve)}",
                "form_data": {
                    "name": name,
                    "description": description,
                    "price": price,
                    "stock_quantity": stock_quantity
                },
                "active_page": "products",
                "user": {"username": "admin", "role": "admin"}
            },
            status_code=422
        )
    except Exception as e:
        # Handle general errors
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "error": f"Error creating product: {str(e)}",
                "form_data": {
                    "name": name,
                    "description": description,
                    "price": price,
                    "stock_quantity": stock_quantity
                },
                "active_page": "products",
                "user": {"username": "admin", "role": "admin"}
            },
            status_code=500
        )

# Update product
@router.put("/{product_id}", response_class=HTMLResponse)
async def update_product(
    request: Request,
    product_id: int = Path(..., gt=0),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    stock_quantity: int = Form(...)
):
    # Validate form inputs
    validation_errors = {}
    
    # Validate name
    if not name or len(name.strip()) < 2:
        validation_errors["name"] = "Product name must be at least 2 characters long"
    elif len(name) > 100:
        validation_errors["name"] = "Product name cannot exceed 100 characters"
    
    # Validate price
    if price <= 0:
        validation_errors["price"] = "Price must be greater than zero"
        
    # Validate stock quantity
    if stock_quantity < 0:
        validation_errors["stock_quantity"] = "Stock quantity cannot be negative"
    
    # Check if product exists first
    product = product_model.get_product_by_id(product_id)
    if not product:
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "error": "Product not found",
                "active_page": "products",
                "user": {"username": "admin", "role": "admin"}
            },
            status_code=404
        )
    
    # Get product images
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_images WHERE product_id = %s ORDER BY sort_order", 
                (product_id,)
            )
            product_images = cursor.fetchall()
    finally:
        conn.close()
        
    # If validation errors exist, return them
    if validation_errors:
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "validation_errors": validation_errors,
                "error": "Please fix the validation errors",
                "product": product,
                "product_images": product_images,
                "form_data": {
                    "name": name,
                    "description": description,
                    "price": price,
                    "stock_quantity": stock_quantity
                },
                "active_page": "products",
                "user": {"username": "admin", "role": "admin"}
            },
            status_code=422
        )
    
    try:
        # Create product data
        product_data = product_schema.ProductUpdate(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity
        )
        
        # Update product in database
        updated_product = product_model.update_product(product_id, product_data)
        
        # Return success with updated product data
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "product": updated_product,
                "product_images": product_images,
                "success": "Product updated successfully!",
                "active_page": "products",
                "user": {"username": "admin", "role": "admin"}
            }
        )
    except ValueError as ve:
        # Handle validation errors from Pydantic
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "error": f"Validation error: {str(ve)}",
                "product": product,
                "product_images": product_images,
                "active_page": "products",
                "user": {"username": "admin", "role": "admin"}
            },
            status_code=422
        )
    except Exception as e:
        # Handle general errors
        return templates.TemplateResponse(
            "admin/products/form.html",
            {
                "request": request,
                "error": f"Error updating product: {str(e)}",
                "product": product,
                "product_images": product_images,
                "active_page": "products",
                "user": {"username": "admin", "role": "admin"}
            },
            status_code=500
        )

# Delete product
@router.delete("/{product_id}", response_class=HTMLResponse)
async def delete_product(
    request: Request,
    product_id: int = Path(..., gt=0)
):
    try:
        # Check if product exists
        product = product_model.get_product_by_id(product_id)
        if not product:
            return HTMLResponse(status_code=404, content="Product not found")
        
        # Delete product images from filesystem
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT image_url FROM product_images WHERE product_id = %s", 
                    (product_id,)
                )
                images = cursor.fetchall()
                
                for image in images:
                    image_path = os.path.join(".", image['image_url'].lstrip('/'))
                    if os.path.exists(image_path):
                        os.remove(image_path)
        finally:
            conn.close()
        
        # Delete product from database
        product_model.delete_product(product_id)
        
        # Return to the admin product list
        # HTMX will only update the container, not do a full page redirect
        return await admin_products_list(
            request=request,
            page=DEFAULT_PAGE,
            per_page=DEFAULT_PER_PAGE
        )
    except Exception as e:
        # Return error
        return HTMLResponse(
            status_code=500, 
            content=f"<div class='bg-red-50 border-l-4 border-red-500 text-red-700 p-4 mb-4'>Error deleting product: {str(e)}</div>"
        )

# Upload temporary product image (when creating new product)
@router.post("/upload-temp/images", response_class=HTMLResponse)
async def upload_temp_image(
    request: Request,
    file: UploadFile = File(...)
):
    # Validate image file
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        return HTMLResponse(
            status_code=400,
            content="<div class='col-span-full text-center text-red-500 py-4'>Invalid file type. Only JPEG, PNG, GIF, and WEBP are allowed.</div>"
        )
    
    # Create directory if it doesn't exist
    upload_dir = "uploads/products/temp"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1].lower()
    new_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(upload_dir, new_filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)
    
    # Return HTML for temporary image
    return HTMLResponse(
        content=f"""
        <div class="col-span-full flex justify-center my-4">
            <div class="relative rounded-lg overflow-hidden border border-green-200 bg-green-50">
                <img src="/uploads/products/temp/{new_filename}" alt="Temporary product image" class="w-full h-32 object-cover">
                <div class="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-10 transition-all">
                    <div class="absolute bottom-0 left-0 right-0 bg-white bg-opacity-90 p-2 text-center text-xs text-gray-600">
                        <p>Image uploaded successfully</p>
                        <p class="text-xs mt-1">Save the product to keep this image</p>
                    </div>
                </div>
                <input type="hidden" name="temp_images" value="{new_filename}">
            </div>
        </div>
        """
    )

# Upload product image
@router.post("/{product_id}/images", response_class=HTMLResponse)
async def upload_product_image(
    request: Request,
    product_id: int = Path(..., gt=0),
    file: UploadFile = File(...)
):
    # Validate image file
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        return HTMLResponse(
            status_code=400,
            content="<div class='col-span-full text-center text-red-500 py-4'>Invalid file type. Only JPEG, PNG, GIF, and WEBP are allowed.</div>"
        )
    
    # Check if product exists
    product = product_model.get_product_by_id(product_id)
    if not product:
        return HTMLResponse(
            status_code=404,
            content="<div class='col-span-full text-center text-red-500 py-4'>Product not found</div>"
        )
    
    # Create directory if it doesn't exist
    upload_dir = "uploads/products"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1].lower()
    new_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(upload_dir, new_filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)
        file_size = len(contents)
    
    # Create image record in database
    image_data = image_schema.ProductImageCreate(
        product_id=product_id,
        image_url=f"/uploads/products/{new_filename}",
        image_type=image_schema.ImageType.gallery,
        is_primary=False,  # Will be set to primary automatically if it's the first image
        file_size=file_size,
        file_type=file.content_type
    )
    
    # Get all product images first to check if it's the first one
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM product_images WHERE product_id = %s", (product_id,))
            image_count = cursor.fetchone()['count']
            
            # If it's the first image, set it as primary
            if image_count == 0:
                image_data.is_primary = True
    finally:
        conn.close()
    
    # Save image to database
    image_model.create_product_image(image_data)
    
    # Get all product images to return
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_images WHERE product_id = %s ORDER BY sort_order", 
                (product_id,)
            )
            product_images = cursor.fetchall()
    finally:
        conn.close()
    
    # Return updated images HTML
    return templates.TemplateResponse(
        "admin/products/_product_images.html",
        {
            "request": request,
            "product": product,
            "product_images": product_images
        }
    )

# Set image as primary
@router.put("/{product_id}/images/{image_id}/set-primary", response_class=HTMLResponse)
async def set_primary_image(
    request: Request,
    product_id: int = Path(..., gt=0),
    image_id: int = Path(..., gt=0)
):
    # Check if product exists
    product = product_model.get_product_by_id(product_id)
    if not product:
        return HTMLResponse(
            status_code=404,
            content="<div class='col-span-full text-center text-red-500 py-4'>Product not found</div>"
        )
    
    # Check if image exists
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_images WHERE image_id = %s AND product_id = %s", 
                (image_id, product_id)
            )
            image = cursor.fetchone()
            
            if not image:
                return HTMLResponse(
                    status_code=404,
                    content="<div class='col-span-full text-center text-red-500 py-4'>Image not found</div>"
                )
    finally:
        conn.close()
    
    # Set image as primary
    image_model.set_primary_image(image_id, product_id)
    
    # Get all product images to return
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_images WHERE product_id = %s ORDER BY sort_order", 
                (product_id,)
            )
            product_images = cursor.fetchall()
    finally:
        conn.close()
    
    # Return updated images HTML
    return templates.TemplateResponse(
        "admin/products/_product_images.html",
        {
            "request": request,
            "product": product,
            "product_images": product_images
        }
    )

# Delete product image
@router.delete("/{product_id}/images/{image_id}", response_class=HTMLResponse)
async def delete_product_image(
    request: Request,
    product_id: int = Path(..., gt=0),
    image_id: int = Path(..., gt=0)
):
    # Check if product exists
    product = product_model.get_product_by_id(product_id)
    if not product:
        return HTMLResponse(
            status_code=404,
            content="<div class='col-span-full text-center text-red-500 py-4'>Product not found</div>"
        )
    
    # Check if image exists and get its path
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_images WHERE image_id = %s AND product_id = %s", 
                (image_id, product_id)
            )
            image = cursor.fetchone()
            
            if not image:
                return HTMLResponse(
                    status_code=404,
                    content="<div class='col-span-full text-center text-red-500 py-4'>Image not found</div>"
                )
            
            # Delete image file
            image_path = os.path.join(".", image['image_url'].lstrip('/'))
            if os.path.exists(image_path):
                os.remove(image_path)
    finally:
        conn.close()
    
    # Delete image from database
    image_model.delete_product_image(image_id)
    
    # Get all product images to return
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_images WHERE product_id = %s ORDER BY sort_order", 
                (product_id,)
            )
            product_images = cursor.fetchall()
    finally:
        conn.close()
    
    # Return updated images HTML
    return templates.TemplateResponse(
        "admin/products/_product_images.html",
        {
            "request": request,
            "product": product,
            "product_images": product_images
        }
    )

# Show reorder images UI
@router.get("/{product_id}/images/reorder-ui", response_class=HTMLResponse)
async def reorder_images_ui(
    request: Request,
    product_id: int = Path(..., gt=0)
):
    # Check if product exists
    product = product_model.get_product_by_id(product_id)
    if not product:
        return HTMLResponse(
            status_code=404,
            content="<div class='text-center text-red-500 py-4'>Product not found</div>"
        )
    
    # Get all product images
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM product_images WHERE product_id = %s ORDER BY sort_order", 
                (product_id,)
            )
            product_images = cursor.fetchall()
    finally:
        conn.close()
    
    # Return reorder modal HTML
    return templates.TemplateResponse(
        "admin/products/image-reorder-modal.html",
        {
            "request": request,
            "product": product,
            "product_images": product_images
        }
    )

# Reorder images
@router.put("/{product_id}/images/reorder", response_class=HTMLResponse)
async def reorder_images(
    request: Request,
    product_id: int = Path(..., gt=0),
    image_ids: List[int] = Form(...)
):
    # Check if product exists
    product = product_model.get_product_by_id(product_id)
    if not product:
        return HTMLResponse(
            status_code=404,
            content="<div class='col-span-full text-center text-red-500 py-4'>Product not found</div>"
        )
    
    # Reorder images
    updated_images = image_model.reorder_images(product_id, image_ids)
    
    if not updated_images:
        return HTMLResponse(
            status_code=400,
            content="<div class='col-span-full text-center text-red-500 py-4'>Failed to reorder images</div>"
        )
    
    # Return updated images HTML
    return templates.TemplateResponse(
        "admin/products/_product_images.html",
        {
            "request": request,
            "product": product,
            "product_images": updated_images
        }
    )