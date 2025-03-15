import moderngl
from array import array
from pygame import Surface,display,constants as const
__all__ = [
    'moderngl',
    'window'
]

def _readShader(path:str) -> str:
    with open(path,'r') as file:
        return file.read()
    
def _makeBuffer(ctx:moderngl.Context,size:tuple[float,float] = (1.0,1.0),offset:tuple[float,float] = (0.0,0.0)):
    return ctx.buffer(data = array('f',[
    -1.0 * size[0]+offset[0] , 1.0 * size[1]+offset[1], 0.0, 0.0,
     1.0 * size[0]+offset[0], 1.0 * size[1]+offset[1], 1.0, 0.0,
    -1.0 * size[0]+offset[0], -1.0 * size[1]+offset[1], 0.0, 1.0,
    1.0 * size[0]+offset[0], -1.0 * size[1]+offset[1], 1.0, 1.0,    
    ]))


class Window:
    def __init__(self,size:tuple[int,int],flags:int=0):
        display.init()
        display.set_mode(size,const.OPENGL|const.DOUBLEBUF|flags)
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND) #type: ignore
        self.ctx.blend_func = self.ctx.SRC_ALPHA, self.ctx.ONE_MINUS_DST_ALPHA #type: ignore
        self.location_holes:list[int] = []
        self.world_surface = Surface(size)
        self.ui_surface = Surface(size,const.SRCALPHA)
        self.world_tex = self.makeTexture(size,(moderngl.NEAREST,moderngl.NEAREST),0)
        self.ui_tex = self.makeTexture(size,(moderngl.LINEAR,moderngl.LINEAR),1)
        self.program, self.render_object = Window.getShader(self.ctx,'./shaders/everything.vert','./shaders/game.frag')
        self.program['world_tex'] = 0
        self.program['ui_tex'] = 1
        self.last_location = 1
        self.tex_to_location = {}


    def setName(self,name:str): display.set_caption(name)

    def getTextureLocation(self,tex):
        k = id(tex)
        return self.tex_to_location.get(k,-1)

    @staticmethod
    def getShader(ctx:moderngl.Context,vertex_path:str,fragment_path:str|None,size = (1.0,1.0),offset = (0.0,0.0)):
        quad_buffer = _makeBuffer(ctx,size,offset)
        program = ctx.program(vertex_shader=_readShader(vertex_path), fragment_shader=(_readShader(fragment_path) if fragment_path else None))
        render_object = ctx.vertex_array(program,[(quad_buffer,'2f 2f', 'vert', 'texcoord')],mode = moderngl.TRIANGLE_STRIP)
        return program, render_object

    def makeTexture(self,size:tuple[int,int],filter:tuple,location:int = -1):
        tex = self.ctx.texture(size,4)
        tex.filter = filter
        tex.swizzle = 'BGRA'
        location = self.getNextLocation() if location == -1 else location
        tex.use(location)
        self.tex_to_location = {id(tex):location}
        return tex

    def getNextLocation(self):
        if self.location_holes:
            return self.location_holes.pop()
        else:
            self.last_location += 1
            return self.last_location

    def draw(self):
        self.world_tex.write(self.world_surface.get_view('1'))
        self.ui_tex.write(self.ui_surface.get_view('1'))
        self.render_object.render()

    def close(self):
        self.ctx.release()
        self.program.release()
        self.render_object.release()
        self.ui_tex.release()
        self.world_tex.release()
        display.quit()

    def size(self):
        return self.ui_surface.get_size()
    
window:Window

