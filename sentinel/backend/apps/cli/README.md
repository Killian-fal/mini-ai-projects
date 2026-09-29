# cli

## scan

Picks pages from the Common Crawl index and stores their raw HTML.

```sh
uv run --env-file .env scan --part 12 --limit 5000
```

| Flag | Default | |
|---|---|---|
| `--part N` | random | index part (1-299), repeatable |
| `--parts N` | 1 | random parts drawn when `--part` is absent |
| `--rows N` | whole part | index rows read per part |
| `--limit N` | 2000 | pages downloaded, split across parts |
| `--workers N` | 4 | parallel downloads. Keep it low: Common Crawl bans the IP |
| `--tranco-top N` | 100000 | sites in the Tranco top N are skipped |

- Put the Tranco list at `tranco.csv` (https://tranco-list.eu/top-1m.csv.zip). Without it, nothing is skipped.
- URLs already stored are skipped, so a part can be rerun.
- Exit code 2: too many downloads failed in a row, the IP is probably banned. Wait, then rerun.
- `tools/scan_all.sh` scans every part, one at a time, and pauses on a ban.
- Never run two scans at once.

## detect

Scores every stored page that has no detection yet with Jev. **Each page is a paid call.**

```sh
uv run --env-file .env detect --limit 100
```

- `--limit N`: pages scored. Default: all of them.
- `.env` needs `TYPESAFE_API_KEY`. `INJECTION_THRESHOLD` (default 0.8) sets the score above which a page is flagged.
- Blocks already seen on a page scored under the threshold are not sent again.
- A failed call is stored on the page as an error, and the run goes on.
