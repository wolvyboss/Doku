#!/usr/bin/env python3
"""
Doku — Générateur de grilles quotidiennes
==========================================
Lit les bases de données dans data/ et génère tous les JSONs de grilles.

Usage :
  python3 generate.py --days 60
  python3 generate.py --days 30 --from 2026-06-01
  python3 generate.py --days 60 --theme foot
  python3 generate.py --days 60 --theme films
  python3 generate.py --days 60 --theme villes-casu
  python3 generate.py --days 60 --theme villes-expert
"""

import json, random, argparse, unicodedata
from datetime import date, timedelta
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# CHARGEMENT DES BASES DE DONNÉES
# ─────────────────────────────────────────────────────────────
def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# ─────────────────────────────────────────────────────────────
# CATALOGUES DE CATÉGORIES PAR THÈME
# ─────────────────────────────────────────────────────────────

CATS_FOOT = [
    ("cdm_1998","Coupe du Monde 1998","🏆"), ("cdm_2002","Coupe du Monde 2002","🏆"),
    ("cdm_2006","Coupe du Monde 2006","🏆"), ("cdm_2010","Coupe du Monde 2010","🏆"),
    ("cdm_2014","Coupe du Monde 2014","🏆"), ("cdm_2018","Coupe du Monde 2018","🏆"),
    ("cdm_2022","Coupe du Monde 2022","🏆"),
    ("euro_1996","Euro 1996","🥈"), ("euro_2000","Euro 2000","🏅"),
    ("euro_2008","Euro 2008","🥈"), ("euro_2012","Euro 2012","🥈"),
    ("euro_2016","Euro 2016","🥈"), ("euro_2020","Euro 2020","🥈"),
    ("euro_2024","Euro 2024","🥈"),
    ("ch98","Champion du Monde 1998","🥇"), ("ch18","Champion du Monde 2018","🥇"),
    ("pl","Premier League","🏴󠁧󠁢󠁥󠁮󠁧󠁿"), ("liga","La Liga","🇪🇸"),
    ("serieA","Serie A","🇮🇹"), ("bund","Bundesliga","🇩🇪"),
    ("pos_gardien","Gardien","🧤"), ("pos_défenseur","Défenseur","🛡️"),
    ("pos_milieu","Milieu","⚙️"), ("pos_attaquant","Attaquant","⚡"),
    ("d90","Actif dans les années 90","📅"), ("d00","Actif dans les années 2000","📅"),
    ("d10","Actif dans les années 2010","📅"), ("d20","Actif dans les années 2020","📅"),
    ("mrs","A joué à Marseille","🔵"), ("mco","A joué à Monaco","🔴"),
    ("lyon","A joué à Lyon","🦁"), ("bx","A joué à Bordeaux","🟣"),
    ("psg","A joué au PSG","🔵"), ("rennes","A joué à Rennes","🔴"),
    ("nice","A joué à Nice","🔴"), ("lille","A joué à Lille","🐘"),
    ("lens","A joué à Lens","🟡"), ("nantes","A joué à Nantes","🐦"),
    ("mtp","A joué à Montpellier","🟠"), ("tlse","A joué à Toulouse","🟣"),
    ("s21","21 à 50 sélections","👕"), ("s51","51 à 100 sélections","👕"),
    ("s100","100+ sélections","⭐"),
    ("tl1","Vainqueur Ligue 1","🏅"), ("teu","Vainqueur Coupe Europe","🌟"),
]

