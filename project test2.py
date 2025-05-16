import cv2
import numpy as np
import xml.etree.ElementTree as ET
from tkinter import filedialog, Tk, Button, Label
import os

def select_file(file_type, extensions, title):
    Tk().withdraw()
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

def apply_filter2D(image, objects):
    for obj in objects:
        xmin, ymin, xmax, ymax = obj["bbox"]
        roi = image[ymin:ymax, xmin:xmax]
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])  # Sharpening filter
        filtered_roi = cv2.filter2D(roi, -1, kernel)
        image[ymin:ymax, xmin:xmax] = filtered_roi
    return image

def apply_medianBlur(image, objects):
    for obj in objects:
        xmin, ymin, xmax, ymax = obj["bbox"]
        roi = image[ymin:ymax, xmin:xmax]
        blurred_roi = cv2.medianBlur(roi, 5)
        image[ymin:ymax, xmin:xmax] = blurred_roi
    return image

def save_image(image, filename, image_path):
    save_path = os.path.join(os.path.dirname(image_path), filename)
    cv2.imwrite(save_path, image)
    print(f"✅ บันทึกรูปแล้ว: {save_path}")

def process_and_display():
    image_path = select_file("JPEG Files", "*.jpg;*.jpeg", "เลือกไฟล์รูป")
    xml_path = select_file("XML Files", "*.xml", "เลือกไฟล์ XML")

    image = cv2.imread(image_path)
    if image is None:
        print("❌ ไม่สามารถเปิดไฟล์รูปภาพได้")
        return

    objects = parse_xml(xml_path)

    image_with_bbox = draw_bbox(image.copy(), objects)
    image_with_filter2D = apply_filter2D(image_with_bbox.copy(), objects)
    image_with_medianBlur = apply_medianBlur(image_with_bbox.copy(), objects)

    combined_image = np.hstack((image_with_bbox, image_with_filter2D, image_with_medianBlur))
    cv2.imshow("Comparison: Original | filter2D | medianBlur", combined_image)

    def close_all():
        """ ปิดหน้าต่าง OpenCV และ Tkinter เมื่อกดปุ่มปิด """
        cv2.destroyAllWindows()
        root.quit()
        root.destroy()

    root = Tk()
    root.title("ดาวน์โหลดไฟล์")
    root.protocol("WM_DELETE_WINDOW", close_all)  # ให้ปิด OpenCV ด้วยเมื่อปิด Tkinter

    Label(root, text="เลือกดาวน์โหลดไฟล์").pack(pady=5)

    Button(root, text="ดาวน์โหลด: รูปที่เพิ่มความคมชัด", command=lambda: save_image(image_with_filter2D, "filtered_image.jpg", image_path)).pack(pady=5)
    Button(root, text="ดาวน์โหลด: รูปที่เพิ่มความ smooth ของภาพ", command=lambda: save_image(image_with_medianBlur, "blurred_image.jpg", image_path)).pack(pady=5)
    Button(root, text="ปิดโปรแกรม", command=close_all).pack(pady=10)

    root.mainloop()
    cv2.destroyAllWindows()  # ปิด OpenCV ทุกรอบ (กันค้าง)

# เรียกใช้ฟังก์ชันหลัก
process_and_display()
