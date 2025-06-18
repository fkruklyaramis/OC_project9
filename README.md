# LITReview - Système de critiques littéraires

![LITReview Logo](/webapp/media/168805567091_LITrevu_banner.png)

Ce projet est une application web Django permettant aux utilisateurs de demander, publier et consulter des critiques de livres ou d'articles littéraires.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Schéma des modèles](#schéma-des-modèles)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Fonctionnement de l'application](#fonctionnement-de-lapplication)
- [Structure du projet](#structure-du-projet)
- [Cas d'utilisation](#cas-dutilisation)
- [Développement](#développement)
- [Déploiement](#déploiement)
- [Dépannage](#dépannage)

## Fonctionnalités

L'application LITReview permet à ses utilisateurs de :

- **Authentification sécurisée**
  - S'inscrire et se connecter à un compte personnel
  - Système de mot de passe sécurisé via Django

- **Gestion de contenu**
  - Créer des tickets pour demander des critiques sur un livre ou un article
  - Publier des critiques en réponse à des tickets existants
  - Créer simultanément un ticket et une critique sur ce ticket ("critique spontanée")
  - Consulter, modifier et supprimer ses propres tickets et critiques
  - Télécharger des images de couverture pour les livres/articles

- **Flux social personnalisé**
  - Consulter un flux des derniers tickets et critiques, classés par ordre chronologique inversé
  - Affichage intelligent des contenus pertinents (publications propres et des utilisateurs suivis)
  - Visualisation des critiques émises en réponse à ses propres tickets

- **Système d'abonnements**
  - Suivre d'autres utilisateurs pour voir leur contenu dans son flux
  - Gérer ses abonnements (suivre/ne plus suivre)
  - Recherche d'utilisateurs par nom d'utilisateur

- **Interface utilisateur intuitive**
  - Navigation simple entre les différentes fonctionnalités
  - Évaluation des critiques avec un système d'étoiles (0 à 5)
  - Messages de confirmation pour toutes les actions importantes

## Schéma des modèles

Voici la structure des modèles de données utilisés dans l'application :

```
+----------------+       +----------------+       +----------------+
|     User       |       |    Ticket      |       |    Review      |
+----------------+       +----------------+       +----------------+
| id             |<----->| id             |<----->| id             |
| username       |       | title          |       | headline       |
| password       |       | description    |       | body           |
| ...            |       | user           |       | rating         |
+----------------+       | image          |       | user           |
        ^                | time_created   |       | ticket         |
        |                +----------------+       | time_created   |
        |                                        +----------------+
        |
        |
+----------------+
|  UserFollows   |
+----------------+
| id             |
| user           |
| followed_user  |
+----------------+
```

### Description des modèles

- **User** : Modèle utilisateur standard de Django
- **Ticket** : Représente une demande de critique pour un livre/article
- **Review** : Représente une critique en réponse à un ticket
- **UserFollows** : Gère les relations d'abonnement entre utilisateurs

## Prérequis

- Python 3.12 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/fkruklyaramis/OC_project9.git
cd OC_project9
```

### 2. Créer un environnement virtuel

```bash
python -m venv env
```

### 3. Activer l'environnement virtuel

- Sous macOS/Linux :
```bash
source env/bin/activate
```

- Sous Windows :
```bash
.\env\Scripts\activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

Les dépendances principales incluent:
- Django 5.2.1 - Framework web
- Pillow 11.2.1 - Bibliothèque pour la gestion des images 
- SQLparse 0.5.3 - Pour le formatage SQL
- ASGI 3.8.1 - Interface ASGI pour la compatibilité serveur

### 5. Appliquer les migrations pour créer la base de données

```bash
cd webapp
python manage.py migrate
```

### 6. (Optionnel) Créer un superutilisateur pour accéder à l'administration Django

```bash
python manage.py createsuperuser
```

## Utilisation

### Lancer le serveur web

Pour démarrer le serveur de développement Django :

```bash
cd webapp
python manage.py runserver
```

Le site sera accessible à l'adresse [http://127.0.0.1:8000/](http://127.0.0.1:8000/) dans votre navigateur.

### Lancer le shell Django

Pour accéder au shell Django interactif (utile pour tester ou déboguer) :

```bash
cd webapp
python manage.py shell
```

### Administration

L'interface d'administration Django est accessible à l'adresse [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) après avoir créé un superutilisateur.

### Navigation dans l'application

Une fois connecté, l'utilisateur a accès à différentes pages via la barre de navigation :

- **Flux** (`/flux/`) : Page principale affichant les tickets et critiques pertinents
  - Boutons pour créer un ticket ou une critique
  - Affichage chronologique des publications

- **Posts** (`/posts/`) : Gestion des publications personnelles
  - Liste des tickets et critiques créés par l'utilisateur
  - Options pour modifier ou supprimer chaque élément

- **Abonnements** (`/subscriptions/`) : Gestion des relations entre utilisateurs
  - Formulaire pour rechercher et suivre d'autres utilisateurs
  - Liste des utilisateurs suivis avec option de désabonnement
  - Liste des abonnés (utilisateurs qui vous suivent)

- **Se déconnecter** (`/logout/`) : Déconnexion de l'application

## Structure du projet

```
webapp/
├── db.sqlite3           # Base de données SQLite
├── manage.py            # Script de gestion Django
├── litrevu/             # Application principale
│   ├── constants.py     # Constantes et messages
│   ├── forms.py         # Formulaires
│   ├── models.py        # Modèles de données
│   ├── views.py         # Vues et logique
│   ├── static/          # Fichiers statiques (CSS, JS)
│   └── templates/       # Templates HTML
├── media/               # Images téléchargées
└── webapp/              # Configuration du projet
    ├── settings.py      # Paramètres Django
    └── urls.py          # Configuration des URL
```

## Cas d'utilisation

### Flux d'utilisateur typique

1. Un utilisateur s'inscrit sur la plateforme
2. Il peut créer un ticket demandant une critique pour un livre
3. Il peut suivre d'autres utilisateurs pour voir leurs publications
4. Il peut consulter son flux personnel contenant :
   - Ses propres tickets et critiques
   - Les tickets et critiques des utilisateurs qu'il suit
   - Les critiques faites sur ses propres tickets

### Création de contenu

- **Tickets** : Demandes de critique pour un livre ou article
- **Critiques** : Réponses à des tickets ou critiques créées avec un nouveau ticket

## Développement

### Commandes utiles

- **Créer une migration après modification des modèles** :
```bash
python manage.py makemigrations
```

- **Appliquer les migrations** :
```bash
python manage.py migrate
```

- **Collecter les fichiers statiques** :
```bash
python manage.py collectstatic
```

### Technologies utilisées

- **Django 5.2.1** : Framework web Python
- **SQLite** : Base de données par défaut
- **HTML/CSS** : Interface utilisateur
- **Pillow** : Gestion des images

## Fonctionnement de l'application

### Système d'authentification

L'application utilise le système d'authentification intégré de Django. Les utilisateurs peuvent :
- Créer un compte avec un nom d'utilisateur et un mot de passe
- Se connecter à leur compte existant
- Se déconnecter

Toutes les fonctionnalités principales de l'application nécessitent une authentification.

### Gestion des tickets et des critiques

- Les tickets sont des demandes de critiques pour des livres ou des articles.
- Les critiques peuvent être créées de deux façons :
  1. En réponse à un ticket existant
  2. Directement avec création simultanée d'un ticket (critique spontanée)
- Chaque critique inclut une note sur une échelle de 0 à 5.
- Un utilisateur ne peut publier qu'une seule critique par ticket.

### Système d'abonnements

- Les utilisateurs peuvent suivre d'autres utilisateurs pour voir leur contenu dans leur flux.
- Un utilisateur ne peut pas se suivre lui-même.
- Les relations d'abonnement sont unidirectionnelles (A peut suivre B sans que B ne suive A).
- Les utilisateurs peuvent voir qui les suit et qui ils suivent.

### Flux personnalisé

Le flux affiche dans l'ordre chronologique inversé (du plus récent au plus ancien) :
- Les tickets et critiques de l'utilisateur connecté
- Les tickets et critiques publiés par les utilisateurs suivis
- Les critiques des autres utilisateurs en réponse aux tickets de l'utilisateur connecté
aze
---

Développé dans le cadre du Projet 9 du parcours Développeur d'Applications Python.
