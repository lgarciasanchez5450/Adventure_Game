#version 330 core

uniform sampler2D source;
uniform sampler2D dest;
in vec2 uv;
out vec4 f_color;

void main() {
    
    vec4 ui = texture(source, uv);
    f_color = texture(dest, uv);
    f_color.rgb = ui.rgb * ui.a + f_color.rgb * (1 - ui.a);
}