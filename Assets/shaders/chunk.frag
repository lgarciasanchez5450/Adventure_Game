#version 330 core

in vec3 uv;
flat in vec3 light;

out vec4 f_color;

uniform sampler2DArray tex;

// Fog Variables
float NEAR = 0.1;
float FAR = 1024.0; // 64*16 = 1024 // 16* 16 == 256
float density = 1.1;
vec3 fog_color = vec3(0.8, 0.9, 1.0);

void main() {
    vec3 color = texture(tex, uv).rgb;
    color = color * light;
    f_color = vec4(color, 1.0);
    float depth = (1 - FAR / NEAR) * gl_FragCoord.z + (FAR / NEAR);
    depth = 1.0 / depth;
    float fog_factor = pow(2, -pow(depth * density, 2));
    f_color.rgb = mix(f_color.rgb,fog_color, 1-fog_factor);
}