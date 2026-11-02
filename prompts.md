# Ecommerce
  จงเขียนโค้ดเว็บแอปพลิเคชันระบบร้านค้าออนไลน์ (E-Commerce Store) แบบ Single-File HTML5 ที่สมบูรณ์ในไฟล์เดียว (รวม HTML, Tailwind CSS ผ่าน CDN และ Vanilla ES6 JavaScript ไว้ในไฟล์ .html เดียวกัน ห้ามแยกไฟล์ และห้ามละโค้ดด้วยคอมเมนต์ว่า // ... rest of code)

  ข้อกำหนดโครงสร้าง HTML ID และ Class บังคับ (ต้องใช้ชื่อตามนี้ทุกตัวอักษรเพื่อใช้ตรวจด้วยระบบอัตโนมัติ):
  1. ช่องค้นหาชื่อสินค้าด้วยคีย์เวิร์ด: id="search-input"
  2. ดรอปดาวน์กรองหมวดหมู่สินค้า: id="category-select" (ต้องมีค่าเริ่มต้น value="all" สำหรับแสดงทั้งหมด)
  3. พื้นที่แสดงรายการสินค้า: id="catalog-grid" โดยการ์ดสินค้าแต่ละชิ้นต้องมี class="catalog-item" และปุ่มเพิ่มลงตะกร้าในแต่ละการ์ดต้องมี class="add-btn"
  4. พื้นที่แสดงรายการในตะกร้าสินค้า: id="cart-list" โดยแต่ละรายการในตะกร้าต้องมีปุ่มเพิ่มจำนวน (class="qty-inc"), ปุ่มลดจำนวน (class="qty-dec") และปุ่มลบสินค้า (class="remove-btn")
  5. ตัวเลขแสดงยอดรวมก่อนหักส่วนลด (Subtotal): id="subtotal-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง เช่น 1500.00 ห้ามใส่สัญลักษณ์สกุลเงินปนในแท็กนี้)
  6. ตัวเลขแสดงส่วนลดโปรโมชัน (Discount): id="discount-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง)
  7. ตัวเลขแสดงภาษีมูลค่าเพิ่ม (Tax/VAT): id="tax-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง)
  8. ตัวเลขแสดงยอดสุทธิที่ต้องชำระ (Grand Total): id="grand-total-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง)
  9. ช่องกรอกชื่อ-ที่อยู่ลูกค้าสำหรับสั่งซื้อ: id="customer-input"
  10. ปุ่มยืนยันการสั่งซื้อ: id="checkout-btn"

  ข้อกำหนดข้อมูลเริ่มต้นและลอจิกการทำงาน:
  - Module 1 (Catalog): มีข้อมูลสินค้าตั้งต้นในตัวแปร Array 6 ชิ้น แบ่งเป็น 3 หมวดหมู่ (Gadgets, Accessories, Audio) ดังนี้:
    1) "Wireless Mouse" หมวด "Accessories" ราคา 400
    2) "USB-C Hub" หมวด "Accessories" ราคา 600
    3) "Bluetooth Speaker" หมวด "Audio" ราคา 1200
    4) "Noise-Canceling Earbuds" หมวด "Audio" ราคา 1500
    5) "Mechanical Keyboard" หมวด "Gadgets" ราคา 2200
    6) "Smart Watch Pro" หมวด "Gadgets" ราคา 3000
  - Module 2 (Filter & Search): เมื่อพิมพ์ใน #search-input หรือเปลี่ยนค่าใน #category-select ต้องกรองสินค้าใน #catalog-grid แบบ Real-time โดยทำงานร่วมกันได้ทั้ง 2 เงื่อนไข
  - Module 3 (Cart Mutation): กด .add-btn เพื่อเพิ่มสินค้าลง #cart-list (ถ้ามีอยู่แล้วให้บวกจำนวนเพิ่ม 1) กด .qty-inc เพิ่มจำนวนทีละ 1, กด .qty-dec ลดจำนวนทีละ 1 (ถ้าลดจนเป็น 0 ให้ลบออกจากตะกร้า), และกด .remove-btn เพื่อลบสินค้านั้นออกจากตะกร้าทันที
  - Module 4 (Financial Formula): คำนวณสดทุกครั้งที่ตะกร้าเปลี่ยน:
    - Subtotal (#subtotal-val) = ผลรวม (ราคา x จำนวน)
    - Discount (#discount-val) = ถ้ายอด Subtotal >= 2000 บาท ให้ลด 15% (Subtotal * 0.15) ถ้าน้อยกว่า 2000 บาท ให้ส่วนลดเป็น 0.00
    - Tax (#tax-val) = คิด VAT 7% จากยอดหลังหักส่วนลด ((Subtotal - Discount) * 0.07)
    - Grand Total (#grand-total-val) = (Subtotal - Discount) + Tax
  - Module 5 (Persistence & Validation):
    - ทุกครั้งที่ข้อมูลในตะกร้าเปลี่ยนแปลง ต้องบันทึกลง localStorage โดยใช้คีย์ชื่อ "app_cart_state" และโหลดกลับมาแสดงผลอัตโนมัติเมื่อเปิดหน้าเว็บใหม่
    - เมื่อกดปุ่ม #checkout-btn ถ้าตะกร้าว่าง หรือช่อง #customer-input ว่างเปล่า ห้ามบันทึกการสั่งซื้อและต้องแจ้งเตือน แต่ถ้าข้อมูลครบและมีสินค้าในตะกร้า ให้บันทึกข้อมูลการสั่งซื้อลง localStorage คีย์ "app_last_order"

  ให้ตอบกลับเป็นโค้ด HTML ฉบับเต็มในบล็อกเดียวที่พร้อมรันทันที

# Book Store
  จงเขียนโค้ดเว็บแอปพลิเคชันระบบร้านหนังสือออนไลน์ (BookStore System) แบบ Single-File HTML5 ที่สมบูรณ์ในไฟล์เดียว (รวม HTML, Tailwind CSS ผ่าน CDN และ Vanilla ES6 JavaScript ไว้ในไฟล์ .html เดียวกัน ห้ามแยกไฟล์ และห้ามละโค้ดด้วยคอมเมนต์ว่า // ... rest of code)

  ข้อกำหนดโครงสร้าง HTML ID และ Class บังคับ (ต้องใช้ชื่อตามนี้ทุกตัวอักษรเพื่อใช้ตรวจด้วยระบบอัตโนมัติ):
  1. ช่องค้นหาชื่อหนังสือด้วยคีย์เวิร์ด: id="search-input"
  2. ดรอปดาวน์กรองหมวดหมู่หนังสือ: id="category-select" (ต้องมีค่าเริ่มต้น value="all" สำหรับแสดงทั้งหมด)
  3. พื้นที่แสดงรายการหนังสือ: id="catalog-grid" โดยการ์ดหนังสือแต่ละเล่มต้องมี class="catalog-item" และปุ่มหยิบใส่ตะกร้าในแต่ละการ์ดต้องมี class="add-btn"
  4. พื้นที่แสดงรายการในตะกร้าหนังสือ: id="cart-list" โดยแต่ละรายการในตะกร้าต้องมีปุ่มเพิ่มจำนวน (class="qty-inc"), ปุ่มลดจำนวน (class="qty-dec") และปุ่มลบรายการ (class="remove-btn")
  5. ตัวเลขแสดงยอดรวมค่าหนังสือ (Subtotal): id="subtotal-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง เช่น 450.00 ห้ามใส่สัญลักษณ์สกุลเงินปนในแท็กนี้)
  6. ตัวเลขแสดงส่วนลดโปรโมชันซื้อครบจำนวนเล่ม (Discount): id="discount-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง)
  7. ตัวเลขแสดงค่าจัดส่งคงที่ (Shipping Fee ใช้ ID นี้แทนช่องภาษี): id="tax-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง)
  8. ตัวเลขแสดงยอดสุทธิที่ต้องชำระ (Grand Total): id="grand-total-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง)
  9. ช่องกรอกชื่อสมาชิกผู้สั่งซื้อ: id="customer-input"
  10. ปุ่มยืนยันการสั่งซื้อหนังสือ: id="checkout-btn"

  ข้อกำหนดข้อมูลเริ่มต้นและลอจิกการทำงาน:
  - Module 1 (Catalog): มีข้อมูลหนังสือตั้งต้นในตัวแปร Array 6 เล่ม แบ่งเป็น 3 หมวดหมู่ (Fiction, Tech, Business) ดังนี้:
    1) "The Silent Forest" หมวด "Fiction" ราคา 180
    2) "Midnight Star" หมวด "Fiction" ราคา 220
    3) "Startup Zero" หมวด "Business" ราคา 280
    4) "Financial Freedom" หมวด "Business" ราคา 320
    5) "Clean Python Architecture" หมวด "Tech" ราคา 450
    6) "Deep Learning Systems" หมวด "Tech" ราคา 550
  - Module 2 (Filter & Search): เมื่อพิมพ์ใน #search-input หรือเปลี่ยนค่าใน #category-select ต้องกรองหนังสือใน #catalog-grid แบบ Real-time โดยทำงานร่วมกันได้ทั้ง 2 เงื่อนไข
  - Module 3 (Cart Mutation): กด .add-btn เพื่อเพิ่มหนังสือลง #cart-list (ถ้ามีอยู่แล้วให้บวกจำนวนเพิ่ม 1) กด .qty-inc เพิ่มจำนวนทีละ 1, กด .qty-dec ลดจำนวนทีละ 1 (ถ้าลดจนเป็น 0 ให้ลบออกจากตะกร้า), และกด .remove-btn เพื่อลบหนังสือนั้นออกจากตะกร้าทันที
  - Module 4 (Financial Formula): คำนวณสดทุกครั้งที่ตะกร้าเปลี่ยน:
    - Subtotal (#subtotal-val) = ผลรวม (ราคาหนังสือ x จำนวนเล่ม)
    - Discount (#discount-val) = ถ้ารวมจำนวนหนังสือทั้งหมดในตะกร้า (Total Quantity) >= 3 เล่มขึ้นไป ให้ลดทันที 80.00 บาท ถ้าน้อยกว่า 3 เล่ม ให้ส่วนลดเป็น 0.00
    - Shipping Fee (#tax-val) = ถ้ามีหนังสือในตะกร้าอย่างน้อย 1 เล่ม ให้คิดค่าส่งคงที่ 50.00 บาท ถ้าตะกร้าว่างให้เป็น 0.00
    - Grand Total (#grand-total-val) = max(0, Subtotal - Discount) + Shipping Fee
  - Module 5 (Persistence & Validation):
    - ทุกครั้งที่ข้อมูลในตะกร้าเปลี่ยนแปลง ต้องบันทึกลง localStorage โดยใช้คีย์ชื่อ "app_cart_state" และโหลดกลับมาแสดงผลอัตโนมัติเมื่อเปิดหน้าเว็บใหม่
    - เมื่อกดปุ่ม #checkout-btn ถ้าตะกร้าว่าง หรือช่อง #customer-input ว่างเปล่า ห้ามบันทึกการสั่งซื้อและต้องแจ้งเตือน แต่ถ้าข้อมูลครบและมีหนังสือในตะกร้า ให้บันทึกข้อมูลการสั่งซื้อลง localStorage คีย์ "app_last_order"

  ให้ตอบกลับเป็นโค้ด HTML ฉบับเต็มในบล็อกเดียวที่พร้อมรันทันที

# Food store
  จงเขียนโค้ดเว็บแอปพลิเคชันระบบจัดการออเดอร์ร้านอาหาร (Food Store Management / POS System) แบบ Single-File HTML5 ที่สมบูรณ์ในไฟล์เดียว (รวม HTML, Tailwind CSS ผ่าน CDN และ Vanilla ES6 JavaScript ไว้ในไฟล์ .html เดียวกัน ห้ามแยกไฟล์ และห้ามละโค้ดด้วยคอมเมนต์ว่า // ... rest of code)

  ข้อกำหนดโครงสร้าง HTML ID และ Class บังคับ (ต้องใช้ชื่อตามนี้ทุกตัวอักษรเพื่อใช้ตรวจด้วยระบบอัตโนมัติ):
  1. ช่องค้นหาชื่อเมนูอาหารด้วยคีย์เวิร์ด: id="search-input"
  2. ดรอปดาวน์กรองหมวดหมู่อาหาร: id="category-select" (ต้องมีค่าเริ่มต้น value="all" สำหรับแสดงทั้งหมด)
  3. พื้นที่แสดงรายการเมนูอาหาร: id="catalog-grid" โดยการ์ดเมนูแต่ละจานต้องมี class="catalog-item" และปุ่มเพิ่มลงรายการสั่งอาหารในแต่ละการ์ดต้องมี class="add-btn"
  4. พื้นที่แสดงรายการออเดอร์ปัจจุบัน: id="cart-list" โดยแต่ละรายการในออเดอร์ต้องมีปุ่มเพิ่มจำนวน (class="qty-inc"), ปุ่มลดจำนวน (class="qty-dec") และปุ่มลบรายการ (class="remove-btn")
  5. ตัวเลขแสดงยอดรวมค่าอาหาร (Subtotal): id="subtotal-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง เช่น 250.00 ห้ามใส่สัญลักษณ์สกุลเงินปนในแท็กนี้)
  6. ตัวเลขแสดงส่วนลดท้ายบิล (Discount): id="discount-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง)
  7. ตัวเลขแสดงค่าบริการร้านอาหาร 10% (Service Charge ใช้ ID นี้): id="tax-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง)
  8. ตัวเลขแสดงยอดสุทธิที่ต้องชำระ (Grand Total): id="grand-total-val" (แสดงเฉพาะตัวเลขทศนิยม 2 ตำแหน่ง)
  9. ช่องกรอกหมายเลขโต๊ะหรือชื่อลูกค้า: id="customer-input"
  10. ปุ่มยืนยันการสั่งอาหารเข้าครัว: id="checkout-btn"

  ข้อกำหนดข้อมูลเริ่มต้นและลอจิกการทำงาน:
  - Module 1 (Catalog): มีข้อมูลเมนูอาหารตั้งต้นในตัวแปร Array 6 เมนู แบ่งเป็น 3 หมวดหมู่ (Main, Drink, Dessert) ดังนี้:
    1) "Iced Matcha Latte" หมวด "Drink" ราคา 60
    2) "Thai Milk Tea" หมวด "Drink" ราคา 70
    3) "Mango Sticky Rice" หมวด "Dessert" ราคา 90
    4) "Chocolate Lava Cake" หมวด "Dessert" ราคา 110
    5) "Pad Kra Pao Beef" หมวด "Main" ราคา 120
    6) "Tom Yum Goong" หมวด "Main" ราคา 180
  - Module 2 (Filter & Search): เมื่อพิมพ์ใน #search-input หรือเปลี่ยนค่าใน #category-select ต้องกรองเมนูใน #catalog-grid แบบ Real-time โดยทำงานร่วมกันได้ทั้ง 2 เงื่อนไข
  - Module 3 (Cart Mutation): กด .add-btn เพื่อเพิ่มเมนูลง #cart-list (ถ้ามีอยู่แล้วให้บวกจำนวนเพิ่ม 1) กด .qty-inc เพิ่มจำนวนทีละ 1, กด .qty-dec ลดจำนวนทีละ 1 (ถ้าลดจนเป็น 0 ให้ลบออกจากออเดอร์), และกด .remove-btn เพื่อลบเมนูนั้นออกจากออเดอร์ทันที
  - Module 4 (Financial Formula): คำนวณสดทุกครั้งที่รายการออเดอร์เปลี่ยน:
    - Subtotal (#subtotal-val) = ผลรวม (ราคาอาหาร x จำนวนจาน)
    - Discount (#discount-val) = ถ้ายอด Subtotal >= 300 บาท ให้ลดทันที 40.00 บาท ถ้าน้อยกว่า 300 บาท ให้ส่วนลดเป็น 0.00
    - Service Charge (#tax-val) = คิดค่าบริการ 10% จากยอดหลังหักส่วนลด ((Subtotal - Discount) * 0.10)
    - Grand Total (#grand-total-val) = (Subtotal - Discount) + Service Charge
  - Module 5 (Persistence & Validation):
    - ทุกครั้งที่รายการออเดอร์เปลี่ยนแปลง ต้องบันทึกลง localStorage โดยใช้คีย์ชื่อ "app_cart_state" และโหลดกลับมาแสดงผลอัตโนมัติเมื่อเปิดหน้าเว็บใหม่
    - เมื่อกดปุ่ม #checkout-btn ถ้าออเดอร์ว่าง หรือช่อง #customer-input ว่างเปล่า ห้ามบันทึกออเดอร์และต้องแจ้งเตือน แต่ถ้าข้อมูลครบและมีอาหารในรายการ ให้บันทึกข้อมูลออเดอร์ลง localStorage คีย์ "app_last_order"

  ให้ตอบกลับเป็นโค้ด HTML ฉบับเต็มในบล็อกเดียวที่พร้อมรันทันที