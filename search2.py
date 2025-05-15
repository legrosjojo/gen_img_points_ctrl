import cv2 as cv
import numpy as np
# Assurez-vous que code2.py est dans le même répertoire et contient :
# - fullContoursProcess(image) : Fonction qui détecte les motifs et peuple code2.center_tab (liste de (x, y, type_motif))
# - angleRedPattern(image) : Fonction qui détecte le motif rouge (centre) et retourne son angle
# - Une variable globale code2.center_tab
# - Une variable globale code2.transformed_mire utilisée par fullContoursProcess
import code2
import math

# === PARAMÈTRES ===
image_original_path = "mire_315a.png" # Utilisée principalement pour la taille de sortie
image_transformed_path = "data/trans.png"
distance_init = 5  # Distance de départ pour la recherche de voisins
step_size = 5      # Pas d'augmentation de la distance lors de la recherche de voisins
max_distance = 100  # Limite maximale de recherche de voisins (en pixels)

# === TABLEAUX DE DONNEES MOTEUR (Bases de référence de la mire originale) ===
# Colle ici les listes base_mire_0, base_mire_90, base_mire_180, base_mire_270.

# --- Début de tes listes base_mire_X ---
def generate_base_mire(image, start_angle=0):
    """
    Génère la base de mire avec code_0 uniquement, à partir de l'image fournie.
    """
    import code2
    code2.center_tab = []
    code2.transformed_mire = image
    code2.fullContoursProcess(image)
    center_tab = code2.center_tab.copy()
    
    def find_neighbor(center_tab, cx, cy, angle, init_dist=5, step_size=5, max_dist=100):
        angle_rad = math.radians(angle)
        d = init_dist
        while d <= max_dist:
            approx_x = cx + d * math.cos(angle_rad)
            approx_y = cy + d * math.sin(angle_rad)
            for (x, y, motif_type) in center_tab:
                if (x, y) == (cx, cy):
                    continue
                distance_to_approx_pos = math.hypot(x - approx_x, y - approx_y)
                if distance_to_approx_pos < step_size:
                    return motif_type
            d += step_size
        return "N"

    def process_motif(center_tab, index, start_angle):
        motif_x, motif_y, motif_type = center_tab[index]
        neighbors = []
        for i in range(8):
            angle = (i * 45 + start_angle) % 360
            neighbors.append(find_neighbor(center_tab, motif_x, motif_y, angle))
        code_0 = str(motif_type) + ''.join(str(n) for n in neighbors)
        return (f"({int(motif_x)}, {int(motif_y)})", code_0, '', '', '')

    result = []
    for i in range(len(center_tab)):
        result.append(process_motif(center_tab, i, start_angle))

    return result

def add_rotated_codes(base_mire):
    """
    Complète base_mire avec code_90, code_180, code_270 par décalage du code_0.
    """
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



# --- Fin de tes listes base_mire_X ---


# Liste contenant toutes les bases de mires pour la recherche de l'orientation
all_base_mires = [
    ("0 degrés", base_mire_0),
    ("90 degrés", base_mire_90),
    ("180 degrés", base_mire_180),
    ("270 degrés", base_mire_270)
]

# --- Dictionnaire lookup pour base_mire_0 (pour la correction FINALE) ---
# On le crée juste pour avoir les coordonnées de base_mire_0 si nécessaire pour la correction,
# bien que dans cette approche, on n'aligne pas DIRECTEMENT sur ces points.
# C'est la MÊME lookup que dans la version précédente.
base_mire_0_lookup = {}
for coords_str, code in base_mire_0:
    try:
        x_str, y_str = coords_str.strip('()').split(', ')
        base_mire_0_lookup[code] = (int(x_str), int(y_str))
    except ValueError:
        print(f"Erreur de parsing pour les coordonnées originales dans base_mire_0: {coords_str}")
        continue # Skip this entry


# === CHARGER IMAGES ===
img_original = cv.imread(image_original_path)
img_transformed = cv.imread(image_transformed_path)

if img_original is None:
    print(f"Erreur de chargement de l'image originale: {image_original_path}")
    exit()
if img_transformed is None:
    print(f"Erreur de chargement de l'image transformée: {image_transformed_path}")
    exit()


