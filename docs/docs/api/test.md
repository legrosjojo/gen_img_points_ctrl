# Module de Test (test.py)

Ce module contient un script de test pour la détection des motifs dans une image.

## Fonctionnalités

Le script teste les fonctionnalités suivantes :
- Chargement d'une image
- Détection des motifs
- Visualisation des résultats

## Code Principal

```python
# Chargement de l'image
img = cv.imread("data/trans.png")

# Détection des motifs
code2.center_tab = []  # Réinitialisation de la liste
code2.transformed_mire = img
code2.fullContoursProcess(code2.transformed_mire)

# Visualisation des résultats
img_copy = img.copy()
for x, y, motif_type in code2.center_tab:
    cv.circle(img_copy, (int(x), int(y)), 5, (0, 0, 255), -1)
```

## Utilisation

Pour exécuter le test :
1. Placer une image de test dans le dossier `data/` nommée `trans.png`
2. Exécuter le script : `python test.py`
3. Observer les résultats dans la fenêtre affichée

## Notes Techniques

- Le script utilise les fonctions de détection de `code2.py`
- Les motifs détectés sont marqués par des cercles rouges
- Le script affiche le nombre total de motifs détectés
- La visualisation est interactive (attente d'une touche pour fermer) 