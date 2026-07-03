#!/usr/bin/env python
"""Ponto de entrada do Django (runserver, migrate, etc.)."""
import os
import sys
from pathlib import Path

def main():
    # Coloca a pasta src/ no caminho para importar o pacote "sti".
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sti.config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
