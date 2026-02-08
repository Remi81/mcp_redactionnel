# MCP Rédactionnel

Petit service Python pour générer et mettre en forme du contenu via des providers d'IA (plugins HTTP).

Quickstart

1. Créez et activez un virtualenv :

   python -m venv .venv
   source .venv/bin/activate

2. Installez les dépendances :

   pip install -r requirements.txt

3. Éditez `config.example.yaml` et copiez en `config.yaml` pour définir vos providers et clés.

4. Utilisez `mcp_redactionnel.service.redaction` et `mcp_redactionnel.service.mise_en_forme`.

Exemples CLI :

- Lister les providers définis dans `config.yaml` :

  ```bash
  python scripts/redact.py --list
  ```

- Rédiger un texte avec le provider `mistral_api` :

  ```bash
  python scripts/redact.py --provider mistral_api --sujet "Économie circulaire" --config config.yaml
  ```

Serveur HTTP pour Postman / Bruno 🚀

1. Démarre le serveur local :

   ```bash
   . .venv/bin/activate && bash scripts/run_server.sh
   ```

   Par défaut le serveur écoute sur `http://127.0.0.1:8000`.

2. Exemples de requêtes (utilisables dans Bruno / Postman) :

   - Lister les providers :

     GET http://127.0.0.1:8000/providers

   - Rédaction (POST JSON) :

     POST http://127.0.0.1:8000/redaction
     Headers: `Content-Type: application/json`
     Body (raw JSON):

     ```json
     {
       "provider": "mistral_api",
       "sujet": "Qu'est-ce que l'économie circulaire ?",
       "sources": ["https://example.com" ],
       "meta": {"length": "400", "tone": "formel"},
       "format": "text"
     }
     ```

Format "text" : renvoie un article en français (plain text) structuré en paragraphes, avec un titre et éventuellement des sous-titres, **sans balises HTML ni Markdown**. Respecte les directives `meta` (par ex. longueur et ton).

Format "html" : renvoie un fragment HTML **accessible** prêt à être inséré dans une page (balises sémantiques, ARIA, pas de styles externes).
   - Mise en forme (POST JSON) :

     POST http://127.0.0.1:8000/mise_en_forme
     Body (raw JSON):

     ```json
     {
       "provider": "mistral_api",
       "texte": "Ton texte à formater"
     }
     ```

3. Exemple `curl` (si tu veux tester rapidement depuis un terminal) :

   ```bash
   curl -X POST "http://127.0.0.1:8000/redaction" -H "Content-Type: application/json" -d '{"provider":"mistral_api","sujet":"Qui est Monet ?"}'
   ```

Docs Swagger / OpenAPI

- Swagger UI: http://127.0.0.1:8000/docs (interface interactive pour tester les endpoints) ✅
- Redoc: http://127.0.0.1:8000/redoc (documentation lisible) ✅
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

Tu peux importer `http://127.0.0.1:8000/openapi.json` dans Bruno/Postman pour obtenir automatiquement les requêtes et exemples.

Note : assure-toi que `config.yaml` contient ton provider `mistral_api` avec la clé (ou que tu utilises les variables d'environnement/gestion des secrets).

Fichiers générés par les tests

- Les artefacts générés localement (par ex. `tests/output/test_final_output.html`) sont écrits par `scripts/test_final_cleaning.py` pour inspection locale.
- Le dossier `tests/output/` contient un fichier `.gitkeep` suivi par Git, mais **son contenu est ignoré** grâce à l'entrée `.gitignore` (`tests/output/*`). Ne commite pas d'artefacts générés par les tests.
- Pour générer et vérifier un exemple localement :

  ```bash
  . .venv/bin/activate && python scripts/test_final_cleaning.py
  ```
