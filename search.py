import cv2 as cv
import numpy as np
import code2  # Assurez-vous que c'est le bon nom de votre fichier
import math

# Charge l'image originale (avant transformation)
img_original = cv.imread("mire_315a.png")  # Chemin vers l'image originale

# S'assure que l'image est bien chargée
if img_original is None:
    print("Erreur: Impossible de charger l'image originale.")
    exit()

# Détecte les motifs dans l'image originale
code2.center_tab = []  # Vide la liste précédente
code2.transformed_mire = img_original
code2.fullContoursProcess(code2.transformed_mire)  # Remplit la liste
center_tab_original = code2.center_tab.copy() #Copie les centres originaux

def estimate_average_distance(img, center_tab):
    """Estime la distance moyenne entre les centres des motifs voisins."""
    distances = []
    for i in range(len(center_tab)):
        for j in range(i + 1, len(center_tab)): # Eviter de recalculer les distances et comparer un point avec lui-même
            x1, y1, _ = center_tab[i]
            x2, y2, _ = center_tab[j]
            distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            distances.append(distance)
    if distances:
        return sum(distances) / len(distances)  # Retourne la moyenne
    else:
        return 0 #Retourne 0 si la liste est vide

d_ref = estimate_average_distance(img_original, center_tab_original) #distance de référence

# Charge l'image transformée
img_transformed = cv.imread("data/trans.png") # Remplacez le chemin si nécessaire

# S'assure que l'image est bien chargée
if img_transformed is None:
    print("Erreur: Impossible de charger l'image transformée.")
    exit()

# Détecte les motifs dans l'image transformée
code2.center_tab = []  # Vide la liste précédente
code2.transformed_mire = img_transformed
code2.fullContoursProcess(code2.transformed_mire)  # Remplit la liste
center_tab_transformed = code2.center_tab.copy() #Copie les centres transformés

#Estimer le facteur d'échelle
def estimate_scale_factor(img_original, img_transformed, center_tab_original, center_tab_transformed, reference_motif_index=0):
    """Estime le facteur d'échelle en comparant les distances entre des motifs de référence."""

    # S'assurer qu'il y a des motifs pour estimer
    if not center_tab_original or not center_tab_transformed:
        print("Erreur: Les listes de centres de motifs sont vides.")
        return 1.0  # Retourner 1.0 pour éviter de casser le code

    # Coordonnées du motif de référence dans l'image originale
    x_ref_orig, y_ref_orig, _ = center_tab_original[reference_motif_index]

    scale_factors = []

    # Boucler à travers les autres motifs pour calculer le facteur d'échelle
    for i in range(1, len(center_tab_original)):
        # S'assurer que l'index est valide dans transformed
        if i < len(center_tab_transformed):
            # Coordonnées dans l'image originale et transformée
            x_orig, y_orig, _ = center_tab_original[i]
            x_trans, y_trans, _ = center_tab_transformed[i]

            # Calculer les distances
            d_orig = math.sqrt((x_orig - x_ref_orig) ** 2 + (y_orig - y_ref_orig) ** 2)
            d_trans = math.sqrt((x_trans - x_ref_orig) ** 2 + (y_trans - y_ref_orig) ** 2)

            # Calculer le facteur d'échelle
            if d_orig > 0:  # Éviter la division par zéro
                scale_factor = d_trans / d_orig
                scale_factors.append(scale_factor)

    # Calculer le facteur d'échelle moyen
    if scale_factors:
        scale_factor_avg = sum(scale_factors) / len(scale_factors)
        return scale_factor_avg
    else:
        return 1.0

scale_factor = estimate_scale_factor(img_original, img_transformed, center_tab_original, center_tab_transformed)

print(f"Facteur d'échelle estimé: {scale_factor}") #Confirmer la valeur

#Calcule la distance de recherche ajustée
search_distance = d_ref * scale_factor

# Crée une copie de l'image transformée pour visualiser les résultats
img_copy = img_transformed.copy()  # Créer une copie de img, et non de transformed_img

