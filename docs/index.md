# Documentation du Projet FIP

Bienvenue dans la documentation du projet de traitement d'images de mires. Ce projet permet de manipuler, transformer et analyser des images de mires pour des applications de calibration, de vision par ordinateur et de traitement d'image.

## Fonctionnalités principales

- **Transformation 3D d'images** : translation, rotation, zoom via une interface graphique interactive
- **Détection et analyse de motifs** : extraction automatique des centres et types de motifs sur la mire
- **Recadrage assisté** : sélection manuelle de 4 points pour recadrer précisément une image
- **Correction et recolorisation** : nettoyage et standardisation des couleurs des motifs détectés
- **Alignement automatique** : recalage d'une mire transformée sur la mire de référence par homographie
- **Capture d'image** : prise de vue directe depuis une caméra compatible (ex : Basler via pypylon)

## Structure du projet

```
.
├── code.py         # Traitement principal des images et transformations
├── crop_gui.py      # Interface graphique pour le recadrage manuel
├── capture.py       # Capture d'image depuis une caméra
├── graph.py         # Interface graphique principale
├── rebuild.py       # Correction et recolorisation des images
├── search.py        # Détection, codage et alignement des motifs
└── data/            # Images d'entrée, résultats, fichiers générés
```

## Démarrage rapide

1. [Installation](installation.md)
2. [Guide d'utilisation](usage/gui.md)
3. [Documentation technique](api/code.md)

## À propos

Projet réalisé dans le cadre du module d'ingénierie FIP, Groupe 3.

# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
