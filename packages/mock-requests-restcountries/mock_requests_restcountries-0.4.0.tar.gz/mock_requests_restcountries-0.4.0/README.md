# mock-requests-restcountries

A mock for REST Countries (v3.1):
- Uses **packaged JSONs** for common URLs
- If a URL isn't cached, it **fetches live once** and caches to `~/.cache/mock_requests_rc`

## Local usage

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip build
pip install -e ".[dev]"

## Bulk priming

- Prime many URLs into **user cache** (and optionally copy into package data):

```bash
# By default this will make real requests; disable with MOCK_REQUESTS_OFFLINE=1.
python scripts/bulk_prime.py --urls-file scripts/seed_urls.txt --to-package
```

## Runtime behavior

Resolution order for a URL:
1. **Package data** (`mock_requests/data/*.json`) — fastest
2. **User cache** (`~/.cache/mock_requests_rc/*.json`)
3. **Live fetch** (unless `MOCK_REQUESTS_OFFLINE=1`), then save to user cache
4. Else: return 404-like mock response

## Safety knobs

- Set `MOCK_REQUESTS_OFFLINE=1` to **disable** live fetches (e.g., CI).
- Set `MOCK_REQUESTS_TIMEOUT=30` to adjust HTTP timeout seconds.
- Set `MOCK_REQUESTS_USER_CACHE_DIR` to customize cache directory.
