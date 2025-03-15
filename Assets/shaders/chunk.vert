#version 330 core

layout (location = 0) in ivec3 in_position;
layout (location = 1) in int in_face;
layout (location = 2) in int in_block_id;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;
uniform int texture_indices[1000];

out vec3 uv;
flat out vec3 light;

const vec2 uv_coords[6] = vec2[6](
    vec2(0,1), vec2(0,0), vec2(1,0), vec2(0,1), vec2(1,0), vec2(1,1)
);

const vec3 global_light_dir = normalize(vec3(0,-1,.5));
const vec3 global_light_color = vec3(1,1,1); // Pure white color


const vec3 normals_from_face[6] = vec3[6](
    vec3(0,1,0), vec3(0,-1,0), // Top Bottom
    vec3(1,0,0), vec3(-1,0,0), // X+  X-
    vec3(0,0,1), vec3(0,0,-1)  // Z+  Z-
);

void main() { // This function is called per-vertex
    // Calculate which texture index we're in 
    int uv_index = gl_VertexID % 6; 
    uv = vec3(uv_coords[uv_index], texture_indices[(in_block_id-1)*6 + in_face]);

    //Certain Faces should get different shadings w.r.t. global illumination color

    vec3 face_normal = normals_from_face[in_face];
    float gi_strength = max(.2,dot(-face_normal,global_light_dir));
    light = gi_strength*global_light_color;
    

    gl_Position = m_proj * m_view * m_model * vec4(in_position,1.0);
}