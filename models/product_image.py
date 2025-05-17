from database import get_connection
from datetime import datetime

# 🖼️ CREATE: Insert Product Image และ Return ที่เพิ่ง Insert
def create_product_image(image):
    conn = get_connection()
    with conn.cursor() as cursor:
        # ถ้าเป็นภาพ primary ให้รีเซ็ตภาพ primary เดิมก่อน
        if image.is_primary:
            cursor.execute(
                "UPDATE product_images SET is_primary = 0 WHERE product_id = %s", 
                (image.product_id,)
            )
        
        # 💾 Insert Product Image
        sql = """
            INSERT INTO product_images (
                product_id, image_url, image_type, sort_order, 
                is_primary, file_size, file_type, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        
        # หาลำดับถัดไป ถ้าไม่ได้ระบุมา
        if image.sort_order == 0:
            cursor.execute(
                "SELECT COALESCE(MAX(sort_order), 0) + 1 FROM product_images WHERE product_id = %s", 
                (image.product_id,)
            )
            next_order = cursor.fetchone()['COALESCE(MAX(sort_order), 0) + 1']
        else:
            next_order = image.sort_order
            
        cursor.execute(sql, (
            image.product_id,
            image.image_url,
            image.image_type,
            next_order,
            image.is_primary,
            image.file_size,
            image.file_type,
            now,
            now
        ))
        conn.commit()
        
        # 🔍 ดึงข้อมูลที่เพิ่ง Insert มาเพื่อตอบกลับ
        image_id = cursor.lastrowid
        cursor.execute("SELECT * FROM product_images WHERE image_id = %s", (image_id,))
        new_image = cursor.fetchone()

    conn.close()
    return new_image


# 🖼️ READ: Select Product Images ของสินค้าหนึ่ง ๆ
def get_product_images(product_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = """
            SELECT * FROM product_images 
            WHERE product_id = %s
            ORDER BY sort_order
        """
        cursor.execute(sql, (product_id,))
        images = cursor.fetchall()

    conn.close()
    return images


# 🖼️ READ: Select Product Image by ID
def get_product_image_by_id(image_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM product_images WHERE image_id = %s"
        cursor.execute(sql, (image_id,))
        image = cursor.fetchone()

    conn.close()
    return image


# 🖼️ UPDATE: แก้ไขข้อมูล Product Image
def update_product_image(image_id: int, image_data):
    conn = get_connection()
    with conn.cursor() as cursor:
        # ตรวจสอบว่ามีรูปนี้หรือไม่
        cursor.execute("SELECT * FROM product_images WHERE image_id = %s", (image_id,))
        current_image = cursor.fetchone()
        
        if not current_image:
            conn.close()
            return None
            
        # ถ้าต้องการตั้งเป็นรูปหลัก ให้รีเซ็ตรูปอื่นก่อน
        if image_data.is_primary:
            cursor.execute(
                "UPDATE product_images SET is_primary = 0 WHERE product_id = %s", 
                (current_image['product_id'],)
            )
        
        # 🔄 Update image
        sql = """
            UPDATE product_images 
            SET image_type = %s, sort_order = %s, is_primary = %s, updated_at = %s
            WHERE image_id = %s
        """
        now = datetime.now()
        cursor.execute(sql, (
            image_data.image_type if image_data.image_type is not None else current_image['image_type'],
            image_data.sort_order if image_data.sort_order is not None else current_image['sort_order'],
            image_data.is_primary if image_data.is_primary is not None else current_image['is_primary'],
            now,
            image_id
        ))
        conn.commit()
        
        # 🔍 ดึงข้อมูลที่ถูก Update มาเพื่อตอบกลับ
        cursor.execute("SELECT * FROM product_images WHERE image_id = %s", (image_id,))
        updated_image = cursor.fetchone()

    conn.close()
    return updated_image


# 🖼️ UPDATE: ตั้งเป็นรูปหลัก
def set_primary_image(image_id: int, product_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        # รีเซ็ตรูปหลักเดิมก่อน
        cursor.execute(
            "UPDATE product_images SET is_primary = 0 WHERE product_id = %s", 
            (product_id,)
        )
        
        # ตั้งรูปใหม่เป็นรูปหลัก
        cursor.execute(
            "UPDATE product_images SET is_primary = 1, updated_at = %s WHERE image_id = %s", 
            (datetime.now(), image_id)
        )
        conn.commit()
        
        # 🔍 ดึงข้อมูลที่ถูก Update มาเพื่อตอบกลับ
        cursor.execute("SELECT * FROM product_images WHERE image_id = %s", (image_id,))
        updated_image = cursor.fetchone()

    conn.close()
    return updated_image


# 🖼️ UPDATE: จัดลำดับรูปภาพใหม่
def reorder_images(product_id: int, image_ids_order: list):
    conn = get_connection()
    with conn.cursor() as cursor:
        # ตรวจสอบว่ารูปทั้งหมดเป็นของสินค้านี้
        placeholders = ', '.join(['%s'] * len(image_ids_order))
        sql = f"""
            SELECT COUNT(*) as count 
            FROM product_images 
            WHERE image_id IN ({placeholders}) AND product_id = %s
        """
        cursor.execute(sql, image_ids_order + [product_id])
        result = cursor.fetchone()
        
        if result['count'] != len(image_ids_order):
            conn.close()
            return False
            
        # อัปเดตลำดับ
        now = datetime.now()
        for idx, image_id in enumerate(image_ids_order, 1):  # เริ่มจาก 1
            cursor.execute(
                "UPDATE product_images SET sort_order = %s, updated_at = %s WHERE image_id = %s", 
                (idx, now, image_id)
            )
        
        conn.commit()
        
        # 🔍 ดึงข้อมูลรูปภาพทั้งหมดของสินค้านี้มาเพื่อตอบกลับ
        cursor.execute(
            "SELECT * FROM product_images WHERE product_id = %s ORDER BY sort_order", 
            (product_id,)
        )
        images = cursor.fetchall()

    conn.close()
    return images


# 🖼️ DELETE: ลบรูปภาพ
def delete_product_image(image_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        # ตรวจสอบว่ามีภาพนี้หรือไม่
        cursor.execute("SELECT * FROM product_images WHERE image_id = %s", (image_id,))
        image = cursor.fetchone()
        
        if not image:
            conn.close()
            return False
            
        # ❌ ลบภาพ
        cursor.execute("DELETE FROM product_images WHERE image_id = %s", (image_id,))
        conn.commit()
        
        # ตรวจสอบว่าถ้าภาพที่ลบเป็นภาพหลัก ให้กำหนดภาพหลักใหม่
        if image['is_primary']:
            cursor.execute(
                """
                UPDATE product_images 
                SET is_primary = 1, updated_at = %s
                WHERE product_id = %s
                ORDER BY sort_order
                LIMIT 1
                """, 
                (datetime.now(), image['product_id'])
            )
            conn.commit()

    conn.close()
    return True