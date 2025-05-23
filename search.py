import cv2
import numpy as np
import code
import math

# === PARAMÈTRES ===
distance_init = 5
step_size = 5
max_distance = 100

# === Variables exportables ===
base_mire = []
motifs_data = []
M_transform = []


# === Recherche d'un voisin dans une direction donnée ===
def find_neighbor(center_tab, cx, cy, angle, init_dist=5, step_size=5, max_dist=100):
    angle_rad = math.radians(angle)
    d = init_dist
    while d <= max_dist:
        approx_x = cx + d * math.cos(angle_rad)
        approx_y = cy + d * math.sin(angle_rad)
        for (x, y, motif_type) in center_tab:
            if (x, y) == (cx, cy):
                continue
            if math.hypot(x - approx_x, y - approx_y) < step_size:
                return motif_type
        d += step_size
    return "N"


# === Génération du code d'un motif donné ===
def process_motif(center_tab, index, start_angle):
    motif_x, motif_y, motif_type = center_tab[index]
    neighbors = []
    for i in range(8):
        angle = (i * 45 + start_angle) % 360
        neighbors.append(find_neighbor(center_tab, motif_x, motif_y, angle, distance_init, step_size, max_distance))
    code = str(motif_type) + ''.join(str(n) for n in neighbors)
    return (f"({int(motif_x)}, {int(motif_y)})", code)


# === Génération de la base mire à partir de l'image de référence ===
def generate_base_mire(image, start_angle=0):
    code.center_tab = []
    code.transformed_mire = image
    code.fullContoursProcess(image)
    center_tab = code.center_tab.copy()

    return [
        (coord, code, '', '', '')
        for coord, code in [process_motif(center_tab, i, start_angle) for i in range(len(center_tab))]
    ]


# === Ajout des codes tournés (90°, 180°, 270°) ===
def add_rotated_codes(base_mire):
    updated = []
    for coord, code_0, _, _, _ in base_mire:
        if len(code_0) != 9:
            updated.append((coord, code_0, '', '', ''))
            continue
        M = code_0[0]
        neighbors = code_0[1:]
        code_90 = M + neighbors[2:] + neighbors[:2]
        code_180 = M + neighbors[4:] + neighbors[:4]
        code_270 = M + neighbors[6:] + neighbors[:6]
        updated.append((coord, code_0, code_90, code_180, code_270))
    return updated


# === Calcul de la matrice d'homographie entre motifs transformés et base mire ===
def compute_homography_matrix(base_mire, motifs_data, min_matches=4):
    lookup_dicts = {
        "0": {code: coord for coord, code, _, _, _ in base_mire},
        "90": {code: coord for coord, _, code, _, _ in base_mire},
        "180": {code: coord for coord, _, _, code, _ in base_mire},
        "270": {code: coord for coord, _, _, _, code in base_mire},
    }

    best_angle = None
    best_lookup = None
    best_count = 0

    for angle, lookup in lookup_dicts.items():
        count = sum(1 for _, code in motifs_data if code in lookup)
        print(f"Angle {angle}° : {count} correspondances")
        if count > best_count:
            best_angle = angle
            best_lookup = lookup
            best_count = count

    if best_lookup is None or best_count < min_matches:
        raise RuntimeError("Pas assez de correspondances pour calculer la transformation.")

    print(f"Meilleure orientation : {best_angle}° avec {best_count} correspondances")

    points_transformed = []
    points_reference = []

    for coords_str, code in motifs_data:
        if code in best_lookup:
            x_str, y_str = coords_str.strip('()').split(', ')
            points_transformed.append((int(x_str), int(y_str)))

            coord_str = best_lookup[code]
            x_ref, y_ref = coord_str.strip('()').split(', ')
            points_reference.append((int(x_ref), int(y_ref)))

    pts_trans_np = np.array(points_transformed, dtype=np.float32)
    pts_ref_np = np.array(points_reference, dtype=np.float32)

    M_transform = cv2.findHomography(pts_trans_np, pts_ref_np, cv2.RANSAC, 5.0)[0]
    return M_transform


