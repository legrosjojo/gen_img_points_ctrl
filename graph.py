import sys
import os
import cv2 as cv
import numpy as np
from PIL import Image

import tkinter as tk
import customtkinter

import crop_gui
import code2
import search
import capture

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")

# Variables globales pour les 3 couleurs dominantes (RGB)
dominant_colors = [
    (255, 0, 0),   # rouge
    (0, 255, 0),   # vert
    (0, 0, 0),     # noir
]

class CustomGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Projet FIP Ingénieur Groupe 3")
        self.geometry("1200x560")

        # === FRAME PRINCIPAL ===
        self.left_frame = customtkinter.CTkFrame(self, width=350)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.right_frame = customtkinter.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.image_label = customtkinter.CTkLabel(self.right_frame, text="Image")
        self.image_label.pack(fill="both", expand=True)

        self.validate_button = customtkinter.CTkButton(self.right_frame, text="Validate", command=self.run_final_processing, state="disabled")
        self.validate_button.pack(pady=10)

        self.pil_image = None
        self.photo = None

        # Création cadre horizontal pour sliders et checkboxes
        controls_frame = customtkinter.CTkFrame(self.left_frame)
        controls_frame.pack(fill="both", expand=True)

        # Cadre sliders à gauche
        self.sliders_frame = customtkinter.CTkFrame(controls_frame)
        self.sliders_frame.pack(side="left", fill="y", padx=(0,20))

        # Cadre checkboxes à droite
        self.checkboxes_frame = customtkinter.CTkFrame(controls_frame)
        self.checkboxes_frame.pack(side="left", fill="y")

        self.create_sliders()
        self.create_checkboxes()

        # Empêche l'interaction tant que mire_315a.png n'est pas chargée
        self.disable_controls()

        # Chargement automatique et activation
        self.load_base_image_and_enable_controls()

    def create_sliders(self):
        slider_params = [
            ("Translation X", -512, 512, 200),
            ("Translation Y", -512, 512, 200),
            ("Translation Z (Zoom)", -250, 250, 200),
            ("Rotation X", -180, 180, 360),
            ("Rotation Y", -180, 180, 360),
            ("Rotation Z", -180, 180, 360),
        ]
        self.sliders = {}
        self.entry_vars = {}
        for label, min_val, max_val, step in slider_params:
            frame = customtkinter.CTkFrame(self.sliders_frame)
            frame.pack(fill="x", pady=5)
            customtkinter.CTkLabel(frame, text=label).pack(anchor="w")
            slider = customtkinter.CTkSlider(frame, from_=min_val, to=max_val, number_of_steps=step, command=self.update_slider_value)
            slider.pack(fill="x")
            entry_var = tk.StringVar()
            entry = customtkinter.CTkEntry(frame, textvariable=entry_var)
            entry.pack(fill="x")
            entry.bind("<Return>", lambda e, l=label: self.update_entry_value(l))
            self.sliders[label] = slider
            self.entry_vars[label] = entry_var
            entry_var.set(str(slider.get()))

    def create_checkboxes(self):
        self.show_data_vars = []
        self.save_data_vars = []

        # Show Data frame
        self.show_data_frame = customtkinter.CTkFrame(self.checkboxes_frame)
        self.show_data_frame.pack(pady=10, fill="x")
        customtkinter.CTkLabel(self.show_data_frame, text="Show Data").pack(anchor="w")
        for i, label in enumerate(["Original Image", "Transformed Image", "Mask", "HSV", "Grey", "Threshold", "Contours", "Contours Min Rouge"]):
            var = tk.BooleanVar(value=code2.show_data[i])
            cb = customtkinter.CTkCheckBox(self.show_data_frame, text=label, variable=var)
            cb.pack(anchor="w")
            self.show_data_vars.append(var)

        # Save Data frame
        self.save_data_frame = customtkinter.CTkFrame(self.checkboxes_frame)
        self.save_data_frame.pack(pady=10, fill="x")
        customtkinter.CTkLabel(self.save_data_frame, text="Save Data").pack(anchor="w")
        for i, label in enumerate(["Parameters", "Original Image", "Transformed Image", "Mask", "HSV", "Grey", "Threshold", "Contours", "Contours Min Rouge"]):
            var = tk.BooleanVar(value=code2.save_data[i])
            cb = customtkinter.CTkCheckBox(self.save_data_frame, text=label, variable=var)
            cb.pack(anchor="w")
            self.save_data_vars.append(var)

    def update_slider_value(self, value):
        for label, slider in self.sliders.items():
            self.entry_vars[label].set(f"{slider.get():.2f}")
        self.update_image()

    def update_entry_value(self, label):
        try:
            value = float(self.entry_vars[label].get())
            self.sliders[label].set(value)
            self.update_image()
        except ValueError:
            pass

    def update_image(self):
        if hasattr(self, 'original_image'):
            t = [
                self.sliders["Translation X"].get(),
                self.sliders["Translation Y"].get(),
                self.sliders["Translation Z (Zoom)"].get(),
            ]
            r = [self.sliders[f"Rotation {a}"].get() for a in "XYZ"]
            transformed = self.apply_transformations(self.original_image, *t, *r)
            self.pil_image = Image.fromarray(cv.cvtColor(transformed, cv.COLOR_RGB2RGBA))
            self.photo = customtkinter.CTkImage(self.pil_image, size=(self.pil_image.width, self.pil_image.height))
            self.image_label.configure(image=self.photo, text="")
            self.image_label.image = self.photo

    def apply_transformations(self, image, t_x, t_y, t_z, r_x, r_y, r_z):
        nrows, ncols = image.shape[:2]
        t = code2.tz_rxy() @ code2.translationXYZ(t_x, t_y, t_z) @ code2.rotationXYZBis(r_x, r_y, r_z)
        H = code2._3Dto2D() @ t @ code2._2Dto3D()
        return cv.warpPerspective(image, H, (ncols, nrows), None, borderValue=(255, 255, 255))

    def disable_controls(self):
        for slider in self.sliders.values():
            slider.configure(state="disabled")
        for entry_var in self.entry_vars.values():
            entry_var.set("")
        self.validate_button.configure(state="disabled")

    def enable_controls(self):
        img = cv.imread("data/mire_315a.png")
        search.base_mire_raw = search.generate_base_mire(img, start_angle=0)
        search.base_mire = search.add_rotated_codes(search.base_mire_raw)
        if img is None:
            raise ValueError("Erreur de chargement de l'image mire_315a.png")


        for slider in self.sliders.values():
            slider.configure(state="normal")
        self.validate_button.configure(state="normal")
        self.original_image = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.update_image()

    def load_base_image_and_enable_controls(self):
        # Charge l'image de base et active les contrôles automatiquement sans popup
        try:
            self.enable_controls()
        except Exception as e:
            print(f"Erreur lors du chargement de l'image de base : {e}")
            self.quit_app()

    def run_final_processing(self):
        # Récupération des paramètres
        t = [
            self.sliders["Translation X"].get(),
            self.sliders["Translation Y"].get(),
            self.sliders["Translation Z (Zoom)"].get(),
        ]
        r = [self.sliders[f"Rotation {a}"].get() for a in "XYZ"]
        code2.t_x, code2.t_y, code2.t_z = t
        code2.r_x, code2.r_y, code2.r_z = r
        code2.show_data = [v.get() for v in self.show_data_vars]
        code2.save_data = [v.get() for v in self.save_data_vars]

        # Applique la transformation et sauvegarde l'image transformée
        img = self.apply_transformations(self.original_image, *t, *r)
        #os.makedirs("data", exist_ok=True)
        cv.imwrite("data/mire_trans.png", cv.cvtColor(img, cv.COLOR_RGB2BGR))
        self.destroy()
        capture.process_capture("data/mire_trans.png", "data/mire_photo.png")
        crop_gui.bool_second=False
        crop_gui.main_crop_gui()
        rebuild.ameliorer_image("data/mire_trans_crop.png", "data/mire_trasn_rebuild.png")

        # Exécute la pipeline d'alignement sans popup
        search.run_alignment_pipeline("mire_rebuild.png", "data/mire_trans_rebuild.png")

        # Fin de l'application
        self.destroy()
        sys.exit()

    def quit_app(self):
        self.destroy()
        sys.exit()

def main_graph():
    app = CustomGUI()
    app.mainloop()

if __name__ == "__main__":
    app = CustomGUI()
    app.mainloop()
