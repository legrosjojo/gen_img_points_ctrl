# Installation

Ce guide vous permettra d'installer et de configurer correctement le projet sur votre système.

## Prérequis

- Python 3.x
- Git
- Une caméra Basler compatible
- Pylon Viewer (pour la configuration de la caméra)

## Installation du projet

### 1. Récupération du projet

Clonez le dépôt Git contenant le projet :

```bash
git clone https://github.com/legrosjojo/gen_img_points_ctrl.git
```

Vous pouvez également récupérer le répertoire `gen_img_points_ctrl` par une autre méthode (téléchargement ZIP, transfert USB, etc.).

### 2. Configuration de l'environnement

#### Se positionner dans le dossier du projet

```bash
cd gen_img_points_ctrl
```

#### Créer un environnement virtuel Python

```bash
python -m venv venv
```

#### Activer l'environnement virtuel

Sous Linux / macOS :
```bash
source venv/bin/activate
```

Sous Windows (cmd) :
```bash
venv\Scripts\activate
```

#### Installer les dépendances

```bash
pip install -r libs.txt
```

## Installation de Pylon Viewer

### 1. Téléchargement

1. Rendez-vous sur le site officiel de Basler : [https://www.baslerweb.com/fr-fr/downloads/software/](https://www.baslerweb.com/fr-fr/downloads/software/)
2. Choisissez la version Linux ARM 64bits

### 2. Installation sur Raspberry Pi

1. Extraire l'archive :
```bash
tar -xzf pylon-*.tar.gz
cd pylon-*/debs-aarch64
```

2. Installer les paquets :
```bash
sudo dpkg -i *.deb
```

3. Si des dépendances manquent, les installer :
```bash
sudo apt-get install -f
```

### 3. Vérification

Une fois l'installation terminée, vous pouvez lancer Pylon Viewer depuis le menu démarrage du Raspberry PI > Sons & vidéo > pylon Viewer

## Prochaines étapes

Une fois l'installation terminée, vous pouvez passer à la section [Utilisation](../usage/) pour apprendre à utiliser le projet. 