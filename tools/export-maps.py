#!/usr/bin/env python3
"""Export OoT2D ``.zmap`` maps from one of the bundled games to PNG.

This is a thin wrapper around the ``oot2d-map`` submodule
(https://github.com/fluxcompile/oot2d-map): it reuses that tool's parser and
renderer but points them at the ``Maps/`` and ``Tiles/`` folders of a game
extracted from one of the archives in this repository, instead of the sample
data bundled with the tool.

Usage::

    python3 tools/export-maps.py [GAME_DIR] [OUT_DIR]

``GAME_DIR``  Folder containing ``Maps/`` (``*.zmap``) and ``Tiles/`` (``*.png``).
              Defaults to the extracted "OoT 2D 2014 v.15.2" game.
``OUT_DIR``   Where the rendered ``*.png`` maps are written.
              Defaults to ``ExportedMaps/`` at the repository root (git-ignored).

Requires Python 3.6+ and Pillow (``pip install pillow``).
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OOT2DMAP_DIR = os.path.join(REPO_ROOT, "oot2d-map")

# The "OoT 2D 2014 v.15.2" build ships the richest map set (19 maps). Its folder
# is extracted from OoT-2D-2014-v.15.2.zip and therefore git-ignored.
DEFAULT_GAME_DIR = os.path.join(
    REPO_ROOT, "OoT-2D-2014-v.15.2", "OoT 2D 2014 v.15.2"
)
DEFAULT_OUT_DIR = os.path.join(REPO_ROOT, "ExportedMaps")


def main(argv):
    game_dir = os.path.abspath(argv[1]) if len(argv) > 1 else DEFAULT_GAME_DIR
    out_dir = os.path.abspath(argv[2]) if len(argv) > 2 else DEFAULT_OUT_DIR

    maps_dir = os.path.join(game_dir, "Maps")
    if not os.path.isdir(maps_dir):
        sys.exit(
            f"[!] No Maps/ folder in {game_dir!r}. Extract the game archive first "
            "(see README) or pass a different GAME_DIR."
        )
    if not os.path.isdir(OOT2DMAP_DIR):
        sys.exit(
            "[!] oot2d-map submodule missing. Run: git submodule update --init oot2d-map"
        )

    # Import the converter from the submodule.
    sys.path.insert(0, OOT2DMAP_DIR)
    import zmap_exporter as z  # noqa: E402

    os.makedirs(out_dir, exist_ok=True)
    # Tileset paths embedded in the .zmap files are relative ("Tiles/xxx.png"),
    # so run from the game directory to resolve them.
    os.chdir(game_dir)

    exported = 0
    for fname in sorted(os.listdir(maps_dir)):
        if not fname.lower().endswith(".zmap"):
            continue
        rel_path = os.path.join("Maps", fname)
        info = z.parse_zmap_header(rel_path)
        if not info.get("tiles", {}).get("tile_data"):
            print(f"[!] No tile data in {fname}, skipping.")
            continue
        tileset_image, tile_width = z.load_tileset_image(info)
        if not tileset_image:
            print(f"[!] Missing tileset for {fname}, skipping.")
            continue
        out_path = os.path.join(out_dir, os.path.splitext(fname)[0] + ".png")
        z.export_map_to_image(info, tileset_image, tile_width, out_path)
        exported += 1

    print(f"\n[+] Done. Exported {exported} map(s) to {out_dir}")


if __name__ == "__main__":
    main(sys.argv)
