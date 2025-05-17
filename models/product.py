from database import get_connection
from datetime import datetime

# 🚀 CREATE: Insert Product และ Return Product ที่เพิ่ง Insert
def create_product(product):
    conn = get_connection()
    with conn.cursor() as cursor:
        # 💾 Insert Product
        sql = """
            INSERT INTO products (name, description, price, stock_quantity, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        cursor.execute(sql, (
            product.name,
            product.description,
            float(product.price),  # แปลงเป็น float เพื่อเก็บในฐานข้อมูล
            product.stock_quantity,
            now,
            now
        ))
        conn.commit()
        
        # 🔍 ดึงข้อมูล Product ที่เพิ่ง Insert มาเพื่อตอบกลับ
        product_id = cursor.lastrowid
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        new_product = cursor.fetchone()

    conn.close()
    return new_product


# 🚀 READ: Select Products ทั้งหมด
def get_products():
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM products ORDER BY created_at DESC"
        cursor.execute(sql)
        products = cursor.fetchall()

    conn.close()
    return products


# 🚀 READ: Select Product โดยใช้ product_id
def get_product_by_id(product_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM products WHERE product_id = %s"
        cursor.execute(sql, (product_id,))
        product = cursor.fetchone()

    conn.close()
    return product


# 🚀 UPDATE: แก้ไขข้อมูล Product โดยใช้ product_id
def update_product(product_id: int, product):
    conn = get_connection()
    with conn.cursor() as cursor:
        # ดึงข้อมูลเดิมมาเพื่ออัปเดตเฉพาะ field ที่ส่งมา
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        current_product = cursor.fetchone()
        
        if not current_product:
            conn.close()
            return None

        # กำหนดค่าที่จะอัปเดต
        name = product.name if product.name is not None else current_product['name']
        description = product.description if product.description is not None else current_product['description']
        price = float(product.price) if product.price is not None else current_product['price']
        stock_quantity = product.stock_quantity if product.stock_quantity is not None else current_product['stock_quantity']
        
        # 🔄 Update Product
        sql = """
            UPDATE products 
            SET name = %s, description = %s, price = %s, stock_quantity = %s, updated_at = %s
            WHERE product_id = %s
        """
        now = datetime.now()
        cursor.execute(sql, (
            name,
            description,
            price,
            stock_quantity,
            now,
            product_id
        ))
        conn.commit()
        
        # 🔍 ดึงข้อมูล Product ที่ถูก Update มาเพื่อตอบกลับ
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        updated_product = cursor.fetchone()

    conn.close()
    return updated_product


# 🚀 DELETE: ลบข้อมูล Product โดยใช้ product_id
def delete_product(product_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        # ❌ ลบ Product
        sql = "DELETE FROM products WHERE product_id = %s"
        cursor.execute(sql, (product_id,))
        conn.commit()

        # 🔄 ตรวจสอบว่ามีการลบหรือไม่
        affected_rows = cursor.rowcount

    conn.close()
    return affected_rows > 0  # ✅ Return True ถ้าลบสำเร็จ