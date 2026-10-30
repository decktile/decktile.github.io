# decktile.github.io

The [decktile](https://github.com/decktile/decktile) website: example decks built with decktile, published at [decktile.github.io](https://decktile.github.io).

- `decks/`: the example decks (a copy of `examples/` in the main repo, so the site can be changed on its own)
- `scripts/build_site.py`: renders every deck to HTML and PDF and writes the front page
- CI rebuilds on every push and weekly with the latest decktile from PyPI

API docs live with the code at [decktile.github.io/decktile](https://decktile.github.io/decktile/).

Build locally:

```bash
uv run --no-project --with decktile python3 scripts/build_site.py --decktile "uv run --no-project --with decktile decktile"
```
