# Loser Queue ?

Ce projet permet d'extraire des données via l'API Riot pour essayer de prouver (ou non) que la loser queue existe.

## Modèle des données extraites
Les données sont extraites puis stockées dans des fichiers `JSON`.

Chaque fichier contient autant d'objet que de parties extraites. Chaque object est composé de `4 couples clef / valeur` :
- `match_id` : l'ID de la partie extraite
- `tier` : le tier de la partie (MASTER, DIAMAND, PLATINUM, ...)
- `team_100` : une liste de 5 éléments contenant des informations sur les résultats des **20 dernières parties (max)** de chaque joueur de l'équipe bleu
- `team_200` : une liste de 5 éléments contenant des informations sur les résultats des **20 dernières parties (max)** de chaque joueur de l'équipe rouge

Un fichier `JSON` est crée par tier.

## Utilisation du projet

### Fichier à ajouter pour rendre le projet fonctionnel

- `loser-queue/.env`:
    - `API_KEY=<CLEF API>` (avec `<CLEF API>` une clef API Riot générable via [cette page](https://developer.riotgames.com/))

### Modification de la configuration

- `loser-queue/src/config.py`:
    ````python
    class Settings:
        """Base config"""

        # Possible values for "tiers" to add in the list : "DIAMOND", "PLATINUM", "GOLD", "SILVER", "BRONZE", "IRON"
        TIERS: list = ["CHALLENGER", "GRANDMASTER", "MASTER"] <-- Liste des tiers dont les parties vont extraites
        NUMBER_OF_MATCHES_BY_TIER: int = 300 <-- Nombre de partie par tier extraites
    ````

### Utilisation via `Docker`
- Installer [`Docker`](https://docs.docker.com/engine/install/)
- Se rendre à la racine du dossier et exécuter la commande :
    ````
    docker compose up --build -d
    ````
Un dossier `data/` va se créer et les fichiers `JSON` seront placés dans ce dossier.

### Utilisation via `Python`
- Télécharger [`Python 3.9`](https://www.python.org/downloads/)
- Installer [`pipenv`](https://pypi.org/project/pipenv/):
    ````
    pip install pipenv
    ````
- Se rendre dans le dossier `loser-queue` et installer les packages nécessaire dans un environnement virtuel:
    ````
    pipenv install
    ````
- Exécuter le fichier `loser-queue/main.py` dans l'environnement virtuel (en se trouvant toujours dans le dossier `loser-queue`):
    ````
    pipenv run python main.py
    ````
Un dossier `loser-queue/data/` va se créer et les fichiers `JSON` seront placés dans ce dossier.

### Temps d'exécution
Pour extraire les informations d'une seule partie, **plus de 220 requêtes HTTP** sont envoyés à l'API Riot.

Avec une clef API de développement classique limité à **100 requêtes HTTP toutes les 2 minutes**, il faut plus de **6 minutes** pour extraire les informations d'une partie.
