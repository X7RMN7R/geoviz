# geoviz

Outil de visualisation géographique de données généalogiques — projet d'exploration personnel.

## Objectifs

- Expérimenter la création d'outils avec l'aide de l'IA
- Creuser le sujet de la visualisation géographique (geocoding, cartographie web)
- Avoir un cas d'usage concret et personnel comme prétexte

## Architecture envisagée

```
geoviz/
├── data/
│   └── arbre.json       # Données généalogiques source
├── geocode/
│   └── geocode.py       # Script Python : enrichissement lat/lon des communes
├── viz/
│   ├── index.html       # Carte interactive
│   ├── app.js           # Logique de visualisation
│   └── style.css        # Styles
└── README.md
```

## Format de données

Le fichier source `data/arbre.json` contient un tableau de personnes avec les champs :

| Champ            | Type    | Description                        |
|------------------|---------|------------------------------------|
| `nom`            | string  | Nom complet                        |
| `generation`     | integer | Numéro de génération (1 = moi)     |
| `commune`        | string  | Commune de naissance               |
| `departement`    | integer | Numéro de département              |
| `annee_naissance`| integer | Année de naissance                 |

L'étape de geocoding enrichira chaque entrée avec `lat` et `lon`.

## Pipeline de traitement

1. **Geocoding** (`geocode/geocode.py`) — résoudre `commune + departement` → `lat/lon` via l'API geo.api.gouv.fr
2. **Visualisation** (`viz/index.html`) — afficher les points sur une carte Leaflet.js, colorés par génération

## Pistes d'évolution

- Afficher les liens familiaux (arêtes entre parents et enfants)
- Supporter le format GEDCOM en entrée
- **Visualisation temporelle** — utiliser `annee_naissance` pour animer la carte dans le temps (les ancêtres apparaissent selon leur époque), avec des marqueurs pour les événements historiques majeurs sur la timeline (Révolution française, guerres, exode rural…) pour contextualiser les migrations familiales
- **Panneau "tops"** — afficher des stats en sidebar : commune avec le plus d'ancêtres (ex: Loctudy), département le plus représenté, génération la plus dispersée géographiquement…

## Déploiement (à faire)

Rendre la carte accessible à la famille nécessite un hébergement. Pistes à explorer :

- **GitHub Pages** — hébergement statique gratuit, idéal pour une page HTML/JS sans backend
- **Netlify / Vercel** — même principe, déploiement par drag & drop ou via Git
- **Serveur personnel** — plus de contrôle, mais plus de setup

Le plus simple sera probablement GitHub Pages : pousser le repo sur GitHub et activer Pages sur le dossier `viz/`.
# geoviz
