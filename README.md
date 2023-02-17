# League Of Legends : Loser Queue ?

Ce projet permet d'extraire des données via l'API Riot pour essayer de prouver (ou non) que la loser queue existe sur *League Of Legends*.

## Modèle des données extraites
Les données sont extraites puis stockées dans des fichiers `JSON`. Le nom du fichier est formatté de la façon suivante :
````
data_<TIER>_<NOMBRE DE PARTIE>_<TIMESTAMP DE FIN D'EXTRACTION>.json
````

Chaque fichier contient autant d'objets que de parties extraites. Chaque objet est composé de **4 couples clef / valeur** :
- `match_id` : l'ID de la partie extraite
- `tier` : le tier de la partie (*MASTER*, *DIAMAND*, *PLATINUM*, ...)
- `team_100` : une liste de 5 éléments contenant des informations sur les résultats des **20 dernières parties (max)** de chaque joueur de l'équipe bleu
- `team_200` : une liste de 5 éléments contenant des informations sur les résultats des **20 dernières parties (max)** de chaque joueur de l'équipe rouge

Un fichier `JSON` est crée par tier.

## Utilisation du projet

### Fichiers à ajouter pour rendre le projet fonctionnel

- `loser-queue/.env`:
    - `API_KEY=<CLEF API>` (avec `<CLEF API>` une clef API Riot générable via [cette page](https://developer.riotgames.com/))
- `loser-queue/config.ini`:
    - Fichier `.ini` avec une section nommée `[default]`
    - La section `[default]` a comme paramètres:
        - `TIERS: ["<LISTE>", "<DE>", "<TIERS>"]` (valeurs possible d'un tiers : *"CHALLENGER"*, *"GRANDMASTER"*, *"MASTER"*, *"DIAMOND"*, *"PLATINUM"*, *"GOLD"*, *"SILVER"*, *"BRONZE"*, *"IRON"*)
        - `NUMBER_OF_MATCHES_BY_TIER: <NOMBRE DE PARTIE EXTRAITES PAR TIER>`

*Exemple de fichier `loser-queue/config.ini`*:
````
[default]
TIERS: ["CHALLENGER", "GRANDMASTER", "MASTER"]
NUMBER_OF_MATCHES_BY_TIER: 300
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

Avec une clef API de développement classique limité à **100 requêtes HTTP toutes les 2 minutes**, il faut plus de **6 minutes** pour extraire les informations d'une partie, ce qui veut dire qu'on peut extraire les informations de **maximum 240 parties par jours**.
