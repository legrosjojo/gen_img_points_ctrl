# Module de Recherche (search.py)

Ce module gère la recherche et l'alignement des motifs dans les images de mires.

## Variables Globales

### Paramètres de recherche
```python
distance_init = 5    # Distance initiale de recherche
step_size = 5        # Pas de recherche
max_distance = 100   # Distance maximale de recherche
```

### Variables exportables
```python
base_mire = []       # Base de données des motifs de référence
motifs_data = []     # Données des motifs détectés
M_transform = []     # Matrice de transformation
```

## Fonctions Principales

### Recherche de voisins
<figure>
    <img src="/images/search.png" alt="Schéma recherche voisin">
    <figcaption>Schéma montrant la recherche de voisins :</figcaption>
    <figcaption>
        - Croix central : centre du motif de référence<br>
        - Trait bleu : direction de la première recherche<br>
        - Trait rouge : distance maximal de recherche (max_distance) <br>
        - Trait jaune : pas de recherche (step_size)<br>
        - Croix sur le cercle unitaire : direction de recherche à chaque étapes (+45°)
    </figcaption>
</figure>
```python
def find_neighbor(center_tab, cx, cy, angle, init_dist=5, step_size=5, max_dist=100):
    """
    Recherche un motif voisin dans une direction donnée.
    
    Args:
        center_tab (list): Liste des centres des motifs
        cx (float): Coordonnée X du centre
        cy (float): Coordonnée Y du centre
        angle (float): Angle de recherche en degrés
        init_dist (int): Distance initiale de recherche
        step_size (int): Pas de recherche
        max_dist (int): Distance maximale de recherche
    
    Returns:
        str: Type du motif trouvé ou "N" si aucun motif n'est trouvé
    """
```

### Traitement d'un motif
<figure>
    <img src="/images/codage.png" alt="Système de codage avec exemple">
    <figcaption>Système de codage avec exemple</figcaption>
</figure>
```python
def process_motif(center_tab, index, start_angle):
    """
    Génère le code d'un motif en analysant ses voisins.
    
    Args:
        center_tab (list): Liste des centres des motifs
        index (int): Index du motif à traiter
        start_angle (float): Angle de départ pour l'analyse
    
    Returns:
        tuple: (coordonnées, code du motif)
    """
```

### Génération de la base mire
```python
def generate_base_mire(image, start_angle=0):
    """
    Génère la base de données des motifs à partir de l'image de référence.
    
    Args:
        image (np.ndarray): Image de référence
        start_angle (float): Angle de départ pour l'analyse
    
    Returns:
        list: Liste des motifs avec leurs codes
    """
```

### Ajout des codes tournés
<figure>
    <img src="/images/rotation_code.png" alt="Schéma de rotation des codes">
    <figcaption>
        Schéma explicatif de la rotation des codes :<br>
        - Code initial : M12345678 (M = type du motif, 1-8 = voisins)<br>
        - Rotation 90° : M34567812 (décalage de 2 positions)<br>
        - Rotation 180° : M56781234 (décalage de 4 positions)<br>
        - Rotation 270° : M78123456 (décalage de 6 positions)<br><br>
        Le décalage de 2 positions correspond à la rotation de 45° entre chaque voisin.<br>
        Une rotation de 90° = 2 positions car 90° ÷ 45° = 2
    </figcaption>
</figure>
```python
def add_rotated_codes(base_mire):
    """
    Ajoute les codes des motifs pour différentes rotations (90°, 180°, 270°).
    
    Args:
        base_mire (list): Liste des motifs de base
    
    Returns:
        list: Liste des motifs avec leurs codes pour toutes les rotations
    """
```

### Calcul de la matrice d'homographie
```python
def compute_homography_matrix(base_mire, motifs_data, min_matches=4):
    """
    Calcule la matrice d'homographie entre les motifs transformés et la base mire.
    
    Args:
        base_mire (list): Base de données des motifs de référence
        motifs_data (list): Données des motifs détectés
        min_matches (int): Nombre minimum de correspondances requises
    
    Returns:
        np.ndarray: Matrice d'homographie
    
    Raises:
        RuntimeError: Si pas assez de correspondances sont trouvées
    """
```

### Pipeline d'alignement
```python
def run_alignment_pipeline(image_original_path, image_transformed_path):
    """
    Exécute le pipeline complet d'alignement d'images.
    
    Args:
        image_original_path (str): Chemin vers l'image de référence
        image_transformed_path (str): Chemin vers l'image transformée
    
    Returns:
        np.ndarray: Matrice de transformation ou None en cas d'échec
    """
```

## Notes Techniques

- Utilise l'algorithme RANSAC pour le calcul de l'homographie
- Les motifs sont codés selon leur type et leurs voisins
- L'alignement prend en compte les rotations de 90°, 180° et 270°
- Les résultats sont sauvegardés dans `data/result.txt`
- Le module utilise les fonctions de détection de `code2.py` 