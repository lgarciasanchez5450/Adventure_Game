from pygame import Surface,image,transform
import numpy as np
import moderngl as mgl
def loadVoxels(path:str,ctx:mgl.Context):
    '''
    #This is a comment
    #BlockID       X+               X-             Y+         Y-          Z+           Z-

     1        grass_side.png       1.X+      grass_top.png dirt.png      1.X+         1.X+
    '''
    backrefs:dict[str,str] = {}
    out:dict[int,tuple[str,str,str,str,str,str]] = {}
    with open(path,'r') as file:
        for line in file.readlines():
            line = line.strip()
            if line.startswith('#') or not line: continue 
            block_id,*raw_sides = line.split()
            sides:list[str] = []
            for name,value in zip(['X+','X-','Y+','Y-','Z+','Z-'],raw_sides):
                value = backrefs.get(value.upper(),value)
                backrefs[f'{block_id}.{name}'] = value
                sides.append(value)
            out[int(block_id)] = tuple(sides) #type: ignore
    indirections = np.zeros(1000,dtype=np.int32)
    imgs_loaded:dict[str,int] = {}
    imgs:list[Surface] = []
    for block_id,side_paths in out.items():
        for i,path in enumerate(side_paths):
            i += (block_id-1)*6
            if path not in imgs_loaded:
                imgs_loaded[path] = len(imgs)
                imgs.append(transform.flip(image.load(f'Assets/Blocks/{path}').convert_alpha(),False,True))
            indirections[i] = imgs_loaded[path]

    first_size = imgs[0].get_size()
    for size in map(Surface.get_size,imgs):
        if first_size != size: 
            raise BufferError("All Images must be the same size")
    
    tex = ctx.texture_array(
        (first_size[0],first_size[1],len(imgs)),
        4,
        b''.join([s.get_view('1').raw for s in imgs])
    )
    tex.swizzle = 'BGRA'
    tex.anisotropy = 8
    tex.build_mipmaps()
    tex.filter = mgl.LINEAR_MIPMAP_LINEAR,mgl.NEAREST
    return tex,indirections
