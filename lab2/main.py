import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Nikita Malyshev P3312. manual brightness contrast blur grayscale.")
        self.root.geometry("1200x800")

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        self.but1 = tk.Button(self.frame, text="image 1", command=lambda: self.load_image("img/img1.png"))
        self.but1.pack(side="left", padx=10)

        self.but2 = tk.Button(self.frame, text="image 2", command=lambda: self.load_image("img/img2.png"))
        self.but2.pack(side="left", padx=10)

        self.gray_btn = tk.Button(self.frame, text="to gray", command=self.convert_to_gray)
        self.gray_btn.pack(side="left", padx=10)

        self.invert_btn = tk.Button(self.frame, text="invert", command=self.invert)
        self.invert_btn.pack(side="left", padx=10)

        self.save_btn = tk.Button(self.frame, text="save png", command=self.save_image)
        self.save_btn.pack(side="left", padx=10)

        self.brightness_slider = tk.Scale(
            self.root, from_=0.5, to=2.0, resolution=0.1,
            orient="horizontal", label="Brightness",
            command=lambda v: self.apply_enhancements()
        )
        self.brightness_slider.set(1.0)
        self.brightness_slider.pack(fill="x", padx=20, pady=5)

        self.contrast_slider = tk.Scale(
            self.root, from_=0.5, to=2.0, resolution=0.1,
            orient="horizontal", label="Contrast",
            command=lambda v: self.apply_enhancements()
        )
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill="x", padx=20, pady=5)

        self.blur_slider = tk.Scale(
            self.root, from_=0, to=3, resolution=1,
            orient="horizontal", label="Blur Radius",
            command=lambda v: self.apply_enhancements()
        )
        self.blur_slider.set(0)
        self.blur_slider.pack(fill="x", padx=20, pady=5)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill="both", expand=True)

        self.left_block = tk.Frame(self.canvas_frame)
        self.left_block.pack(side="left", fill="both", expand=True)

        self.canvas_original = tk.Canvas(self.left_block, bg="white", height=350)
        self.canvas_original.pack(fill="both", expand=True)

        self.hist_original = tk.Canvas(self.left_block, bg="black", height=150)
        self.hist_original.pack(fill="x")

        self.right_block = tk.Frame(self.canvas_frame)
        self.right_block.pack(side="right", fill="both", expand=True)

        self.canvas_modified = tk.Canvas(self.right_block, bg="white", height=350)
        self.canvas_modified.pack(fill="both", expand=True)

        self.hist_modified = tk.Canvas(self.right_block, bg="black", height=150)
        self.hist_modified.pack(fill="x")

        self.original_image = None
        self.display_image = None
        self.photo_original = None
        self.photo_modified = None

        self.root.bind("<Configure>", self.on_resize)
        self.root.mainloop()

    def load_image(self, path):
        try:
            self.original_image = Image.open(path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Error", f"Не удалось открыть изображение:\n{e}")
            return

        self.display_image = self.original_image.copy()
        self.brightness_slider.set(1.0)
        self.contrast_slider.set(1.0)
        self.blur_slider.set(0)
        self.update_images()

    def update_images(self):
        if self.original_image is None:
            return

        w_left = self.canvas_original.winfo_width()
        h_left = self.canvas_original.winfo_height()
        if w_left > 1 and h_left > 1:
            img_left = self.original_image.copy()
            img_left.thumbnail((w_left, h_left))
            self.photo_original = ImageTk.PhotoImage(img_left)
            self.canvas_original.delete("all")
            self.canvas_original.create_image(
                w_left // 2, h_left // 2, anchor="center", image=self.photo_original
            )
            self.draw_histogram(self.original_image, self.hist_original)

        if self.display_image is None:
            return

        w_right = self.canvas_modified.winfo_width()
        h_right = self.canvas_modified.winfo_height()
        if w_right > 1 and h_right > 1:
            img_right = self.display_image.copy()
            img_right.thumbnail((w_right, h_right))
            self.photo_modified = ImageTk.PhotoImage(img_right)
            self.canvas_modified.delete("all")
            self.canvas_modified.create_image(
                w_right // 2, h_right // 2, anchor="center", image=self.photo_modified
            )
            self.draw_histogram(self.display_image, self.hist_modified)

    def draw_histogram(self, img, canvas):
        canvas.delete("all")
        hist = img.histogram()
        r_hist = hist[0:256]
        g_hist = hist[256:512]
        b_hist = hist[512:768]

        w = canvas.winfo_width()
        h = canvas.winfo_height()

        max_val = max(max(r_hist), max(g_hist), max(b_hist), 1)

        for i in range(256):
            x0 = int(i * w / 256)
            x1 = int((i + 1) * w / 256)
            r_h = int(r_hist[i] / max_val * h)
            g_h = int(g_hist[i] / max_val * h)
            b_h = int(b_hist[i] / max_val * h)
            canvas.create_line(x0, h, x0, h - r_h, fill="red")
            canvas.create_line(x0, h, x0, h - g_h, fill="green")
            canvas.create_line(x0, h, x0, h - b_h, fill="blue")

    def convert_to_gray(self):
        if self.original_image is None:
            return
        gray_pixels = [(avg, avg, avg) for r, g, b in self.original_image.getdata()
                       if (avg := (r + g + b) // 3)]
        gray_image = Image.new("RGB", self.original_image.size)
        gray_image.putdata(gray_pixels)
        self.display_image = gray_image
        self.update_images()

    def invert(self):
        if self.original_image is None:
            return
        inverted_pixels = [(255 - r, 255 - g, 255 - b) for r, g, b in self.original_image.getdata()]
        inverted_image = Image.new("RGB", self.original_image.size)
        inverted_image.putdata(inverted_pixels)
        self.display_image = inverted_image
        self.update_images()

    def save_image(self):
        if self.display_image is None:
            messagebox.showinfo("Save", "Нет изображения для сохранения.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            title="Сохранить как"
        )
        if not file_path:
            return
        try:
            self.display_image.save(file_path, "PNG")
            messagebox.showinfo("Saved", f"Изображение сохранено: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Не удалось сохранить изображение:\n{e}")

    def apply_enhancements(self):
        if self.original_image is None:
            return
        img = self.original_image.copy()
        pixels = list(img.getdata())
        new_pixels = []

        brightness_factor = float(self.brightness_slider.get())
        contrast_factor = float(self.contrast_slider.get())

        for r, g, b in pixels:
            r = int(r * brightness_factor)
            g = int(g * brightness_factor)
            b = int(b * brightness_factor)

            r = int((r - 128) * contrast_factor + 128)
            g = int((g - 128) * contrast_factor + 128)
            b = int((b - 128) * contrast_factor + 128)

            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            new_pixels.append((r, g, b))

        img = Image.new("RGB", img.size)
        img.putdata(new_pixels)

        blur_radius = int(self.blur_slider.get())
        if blur_radius > 0:
            img = self.manual_blur(img, blur_radius)

        self.display_image = img
        self.update_images()

    def manual_blur(self, img, radius):
        pixels = img.load()
        w, h = img.size
        new_img = Image.new("RGB", (w, h))
        new_pixels = new_img.load()

        for x in range(w):
            for y in range(h):
                r_sum = g_sum = b_sum = count = 0
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            r, g, b = pixels[nx, ny]
                            r_sum += r
                            g_sum += g
                            b_sum += b
                            count += 1
                new_pixels[x, y] = (r_sum // count, g_sum // count, b_sum // count)

        return new_img

    def on_resize(self, event):
        self.update_images()


if __name__ == "__main__":
    app = App()
