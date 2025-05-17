from database import get_connection
from datetime import datetime
from decimal import Decimal

# 📦 CREATE: สร้าง Order และ Order Items
def create_order(order_data):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # เริ่ม Transaction
            conn.begin()
            
            # 1. ตรวจสอบว่าสินค้ามีพอหรือไม่ และคำนวณราคารวม
            total_amount = Decimal('0.00')
            order_items = []
            
            for item in order_data.items:
                # ดึงข้อมูลสินค้า
                cursor.execute("SELECT * FROM products WHERE product_id = %s", (item.product_id,))
                product = cursor.fetchone()
                
                if not product:
                    raise ValueError(f"Product with ID {item.product_id} not found")
                    
                if product['stock_quantity'] < item.quantity:
                    raise ValueError(f"Not enough stock for product {product['name']}")
                
                # คำนวณราคารวมของ item นี้
                price = Decimal(str(product['price']))
                subtotal = price * item.quantity
                total_amount += subtotal
                
                # เก็บข้อมูลสำหรับสร้าง order item
                order_items.append({
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'price_at_time': price,
                    'subtotal': subtotal,
                    'product': product  # เก็บข้อมูลสินค้าเพื่อใช้ในการอัปเดตสต็อก
                })
            
            # 2. สร้าง Order
            now = datetime.now()
            sql = """
                INSERT INTO orders (user_id, total_amount, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                order_data.user_id,
                float(total_amount),
                'pending',  # เริ่มต้นเป็น pending
                now,
                now
            ))
            
            # รับ ID ของ order ที่เพิ่งสร้าง
            order_id = cursor.lastrowid
            
            # 3. สร้าง Order Items
            for item in order_items:
                sql = """
                    INSERT INTO order_items (
                        order_id, product_id, quantity, price_at_time, subtotal
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    order_id,
                    item['product_id'],
                    item['quantity'],
                    float(item['price_at_time']),
                    float(item['subtotal'])
                ))
                
                # 4. อัปเดตสต็อกสินค้า
                new_stock = item['product']['stock_quantity'] - item['quantity']
                cursor.execute(
                    "UPDATE products SET stock_quantity = %s, updated_at = %s WHERE product_id = %s",
                    (new_stock, now, item['product_id'])
                )
            
            # Commit Transaction
            conn.commit()
            
            # ดึงข้อมูล Order ที่เพิ่งสร้างมาเพื่อตอบกลับ
            order = get_order_with_items(order_id)
            
    except Exception as e:
        # เมื่อเกิดข้อผิดพลาด ให้ Rollback
        conn.rollback()
        conn.close()
        raise e
        
    conn.close()
    return order


# 📦 READ: ดึงข้อมูล Order ทั้งหมด
def get_orders():
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM orders ORDER BY created_at DESC"
        cursor.execute(sql)
        orders = cursor.fetchall()

    conn.close()
    return orders


# 📦 READ: ดึงข้อมูล Order ของผู้ใช้คนใดคนหนึ่ง
def get_user_orders(user_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC"
        cursor.execute(sql, (user_id,))
        orders = cursor.fetchall()

    conn.close()
    return orders


# 📦 READ: ดึงข้อมูล Order พร้อม Order Items
def get_order_with_items(order_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        # ดึงข้อมูล Order
        sql = "SELECT * FROM orders WHERE order_id = %s"
        cursor.execute(sql, (order_id,))
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            return None
            
        # ดึงข้อมูล Order Items
        sql = """
            SELECT oi.*, p.name as product_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """
        cursor.execute(sql, (order_id,))
        items = cursor.fetchall()
        
        # เพิ่ม items เข้าไปใน order
        order['items'] = items

    conn.close()
    return order


# 📦 UPDATE: อัปเดตสถานะ Order
def update_order_status(order_id: int, status: str):
    conn = get_connection()
    with conn.cursor() as cursor:
        # ตรวจสอบว่ามี Order นี้หรือไม่
        cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        current_order = cursor.fetchone()
        
        if not current_order:
            conn.close()
            return None
            
        # ถ้าสถานะเปลี่ยนจาก pending เป็น cancelled ให้คืนสต็อกสินค้า
        if current_order['status'] == 'pending' and status == 'cancelled':
            # ดึงข้อมูล order items
            cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
            items = cursor.fetchall()
            
            now = datetime.now()
            
            # คืนสต็อกสินค้า
            for item in items:
                cursor.execute(
                    """
                    UPDATE products 
                    SET stock_quantity = stock_quantity + %s, updated_at = %s 
                    WHERE product_id = %s
                    """,
                    (item['quantity'], now, item['product_id'])
                )
        
        # อัปเดตสถานะ
        sql = "UPDATE orders SET status = %s, updated_at = %s WHERE order_id = %s"
        now = datetime.now()
        cursor.execute(sql, (status, now, order_id))
        conn.commit()
        
        # ดึงข้อมูล Order ที่อัปเดตแล้วพร้อม items
        updated_order = get_order_with_items(order_id)

    conn.close()
    return updated_order