DOKU — Guide contributeur
Le projet
Jeu de grille 3×3 quotidien. Site : doku-mu.vercel.app — hébergé sur Vercel, mis à jour automatiquement à chaque commit sur main.
Architecture
Tout est statique — fichiers JSON sur GitHub servis par Vercel. Pas de serveur, pas de base de données.
data/
├── themes.json          ← catalogue des thèmes (règles, couleurs, chips)
├── foot/
│   ├── foot_entries.json      ← réponses possibles + attributs
│   └── foot_categories.json  ← catégories de la grille + descriptions
├── films/ animaux/ villes/villes-casu/ villes/villes-expert/

grilles/
├── foot.json            ← grilles précalculées 60 jours (généré auto)
├── films.json / villes-casu.json / villes-expert.json / animaux.json

index.html               ← page d'accueil (ne pas modifier)
jeu.html                 ← moteur générique (ne pas modifier sauf mapping)
generate.py              ← script local uniquement

**Comment le jeu fonctionne**
Quand un joueur ouvre jeu.html?theme=foot :

Le navigateur charge data/foot/foot_entries.json — la liste des joueurs
Le navigateur charge grilles/foot.json — les grilles précalculées
Il trouve la grille dont la date correspond à aujourd'hui
Il affiche la grille et valide les réponses en comparant avec les entries

jeu.html est un moteur générique. Il ne connaît aucun thème en particulier — il lit juste l'URL, charge les bons fichiers, et fait tourner la logique.
Maintenance mensuelle
bashpython generate.py --days 60

# Uploader grilles/*.json sur GitHub
Ajouter un thème

Créer data/nouveau/nouveau_entries.json + nouveau_categories.json
Ajouter une ligne dans data/themes.json
Ajouter le chemin dans entriesPaths et catPaths dans jeu.html
Lancer generate.py --theme nouveau --days 60
Uploader grilles/nouveau.json

Points critiques

Ne jamais mettre d'apostrophe dans une string JS entre guillemets simples — ça casse tout le JS silencieusement
Toujours utiliser des tirets dans les noms de dossiers, jamais d'espaces
Après modification des entries, toujours régénérer les grilles
