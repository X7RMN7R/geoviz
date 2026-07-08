"""
geocode.py — Enrichit arbre.json avec les coordonnées GPS (lat/lon) de chaque commune.

Utilise l'API geo.api.gouv.fr (gratuite, sans clé, données France métropolitaine + DOM).

Usage :
    python geocode.py
    python geocode.py --input ../data/arbre.json --output ../data/arbre_geocoded.json
"""

import json
import time
import argparse
from pathlib import Path

import requests

API_URL = "https://geo.api.gouv.fr/communes"

# Communes fusionnées ou renommées : ancien nom → nom actuel reconnu par l'API
# Ajouter ici les cas identifiés lors du geocoding.
ALIASES: dict[str, str] = {
    "Chaillé sous les Ormeaux": "Rives-de-l'Yon",
    "Saint Florent des Bois": "Rives-de-l'Yon",
    "Piré": "Piré-Chancé",
    "Bellenoue": "Château-Guibert",
}


def geocode_commune(commune: str, departement: int | None) -> tuple[float, float] | None:
    """
    Retourne (lat, lon) pour une commune + département donnés.
    Si la recherche avec département échoue, retente sans département.
    Retourne None si la commune est introuvable.
    """
    def _appel(params: dict) -> tuple[float, float] | None:
        try:
            response = requests.get(API_URL, params=params, timeout=5)
            response.raise_for_status()
            results = response.json()
            if results:
                coords = results[0].get("centre", {}).get("coordinates")
                if coords:
                    lon, lat = coords  # GeoJSON : [longitude, latitude]
                    return lat, lon
        except requests.RequestException as e:
            print(f"  ⚠ Erreur réseau pour '{commune}' : {e}")
        return None

    base = {"fields": "centre", "format": "json", "geometry": "centre"}

    # 1er essai : avec département
    if departement:
        result = _appel({**base, "nom": commune, "codeDepartement": str(departement).zfill(2)})
        if result:
            return result
        print(f"    ↳ Introuvable avec dept {departement}, nouvel essai sans département…")

    # 2e essai : sans département (utile pour les communes fusionnées avec nom ambigu)
    return _appel({**base, "nom": commune})


def main(input_path: Path, output_path: Path) -> None:
    with open(input_path, encoding="utf-8") as f:
        personnes = json.load(f)

    print(f"→ {len(personnes)} personne(s) à géocoder\n")

    enrichies = []
    non_trouvees = []

    for personne in personnes:
        commune_originale = personne.get("commune", "")
        departement = personne.get("departement")
        nom = personne.get("nom", "?")

        if not commune_originale:
            enrichies.append({**personne, "lat": None, "lon": None})
            continue

        # Appliquer l'alias si la commune a été fusionnée/renommée
        commune_recherche = ALIASES.get(commune_originale, commune_originale)
        if commune_recherche != commune_originale:
            print(f"  Geocoding : {nom} — {commune_originale} → {commune_recherche} ({departement})")
        else:
            print(f"  Geocoding : {nom} — {commune_originale} ({departement})")

        result = geocode_commune(commune_recherche, departement)

        if result:
            lat, lon = result
            print(f"    ✓ {lat:.5f}, {lon:.5f}")
            enrichie = {**personne, "lat": lat, "lon": lon}
        else:
            print(f"    ✗ Commune introuvable")
            non_trouvees.append(f"{nom} ({commune_originale})")
            enrichie = {**personne, "lat": None, "lon": None}

        enrichies.append(enrichie)
        time.sleep(0.1)  # délai poli entre les requêtes

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enrichies, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Fichier écrit : {output_path}")
    print(f"  Géocodés     : {len(enrichies) - len(non_trouvees)}/{len(enrichies)}")
    if non_trouvees:
        print(f"\n  ✗ Non trouvés ({len(non_trouvees)}) :")
        for n in non_trouvees:
            print(f"    - {n}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Geocode les communes d'un arbre généalogique.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "arbre.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "arbre_geocoded.json",
    )
    args = parser.parse_args()
    main(args.input, args.output)
