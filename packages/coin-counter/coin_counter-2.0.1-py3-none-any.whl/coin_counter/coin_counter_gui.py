import os
import cv2
import json
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

REF_DIR = 'refs'
META_FILE = os.path.join(REF_DIR, "metadata.json")
os.makedirs(REF_DIR, exist_ok=True)

def load_metadata():
    if not os.path.exists(META_FILE):
        return {}
    with open(META_FILE, 'r') as f:
        return json.load(f)

def save_metadata(meta):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

def save_reference(label, value, front_path, back_path):
    meta = load_metadata()
    if label in meta:
        print(f"Reference for {label} already exists. — overwriting metadata")
    
    front_dst = os.path.join(REF_DIR, f"{label}_front.jpg")
    back_dst = os.path.join(REF_DIR, f"{label}_back.jpg")
    front_img = cv2.imread(front_path)
    back_img = cv2.imread(back_path)
    if front_img is None or back_img is None:
        raise FileNotFoundError("Could not read front/back image. Check paths.")

    cv2.imwrite(front_dst, front_img)
    cv2.imwrite(back_dst, back_img)

    meta[label] = {"value": float(value), "front": os.path.basename(front_dst), "back": os.path.basename(back_dst)}
    save_metadata(meta)

def make_orb(nfeatures=1000):
    return cv2.ORB_create(nfeatures)

def compute_orb_features(image, orb=None):
    if orb is None:
        orb = make_orb()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    keypoints, descriptors = orb.detectAndCompute(gray, None)
    return keypoints, descriptors

def match_features(desc1, desc2, ratio=0.75):
    if desc1 is None or desc2 is None:
        return []
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = bf.knnMatch(desc1, desc2, k=2)
    good_matches = []
    for m_n in matches:
        if len(m_n) != 2:
            continue
        m, n = m_n
        if m.distance < ratio * n.distance:
            good_matches.append(m)
    return good_matches

def detect_circles_hough(image, dp=1.1, min_dist=30, param1=100, param2=30, min_radius=8, max_radius=200):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    gray = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, min_dist,
                               param1=param1, param2=param2,
                               minRadius=min_radius, maxRadius=max_radius)
    if circles is None:
        return []
    circles = np.uint16(np.around(circles[0, :]))
    return circles.tolist()

