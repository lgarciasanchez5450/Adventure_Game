import moderngl as mgl

class FBO:
    @classmethod
    def new(cls,ctx:mgl.Context,size:tuple[int,int]):
        depth_tex = ctx.depth_texture(size)
        frame_tex = ctx.texture(size, 4, dtype='f1')
        return FBO(depth_tex,frame_tex,ctx.framebuffer([frame_tex], depth_tex))

    def __init__(self,depth_tex:mgl.Texture,frame_tex:mgl.Texture,framebuffer:mgl.Framebuffer):
        self.depth_texture = depth_tex
        self.frame_texture = frame_tex
        self.framebuffer = framebuffer

    def release(self):
        self.depth_texture.release()
        self.frame_texture.release()
        self.framebuffer.release()
