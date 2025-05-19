from PIL import Image
import numpy as np
from scipy.ndimage import label
import os

# --- Définition des couleurs fixes ---
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)

COLOR_ID_MAP = {
    COLOR_BLACK: 1,
    COLOR_RED: 2,
    COLOR_GREEN: 3
}
ID_COLOR_MAP = {v: k for k, v in COLOR_ID_MAP.items()}

# --- Seuils de détection des couleurs originales ---
def is_white_bg(r, g, b):
    return r > 230 and g > 230 and b > 230

def is_green_dot(r, g, b):
    return g > 180 and r < 100 and b < 100

def is_blueish_ring(r, g, b):
    return b > 150 and g > 100 and r < 120

def is_reddish_dash(r, g, b):
    return r > 180 and g < 180 and b < 180

# --- Étape 1 : Recolorier l'image ---
def recolor_image(input_image_path, output_image_path):
    try:
        original_img = Image.open(input_image_path).convert("RGB")
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{input_image_path}' n'a pas été trouvé.")
        return None

    width, height = original_img.size
    new_img = Image.new("RGB", (width, height))
    original_pixels = original_img.load()
    new_pixels = new_img.load()

    for y in range(height):
        for x in range(width):
            r, g, b = original_pixels[x, y]
            if is_white_bg(r, g, b):
                new_pixels[x, y] = COLOR_WHITE
            elif is_green_dot(r, g, b):
                new_pixels[x, y] = COLOR_GREEN
            elif is_blueish_ring(r, g, b):
                new_pixels[x, y] = COLOR_BLACK
            elif is_reddish_dash(r, g, b):
                new_pixels[x, y] = COLOR_RED
            else:
                new_pixels[x, y] = COLOR_WHITE

    new_img.save(output_image_path)
    return output_image_path

# --- Étape 2 : Épaissir les motifs ---
def thicken_shapes(input_image_path, output_image_path):
    if input_image_path is None:
        return None

    try:
        img = Image.open(input_image_path).convert("RGB")
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{input_image_path}' pour l'épaississement n'a pas été trouvé.")
        return None

    width, height = img.size
    input_pixels = img.load()
    thick_img = img.copy()
    output_pixels = thick_img.load()

    for y in range(height):
        for x in range(width):
            if input_pixels[x, y] == COLOR_WHITE:
                neighbor_colors_found = {
                    "green": False,
                    "black": False,
                    "red": False
                }

                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            neighbor_color = input_pixels[nx, ny]
                            if neighbor_color == COLOR_GREEN:
                                neighbor_colors_found["green"] = True
                            elif neighbor_color == COLOR_BLACK:
                                neighbor_colors_found["black"] = True
                            elif neighbor_color == COLOR_RED:
                                neighbor_colors_found["red"] = True

                if neighbor_colors_found["green"]:
                    output_pixels[x, y] = COLOR_GREEN
                elif neighbor_colors_found["black"]:
                    output_pixels[x, y] = COLOR_BLACK
                elif neighbor_colors_found["red"]:
                    output_pixels[x, y] = COLOR_RED

    thick_img.save(output_image_path)
    return output_image_path

# --- Étape 3 : Nettoyage des motifs par couleur dominante ---
def clean_motifs(input_image_path, output_image_path):
    try:
        img = Image.open(input_image_path).convert("RGB")
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{input_image_path}' pour le nettoyage n'a pas été trouvé.")
        return None

    img_array = np.array(img)
    h, w, _ = img_array.shape

    id_map = np.zeros((h, w), dtype=np.uint8)
    for color, idx in COLOR_ID_MAP.items():
        mask = np.all(img_array == color, axis=2)
        id_map[mask] = idx

    non_white_mask = np.any(img_array != COLOR_WHITE, axis=2)
    structure = np.ones((3, 3), dtype=np.uint8)
    labeled_array, num_features = label(non_white_mask, structure=structure)

    for motif_id in range(1, num_features + 1):
        motif_mask = labeled_array == motif_id
        motif_pixels = id_map[motif_mask]

        if len(motif_pixels) == 0:
            continue

        unique_ids, counts = np.unique(motif_pixels, return_counts=True)
        dominant_id = unique_ids[np.argmax(counts)]
        id_map[motif_mask] = dominant_id

    cleaned_img = np.full((h, w, 3), COLOR_WHITE, dtype=np.uint8)
    for idx, color in ID_COLOR_MAP.items():
        cleaned_img[id_map == idx] = color

    cleaned_pil = Image.fromarray(cleaned_img, "RGB")
    cleaned_pil.save(output_image_path)
    return output_image_path

# --- Fonction principale attendue par les autres scripts ---
def ameliorer_image(image_path="data/mire_photo.png", sortie_path="data/mire_rebuild.png"):
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    recolored_path = f"temp/{base_name}_recolor.png"
    thickened_path = f"temp/{base_name}_thick.png"
    final_output_path = sortie_path

    os.makedirs("temp", exist_ok=True)

    path1 = recolor_image(image_path, recolored_path)
    path2 = thicken_shapes(path1, thickened_path)
    if path2:
        clean_motifs(path2, final_output_path)
    
    for path in [recolored_path, thickened_path]:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Erreur lors de la suppression de {path} : {e}")
