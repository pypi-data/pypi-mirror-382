#! /usr/bin/env python3
"""
This module is used to encode and decode between common colour names
and RGB integer values.  Standard Windows and CSS colour names are recognized.
"""

#===============================================================================
# Imports
#===============================================================================

from typing import Dict, Union, Sequence, Set
from . import codec


#===============================================================================
# Colour CODEC
#===============================================================================

class Colour(codec.KeywordCodec):
    """
    Colour Coder / Decoder
    """

    _KEYS = {'fg_color', 'bg_color', 'true-color'}
    _COLOUR: Dict[str, int] = {}

    @classmethod
    def _windows_colour(cls, name: str, rgb: int):
        cls._COLOUR[name] = rgb

    @classmethod
    def _css_colour(cls, name: str, r: int, g: int, b: int):
        name = name.lower()
        rgb = r*65536 + g * 256 + b
        cls._COLOUR[name.lower()] = rgb

    @classmethod
    def colour_to_argb(cls, clr: Union[str, int, Sequence[int]]) -> str:
        """
        Convert a colour to an ARGB string (#ff_RR_GG_BB)
        """

        rgb = None

        if isinstance(clr, str) and clr.isdecimal():
            clr = int(clr)

        if isinstance(clr, int):
            r = clr & 255
            g = (clr >> 8) & 255
            b = (clr >> 16) & 255
            rgb = r*65536 + g * 256 + b

        elif isinstance(clr, str):
            name = clr.lower()
            if name.startswith('#'):
                if len(clr) == 4:
                    code = clr[1] + clr[1] + clr[2] + clr[2] + clr[3] + clr[3]
                else:
                    code = clr[-6:]
                rgb = int(code, 16)
            elif name in cls._COLOUR:
                rgb = cls._COLOUR[name]

        elif isinstance(clr, (list, tuple)) and len(clr) == 3:
            r, g, b = clr
            rgb = r * 65536 + g * 256 + b

        if rgb is not None:
            return f"#ff{rgb & 0xFF_FF_FF:06x}"

        raise ValueError(f"Not a recognized colour: {clr}")

    @classmethod
    def argb_to_colour(cls, argb: str) -> str:
        """
        Convert an ARGB (#ff_RR_GG_BB) colour to a named colour,
        if possible.
        """

        argb = argb.lower()

        if argb in cls._COLOUR:
            return argb

        if argb.startswith('#') and len(argb) > 6:
            rgb = int(argb[-6:], 16)
        elif argb.isdecimal() or argb[0] == '-' and argb[1:].isdecimal():
            bgr = int(argb)
            r = bgr & 255
            g = (bgr >> 8) & 255
            b = (bgr >> 16) & 255
            rgb = r*65536 + g * 256 + b
        else:
            raise ValueError(f"Unrecognized #ARGB code: {argb}")

        for clr, value in cls._COLOUR.items():
            if rgb == value:
                return clr

        return f"#ff{rgb & 0xFF_FF_FF:06x}"


    def encodes(self, keyword: str) -> bool:
        """
        Predicate, indicating whether or not this keyword codec will encode
        and decode a particular keyword

        Parameters:
            keyword (str): keyword to test

        Returns:
            bool: ``True`` if ``keyword`` is ``'fg_color'``, ``'bg_color'``,
            or ``'true-color'``, ``False`` otherwise
        """
        return keyword in self._KEYS


    def encode(self, colour: Union[str, int, Sequence[int]]) -> str: # pylint: disable=arguments-differ,arguments-renamed
        """
        Encode a named colour into an #ARGB value::

            >>> colour = Colour()
            >>> colour.encode("RED")
            #ffff0000
            >>> colour.encode((0, 0, 255))
            #ff0000ff
            >>> colour.encode("#FA8800")
            #fffa8800

        Parameters:
           colour: the colour to encoded

        Returns:
            str: the #ARGB value
        """

        return self.colour_to_argb(colour)

    def decode(self, colour: str) -> str:     # pylint: disable=arguments-differ,arguments-renamed
        """
        Decode an ARGB value into a named colour, if possible::

            >>> colour = Colour()
            >>> colour.decode(str(0xFF_FF_FF))
            'white'
            >>> colour.decode(str(0x9A_FA_00))
            'mediumspringgreen'
            >>> colour.decode('#00FA9A'))
            'mediumspringgreen'
            >>> colour.decode(str(16418816))
            '#ff0088fa'

        Parameters:
           colour (str): an #ARGB colour value

        Returns:
            str: the name of the colour
        """

        return self.argb_to_colour(colour)


    def range(self) -> Set[str]:
        """
        Return the set of known colour names
        """

        return set(self._COLOUR)


# Colours from Window's online document

