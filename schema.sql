SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;


-- สร้างตาราง users (มีอยู่แล้ว)
CREATE TABLE IF NOT EXISTS users (
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
)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- สร้างตาราง products
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- สร้างตาราง product_images
CREATE TABLE IF NOT EXISTS product_images (
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
)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- สร้างตาราง orders
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- สร้างตาราง order_items
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_time DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- เพิ่มข้อมูล User ตัวอย่าง
-- เพิ่ม User ตัวอย่าง
-- หมายเหตุ: รหัสผ่านถูกเข้ารหัสด้วย bcrypt
-- รหัสผ่าน: 12345678

INSERT INTO users (first_name, last_name, email, phone, address, username, password, role, created_at) VALUES
('Admin', 'User', 'admin@email.com', '0901234567', '789 Admin St, Bangkok', 'admin1', '$2b$12$w1Tmfu2UqH9iGn7FZObSf.gzC1ZVy8x9B.Jo/om3sSDMUrofZ39Oi', 'admin', NOW()),
('John', 'Doe', 'user1@email.com', '0812345678', '123 Main St, Bangkok', 'user1', '$2b$12$w1Tmfu2UqH9iGn7FZObSf.gzC1ZVy8x9B.Jo/om3sSDMUrofZ39Oi', 'user', NOW());
-- เพิ่มสินค้าตัวอย่าง
INSERT INTO products (name, description, price, stock_quantity, created_at, updated_at) VALUES
('สมาร์ทโฟน XYZ', 'สมาร์ทโฟนรุ่นใหม่ล่าสุดจาก XYZ', 15000.00, 50, NOW(), NOW()),
('แล็ปท็อป ABC', 'แล็ปท็อปประสิทธิภาพสูงสำหรับทำงานและเล่นเกม', 35000.00, 20, NOW(), NOW()),
('หูฟังไร้สาย', 'หูฟังไร้สายเสียงคุณภาพสูง แบตเตอรี่อายุการใช้งานยาวนาน', 3500.00, 100, NOW(), NOW()),
('กล้องถ่ายรูป', 'กล้องถ่ายรูปความละเอียดสูง 24MP', 28000.00, 15, NOW(), NOW()),
('สมาร์ทวอทช์', 'นาฬิกาอัจฉริยะติดตามสุขภาพและการออกกำลังกาย', 6500.00, 30, NOW(), NOW());