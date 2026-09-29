import sys
from pathlib import Path

MAX = 300
bad = [p for p in Path().rglob("*.py") if ".venv" not in p.parts and sum(1 for _ in p.open()) > MAX]
for p in bad:
    print(f"{p}: > {MAX} lignes")
sys.exit(1 if bad else 0)
