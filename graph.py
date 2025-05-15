import sys
import os
import tkinter as tk
import customtkinter
import cv2 as cv
import numpy as np
from PIL import Image
import code2
import search

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
        self.title("Projet Ingénieur Groupe 3")
        self.geometry("1200x700")

        # === FRAME PRINCIPAL ===
        self.left_frame = customtkinter.CTkFrame(self, width=350)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.right_frame = customtkinter.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.image_label = customtkinter.CTkLabel(self.right_frame, text="Image")
        self.image_label.pack(fill="both", expand=True)

        self.validate_button = customtkinter.CTkButton(self.right_frame, text="Validate", command=self.confirm_transformed_image, state="disabled")
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

        # Empêche l'interaction tant que mire_315a.png n'est pas validée
        self.disable_controls()

        # Affiche la première image avec demande de validation
        self.show_image_confirmation("mire_315a.png", "Confirmer l'image de base ?", self.enable_controls, is_first_popup=True)

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
        for entry in self.entry_vars.values():
            entry.set("")
        self.validate_button.configure(state="disabled")

    def enable_controls(self):
        img = cv.imread("mire_315a.png")
        if img is None:
            raise ValueError("Erreur de chargement de l'image mire_315a.png")
        search.generate_base_mire(img)
        search.add_rotated_codes(search.motifs_data)

        for slider in self.sliders.values():
            slider.configure(state="normal")
        self.validate_button.configure(state="normal")
        self.original_image = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.update_image()

    def confirm_transformed_image(self):
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

        img = self.apply_transformations(self.original_image, *t, *r)
        os.makedirs("data", exist_ok=True)
        cv.imwrite("data/trans.png", cv.cvtColor(img, cv.COLOR_RGB2BGR))
        self.show_image_confirmation("data/trans.png", "Valider l'image transformée ?", self.run_final_processing)

    def show_image_confirmation(self, path, message, on_confirm_callback, is_first_popup=False):
        overlay = customtkinter.CTkToplevel(self)
        overlay.title("Confirmation requise")
        overlay.geometry(f"700x500+{(overlay.winfo_screenwidth() - 700) // 2}+{(overlay.winfo_screenheight() - 500) // 2}")
        overlay.grab_set()

        container = customtkinter.CTkFrame(overlay)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = customtkinter.CTkFrame(container)
        left_frame.pack(side="left", fill="both", expand=True)

        img = Image.open(path)
        img.thumbnail((350, 380))
        ctk_img = customtkinter.CTkImage(img, size=img.size)
        label_img = customtkinter.CTkLabel(left_frame, image=ctk_img)
        label_img.image = ctk_img
        label_img.pack(pady=10)

        label_msg = customtkinter.CTkLabel(left_frame, text=message)
        label_msg.pack(pady=5)

        if is_first_popup:
            right_frame = customtkinter.CTkFrame(container, width=200)
            right_frame.pack(side="left", fill="y", padx=20)

            customtkinter.CTkLabel(right_frame, text="Couleurs prédominantes", font=("Roboto", 14)).pack(pady=10)

            global dominant_colors

            self.color_boxes = []
            self.color_labels = []

            for color in dominant_colors:
                box = customtkinter.CTkFrame(right_frame, width=80, height=80, fg_color="gray")
                box.pack(pady=10)
                box.pack_propagate(False)

                hex_color = '#%02x%02x%02x' % color
                box.configure(fg_color=hex_color)

                label = customtkinter.CTkLabel(right_frame, text=f"R: {color[0]}  G: {color[1]}  B: {color[2]}")
                label.pack()

                self.color_boxes.append(box)
                self.color_labels.append(label)

        btn_frame = customtkinter.CTkFrame(overlay)
        btn_frame.pack(pady=10)
        customtkinter.CTkButton(btn_frame, text="Valider", command=lambda: [overlay.destroy(), on_confirm_callback()]).pack(side="left", padx=10)
        customtkinter.CTkButton(btn_frame, text="Annuler", command=self.quit_app if is_first_popup else overlay.destroy).pack(side="right", padx=10)


    def quit_app(self):
        self.destroy()
        sys.exit()

    def run_final_processing(self):
        # Ici tu peux appeler ta fonction principale si besoin
        #search.main()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = CustomGUI()
    app.mainloop()
