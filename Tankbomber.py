import cv2
import numpy as np
import xml.etree.ElementTree as ET
from tkinter import filedialog, Tk, Button
import os

def select_file(file_type, extensions, title):
    Tk().withdraw()  # ปิดหน้าต่างหลักของ Tkinter
    file_path = filedialog.askopenfilename(title=title, filetypes=[(file_type, extensions)])
    return file_path

def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    objects = []
    
    for obj in root.findall("object"):
        name = obj.find("name").text
        bbox = obj.find("bndbox")
        xmin = int(bbox.find("xmin").text)
        ymin = int(bbox.find("ymin").text)
        xmax = int(bbox.find("xmax").text)
        ymax = int(bbox.find("ymax").text)
        objects.append({"name": name, "bbox": (xmin, ymin, xmax, ymax)})
    
    return objects

def draw_bbox(image, objects):
    for obj in objects:
        xmin, ymin, xmax, ymax = obj["bbox"]
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)  # วาดกรอบสีเขียว
        cv2.putText(image, obj["name"], (xmin, ymin - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

def sharpen_image(image):
    # ใช้ sharpening kernel
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened_image = cv2.filter2D(image, -1, kernel)
    return sharpened_image

def apply_median_blur(image, objects, kernel_size=5):
    # สร้างภาพเปล่าขนาดเท่าภาพต้นฉบับ
    blurred_image = np.zeros_like(image)
    
    for obj in objects:
        xmin, ymin, xmax, ymax = obj["bbox"]

        # ตัดส่วนของรูปที่ต้องการทำ Median Blur
        roi = image[ymin:ymax, xmin:xmax]
        
        # ทำ Median Blur
        blurred_roi = cv2.medianBlur(roi, kernel_size)
        
        # นำภาพที่ทำ Median Blur ไปใส่ในตำแหน่งเดิม
        blurred_image[ymin:ymax, xmin:xmax] = blurred_roi
    
    return blurred_image

def merge_images(original, sharpened, blurred):
    # ปรับขนาดภาพที่เบลอและที่ผ่านการชัดขึ้นให้เท่ากับภาพต้นฉบับ
    sharpened_resized = cv2.resize(sharpened, (original.shape[1], original.shape[0]))
    blurred_resized = cv2.resize(blurred, (original.shape[1], original.shape[0]))

    # รวมภาพทั้งสามรูป
    combined = np.hstack((original, sharpened_resized, blurred_resized))
    return combined

def save_image(image, filename):
    # เลือกที่เก็บไฟล์สำหรับการดาวน์โหลด
    save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg")])
    if save_path:
        cv2.imwrite(save_path, image)

# เลือกไฟล์รูปและ XML
image_path = select_file("JPEG Files", "*.jpg;*.jpeg", "เลือกไฟล์รูป")
xml_path = select_file("XML Files", "*.xml", "เลือกไฟล์ XML")

# โหลดรูปภาพ
image = cv2.imread(image_path)
if image is None:
    print("❌ ไม่สามารถเปิดไฟล์รูปภาพได้")
else:
    objects = parse_xml(xml_path)

    # วาดกรอบที่รูปต้นฉบับ
    image_with_bbox = draw_bbox(image.copy(), objects)

    # สร้างภาพที่ทำ Median Blur และ Sharpening
    sharpened_image = sharpen_image(image.copy())
    blurred_image = apply_median_blur(image.copy(), objects)

    # รวม 3 รูปให้แสดงคู่กัน
    final_image = merge_images(image_with_bbox, sharpened_image, blurred_image)

    # แสดงรูปที่มีกรอบ และ รูปที่ทำ Median Blur ข้างๆ
    cv2.imshow("Original + Sharpened + Median Blurred", final_image)

    # สร้าง UI สำหรับดาวน์โหลดรูป
    def save_sharpened():
        save_image(sharpened_image, "sharpened_image.jpg")
        
    def save_blurred():
        save_image(blurred_image, "blurred_image.jpg")
        
    def save_original():
        save_image(image_with_bbox, "original_image.jpg")

    root = Tk()
    root.title("Image Processing")

    save_sharpened_button = Button(root, text="ดาวน์โหลดรูปที่ปรับความชัด", command=save_sharpened)
    save_sharpened_button.pack(pady=10)

    save_blurred_button = Button(root, text="ดาวน์โหลดรูปที่ปรับความเบลอ", command=save_blurred)
    save_blurred_button.pack(pady=10)

    root.mainloop()

    cv2.waitKey(0)
    cv2.destroyAllWindows()