CATS_VILLES = [
    ("pop_500k+","Plus de 500 000 habitants","🏙️"),
    ("pop_100k+","Plus de 100 000 habitants","🏙️"),
    ("pop_50k+","Plus de 50 000 habitants","🏘️"),
    ("pop_20k+","Plus de 20 000 habitants","🏘️"),
    ("pop_10k+","Plus de 10 000 habitants","🏡"),
    ("reg_idf","Île-de-France","🗼"), ("reg_ara","Auvergne-Rhône-Alpes","⛰️"),
    ("reg_paca","PACA","☀️"), ("reg_occ","Occitanie","🌻"),
    ("reg_naq","Nouvelle-Aquitaine","🍷"), ("reg_gest","Grand Est","🥨"),
    ("reg_hdf","Hauts-de-France","🌾"), ("reg_nor","Normandie","🐄"),
    ("reg_bre","Bretagne","⚓"), ("reg_pdl","Pays de la Loire","🏰"),
    ("reg_cvl","Centre-Val de Loire","🏰"), ("reg_bfc","Bourgogne-Franche-Comté","🍇"),
    ("reg_cor","Corse","🌴"), ("reg_reunion","La Réunion","🌋"),
    ("reg_mart","Martinique","🌴"), ("reg_guad","Guadeloupe","🌺"),
    ("reg_guy","Guyane","🌿"),
    ("ligue1","Club en Ligue 1","⚽"), ("ligue2","Club en Ligue 2","🥈"),
    ("prefecture_reg","Préfecture de région","🏛️"),
    ("prefecture_dept","Préfecture de département","🏛️"),
    ("port_maritime","Port maritime","⚓"),
    ("fleuve_seine","Traversée par la Seine","🌊"),
    ("fleuve_loire","Traversée par la Loire","🌊"),
    ("fleuve_rhone","Traversée par le Rhône","🌊"),
    ("fleuve_garonne","Traversée par la Garonne","🌊"),
    ("fleuve_rhin","Traversée par le Rhin","🌊"),
    ("station_ski","Station de ski","⛷️"),
    ("station_balneaire","Station balnéaire","🏖️"),
    ("ville_thermale","Ville thermale","💧"),
    ("patrimoine_unesco","Patrimoine UNESCO","🏛️"),
    ("universite","Ville universitaire","🎓"),
    ("jo2024","Ville hôte JO 2024","🏅"),
    ("metro","Réseau de métro","🚇"),
    ("tgv","Gare TGV","🚄"),
    ("dom_tom","DOM-TOM","🌴"),
    ("lettre_a","Commence par A","🔤"), ("lettre_b","Commence par B","🔤"),
    ("lettre_c","Commence par C","🔤"), ("lettre_d","Commence par D","🔤"),
    ("lettre_e","Commence par E","🔤"), ("lettre_f","Commence par F","🔤"),
    ("lettre_g","Commence par G","🔤"), ("lettre_l","Commence par L","🔤"),
    ("lettre_m","Commence par M","🔤"), ("lettre_n","Commence par N","🔤"),
    ("lettre_p","Commence par P","🔤"), ("lettre_r","Commence par R","🔤"),
    ("lettre_s","Commence par S","🔤"), ("lettre_t","Commence par T","🔤"),
    ("lettre_v","Commence par V","🔤"),
    ("fin_on","Se termine en '-on'","🔡"), ("fin_es","Se termine en '-es'","🔡"),
    ("fin_ille","Se termine en '-ille'","🔡"), ("fin_ais","Se termine en '-ais'","🔡"),
    ("fin_ens","Se termine en '-ens'","🔡"), ("fin_an","Se termine en '-an'","🔡"),
    ("fin_ois","Se termine en '-ois'","🔡"), ("fin_ers","Se termine en '-ers'","🔡"),
    ("fin_aux","Se termine en '-aux'","🔡"), ("fin_ours","Se termine en '-ours'","🔡"),
    ("fin_eau","Se termine en '-eau'","🔡"),
]

