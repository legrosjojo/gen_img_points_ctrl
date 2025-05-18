from PIL import Image

# Définir les couleurs fixes (RGB)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)

# Fonctions de détection par seuils
def is_white_bg(r, g, b):
    return r > 230 and g > 230 and b > 230

def is_green_dot(r, g, b):
    return g > 180 and r < 100 and b < 100

def is_blueish_ring(r, g, b):
    return b > 150 and g > 100 and r < 120

def is_reddish_dash(r, g, b):
    return r > 180 and g < 180 and b < 180

def recolor_image(input_image_path, output_image_path):
    try:
        original_img = Image.open(input_image_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"Erreur : Le fichier '{input_image_path}' n'a pas été trouvé.")

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
                new_pixels[x, y] = COLOR_WHITE  # Par défaut : fond blanc

    new_img.save(output_image_path)
    print(f"[INFO] Étape 1 : Image recolorée sauvegardée dans '{output_image_path}'")
    return output_image_path

def thicken_shapes(input_image_path, output_image_path):
    try:
        img = Image.open(input_image_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"Erreur : Le fichier '{input_image_path}' pour épaississement n'a pas été trouvé.")

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
    print(f"[INFO] Étape 2 : Image épaissie sauvegardée dans '{output_image_path}'")
    return output_image_path

def ameliorer_image(image_path="data/mire_photo.png", sortie_path="data/mire_rebuild.png"):
    image_intermediaire = "temp_recolor.png"
    path_recolored = recolor_image(image_path, image_intermediaire)
    path_final = thicken_shapes(path_recolored, sortie_path)
    return path_final

# --- Exemple d'utilisation ---
if __name__ == "__main__":
    try:
        ameliorer_image("data/mire_photo.png", "data/mire_rebuild.png")
    except FileNotFoundError as e:
        print(e)
