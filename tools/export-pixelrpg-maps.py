#!/usr/bin/env python3
"""Export OoT2D ``.zmap`` maps to the PixelRPG map-editor format.

Builds on the ``oot2d-map`` submodule's parser (like ``export-maps.py``,
which renders PNGs) but emits the PixelRPG project formats instead:

  OUT_DIR/spritesets/<tileset>.png    copied tileset image
  OUT_DIR/spritesets/<tileset>.json   PixelRPG sprite-set descriptor
  OUT_DIR/maps/<map>.json             PixelRPG map (ground + overlay layer)
  OUT_DIR/index.json                  what was exported (for registration)

The ``.zmap`` tile list is one ordered stream with a ``start_layer_2``
split — tiles before it become the ``ground`` tier, tiles from it on the
``overlay`` tier (the original renderer just paints later-over-earlier).
Tile ids are local indices into the tileset at the header's sheet width,
which matches the PixelRPG convention (descriptor ``columns`` = header
``tilesheet_width / 16``), so ids transfer 1:1.

No solidity information exists in the ``.zmap`` files — exported tiles
are all walkable; tune ``solid`` flags in the editor. Use the PNGs from
``tools/export-maps.py`` (``ExportedMaps/``) as the visual reference.

Usage::

    python3 tools/export-pixelrpg-maps.py [GAME_DIR] [OUT_DIR]
"""

import json
import os
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OOT2DMAP_DIR = os.path.join(REPO_ROOT, "oot2d-map")
DEFAULT_GAME_DIR = os.path.join(REPO_ROOT, "OoT-2D-2014-v.15.2", "OoT 2D 2014 v.15.2")
DEFAULT_OUT_DIR = os.path.join(REPO_ROOT, "ExportedMaps", "pixelrpg")

TILE = 8  # the 2014 game uses 8px tiles (zmap_exporter.TILE_SIZE)


def slug(name: str) -> str:
    return name.lower().replace(" ", "-").replace("_", "-")


def main(argv):
    game_dir = os.path.abspath(argv[1]) if len(argv) > 1 else DEFAULT_GAME_DIR
    out_dir = os.path.abspath(argv[2]) if len(argv) > 2 else DEFAULT_OUT_DIR
    maps_dir = os.path.join(game_dir, "Maps")
    if not os.path.isdir(maps_dir):
        sys.exit(f"[!] No Maps/ in {game_dir!r} — extract the game archive first (see README).")
    if not os.path.isdir(OOT2DMAP_DIR):
        sys.exit("[!] oot2d-map submodule missing. Run: git submodule update --init oot2d-map")

    sys.path.insert(0, OOT2DMAP_DIR)
    import zmap_exporter as z  # noqa: E402

    os.makedirs(os.path.join(out_dir, "maps"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "spritesets"), exist_ok=True)
    cwd = os.getcwd()
    os.chdir(game_dir)  # tileset paths inside the .zmap are game-relative

    from PIL import Image

    exported, spritesets = [], {}
    for fname in sorted(os.listdir(maps_dir)):
        if not fname.lower().endswith(".zmap"):
            continue
        info = z.parse_zmap_header(os.path.join(maps_dir, fname))
        tiles = (info.get("tiles") or {}).get("tile_data") or []
        tileset_rel = info.get("tileset", "")
        if not tiles or not tileset_rel or not os.path.isfile(tileset_rel):
            print(f"[skip] {fname}: tiles={len(tiles)} tileset={tileset_rel!r}")
            continue

        set_id = slug(os.path.splitext(os.path.basename(tileset_rel))[0])
        sheet_cols = max(1, info.get("tilesheet_width", TILE) // TILE)
        if set_id not in spritesets:
            img = Image.open(tileset_rel)
            dst_png = os.path.join(out_dir, "spritesets", f"{set_id}.png")
            shutil.copyfile(tileset_rel, dst_png)
            rows = img.height // TILE
            descriptor = {
                "version": "1.0.0",
                "id": set_id,
                "name": set_id.replace("-", " ").title(),
                "kind": "tileset",
                "image": {"id": "main", "path": f"{set_id}.png", "type": "image"},
                "spriteWidth": TILE,
                "spriteHeight": TILE,
                "columns": sheet_cols,
                "rows": rows,
                "margin": 0,
                "spacing": 0,
                "sprites": [
                    {"id": i, "col": i % sheet_cols, "row": i // sheet_cols} for i in range(sheet_cols * rows)
                ],
            }
            with open(os.path.join(out_dir, "spritesets", f"{set_id}.json"), "w") as fh:
                json.dump(descriptor, fh, indent=1)
            spritesets[set_id] = sheet_cols

        map_id = slug(os.path.splitext(fname)[0])
        min_x = min(t["x"] for t in tiles)
        min_y = min(t["y"] for t in tiles)
        cols = max(t["x"] for t in tiles) - min_x + 1
        rows = max(t["y"] for t in tiles) - min_y + 1
        split = (info["tiles"].get("start_layer_2") or len(tiles)) or len(tiles)

        def layer_sprites(entries):
            return [
                {"x": t["x"] - min_x, "y": t["y"] - min_y, "spriteId": t["tile_id"], "spriteSetId": set_id}
                for t in entries
            ]

        map_data = {
            "id": map_id,
            "name": os.path.splitext(fname)[0].replace("_", " "),
            "version": "1.0.0",
            "tileWidth": TILE,
            "tileHeight": TILE,
            "columns": cols,
            "rows": rows,
            "spriteSets": [
                {"id": set_id, "path": f"../spritesets/{set_id}.json", "type": "spriteset", "firstGid": 1}
            ],
            "layers": [
                {"id": "layer_ground", "name": "Ground", "visible": True, "tier": "ground",
                 "sprites": layer_sprites(tiles[:split])},
                {"id": "layer_overlay", "name": "Overlay", "visible": True, "tier": "overlay",
                 "sprites": layer_sprites(tiles[split:])},
                {"id": "layer_functional", "name": "Functional", "visible": True, "sprites": []},
            ],
            "properties": {
                "source": f"Maps/{fname} from 'The Legend of Zelda: Ocarina of Time 2D' v0.10.2 "
                "by CheerfulSage & GodsTurf (oot-2d.com, 2014) — archive "
                "the-legend-of-zelda-ocarina-of-time-2d-0-10-2-en-win.zip in the PixelRPG/oot-2d repo; "
                "converted by tools/export-pixelrpg-maps.py (zmap parser: fluxcompile/oot2d-map)",
            },
            "objectPlacements": [],
            "editorData": {},
        }
        with open(os.path.join(out_dir, "maps", f"{map_id}.json"), "w") as fh:
            json.dump(map_data, fh, indent=1)
        exported.append({"id": map_id, "tileset": set_id, "cols": cols, "rows": rows, "tiles": len(tiles)})
        print(f"[ok] {map_id}: {cols}x{rows}, {len(tiles)} tiles, tileset {set_id}")

    os.chdir(cwd)
    with open(os.path.join(out_dir, "index.json"), "w") as fh:
        json.dump(exported, fh, indent=1)
    print(f"\n{len(exported)} maps → {out_dir}")


if __name__ == "__main__":
    main(sys.argv)