CATS_FILMS = [
    ("dec_40","Années 40","🎞️"), ("dec_50","Années 50","🎬"),
    ("dec_60","Années 60","🎬"), ("dec_70","Années 70","📽️"),
    ("dec_80","Années 80","📼"), ("dec_90","Années 90","💿"),
    ("dec_00","Années 2000","💿"), ("dec_10","Années 2010","🎥"),
    ("dec_20","Années 2020","🎥"),
    ("genre_action","Film d'action","💥"), ("genre_comedie","Comédie","😂"),
    ("genre_drame","Drame","🎭"), ("genre_sf","Science-fiction","🚀"),
    ("genre_horreur","Film d'horreur","👻"), ("genre_animation","Film d'animation","🎨"),
    ("genre_thriller","Thriller","🔪"), ("genre_aventure","Film d'aventure","🗺️"),
    ("genre_fantastique","Fantastique","🧙"), ("genre_western","Western","🤠"),
    ("real_kubrick","Réalisé par Kubrick","🎬"),
    ("real_spielberg","Réalisé par Spielberg","🎬"),
    ("real_scorsese","Réalisé par Scorsese","🎬"),
    ("real_tarantino","Réalisé par Tarantino","🎬"),
    ("real_nolan","Réalisé par Nolan","🎬"),
    ("real_cameron","Réalisé par Cameron","🎬"),
    ("real_coppola","Réalisé par Coppola","🎬"),
    ("real_villeneuve","Réalisé par Villeneuve","🎬"),
    ("real_fincher","Réalisé par Fincher","🎬"),
    ("real_coen","Réalisé par les Coen","🎬"),
    ("real_anderson","Réalisé par Wes Anderson","🎬"),
    ("real_scott","Réalisé par Ridley Scott","🎬"),
    ("real_kurosawa","Réalisé par Kurosawa","🎬"),
    ("real_miyazaki","Réalisé par Miyazaki","🎬"),
    ("real_hitchcock","Réalisé par Hitchcock","🎬"),
    ("real_chazelle","Réalisé par Chazelle","🎬"),
    ("real_fellini","Réalisé par Fellini","🎬"),
    ("real_bergman","Réalisé par Bergman","🎬"),
    ("real_leone","Réalisé par Sergio Leone","🎬"),
    ("real_bongjoho","Réalisé par Bong Joon-ho","🎬"),
    ("real_inarritu","Réalisé par Iñárritu","🎬"),
    ("real_cuaron","Réalisé par Cuarón","🎬"),
    ("real_besson","Réalisé par Luc Besson","🎬"),
    ("real_lynch","Réalisé par David Lynch","🎬"),
    ("real_aronofsky","Réalisé par Aronofsky","🎬"),
    ("real_zemeckis","Réalisé par Zemeckis","🎬"),
    ("real_lanthimos","Réalisé par Lanthimos","🎬"),
    ("real_gerwig","Réalisé par Greta Gerwig","🎬"),
    ("real_eggers","Réalisé par Robert Eggers","🎬"),
    ("real_peele","Réalisé par Jordan Peele","🎬"),
    ("real_aster","Réalisé par Ari Aster","🎬"),
    ("real_haneke","Réalisé par Michael Haneke","🎬"),
    ("real_ang","Réalisé par Ang Lee","🎬"),
    ("real_lumet","Réalisé par Sidney Lumet","🎬"),
    ("pays_usa","Production américaine","🇺🇸"),
    ("pays_uk","Production britannique","🇬🇧"),
    ("pays_france","Production française","🇫🇷"),
    ("pays_italie","Production italienne","🇮🇹"),
    ("pays_japon","Production japonaise","🇯🇵"),
    ("pays_coree","Production coréenne","🇰🇷"),
    ("pays_allemagne","Production allemande","🇩🇪"),
    ("pays_canada","Production canadienne","🇨🇦"),
    ("pays_mexique","Production mexicaine","🇲🇽"),
    ("pays_suede","Production suédoise","🇸🇪"),
    ("pays_nz","Production néo-zélandaise","🇳🇿"),
    ("pays_australia","Production australienne","🇦🇺"),
    ("note_9plus","Note IMDb ≥ 9/10","⭐"),
    ("bo_1milliard","Plus d'1 milliard $ au box-office","💰"),
    ("bo_500m","Plus de 500M$ au box-office","💵"),
    ("oscar_film","Oscar du meilleur film","🏆"),
    ("oscar_real","Oscar du meilleur réalisateur","🏆"),
    ("oscar_etranger","Oscar du meilleur film étranger","🏆"),
    ("oscar_animation","Oscar du meilleur film animé","🏆"),
    ("franchise_marvel","Univers Marvel","🦸"),
    ("franchise_starwars","Saga Star Wars","⚔️"),
    ("franchise_lotr","Le Seigneur des Anneaux","💍"),
    ("franchise_pixar","Film Pixar","🔵"),
    ("franchise_batman","Franchise Batman","🦇"),
    ("franchise_alien","Franchise Alien","👾"),
    ("franchise_matrix","Franchise Matrix","💊"),
    ("franchise_indiana","Indiana Jones","🎩"),
    ("franchise_avatar","Franchise Avatar","🌿"),
    ("franchise_dune","Saga Dune","🏜️"),
    ("franchise_jurassic","Jurassic Park","🦕"),
    ("franchise_madmax","Franchise Mad Max","🚗"),
    ("franchise_bttf","Retour vers le futur","⏰"),
    ("dur_2h30plus","Durée supérieure à 2h30","⏱️"),
    ("dur_3h","Durée supérieure à 3h","⏱️"),
    ("langue_fr","Tourné en français","🗣️"),
    ("langue_ja","Tourné en japonais","🗣️"),
    ("langue_de","Tourné en allemand","🗣️"),
    ("langue_it","Tourné en italien","🗣️"),
    ("acteur_dicaprio","Avec Leonardo DiCaprio","🎭"),
    ("acteur_hanks","Avec Tom Hanks","🎭"),
    ("acteur_pitt","Avec Brad Pitt","🎭"),
]

