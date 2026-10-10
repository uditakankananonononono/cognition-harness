"""v11 orchestrator: one subprocess per suite (hard isolation boundary).
Usage: python3 run_study.py <v9|v10|both>
"""
import subprocess, sys
from pathlib import Path

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    here = Path(__file__).resolve().parent
    for tag in ('v9', 'v10'):
        if which in (tag, 'both'):
            subprocess.run([sys.executable, str(here / 'run_one_suite.py'), tag], check=True)
