import glm



NEAR = .1
FAR = 1024

class RasterCamera:
    def __init__(self,position) -> None:
        self.position = glm.vec3(position)
        self.yaw = 0.0
        self.pitch = 0.0
        self.forward = glm.vec3(0,1,0)
        self.right  = glm.vec3(1,0,0)
        self.aspect_ratio = 16/9#engine.window_size[0] / engine.window_size[1]
        self.real_fov:float = 90
        self.target_fov:float = 90 #allows for smoothly transitioning between fovs
        self.up = glm.vec3(0,0,1)


    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)
    
    def get_projection_matrix(self) -> glm.mat4x4:
        return glm.perspective(glm.radians(self.real_fov), self.aspect_ratio, NEAR, FAR)
    


# class EntityCamera(RasterCamera):
#     def __init__(self,scene:"RasterScene",entity:AliveEntity):
#         super().__init__(scene,entity.pos)
#         self.position = entity.pos
#         self.entity = entity

#     def update(self):
#         super().update()
#         self.entity.forward = self.xz_forward
#         self.entity.face_dir = self.forward
#         self.entity.right = self.right



# class RayTraceCamera:
#     def __init__(self,scene:"RayTraceScene",position:tuple[int,int,int]) -> None:
#         self.pos= glm.vec3(position)
#         self.position = self.pos
#         self.scene = scene
#         self.engine = scene.engine
#         self.yaw = 45
#         self.pitch = -32
#         self.xz_forward = glm.vec3()
#         self.forward = glm.vec3()
#         yaw = glm.radians(self.yaw)
#         pitch = glm.radians(self.pitch)
#         self.xz_forward.x = glm.cos(yaw)
#         self.xz_forward.z = glm.sin(yaw)
#         self.forward.x = self.xz_forward.x * glm.cos(pitch)
#         self.forward.y = glm.sin(pitch)
#         self.forward.z = self.xz_forward.z * glm.cos(pitch) 
#         self.right  = glm.normalize(glm.cross(self.forward,glm.vec3(0,1,0)))
       
#         self.up = glm.normalize(glm.cross(self.right, self.forward))

#     def update(self):
#         self.position = self.pos
#         rel_x, rel_y = pygame.mouse.get_rel()
#         self.yaw += rel_x * 0.1
#         self.pitch -= rel_y * 0.1
#         self.pitch = min(max(self.pitch,-90),90)
#         self.yaw %= 360
#         yaw = glm.radians(self.yaw)
#         pitch = glm.radians(self.pitch)
#         self.xz_forward.x = glm.cos(yaw)
#         self.xz_forward.z = glm.sin(yaw)
#         self.forward.x = self.xz_forward.x * glm.cos(pitch)
#         self.forward.y = glm.sin(pitch)
#         self.forward.z = self.xz_forward.z * glm.cos(pitch) 
#         self.right  = glm.normalize(glm.cross(self.forward,glm.vec3(0,1,0)))
       
#         self.up = glm.normalize(glm.cross(self.right, self.forward))
#         # print(self.up)