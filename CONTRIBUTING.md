# Contributing to CachePilot

The maintained contribution guide is [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

Before submitting changes:

```bash
docker compose up --build -d
docker compose exec -T api pytest -q tests/unit tests/load --disable-warnings --no-cov
python3 -m compileall -q app scripts tests
git diff --check
```

Keep secrets out of commits. Update the README and focused documentation whenever public behavior or setup changes.
