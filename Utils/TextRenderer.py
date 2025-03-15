from typing import TypeVar,Generator
from pygame import Surface, Font,Color,constants as const
C = TypeVar("C",Color,tuple)




class RichCharacter:
    def __init__(self,text:str,color:tuple[int,int,int]|Color,bold:bool=False,italic:bool = False,underlined:bool=False,strikethrough:bool = False) -> None:
        self.char = text
        self.color = color
        self.bold = bold
        self.italic = italic
        self.underlined=underlined
        self.strikethrough = strikethrough

    def is_similiar(self,other:"RichCharacter"):
        return (
            self.color == other.color and
            self.bold == other.bold and
            self.italic == other.italic and
            self.underlined == other.underlined and
            self.strikethrough == other.strikethrough
        )
    
    def __add__(self,other:"RichCharacter"):
        assert self.is_similiar(other), 'Must be similar to other!'
        return RichCharacter(self.char+other.char,self.color,self.bold,self.italic,self.underlined,self.strikethrough)
    
    def __iadd__(self,other:"RichCharacter"):
        assert self.is_similiar(other), 'Must be similar to other!'
        self.char += other.char
        return self
    
    def __repr__(self):
        return f'RC[{self.char}]'
    
def b36_to_color(c:str) -> tuple[int,int,int]:
    assert len(c) == 3, 'length of <c> must be 3.'
    r,g,b = c
    return int(r,36)*7314//1000,int(g,36)*7314//1000,int(b,36)*7314//1000

class TextRenderer:
    def __init__(self,font:Font,base_color:Color|tuple[int,int,int] = (0,0,0)) -> None:
        self.font = font
        self.base_color = base_color

    def lines(self,text:str):
        return text.count('\n')
    
    def preprocess_text(self,text:str) -> Generator[list[RichCharacter],None,None]:
        lines = text.splitlines() 
        color = self.base_color
        for line in lines:
            rich_line = []
            i = 0
            while True:
                for i,char in enumerate(line):
                    if char == '§':
                        break
                    else:
                        rich_line.append(RichCharacter(char,color))
                else:
                    break
                line = line[i:]
                #if we get here then it is probable that we need to parse a code
                #there are 3 ways to continue here ,either the next character is § or C or any other one
                code_prefix = line[:2]
                line = line[2:]
                if code_prefix == '§§':
                    rich_line.append(RichCharacter('§',color))
                elif code_prefix == '§C':
                    args = line[:3]
                    print('args:',args)
                    try:
                        color = b36_to_color(args)
                    except:
                        rich_line.extend(map(lambda s:RichCharacter(s,color),code_prefix+args))
                    finally:
                        line = line[3:]
                else:
                    rich_line.append(RichCharacter(code_prefix[0],color))
                    if len(code_prefix) == 2:
                        rich_line.append(RichCharacter(code_prefix[1],color))

            yield rich_line
                
    def render_align(self,text:str,align:float = 0) -> Surface:
        surfs = self.render(text)
        if len(surfs) == 0: return Surface((0,0))
        if len(surfs) == 1: return surfs[0]
        big_surf = Surface((max(surf.get_width() for surf in surfs),sum(surf.get_height() for surf in surfs)))
        y_offset = 0
        for surf in surfs:
            big_surf.blit(surf,(((big_surf.get_width()-surf.get_width())*align).__trunc__(),y_offset))
            y_offset += surf.get_height()
        return big_surf

    def render(self,text:str) -> list[Surface]:
        rich_lines = self.preprocess_text(text)
        line_renders:list[Surface] = []
        GROUP_SIMILAR = True #group similar RichCharacter's if it improves performance 
        for rich_line in rich_lines:
            if not rich_line:
                line_renders.append(Surface((1,self.font.get_height()),const.SRCCOLORKEY))
                line_renders[-1].set_colorkey((0,0,0))
            surf = Surface(self.font.size(''.join([rc.char for rc in rich_line])),const.SRCALPHA)
            if GROUP_SIMILAR:
                t_line = []
                last_char = rich_line[0]
                for char in rich_line[1:]:
                    if last_char.is_similiar(char):
                        last_char += char
                    else:
                        t_line.append(last_char)
                        last_char = char
                else:
                    t_line.append(last_char)
                rich_line = t_line
            x_offset = 0
            for rich_text in rich_line:
                self.font.set_italic(rich_text.italic)
                self.font.set_underline(rich_text.underlined)
                self.font.set_strikethrough(rich_text.strikethrough)
                self.font.set_bold(rich_text.bold)
                surf.blit(self.font.render(rich_text.char,True,rich_text.color),(x_offset,0))
                x_offset += self.font.size(rich_text.char)[0]
            line_renders.append(surf)
        return line_renders