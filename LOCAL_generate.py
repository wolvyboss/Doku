#!/usr/bin/env python3
"""
DOKU — Générateur de grilles quotidiennes
==========================================
Lit data/themes.json et data/{theme}/entries.json + categories.json
Génère grilles/{theme}.json pour chaque thème actif.

Usage :
  python generate.py --days 60
  python generate.py --days 60 --theme foot
  python generate.py --days 30 --from 2026-07-01
"""
import json, random, argparse, unicodedata, os
from datetime import date, timedelta
from collections import defaultdict

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# Enrichissement automatique des villes (lettres + terminaisons)
LETTRES_OK   = set('abcdefglmnprstv')
TERMINAISONS = ['on','es','ille','ais','ens','an','ois','ers','aux','ours','eau']

def normalize(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

def enrich_villes(entries):
    for v in entries:
        nom_clean = normalize(v["name"].split('-')[0].split(' ')[-1])
        if nom_clean and nom_clean[0] in LETTRES_OK:
            attr = f"lettre_{nom_clean[0]}"
            if attr not in v["attrs"]: v["attrs"].append(attr)
        for term in TERMINAISONS:
            if nom_clean.endswith(term):
                attr = f"fin_{term}"
                if attr not in v["attrs"]: v["attrs"].append(attr)
                break
    return entries

# Moteur générique
def match(item, cat_id):
    if cat_id.startswith("pos_"):
        return item.get("pos") == cat_id[4:]
    return cat_id in item.get("attrs", [])

def build_compat(entries, categories, seuil=2):
    cat_ids = [c["id"] for c in categories]
    compat = {}
    for i, a in enumerate(cat_ids):
        set_a = {it["name"] for it in entries if match(it, a)}
        for b in cat_ids[i+1:]:
            set_b = {it["name"] for it in entries if match(it, b)}
            communs = list(set_a & set_b)
            if len(communs) >= seuil:
                compat[(a,b)] = communs
                compat[(b,a)] = communs
    return compat, cat_ids

def get_label(cat_id, categories):
    for c in categories:
        if c["id"] == cat_id: return c["label"], c["icon"]
    return cat_id, "❓"

def triplet_ok(triplet, categories, familles_strictes):
    famille_map = {c["id"]: c.get("famille", c["id"]) for c in categories}
    fams = [famille_map.get(c, c) for c in triplet]
    return all(fams.count(f) <= 1 for f in familles_strictes)

def generate_grille(seed, compat, cat_ids, categories, familles_strictes, difficulte=0.5):
    rng = random.Random(seed)
    voisins = defaultdict(set)
    for (a,b) in compat: voisins[a].add(b)
    pool = sorted(cat_ids, key=lambda c: -len(voisins[c]))[:50]
    best, best_diff = None, 999
    for _ in range(20000):
        rows = rng.sample(pool, 3)
        if not triplet_ok(rows, categories, familles_strictes): continue
        cols_ok = [c for c in cat_ids if c not in rows and
                   all((r,c) in compat or (c,r) in compat for r in rows)]
        if len(cols_ok) < 3: continue
        cols = rng.sample(cols_ok, 3)
        if not triplet_ok(cols, categories, familles_strictes): continue
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

def generate_theme(theme, entries, categories, start_date, nb_days):
    tid = theme["id"]
    seuil = theme.get("seuil", 2)
    offset = theme.get("seed_offset", 0)
    familles_strictes = theme.get("familles_strictes", [])

    if "villes" in tid:
        entries = enrich_villes(entries)

    print(f"\n{'─'*50}")
    print(f"🎮 {theme['label']} ({len(entries)} entrées)")
    compat, cat_ids = build_compat(entries, categories, seuil)
    print(f"   {len(cat_ids)} catégories · {len(compat)//2} paires compatibles")

    grilles = []
    for i in range(nb_days):
        current = start_date + timedelta(days=i)
        seed = int(current.strftime("%Y%m%d")) + offset
        jour = current.weekday()
        difficulte = 0.2 + jour * 0.11
        result = generate_grille(seed, compat, cat_ids, categories, familles_strictes, difficulte)
        if not result:
            print(f"   ❌ {current} : impossible")
            continue
        rows, cols, score, min_case, avg = result
        cellules = {}
        for ri, r in enumerate(rows):
            for ci, c in enumerate(cols):
                key = (r,c) if (r,c) in compat else (c,r)
                cellules[str(ri*3+ci)] = compat.get(key,[])
        diff_e = "🟢" if score<0.35 else "🟡" if score<0.65 else "🔴"
        print(f"   ✅ {current} {diff_e} (moy. {avg}/case)")
        grilles.append({
            "date": str(current), "theme": tid,
            "difficulte": score,
            "stats": {"moyenne": avg, "min": min_case},
            "lignes":   [{"id":r,"label":get_label(r,categories)[0],"icon":get_label(r,categories)[1]} for r in rows],
            "colonnes": [{"id":c,"label":get_label(c,categories)[0],"icon":get_label(c,categories)[1]} for c in cols],
            "cellules": cellules,
        })
    return grilles

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",  type=int, default=60)
    parser.add_argument("--from",  dest="start", default=None)
    parser.add_argument("--theme", default="all")
    args = parser.parse_args()

    start = date.today()
    if args.start: start = date.fromisoformat(args.start)

    os.makedirs("grilles", exist_ok=True)
    themes = load("data/themes.json")
    if args.theme != "all":
        themes = [t for t in themes if t["id"] == args.theme]

    print(f"\n🚀 DOKU — {args.days} jours depuis {start}\n")

    for theme in themes:
        if not theme.get("active", True):
            print(f"⏭️  {theme['label']} ignoré")
            continue
        entries    = load(f"data/{theme['id']}/entries.json")
        categories = load(f"data/{theme['id']}/categories.json")
        grilles = generate_theme(theme, entries, categories, start, args.days)
        out = f"grilles/{theme['id']}.json"
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(grilles, f, ensure_ascii=False, indent=2)
        print(f"   💾 {len(grilles)} grilles → {out}")

    print(f"\n✅ Terminé. Uploade le dossier grilles/ sur GitHub.\n")