# pylint: disable=protected-access
Colour._windows_colour("aliceblue", 0xF0F8FF)
Colour._windows_colour("antiquewhite", 0xFAEBD7)
Colour._windows_colour("aqua", 0x00FFFF)
Colour._windows_colour("aquamarine", 0x7FFFD4)
Colour._windows_colour("azure", 0xF0FFFF)
Colour._windows_colour("beige", 0xF5F5DC)
Colour._windows_colour("bisque", 0xFFE4C4)
Colour._windows_colour("black", 0x000000)
Colour._windows_colour("blanchedalmond", 0xFFEBCD)
Colour._windows_colour("blue", 0x0000FF)
Colour._windows_colour("blueviolet", 0x8A2BE2)
Colour._windows_colour("brown", 0xA52A2A)
Colour._windows_colour("burlywood", 0xDEB887)
Colour._windows_colour("cadetblue", 0x5F9EA0)
Colour._windows_colour("chartreuse", 0x7FFF00)
Colour._windows_colour("chocolate", 0xD2691E)
Colour._windows_colour("coral", 0xFF7F50)
Colour._windows_colour("cornflower", 0x6495ED)
Colour._windows_colour("cornsilk", 0xFFF8DC)
Colour._windows_colour("crimson", 0xDC143C)
Colour._windows_colour("cyan", 0x00FFFF)
Colour._windows_colour("darkblue", 0x00008B)
Colour._windows_colour("darkcyan", 0x008B8B)
Colour._windows_colour("darkgoldenrod", 0xB8860B)
Colour._windows_colour("darkgray", 0xA9A9A9)
Colour._windows_colour("darkgreen", 0x006400)
Colour._windows_colour("darkkhaki", 0xBDB76B)
Colour._windows_colour("darkmagenta", 0x8B008B)
Colour._windows_colour("darkolivegreen", 0x556B2F)
Colour._windows_colour("darkorange", 0xFF8C00)
Colour._windows_colour("darkorchid", 0x9932CC)
Colour._windows_colour("darkred", 0x8B0000)
Colour._windows_colour("darksalmon", 0xE9967A)
Colour._windows_colour("darkseagreen", 0x8FBC8B)
Colour._windows_colour("darkslateblue", 0x483D8B)
Colour._windows_colour("darkslategray", 0x2F4F4F)
Colour._windows_colour("darkturquoise", 0x00CED1)
Colour._windows_colour("darkviolet", 0x9400D3)
Colour._windows_colour("deeppink", 0xFF1493)
Colour._windows_colour("deepskyblue", 0x00BFFF)
Colour._windows_colour("dimgray", 0x696969)
Colour._windows_colour("dodgerblue", 0x1E90FF)
Colour._windows_colour("firebrick", 0xB22222)
Colour._windows_colour("floralwhite", 0xFFFAF0)
Colour._windows_colour("forestgreen", 0x228B22)
Colour._windows_colour("fuchsia", 0xFF00FF)
Colour._windows_colour("gainsboro", 0xDCDCDC)
Colour._windows_colour("ghostwhite", 0xF8F8FF)
Colour._windows_colour("gold", 0xFFD700)
Colour._windows_colour("goldenrod", 0xDAA520)
Colour._windows_colour("gray", 0x808080)
Colour._windows_colour("green", 0x008000)
Colour._windows_colour("greenyellow", 0xADFF2F)
Colour._windows_colour("honeydew", 0xF0FFF0)
Colour._windows_colour("hotpink", 0xFF69B4)
Colour._windows_colour("indianred", 0xCD5C5C)
Colour._windows_colour("indigo", 0x4B0082)
Colour._windows_colour("ivory", 0xFFFFF0)
Colour._windows_colour("khaki", 0xF0E68C)
Colour._windows_colour("lavender", 0xE6E6FA)
Colour._windows_colour("lavenderblush", 0xFFF0F5)
Colour._windows_colour("lawngreen", 0x7CFC00)
Colour._windows_colour("lemonchiffon", 0xFFFACD)
Colour._windows_colour("lightblue", 0xADD8E6)
Colour._windows_colour("lightcoral", 0xF08080)
Colour._windows_colour("lightcyan", 0xE0FFFF)
Colour._windows_colour("lightgoldenrodyellow", 0xFAFAD2)
Colour._windows_colour("lightgreen", 0x90EE90)
Colour._windows_colour("lightgray", 0xD3D3D3)
Colour._windows_colour("lightpink", 0xFFB6C1)
Colour._windows_colour("lightsalmon", 0xFFA07A)
Colour._windows_colour("lightseagreen", 0x20B2AA)
Colour._windows_colour("lightskyblue", 0x87CEFA)
Colour._windows_colour("lightslategray", 0x778899)
Colour._windows_colour("lightsteelblue", 0xB0C4DE)
Colour._windows_colour("lightyellow", 0xFFFFE0)
Colour._windows_colour("lime", 0x00FF00)
Colour._windows_colour("limegreen", 0x32CD32)
Colour._windows_colour("linen", 0xFAF0E6)
Colour._windows_colour("magenta", 0xFF00FF)
Colour._windows_colour("maroon", 0x800000)
Colour._windows_colour("mediumaquamarine", 0x66CDAA)
Colour._windows_colour("mediumblue", 0x0000CD)
Colour._windows_colour("mediumorchid", 0xBA55D3)
Colour._windows_colour("mediumpurple", 0x9370DB)
Colour._windows_colour("mediumseagreen", 0x3CB371)
Colour._windows_colour("mediumslateblue", 0x7B68EE)
Colour._windows_colour("mediumspringgreen", 0x00FA9A)
Colour._windows_colour("mediumturquoise", 0x48D1CC)
Colour._windows_colour("mediumvioletred", 0xC71585)
Colour._windows_colour("midnightblue", 0x191970)
Colour._windows_colour("mintcream", 0xF5FFFA)
Colour._windows_colour("mistyrose", 0xFFE4E1)
Colour._windows_colour("moccasin", 0xFFE4B5)
Colour._windows_colour("navajowhite", 0xFFDEAD)
Colour._windows_colour("navy", 0x000080)
Colour._windows_colour("oldlace", 0xFDF5E6)
Colour._windows_colour("olive", 0x808000)
Colour._windows_colour("olivedrab", 0x6B8E23)
Colour._windows_colour("orange", 0xFFA500)
Colour._windows_colour("orangered", 0xFF4500)
Colour._windows_colour("orchid", 0xDA70D6)
Colour._windows_colour("palegoldenrod", 0xEEE8AA)
Colour._windows_colour("palegreen", 0x98FB98)
Colour._windows_colour("paleturquoise", 0xAFEEEE)
Colour._windows_colour("palevioletred", 0xDB7093)
Colour._windows_colour("papayawhip", 0xFFEFD5)
Colour._windows_colour("peachpuff", 0xFFDAB9)
Colour._windows_colour("peru", 0xCD853F)
Colour._windows_colour("pink", 0xFFC0CB)
Colour._windows_colour("plum", 0xDDA0DD)
Colour._windows_colour("powderblue", 0xB0E0E6)
Colour._windows_colour("purple", 0x800080)
Colour._windows_colour("red", 0xFF0000)
Colour._windows_colour("rosybrown", 0xBC8F8F)
Colour._windows_colour("royalblue", 0x4169E1)
Colour._windows_colour("saddlebrown", 0x8B4513)
Colour._windows_colour("salmon", 0xFA8072)
Colour._windows_colour("sandybrown", 0xF4A460)
Colour._windows_colour("seagreen", 0x2E8B57)
Colour._windows_colour("seashell", 0xFFF5EE)
Colour._windows_colour("sienna", 0xA0522D)
Colour._windows_colour("silver", 0xC0C0C0)
Colour._windows_colour("skyblue", 0x87CEEB)
Colour._windows_colour("slateblue", 0x6A5ACD)
Colour._windows_colour("slategray", 0x708090)
Colour._windows_colour("snow", 0xFFFAFA)
Colour._windows_colour("springgreen", 0x00FF7F)
Colour._windows_colour("steelblue", 0x4682B4)
Colour._windows_colour("tan", 0xD2B48C)
Colour._windows_colour("teal", 0x008080)
Colour._windows_colour("thistle", 0xD8BFD8)
Colour._windows_colour("tomato", 0xFF6347)
Colour._windows_colour("turquoise", 0x40E0D0)
Colour._windows_colour("violet", 0xEE82EE)
Colour._windows_colour("wheat", 0xF5DEB3)
Colour._windows_colour("white", 0xFFFFFF)
Colour._windows_colour("whitesmoke", 0xF5F5F5)
Colour._windows_colour("yellow", 0xFFFF00)
Colour._windows_colour("yellowgreen", 0x9ACD32)


