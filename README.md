# geoviz

Visualisation géographique de données généalogiques.

Pipeline : données source → geocoding Python (geo.api.gouv.fr) → carte interactive Leaflet.js.

## Lancer en local

```bash
python3 geocode/csv_to_json.py
python3 geocode/geocode.py
python3 -m http.server 8000
# puis ouvrir http://localhost:8000/viz/
```
