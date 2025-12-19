# muslimINT

## MuslimINT website

Site web permettant d’emprunter, ajouter et gérer des livres de l’association MuslimInt.  
Suivi des emprunts et alertes lorsque la date de retour approche.

---

## Prérequis
- Python 3.x
- pip
- virtualenv

---

## Création et activation de l’environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

## Installation des dépendances
À la racine du projet :

`pip3 install -r requirements.txt``


## Création de la base de données (Django)
Se placer dans le dossier du projet Django : `cd muslimINT_lib`

Créer les fichiers de migration : `python3 manage.py makemigrations`

Créer la base de données et appliquer les migrations : `python3 manage.py migrate`

Créer un super utilisateur pour la partie admin : `python3 manage.py createsuperuser`

## Lancement du serveur de développement

`python manage.py runserver`

--> Application accessible à l’adresse : http://127.0.0.1:8000/ (en local pour le moment)