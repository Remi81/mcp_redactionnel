Merci pour ton intérêt pour ce projet !

Principes rapides
-----------------
- **Ne commite jamais de secrets** (clés API, jetons, fichiers .env, etc.). Utilise `config.example.yaml` et des variables d'environnement (ex. `MISTRAL_API_KEY`).
- **N'ajoute pas d'artefacts générés par les tests** au repo. Les artefacts locaux sont écrits dans `tests/output/` et ce dossier est ignoré (seul `tests/output/.gitkeep` est suivi).

Tests & exécution locale
-------------------------
- Pour lancer la suite de tests :

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  pytest -q
  ```

- Script d'exemple pour vérifier le nettoyage HTML :

  ```bash
  . .venv/bin/activate && python scripts/test_final_cleaning.py
  ```

Bonnes pratiques recommandées
-----------------------------
- Installe et active `pre-commit` localement pour prévenir les commits problématiques (formatage, détection basique d'erreurs). Exemple :

  ```bash
  pip install pre-commit
  pre-commit install
  ```

- Optionnel mais fortement recommandé : ajouter un scanner de secrets (ex. `detect-secrets`) dans les hooks de `pre-commit` pour bloquer l'ajout accidentel de clés.

Merci — et encore une fois, ne commite pas de secrets ni d'artefacts générés localement.
