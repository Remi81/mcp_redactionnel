#!/usr/bin/env python3
"""CLI minimal pour le service `rédaction`.
Usage:
  python scripts/redact.py --provider mistral_api --sujet "Sujet" [--sources s1 s2] [--config config.yaml]
"""
import argparse
from mcp_redactionnel.service import redaction_by_name, list_providers

parser = argparse.ArgumentParser(description='MCP Rédactionnel - CLI')
parser.add_argument('--provider', '-p', required=False, help='Nom du provider (ex: mistral_api)')
parser.add_argument('--sujet', '-s', required=False, help='Sujet à rédiger')
parser.add_argument('--sources', nargs='*', default=None, help='Sources optionnelles')
parser.add_argument('--config', '-c', default='config.yaml', help='Chemin vers le fichier de config')
parser.add_argument('--format', '-f', choices=['text','html'], default='text', help='Format de sortie: text (par défaut) ou html (accessible)')
parser.add_argument('--list', action='store_true', help='Lister les providers disponibles')

args = parser.parse_args()

if args.list:
    providers = list_providers(args.config)
    print('Providers:', ', '.join(providers))
    raise SystemExit(0)

if not args.provider or not args.sujet:
    parser.print_help()
    raise SystemExit(1)

out = redaction_by_name(args.provider, args.sujet, sources=args.sources, config_path=args.config, format=args.format)
print('\n--- RÉSULTAT ---\n')
print(out)
