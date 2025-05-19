# Installation

Ce guide vous aidera à installer et configurer le projet sur votre système.

## Prérequis

- Python 3.8 ou supérieur
- Une caméra compatible (optionnel, pour la capture)
- Git (pour cloner le dépôt)

## Installation des dépendances

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_DOSSIER]
```

2. Installez les dépendances Python :
```bash
pip install -r requirements.txt
```

Les dépendances principales sont :
- `opencv-python` : pour le traitement d'images
- `numpy` : pour les calculs matriciels
- `Pillow` : pour la manipulation d'images
- `customtkinter` : pour l'interface graphique
- `pypylon` : pour la capture via caméra Basler (optionnel)

## Configuration

1. Créez un dossier `data` à la racine du projet :
```bash
mkdir data
```

2. Placez vos images de mires dans le dossier `data/` :
- `mire_315a.png` : image de référence
- Autres images de mires selon vos besoins

## Vérification de l'installation

Pour vérifier que tout est correctement installé, lancez l'interface principale :

```bash
python graph.py
```

Si l'interface s'ouvre correctement, l'installation est réussie.

## Dépannage

### Problèmes courants

1. **Erreur d'importation de modules**
   - Vérifiez que toutes les dépendances sont installées
   - Utilisez `pip list` pour voir les packages installés

2. **Erreur de capture caméra**
   - Vérifiez que la caméra est correctement connectée
   - Installez les pilotes appropriés pour votre caméra

3. **Erreur d'affichage de l'interface**
   - Vérifiez que vous avez les droits d'accès au dossier `data/`
   - Assurez-vous que les images de référence sont présentes 