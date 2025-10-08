
import pygame.freetype

class Font(pygame.freetype.Font):
    """支持深层次拷贝的Font类"""

    def __init__(self, file=None, size=0, font_index=0, resolution=0, ucs4=False):
        super().__init__(file, size, font_index, resolution, ucs4)

        self._init_params = {
            'file': file,
            'size': size,
            'font_index': font_index,
            'resolution': resolution,
            'ucs4': ucs4
        }

        self.attrs = ["antialiased", "kerning", "origin", "pad", "ucs4", "use_bitmap_strikes", "vertical",
                      "strong", "oblique", "underline", "wide",
                      "fgcolor", "bgcolor",
                      "strength", "underline_adjustment", "rotation"]

    def __deepcopy__(self, memo):
        """实现深度拷贝"""
        # 创建新的字体实例
        new_font = Font(**self._init_params)

        for attr in self.attrs:
            if getattr(self, attr, None) is not None:
                setattr(new_font, attr, getattr(self, attr))

        return new_font

    def __eq__(self, other):
        if isinstance(other, Font):
            for attr in self.attrs:
                if getattr(self, attr, None) is None or getattr(other, attr) != getattr(self, attr):
                    return False
            return True
        return False