# Additional CSS colours from Webucator.com

Colour._css_colour("ANTIQUEWHITE1", 255, 239, 219)
Colour._css_colour("ANTIQUEWHITE2", 238, 223, 204)
Colour._css_colour("ANTIQUEWHITE3", 205, 192, 176)
Colour._css_colour("ANTIQUEWHITE4", 139, 131, 120)
Colour._css_colour("AQUAMARINE1", 127, 255, 212)
Colour._css_colour("AQUAMARINE2", 118, 238, 198)
Colour._css_colour("AQUAMARINE3", 102, 205, 170)
Colour._css_colour("AQUAMARINE4", 69, 139, 116)
Colour._css_colour("AZURE1", 240, 255, 255)
Colour._css_colour("AZURE2", 224, 238, 238)
Colour._css_colour("AZURE3", 193, 205, 205)
Colour._css_colour("AZURE4", 131, 139, 139)
Colour._css_colour("BANANA", 227, 207, 87)
Colour._css_colour("BISQUE1", 255, 228, 196)
Colour._css_colour("BISQUE2", 238, 213, 183)
Colour._css_colour("BISQUE3", 205, 183, 158)
Colour._css_colour("BISQUE4", 139, 125, 107)
Colour._css_colour("BLUE1", 0, 0, 255)
Colour._css_colour("BLUE2", 0, 0, 238)
Colour._css_colour("BLUE3", 0, 0, 205)
Colour._css_colour("BLUE4", 0, 0, 139)
Colour._css_colour("BRICK", 156, 102, 31)
Colour._css_colour("BROWN1", 255, 64, 64)
Colour._css_colour("BROWN2", 238, 59, 59)
Colour._css_colour("BROWN3", 205, 51, 51)
Colour._css_colour("BROWN4", 139, 35, 35)
Colour._css_colour("BURLYWOOD1", 255, 211, 155)
Colour._css_colour("BURLYWOOD2", 238, 197, 145)
Colour._css_colour("BURLYWOOD3", 205, 170, 125)
Colour._css_colour("BURLYWOOD4", 139, 115, 85)
Colour._css_colour("BURNTSIENNA", 138, 54, 15)
Colour._css_colour("BURNTUMBER", 138, 51, 36)
Colour._css_colour("CADETBLUE1", 152, 245, 255)
Colour._css_colour("CADETBLUE2", 142, 229, 238)
Colour._css_colour("CADETBLUE3", 122, 197, 205)
Colour._css_colour("CADETBLUE4", 83, 134, 139)
Colour._css_colour("CADMIUMORANGE", 255, 97, 3)
Colour._css_colour("CADMIUMYELLOW", 255, 153, 18)
Colour._css_colour("CARROT", 237, 145, 33)
Colour._css_colour("CHARTREUSE1", 127, 255, 0)
Colour._css_colour("CHARTREUSE2", 118, 238, 0)
Colour._css_colour("CHARTREUSE3", 102, 205, 0)
Colour._css_colour("CHARTREUSE4", 69, 139, 0)
Colour._css_colour("CHOCOLATE1", 255, 127, 36)
Colour._css_colour("CHOCOLATE2", 238, 118, 33)
Colour._css_colour("CHOCOLATE3", 205, 102, 29)
Colour._css_colour("CHOCOLATE4", 139, 69, 19)
Colour._css_colour("COBALT", 61, 89, 171)
Colour._css_colour("COBALTGREEN", 61, 145, 64)
Colour._css_colour("COLDGREY", 128, 138, 135)
Colour._css_colour("CORAL1", 255, 114, 86)
Colour._css_colour("CORAL2", 238, 106, 80)
Colour._css_colour("CORAL3", 205, 91, 69)
Colour._css_colour("CORAL4", 139, 62, 47)
Colour._css_colour("CORNFLOWERBLUE", 100, 149, 237)
Colour._css_colour("CORNSILK1", 255, 248, 220)
Colour._css_colour("CORNSILK2", 238, 232, 205)
Colour._css_colour("CORNSILK3", 205, 200, 177)
Colour._css_colour("CORNSILK4", 139, 136, 120)
Colour._css_colour("CYAN1", 0, 255, 255)
Colour._css_colour("CYAN2", 0, 238, 238)
Colour._css_colour("CYAN3", 0, 205, 205)
Colour._css_colour("CYAN4", 0, 139, 139)
Colour._css_colour("DARKGOLDENROD1", 255, 185, 15)
Colour._css_colour("DARKGOLDENROD2", 238, 173, 14)
Colour._css_colour("DARKGOLDENROD3", 205, 149, 12)
Colour._css_colour("DARKGOLDENROD4", 139, 101, 8)
Colour._css_colour("DARKOLIVEGREEN1", 202, 255, 112)
Colour._css_colour("DARKOLIVEGREEN2", 188, 238, 104)
Colour._css_colour("DARKOLIVEGREEN3", 162, 205, 90)
Colour._css_colour("DARKOLIVEGREEN4", 110, 139, 61)
Colour._css_colour("DARKORANGE1", 255, 127, 0)
Colour._css_colour("DARKORANGE2", 238, 118, 0)
Colour._css_colour("DARKORANGE3", 205, 102, 0)
Colour._css_colour("DARKORANGE4", 139, 69, 0)
Colour._css_colour("DARKORCHID1", 191, 62, 255)
Colour._css_colour("DARKORCHID2", 178, 58, 238)
Colour._css_colour("DARKORCHID3", 154, 50, 205)
Colour._css_colour("DARKORCHID4", 104, 34, 139)
Colour._css_colour("DARKSEAGREEN1", 193, 255, 193)
Colour._css_colour("DARKSEAGREEN2", 180, 238, 180)
Colour._css_colour("DARKSEAGREEN3", 155, 205, 155)
Colour._css_colour("DARKSEAGREEN4", 105, 139, 105)
Colour._css_colour("DARKSLATEGRAY1", 151, 255, 255)
Colour._css_colour("DARKSLATEGRAY2", 141, 238, 238)
Colour._css_colour("DARKSLATEGRAY3", 121, 205, 205)
Colour._css_colour("DARKSLATEGRAY4", 82, 139, 139)
Colour._css_colour("DEEPPINK1", 255, 20, 147)
Colour._css_colour("DEEPPINK2", 238, 18, 137)
Colour._css_colour("DEEPPINK3", 205, 16, 118)
Colour._css_colour("DEEPPINK4", 139, 10, 80)
Colour._css_colour("DEEPSKYBLUE1", 0, 191, 255)
Colour._css_colour("DEEPSKYBLUE2", 0, 178, 238)
Colour._css_colour("DEEPSKYBLUE3", 0, 154, 205)
Colour._css_colour("DEEPSKYBLUE4", 0, 104, 139)
Colour._css_colour("DODGERBLUE1", 30, 144, 255)
Colour._css_colour("DODGERBLUE2", 28, 134, 238)
Colour._css_colour("DODGERBLUE3", 24, 116, 205)
Colour._css_colour("DODGERBLUE4", 16, 78, 139)
Colour._css_colour("EGGSHELL", 252, 230, 201)
Colour._css_colour("EMERALDGREEN", 0, 201, 87)
Colour._css_colour("FIREBRICK1", 255, 48, 48)
Colour._css_colour("FIREBRICK2", 238, 44, 44)
Colour._css_colour("FIREBRICK3", 205, 38, 38)
Colour._css_colour("FIREBRICK4", 139, 26, 26)
Colour._css_colour("FLESH", 255, 125, 64)
Colour._css_colour("GOLD1", 255, 215, 0)
Colour._css_colour("GOLD2", 238, 201, 0)
Colour._css_colour("GOLD3", 205, 173, 0)
Colour._css_colour("GOLD4", 139, 117, 0)
Colour._css_colour("GOLDENROD1", 255, 193, 37)
Colour._css_colour("GOLDENROD2", 238, 180, 34)
Colour._css_colour("GOLDENROD3", 205, 155, 29)
Colour._css_colour("GOLDENROD4", 139, 105, 20)
Colour._css_colour("GRAY1", 3, 3, 3)
Colour._css_colour("GRAY10", 26, 26, 26)
Colour._css_colour("GRAY11", 28, 28, 28)
Colour._css_colour("GRAY12", 31, 31, 31)
Colour._css_colour("GRAY13", 33, 33, 33)
Colour._css_colour("GRAY14", 36, 36, 36)
Colour._css_colour("GRAY15", 38, 38, 38)
Colour._css_colour("GRAY16", 41, 41, 41)
Colour._css_colour("GRAY17", 43, 43, 43)
Colour._css_colour("GRAY18", 46, 46, 46)
Colour._css_colour("GRAY19", 48, 48, 48)
Colour._css_colour("GRAY2", 5, 5, 5)
Colour._css_colour("GRAY20", 51, 51, 51)
Colour._css_colour("GRAY21", 54, 54, 54)
Colour._css_colour("GRAY22", 56, 56, 56)
Colour._css_colour("GRAY23", 59, 59, 59)
Colour._css_colour("GRAY24", 61, 61, 61)
Colour._css_colour("GRAY25", 64, 64, 64)
Colour._css_colour("GRAY26", 66, 66, 66)
Colour._css_colour("GRAY27", 69, 69, 69)
Colour._css_colour("GRAY28", 71, 71, 71)
Colour._css_colour("GRAY29", 74, 74, 74)
Colour._css_colour("GRAY3", 8, 8, 8)
Colour._css_colour("GRAY30", 77, 77, 77)
Colour._css_colour("GRAY31", 79, 79, 79)
Colour._css_colour("GRAY32", 82, 82, 82)
Colour._css_colour("GRAY33", 84, 84, 84)
Colour._css_colour("GRAY34", 87, 87, 87)
Colour._css_colour("GRAY35", 89, 89, 89)
Colour._css_colour("GRAY36", 92, 92, 92)
Colour._css_colour("GRAY37", 94, 94, 94)
Colour._css_colour("GRAY38", 97, 97, 97)
Colour._css_colour("GRAY39", 99, 99, 99)
Colour._css_colour("GRAY4", 10, 10, 10)
Colour._css_colour("GRAY40", 102, 102, 102)
Colour._css_colour("GRAY42", 107, 107, 107)
Colour._css_colour("GRAY43", 110, 110, 110)
Colour._css_colour("GRAY44", 112, 112, 112)
Colour._css_colour("GRAY45", 115, 115, 115)
Colour._css_colour("GRAY46", 117, 117, 117)
Colour._css_colour("GRAY47", 120, 120, 120)
Colour._css_colour("GRAY48", 122, 122, 122)
Colour._css_colour("GRAY49", 125, 125, 125)
Colour._css_colour("GRAY5", 13, 13, 13)
Colour._css_colour("GRAY50", 127, 127, 127)
Colour._css_colour("GRAY51", 130, 130, 130)
Colour._css_colour("GRAY52", 133, 133, 133)
Colour._css_colour("GRAY53", 135, 135, 135)
Colour._css_colour("GRAY54", 138, 138, 138)
Colour._css_colour("GRAY55", 140, 140, 140)
Colour._css_colour("GRAY56", 143, 143, 143)
Colour._css_colour("GRAY57", 145, 145, 145)
Colour._css_colour("GRAY58", 148, 148, 148)
Colour._css_colour("GRAY59", 150, 150, 150)
Colour._css_colour("GRAY6", 15, 15, 15)
Colour._css_colour("GRAY60", 153, 153, 153)
Colour._css_colour("GRAY61", 156, 156, 156)
Colour._css_colour("GRAY62", 158, 158, 158)
Colour._css_colour("GRAY63", 161, 161, 161)
Colour._css_colour("GRAY64", 163, 163, 163)
Colour._css_colour("GRAY65", 166, 166, 166)
Colour._css_colour("GRAY66", 168, 168, 168)
Colour._css_colour("GRAY67", 171, 171, 171)
Colour._css_colour("GRAY68", 173, 173, 173)
Colour._css_colour("GRAY69", 176, 176, 176)
Colour._css_colour("GRAY7", 18, 18, 18)
Colour._css_colour("GRAY70", 179, 179, 179)
Colour._css_colour("GRAY71", 181, 181, 181)
Colour._css_colour("GRAY72", 184, 184, 184)
Colour._css_colour("GRAY73", 186, 186, 186)
Colour._css_colour("GRAY74", 189, 189, 189)
Colour._css_colour("GRAY75", 191, 191, 191)
Colour._css_colour("GRAY76", 194, 194, 194)
Colour._css_colour("GRAY77", 196, 196, 196)
Colour._css_colour("GRAY78", 199, 199, 199)
Colour._css_colour("GRAY79", 201, 201, 201)
Colour._css_colour("GRAY8", 20, 20, 20)
Colour._css_colour("GRAY80", 204, 204, 204)
Colour._css_colour("GRAY81", 207, 207, 207)
Colour._css_colour("GRAY82", 209, 209, 209)
Colour._css_colour("GRAY83", 212, 212, 212)
Colour._css_colour("GRAY84", 214, 214, 214)
Colour._css_colour("GRAY85", 217, 217, 217)
Colour._css_colour("GRAY86", 219, 219, 219)
Colour._css_colour("GRAY87", 222, 222, 222)
Colour._css_colour("GRAY88", 224, 224, 224)
Colour._css_colour("GRAY89", 227, 227, 227)
Colour._css_colour("GRAY9", 23, 23, 23)
Colour._css_colour("GRAY90", 229, 229, 229)
Colour._css_colour("GRAY91", 232, 232, 232)
Colour._css_colour("GRAY92", 235, 235, 235)
Colour._css_colour("GRAY93", 237, 237, 237)
Colour._css_colour("GRAY94", 240, 240, 240)
Colour._css_colour("GRAY95", 242, 242, 242)
Colour._css_colour("GRAY97", 247, 247, 247)
Colour._css_colour("GRAY98", 250, 250, 250)
Colour._css_colour("GRAY99", 252, 252, 252)
Colour._css_colour("GREEN1", 0, 255, 0)
Colour._css_colour("GREEN2", 0, 238, 0)
Colour._css_colour("GREEN3", 0, 205, 0)
Colour._css_colour("GREEN4", 0, 139, 0)
Colour._css_colour("HONEYDEW1", 240, 255, 240)
Colour._css_colour("HONEYDEW2", 224, 238, 224)
Colour._css_colour("HONEYDEW3", 193, 205, 193)
Colour._css_colour("HONEYDEW4", 131, 139, 131)
Colour._css_colour("HOTPINK1", 255, 110, 180)
Colour._css_colour("HOTPINK2", 238, 106, 167)
Colour._css_colour("HOTPINK3", 205, 96, 144)
Colour._css_colour("HOTPINK4", 139, 58, 98)
Colour._css_colour("INDIANRED1", 255, 106, 106)
Colour._css_colour("INDIANRED2", 238, 99, 99)
Colour._css_colour("INDIANRED3", 205, 85, 85)
Colour._css_colour("INDIANRED4", 139, 58, 58)
Colour._css_colour("IVORY1", 255, 255, 240)
Colour._css_colour("IVORY2", 238, 238, 224)
Colour._css_colour("IVORY3", 205, 205, 193)
Colour._css_colour("IVORY4", 139, 139, 131)
Colour._css_colour("IVORYBLACK", 41, 36, 33)
Colour._css_colour("KHAKI1", 255, 246, 143)
Colour._css_colour("KHAKI2", 238, 230, 133)
Colour._css_colour("KHAKI3", 205, 198, 115)
Colour._css_colour("KHAKI4", 139, 134, 78)
Colour._css_colour("LAVENDERBLUSH1", 255, 240, 245)
Colour._css_colour("LAVENDERBLUSH2", 238, 224, 229)
Colour._css_colour("LAVENDERBLUSH3", 205, 193, 197)
Colour._css_colour("LAVENDERBLUSH4", 139, 131, 134)
Colour._css_colour("LEMONCHIFFON1", 255, 250, 205)
Colour._css_colour("LEMONCHIFFON2", 238, 233, 191)
Colour._css_colour("LEMONCHIFFON3", 205, 201, 165)
Colour._css_colour("LEMONCHIFFON4", 139, 137, 112)
Colour._css_colour("LIGHTBLUE1", 191, 239, 255)
Colour._css_colour("LIGHTBLUE2", 178, 223, 238)
Colour._css_colour("LIGHTBLUE3", 154, 192, 205)
Colour._css_colour("LIGHTBLUE4", 104, 131, 139)
Colour._css_colour("LIGHTCYAN1", 224, 255, 255)
Colour._css_colour("LIGHTCYAN2", 209, 238, 238)
Colour._css_colour("LIGHTCYAN3", 180, 205, 205)
Colour._css_colour("LIGHTCYAN4", 122, 139, 139)
Colour._css_colour("LIGHTGOLDENROD1", 255, 236, 139)
Colour._css_colour("LIGHTGOLDENROD2", 238, 220, 130)
Colour._css_colour("LIGHTGOLDENROD3", 205, 190, 112)
Colour._css_colour("LIGHTGOLDENROD4", 139, 129, 76)
Colour._css_colour("LIGHTGREY", 211, 211, 211)
Colour._css_colour("LIGHTPINK1", 255, 174, 185)
Colour._css_colour("LIGHTPINK2", 238, 162, 173)
Colour._css_colour("LIGHTPINK3", 205, 140, 149)
Colour._css_colour("LIGHTPINK4", 139, 95, 101)
Colour._css_colour("LIGHTSALMON1", 255, 160, 122)
Colour._css_colour("LIGHTSALMON2", 238, 149, 114)
Colour._css_colour("LIGHTSALMON3", 205, 129, 98)
Colour._css_colour("LIGHTSALMON4", 139, 87, 66)
Colour._css_colour("LIGHTSKYBLUE1", 176, 226, 255)
Colour._css_colour("LIGHTSKYBLUE2", 164, 211, 238)
Colour._css_colour("LIGHTSKYBLUE3", 141, 182, 205)
Colour._css_colour("LIGHTSKYBLUE4", 96, 123, 139)
Colour._css_colour("LIGHTSLATEBLUE", 132, 112, 255)
Colour._css_colour("LIGHTSTEELBLUE1", 202, 225, 255)
Colour._css_colour("LIGHTSTEELBLUE2", 188, 210, 238)
Colour._css_colour("LIGHTSTEELBLUE3", 162, 181, 205)
Colour._css_colour("LIGHTSTEELBLUE4", 110, 123, 139)
Colour._css_colour("LIGHTYELLOW1", 255, 255, 224)
Colour._css_colour("LIGHTYELLOW2", 238, 238, 209)
Colour._css_colour("LIGHTYELLOW3", 205, 205, 180)
Colour._css_colour("LIGHTYELLOW4", 139, 139, 122)
Colour._css_colour("MAGENTA2", 238, 0, 238)
Colour._css_colour("MAGENTA3", 205, 0, 205)
Colour._css_colour("MAGENTA4", 139, 0, 139)
Colour._css_colour("MANGANESEBLUE", 3, 168, 158)
Colour._css_colour("MAROON1", 255, 52, 179)
Colour._css_colour("MAROON2", 238, 48, 167)
Colour._css_colour("MAROON3", 205, 41, 144)
Colour._css_colour("MAROON4", 139, 28, 98)
Colour._css_colour("MEDIUMORCHID1", 224, 102, 255)
Colour._css_colour("MEDIUMORCHID2", 209, 95, 238)
Colour._css_colour("MEDIUMORCHID3", 180, 82, 205)
Colour._css_colour("MEDIUMORCHID4", 122, 55, 139)
Colour._css_colour("MEDIUMPURPLE1", 171, 130, 255)
Colour._css_colour("MEDIUMPURPLE2", 159, 121, 238)
Colour._css_colour("MEDIUMPURPLE3", 137, 104, 205)
Colour._css_colour("MEDIUMPURPLE4", 93, 71, 139)
Colour._css_colour("MELON", 227, 168, 105)
Colour._css_colour("MINT", 189, 252, 201)
Colour._css_colour("MISTYROSE1", 255, 228, 225)
Colour._css_colour("MISTYROSE2", 238, 213, 210)
Colour._css_colour("MISTYROSE3", 205, 183, 181)
Colour._css_colour("MISTYROSE4", 139, 125, 123)
Colour._css_colour("NAVAJOWHITE1", 255, 222, 173)
Colour._css_colour("NAVAJOWHITE2", 238, 207, 161)
Colour._css_colour("NAVAJOWHITE3", 205, 179, 139)
Colour._css_colour("NAVAJOWHITE4", 139, 121, 94)
Colour._css_colour("OLIVEDRAB1", 192, 255, 62)
Colour._css_colour("OLIVEDRAB2", 179, 238, 58)
Colour._css_colour("OLIVEDRAB3", 154, 205, 50)
Colour._css_colour("OLIVEDRAB4", 105, 139, 34)
Colour._css_colour("ORANGE1", 255, 165, 0)
Colour._css_colour("ORANGE2", 238, 154, 0)
Colour._css_colour("ORANGE3", 205, 133, 0)
Colour._css_colour("ORANGE4", 139, 90, 0)
Colour._css_colour("ORANGERED1", 255, 69, 0)
Colour._css_colour("ORANGERED2", 238, 64, 0)
Colour._css_colour("ORANGERED3", 205, 55, 0)
Colour._css_colour("ORANGERED4", 139, 37, 0)
Colour._css_colour("ORCHID1", 255, 131, 250)
Colour._css_colour("ORCHID2", 238, 122, 233)
Colour._css_colour("ORCHID3", 205, 105, 201)
Colour._css_colour("ORCHID4", 139, 71, 137)
Colour._css_colour("PALEGREEN1", 154, 255, 154)
Colour._css_colour("PALEGREEN2", 144, 238, 144)
Colour._css_colour("PALEGREEN3", 124, 205, 124)
Colour._css_colour("PALEGREEN4", 84, 139, 84)
Colour._css_colour("PALETURQUOISE1", 187, 255, 255)
Colour._css_colour("PALETURQUOISE2", 174, 238, 238)
Colour._css_colour("PALETURQUOISE3", 150, 205, 205)
Colour._css_colour("PALETURQUOISE4", 102, 139, 139)
Colour._css_colour("PALEVIOLETRED1", 255, 130, 171)
Colour._css_colour("PALEVIOLETRED2", 238, 121, 159)
Colour._css_colour("PALEVIOLETRED3", 205, 104, 137)
Colour._css_colour("PALEVIOLETRED4", 139, 71, 93)
Colour._css_colour("PEACHPUFF1", 255, 218, 185)
Colour._css_colour("PEACHPUFF2", 238, 203, 173)
Colour._css_colour("PEACHPUFF3", 205, 175, 149)
Colour._css_colour("PEACHPUFF4", 139, 119, 101)
Colour._css_colour("PEACOCK", 51, 161, 201)
Colour._css_colour("PINK1", 255, 181, 197)
Colour._css_colour("PINK2", 238, 169, 184)
Colour._css_colour("PINK3", 205, 145, 158)
Colour._css_colour("PINK4", 139, 99, 108)
Colour._css_colour("PLUM1", 255, 187, 255)
Colour._css_colour("PLUM2", 238, 174, 238)
Colour._css_colour("PLUM3", 205, 150, 205)
Colour._css_colour("PLUM4", 139, 102, 139)
Colour._css_colour("PURPLE1", 155, 48, 255)
Colour._css_colour("PURPLE2", 145, 44, 238)
Colour._css_colour("PURPLE3", 125, 38, 205)
Colour._css_colour("PURPLE4", 85, 26, 139)
Colour._css_colour("RASPBERRY", 135, 38, 87)
Colour._css_colour("RAWSIENNA", 199, 97, 20)
Colour._css_colour("RED1", 255, 0, 0)
Colour._css_colour("RED2", 238, 0, 0)
Colour._css_colour("RED3", 205, 0, 0)
Colour._css_colour("RED4", 139, 0, 0)
Colour._css_colour("ROSYBROWN1", 255, 193, 193)
Colour._css_colour("ROSYBROWN2", 238, 180, 180)
Colour._css_colour("ROSYBROWN3", 205, 155, 155)
Colour._css_colour("ROSYBROWN4", 139, 105, 105)
Colour._css_colour("ROYALBLUE1", 72, 118, 255)
Colour._css_colour("ROYALBLUE2", 67, 110, 238)
Colour._css_colour("ROYALBLUE3", 58, 95, 205)
Colour._css_colour("ROYALBLUE4", 39, 64, 139)
Colour._css_colour("SALMON1", 255, 140, 105)
Colour._css_colour("SALMON2", 238, 130, 98)
Colour._css_colour("SALMON3", 205, 112, 84)
Colour._css_colour("SALMON4", 139, 76, 57)
Colour._css_colour("SAPGREEN", 48, 128, 20)
Colour._css_colour("SEAGREEN1", 84, 255, 159)
Colour._css_colour("SEAGREEN2", 78, 238, 148)
Colour._css_colour("SEAGREEN3", 67, 205, 128)
Colour._css_colour("SEAGREEN4", 46, 139, 87)
Colour._css_colour("SEASHELL1", 255, 245, 238)
Colour._css_colour("SEASHELL2", 238, 229, 222)
Colour._css_colour("SEASHELL3", 205, 197, 191)
Colour._css_colour("SEASHELL4", 139, 134, 130)
Colour._css_colour("SEPIA", 94, 38, 18)
Colour._css_colour("SGIBEET", 142, 56, 142)
Colour._css_colour("SGIBRIGHTGRAY", 197, 193, 170)
Colour._css_colour("SGICHARTREUSE", 113, 198, 113)
Colour._css_colour("SGIDARKGRAY", 85, 85, 85)
Colour._css_colour("SGIGRAY12", 30, 30, 30)
Colour._css_colour("SGIGRAY16", 40, 40, 40)
Colour._css_colour("SGIGRAY32", 81, 81, 81)
Colour._css_colour("SGIGRAY36", 91, 91, 91)
Colour._css_colour("SGIGRAY52", 132, 132, 132)
Colour._css_colour("SGIGRAY56", 142, 142, 142)
Colour._css_colour("SGIGRAY72", 183, 183, 183)
Colour._css_colour("SGIGRAY76", 193, 193, 193)
Colour._css_colour("SGIGRAY92", 234, 234, 234)
Colour._css_colour("SGIGRAY96", 244, 244, 244)
Colour._css_colour("SGILIGHTBLUE", 125, 158, 192)
Colour._css_colour("SGILIGHTGRAY", 170, 170, 170)
Colour._css_colour("SGIOLIVEDRAB", 142, 142, 56)
Colour._css_colour("SGISALMON", 198, 113, 113)
Colour._css_colour("SGISLATEBLUE", 113, 113, 198)
Colour._css_colour("SGITEAL", 56, 142, 142)
Colour._css_colour("SIENNA1", 255, 130, 71)
Colour._css_colour("SIENNA2", 238, 121, 66)
Colour._css_colour("SIENNA3", 205, 104, 57)
Colour._css_colour("SIENNA4", 139, 71, 38)
Colour._css_colour("SKYBLUE1", 135, 206, 255)
Colour._css_colour("SKYBLUE2", 126, 192, 238)
Colour._css_colour("SKYBLUE3", 108, 166, 205)
Colour._css_colour("SKYBLUE4", 74, 112, 139)
Colour._css_colour("SLATEBLUE1", 131, 111, 255)
Colour._css_colour("SLATEBLUE2", 122, 103, 238)
Colour._css_colour("SLATEBLUE3", 105, 89, 205)
Colour._css_colour("SLATEBLUE4", 71, 60, 139)
Colour._css_colour("SLATEGRAY1", 198, 226, 255)
Colour._css_colour("SLATEGRAY2", 185, 211, 238)
Colour._css_colour("SLATEGRAY3", 159, 182, 205)
Colour._css_colour("SLATEGRAY4", 108, 123, 139)
Colour._css_colour("SNOW1", 255, 250, 250)
Colour._css_colour("SNOW2", 238, 233, 233)
Colour._css_colour("SNOW3", 205, 201, 201)
Colour._css_colour("SNOW4", 139, 137, 137)
Colour._css_colour("SPRINGGREEN1", 0, 238, 118)
Colour._css_colour("SPRINGGREEN2", 0, 205, 102)
Colour._css_colour("SPRINGGREEN3", 0, 139, 69)
Colour._css_colour("STEELBLUE1", 99, 184, 255)
Colour._css_colour("STEELBLUE2", 92, 172, 238)
Colour._css_colour("STEELBLUE3", 79, 148, 205)
Colour._css_colour("STEELBLUE4", 54, 100, 139)
Colour._css_colour("TAN1", 255, 165, 79)
Colour._css_colour("TAN2", 238, 154, 73)
Colour._css_colour("TAN3", 205, 133, 63)
Colour._css_colour("TAN4", 139, 90, 43)
Colour._css_colour("THISTLE1", 255, 225, 255)
Colour._css_colour("THISTLE2", 238, 210, 238)
Colour._css_colour("THISTLE3", 205, 181, 205)
Colour._css_colour("THISTLE4", 139, 123, 139)
Colour._css_colour("TOMATO1", 255, 99, 71)
Colour._css_colour("TOMATO2", 238, 92, 66)
Colour._css_colour("TOMATO3", 205, 79, 57)
Colour._css_colour("TOMATO4", 139, 54, 38)
Colour._css_colour("TURQUOISE1", 0, 245, 255)
Colour._css_colour("TURQUOISE2", 0, 229, 238)
Colour._css_colour("TURQUOISE3", 0, 197, 205)
Colour._css_colour("TURQUOISE4", 0, 134, 139)
Colour._css_colour("TURQUOISEBLUE", 0, 199, 140)
Colour._css_colour("VIOLETRED", 208, 32, 144)
Colour._css_colour("VIOLETRED1", 255, 62, 150)
Colour._css_colour("VIOLETRED2", 238, 58, 140)
Colour._css_colour("VIOLETRED3", 205, 50, 120)
Colour._css_colour("VIOLETRED4", 139, 34, 82)
Colour._css_colour("WARMGREY", 128, 128, 105)
Colour._css_colour("WHEAT1", 255, 231, 186)
Colour._css_colour("WHEAT2", 238, 216, 174)
Colour._css_colour("WHEAT3", 205, 186, 150)
Colour._css_colour("WHEAT4", 139, 126, 102)
Colour._css_colour("YELLOW1", 255, 255, 0)
Colour._css_colour("YELLOW2", 238, 238, 0)
Colour._css_colour("YELLOW3", 205, 205, 0)
Colour._css_colour("YELLOW4", 139, 139, 0)

for basename in [name[:-1] for name in Colour._COLOUR if name.endswith("1")]:
    if basename not in Colour._COLOUR:
        Colour._COLOUR[basename] = Colour._COLOUR[basename+"1"]
