# BTCZ Tools

Suite d'outils desktop pour les mineurs **BitcoinZ (BTCZ)**.
Construit autour d'un **Data Layer commun** : une donnee reseau recuperee une fois est reutilisee par tous les modules.

**Multilingue** : 🇬🇧 EN (défaut), 🇫🇷 FR, 🇪🇸 ES, 🇩🇪 DE — changement à chaud via le sélecteur de la sidebar, langue mémorisée dans `data/settings.json`.
**Logo BTCZ** téléchargé au premier lancement et mis en cache dans `data/` (icône de fenêtre + sidebar).

## Modules

| Module | Etat | Description |
|---|---|---|
| 📊 Dashboard | fonctionnel | Vue reseau + marche en direct |
| ⛏️ Mining Tracker | fonctionnel | Rewards recus sur une adresse t1, par jour ou par periode, export CSV |
| 💰 Profitability | Phase 2 | Calculateur de rentabilite |
| 🌊 Pool Explorer | Phase 3 | Comparaison des pools |
| 🌐 Network Explorer | fonctionnel | Stats reseau + derniers blocs (avec mineur) |

## Architecture

```
BTCZTools/
├── app/
│   ├── main.py            point d'entree + navigation
│   ├── ui/                thème et widgets réutilisables
│   ├── core/              data layer, cache TTL, logs, erreurs
│   ├── api/               clients (insight, getbtcz, market)
│   ├── models/            modèles communs (NetworkStats, Block, ...)
│   └── utils/             format, calcul reward / nethash
├── modules/               un dossier par outil
├── config/                endpoints, TTL, constantes
└── data/                  cache local, historique, logs
```

## Sources de donnees

- **Network / blocs / mineur** : `explorer.btcz.rocks` (Insight, `getInfo` + `minedBy`)
- **Adresses** : `explorer.getbtcz.com` (principal) avec `btcz.rocks` en fallback
- **Prix** : CoinGecko (`bitcoinz`, EUR + USD)

Le Data Layer bascule automatiquement vers la source de secours si la principale echoue.

## Constantes reseau

- Block reward = `12500 / 2^(height // 840000)` -> **3125 BTCZ** actuellement
- Block time cible = 150 s
- Network hashrate affiche = recalcule (`difficulty x 2^32 / blocktime`), la valeur brute du noeud etant peu fiable

## Prerequis

- Python 3.10+
- Connexion internet

## Installation

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
# BTCZ-Tools
