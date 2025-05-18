import random
import json
from fontTools.ttLib import TTFont


def shuffle(input_path: str, output_path: str, map_output_path: str):
    """
    This function takes a font, randomly shuffles the glyphs and creates a new font.
    A map of how the font has been shuffled will be created alongside it (you can use that map to encrypt text,
    such that it is displayed correctly when using the new font.)

    Inputs:
        - input_path: str, the path to the input font .ttf.
        - output_path: str, the path to which the output font will be saved to.
        - map_output_path: str, the path to which the translation map will be saved to.
    """
    font = TTFont(input_path)

    cmap_table = font["cmap"]
    cmap_subtable = next(
        (t for t in cmap_table.tables if t.platformID == 3 and t.platEncID in (1, 10)),
        None,
    )
    if cmap_subtable is None:
        raise ValueError("No suitable cmap subtable found.")

    cmap = cmap_subtable.cmap

    codepoints_to_glyphs = {cp: g for cp, g in cmap.items() if 32 <= cp <= 0x10FFFF}
    glyphs = list(codepoints_to_glyphs.values())
    random.shuffle(glyphs)

    new_cmap = dict(zip(codepoints_to_glyphs.keys(), glyphs))
    cmap_subtable.cmap = new_cmap

    glyph_to_original_cp = {g: cp for cp, g in codepoints_to_glyphs.items()}
    translation_map = {}

    for new_cp, g in new_cmap.items():
        orig_cp = glyph_to_original_cp.get(g)
        if orig_cp is not None:
            translation_map[chr(orig_cp)] = chr(new_cp)

    with open(map_output_path, "w", encoding="utf-8") as f:
        json.dump(translation_map, f, ensure_ascii=False, indent=2)

    font.save(output_path)
    return translation_map


def encrypt(text: str, translation_map: dict[str, str]) -> str:
    """
    Helper function which takes some text and the translation map of the
    shuffle function to create text that is legible using the correct font,
    but obfuscated using a non-shuffled font.

    Inputs:
        - text: str, the text to be encrypted/obfuscated/masked
        - translation_map: dict[str, str], the translation map of a given shuffled font.
    """
    return "".join(translation_map.get(c, c) for c in text)