def detect_circles_contour(image, min_area=500, max_area=50000, circularity_thresh=0.7):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    circles = []
    

    _, thresh1 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours1, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

    _, thresh2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours2, _ = cv2.findContours(thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

    thresh3 = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 11, 2)
    contours3, _ = cv2.findContours(thresh3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

    edges = cv2.Canny(blurred, 50, 150)
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    contours4, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    all_contours = contours1 + contours2 + contours3 + contours4
    
    
    found_circles = []
    for contour in all_contours:
        area = cv2.contourArea(contour)
        if area < min_area or area > max_area:
            continue
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        if circularity >= circularity_thresh:
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            circle_info = [int(cx), int(cy), int(radius)]
            
            is_duplicate = False
            for existing in found_circles:
                dist = np.sqrt((existing[0] - circle_info[0])**2 + (existing[1] - circle_info[1])**2)
                if dist < radius * 0.5:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                found_circles.append(circle_info)
    
    return found_circles

def extract_circle(image, cx, cy, r, pad=0.45):
    h, w = image.shape[:2]
    r_pad = int(r * (1 + pad))
    x1 = max(0, cx - r_pad)
    y1 = max(0, cy - r_pad)
    x2 = min(w, cx + r_pad)
    y2 = min(h, cy + r_pad)
    crop = image[y1:y2, x1:x2]
    return crop, (x1, y1, x2, y2)

def load_references(orb=None):
    meta = load_metadata()
    if not meta:
        return {}
    if orb is None:
        orb = make_orb()
    references = {}
    for label, info in meta.items():
        front_path = os.path.join(REF_DIR, info['front'])
        back_path = os.path.join(REF_DIR, info['back'])
        front_img = cv2.imread(front_path)
        back_img = cv2.imread(back_path)
        if front_img is None or back_img is None:
            continue
        front_kp, front_desc = compute_orb_features(front_img, orb)
        back_kp, back_desc = compute_orb_features(back_img, orb)
        references[label] = {
            "value": float(info['value']),
            "front_img": front_img,
            "back_img": back_img,
            "front_kp": front_kp,
            "front_desc": front_desc,
            "back_kp": back_kp,
            "back_desc": back_desc
        }
    return references

def identify_coin(crop_img, references, orb=None, match_ratio=0.75, match_threshold=8):
    if orb is None:
        orb = make_orb()
    kp, desc = compute_orb_features(crop_img, orb)
    best_label = None
    best_matches = 0
    details = {}
    for label, info in references.items():
        front_desc = info.get('front_desc')
        back_desc = info.get('back_desc')
        good_front_matches = match_features(desc, front_desc, ratio=match_ratio)
        good_back_matches = match_features(desc, back_desc, ratio=match_ratio)
        score_front = len(good_front_matches) if good_front_matches is not None else 0
        score_back = len(good_back_matches) if good_back_matches is not None else 0
        score = max(score_front, score_back)
        if score > best_matches:
            best_matches = score
            best_label = label
            which = 'front' if score_front >= score_back else 'back'
            details = {"score": score, "front_matches": score_front, "back_matches": score_back, "which": which}
    if best_matches >= match_threshold:
        return best_label, best_matches, details
    return best_label, best_matches, details

class CoinCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Coin Counter Application")
        self.root.geometry("1200x800")
        
        self.scene_img = None
        self.annotated_img = None
        self.counts = {}
        self.total_value = 0.0
        
        self.create_widgets()
        
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.detect_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.detect_frame, text='Detect Coins')
        self.create_detect_tab()
        
        self.register_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text='Register Coin')
        self.create_register_tab()
        
    def create_detect_tab(self):
        control_frame = ttk.Frame(self.detect_frame)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(control_frame, text="Load Scene Image", command=self.load_scene).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Detect Coins", command=self.detect_coins).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Save Annotated Image", command=self.save_annotated).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Save Pie Chart", command=self.save_pie_chart).pack(side='left', padx=5)
        
        method_frame = ttk.LabelFrame(self.detect_frame, text="Detection Method")
        method_frame.pack(fill='x', padx=10, pady=5)
        
        self.detection_method = tk.StringVar(value="hough")
        ttk.Radiobutton(method_frame, text="Hough Circle Detection", variable=self.detection_method, 
                       value="hough", command=self.toggle_parameters).pack(side='left', padx=10, pady=5)
        ttk.Radiobutton(method_frame, text="Contour Detection", variable=self.detection_method, 
                       value="contour", command=self.toggle_parameters).pack(side='left', padx=10, pady=5)
        

        param_frame = ttk.LabelFrame(self.detect_frame, text="Detection Parameters")
        param_frame.pack(fill='x', padx=10, pady=5)
        

        self.hough_frame = ttk.Frame(param_frame)
        self.hough_frame.pack(fill='x')
        
        ttk.Label(self.hough_frame, text="Min Radius:").grid(row=0, column=0, padx=5, pady=5)
        self.min_radius_var = tk.IntVar(value=8)
        ttk.Entry(self.hough_frame, textvariable=self.min_radius_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.hough_frame, text="Max Radius:").grid(row=0, column=2, padx=5, pady=5)
        self.max_radius_var = tk.IntVar(value=200)
        ttk.Entry(self.hough_frame, textvariable=self.max_radius_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(self.hough_frame, text="Param2:").grid(row=0, column=4, padx=5, pady=5)
        self.param2_var = tk.IntVar(value=30)
        ttk.Entry(self.hough_frame, textvariable=self.param2_var, width=10).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(self.hough_frame, text="Match Threshold:").grid(row=0, column=6, padx=5, pady=5)
        self.match_threshold_var = tk.IntVar(value=8)
        ttk.Entry(self.hough_frame, textvariable=self.match_threshold_var, width=10).grid(row=0, column=7, padx=5, pady=5)
        

        self.contour_frame = ttk.Frame(param_frame)
        
        ttk.Label(self.contour_frame, text="Min Area:").grid(row=0, column=0, padx=5, pady=5)
        self.min_area_var = tk.IntVar(value=500)
        ttk.Entry(self.contour_frame, textvariable=self.min_area_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.contour_frame, text="Max Area:").grid(row=0, column=2, padx=5, pady=5)
        self.max_area_var = tk.IntVar(value=50000)
        ttk.Entry(self.contour_frame, textvariable=self.max_area_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(self.contour_frame, text="Circularity:").grid(row=0, column=4, padx=5, pady=5)
        self.circularity_var = tk.DoubleVar(value=0.7)
        ttk.Entry(self.contour_frame, textvariable=self.circularity_var, width=10).grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(self.contour_frame, text="Match Threshold:").grid(row=0, column=6, padx=5, pady=5)
        self.match_threshold_contour_var = tk.IntVar(value=8)
        ttk.Entry(self.contour_frame, textvariable=self.match_threshold_contour_var, width=10).grid(row=0, column=7, padx=5, pady=5)
        

        content_frame = ttk.Frame(self.detect_frame)
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        

        left_frame = ttk.LabelFrame(content_frame, text="Image Display")
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.image_label = ttk.Label(left_frame)
        self.image_label.pack(padx=10, pady=10)
        

        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        

        results_frame = ttk.LabelFrame(right_frame, text="Detection Results")
        results_frame.pack(fill='both', expand=True, pady=5)
        
        self.results_text = tk.Text(results_frame, height=10, width=40)
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_text.config(yscrollcommand=scrollbar.set)
        

        chart_frame = ttk.LabelFrame(right_frame, text="Coin Distribution")
        chart_frame.pack(fill='both', expand=True, pady=5)
        
        self.chart_canvas_frame = chart_frame
        
    def create_register_tab(self):
        form_frame = ttk.LabelFrame(self.register_frame, text="Coin Registration")
        form_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(form_frame, text="Coin Label:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.label_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.label_var, width=30).grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Coin Value:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.value_var = tk.DoubleVar()
        ttk.Entry(form_frame, textvariable=self.value_var, width=30).grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Front Image:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.front_path_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.front_path_var, width=30).grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(form_frame, text="Browse", command=lambda: self.browse_file(self.front_path_var)).grid(row=2, column=2, padx=5)
        
        ttk.Label(form_frame, text="Back Image:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.back_path_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.back_path_var, width=30).grid(row=3, column=1, padx=10, pady=10)
        ttk.Button(form_frame, text="Browse", command=lambda: self.browse_file(self.back_path_var)).grid(row=3, column=2, padx=5)
        
        ttk.Button(form_frame, text="Register Coin", command=self.register_coin).grid(row=4, column=1, pady=20)
        
        list_frame = ttk.LabelFrame(self.register_frame, text="Registered Coins")
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.coins_listbox = tk.Listbox(list_frame, height=15)
        self.coins_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Button(list_frame, text="Refresh List", command=self.refresh_coins_list).pack(pady=5)
        
        self.refresh_coins_list()
        
    def toggle_parameters(self):
        """Toggle between Hough and Contour parameter frames"""
        if self.detection_method.get() == "hough":
            self.contour_frame.pack_forget()
            self.hough_frame.pack(fill='x')
        else:
            self.hough_frame.pack_forget()
            self.contour_frame.pack(fill='x')
        
    def browse_file(self, var):
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)
    
    def load_scene(self):
        filename = filedialog.askopenfilename(
            title="Select Scene Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if filename:
            self.scene_img = cv2.imread(filename)
            if self.scene_img is None:
                messagebox.showerror("Error", "Could not read image file")
                return
            self.display_image(self.scene_img)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Loaded scene image: {os.path.basename(filename)}\n")
    
    def display_image(self, cv_img):
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w = rgb_img.shape[:2]
        max_size = 500
        if h > max_size or w > max_size:
            scale = min(max_size/h, max_size/w)
            new_w, new_h = int(w*scale), int(h*scale)
            rgb_img = cv2.resize(rgb_img, (new_w, new_h))
        
        img_pil = Image.fromarray(rgb_img)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.image_label.configure(image=img_tk)
        self.image_label.image = img_tk
    
    def detect_coins(self):
        if self.scene_img is None:
            messagebox.showwarning("Warning", "Please load a scene image first")
            return
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Detecting coins...\n")
        self.root.update()
        
        try:
            if self.detection_method.get() == "hough":
                self.results_text.insert(tk.END, "Using: Hough Circle Detection\n")
                self.results_text.insert(tk.END, f"Parameters: Min Radius={self.min_radius_var.get()}, Max Radius={self.max_radius_var.get()}, Param2={self.param2_var.get()}\n")
                
                circles = detect_circles_hough(self.scene_img, 
                                              dp=1.2, min_dist=30,
                                              param1=100, param2=self.param2_var.get(),
                                              min_radius=self.min_radius_var.get(),
                                              max_radius=self.max_radius_var.get())
                match_threshold = self.match_threshold_var.get()
                
            else: 
                self.results_text.insert(tk.END, "Using: Contour Detection\n")
                self.results_text.insert(tk.END, f"Parameters: Min Area={self.min_area_var.get()}, Max Area={self.max_area_var.get()}, Circularity={self.circularity_var.get()}\n")
                
                circles = detect_circles_contour(self.scene_img,
                                                min_area=self.min_area_var.get(),
                                                max_area=self.max_area_var.get(),
                                                circularity_thresh=self.circularity_var.get())
                match_threshold = self.match_threshold_contour_var.get()
            
            self.results_text.insert(tk.END, f"Found {len(circles)} circular candidates\n\n")
            
            references = load_references()
            if not references:
                messagebox.showwarning("Warning", "No reference coins registered")
                return
            
            orb = make_orb()
            detections = []
            results = []
            
            for c in circles:
                cx, cy, r = int(c[0]), int(c[1]), int(c[2])
                crop, bbox = extract_circle(self.scene_img, cx, cy, r)
                if crop.size == 0:
                    continue
                
                crop_small = cv2.resize(crop, (200, 200), interpolation=cv2.INTER_AREA)
                label, score, details = identify_coin(crop_small, references, orb=orb,
                                                     match_threshold=match_threshold)
                
                value = references[label]['value'] if label else 0
                detections.append((cx, cy, r))
                results.append({"label": label, "score": score, "details": details, "value": value})
            
            self.annotated_img, self.counts, self.total_value = self.annotate_and_display(
                self.scene_img, detections, results
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Detection failed: {str(e)}")
    
    def annotate_and_display(self, scene_img, detections, results):
        out = scene_img.copy()
        counts = defaultdict(int)
        total_value = 0.0
        
        for det, res in zip(detections, results):
            cx, cy, r = det
            label = res.get('label', 'Unknown')
            value = res.get('value', 0.0)
            score = res.get('score')
            
            cv2.circle(out, (cx, cy), r, (0, 255, 0), 2)
            text = f"{label} (${value:.2f})" if label != 'Unknown' else "Unknown"
            cv2.putText(out, text, (cx - r, cy + r + 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            if label:
                counts[label] += 1
                total_value += value
        
        self.display_image(out)
        
        self.results_text.insert(tk.END, "Detected coins:\n")
        meta = load_metadata()
        for label, count in counts.items():
            coin_value = meta[label]['value']
            self.results_text.insert(tk.END, f"  {count} x {label} (${coin_value} each) = ${count * coin_value:.2f}\n")
        self.results_text.insert(tk.END, f"\nTotal value: ${total_value:.2f}\n")
        
        if counts:
            self.display_pie_chart(counts, total_value)
        
        return out, counts, total_value
    
    def display_pie_chart(self, counts, total_value):
        for widget in self.chart_canvas_frame.winfo_children():
            widget.destroy()
        
        meta = load_metadata()
        labels = []
        sizes = []
        for label, count in counts.items():
            labels.append(f"{label}\n(${meta[label]['value']} each)")
            sizes.append(count)
        
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.set_title(f"Coin Distribution\nTotal Value: ${total_value:.2f}")
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        self.current_chart = fig
    
    def save_annotated(self):
        if self.annotated_img is None:
            messagebox.showwarning("Warning", "No annotated image to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            cv2.imwrite(filename, self.annotated_img)
            messagebox.showinfo("Success", f"Annotated image saved to {filename}")
    
    def save_pie_chart(self):
        if not hasattr(self, 'current_chart'):
            messagebox.showwarning("Warning", "No pie chart to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if filename:
            self.current_chart.savefig(filename, bbox_inches='tight')
            messagebox.showinfo("Success", f"Pie chart saved to {filename}")
    
    def register_coin(self):
        label = self.label_var.get()
        try:
            value = self.value_var.get()
        except:
            messagebox.showerror("Error", "Invalid value")
            return
        
        front_path = self.front_path_var.get()
        back_path = self.back_path_var.get()
        
        if not label or not front_path or not back_path:
            messagebox.showwarning("Warning", "Please fill all fields")
            return
        
        try:
            save_reference(label, value, front_path, back_path)
            messagebox.showinfo("Success", f"Registered {label} with value ${value:.2f}")
            self.refresh_coins_list()
            self.label_var.set("")
            self.value_var.set(0.0)
            self.front_path_var.set("")
            self.back_path_var.set("")
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
    
    def refresh_coins_list(self):
        self.coins_listbox.delete(0, tk.END)
        meta = load_metadata()
        for label, info in meta.items():
            self.coins_listbox.insert(tk.END, f"{label} - ${info['value']:.2f}")

def main():
    root = tk.Tk()
    app = CoinCounterGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()