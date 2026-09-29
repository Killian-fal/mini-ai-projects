#!/usr/bin/env bash
# Toutes les parts d'index, dans un ordre aléatoire, une part entière par run de scan.
# Échec (bannissement CloudFront = exit 2, ou autre) : pause puis nouvel essai de la même part,
# 3 essais au plus. Arrêt quand le disque de Mongo passe sous MIN_FREE_GB.
set -u
cd "$(dirname "$0")/.."
WORKERS=${WORKERS:-3}
PAUSE=${PAUSE:-1800}  # le ban observé a duré moins de 35 min
# vérifié entre deux parts seulement, et une part entière pèse ~7 Go : garder plus que ça de marge
MIN_FREE_GB=${MIN_FREE_GB:-12}
MONGO=${MONGO_CONTAINER:-backend-mongo-1}

# un seul scan à la fois : deux en parallèle doublent le débit et font bannir l'IP
while pgrep -f "bin/scan --part" > /dev/null; do sleep 60; done

for part in $(seq 1 299 | sort -R); do
  free=$(docker exec "$MONGO" df -BG --output=avail /data/db | tail -1 | tr -dc 0-9)
  if [ "${free:-0}" -lt "$MIN_FREE_GB" ]; then
    echo "disque Mongo : ${free} Go libres, arrêt"
    exit 0
  fi
  for try in 1 2 3; do
    echo "=== part $part, essai $try ($(date '+%F %H:%M'), ${free} Go libres)"
    uv run --env-file .env scan --part "$part" --limit 1000000 --workers "$WORKERS" && break
    echo "échec (exit $?), pause ${PAUSE}s"
    sleep "$PAUSE"
  done
done
echo "toutes les parts sont faites"
