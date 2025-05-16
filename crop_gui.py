import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

selected_points = []

CROP_WIDTH = 512
CROP_HEIGHT = 512
IMAGE_PATH = "photo_color.png"


class CropApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sélection 4 points pour crop")
        self.geometry("800x600")  # taille initiale fenêtre
        
        # Chargement image
        self.img_cv_orig = cv2.imread(IMAGE_PATH)
        self.img_cv_orig = cv2.cvtColor(self.img_cv_orig, cv2.COLOR_BGR2RGB)
        self.img_pil_orig = Image.fromarray(self.img_cv_orig)
        self.img_width_orig, self.img_height_orig = self.img_pil_orig.size
        
        # Canvas qui prendra toute la place disponible
        self.canvas = ctk.CTkCanvas(self, bg="black")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.label = ctk.CTkLabel(self, text="Cliquez sur 4 points (dans l'ordre).")
        self.label.pack(pady=5)
        
        self.btn_reset = ctk.CTkButton(self, text="Réinitialiser", command=self.reset_points)
        self.btn_reset.pack(side="left", padx=10, pady=10)
        
        self.btn_crop = ctk.CTkButton(self, text="Rogner et sauver", command=self.crop_and_save)
        self.btn_crop.pack(side="right", padx=10, pady=10)
        self.btn_crop.configure(state="disabled")
        
        self.circles = []
        self.polygon = None
        self.mask_overlay = None

        
        # Variables pour l'image affichée et son échelle
        self.tk_img = None
        self.img_width = None
        self.img_height = None
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        # Bind pour clic souris et redimensionnement fenêtre
        self.canvas.bind("<Button-1>", self.on_click)
        self.bind("<Configure>", self.on_resize)
        
        # Affichage initial
        self.update_image()
    
    def update_image(self):
        # Récupérer taille canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:
            # taille pas encore initialisée, attendre
            self.after(100, self.update_image)
            return
        
        # Calcul scale pour garder ratio
        scale_w = canvas_width / self.img_width_orig
        scale_h = canvas_height / self.img_height_orig
        scale = min(scale_w, scale_h)
        
        # Nouvelle taille image
        self.img_width = int(self.img_width_orig * scale)
        self.img_height = int(self.img_height_orig * scale)
        
        self.scale_x = self.img_width_orig / self.img_width
        self.scale_y = self.img_height_orig / self.img_height
        
        # Redimensionner l'image PIL
        img_resized = self.img_pil_orig.resize((self.img_width, self.img_height), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img_resized)
        
        self.canvas.delete("all")
        # Afficher image au centre du canvas
        x = (canvas_width - self.img_width) // 2
        y = (canvas_height - self.img_height) // 2
        self.image_on_canvas = self.canvas.create_image(x, y, anchor="nw", image=self.tk_img)
        
        # Redessiner les points déjà sélectionnés avec ajustement échelle et décalage
        for circle in self.circles:
            self.canvas.delete(circle)
        self.circles.clear()
        
        for pt in selected_points:
            # Ajuster point en fonction scale et position image
            px = int(pt[0] / self.scale_x + x)
            py = int(pt[1] / self.scale_y + y)
            r = 5
            c = self.canvas.create_oval(px - r, py - r, px + r, py + r, fill="red")
            self.circles.append(c)
        if len(selected_points) == 4:
            self.draw_polygon_and_mask()

    
    def on_click(self, event):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_img_pos = (canvas_width - self.img_width) // 2
        y_img_pos = (canvas_height - self.img_height) // 2
        
        # Vérifier que le clic est sur l'image
        if not (x_img_pos <= event.x <= x_img_pos + self.img_width and
                y_img_pos <= event.y <= y_img_pos + self.img_height):
            return
        
        if len(selected_points) < 4:
            # Convertir coord canvas -> coord image originale
            x_orig = (event.x - x_img_pos) * self.scale_x
            y_orig = (event.y - y_img_pos) * self.scale_y
            
            selected_points.append((x_orig, y_orig))
            
            # Dessiner cercle au bon endroit
            r = 5
            c = self.canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, fill="red")
            self.circles.append(c)
            
            if len(selected_points) == 4:
                self.label.configure(text="4 points sélectionnés, cliquez sur 'Rogner et sauver'")
                self.btn_crop.configure(state="normal")
                self.draw_polygon_and_mask()

    
    def reset_points(self):
        global selected_points
        selected_points = []
        for c in self.circles:
            self.canvas.delete(c)
        self.circles.clear()
        self.label.configure(text="Cliquez sur 4 points (dans l'ordre).")
        self.btn_crop.configure(state="disabled")
        if self.polygon:
            self.canvas.delete(self.polygon)
            self.polygon = None
        if self.mask_overlay:
            self.canvas.delete(self.mask_overlay)
            self.mask_overlay = None

    
    def crop_and_save(self):
        global selected_points
        if len(selected_points) != 4:
            self.label.configure(text="Veuillez sélectionner exactement 4 points.")
            self.destroy()
            return
        
        pts_src = np.array(selected_points, dtype=np.float32)
        pts_dst = np.array([
            [0, 0],
            [CROP_WIDTH - 1, 0],
            [CROP_WIDTH - 1, CROP_HEIGHT - 1],
            [0, CROP_HEIGHT - 1]
        ], dtype=np.float32)
        
        M = cv2.getPerspectiveTransform(pts_src, pts_dst)
        img_cropped = cv2.warpPerspective(self.img_cv_orig, M, (CROP_WIDTH, CROP_HEIGHT))
        cv2.imwrite("mire_315a.png", cv2.cvtColor(img_cropped, cv2.COLOR_RGB2BGR))
        
        self.label.configure(text="Image rognée sauvegardée sous 'mire_315a.png'")
        self.btn_crop.configure(state="disabled")
        self.destroy()

    def draw_polygon_and_mask(self):
        if len(selected_points) != 4:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_img_pos = (canvas_width - self.img_width) // 2
        y_img_pos = (canvas_height - self.img_height) // 2

        # Convertir les points image -> canvas
        points_canvas = []
        for pt in selected_points:
            px = int(pt[0] / self.scale_x + x_img_pos)
            py = int(pt[1] / self.scale_y + y_img_pos)
            points_canvas.append((px, py))

        # Tracer le polygone (fermé)
        if self.polygon:
            self.canvas.delete(self.polygon)
        self.polygon = self.canvas.create_line(*points_canvas, *points_canvas[:1], fill="green", width=2)

        # Masque gris semi-transparent
        if self.mask_overlay:
            self.canvas.delete(self.mask_overlay)

        # Créer une image noire avec alpha
        mask = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 150))
        mask_draw = Image.new("L", (canvas_width, canvas_height), 0)

        import PIL.ImageDraw as ImageDraw
        draw = ImageDraw.Draw(mask_draw)
        draw.polygon(points_canvas, fill=255)  # Dessine zone de sélection en blanc

        # Convertir en array numpy pour masque alpha
        np_mask = np.array(mask)
        alpha_mask = np.array(mask_draw)
        np_mask[..., 3] = 150 - (alpha_mask // 2)  # Transparence inverse dans la zone sélectionnée

        final_mask = Image.fromarray(np_mask)
        self.tk_mask = ImageTk.PhotoImage(final_mask)
        self.mask_overlay = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_mask)


    def on_resize(self, event):
        # Mise à jour de l'image redimensionnée
        self.update_image()


if __name__ == "__main__":
    app = CropApp()
    app.mainloop()
