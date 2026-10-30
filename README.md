# decktile.github.io

The [decktile](https://github.com/decktile/decktile) website: example decks built with decktile, published at [decktile.github.io](https://decktile.github.io).

- `scripts/build_site.py`: renders every deck in decktile's [`examples/`](https://github.com/decktile/decktile/tree/master/examples) to HTML and PDF and writes the front page
- CI checks out `examples/` from the main repo and rebuilds on every push here, whenever decktile's examples change, and weekly with the latest decktile from PyPI

API docs live with the code at [decktile.github.io/decktile](https://decktile.github.io/decktile/).

Build locally (from a checkout next to `decktile/`):

```bash
uv run --no-project --with decktile python3 scripts/build_site.py --src ../decktile/examples --decktile "uv run --no-project --with decktile decktile"
```
