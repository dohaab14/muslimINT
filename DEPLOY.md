# Déploiement MuslimINT — Guide rapide

## Prérequis
- Python 3.12+
- Un serveur Linux (ou PythonAnywhere / Railway / Render)

---

## 1. Cloner et installer

```bash
git clone <url-du-repo>
cd muslimINT-main/muslimINT_lib
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
```

## 2. Configurer l'environnement

```bash
cp .env.example .env
```

Éditer `.env` :
```
SECRET_KEY=<générer-une-clé-unique>
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
```

Pour générer une clé secrète :
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 3. Base de données et fichiers statiques

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 4. Lancer avec Gunicorn

```bash
gunicorn muslimINT_lib.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

## 5. Serveur web (Nginx)

Exemple de configuration Nginx en reverse proxy :

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location /static/ {
        alias /chemin/vers/muslimINT_lib/staticfiles/;
    }

    location /media/ {
        alias /chemin/vers/muslimINT_lib/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Option simple : PythonAnywhere

1. Créer un compte sur [pythonanywhere.com](https://www.pythonanywhere.com)
2. Uploader le projet (via git ou upload)
3. Créer un virtualenv et installer les dépendances
4. Configurer l'app web :
   - **Source code** : `/home/votre-user/muslimINT-main/muslimINT_lib`
   - **WSGI file** : pointer vers `muslimINT_lib.wsgi`
   - **Static files** : `/static/` → `/home/votre-user/muslimINT-main/muslimINT_lib/staticfiles`
   - **Media files** : `/media/` → `/home/votre-user/muslimINT-main/muslimINT_lib/media`
5. Éditer le `.env` avec `DEBUG=False` et une vraie `SECRET_KEY`
6. Reload l'app

---

## Checklist production

- [x] `SECRET_KEY` unique dans `.env`
- [x] `DEBUG=False`
- [x] `ALLOWED_HOSTS` configuré
- [x] `collectstatic` exécuté
- [x] `migrate` exécuté
- [x] Pages 404/500 personnalisées
- [x] HTTPS activé (via Nginx ou PythonAnywhere)
- [x] Cookies sécurisés activés automatiquement
- [x] Logging configuré (`logs/django.log`, `logs/security.log`)
