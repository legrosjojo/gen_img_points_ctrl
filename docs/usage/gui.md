# Interface Graphique

L'interface graphique principale (`graph.py`) permet de contrôler toutes les fonctionnalités du projet de manière intuitive.

## Lancement

```bash
python graph.py
```

## Fonctionnalités

### Contrôles de transformation

L'interface propose des sliders pour contrôler les transformations 3D :

- **Translation**
  - X : déplacement horizontal (-512 à 512)
  - Y : déplacement vertical (-512 à 512)
  - Z : zoom (-250 à 250)

- **Rotation**
  - X : rotation autour de l'axe X (-180° à 180°)
  - Y : rotation autour de l'axe Y (-180° à 180°)
  - Z : rotation autour de l'axe Z (-180° à 180°)

### Options de visualisation

Des cases à cocher permettent de contrôler l'affichage des différentes étapes du traitement :

- Image originale
- Image transformée
- Masque
- HSV
- Niveaux de gris
- Seuillage
- Contours
- Contours minimum (rouge)

### Options de sauvegarde

Vous pouvez choisir quelles données sauvegarder :

- Paramètres
- Image originale
- Image transformée
- Masque
- HSV
- Niveaux de gris
- Seuillage
- Contours
- Contours minimum (rouge)

## Workflow typique

1. Chargez une image de mire de référence
2. Ajustez les paramètres de transformation
3. Visualisez les différentes étapes du traitement
4. Validez pour lancer le processus complet :
   - Capture de l'image
   - Recadrage
   - Correction
   - Alignement

## Astuces

- Utilisez les champs de texte pour entrer des valeurs précises
- La touche Entrée valide la valeur dans un champ de texte
- Le bouton "Validate" lance le processus complet
- Les résultats sont sauvegardés dans le dossier `data/` 