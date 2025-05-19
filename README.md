# gen_img_points_ctrl

## Présentation

Ce projet permet de manipuler, transformer et analyser des images de mires pour des applications de calibration, de vision par ordinateur et de traitement d'image. Il propose une interface graphique avancée pour appliquer des transformations 3D (translation, rotation, zoom), capturer des images via caméra, recadrer, reconstruire et aligner automatiquement les motifs détectés.

## Fonctionnalités principales

- **Transformation 3D d'images** : translation, rotation, zoom via une interface graphique interactive.
- **Détection et analyse de motifs** : extraction automatique des centres et types de motifs sur la mire.
- **Recadrage assisté** : sélection manuelle de 4 points pour recadrer précisément une image.
- **Correction et recolorisation** : nettoyage et standardisation des couleurs des motifs détectés.
- **Alignement automatique** : recalage d'une mire transformée sur la mire de référence par homographie.
- **Capture d'image** : prise de vue directe depuis une caméra compatible (ex : Basler via pypylon).
- **Sauvegarde et visualisation** : export des résultats, images intermédiaires, matrices de transformation, etc.

## Architecture du projet

```
.
├── code.py         # Traitement principal des images et transformations
├── crop_gui.py      # Interface graphique pour le recadrage manuel
├── capture.py       # Capture d'image depuis une caméra
├── graph.py         # Interface graphique principale (contrôle des transformations)
├── rebuild.py       # Correction et recolorisation des images de mire
├── search.py        # Détection, codage et alignement des motifs
├── test.py          # Exemple de détection de motifs (script de test)
├── data/            # Images d'entrée, résultats, fichiers générés
├── mire_7x7.png     # Exemple de mire
├── mire_11x11.png   # Exemple de mire
├── webographie.txt  # Sources et documentation utiles
└── README.md        # Ce document
```

## Installation

### Prérequis

- Python 3.8+
- Une caméra compatible (optionnel, pour la capture)
- Les bibliothèques suivantes (à installer via pip) :

```bash
pip install opencv-python numpy pillow customtkinter pypylon
```

> **Remarque** : `pypylon` n'est nécessaire que pour la capture via caméra Basler.

### Dépendances principales

- `opencv-python`
- `numpy`
- `Pillow`
- `customtkinter`
- `pypylon` (optionnel, pour la capture caméra)

## Utilisation

### Lancement de l'interface principale

```bash
python graph.py
```

Cette interface permet de :
- Charger une mire de référence (`data/mire_315a.png`)
- Appliquer des transformations (translation, rotation, zoom) via des sliders
- Visualiser et sauvegarder les différentes étapes du traitement
- Lancer la capture, le recadrage, la correction et l'alignement automatiquement

### Recadrage manuel d'une image

Pour lancer uniquement l'outil de recadrage :

```bash
python crop_gui.py
```

### Capture d'image depuis la caméra

Pour capturer une image et l'afficher en plein écran :

```bash
python capture.py
```

### Test de détection de motifs

Pour tester la détection de motifs sur une image :

```bash
python test.py
```

## Organisation des données

- Les images d'entrée et de sortie sont stockées dans le dossier `data/`.
- Les résultats d'alignement et d'encodage sont exportés dans `data/result.txt`.

## Documentation

- Le code est documenté avec des docstrings et des commentaires.
- Un fichier `webographie.txt` recense les principales sources et inspirations utilisées pour le développement.

### Visualisation de la documentation

Pour visualiser la documentation en local :

1. Installez MkDocs et ses dépendances :
```bash
pip install mkdocs mkdocs-material
```

2. Naviguez dans le dossier `docs/` :
```bash
cd docs
```

3. Lancez le serveur de développement MkDocs :
```bash
mkdocs serve
```

4. Ouvrez votre navigateur à l'adresse : http://127.0.0.1:8000

La documentation sera automatiquement mise à jour à chaque modification des fichiers source.

## À propos

Projet réalisé dans le cadre du module d'ingénierie FIP, Groupe 3.