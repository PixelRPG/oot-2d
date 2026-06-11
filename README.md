# The Legend Of Zelda - Ocarina Of Time 2D 🧝‍♂️

This project contains or references to work in progress or abandoned Ocarina of Time 2D projects. Contributions are welcome 👍.

# Files

* `ZELDA-Oot2D.zip`: Ocarina of Time 2D by Richard Denton (2006)
* `the-legend-of-zelda-ocarina-of-time-2d-0-10-2-en-win.zip`: Ocarina of Time 2D v0.10 by CheerfulSage & GodsTurf (2014)
* `OoT-2D-2014-v.15.2.zip`: Ocarina of Time 2D v0.15 by CheerfulSage & GodsTurf (2014)
* `oot2d_fsa.zip`: Ocarina Of Time 2D FSA by Team Dekunutz
* `zelda-oot-2d-unity_v0.2.0_windows.zip`: Ocarina of Time 2D (Unity) v0.2.0 — prebuilt Windows build by moobotec ([release](https://github.com/moobotec/zelda-oot-2d-unity/releases/tag/v0.2.0_a); source is the [`zelda-oot-2d-unity`](https://github.com/moobotec/zelda-oot-2d-unity) submodule)

The directories extracted from these archives are ignored via `.gitignore` (see the archives above for the original source).

# Source code (git submodules)

Unity source projects are referenced as git submodules. Initialize them with `git submodule update --init`.

* [`OoT2DUnity`](https://github.com/Colbydude/OoT2DUnity): Ocarina of Time 2D: Unity by Colbydude — a fan game for the purpose of learning Unity (Unity 2022.3.0f1), inspired by Team Dekunutz's OoT2D FSA.
* [`Unity2D-Zelda`](https://github.com/Ellard24/Unity2D-Zelda): "Electric Slide" — a 2D Zelda-style Unity project built as a CS 419 university course project (Ellard24).
* [`zelda-oot-2d-unity`](https://github.com/moobotec/zelda-oot-2d-unity): Ocarina of Time 2D, an actively developed personal/experimental Unity fan game (minimap, inventory, NPC dialogue & save systems) by moobotec.

# Tools

* [`oot2d-map`](https://github.com/fluxcompile/oot2d-map): Python tool by fluxcompile that parses the `.zmap` map files of the OoT2D fan project and renders them to `.png`.

## Extracting assets from the games

`tools/` collects small scripts that pull assets out of the bundled games. More
can be added over time (sprites, audio, tilesets, …).

### Maps → PNG

`tools/export-maps.py` wraps the `oot2d-map` submodule and runs it against the
`Maps/` + `Tiles/` folders of an extracted game (default: the "OoT 2D 2014
v.15.2" build), rendering each `.zmap` to a PNG.

```bash
# 1. Initialize the converter submodule and install its dependency
git submodule update --init oot2d-map
pip install pillow

# 2. Extract a game archive that contains Maps/ + Tiles/, e.g.:
unzip OoT-2D-2014-v.15.2.zip

# 3. Convert (writes to ExportedMaps/, which is git-ignored)
python3 tools/export-maps.py

# …or point it at any game folder / output dir:
python3 tools/export-maps.py "<game folder with Maps/ and Tiles/>" out/
```

This produces one PNG per map (e.g. `ExportedMaps/Kokiri_Forest.png`).

# Links

## Abandoned

* [Ocarina of Time 2D 2006-2014 summary](https://n64squid.com/ocarina-of-time-2d/)
* [Ocarina of Time 2D](http://www.oot-2d.com/) [(video)](https://www.youtube.com/watch?v=DbgcVkPkLqc&t=330s)
* [Ocarina Of Time 2D FSA(2011)](http://zfgc.com/forum/index.php?topic=30924)

## Unfinished

* [Ocarina of Time 2D: Unity](http://zfgc.com/forum/index.php?topic=42040) [(Source)](https://github.com/Colbydude/OoT2DUnity) [(presentation)](http://zfgc.com/forum/index.php?topic=42040)