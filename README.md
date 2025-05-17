# 🚀 คู่มือการติดตั้งโปรเจกต์ E-commerce API

## 🔧 Project Setup
#
1️⃣ Clone the Repository

# Clone this repository
$ git clone <repository_url>
git clone https://github.com/noraphat/project-ecom-soa.git


$ cd <repository_folder>
cd project-mini-ecommerce\Backend-FastAPI


## 📂 โครงสร้างโปรเจกต์
```
project-ecom-soa/
│── .github/                         # 🗂️ โฟลเดอร์หลักสำหรับ GitHub Configuration
│   ├── workflows                    # 🔄 กำหนด Workflow สำหรับ GitHub Actions
│   │   ├── main.yml                 # 🤖 ไฟล์ CI Workflow หลัก (เช่น รันเทส, build Docker)
│── main.py                          # 🔥 FastAPI Entry Point
│── database.py                      # 🔗 เชื่อมต่อ MySQL
│── auth.py                          # 🔒 จัดการ JWT Authentication
│── schema.sql                       # 💾 คำสั่ง SQL สำหรับสร้างฐานข้อมูล
│── models/                          # 📂 จัดการ Model ของ Database
│   ├── user.py                      # 👤 จัดการข้อมูล User
│   ├── product.py                   # 🛍️ จัดการข้อมูล Product
│   ├── product_image.py             # 🖼️ จัดการข้อมูลรูปภาพสินค้า
│   ├── order.py                     # 📦 จัดการข้อมูล Order
│── routers/                         # 📂 API Endpoint
│   ├── user.py                      # 👤 API สำหรับ User Management
│   ├── product.py                   # 🛍️ API สำหรับ Product Management
│   ├── product_image.py             # 🖼️ API สำหรับจัดการรูปภาพสินค้า
│   ├── order.py                     # 📦 API สำหรับจัดการ Order
│── schemas/                         # 📂 Pydantic Schemas
│   ├── user.py                      # 🏗️ Schema สำหรับ User
│   ├── product.py                   # 🏗️ Schema สำหรับ Product
│   ├── product_image.py             # 🏗️ Schema สำหรับรูปภาพสินค้า
│   ├── order.py                     # 🏗️ Schema สำหรับ Order
│── uploads/                         # 📂 โฟลเดอร์เก็บรูปภาพสินค้า
│   ├── products/                    # 🖼️ รูปภาพสินค้า
│── templates/                       # 📂 เทมเพลตสำหรับส่วน Frontend
│   ├── base.html                    # 🏗️ เทมเพลตหลัก
│   ├── components/                  # 📂 คอมโพเนนต์ย่อยสำหรับเทมเพลต
│   │   ├── header.html              # 🔝 ส่วน Header
│   │   ├── navbar.html              # 🧭 เมนูนำทาง
│   │   ├── footer.html              # 👣 ส่วน Footer
│   │   └── _recent_activity.html    # 🔄 ส่วนแสดงกิจกรรมล่าสุด
│   └── admin/                       # 📂 เทมเพลตสำหรับส่วน Admin
│       ├── login.html               # 🔐 หน้า Login
│       └── dashboard.html           # 📊 หน้า Dashboard
│── .gitignore                       # 🚫 ไฟล์ที่ไม่ต้องการให้ Git ติดตาม
│── requirements.txt                 # 📜 รายการ Python Packages
│── README.md                        # 📖 คำอธิบายโปรเจค
│── schema.sql                       # 🧱 คำสั่ง SQL สำหรับสร้างตารางและโครงสร้างฐานข้อมูล
│── Dockerfile                       # 🐳 สคริปต์สำหรับสร้าง Docker Image ของ FastAPI Application
│── docker-compose.yml               # 🛠️ กำหนดบริการ (FastAPI + MySQL) เพื่อให้ทำงานร่วมกันด้วย Docker
```

## 🛠️ การติดตั้ง Dependencies
### Windows
```bash
python -m venv venv  # สร้าง virtual environment
venv\Scripts\activate  # เปิดใช้งาน venv
pip install -r requirements.txt  # ติดตั้ง dependencies
```

