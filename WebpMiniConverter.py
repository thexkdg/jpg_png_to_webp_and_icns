import os
import tkinter.messagebox as mb
import threading
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

__version__ = "1.0.0"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ImageConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Webp Mini Converter - PNG and JPG to Webp, Ico, Icns (by thex.kdg@icloud.com)")
        self.geometry("700x500")
        self.resizable(False, False)

        self.selected_files = []

        # === Button add files ===
        self.add_button = ctk.CTkButton(self, text="Add files", command=self.add_files)
        self.add_button.pack(pady=10)

        # === List files ===
        self.file_listbox = ctk.CTkTextbox(self, height=100)
        self.file_listbox.pack(pady=10, padx=20, fill="both")

        # === Progress bar ===
        self.progress_bar = ctk.CTkProgressBar(master=self, orientation="horizontal")
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # forget by default

        # === Format convert ===
        self.format_menu = ctk.CTkOptionMenu(self, values=["webp", "ico", "icns"])
        self.format_menu.set("webp")
        self.format_menu.pack(pady=10)

        # === Resize block ===
        self.resize_checkbox = ctk.CTkCheckBox(self, text="Resize")
        self.resize_checkbox.pack()

        self.resize_frame = ctk.CTkFrame(self)
        self.resize_frame.pack(pady=5)

        self.width_entry = ctk.CTkEntry(self.resize_frame, placeholder_text="Width")
        self.width_entry.grid(row=0, column=0, padx=5)
        self.height_entry = ctk.CTkEntry(self.resize_frame, placeholder_text="Height (auto)")
        self.height_entry.grid(row=0, column=1, padx=5)

        # === Block Canvas Resize ===
        self.canvas_checkbox = ctk.CTkCheckBox(self, text="Canvas resize")
        self.canvas_checkbox.pack()

        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(pady=5)

        self.canvas_width = ctk.CTkEntry(self.canvas_frame, placeholder_text="Width")
        self.canvas_width.grid(row=0, column=0, padx=5)
        self.canvas_height = ctk.CTkEntry(self.canvas_frame, placeholder_text="Height")
        self.canvas_height.grid(row=0, column=1, padx=5)

        # === Button Convert ===
        self.convert_button = ctk.CTkButton(self, text="Choise dir and Convert", command=self.convert_images)
        self.convert_button.pack(pady=20)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Pictures", "*.png *.jpg *.jpeg")])
        self.selected_files.extend(files)
        self.refresh_file_list()

    def refresh_file_list(self):
        self.file_listbox.delete("0.0", "end")
        for f in self.selected_files:
            self.file_listbox.insert("end", f + "\n")
    def convert_images(self):
        if not self.selected_files:
            print("No choise files.")
            return

        output_dir = filedialog.askdirectory(title="Choise directory")
        if not output_dir:
            return

        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))
        self.update_idletasks()

        # Start in thread
        thread = threading.Thread(
            target=self._process_images_thread,
            args=(output_dir,),
            daemon=True
        )
        thread.start()

    def _process_images_thread(self, output_dir):
        format_selected = self.format_menu.get()
        is_resize = self.resize_checkbox.get()
        is_canvas = self.canvas_checkbox.get()
        total_files = len(self.selected_files)

        for index, file_path in enumerate(self.selected_files):
            try:
                img = Image.open(file_path).convert("RGBA")

                # Resize
                if is_resize:
                    width = self._safe_int(self.width_entry.get(), img.width)
                    height = self._safe_int(self.height_entry.get(), None)
                    if height is None:
                        ratio = img.height / img.width
                        height = int(width * ratio)
                    img = img.resize((width, height), Image.LANCZOS)

                # Canvas
                if is_canvas:
                    canvas_width = self._safe_int(self.canvas_width.get(), img.width)
                    canvas_height = self._safe_int(self.canvas_height.get(), img.height)
                    new_img = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
                    offset_x = (canvas_width - img.width) // 2
                    offset_y = (canvas_height - img.height) // 2
                    new_img.paste(img, (offset_x, offset_y))
                    img = new_img

                # Save
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}.{format_selected}")
                if format_selected == "webp":
                    img.save(output_path, format="WEBP")
                elif format_selected == "ico":
                    img.save(output_path, format="ICO", sizes=[(256, 256)])
                elif format_selected == "icns":
                    img.save(output_path, format="ICNS")

            except Exception as e:
                print(f"Error: {e}")

            # Update after
            progress = (index + 1) / total_files
            self.after(0, lambda p=progress: self.progress_bar.set(p))

        # Ending after
        self.after(100, self._on_processing_done)
    
    # === End ===    
    def _on_processing_done(self):
        self.progress_bar.pack_forget()
        mb.showinfo("Maked!", "All files converted!")

    def _safe_int(self, value, fallback):
        try:
            return int(value)
        except:
            return fallback

if __name__ == "__main__":
    app = ImageConverterApp()
    app.mainloop()