def main_avec_sequence(img, center_tab, search_distance, angle_tolerance, starting_angle):
    """Fonction main avec séquence de touches pour le débogage."""
    # Étape 1: Trouver le motif près du centre
    image_height, image_width = img.shape[:2]
    center_x = image_width // 2
    center_y = image_height // 2
    best_motif = None
    min_distance = float('inf')
    max_distance_from_center_ratio = 0.2  # Ajuster selon vos besoins

    for x, y, motif_type in center_tab:
        distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        if distance < min_distance and distance < min(image_width, image_height) * max_distance_from_center_ratio:
            min_distance = distance
            best_motif = (x, y, motif_type)

    if best_motif is None:
        print("Aucun motif trouvé dans center_tab.")
        return

    motif_x, motif_y, motif_type = best_motif

    # Dessiner le centre du motif
    cv.circle(img_copy, (int(motif_x), int(motif_y)), 5, (255, 0, 0), -1)  # Bleu
    cv.imshow("Image", img_copy)
    print(f"Centre : {(motif_x, motif_y)}, Type : {motif_type}")
    wait_for_key('h')

    # Étape 2: Trouver les 8 voisins
    neighbor_types = []
    for i in range(8): #Boucle de 0 à 7
        angle = (i * 45 + starting_angle) % 360  # Calculer l'angle en tenant compte de starting_angle
        print(f"Recherche à l'angle: {angle}")
        neighbor_type, neighbor_coords = find_neighbor_in_direction_optimized(img, center_tab, motif_x, motif_y, angle, search_distance, angle_tolerance)
        neighbor_types.append(neighbor_type)

        # Dessiner une ligne vers le voisin (ou là où on s'attend à le trouver)
        angle_rad = math.radians(angle)
        approx_neighbor_x = motif_x + search_distance * math.cos(angle_rad)
        approx_neighbor_y = motif_y + search_distance * math.sin(angle_rad)

        if neighbor_type is not None:
           # Ajout d'un print de débogage pour voir les informations trouvées par le code
           print(f"Voisin trouvé: Type={neighbor_type}, Coords=({neighbor_coords[0]},{neighbor_coords[1]})")
           cv.line(img_copy, (int(motif_x), int(motif_y)), (int(neighbor_coords[0]), int(neighbor_coords[1])), (0, 255, 0), 2)  # Vert (vers le voisin réel)
           cv.circle(img_copy, (int(neighbor_coords[0]), int(neighbor_coords[1])), 5, (0,0,255), -1)
        else:
            cv.line(img_copy, (int(motif_x), int(motif_y)), (int(approx_neighbor_x), int(approx_neighbor_y)), (0, 0, 255), 2)  # Rouge (si aucun voisin trouvé)
            print("Pas de voisin trouvé.")

        cv.imshow("Image", img_copy)
        wait_for_key('h')

    # Étape 3: Générer le code de voisinage
    neighbor_code = "".join([str(n) if n is not None else "N" for n in neighbor_types])

    print(f"Code de voisinage: {neighbor_code}")
    print("Fin du processus.")
    wait_for_key('h')

    cv.destroyAllWindows()

def find_neighbor_in_direction_optimized(img, center_tab, center_x, center_y, angle, search_distance, angle_tolerance):
    """Recherche le voisin dans une direction donnée avec tolérance angulaire."""
    best_neighbor_type = None
    closest_neighbor_coords = None  # Ajouter pour enregistrer les coordonnées du meilleur voisin.
    min_distance = float('inf')

    for a in np.arange(angle - angle_tolerance, angle + angle_tolerance + 0.1, 0.1):
        # Calculer la position approximative du voisin
        angle_rad = math.radians(a)
        approx_neighbor_x = center_x + search_distance * math.cos(angle_rad)
        approx_neighbor_y = center_y + search_distance * math.sin(angle_rad)

        # Trouver le voisin le plus proche dans center_tab
        for x, y, motif_type in center_tab:
            distance = math.sqrt((x - approx_neighbor_x)**2 + (y - approx_neighbor_y)**2)
            if distance < min_distance:#La condition de distance est enlevée
                min_distance = distance
                best_neighbor_type = motif_type
                closest_neighbor_coords = (x, y)  # Enregistre les coordonnées

    if best_neighbor_type is not None:
        return best_neighbor_type, closest_neighbor_coords
    else:
        return None, None

def wait_for_key(key='h'):
    """Attend que la touche spécifiée soit pressée."""
    while True:
        k = cv.waitKey(0) & 0xFF  # Masque avec 0xFF pour ne récupérer que le dernier octet (nécessaire en 64 bits)
        if k == ord(key):  # ord(key) convertit le caractère en code ASCII
            break
        elif k == ord('q'):  # Ajout d'une touche pour quitter.
            print("Programme terminé par l'utilisateur.")
            cv.destroyAllWindows()
            exit()
        else:
            print(f"Appuyez sur '{key}' pour continuer ou 'q' pour quitter. Touche pressée : {chr(k)}")  # Affiche la touche pressée.

# Définir les valeurs de search_distance et angle_tolerance
search_distance = 20  # Ajuster si nécessaire
angle_tolerance = 10  # Ajuster si nécessaire

#Calculer l'angle de départ
starting_angle = code2.angleRedPattern(img_transformed)
print(f"Angle de départ : {starting_angle}")

# Remplace l'appel à l'ancienne fonction main par la nouvelle avec les paramètres
main_avec_sequence(img_transformed, center_tab_transformed, search_distance, angle_tolerance, starting_angle)