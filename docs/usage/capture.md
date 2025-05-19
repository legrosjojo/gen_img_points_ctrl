# Capture d'images

Ce module permet de capturer des images à partir de différentes sources.

## Fonctionnalités

- Capture d'images depuis la webcam
- Capture d'images depuis des fichiers
- Prétraitement des images capturées

## Utilisation

```python
from code import capture

# Capture depuis la webcam
image = capture.from_webcam()

# Capture depuis un fichier
image = capture.from_file("chemin/vers/image.jpg")
```

## Configuration

Les paramètres de capture peuvent être ajustés dans le fichier de configuration. 