# ─────────────────────────────────────────────────────────────
# FAMILLES DE CATÉGORIES PAR THÈME
# ─────────────────────────────────────────────────────────────

def get_famille_foot(cat_id):
    if cat_id.startswith("cdm_"):   return "cdm"
    if cat_id.startswith("euro_"):  return "euro"
    if cat_id.startswith("pos_"):   return "poste"
    if cat_id.startswith("d"):      return "decennie"
    if cat_id.startswith("s"):      return "selections"
    if cat_id in ("pl","liga","serieA","bund"): return "ligue"
    if cat_id in ("tl1","teu"):     return "titre"
    if cat_id in ("ch98","ch18"):   return "champion"
    return "club_fr"

def get_famille_villes(cat_id):
    if cat_id.startswith("pop_"):          return "population"
    if cat_id.startswith("reg_"):          return "region"
    if cat_id.startswith("fleuve_"):       return "fleuve"
    if cat_id.startswith("lettre_"):       return "lettre"
    if cat_id.startswith("fin_"):          return "terminaison"
    if cat_id in ("ligue1","ligue2"):      return "foot"
    if cat_id.startswith("prefecture_"):   return "prefecture"
    if cat_id in ("station_ski","station_balneaire","ville_thermale"): return "tourisme"
    if cat_id == "port_maritime":          return "maritime"
    if cat_id in ("metro","tgv"):          return "transport"
    return cat_id

def get_famille_films(cat_id):
    if cat_id.startswith("dec_"):       return "decennie"
    if cat_id.startswith("genre_"):     return "genre"
    if cat_id.startswith("real_"):      return "realisateur"
    if cat_id.startswith("pays_"):      return "pays"
    if cat_id.startswith("oscar_"):     return "oscar"
    if cat_id.startswith("bo_"):        return "boxoffice"
    if cat_id.startswith("franchise_"): return "franchise"
    if cat_id.startswith("dur_"):       return "duree"
    if cat_id.startswith("langue_"):    return "langue"
    if cat_id.startswith("acteur_"):    return "acteur"
    if cat_id.startswith("note_"):      return "note"
    return cat_id

FAMILLES_STRICTES_FOOT   = {"cdm","euro","ligue","decennie","poste","selections"}
FAMILLES_STRICTES_VILLES = {"population","region","fleuve","foot","prefecture","transport"}
FAMILLES_STRICTES_FILMS  = {"decennie","genre","pays","langue"}

