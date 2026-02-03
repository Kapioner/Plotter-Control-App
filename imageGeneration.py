import torch
import threading
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageTk, ImageOps, ImageDraw
from datetime import datetime
import numpy as np
import cv2
import tkinter as tk
from tkinter import ttk
import time
from multiprocessing.shared_memory import ShareableList

def draw_points_on_image(points, image_pil, point_color=(0, 0, 0), point_size=1):
    if image_pil is None:
        return Image.new('RGB', (512, 512), color='white')

    width, height = image_pil.size

    if points is None or len(points) == 0:
        return Image.new('RGB', (width, height), color='white')

    drawn_image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(drawn_image)

    try:
        transformed_points = points.copy()
        valid_points_indices = (transformed_points[:, 0] >= 0) & (transformed_points[:, 0] < width) & \
                               (transformed_points[:, 1] >= 0) & (transformed_points[:, 1] < height)
        valid_points = transformed_points[valid_points_indices]

        if point_size == 1:
            draw.point([tuple(p) for p in valid_points.astype(int)], fill=point_color)
        else:
            for x, y in valid_points.astype(int):
                x0 = x - point_size // 2
                y0 = y - point_size // 2
                x1 = x + (point_size - point_size // 2)
                y1 = y + (point_size - point_size // 2)
                draw.ellipse([(x0, y0), (x1, y1)], fill=point_color)

        return drawn_image
    except Exception as e:
        print(f"Błąd podczas rysowania punktów: {e}")
        return Image.new('RGB', (width, height), color='red')
def draw_contours_as_lines(list_of_contour_arrays, image_pil, line_color=(0, 0, 0), line_width=1):
    if image_pil is None:
        return Image.new('RGB', (512, 512), color='white')

    width, height = image_pil.size

    if not list_of_contour_arrays:
        return Image.new('RGB', (width, height), color='white')

    drawn_image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(drawn_image)

    try:
        for contour in list_of_contour_arrays:
            if contour is None or len(contour) < 2:
                continue

            image_coords = contour.copy()
            image_coords = image_coords.astype(int)

            points_for_drawing = [(p[0], p[1]) for p in image_coords]

            if len(points_for_drawing) >= 2:
                draw.line(points_for_drawing, fill=line_color, width=line_width)
                draw.line([points_for_drawing[-1], points_for_drawing[0]], fill=line_color, width=line_width)

        return drawn_image
    except Exception as e:
        print(f"Błąd podczas rysowania konturów: {e}")
        return Image.new('RGB', (width, height), color='red')
def generate_and_display(prompt, width, height, kernel, thresh1, thresh2, min_area, device, status_label, frame, max_points,shm_name):
    def _thread():
        s2 = ShareableList(name=shm_name)
        for widget in frame.winfo_children():
            widget.destroy()
        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(frame, maximum=100, variable=progress_var, length=200)
        progress_bar.pack()
        status_label.config(text="Ładowanie modelu...")
        torch_device = {
            "cpu": torch.device("cpu"),
            "cuda": torch.device("cuda"),
            "directml": torch.device("dml") if torch.backends.mps.is_available() else torch.device("cpu")
        }[device]
        pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
        pipe = pipe.to(torch_device)
        num_inference_steps = 50
        start_time = time.time()
        def callback(step, timestep, latents):
            elapsed = time.time() - start_time
            est_total = elapsed / (step + 1) * num_inference_steps
            remaining = est_total - elapsed
            percent = int((step + 1) / num_inference_steps * 100)
            def update_gui():
                progress_var.set(percent)
                progress_bar.update_idletasks()
                status_label.config(text=f"Postęp: {step+1}/{num_inference_steps}, ETA: {int(remaining)}s")
            frame.after(0, update_gui)
        status_label.config(text="Generowanie obrazu...")
        image = pipe(prompt, height=height, width=width, num_inference_steps=num_inference_steps, callback=callback, callback_steps=1).images[0]
        gray = ImageOps.grayscale(image)
        np_gray = np.array(gray)
        kernel_value = kernel if kernel % 2 == 1 else kernel + 1
        blurred = cv2.GaussianBlur(np_gray, (kernel_value, kernel_value), 0)
        edges = cv2.Canny(blurred, thresh1, thresh2)
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_img = np.zeros_like(edges)
        selected_contours = []
        all_points = []
        for cnt in contours:
            if cv2.contourArea(cnt) >= min_area:
                cnt = cnt.squeeze(axis=1)
                if len(cnt.shape) == 1:
                    continue
                cv2.drawContours(contour_img, [cnt], -1, 255, 1)
                selected_contours.append(cnt)
                all_points.extend(cnt)
        all_points_np = np.array(all_points) if all_points else np.empty((0, 2), dtype=int)
        if all_points_np.shape[0] > max_points:
            step = max(1, all_points_np.shape[0] // max_points)
            all_points_np = all_points_np[::step][:max_points]
        np_image_rgb = np.array(image)
        np_image_bgr = cv2.cvtColor(np_image_rgb, cv2.COLOR_RGB2BGR)
        gray_for_direct = cv2.cvtColor(np_image_bgr, cv2.COLOR_BGR2GRAY) 
        _, thresh_for_direct = cv2.threshold(gray_for_direct, 127, 255, cv2.THRESH_BINARY)
        contours_B, _ = cv2.findContours(thresh_for_direct.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_B_color_bgr = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.drawContours(contour_B_color_bgr, contours_B, -1, (255, 255, 255), 1)
        contour_B_pil = Image.fromarray(cv2.cvtColor(contour_B_color_bgr, cv2.COLOR_BGR2RGB))
        plotter_image = Image.new('RGB', image.size, color='white')
        draw_plotter = ImageDraw.Draw(plotter_image)
        PEN_DOWN_DIST_THRESHOLD = 60
        if len(all_points_np) > 1:
            start_idx = np.argmin(all_points_np[:, 0] + (image.size[1] - all_points_np[:, 1]))
            visited = [start_idx]
            unvisited = set(range(len(all_points_np))) - {start_idx}
            current_idx = start_idx
            current_point = tuple(map(int, all_points_np[current_idx]))
            pen_down = True
            while unvisited:
                next_points = all_points_np[list(unvisited)]
                dists = np.linalg.norm(next_points - all_points_np[current_idx], axis=1)
                next_rel_idx = np.argmin(dists)
                next_idx = list(unvisited)[next_rel_idx]
                next_point = tuple(map(int, all_points_np[next_idx]))
                dist = np.linalg.norm(np.array(current_point) - np.array(next_point))
                if dist > PEN_DOWN_DIST_THRESHOLD:
                    pen_down = False  # Podnieś pisak
                else:
                    if pen_down:
                        draw_plotter.line([current_point, next_point], fill=(0, 0, 0), width=1)
                    pen_down = True  # Opuść pisak
                current_point = next_point
                current_idx = next_idx
                visited.append(current_idx)
                unvisited.remove(current_idx)
        end_time = time.time()
        start_str = datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
        end_str = datetime.fromtimestamp(end_time).strftime('%H:%M:%S')
        end_day = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')
        s2[32] = start_str
        s2[33] = end_str
        img_w = width
        img_h = height
        with open("punkty.txt", "w") as f:
            f.write(f"{prompt}\n")
            f.write(f"{start_str}\n")
            f.write(f"{end_str}\n")
            f.write(f"{end_day}\n")
            for pt in all_points_np:
                x_norm = pt[0] / img_w
                y_norm = pt[1] / img_h
                x_robot = -92.5 + x_norm * (36 - -56) + 70
                y_robot = -56 + y_norm * (36 - -56)
                f.write(f"{x_robot:.2f},{y_robot:.2f}\n")
        pil_points = draw_points_on_image(all_points_np, image_pil=image, point_color=(255, 0, 0), point_size=1)
        pil_images = [
            image,
            gray,
            Image.fromarray(contour_img),
            contour_B_pil
        ]
        titles = ["Oryginalny", "Odcienie szarości", "Kontury po przekształceniach", "Kontury bezpośrednio", ]
        for widget in frame.winfo_children():
            widget.destroy()
        for img, title in zip(pil_images, titles):
            f = tk.Frame(frame)
            f.pack(side="left", padx=3)
            tk_img = ImageTk.PhotoImage(img.resize((128, 128)))
            lbl = tk.Label(f, image=tk_img)
            lbl.image = tk_img
            lbl.pack()
            tk.Label(f, text=title).pack()
        status_label.config(text="Gotowe.")
        s2[30] = 1
    threading.Thread(target=_thread).start()