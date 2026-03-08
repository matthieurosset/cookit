# Cookit

Gestionnaire de recettes personnel, auto-hébergé en Docker sur Synology NAS via Portainer.

## Stack

Flask + SQLite + HTMX + Vanilla JS + CSS pur. Interface en français.

## Commandes

- **Tests** : `python -m pytest tests/ -v` (depuis la racine du projet)
- **Dev local** : `python run.py` (port 5000)

## Déploiement ("publie")

Quand l'utilisateur dit "publie" (ou "deploy", "mets en prod", etc.), exécuter ces étapes dans l'ordre :

1. **Lancer les tests** pour vérifier que tout passe
2. **Commit** les changements (si pas déjà fait)
3. **Push** sur `origin main` : `git push origin main`
4. **Attendre le build GitHub Actions** : poll l'API GitHub jusqu'à `conclusion: success`
   ```
   TOKEN=$(git credential fill <<< $'host=github.com\nprotocol=https' 2>/dev/null | grep password | cut -d= -f2)
   curl -s -H "Authorization: Bearer $TOKEN" "https://api.github.com/repos/matthieurosset/cookit/actions/runs?per_page=1"
   ```
5. **Pull la nouvelle image** via MCP :
   ```
   mcp__portainer__dockerProxy POST /images/create?fromImage=ghcr.io/matthieurosset/cookit&tag=latest
   ```
6. **Redéployer sur Portainer** via MCP : mettre à jour le stack avec `mcp__portainer__updateStack` (stackId: 52).
   Utiliser un label `cookit.deployed` avec le timestamp courant pour forcer la recréation du container :
   ```yaml
   services:
     cookit:
       image: ghcr.io/matthieurosset/cookit:latest
       container_name: cookit
       restart: unless-stopped
       ports:
         - "5100:5000"
       volumes:
         - /volume3/docker/cookit/data:/data
       environment:
         - PUID=1038
         - PGID=65536
         - UMASK=022
         - SECRET_KEY=cookit-prod-key-s3cur3
         - COOKIT_DATA_DIR=/data
       labels:
         - "cookit.deployed=<TIMESTAMP_ISO>"
   ```
7. **Confirmer** que le container tourne : `mcp__portainer__dockerProxy GET /containers/cookit/json` → vérifier `State.Running: true`

## Infra

- **GitHub** : `matthieurosset/cookit` (CI: GitHub Actions → GHCR)
- **Image** : `ghcr.io/matthieurosset/cookit:latest`
- **Portainer stack ID** : 52
- **Port** : 5100 (host) → 5000 (container)
- **Données** : `/volume3/docker/cookit/data` (montée sur Y:\cookit\data depuis Windows)
- **NAS conventions** : PUID=1038, PGID=65536, UMASK=022
