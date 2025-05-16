import cv2
import numpy as np
import xml.etree.ElementTree as ET
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# ฟังก์ชันเลือกไฟล์ XML และรูปภาพ
def select_files():
    xml_path = filedialog.askopenfilename(title="เลือกไฟล์ XML", filetypes=[("XML Files", "*.xml")])
    if not xml_path:
        messagebox.showerror("Error", "กรุณาเลือกไฟล์ XML")
        return
    
    image_path = filedialog.askopenfilename(title="เลือกไฟล์ JPG", filetypes=[("Image Files", "*.jpg;*.png")])
    if not image_path:
        messagebox.showerror("Error", "กรุณาเลือกไฟล์รูปภาพ")
        return
    
    filename, objects = parse_xml(xml_path)
    
    if os.path.basename(image_path) != filename:
        messagebox.showwarning("Warning", "ชื่อไฟล์รูปไม่ตรงกับ XML แต่สามารถใช้ได้")
    
    draw_bbox(image_path, objects)
    get_average_color(image_path, objects)

# ฟังก์ชันอ่านค่ากรอบจาก XML
def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    filename = root.find("filename").text
    objects = []
    
    for obj in root.findall("object"):
        name = obj.find("name").text
        bbox = obj.find("bndbox")
        xmin = int(bbox.find("xmin").text)
        ymin = int(bbox.find("ymin").text)
        xmax = int(bbox.find("xmax").text)
        ymax = int(bbox.find("ymax").text)
        
        objects.append({"name": name, "bbox": (xmin, ymin, xmax, ymax)})
    
    return filename, objects

# ฟังก์ชันวาดกรอบ Bounding Box บนรูป
def draw_bbox(image_path, objects):
    image = cv2.imread(image_path)
    
    for obj in objects:
        xmin, ymin, xmax, ymax = obj["bbox"]
        cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
        cv2.putText(image, obj["name"], (xmin, ymin - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    cv2.imshow("Labeled Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# ฟังก์ชันหาค่าเฉลี่ยสีภายในกรอบ
def get_average_color(image_path, objects):
    image = cv2.imread(image_path)

    for obj in objects:
        xmin, ymin, xmax, ymax = obj["bbox"]
        roi = image[ymin:ymax, xmin:xmax]  # ตัดเฉพาะส่วนที่อยู่ในกรอบ
        avg_color = np.mean(roi, axis=(0, 1))  # หาค่าเฉลี่ยสี (BGR)
        
        print(f"Color inside {obj['name']}: BGR = {avg_color}")

# ส่วน UI
root = tk.Tk()
root.title("เลือกไฟล์ XML และรูปภาพ")
root.geometry("300x150")

btn_select = tk.Button(root, text="เลือกไฟล์ XML และ JPG", command=select_files, padx=10, pady=5)
btn_select.pack(pady=20)

root.mainloop()