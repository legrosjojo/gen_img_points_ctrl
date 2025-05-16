import cv2
import numpy as np

def corriger_pixels_errants(image, couleur_cible, couleur_a_corriger, taille_kernel=3):
    mask_cible = np.all(image == couleur_cible, axis=2).astype(np.uint8)
    mask_errant = np.all(image == couleur_a_corriger, axis=2).astype(np.uint8)
    kernel = np.ones((taille_kernel, taille_kernel), np.uint8)
    influence = cv2.dilate(mask_cible, kernel, iterations=1)
    corriger = (mask_errant == 1) & (influence == 1)
    image[corriger] = couleur_cible
    return image

def couleur_predominante_kmeans(image, k=3):
    pixels = image.reshape((-1, 3))
    if len(pixels) == 0:
        return np.array([]), np.array([])
    pixels = np.float32(pixels)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    counts = np.bincount(labels.flatten())
    sorted_idx = np.argsort(counts)[::-1]
    sorted_centers = centers[sorted_idx]
    sorted_counts = counts[sorted_idx]
    return sorted_centers.astype(int), sorted_counts

def couleur_predominante_kmeans_exclure_blanc(image, k=3):
    pixels = image.reshape((-1, 3))
    pixels_filtrés = pixels[np.any(pixels != [255, 255, 255], axis=1)]
    if len(pixels_filtrés) == 0:
        return np.array([]), np.array([])
    pixels_filtrés = np.float32(pixels_filtrés)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels_filtrés, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    counts = np.bincount(labels.flatten())
    sorted_idx = np.argsort(counts)[::-1]
    sorted_centers = centers[sorted_idx]
    sorted_counts = counts[sorted_idx]
    return sorted_centers.astype(int), sorted_counts

def masquer_couleur_dominante_en_blanc(image, dominant_color, seuil=80):
    lower = np.array([max(c - seuil, 0) for c in dominant_color], dtype=np.uint8)
    upper = np.array([min(c + seuil, 255) for c in dominant_color], dtype=np.uint8)
    masque = cv2.inRange(image, lower, upper)
    image[masque > 0] = (255, 255, 255)
    return image

def recolorer_avec_couleurs_fixes(image, couleurs_dominantes, seuil=80):
    couleurs_fixes = [
        (0, 0, 0),      # noir
        (0, 255, 0),    # vert
        (0, 0, 255)     # rouge
    ]
    image_recolorée = np.full_like(image, 255)
    correspondances = []
    couleurs_fixes_utilisées = set()
    for couleur in couleurs_dominantes:
        distances = [np.linalg.norm(np.array(couleur) - np.array(fixe)) if fixe not in couleurs_fixes_utilisées else np.inf for fixe in couleurs_fixes]
        idx_min = np.argmin(distances)
        couleur_proche = couleurs_fixes[idx_min]
        correspondances.append((couleur, couleur_proche))
        couleurs_fixes_utilisées.add(couleur_proche)

    for couleur_source, couleur_cible in correspondances:
        lower = np.array([max(c - seuil, 0) for c in couleur_source], dtype=np.uint8)
        upper = np.array([min(c + seuil, 255) for c in couleur_source], dtype=np.uint8)
        masque = cv2.inRange(image, lower, upper)
        image_recolorée[masque > 0] = couleur_cible

    return image_recolorée

def ameliorer_image(image_path="mire_315a.png", sortie_path="mire_315a_rebuild.png", seuil=80):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image non trouvée : {image_path}")

    dominant_color, _ = couleur_predominante_kmeans(image, k=3)
    dominant_color = dominant_color[0]

    image_modifiee = masquer_couleur_dominante_en_blanc(image.copy(), dominant_color, seuil=seuil)

    couleurs_restantes, counts = couleur_predominante_kmeans_exclure_blanc(image_modifiee, k=3)
    print("Couleurs dominantes restantes (BGR) sans compter le blanc :")
    for i, c in enumerate(couleurs_restantes):
        print(f"{i+1}: {c} (count: {counts[i]})")

    image_recolorée = recolorer_avec_couleurs_fixes(image_modifiee, couleurs_restantes, seuil=seuil)

    image_recolorée = corriger_pixels_errants(image_recolorée, (0, 255, 0), (0, 0, 255))
    image_recolorée = corriger_pixels_errants(image_recolorée, (0, 0, 0), (0, 0, 255))

    cv2.imwrite(sortie_path, image_recolorée)