# === DÉTECTER MOTIFS TRANSFORMÉS ===
print("Détection des motifs dans l'image transformée...")
code2.center_tab = [] # Réinitialise center_tab avant chaque détection
code2.transformed_mire = img_transformed # Définit l'image à traiter dans code2
code2.fullContoursProcess(code2.transformed_mire) # Exécute la détection
center_tab_transformed = code2.center_tab.copy() # Copie les résultats

print(f"Détecté {len(center_tab_transformed)} motifs dans l'image transformée.")

if not center_tab_transformed:
    print("Aucun motif détecté dans l'image transformée.")
    exit()

# === ANGLE DE DÉPART ===
# Utilisé pour orienter la recherche des voisins (directions 0-7) par rapport à la rotation globale de la mire.
# code2.angleRedPattern doit détecter le motif rouge et retourner son angle (par exemple, 0 pour Est, 90 pour Sud, etc.)
starting_angle = code2.angleRedPattern(img_transformed)
print(f"Angle de départ (basé sur motif rouge): {starting_angle}°")


# === RECHERCHE VOISINS ===
# Identique à la version précédente
def find_neighbor(center_tab, cx, cy, angle, init_dist, step_size, max_dist):
    angle_rad = math.radians(angle)
    d = init_dist
    while d <= max_dist:
        approx_x = cx + d * math.cos(angle_rad)
        approx_y = cy + d * math.sin(angle_rad)
        for (x, y, motif_type) in center_tab:
            if (x, y) == (cx, cy):
                continue
            distance_to_approx_pos = math.hypot(x - approx_x, y - approx_y)
            if distance_to_approx_pos < step_size:
                actual_distance = math.hypot(x - cx, y - cy)
                return motif_type, (x, y), actual_distance
        d += step_size
    return "N", None, None # Not found


# === PROCESS MOTIF ===
# Identique à la version précédente
def process_motif(center_tab, index, start_angle):
    if index is None or index < 0 or index >= len(center_tab):
        return None
    motif_x, motif_y, motif_type = center_tab[index]
    neighbor_types = []
    for i in range(8):
        angle = (i * 45 + start_angle) % 360
        neighbor_type, neighbor_coords, dist = find_neighbor(
            center_tab, motif_x, motif_y, angle,
            distance_init, step_size, max_distance
        )
        neighbor_types.append(str(neighbor_type))
    neighbor_code = str(motif_type) + "".join(neighbor_types)
    return (f"({int(motif_x)}, {int(motif_y)})", neighbor_code)


# === PROCESS ALL DETECTED MOTIFS ===
# Génère les codes de voisinage pour tous les motifs détectés dans l'image transformée.
motifs_data = []  # Liste pour stocker les résultats (coordonnées transformées et codes)

print(f"\nProcessing {len(center_tab_transformed)} detected motifs to generate codes...")

for index in range(len(center_tab_transformed)):
    motif_data = process_motif(center_tab_transformed, index, starting_angle)
    if motif_data:
        motifs_data.append(motif_data)

print(f"Finished processing motifs. Generated codes for {len(motifs_data)} points.")


# ==========================================================
# === CALCULER LA TRANSFORMATION EN 2 ÉTAPES ===
# ==========================================================

print("\n--- Début de la recherche de transformation en 2 étapes ---")

# 1. Trouver la meilleure mire de référence (pour l'orientation de l'ENTREE)
best_match_count = 0
best_match_base_mire_name = None
best_match_base_mire_list = None # On stocke la liste entière de la meilleure mire
best_match_original_lookup = None # Dictionnaire lookup pour la meilleure mire

print("Recherche de la meilleure orientation de la mire de référence (pour identifier l'entrée)...")

for mire_name, base_mire_list in all_base_mires:
    current_original_lookup = {}
    for coords_str, code in base_mire_list:
        try:
            x_str, y_str = coords_str.strip('()').split(', ')
            current_original_lookup[code] = (int(x_str), int(y_str))
        except ValueError:
            continue
    current_match_count = 0
    for _, transformed_code in motifs_data:
        if transformed_code in current_original_lookup:
            current_match_count += 1

    # print(f"  Correspondances trouvées pour {mire_name} : {current_match_count}")

    if current_match_count > best_match_count:
        best_match_count = current_match_count
        best_match_base_mire_name = mire_name
        best_match_base_mire_list = base_mire_list # Stocke la liste
        best_match_original_lookup = current_original_lookup # Stocke le lookup