# === Pipeline principal ===
# === Pipeline principal ===
def run_alignment_pipeline(image_original_path, image_transformed_path):
    img_original = cv2.imread(image_original_path)
    img_transformed = cv2.imread(image_transformed_path)

    if img_original is None:
         print(f"Error: Could not load original image from {image_original_path}")
         return None
    if img_transformed is None:
         print(f"Error: Could not load transformed image from {image_transformed_path}")
         return None

    print("Génération de la base mire à partir de l'image originale...")
    # Ensure code.center_tab is cleared before use in generate_base_mire
    code.center_tab = []
    code.transformed_mire = img_original # Use original image for base mire generation
    # Temporarily disable show/save flags that might pop up windows during base mire gen
    original_show_data = code.show_data.copy()
    original_save_data = code.save_data.copy()
    code.show_data = [False] * len(code.show_data)
    code.save_data = [False] * len(code.save_data)

    base_mire_raw = generate_base_mire(img_original, start_angle=0)
    base_mire = add_rotated_codes(base_mire_raw)

    # Restore original show/save flags
    code.show_data = original_show_data
    code.save_data = original_save_data


    print("Détection des motifs dans l'image transformée...")
    # Ensure code.center_tab is cleared before use
    code.center_tab = []
    code.transformed_mire = img_transformed # Use transformed image for motif detection
    code.fullContoursProcess(img_transformed)
    center_tab_transformed = code.center_tab.copy() # Get the centers found in the transformed image

    # Get the starting angle from red patterns in the transformed image
    starting_angle = code.angleRedPattern(img_transformed)

    # --- Check if angle determination failed ---
    if starting_angle is None:
        print("Error: Could not determine the starting angle of red patterns in the transformed image. Alignment aborted.")
        # Optionally display images before exiting
        cv2.imshow("Original", img_original)
        cv2.imshow("Transformée", img_transformed)
        print("Alignment failed.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return None # Indicate failure

    print(f"Detected starting angle: {starting_angle}°")

    # Process the detected motifs using the determined starting angle
    motifs_data = [process_motif(center_tab_transformed, i, starting_angle) for i in range(len(center_tab_transformed))]

    print("Calculating homography matrix...")
    try:
        M_transform = compute_homography_matrix(base_mire, motifs_data)

        print("Homography transformation matrix:")
        print(M_transform)

        # Apply the homography matrix to align the transformed image to the original
        img_aligned = cv2.warpPerspective(img_transformed, M_transform, (img_original.shape[1], img_original.shape[0]))

        # Display results
        cv2.imshow("Original", img_original)
        cv2.imwrite("data/Original.png", img_original)
        cv2.imshow("Transformee", img_transformed)
        cv2.imwrite("data/Transformee.png", img_transformed)
        cv2.imshow("Alignee", img_aligned)
        cv2.imwrite("data/Alignee.png", img_aligned)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        with open("data/result.txt", "w") as file:
            file.write("-------- ENCODAGE MIRE ORIGINALE --------\n-------- ((x,y),(codage_voisin_0_degree),(codage_voisin_90_degree),(codage_voisin_180_degree),(codage_voisin_270_degree)) --------\n\n")
            for k, v, w, x, y in base_mire:
                file.write(f"{k}, {v}, {w}, {x}, {y}\n")
            file.write("\n\n-------- ENCODAGE MIRE MODIFIEE --------\n-------- ((x,y),(codage_voisin)) --------\n\n")
            for k, v, in motifs_data:
                file.write(f"{k}, {v}\n")
            file.write("\n\n-------- MATRICE DE TRANSFORMATION --------\n")
            file.write(f"{M_transform}\n")

        return M_transform

    except RuntimeError as e:
        print(f"Alignment failed during homography calculation: {e}")
        # Optionally display images before exiting
        cv2.imshow("Original", img_original)
        cv2.imshow("Transformée", img_transformed)
        print("Alignment failed.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return None # Indicate failure


# === Exécution si lancé directement ===
if __name__ == "__main__":
    run_alignment_pipeline("data/mire_rebuild.png", "data/mire_trans_rebuild.png")
