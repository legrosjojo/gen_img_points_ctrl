# Module de Test

Ce module contient un script de test pour la détection des motifs dans une image.

## Fonctionnalités

- Chargement d'une image
- Détection des motifs
- Visualisation des résultats

## Code Principal

```python
import cv2
import numpy as np
import code

# Charger l'image
img = cv2.imread('data/trans.png')
if img is None:
    print("Erreur: Impossible de charger l'image")
    exit()

# Initialiser code.center_tab
code.center_tab = []  # Réinitialisation de la liste
code.transformed_mire = img
code.fullContoursProcess(code.transformed_mire)

# Créer une copie de l'image pour visualiser les centres
img_centers = img.copy()

# Dessiner des cercles rouges aux coordonnées des centres détectés
for x, y, motif_type in code.center_tab:
    cv2.circle(img_centers, (int(x), int(y)), 5, (0, 0, 255), -1)

# Afficher le nombre de motifs détectés
print(f"Nombre de motifs détectés : {len(code.center_tab)}")

# Afficher l'image avec les cercles
cv2.imshow('Centres détectés', img_centers)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

## Utilisation

1. Placez l'image à tester dans le dossier `data/` sous le nom `trans.png`
2. Exécutez le script avec `python test.py`
3. L'image avec les centres détectés s'affichera
4. Appuyez sur une touche pour fermer la fenêtre

## Notes Techniques

- Le script utilise les fonctions de détection de `code.py`
- Les centres détectés sont marqués par des cercles rouges
- La visualisation est interactive 