# ─────────────────────────────────────────────────────────────
# PRÉPARATION DES DONNÉES VILLES (ajout attrs lettres)
# ─────────────────────────────────────────────────────────────

def normalize(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

LETTRES_OK   = set('abcdefglmnprstv')
TERMINAISONS = ['on','es','ille','ais','ens','an','ois','ers','aux','ours','eau']

def enrich_villes(villes):
    for v in villes:
        nom = v["name"]
        # Prendre le dernier mot du nom pour les villes composées
        nom_clean = normalize(nom.split('-')[0].split(' ')[-1])
        if nom_clean and nom_clean[0] in LETTRES_OK:
            attr = f"lettre_{nom_clean[0]}"
            if attr not in v["attrs"]:
                v["attrs"].append(attr)
        for term in TERMINAISONS:
            if nom_clean.endswith(term):
                attr = f"fin_{term}"
                if attr not in v["attrs"]:
                    v["attrs"].append(attr)
                break
    return villes

# ─────────────────────────────────────────────────────────────
# MOTEUR DE GÉNÉRATION (générique)
# ─────────────────────────────────────────────────────────────

def match(item, cat_id):
    """Vérifie si un item correspond à une catégorie."""
    if cat_id.startswith("pos_"):
        return item.get("pos") == cat_id[4:]
    return cat_id in item.get("attrs", [])

def build_compat(items, categories, seuil=2):
    """Précalcule toutes les paires de catégories compatibles."""
    cat_ids = list(dict.fromkeys(c[0] for c in categories))
    compat = {}
    for i, a in enumerate(cat_ids):
        set_a = {it["name"] for it in items if match(it, a)}
        for b in cat_ids[i+1:]:
            set_b = {it["name"] for it in items if match(it, b)}
            communs = list(set_a & set_b)
            if len(communs) >= seuil:
                compat[(a,b)] = communs
                compat[(b,a)] = communs
    return compat, cat_ids

def cat_label(cat_id, categories):
    for cid, label, icon in categories:
        if cid == cat_id: return label, icon
    return cat_id, "❓"

def triplet_ok(triplet, get_famille, familles_strictes):
    fams = [get_famille(c) for c in triplet]
    return all(fams.count(f) <= 1 for f in familles_strictes)

def generate_grille(seed, compat, cat_ids, get_famille, familles_strictes, difficulte=0.5):
    rng = random.Random(seed)
    voisins = defaultdict(set)
    for (a,b) in compat:
        voisins[a].add(b)
    cats_sorted = sorted(cat_ids, key=lambda c: -len(voisins[c]))
    pool = cats_sorted[:50]
    best, best_diff = None, 999
    for _ in range(20000):
        rows = rng.sample(pool, 3)
        if not triplet_ok(rows, get_famille, familles_strictes): continue
        cols_ok = [c for c in cat_ids if c not in rows and
                   all((r,c) in compat or (c,r) in compat for r in rows)]
        if len(cols_ok) < 3: continue
        cols = rng.sample(cols_ok, 3)
        if not triplet_ok(cols, get_famille, familles_strictes): continue
        counts = []
        for r in rows:
            for c in cols:
                key = (r,c) if (r,c) in compat else (c,r)
                counts.append(len(compat.get(key,[])))
        avg = sum(counts)/9
        score = max(0, min(1, 1-(avg-3)/15))
        diff = abs(score-difficulte)
        if diff < best_diff:
            best_diff = diff
            best = (rows, cols, round(score,2), min(counts), round(avg,1))
        if best_diff < 0.05: break
    return best

def generate_theme(theme_name, items, categories, get_famille, familles_strictes,
                   start_date, nb_days, seed_offset=0, seuil=2):
    """Génère toutes les grilles pour un thème."""
    print(f"\n{'─'*50}")
    print(f"🎮 Thème : {theme_name}")
    print(f"   {len(items)} entrées")
    compat, cat_ids = build_compat(items, categories, seuil)
    print(f"   {len(cat_ids)} catégories · {len(compat)//2} paires compatibles")
    print(f"{'─'*50}")

    grilles = []
    for i in range(nb_days):
        current = start_date + timedelta(days=i)
        seed = int(current.strftime("%Y%m%d")) + seed_offset
        jour = current.weekday()
        difficulte = 0.2 + jour * 0.11
        result = generate_grille(seed, compat, cat_ids, get_famille,
                                  familles_strictes, difficulte)
        if not result:
            print(f"   ❌ {current} : impossible")
            continue
        rows, cols, score, min_case, avg = result
        cellules = {}
        for ri, r in enumerate(rows):
            for ci, c in enumerate(cols):
                key = (r,c) if (r,c) in compat else (c,r)
                cellules[str(ri*3+ci)] = compat.get(key,[])
        lignes_data   = [{"id":r,"label":cat_label(r,categories)[0],
                          "icon":cat_label(r,categories)[1]} for r in rows]
        colonnes_data = [{"id":c,"label":cat_label(c,categories)[0],
                          "icon":cat_label(c,categories)[1]} for c in cols]
        diff_emoji = "🟢" if score<0.35 else "🟡" if score<0.65 else "🔴"
        print(f"   ✅ {current} {diff_emoji} (moy. {avg} / case, min {min_case})")
        grilles.append({
            "date": str(current),
            "theme": theme_name,
            "difficulte": score,
            "stats": {"moyenne": avg, "min": min_case},
            "lignes": lignes_data,
            "colonnes": colonnes_data,
            "cellules": cellules,
        })
    return grilles

def save(grilles, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(grilles, f, ensure_ascii=False, indent=2)
    print(f"\n   💾 {len(grilles)} grilles → {path}")

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Génère toutes les grilles Doku")
    parser.add_argument("--days",  type=int, default=60, help="Nombre de jours")
    parser.add_argument("--from",  dest="start", default=None, help="Date de début YYYY-MM-DD")
    parser.add_argument("--theme", default="all",
                        choices=["all","foot","villes-casu","villes-expert","films"],
                        help="Thème à générer (défaut: all)")
    args = parser.parse_args()

    start = date.today()
    if args.start:
        start = date.fromisoformat(args.start)

    print(f"\n🚀 Génération Doku — {args.days} jours depuis {start}")
    print(f"   Thème : {args.theme}")

    # Charger les bases
    players = load('data/players.json')
    villes  = enrich_villes(load('data/villes.json'))
    films   = load('data/films.json')

    villes_casu   = [v for v in villes if "pop_20k+" in v["attrs"]]
    villes_expert = villes  # toutes les villes

    themes = {
        "foot":          (players, CATS_FOOT,   get_famille_foot,   FAMILLES_STRICTES_FOOT,   0, 3, "grilles-foot.json"),
        "villes-casu":   (villes_casu,  CATS_VILLES, get_famille_villes, FAMILLES_STRICTES_VILLES, 1, 2, "grilles-villes-casu.json"),
        "villes-expert": (villes_expert, CATS_VILLES, get_famille_villes, FAMILLES_STRICTES_VILLES, 2, 2, "grilles-villes-expert.json"),
        "films":         (films,  CATS_FILMS,  get_famille_films,  FAMILLES_STRICTES_FILMS,  3, 2, "grilles-films.json"),
    }

    to_generate = themes.keys() if args.theme == "all" else [args.theme]

    for theme_name in to_generate:
        items, cats, get_fam, fam_strictes, offset, seuil, outfile = themes[theme_name]
        grilles = generate_theme(
            theme_name, items, cats, get_fam, fam_strictes,
            start, args.days, seed_offset=offset, seuil=seuil
        )
        save(grilles, outfile)

    print(f"\n✅ Terminé — uploade les fichiers JSON sur GitHub\n")
