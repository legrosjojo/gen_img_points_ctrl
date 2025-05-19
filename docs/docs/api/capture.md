# Module de Capture d'Images (capture.py)

Ce module gère la capture d'images depuis une caméra compatible avec le SDK Basler Pylon et l'affichage en plein écran.

## Interface de capture

<figure>
    <img src="/images/photo_color.png" alt="Exemple d'image capturée">
    <figcaption>Exemple d'image capturée</figcaption>
</figure>

## Fonctions Principales

### Affichage en plein écran
```python
def fullscreen(image):
    """
    Affiche une image en plein écran.
    
    Args:
        image (str): Chemin vers l'image à afficher
    
    Raises:
        ValueError: Si l'image ne peut pas être lue
    """
```

### Capture d'image couleur
```python
def capture_color_image(filename):
    """
    Capture une image depuis une caméra Basler et la sauvegarde.
    
    Args:
        filename (str): Nom du fichier de sortie
    
    Raises:
        RuntimeError: Si aucune caméra n'est trouvée ou si le format BGR n'est pas supporté
    """
```

### Traitement de capture
```python
def process_capture(image, filename):
    """
    Affiche une image en plein écran et capture une nouvelle image.
    
    Args:
        image (str): Chemin vers l'image à afficher
        filename (str): Nom du fichier pour la capture
    """
```

## Utilisation

### Exemple de capture d'image
```python
# Afficher une image de référence et capturer une nouvelle image
process_capture("data/mire_315a.png", "data/mire_photo.png")
```

## Notes Techniques

- Utilise le SDK Basler Pylon pour la communication avec la caméra
- Les images sont capturées au format BGR (compatible avec OpenCV)
- L'affichage en plein écran utilise CustomTkinter pour obtenir les dimensions de l'écran
- La capture d'image inclut la gestion des différents formats de pixels (RGB8, Mono8)
- Le module gère automatiquement la connexion/déconnexion de la caméra

## Classes

### CameraCapture
```python
class CameraCapture:
    """
    Classe pour gérer la capture d'images depuis une caméra Basler.
    
    Cette classe permet de :
    - Se connecter à une caméra Basler
    - Capturer des images
    - Gérer les paramètres de la caméra
    - Sauvegarder les images capturées
    """
```

## Méthodes Principales

### Initialisation
```python
def __init__(self):
    """
    Initialise la connexion à la caméra et configure les paramètres par défaut.
    
    Raises:
        Exception: Si aucune caméra n'est trouvée ou si la connexion échoue
    """
```

### Capture d'image
```python
def capture_image(self):
    """
    Capture une image depuis la caméra.
    
    Returns:
        np.ndarray: Image capturée au format BGR
    """
```

### Sauvegarde d'image
```python
def save_image(self, image, filename):
    """
    Sauvegarde une image sur le disque.
    
    Args:
        image (np.ndarray): Image à sauvegarder
        filename (str): Nom du fichier de sortie
    """
```

### Configuration de la caméra
```python
def configure_camera(self, exposure_time=None, gain=None):
    """
    Configure les paramètres de la caméra.
    
    Args:
        exposure_time (float, optional): Temps d'exposition en microsecondes
        gain (float, optional): Gain de la caméra
    """
```

## Utilisation

### Exemple de capture d'image
```python
# Créer une instance de capture
camera = CameraCapture()

# Configurer la caméra
camera.configure_camera(exposure_time=10000, gain=1.0)

# Capturer une image
image = camera.capture_image()

# Sauvegarder l'image
camera.save_image(image, "capture.png")
```

## Notes Techniques

- Utilise le SDK Basler Pylon pour la communication avec la caméra
- Les images sont capturées au format BGR (compatible avec OpenCV)
- La classe gère automatiquement la connexion/déconnexion de la caméra
- Les paramètres de la caméra peuvent être ajustés en temps réel 