### MacOS/Linux
```bash
python3 -m venv venv  # สร้าง virtual environment
source venv/bin/activate  # เปิดใช้งาน venv
pip3 install -r requirements.txt  # ติดตั้ง dependencies
```

---

## 🐳 การตั้งค่า Docker
### 1️⃣ สร้าง Docker Network
```bash
docker network create nw_20250315_database
```

### 2️⃣ รัน Container ของ MySQL
```bash
docker run --name db_mysql -e MYSQL_ROOT_PASSWORD=1111 --network nw_20250315_database -p 3306:3306 -d mysql:5.7
```

### 3️⃣ รัน phpMyAdmin (ตัวเลือกเสริม)
```bash
docker run --name db_phpmyadmin --network nw_20250315_database -p 8888:80 -e PMA_ARBITRARY=1 -d phpmyadmin/phpmyadmin
```

### 4️⃣ เข้าใช้งาน phpMyAdmin
- เปิดเบราว์เซอร์: [http://localhost:8888](http://localhost:8888)
- Server: `db_mysql`
- Username: `root`
- Password: `1111`

---

## 🛠️ การตั้งค่าฐานข้อมูล
### 5️⃣ เข้าถึง MySQL และสร้างฐานข้อมูล
#### เชื่อมต่อผ่าน CLI:
```bash
docker exec -it db_mysql mysql -u root -p
```
#### รันคำสั่ง SQL:
```sql
CREATE DATABASE nor_db;
USE nor_db;

-- สร้างตาราง users
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE,
    address TEXT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- สร้างตาราง products
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- สร้างตาราง product_images
CREATE TABLE product_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    image_type ENUM('main', 'thumbnail', 'gallery') DEFAULT 'gallery',
    sort_order INT DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    file_size INT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- สร้างตาราง orders
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- สร้างตาราง order_items
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_time DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- เพิ่มข้อมูลตัวอย่าง (ถ้าต้องการ)
-- เพิ่มข้อมูล User
INSERT INTO users (first_name, last_name, email, phone, address, username, password, role, created_at) VALUES
('Admin', 'User', 'admin@email.com', '0901234567', '789 Admin St, Bangkok', 'admin1', '$2b$12$w1Tmfu2UqH9iGn7FZObSf.gzC1ZVy8x9B.Jo/om3sSDMUrofZ39Oi', 'admin', NOW()),
('John', 'Doe', 'john.doe@email.com', '0812345678', '123 Main St, Bangkok', 'user1', '$2b$12$w1Tmfu2UqH9iGn7FZObSf.gzC1ZVy8x9B.Jo/om3sSDMUrofZ39Oi', 'user', NOW());

-- เพิ่มสินค้าตัวอย่าง
INSERT INTO products (name, description, price, stock_quantity, created_at, updated_at) VALUES
('สมาร์ทโฟน XYZ', 'สมาร์ทโฟนรุ่นใหม่ล่าสุดจาก XYZ', 15000.00, 50, NOW(), NOW()),
('แล็ปท็อป ABC', 'แล็ปท็อปประสิทธิภาพสูงสำหรับทำงานและเล่นเกม', 35000.00, 20, NOW(), NOW()),
('หูฟังไร้สาย', 'หูฟังไร้สายเสียงคุณภาพสูง แบตเตอรี่อายุการใช้งานยาวนาน', 3500.00, 100, NOW(), NOW());
```

**หมายเหตุ:** รหัสผ่านตัวอย่างในคำสั่ง SQL คือ "12345678" ที่ผ่านการ hash แล้ว

---

## 🚀 การรันเซิร์ฟเวอร์ FastAPI
### 6️⃣ เริ่มต้นเซิร์ฟเวอร์ FastAPI
#### Windows:
```bash
uvicorn main:app --reload
```
#### MacOS/Linux:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🎨 การใช้งาน Jinja2 Templates และ HTMX

โปรเจกต์นี้เริ่มมีการใช้ Jinja2 เพื่อเรนเดอร์ Templates และใช้ HTMX เพื่อเพิ่มความสามารถ Dynamic ให้กับ Frontend โดยไม่ต้องเขียน JavaScript มากมาย

### ✨ ระบบ Admin Interface แบบง่าย

โปรเจกต์มีหน้า Admin Interface แบบง่ายสำหรับการจัดการระบบ:

| เส้นทาง (Endpoint) | คำอธิบาย |
|------------------|----------|
| `/admin/login`   | หน้าเข้าสู่ระบบ (Login) สำหรับ Admin |
| `/admin/dashboard` | หน้า Dashboard แสดงข้อมูลสรุป |

### 🖼️ การทดสอบ Templates และหน้า Admin

1. เริ่มต้นเซิร์ฟเวอร์ FastAPI:
   ```bash
   uvicorn main:app --reload
   ```

2. เปิดเบราว์เซอร์และเข้าไปที่:
   - [http://localhost:8000/admin/login](http://localhost:8000/admin/login) - เพื่อเข้าสู่ระบบ Admin
   - ล็อกอินด้วย username: `admin1` และ password: `12345678`
   - เมื่อเข้าสู่ระบบสำเร็จ ระบบจะนำคุณไปยังหน้า Dashboard

3. ทดสอบ HTMX Features:
   - การส่งฟอร์ม Login โดยไม่ refresh หน้า
   - การแสดงข้อมูล Recent Activity ที่ refresh อัตโนมัติทุก 30 วินาที
   - ปุ่ม Logout ที่ทำงานผ่าน HTMX

### 🔨 โครงสร้าง Templates

```
templates/
├── base.html              # 🏗️ เทมเพลตหลักที่เป็น Layout หลัก
├── admin/
│   ├── login.html         # 🔐 หน้า Login สำหรับ Admin
│   └── dashboard.html     # 📊 หน้า Dashboard สำหรับ Admin
└── components/
    ├── header.html        # 🔝 ส่วน Header ของเว็บ
    ├── navbar.html        # 🧭 เมนูนำทาง
    ├── footer.html        # 👣 ส่วน Footer ของเว็บ
    └── _recent_activity.html  # 🔄 ส่วนแสดงกิจกรรมล่าสุด (HTMX partial)
```

### 🧩 การทำงานของ HTMX

HTMX ช่วยให้เว็บแอพของเรามีความสามารถ Dynamic โดยไม่ต้องเขียน JavaScript มากมาย:
- ฟอร์ม Login ส่งข้อมูลแบบ AJAX ด้วย `hx-post="/admin/login"`
- Recent Activity โหลดข้อมูลอัตโนมัติด้วย `hx-get="/admin/recent-activity"` และ `hx-trigger="load, every 30s"`
- ปุ่ม Logout ทำงานผ่าน HTMX ด้วย `hx-post="/logout"` และ `hx-push-url="true"`

---

## 🔥 API Endpoints

### 👤 User Management
| Method   | Endpoint                | คำอธิบาย                   |
| -------- | ----------------------- | -------------------------- |
| `POST`   | `/users/login`          | เข้าสู่ระบบและรับ JWT Token |
| `POST`   | `/users/`               | สร้างผู้ใช้ใหม่              |
| `GET`    | `/users/`               | ดึงข้อมูลผู้ใช้ทั้งหมด         |
| `GET`    | `/users/{id}`           | ดึงข้อมูลผู้ใช้ตาม ID       |
| `PUT`    | `/users/{id}`           | อัปเดตข้อมูลผู้ใช้           |
| `DELETE` | `/users/{id}`           | ลบผู้ใช้                    |

### 🛍️ Product Management
| Method   | Endpoint                | คำอธิบาย                     |
| -------- | ----------------------- | ---------------------------- |
| `POST`   | `/products/`            | สร้างสินค้าใหม่                |
| `GET`    | `/products/`            | ดึงข้อมูลสินค้าทั้งหมด           |
| `GET`    | `/products/{id}`        | ดึงข้อมูลสินค้าตาม ID         |
| `PUT`    | `/products/{id}`        | อัปเดตข้อมูลสินค้า             |
| `DELETE` | `/products/{id}`        | ลบสินค้า                      |

### 🖼️ Product Image Management
| Method   | Endpoint                                     | คำอธิบาย                      |
| -------- | -------------------------------------------- | ----------------------------- |
| `POST`   | `/products/{id}/images`                      | อัปโหลดรูปภาพสินค้า             |
| `GET`    | `/products/{id}/images`                      | ดึงรูปภาพทั้งหมดของสินค้า         |
| `GET`    | `/products/{id}/images/{image_id}`           | ดึงรูปภาพเดียวของสินค้า          |
| `PUT`    | `/products/{id}/images/{image_id}`           | อัปเดตข้อมูลรูปภาพ              |
| `DELETE` | `/products/{id}/images/{image_id}`           | ลบรูปภาพ                       |
| `PUT`    | `/products/{id}/images/{image_id}/set-primary` | ตั้งเป็นรูปภาพหลัก              |
| `PUT`    | `/products/{id}/images/reorder`                | จัดเรียงลำดับรูปภาพใหม่          |

### 📦 Order Management
| Method   | Endpoint                           | คำอธิบาย                     |
| -------- | ---------------------------------- | ---------------------------- |
| `POST`   | `/orders/`                         | สร้าง Order ใหม่             |
| `GET`    | `/orders/`                         | ดึงข้อมูล Order ทั้งหมด       |
| `GET`    | `/orders/{id}`                     | ดึงข้อมูล Order ตาม ID      |
| `PUT`    | `/orders/{id}`                     | อัปเดตสถานะ Order           |
| `GET`    | `/users/{id}/orders`               | ดึงประวัติการสั่งซื้อของผู้ใช้     |

---

## 🔄 ตัวอย่างการใช้งาน API

### 🔐 การเข้าสู่ระบบและใช้ JWT Token
```bash
# 1. เข้าสู่ระบบเพื่อรับ Token
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin1&password=12345678"

# 2. นำ Token ที่ได้ไปใช้ในการเรียก API อื่น ๆ
curl -X GET "http://localhost:8000/products/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 🛍️ การสร้างสินค้าใหม่
```json
POST /products/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "หูฟังไร้สาย XYZ",
  "description": "หูฟังไร้สายรุ่นใหม่ เสียงดี ใส่สบาย",
  "price": 2500.00,
  "stock_quantity": 100
}
```

### 🖼️ การอัปโหลดรูปภาพสินค้า
```
POST /products/1/images/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

file: <file>
image_type: main
is_primary: true
```

### 📦 การสร้าง Order
```json
POST /orders/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "user_id": 2,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ]
}
```

## 🖼️ จัดการไฟล์รูปภาพ

### ข้อจำกัดของไฟล์
- **ขนาดไฟล์สูงสุด:** 5MB
- **นามสกุลที่รองรับ:** jpg, jpeg, png, gif, webp
- **ชนิดไฟล์ที่รองรับ:** image/jpeg, image/png, image/gif, image/webp

### เส้นทางการเข้าถึงรูปภาพ
รูปภาพที่อัปโหลดจะถูกเก็บในโฟลเดอร์ `uploads/products/` และสามารถเข้าถึงได้ผ่าน URL ในรูปแบบ:
```
http://localhost:8000/uploads/products/{filename}
```

### การจัดการรูปภาพหลัก
สินค้าแต่ละชิ้นสามารถมีรูปภาพหลักได้เพียงรูปเดียวเท่านั้น โดยการตั้งค่าผ่าน:
- เมื่ออัปโหลดรูปภาพใหม่ใช้ฟิลด์ `is_primary: true`
- เปลี่ยนรูปภาพหลักโดยใช้ endpoint `/products/{id}/images/{image_id}/set-primary`

---

## 🧪 ทดสอบ API ด้วย Swagger UI
คุณสามารถทดสอบ API ทั้งหมดได้ผ่าน Swagger UI ที่ URL:
```
http://localhost:8000/docs
```

## ✅ เสร็จสิ้น! 🎉
ตอนนี้คุณสามารถทดสอบ API ผ่าน **Postman** หรือ **Swagger UI** ที่ `http://127.0.0.1:8000/docs` 🚀