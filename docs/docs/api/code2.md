# Module Principal (code2.py)

Ce module contient les fonctions principales pour le traitement et la transformation des images de mires.

## Exemples d'Images

### Image de Référence
<figure>
    <img src="/images/mire_315a.png" alt="Image de référence">
    <figcaption>Image de référence (mire_315a.png)</figcaption>
</figure>

### Image Transformée
<figure>
    <img src="/images/trans.png" alt="Image transformée">
    <figcaption>Image après transformation (trans.png)</figcaption>
</figure>

## Variables Globales

### Paramètres de l'image
```python
path_mire_orig = "data/mire_315a.png"  # Chemin vers l'image de référence
mire_orig = cv.imread(path_mire_orig)   # Image originale
modified_mire = mire_orig               # Version modifiée de l'image
transformed_mire = mire_orig.copy()     # Version transformée de l'image
contours_mire = None                    # Contours détectés dans l'image
```

### Paramètres de la caméra virtuelle
```python
virtual_focal = 75                      # Distance focale virtuelle (par défaut: 75)
virtual_focal_dist = ncols / (2 * np.tan(np.radians(virtual_focal / 2)))  # Distance focale calculée
```

### Paramètres de transformation
<figure>
    <img src="/images/sixaxes.jpg" alt="Représentation des six axes">
</figure>
```python
# Translation
t_x = 0    # Translation sur l'axe X
t_y = 0    # Translation sur l'axe Y
t_z = 20   # Translation sur l'axe Z

# Rotation
r_x = 20   # Rotation autour de l'axe X
r_y = 0    # Rotation autour de l'axe Y
r_z = 46   # Rotation autour de l'axe Z
bool_rxy = None   # Détermine l'ordre de rotation 'xy' ou 'yx' quand r_x et r_y sont utilisés
sens_rxy = None   # Spécifie l'ordre de rotation ('xy' ou 'yx')

# Échelle
sc_x = 1   # Facteur d'échelle sur l'axe X
sc_y = 1   # Facteur d'échelle sur l'axe Y
sc_z = 1   # Facteur d'échelle sur l'axe Z
```

### Paramètres de détection
```python
inter_contours = 10     # Espacement entre les contours
limit_area = 25        # Surface minimale des contours
limit_extrm_angle = 5.0 # Angle limite pour les motifs extrêmes
max_distance_search_pixel = 50  # Rayon maximum de recherche de pixels
```

### Masques de couleur
```python
mask = [
    ([38, 179, 38], [38, 179, 38]),  # Vert
    ([0, 0, 255], [201, 201, 255]),  # Rouge
    ([0, 0, 0], [170, 170, 170])     # Noir
]

threshold = [100, 76, 30]  # Valeurs de seuil pour chaque masque
```

### Variables de contrôle
```python
center_tab = []  # Liste des centres des contours détectés
angle_tab = []   # Liste des angles détectés

# Flags d'affichage
show_data = [False, False, False, False, False, False, False, False]  # [img, transformation, mask, hsv, grey, threshold, contours, contours min rouge]

# Flags de sauvegarde
save_data = [False, False, False, False, False, False, False, False, False]  # [parameters, img, transformation, mask, hsv, grey, threshold, contours, contours min rouge]
```

## Fonctions Principales

### Transformation 2D vers 3D
```python
def _2Dto3D():
    """
    Crée une matrice de transformation 2D vers 3D qui centre les coordonnées de l'image.
    
    Returns:
        np.ndarray: Matrice de transformation 4x4 de type float32
    """
```

### Transformation 3D vers 2D
```python
def _3Dto2D():
    """
    Crée une matrice de projection 3D vers 2D pour simuler une caméra virtuelle.
    
    Returns:
        np.ndarray: Matrice de projection 3x4 de type float32
    """
```

### Rotations
```python
def rotationXYZ(axis, degXYZ=None):
    """
    Crée une matrice de rotation 4x4 autour d'un axe spécifique (X, Y, ou Z) selon un angle en degrés.
    
    Args:
        axis (str): Axe de rotation ('x', 'y', ou 'z')
        degXYZ (float, optional): Angle de rotation en degrés
    
    Returns:
        np.ndarray: Matrice de rotation 4x4 de type float32. Retourne la matrice identité si aucun angle n'est fourni.
    """
```

### Translation
```python
def translationXYZ(tx=0, ty=0, tz=0):
    """
    Applique une translation selon les axes X, Y et Z.
    
    Args:
        tx (float): Translation sur l'axe X
        ty (float): Translation sur l'axe Y
        tz (float): Translation sur l'axe Z
    
    Returns:
        np.ndarray: Matrice de translation 4x4
    """
```

### Mise à l'échelle
```python
def scaleXYZ(scx, scy, scz):
    """
    Applique une mise à l'échelle selon les axes X, Y et Z.
    
    Args:
        scx (float): Facteur d'échelle sur l'axe X
        scy (float): Facteur d'échelle sur l'axe Y
        scz (float): Facteur d'échelle sur l'axe Z
    
    Returns:
        np.ndarray: Matrice de mise à l'échelle 4x4
    """
```

### Détection de motifs
```python
def fullContoursProcess(img):
    """
    Traite l'image pour détecter et analyser les contours des motifs.
    
    Args:
        img (np.ndarray): Image à traiter
    
    Returns:
        list: Liste des centres des motifs détectés
    """
```

### Angle des motifs rouges
```python
def angleRedPattern(img):
    """
    Détermine l'angle des motifs rouges dans l'image.
    
    Args:
        img (np.ndarray): Image à analyser
    
    Returns:
        float: Angle en degrés
    """
```

### Recherche de pixels
```python
def find_pixel_dir(img, start_x, start_y, dir, target_color):
    """
    Recherche un pixel d'une couleur spécifique dans une direction donnée.
    
    Args:
        img (np.ndarray): Image à analyser
        start_x (int): Position X de départ
        start_y (int): Position Y de départ
        dir (str): Direction de recherche
        target_color (tuple): Couleur cible (B, G, R)
    
    Returns:
        tuple: Coordonnées (x, y) du pixel trouvé ou None si non trouvé
    """
```

## Notes Techniques

- Les transformations utilisent des matrices homogènes 4x4
- Les coordonnées sont centrées avant transformation
- Les motifs sont détectés par analyse de contours et de couleurs
- L'angle des motifs rouges est utilisé pour l'orientation
- Le système de coordonnées suit la convention :
  ```
               z  
               |  
               |  
               |  
               O----------------- y  
              /  
             /  
            /  
           x 
  ``` 