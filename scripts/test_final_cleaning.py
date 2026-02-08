#!/usr/bin/env python
"""Test final du nettoyage HTML avec un appel réel à Mistral"""
import os
import sys
import traceback
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_redactionnel.service import mise_en_forme_by_name

# Test avec un texte simple
texte_test = "Les énergies renouvelables sont essentielles pour l'avenir. Elles permettent de réduire les émissions de CO2."


def main():
    print("🔧 Test du nettoyage HTML...")
    print(f"📝 Texte d'entrée: {texte_test}")
    print("\n" + "="*80)

    try:
        result = mise_en_forme_by_name(
            provider_name='mistral_api',
            texte=texte_test,
            config_path='config.yaml'
        )
        
        print("\n✅ RÉSULTAT NETTOYÉ:")
        print("="*80)
        print(result)
        print("="*80)
        
        # Vérifications
        print("\n🔍 VÉRIFICATIONS:")
        has_literal_backslash_n = r'\n' in result
        has_real_newlines = '\n' in result
        has_code_fences = '```' in result
        has_escaped_quotes = r'\"' in result
        starts_with_tag = result.strip().startswith('<')
        
        print(f"  Contient des \\n littéraux (MAUVAIS): {'❌ OUI' if has_literal_backslash_n else '✅ NON'}")
        print(f"  Contient des vrais sauts de ligne (BON): {'✅ OUI' if has_real_newlines else '❌ NON'}")
        print(f"  Contient des fences ``` (MAUVAU): {'❌ OUI' if has_code_fences else '✅ NON'}")
        print(f"  Contient des \\\" échappés (MAUVAU): {'❌ OUI' if has_escaped_quotes else '✅ NON'}")
        print(f"  Commence par < (BON): {'✅ OUI' if starts_with_tag else '❌ NON'}")
        
        # Comptage
        line_count = result.count('\n')
        print(f"\n📊 Statistiques:")
        print(f"  Longueur totale: {len(result)} caractères")
        print(f"  Nombre de sauts de ligne: {line_count}")
        
        # Sauvegarder un artefact local dans `tests/output/` (ignore par git) pour inspection locale
        output_dir = Path(__file__).parent.parent / 'tests' / 'output'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / 'test_final_output.html'
        with open(output_path, 'w') as f:
            f.write(result)
        print(f"\n💾 Résultat sauvegardé localement (ignoré par Git): {output_path}")
        
        # Statut final
        if not has_literal_backslash_n and has_real_newlines and not has_code_fences and starts_with_tag:
            print("\n🎉 SUCCESS! Le HTML est propre et prêt pour la base de données")
            sys.exit(0)
        else:
            print("\n⚠️  ATTENTION: Le HTML contient encore des artefacts à nettoyer")
            sys.exit(1)
            
    except Exception as e:
        print("\n❌ ERREUR:", e)
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    # Only run the integration test if a Mistral API key is provided
    if not os.environ.get('MISTRAL_API_KEY'):
        print("Skipping integration test: MISTRAL_API_KEY not set")
        raise SystemExit(0)
    main()
