# Utilisation

Ce guide vous explique comment utiliser le projet une fois l'installation terminée.

## Démarrage

### Préparation

Avant de lancer le script principal, assurez-vous que :

1. Pylon Viewer est fermé (le script ne pourra pas utiliser la caméra si Pylon Viewer est ouvert)
2. Tous les périphériques nécessaires sont correctement connectés
3. Votre environnement virtuel Python est activé

### Lancement du script principal

Pour démarrer l'application, exécutez :

```bash
python capture.py
```

## Fonctionnalités principales

### Capture d'images

Le script `capture.py` permet de :

- Capturer des images via la caméra Basler
- Sauvegarder les images capturées
- Visualiser les images en temps réel

### Traitement des images

Le projet inclut plusieurs scripts pour le traitement des images :

- `crop_gui.py` : Interface graphique pour le recadrage d'images
- `crop_gui2.py` : Version alternative de l'interface de recadrage
- `graph.py` : Visualisation et analyse des données
- `rebuild.py` : Reconstruction d'images
- `search.py` : Recherche dans les images

## Structure des fichiers

Le projet est organisé comme suit :

```
gen_img_points_ctrl/
├── data/           # Dossier contenant les images et données
├── docs/           # Documentation
├── capture.py      # Script principal de capture
├── crop_gui.py     # Interface de recadrage
├── graph.py        # Visualisation des données
├── rebuild.py      # Reconstruction d'images
└── search.py       # Recherche dans les images
```

## Bonnes pratiques

1. **Gestion des images**
   - Sauvegardez régulièrement vos images
   - Utilisez des noms de fichiers descriptifs
   - Organisez vos images dans le dossier `data/`

2. **Utilisation de la caméra**
   - Vérifiez toujours que Pylon Viewer est fermé avant de lancer le script
   - Assurez-vous que la caméra est correctement connectée
   - Vérifiez les paramètres de capture si nécessaire

3. **Environnement de travail**
   - Gardez votre environnement virtuel à jour
   - Vérifiez régulièrement les mises à jour des dépendances
   - Sauvegardez vos modifications régulièrement

## Dépannage

### Problèmes courants

1. **La caméra ne répond pas**
   - Vérifiez que Pylon Viewer est bien fermé
   - Assurez-vous que la caméra est correctement connectée
   - Redémarrez l'application

2. **Erreurs de capture**
   - Vérifiez les permissions d'accès au dossier `data/`
   - Assurez-vous que l'espace disque est suffisant
   - Vérifiez les paramètres de la caméra

3. **Problèmes d'interface**
   - Vérifiez que toutes les dépendances sont installées
   - Redémarrez l'application
   - Vérifiez les logs pour plus de détails

## Support

Si vous rencontrez des problèmes non résolus, n'hésitez pas à :

1. Consulter la documentation complète
2. Vérifier les issues sur le dépôt GitHub
3. Contacter l'équipe de support 