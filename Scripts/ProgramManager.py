import moderngl as mgl
import os

class ProgramManager:
    def __init__(self,ctx:mgl.Context) -> None:
        self.ctx = ctx

    def getProgram(self,vert:str,frag:str):
        if os.path.isfile(vert):
            with open(vert,'r') as file:
                vert = file.read()
        if os.path.isfile(frag):
            with open(frag,'r') as file:
                frag = file.read()
        return self.ctx.program(vertex_shader = vert,fragment_shader=frag)
