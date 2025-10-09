from cooptools.colors import Color
import harfang as hf

def harfang_color_from_coopcolor(coopcolor: Color = None):
    if coopcolor is None:
        coopcolor = Color.Blue

    ctup = coopcolor.value
    return hf.Color(ctup[0], ctup[1], ctup[2])