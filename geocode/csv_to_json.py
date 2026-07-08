"""
csv_to_json.py — Convertit le CSV d'arbre généalogique en arbre.json.

Format CSV attendu :
  - Ligne 1 : numéros de génération (0, 1, 2, …), une génération = 2 colonnes (nom, lieu)
  - Lignes suivantes : une personne par ligne, positionnée dans la paire de colonnes
    correspondant à sa génération
  - Lieu au format "Commune (département)" — département et/ou commune peuvent être absents

Usage :
    python3 csv_to_json.py
    python3 csv_to_json.py --input ../data/source.csv --output ../data/arbre.json
"""

import csv
import json
import re
import argparse
from pathlib import Path


def parse_lieu(lieu: str) -> tuple[str | None, int | None]:
    """
    Parse "Commune (département)" → (commune, departement).
    Exemples :
        "Brest (29)"              → ("Brest", 29)
        "La Guerche de Bretagne"  → ("La Guerche de Bretagne", None)
        "?"                       → (None, None)
        ""                        → (None, None)
    """
    lieu = lieu.strip()

    if not lieu or lieu == "?":
        return None, None

    match = re.match(r"^(.+?)\s*\((\d{1,3}[AB]?)\)\s*$", lieu)
    if match:
        commune = match.group(1).strip()
        dept_str = match.group(2)
        try:
            departement = int(dept_str)
        except ValueError:
            departement = None  # cas "2A", "2B" — Corse, à gérer si besoin
        return commune, departement

    # Pas de département entre parenthèses
    return lieu, None


def convert(input_path: Path, output_path: Path) -> None:
    with open(input_path, encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if not rows:
        print("Fichier vide.")
        return

    # Ligne 0 : en-têtes de génération
    header = rows[0]
    # Nombre de générations = nombre de paires de colonnes
    nb_cols = len(header)
    nb_generations = nb_cols // 2

    personnes = []
    seen = set()  # pour dédoublonner (nom + génération)

    for row in rows[1:]:
        # Compléter la ligne si elle a moins de colonnes que l'en-tête
        row = row + [""] * (nb_cols - len(row))

        for gen in range(nb_generations):
            nom = row[gen * 2].strip()
            lieu = row[gen * 2 + 1].strip() if gen * 2 + 1 < len(row) else ""

            if not nom:
                continue

            cle = (nom, gen)
            if cle in seen:
                continue
            seen.add(cle)

            commune, departement = parse_lieu(lieu)

            personnes.append({
                "nom": nom,
                "generation": gen,
                "commune": commune,
                "departement": departement,
                "annee_naissance": None,
            })

    # Tri par génération puis nom
    personnes.sort(key=lambda p: (p["generation"], p["nom"]))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(personnes, f, ensure_ascii=False, indent=2)

    # Résumé
    print(f"✓ {len(personnes)} personnes exportées → {output_path}")
    manque_commune = sum(1 for p in personnes if not p["commune"])
    manque_dept    = sum(1 for p in personnes if p["commune"] and not p["departement"])
    if manque_commune:
        print(f"  ⚠ Commune manquante   : {manque_commune} personne(s)")
    if manque_dept:
        print(f"  ⚠ Département manquant : {manque_dept} personne(s) — geocoding moins fiable")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "Répartition Géographique - Feuille 1.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "arbre.json",
    )
    args = parser.parse_args()
    convert(args.input, args.output)