if best_match_count < 4:
    print(f"\nErreur: Seulement {best_match_count} correspondances trouvées avec la meilleure mire ({best_match_base_mire_name}). Nécessite au moins 4 points pour calculer une transformation.")
    exit()
else:
    print(f"\nMeilleure mire de référence trouvée (pour l'entrée): {best_match_base_mire_name} avec {best_match_count} correspondances.")


# 2. Collecter les paires de points (Source -> Cible Temporaire)
# La SOURCE sont les points détectés dans l'image transformée.
# La CIBLE TEMPORAIRE sont les points correspondants dans la *meilleure mire trouvée*.

points_transformed_list = [] # Liste de tuples (xt, yt) des points détectés (Source)
points_best_match_list = []  # Liste de tuples (xo, yo) des points correspondants dans la MEILLEURE MIRE (Cible Temporaire)

print("Collecte des paires de points correspondants (points transformés -> points de la meilleure mire)...")

# On parcourt les motifs détectés dans l'image transformée
for transformed_coords_str, transformed_code in motifs_data:
    # Parser les coordonnées du point détecté
    try:
        xt_str, yt_str = transformed_coords_str.strip('()').split(', ')
        transformed_point = (int(xt_str), int(yt_str))
    except ValueError:
        print(f"Erreur de parsing pour les coordonnées transformées : {transformed_coords_str}")
        continue

    # Chercher le code détecté dans le dictionnaire de la *meilleure* mire trouvée
    if transformed_code in best_match_original_lookup:
        # Si le code est trouvé, le point cible TEMPORAIRE est celui de la meilleure mire
        best_match_point = best_match_original_lookup[transformed_code]

        # Ajouter la paire : point détecté (source) et point dans la meilleure mire (cible TEMPORAIRE)
        points_transformed_list.append(transformed_point)
        points_best_match_list.append(best_match_point)
        # print(f"  Paire temporaire : Transformed {transformed_point} -> Best Match {best_match_point} (Code: {transformed_code})")
    # else:
        # Ce code détecté n'est pas un code valide dans la meilleure mire
        # print(f"  Code {transformed_code} détecté n'a pas de correspondance dans la meilleure mire.")


# Convertir les listes en numpy arrays de type float32
points_transformed_np = np.array(points_transformed_list, dtype=np.float32)
points_best_match_np = np.array(points_best_match_list, dtype=np.float32) # Points dans la meilleure mire

print(f"Collecté {len(points_transformed_np)} paires de points valides (transformés -> meilleure mire) pour le calcul de la première matrice.")

# 3. Calculer la première matrice: Transfomation de l'image transformée vers la meilleure mire.
M_to_best_match = None # Matrice de transformation de l'image transformée vers la meilleure mire

if len(points_transformed_np) < 4:
    print("Erreur: Pas assez de points collectés pour M_to_best_match.")
else:
    if len(points_transformed_np) > 4:
        print("Calcul de M_to_best_match (Homographie) avec RANSAC...")
        M_to_best_match, mask = cv.findHomography(points_transformed_np, points_best_match_np, cv.RANSAC, 5.0)
        if M_to_best_match is not None:
             print(f"M_to_best_match calculée (avec {np.sum(mask)} inliers).")
        else:
             print("cv.findHomography pour M_to_best_match a échoué.")
    else: # Exactement 4 points
        print("Calcul de M_to_best_match avec exactement 4 points...")
        M_to_best_match = cv.getPerspectiveTransform(points_transformed_np, points_best_match_np)
        print("M_to_best_match calculée.")

    if M_to_best_match is not None:
        print(M_to_best_match)
    else:
         print("Le calcul de M_to_best_match a échoué.")


# 4. Calculer la deuxième matrice: Rotation pour aller de la meilleure mire à base_mire_0.
M_correction_rotation = None # Matrice de correction de rotation

