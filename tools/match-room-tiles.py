#!/usr/bin/env python3
"""Reconstruct a tile grid from a room screenshot by exact-matching tiles.

The OoT2D FSA project (``oot2d_fsa/``) stores rooms as GameMaker ``.bin``
files whose tile-id semantics depend on GMK-internal background data we
can't read — but the repo ships AUTHORITATIVE room screenshots
(``oot2d_fsa/graphics/screens/kokiri_inside_sample_01.png`` is
``links_house`` rendered at exactly 21x15 tiles of 16px). This tool
slices such a screenshot into tile cells and finds each cell's
pixel-exact position in a tileset image, producing:

  * ``<out>.json``  — the grid as ``{cols, rows, cells: [[{x,y} | null, …], …]}``
                      where ``x``/``y`` are tileset cell coords and
                      ``null`` marks cells with no exact tileset match
                      (usually object sprites composited over the floor —
                      in a re-port those become object placements, which
                      is what you want anyway);
  * ``<out>.png``   — a verification render rebuilt from the matches
                      (should reproduce the screenshot wherever matched).

Usage:
  python3 tools/match-room-tiles.py SCREENSHOT TILESET OUT_BASE \
      [--tile 16] [--offset-x 0] [--offset-y 0]

Example (Link's house from FSA):
  python3 tools/match-room-tiles.py \
      oot2d_fsa/graphics/screens/kokiri_inside_sample_01.png \
      oot2d_fsa/graphics/finalized/tileset_kokiri_forest_interior.png \
      ExportedMaps/fsa_links_house
"""

import argparse
import json
import sys

from PIL import Image


def cell_bytes(image: Image.Image, x_px: int, y_px: int, tile: int) -> bytes:
    return image.crop((x_px, y_px, x_px + tile, y_px + tile)).tobytes()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("screenshot")
    parser.add_argument("tileset")
    parser.add_argument("out_base")
    parser.add_argument("--tile", type=int, default=16)
    parser.add_argument("--offset-x", type=int, default=0)
    parser.add_argument("--offset-y", type=int, default=0)
    args = parser.parse_args()

    tile = args.tile
    shot = Image.open(args.screenshot).convert("RGB")
    tileset = Image.open(args.tileset).convert("RGB")

    # Index every tileset cell by its raw pixels for O(1) lookup.
    ts_cols = tileset.width // tile
    ts_rows = tileset.height // tile
    index: dict[bytes, tuple[int, int]] = {}
    for ty in range(ts_rows):
        for tx in range(ts_cols):
            # First occurrence wins — duplicated cells in the sheet all
            # render identically, so the choice doesn't matter visually.
            index.setdefault(cell_bytes(tileset, tx * tile, ty * tile, tile), (tx, ty))

    cols = (shot.width - args.offset_x) // tile
    rows = (shot.height - args.offset_y) // tile
    cells: list[list[dict | None]] = []
    matched = 0
    unmatched: list[tuple[int, int]] = []
    for y in range(rows):
        row: list[dict | None] = []
        for x in range(cols):
            key = cell_bytes(shot, args.offset_x + x * tile, args.offset_y + y * tile, tile)
            hit = index.get(key)
            if hit:
                row.append({"x": hit[0], "y": hit[1]})
                matched += 1
            else:
                row.append(None)
                unmatched.append((x, y))
        cells.append(row)

    with open(f"{args.out_base}.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "screenshot": args.screenshot,
                "tileset": args.tileset,
                "tile": tile,
                "cols": cols,
                "rows": rows,
                "cells": cells,
            },
            handle,
            indent=1,
        )

    verify = Image.new("RGB", (cols * tile, rows * tile), (32, 32, 38))
    for y in range(rows):
        for x in range(cols):
            ref = cells[y][x]
            if ref is None:
                continue
            verify.paste(
                tileset.crop((ref["x"] * tile, ref["y"] * tile, ref["x"] * tile + tile, ref["y"] * tile + tile)),
                (x * tile, y * tile),
            )
    verify.save(f"{args.out_base}.png")

    total = cols * rows
    print(f"{matched}/{total} cells matched ({100 * matched // total}%); {len(unmatched)} unmatched")
    if unmatched:
        print("unmatched (x,y) — likely object overlays:", unmatched[:40])
    return 0


if __name__ == "__main__":
    sys.exit(main())
