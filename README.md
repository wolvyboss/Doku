DOKU — Jeu de grille quotidien
DOKU est un jeu de culture générale quotidien inspiré de Metrodoku. Une grille 3×3 s'affiche chaque jour — chaque ligne et chaque colonne correspond à une catégorie. Le joueur doit trouver une réponse qui satisfait simultanément la catégorie de sa ligne ET de sa colonne. 3 erreurs maximum.
🌐 doku-mu.vercel.app

Thèmes disponibles
ThèmeEntrées⚽Équipe de France56 joueurs depuis 1998🗺️Villes de France136 grandes villes🧭Villes de France Expert157 communes🎬Films Cultes258 films internationaux🐾Animaux du monde209 animaux

Comment ça marche
L'architecture est 100% statique — pas de serveur, pas de base de données. Tout repose sur des fichiers JSON hébergés sur GitHub et servis automatiquement par Vercel.
data/{theme}/entries.json      ← qui peut être une réponse et avec quels attributs
data/{theme}/categories.json   ← quelles catégories apparaissent sur la grille
        ↓
generate.py                    ← calcule toutes les combinaisons valides
        ↓
grilles/{theme}.json           ← grilles précalculées pour 60 jours
        ↓
GitHub → Vercel → navigateur
        ↓
jeu.html charge les données du thème et affiche la grille du jour
Quand un joueur ouvre jeu.html?theme=foot, le site charge data/foot/foot_entries.json et grilles/foot.json en parallèle, trouve la grille correspondant à la date du jour, et valide les réponses en temps réel côté navigateur.

Structure du repo
Doku/
├── data/                              ← tu modifies ici
│   ├── themes.json                    ← catalogue central des thèmes
│   ├── foot/
│   │   ├── foot_entries.json          ← liste des joueurs avec attributs
│   │   └── foot_categories.json      ← catégories du thème foot
│   ├── films/
│   ├── villes/
│   │   ├── villes casu/
│   │   └── villes expert/
│   └── animaux/
├── grilles/                           ← généré automatiquement
│   ├── foot.json
│   ├── films.json
│   ├── villes-casu.json
│   ├── villes-expert.json
│   └── animaux.json
├── index.html                         ← page d'accueil, ne pas modifier
├── jeu.html                           ← moteur de jeu générique, ne pas modifier
└── generate.py                        ← script local uniquement

Maintenance
Regénérer les grilles (une fois par mois)
bashpython generate.py --days 60
Puis uploader les fichiers du dossier grilles/ sur GitHub. Vercel met à jour le site en 30 secondes.
Modifier un thème existant
Ouvrir data/{theme}/{theme}_entries.json, faire les modifications, relancer le script pour ce thème uniquement :
bashpython generate.py --theme animaux --days 60
Ajouter un nouveau thème

Créer data/nouveau-theme/ avec deux fichiers : entries.json et categories.json
Ajouter une entrée dans data/themes.json
Lancer python generate.py --theme nouveau-theme --days 60
Uploader grilles/nouveau-theme.json sur GitHub
Ajouter le chemin dans le mapping de jeu.html

index.html et jeu.html ne changent jamais pour les étapes 1 à 4.

Stack

Frontend : HTML / CSS / JavaScript vanilla
Hébergement : Vercel, déploiement automatique depuis GitHub
Données : fichiers JSON statiques, aucune base de données
Génération : Python 3, exécuté localement


Contributeurs : wolvyboss · ClementdeLoubresse