if M_to_best_match is not None:
    correction_angle = 0 # Angle de rotation nécessaire pour aller de la meilleure mire à 0 degrés
    if best_match_base_mire_name == "90 degrés":
        correction_angle = 90 # Pour aller de 90 à 0, on tourne de -90 (ou 270)
    elif best_match_base_mire_name == "180 degrés":
        correction_angle = 180 # Pour aller de 180 à 0, on tourne de -180 (ou 180)
    elif best_match_base_mire_name == "270 degrés":
        correction_angle = 270 # Pour aller de 270 à 0, on tourne de -270 (ou 90)

    # Déterminer le centre de rotation. Utilisons le centre de l'image de la mire originale (base_mire_0).
    # Un centre commun approx est (256, 256) ou (255, 255). Prenons (256, 256) pour simplifier.
    center_of_rotation = (img_original.shape[1] // 2, img_original.shape[0] // 2) # Centre de l'image de sortie

    print(f"\nCalcul de la matrice de correction de rotation (-{correction_angle} degrés) autour de {center_of_rotation}...")

    # cv.getRotationMatrix2D donne une matrice 2x3 pour rotation 2D affine
    M_rotation_affine = cv.getRotationMatrix2D(center_of_rotation, correction_angle, 1.0)

    # Convertir la matrice affine 2x3 en matrice 3x3 projective pour pouvoir la multiplier avec une homographie
    M_correction_rotation = np.vstack([M_rotation_affine, [0, 0, 1]]).astype(np.float32)

    print("Matrice de correction de rotation calculée:")
    print(M_correction_rotation)

# 5. Composer les deux matrices: M_final = M_correction_rotation * M_to_best_match
# L'ordre de multiplication est important : on applique d'abord M_to_best_match, puis M_correction_rotation.
M_final = None
if M_to_best_match is not None and M_correction_rotation is not None:
    print("\nComposition des matrices: M_final = M_correction_rotation @ M_to_best_match")
    M_final = M_correction_rotation @ M_to_best_match # Utilise l'opérateur @ pour la multiplication matricielle

    print("Matrice de transformation finale calculée:")
    print(M_final)
else:
    print("\nImpossible de calculer la matrice finale (une des matrices intermédiaires manquait).")


# 6. Appliquer la Transformation Finale
img_aligned = None # Initialise l'image alignée à None

if M_final is not None:
    # L'image de sortie doit avoir la même taille que l'image originale (base_mire_0)
    output_width, output_height = img_original.shape[1], img_original.shape[0]
    output_size = (output_width, output_height) # cv.warpPerspective attend (width, height)

    print(f"\nApplication de la transformation finale à l'image transformée (taille de sortie: {output_size})...")
    img_aligned = cv.warpPerspective(img_transformed, M_final, output_size)

else:
    print("\nLa matrice de transformation finale n'a pas pu être calculée. L'alignement ne sera pas effectué.")


# ==========================================================
# === AFFICHAGE DES RESULTATS ===
# ==========================================================

# 7. Afficher les images pour visualiser le résultat de l'alignement
print("\nAffichage des images : Originale, Transformée d'origine, et Transformée Alignée (vers l'Originale).")

# Affiche l'image originale (la cible)
cv.imshow("Image Originale (Cible de l'alignement)", img_original)

# Affiche l'image transformée telle qu'elle a été chargée initialement
cv.imshow("Image Transformee (Originale chargee)", img_transformed)

# Affiche l'image alignée seulement si le calcul et l'application ont réussi
if img_aligned is not None:
     cv.imshow("Image Transformee Alignee (vers Originale)", img_aligned)

print("Appuyez sur n'importe quelle touche pour fermer les fenêtres d'affichage.")
cv.waitKey(0) # Attend une pression de touche dans une fenêtre OpenCV
cv.destroyAllWindows() # Ferme toutes les fenêtres OpenCV ouvertes

# Optionnel: Sauvegarder l'image alignée sur le disque
#if img_aligned is not None:
#   cv.imwrite("aligned_to_original_mire_2step.png", img_aligned)
#   print("Image alignée sauvegardée sous 'aligned_to_original_mire_2step.png'")

img_mire_originale = cv.imread("mire_315a.png")
base_mire_raw = generate_base_mire(img_mire_originale, start_angle=0)
base_mire_complete = add_rotated_codes(base_mire_raw)

# Affichage exemple :
for entry in base_mire_complete[:5]:
    print(entry)

