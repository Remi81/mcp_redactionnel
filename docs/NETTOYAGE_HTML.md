# Nettoyage du HTML généré par l'IA

## Problème identifié

Les modèles d'IA (Mistral notamment) ont tendance à générer du HTML avec des artefacts qui empêchent l'insertion directe en base de données :

1. **Fences Markdown** : ` ```html ... ``` `
2. **Séquences littérales échappées** : 
   - `\n` au lieu de vrais sauts de ligne (caractère newline)
   - `\"` au lieu de `"`
   - `\t` au lieu de tabulations
3. **Préambules** : "Voici le résultat HTML", "J'ai créé ce code", etc.

### Exemple de sortie problématique

```
```html\n<article>\n  <h1 id=\"title\">Test</h1>\n</article>\n```
```

Au lieu de :

```html
<article>
  <h1 id="title">Test</h1>
</article>
```

## Solution mise en place

### 1. Amélioration des prompts

Les prompts ont été renforcés avec :

- **Instructions en tête ET en fin** (répétition)
- **Format visuel clair** : ❌ INTERDIT / ✓ REQUIS
- **Contexte technique** : "sera inséré DIRECTEMENT dans une base de données"
- **Exemples concrets** : montrer ce qui est attendu
- **Instruction précise** : "Premier caractère de ta réponse doit être <"

Voir [prompts.yaml](../mcp_redactionnel/prompts.yaml)

### 2. Fonction de nettoyage robuste

La fonction `_clean_html_fragment()` dans [service.py](../mcp_redactionnel/service.py) applique plusieurs transformations :

```python
def _clean_html_fragment(s: str) -> str:
    """Clean HTML from LLM artifacts"""
    # 1. Supprimer les fences Markdown
    m = re.search(r"^```(?:html)?\s*(.*)\s*```$", text, flags=re.S)
    if m:
        text = m.group(1).strip()
    
    # 2. Remplacer les séquences LITTÉRALES (2 caractères : \ + n)
    #    par de VRAIS caractères (newline, tab, quote)
    text = text.replace(r'\n', '\n')   # literal \n → real newline
    text = text.replace(r'\t', '\t')   # literal \t → real tab
    text = text.replace(r'\"', '"')    # literal \" → real quote
    text = text.replace(r"\'", "'")    # literal \' → real quote
    
    return text.strip()
```

**Point clé** : L'IA génère littéralement les caractères `\` suivi de `n` (2 chars), pas la séquence d'échappement Python `\n`. Le `r'\n'` dans le code représente ces 2 caractères littéraux.

### 3. Application systématique

Le nettoyage est appliqué automatiquement dans :

- `redaction(..., format='html')` → nettoie le résultat
- `mise_en_forme(...)` → nettoie toujours le résultat

Aucune action manuelle requise côté utilisateur.

## Vérification

### Tests unitaires

```bash
pytest tests/test_html_cleaning.py -v
```

Vérifie que :
- Les fences sont supprimées
- Les `\n` littéraux deviennent de vrais newlines
- Les `\"` deviennent des `"`
- Le HTML commence bien par `<`

### Test end-to-end

```bash
python scripts/test_final_cleaning.py
```

Appelle l'API Mistral, génère du HTML, applique le nettoyage et vérifie :
- ✅ Pas de `\n` littéraux
- ✅ De vrais sauts de ligne
- ✅ Pas de fences
- ✅ Commence par `<`

### Test manuel avec l'API

```bash
curl -X POST http://127.0.0.1:8000/mise_en_forme \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "mistral_api",
    "texte": "Test de nettoyage HTML."
  }'
```

Le résultat doit être du HTML pur, sans fences ni échappements.

## Analyse binaire

Pour vérifier qu'un fichier contient de **vrais** sauts de ligne :

```bash
# Voir les caractères réels
od -c fichier.html | head -20

# Doit montrer \n (1 caractère newline)
# PAS \ suivi de n (2 caractères)
```

## Insertion en base de données

Le HTML retourné est prêt pour :

```sql
INSERT INTO articles (content) VALUES (?);
```

Ou :

```python
# Django/SQLAlchemy
Article.objects.create(content=html_from_api)
```

Aucun post-traitement nécessaire.

## Limitations connues

1. **L'IA ne respecte pas toujours les prompts** : Même avec des instructions claires, certains modèles continuent à générer des artefacts. C'est pourquoi le nettoyage par code est **indispensable**.

2. **Pas de validation sémantique** : Le nettoyage ne vérifie pas que le HTML est bien formé ou sécurisé. Pour cela, utiliser :
   - `html.parser` pour valider la structure
   - `bleach` pour whitelister les balises autorisées
   - Validation ARIA pour l'accessibilité

3. **Dépendance au format de sortie de l'IA** : Si Mistral change son format de sortie, il faudra adapter `_clean_html_fragment()`.

## Améliorations futures

- [ ] Ajouter validation HTML avec `html5lib`
- [ ] Implémenter whitelist de balises (security)
- [ ] Logger les cas où le nettoyage est appliqué (monitoring)
- [ ] Paramètre `temperature=0` pour réduire la créativité de l'IA
- [ ] Tester avec d'autres modèles (Claude, GPT-4, etc.)
