# main.py
from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from routers import user as user_router
from routers import product as product_router
from routers import product_image as product_image_router
from routers import order as order_router
from routers import admin_product as admin_product_router
from fastapi.middleware.cors import CORSMiddleware
from auth import authenticate_user, create_access_token, decode_access_token
from database import get_connection
import os
from typing import Optional

# 🚀 สร้าง FastAPI App
app = FastAPI(
    title="E-commerce API",
    description="API สำหรับร้านค้าออนไลน์ มีระบบจัดการ User, Product, Order",
    version="1.0.0"
)

# สร้างโฟลเดอร์สำหรับเก็บรูปภาพ
os.makedirs("uploads/products", exist_ok=True)

# 🔗 รวม Router เข้ากับ FastAPI App
app.include_router(user_router.router)
app.include_router(product_router.router)
app.include_router(product_image_router.router)
app.include_router(order_router.router)
app.include_router(admin_product_router.router)

# 🖼️ Mount เส้นทางสำหรับไฟล์สตาติก (รูปภาพสินค้า)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# สร้างโฟลเดอร์สำหรับเก็บรูปภาพชั่วคราว
os.makedirs("uploads/products/temp", exist_ok=True)

# 🎨 ตั้งค่า Jinja2 Templates
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8181"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Admin Login Page
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    token = request.cookies.get("access_token")
    if token and token.startswith("Bearer "):
        try:
            token_data = decode_access_token(token.replace("Bearer ", ""))
            if token_data:
                conn = get_connection()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE username = %s", (token_data.get("sub"),))
                    user = cursor.fetchone()
                conn.close()

                if user:
                    return RedirectResponse(url="/admin/dashboard", status_code=302)
        except Exception:
            pass

    return templates.TemplateResponse("admin/login.html", {"request": request})

# 🔐 Admin Login Post
@app.post("/admin/login", response_class=HTMLResponse)
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(username, password)
    if not user or user["role"] != "admin":
        return templates.TemplateResponse(
            "admin/login.html",
            {"request": request, "error": "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง หรือคุณไม่มีสิทธิ์ Admin"}
        )

    token = create_access_token(data={"sub": user["username"]})

    # 👉 สร้าง response redirect สำหรับ cookie
    response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)

    # 👉 ถ้ามาจาก HTMX ให้ตอบกลับด้วย HTML + JavaScript redirect
    if request.headers.get("HX-Request") == "true":
        html_redirect = """
        <script>
            window.location.href = "/admin/dashboard";
        </script>
        """
        redirect_html = HTMLResponse(content=html_redirect)
        redirect_html.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
        return redirect_html

    return response

# 🏠 Admin Dashboard
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

    try:
        token_data = decode_access_token(token.replace("Bearer ", ""))
        if not token_data:
            return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (token_data.get("sub"),))
            user = cursor.fetchone()

            if not user or user["role"] != "admin":
                conn.close()
                return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

            cursor.execute("SELECT COUNT(*) as count FROM products")
            product_count = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM orders")
            order_count = cursor.fetchone()['count']

        conn.close()

        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "user": user,
                "product_count": product_count,
                "user_count": user_count,
                "order_count": order_count,
                "active_page": "dashboard"
            }
        )

    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)

# 🔄 Logout
@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

# 🔄 Recent Activity Endpoint
@app.get("/admin/recent-activity", response_class=HTMLResponse)
async def get_recent_activity(request: Request):
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        return "<p class='text-center text-red-500'>Authentication required to load recent activity</p>"

    try:
        token_data = decode_access_token(token.replace("Bearer ", ""))
        if not token_data:
            return "<p class='text-center text-red-500'>Authentication expired. Please refresh page.</p>"

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT role FROM users WHERE username = %s", (token_data.get("sub"),))
            user = cursor.fetchone()

            if not user or user["role"] != "admin":
                conn.close()
                return "<p class='text-center text-red-500'>You don't have permission to view this content</p>"

            cursor.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 5")
            recent_orders = cursor.fetchall()

        conn.close()

        return templates.TemplateResponse(
            "components/_recent_activity.html",
            {"request": request, "recent_orders": recent_orders}
        )

    except Exception as e:
        return f"<p class='text-center text-red-500'>Error loading activity data: {str(e)}</p>"
